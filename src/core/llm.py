import os
import logging
import json
import ollama
from typing import Dict, Any, List

from .prompts import CLASSIFIER_PROMPT, SYSTEM_IDENTITY

logger = logging.getLogger(__name__)

class OllamaClient:
    LIGHT_MODEL = "qwen2.5-coder:1.5b"
    HEAVY_MODEL = "llama3"
    
    def __init__(self, model: str = "llama3"):
        self.model = model
        self.host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.client = ollama.Client(host=self.host)

    def assess_complexity(self, user_input: str) -> str:
        """
        Use a lightweight model to classify if the request is simple or complex.
        Returns: "simple" or "complex"
        """
        system_prompt = (
            "Classify if this request is SIMPLE or COMPLEX.\n"
            "SIMPLE: greetings, basic questions, single-step tasks, status checks, short answers.\n"
            "COMPLEX: multi-step reasoning, code generation, detailed analysis, debugging.\n\n"
            "Output ONLY valid JSON: {\"complexity\": \"simple\"} or {\"complexity\": \"complex\"}"
        )
        
        try:
            response = self.client.generate(
                model=self.LIGHT_MODEL,
                prompt=f"Request: {user_input}",
                system=system_prompt,
                format="json",
                stream=False
            )
            result = json.loads(response['response'])
            complexity = result.get("complexity", "simple")
            logger.info(f"Complexity assessment: {complexity} for input: {user_input[:50]}...")
            return complexity
        except Exception as e:
            logger.warning(f"Complexity assessment failed: {e}, defaulting to simple")
            return "simple"

    def classify_intent(self, user_input: str, tools: List[str], model_override: str = None) -> Dict[str, Any]:
        """
        Fast LLM call to route the request using andy-os classifier prompt.
        """
        current_model = model_override or self.model
        system_prompt = CLASSIFIER_PROMPT.format(tools=', '.join(tools))
        
        try:
            response = self.client.generate(
                model=current_model,
                prompt=f"Request: {user_input}",
                system=system_prompt,
                format="json",
                stream=False
            )
            return json.loads(response['response'])
        except Exception as e:
            logger.error(f"Classification failed using {current_model}: {e}")
            return {"intent": "conversational", "tool": None, "args": {}}

    def chat(self, messages: List[Dict[str, str]], model_override: str = None, context: str = "") -> str:
        """
        Standard chat completion with andy-os identity.
        """
        current_model = model_override or self.model
        
        # Prepend system message with andy-os identity
        system_content = SYSTEM_IDENTITY
        if context:
            system_content += f"\n\n## Recent Context:\n{context}"
        
        full_messages = [{"role": "system", "content": system_content}] + messages
        
        try:
            response = self.client.chat(
                model=current_model,
                messages=full_messages,
                stream=False
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"Chat failed using {current_model}: {e}")
            return f"I encountered an error: {e}"
