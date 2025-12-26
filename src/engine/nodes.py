
from typing import Dict, Any
from .state import AgentState
from ..core.llm import OllamaClient
from ..tools.registry import ToolRegistry
import logging

logger = logging.getLogger(__name__)

# Singletons for this example, or strictly instantiated in main
client = OllamaClient()
registry = ToolRegistry()

def classifier_node(state: AgentState) -> AgentState:
    logger.info("Running Classifier")
    user_input = state["user_input"]
    tool_names = registry.get_tool_names()
    
    # Step 1: Assess complexity using lightweight model
    complexity = client.assess_complexity(user_input)
    state["complexity"] = complexity
    
    # Step 2: Choose model based on complexity
    # BUT respect pre-set model_override from server (resource constraint)
    existing_override = state.get("model_override")
    if existing_override:
        logger.info(f"Resource constraint: keeping forced model {existing_override}")
    elif complexity == "complex":
        state["model_override"] = client.HEAVY_MODEL
        logger.info(f"Complex request detected, will use {client.HEAVY_MODEL} for synthesis")
    else:
        state["model_override"] = client.LIGHT_MODEL
        logger.info(f"Simple request, using {client.LIGHT_MODEL}")
    
    # Step 3: Classify intent (always with light model for speed)
    result = client.classify_intent(user_input, tool_names, model_override=client.LIGHT_MODEL)
    
    state["intent"] = result.get("intent", "conversational")
    state["selected_tool"] = result.get("tool")
    state["tool_args"] = result.get("args", {})
    
    return state

def tool_node(state: AgentState) -> AgentState:
    logger.info(f"Running Tool: {state['selected_tool']}")
    tool_name = state["selected_tool"]
    args = state["tool_args"]
    
    tool_func = registry.get_tool(tool_name)
    if tool_func:
        try:
            output = tool_func(**args)
            state["tool_output"] = output
        except Exception as e:
            state["tool_output"] = {"success": False, "error": str(e)}
    else:
        state["tool_output"] = {"success": False, "error": "Tool not found"}
        
    return state

def synthesizer_node(state: AgentState) -> AgentState:
    logger.info("Synthesizing Response")
    model_override = state.get("model_override")
    
    # Construct context from state
    messages = list(state.get("messages", []))
    
    # If we just ran a tool, add that context
    if state.get("selected_tool"):
        tool_ctx = (
            f"Result of tool '{state['selected_tool']}':\n"
            f"{state['tool_output']}\n"
        )
        # Add as system/context message temporarily or just append to history?
        # For simplicity, we assume 'messages' holds the history.
        # We'll create a new prompt for synthesis.
        system_msg = "You are Agent-OS. Answer the user based on the tool output provided."
        messages.append({"role": "system", "content": system_msg})
        messages.append({"role": "user", "content": f"Tool Output: {tool_ctx}"})
    
    response = client.chat(messages, model_override=model_override)
    state["final_response"] = response
    
    return state
