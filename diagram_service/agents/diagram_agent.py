import logging
from typing import Any, Dict

from diagram_service.agents.chat_agent import ChatAgent
from diagram_service.llm.gemini_client import GeminiClient
from diagram_service.tools.diagram_tools import DiagramTools


class DiagramAgent:
    """Main agent for creating diagrams from natural language descriptions."""

    def __init__(self, gemini_api_key: str):
        """Initialize the diagram agent with LLM client, tools, and chat agent."""
        self.llm_client = GeminiClient(gemini_api_key)
        self.diagram_tools = DiagramTools()
        self.chat_agent = ChatAgent(gemini_api_key)
        self.logger = logging.getLogger(__name__)

    async def create_diagram_from_description(self, user_description: str) -> str:
        """
        Main workflow: Convert user description to diagram image.

        Args:
            user_description: Natural language description of the desired diagram

        Returns:
            Path to the generated diagram image
        """
        self.logger.info(f"Creating diagram from description: {user_description}")

        try:
            # Step 1: Get supported node types from tools
            supported_node_types = self.diagram_tools.get_supported_node_types()

            # Step 2: Use LLM to generate diagram specification
            diagram_spec = await self.llm_client.generate_diagram_specification(
                user_description, supported_node_types
            )

            self.logger.info(
                f"Generated diagram specification: {diagram_spec.model_dump()}"
            )

            # Step 3: Create the diagram using tools
            image_path = self.diagram_tools.create_diagram(
                name=diagram_spec.name,
                nodes=diagram_spec.nodes,
                connections=diagram_spec.connections,
                clusters=diagram_spec.clusters,
            )

            self.logger.info(f"Created diagram image at: {image_path}")
            return image_path

        except Exception as e:
            self.logger.error(f"Error creating diagram: {e}")
            raise

    async def chat_with_assistant(self, user_message: str) -> Dict[str, Any]:
        """
        Assistant-style interaction for more complex workflows.

        Args:
            user_message: User's message or question

        Returns:
            Response containing either text response or diagram specification
        """
        return await self.chat_agent.chat_with_assistant(user_message)

    def get_supported_components(self) -> Dict[str, str]:
        """Get list of supported diagram components with descriptions."""
        return self.chat_agent.get_supported_components()

    async def health_check(self) -> Dict[str, bool]:
        """Check health of all agent components."""
        return await self.chat_agent.health_check()

    def cleanup(self) -> None:
        """Clean up agent resources."""
        self.diagram_tools.cleanup()
        self.chat_agent.cleanup()


class DiagramAgentPool:
    """Pool of diagram agents for handling concurrent requests."""

    def __init__(self, gemini_api_key: str, pool_size: int = 3):
        """Initialize the agent pool."""
        self.gemini_api_key = gemini_api_key
        self.pool_size = pool_size
        self.logger = logging.getLogger(__name__)

    async def get_agent(self) -> DiagramAgent:
        """Get an agent from the pool (creates new one for stateless design)."""
        # Create new agent for this request (stateless)
        agent = DiagramAgent(self.gemini_api_key)
        return agent

    async def execute_with_agent(self, func):
        """Execute a function with an agent from the pool."""
        agent = await self.get_agent()
        try:
            return await func(agent)
        finally:
            # Clean up agent resources
            agent.cleanup()
