from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    """
    Represents the state of the agent workflow.
    """
    user_input: str
    messages: List[Dict[str, str]]
    
    # Classification State
    intent: str  # e.g., "tool_use", "conversational", "ambiguous"
    selected_tool: Optional[str]
    tool_args: Dict[str, Any]
    
    # Execution State
    tool_output: Optional[Dict[str, Any]]
    
    # Final Response
    final_response: str
    error: Optional[str]
    
    # Configuration
    model_override: Optional[str]
    complexity: Optional[str]  # "simple" or "complex"
