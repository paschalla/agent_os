import logging
import sys
import os
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Ensure src is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.engine.graph import create_agent_graph
from src.engine.state import AgentState
from src.core.resources import ResourceMonitor, ResourceStatus
from src.core.memory import memory

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load env
load_dotenv()

# Initialize Resource Monitor
monitor = ResourceMonitor(cpu_threshold_critical=85.0, mem_threshold_critical=90.0)

# Current conversation ID (simple session management)
current_conversation_id = memory.get_or_create_conversation()
logger.info(f"Using conversation ID: {current_conversation_id}")

app = FastAPI(title="andy-os API")

# ... (CORS middleware)

# Initialize Agent Graph
try:
    graph = create_agent_graph()
    logger.info("Agent Graph initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Agent Graph: {e}")
    graph = None

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []

class ChatResponse(BaseModel):
    response: str
    tool_output: Optional[Dict[str, Any]] = None
    model_used: str

@app.get("/health")
async def health_check():
    return {"status": "ok", "agent_status": "ready" if graph else "error"}

@app.get("/api/status")
async def get_status():
    metrics = monitor.get_metrics()
    return {
        "cpu": metrics.cpu_percent,
        "memory": metrics.memory_percent,
        "load_avg": {
            "1m": metrics.load_avg[0],
            "5m": metrics.load_avg[1],
            "15m": metrics.load_avg[2]
        },
        "temperature": metrics.temperature,
        "status": metrics.status.value,
        "mode": "Power Save" if metrics.status == ResourceStatus.CRITICAL else "Performance"
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not graph:
        raise HTTPException(status_code=500, detail="Agent system not initialized")
    
    logger.info(f"Received message: {request.message}")
    
    # Resource constraint check - force light model if system is under pressure
    force_light = monitor.should_use_light_model()
    if force_light:
        logger.warning("Resource constraint detected, will force light model")

    try:
        # Construct state
        current_messages = list(request.history)
        current_messages.append({"role": "user", "content": request.message})
        
        state: AgentState = {
            "user_input": request.message,
            "messages": current_messages,
            "intent": "ambiguous",
            "selected_tool": None,
            "tool_args": {},
            "tool_output": None,
            "final_response": "",
            "error": None,
            # Model selection now handled by classifier_node via complexity assessment
            # But if resources are constrained, force light model
            "model_override": "qwen2.5-coder:1.5b" if force_light else None,
            "complexity": None
        }
        
        result = graph.invoke(state)
        
        response_text = result.get("final_response", "No response generated.")
        tool_out = result.get("tool_output")
        model_used = result.get("model_override", "unknown")
        
        # Save messages to persistent memory
        memory.save_message(current_conversation_id, "user", request.message)
        memory.save_message(current_conversation_id, "assistant", response_text, 
                           {"model": model_used, "tool_output": tool_out})
        
        return ChatResponse(
            response=response_text,
            tool_output=tool_out if isinstance(tool_out, dict) else None,
            model_used=model_used
        )
        
    except Exception as e:
        logger.error(f"Error processing chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Listen on all interfaces
    uvicorn.run("src.interface.server:app", host="0.0.0.0", port=8000, reload=True)
