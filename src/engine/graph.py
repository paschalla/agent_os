from langgraph.graph import StateGraph, START, END
from .state import AgentState
from .nodes import classifier_node, tool_node, synthesizer_node

def route_step(state: AgentState):
    if state.get("intent") == "tool_use" and state.get("selected_tool"):
        return "tool_node"
    return "synthesizer_node"

def create_agent_graph():
    workflow = StateGraph(AgentState)
    
    # Add Nodes
    workflow.add_node("classifier_node", classifier_node)
    workflow.add_node("tool_node", tool_node)
    workflow.add_node("synthesizer_node", synthesizer_node)
    
    # Add Edges
    workflow.add_edge(START, "classifier_node")
    
    workflow.add_conditional_edges(
        "classifier_node",
        route_step,
        {
            "tool_node": "tool_node",
            "synthesizer_node": "synthesizer_node"
        }
    )
    
    workflow.add_edge("tool_node", "synthesizer_node")
    workflow.add_edge("synthesizer_node", END)
    
    return workflow.compile()
