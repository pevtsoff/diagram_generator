#!/usr/bin/env python3
"""Test script to debug LLM responses for diagram requests."""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from diagram_service.agents.diagram_agent import DiagramAgent

async def test_llm_response():
    """Test what the LLM returns for diagram requests."""
    
    # Get API key
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    use_mock = os.getenv("USE_MOCK_LLM", "false").lower() == "true"
    
    if not gemini_api_key and not use_mock:
        print("❌ No Gemini API key found. Set GEMINI_API_KEY or USE_MOCK_LLM=true")
        return
    
    try:
        # Initialize agent
        agent = DiagramAgent(gemini_api_key or "mock", use_mock=use_mock)
        
        # Test message
        test_message = "can you create me this diagram - User ->Nginx ->API ->Redis, and Api->Database"
        
        print(f"🧪 Testing message: {test_message}")
        print("=" * 50)
        
        # Get supported node types
        supported_node_types = agent.diagram_tools.get_supported_node_types()
        print(f"📋 Supported node types: {supported_node_types[:10]}...")
        print("=" * 50)
        
        # Test the LLM response directly
        response = await agent.llm_client.assistant_chat(test_message, supported_node_types)
        
        print("🤖 LLM Response:")
        print(response)
        print("=" * 50)
        
        # Test the full chat flow
        result = await agent.chat_with_assistant(test_message)
        
        print("📊 Chat Result:")
        print(f"Type: {result.get('type')}")
        print(f"Message: {result.get('message', 'N/A')}")
        print(f"Response: {result.get('response', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_llm_response()) 