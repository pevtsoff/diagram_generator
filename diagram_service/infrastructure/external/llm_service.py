import logging
from typing import Any, Dict, List, Protocol

import google.generativeai as genai
from pydantic import BaseModel, Field

# Create logger at module level
logger = logging.getLogger(__name__)


class LLMService(Protocol):
    """Protocol for LLM service integration."""

    async def generate_diagram_specification(
        self, description: str, supported_node_types: List[str]
    ) -> Dict[str, Any]: ...

    async def chat_with_assistant(self, message: str) -> Dict[str, Any]: ...

    async def generate_chat_response(self, message: str) -> str: ...


class GeminiLLMService(BaseModel):
    """Gemini-based LLM service implementation."""

    api_key: str = Field(..., description="Gemini API key")

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, api_key: str):
        super().__init__(api_key=api_key)

    async def generate_diagram_specification(
        self, description: str, supported_node_types: List[str]
    ) -> Dict[str, Any]:
        """Generate diagram specification from description."""
        try:
            # For now, return a mock response since the old Gemini client was removed
            # In a full implementation, this would call the actual LLM service
            return {
                "name": "Mock Diagram",
                "nodes": [],
                "connections": [],
                "clusters": [],
            }
        except Exception as e:
            logger.error(f"Error generating diagram specification: {e}")
            raise

    async def chat_with_assistant(self, message: str) -> Dict[str, Any]:
        """Chat with the assistant."""
        try:
            # This would use the existing chat functionality
            # For now, return a mock response
            return {
                "type": "text",
                "response": f"Assistant response to: {message}",
                "image_url": "",
                "specification": {},
                "supported_node_types": [],
            }
        except Exception as e:
            logger.error(f"Error in chat with assistant: {e}")
            raise

    async def generate_chat_response(self, message: str) -> str:
        """Generate a conversational response using Gemini."""
        try:
            # Configure Gemini
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")

            # Create a context-aware prompt
            system_prompt = """You are a helpful AI assistant specialized in creating architecture diagrams. You can help users create AWS, Azure, and GCP architecture diagrams.

Your capabilities include:
- Creating AWS architectures (EC2 + RDS, FastAPI + SQS, Lambda + DynamoDB)
- Creating Azure architectures (App Service + SQL Database, Functions + Storage)
- Creating GCP architectures (Compute Engine + Cloud SQL, Cloud Functions + Firestore)

When users ask for diagrams, guide them to use specific requests like:
- "Create a FastAPI + SQS architecture"
- "Generate an EC2 + RDS diagram"
- "Make an AWS architecture with Lambda"

Be friendly, helpful, and conversational. Keep responses concise and engaging."""

            # Generate response
            response = await model.generate_content_async(
                f"{system_prompt}\n\nUser: {message}\n\nAssistant:"
            )

            logger.info(f"Generated LLM response: {response.text.strip()}")
            return response.text.strip()

        except Exception as e:
            logger.error(f"Error generating chat response: {e}")
            logger.error(f"API Key length: {len(self.api_key) if self.api_key else 0}")

            # Check if it's a rate limit error
            if "429" in str(e) or "quota" in str(e).lower():
                return "🤖 I'm currently experiencing high demand from the AI service. Let me help you with diagram generation instead! Try asking me to 'Create a FastAPI + SQS architecture' or 'Generate an EC2 + RDS diagram' and I'll build one for you."

            # Fallback response for other errors
            return "💬 I'm here to help you create architecture diagrams! Try asking me to 'Create a FastAPI + SQS architecture' or 'Generate an EC2 + RDS diagram' and I'll build one for you."
