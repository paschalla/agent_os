from src.tools.knowledge import search_knowledge_base
import os

def test_kb():
    # Ensure exports dir exists
    if not os.path.exists("exports"):
        os.makedirs("exports")
        
    # Create a dummy fact
    with open("exports/fact.md", "w") as f:
        f.write("# Secret Info\nThe secret access code is: AGENT-OS-777.")
        
    print("Searching for 'secret access code'...")
    result = search_knowledge_base("secret access code")
    print(f"Result:\n{result}")
    
    if "AGENT-OS-777" in result:
        print("SUCCESS: Found the secret.")
    else:
        print("FAILURE: Did not find the secret.")

if __name__ == "__main__":
    test_kb()
