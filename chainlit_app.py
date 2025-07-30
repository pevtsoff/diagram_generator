import os
import asyncio
import logging
from typing import Optional
from pathlib import Path
import chainlit as cl
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import your existing service components
from diagram_service.agents.diagram_agent import DiagramAgent
from diagram_service.llm.gemini_client import DiagramRequest

# Global agent instance
agent: Optional[DiagramAgent] = None


@cl.on_chat_start
async def start():
    global agent
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    
    if not gemini_api_key:
        await cl.Message(
            content="⚠️ **Warning**: No Gemini API key found. Please set `GEMINI_API_KEY` in your environment.",
            author="System"
        ).send()
        return
    
    try:
        agent = DiagramAgent(gemini_api_key)
        await cl.Message(
            content="🎉 **Diagram Generator Assistant** is ready!\n\nI can help you create various types of diagrams including:\n\n• AWS architecture diagrams\n• Network diagrams\n• System architecture diagrams\n• Flow charts\n• Sequence diagrams\n\nJust describe what you want, and I'll create it for you!",
            author="Assistant"
        ).send()
        
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        await cl.Message(
            content=f"❌ **Error**: Failed to initialize the diagram agent: {str(e)}",
            author="System"
        ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages."""
    global agent
    
    if agent is None:
        await cl.Message(
            content="❌ **Error**: Agent not initialized. Please check your configuration.",
            author="System"
        ).send()
        return
    
    try:
        # Show typing indicator
        await cl.Message(content="🤔 Thinking...", author="Assistant").send()
        
        # Process the message
        response = await agent.chat_with_assistant(message.content)
        
        if response.get("type") == "diagram":
            # Handle diagram response
            diagram_path = response.get("diagram_path")
            if diagram_path and os.path.exists(diagram_path):
                # Create image element
                image = cl.Image(
                    path=diagram_path,
                    name="generated_diagram",
                    display="inline",
                    size="large"
                )
                
                # Send the diagram with description
                await cl.Message(
                    content=f"📊 **Diagram Generated!**\n\n{response.get('message', 'Your diagram has been created successfully.')}",
                    elements=[image]
                ).send()
            else:
                await cl.Message(
                    content=f"❌ **Error**: Failed to generate diagram. {response.get('message', 'Unknown error')}",
                    author="Assistant"
                ).send()
        
        elif response.get("type") == "text":
            # Handle text response
            await cl.Message(
                content=response.get("response", "I'm here to help with diagram creation!"),
                author="Assistant"
            ).send()
        
        elif response.get("type") == "error":
            # Handle error response
            await cl.Message(
                content=f"❌ **Error**: {response.get('message', 'An error occurred')}",
                author="Assistant"
            ).send()
        
        else:
            # Default response
            await cl.Message(
                content=response.get("response", "I'm here to help with diagram creation!"),
                author="Assistant"
            ).send()
            
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await cl.Message(
            content=f"❌ **Error**: An unexpected error occurred: {str(e)}",
            author="System"
        ).send()


@cl.on_chat_end
async def end():
    """Clean up when chat ends."""
    global agent
    agent = None
    logger.info("Chat session ended, agent cleaned up") 