import sys
from ..engine.graph import create_agent_graph
from ..engine.state import AgentState

def run_repl():
    print("Initializing Agent-OS...")
    graph = create_agent_graph()
    
    print("Agent-OS Ready. Type 'exit' to quit.")
    print("-" * 50)
    
    history = []
    
    while True:
        try:
            user_input = input("\n>>> ").strip()
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
                
            if not user_input:
                continue
            
            # Prepare state
            state: AgentState = {
                "user_input": user_input,
                "messages": history,
                "intent": "ambiguous",
                "selected_tool": None,
                "tool_args": {},
                "tool_output": None,
                "final_response": "",
                "error": None
            }
            
            # Run Graph
            print("Thinking...")
            result = graph.invoke(state)
            
            # Display Output
            response = result.get("final_response", "No response.")
            print(f"\nAgent: {response}")
            
            # Update History (naive)
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": response})
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
