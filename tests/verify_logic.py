import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.engine.graph import create_agent_graph
from src.core.llm import OllamaClient

class TestAgentOS(unittest.TestCase):
    
    @patch('src.engine.nodes.client')
    def test_routing_safe_tool(self, mock_client):
        """Test that list files routes to tool_node"""
        print("\nTesting Safe Tool Routing...")
        
        # Mock Classification
        mock_client.classify_intent.return_value = {
            "intent": "tool_use", 
            "tool": "run_command", 
            "args": {"command": "ls -la"}
        }
        # Mock Chat (Synthesis)
        mock_client.chat.return_value = "Here are the files."
        
        graph = create_agent_graph()
        initial_state = {"user_input": "ls", "messages": []}
        
        result = graph.invoke(initial_state)
        
        self.assertEqual(result["selected_tool"], "run_command")
        self.assertIsNotNone(result.get("tool_output"))
        self.assertTrue(result["tool_output"]["success"])
        print("PASS: Routed to tool and executed.")

    @patch('src.engine.nodes.client')
    def test_safety_block(self, mock_client):
        """Test that sudo rm -rf is blocked"""
        print("\nTesting Safety Block...")
        
        mock_client.classify_intent.return_value = {
            "intent": "tool_use", 
            "tool": "run_command", 
            "args": {"command": "sudo rm -rf /"}
        }
        mock_client.chat.return_value = "I cannot do that."
        
        graph = create_agent_graph()
        initial_state = {"user_input": "destroy", "messages": []}
        
        result = graph.invoke(initial_state)
        
        tool_output = result.get("tool_output")
        self.assertFalse(tool_output["success"])
        self.assertIn("Security Block", tool_output["output"])
        print("PASS: Dangerous command blocked.")

    @patch('src.engine.nodes.client')
    def test_conversational(self, mock_client):
        """Test conversational routing"""
        print("\nTesting Conversational Routing...")
        
        mock_client.classify_intent.return_value = {
            "intent": "conversational", 
            "tool": None, 
            "args": {}
        }
        mock_client.chat.return_value = "Hello there!"
        
        graph = create_agent_graph()
        initial_state = {"user_input": "Hello", "messages": []}
        
        result = graph.invoke(initial_state)
        
        self.assertIsNone(result.get("selected_tool"))
        self.assertEqual(result["final_response"], "Hello there!")
        print("PASS: Routed to synthesis directly.")

if __name__ == "__main__":
    unittest.main()
