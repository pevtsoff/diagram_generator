import asyncio
import os

import pytest

from diagram_service.agents.chat_agent import ChatAgent
from diagram_service.agents.diagram_agent import DiagramAgent
from diagram_service.api.models import DiagramRequest
from tests.mocks.mock_client import MockLLMClient


def create_test_agent():
    """Create a test agent with mock LLM client."""

    class TestDiagramAgent(DiagramAgent):
        def __init__(self):
            # Initialize with mock API key
            super().__init__("mock_api_key")

            # Override with mock client
            self.llm_client = MockLLMClient()

            # Create chat agent with mock client
            self.chat_agent = ChatAgent("mock_api_key")
            self.chat_agent.llm_client = MockLLMClient()

    return TestDiagramAgent()


class TestMockLLMClient:
    """Test cases for MockLLMClient."""

    def setup_method(self):
        """Setup for each test method."""
        self.mock_client = MockLLMClient()

    @pytest.mark.asyncio
    async def test_assistant_chat_diagram_request(self):
        """Test assistant chat with diagram request."""
        message = "create me a diagram with nginx and api"
        supported_types = ["ec2", "rds", "alb", "general"]

        response = await self.mock_client.assistant_chat(message, supported_types)

        # Should return JSON for diagram requests
        assert response.startswith("{")
        assert response.endswith("}")
        assert "nginx" in response.lower()
        assert "api" in response.lower()

    @pytest.mark.asyncio
    async def test_assistant_chat_general_request(self):
        """Test assistant chat with general request."""
        message = "what is cloud computing?"
        supported_types = ["ec2", "rds", "alb"]

        response = await self.mock_client.assistant_chat(message, supported_types)

        # Should return text response for general requests
        assert not response.startswith("{")
        assert "cloud" in response.lower()

    @pytest.mark.asyncio
    async def test_generate_diagram_specification_nginx(self):
        """Test diagram specification generation for nginx pattern."""
        description = "User -> Nginx -> API -> Redis, and API -> Database"
        supported_types = ["ec2", "rds", "alb", "general"]

        spec = await self.mock_client.generate_diagram_specification(
            description, supported_types
        )

        assert isinstance(spec, DiagramRequest)
        assert "nginx" in spec.name.lower()
        assert len(spec.nodes) >= 4  # user, nginx, api, redis, database
        assert len(spec.connections) >= 4

    @pytest.mark.asyncio
    async def test_generate_diagram_specification_microservices(self):
        """Test diagram specification generation for microservices pattern."""
        description = "microservices architecture with auth and payment services"
        supported_types = ["ec2", "rds", "alb", "sqs"]

        spec = await self.mock_client.generate_diagram_specification(
            description, supported_types
        )

        assert isinstance(spec, DiagramRequest)
        assert "microservices" in spec.name.lower()
        assert len(spec.nodes) >= 3
        assert len(spec.clusters) >= 1

    @pytest.mark.asyncio
    async def test_generate_diagram_specification_redis(self):
        """Test diagram specification generation for Redis pattern."""
        description = "web application with Redis cache and database"
        supported_types = ["ec2", "rds", "alb", "redis"]

        spec = await self.mock_client.generate_diagram_specification(
            description, supported_types
        )

        assert isinstance(spec, DiagramRequest)
        assert "redis" in spec.name.lower()
        assert len(spec.nodes) >= 3  # api, redis, database
        assert len(spec.connections) >= 2

        # Check that Redis node is present
        redis_nodes = [node for node in spec.nodes if node["type"] == "onprem_redis"]
        assert len(redis_nodes) >= 1
        assert any("redis" in node["label"].lower() for node in redis_nodes)

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check method."""
        assert await self.mock_client.health_check() is True


class TestDiagramAgentIntegration:
    """Test cases for DiagramAgent integration with mock LLM."""

    def setup_method(self):
        """Setup for each test method."""
        self.agent = create_test_agent()

    def teardown_method(self):
        """Cleanup after each test method."""
        if hasattr(self.agent, "diagram_tools"):
            self.agent.diagram_tools.cleanup()

    @pytest.mark.asyncio
    async def test_chat_with_assistant_diagram_request(self):
        """Test chat with assistant for diagram request."""
        message = "create a diagram with nginx and api server"

        result = await self.agent.chat_with_assistant(message)

        assert result["type"] == "diagram"
        assert "diagram_path" in result
        assert "message" in result
        assert "successfully" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_chat_with_assistant_general_request(self):
        """Test chat with assistant for general request."""
        message = "what components are supported?"

        result = await self.agent.chat_with_assistant(message)

        assert result["type"] == "text"
        assert "response" in result
        assert "components" in result["response"].lower()

    @pytest.mark.asyncio
    async def test_chat_with_assistant_error_handling(self):
        """Test error handling in chat with assistant."""
        # Test with invalid message that might cause issues
        message = ""

        result = await self.agent.chat_with_assistant(message)

        # Should handle gracefully
        assert "type" in result
        assert result["type"] in ["text", "error"]

    def test_agent_initialization(self):
        """Test agent initialization."""
        assert self.agent is not None
        assert hasattr(self.agent, "llm_client")
        assert hasattr(self.agent, "diagram_tools")
        assert isinstance(self.agent.llm_client, MockLLMClient)


class TestLLMResponseParsing:
    """Test cases for LLM response parsing and diagram creation."""

    def setup_method(self):
        """Setup for each test method."""
        self.agent = create_test_agent()

    def teardown_method(self):
        """Cleanup after each test method."""
        if hasattr(self.agent, "diagram_tools"):
            self.agent.diagram_tools.cleanup()

    @pytest.mark.asyncio
    async def test_diagram_creation_from_llm_response(self):
        """Test creating diagram from LLM response."""
        message = "create a simple web app with load balancer and database"

        result = await self.agent.chat_with_assistant(message)

        assert result["type"] == "diagram"
        assert "diagram_path" in result
        assert os.path.exists(result["diagram_path"])

        # Clean up the generated file
        if os.path.exists(result["diagram_path"]):
            os.remove(result["diagram_path"])

    @pytest.mark.asyncio
    async def test_supported_node_types_integration(self):
        """Test that supported node types are properly integrated."""
        node_types = self.agent.diagram_tools.get_supported_node_types()

        assert isinstance(node_types, list)
        assert len(node_types) >= 10  # Should have many node types
        assert "aws_ec2" in node_types
        assert "aws_rds" in node_types
        assert "aws_alb" in node_types
        assert "onprem_redis" in node_types  # Test Redis is included

    @pytest.mark.asyncio
    async def test_redis_diagram_creation_from_llm(self):
        """Test creating Redis diagram from LLM response."""
        message = "create a web app with API server, Redis cache, and database"

        result = await self.agent.chat_with_assistant(message)

        assert result["type"] == "diagram"
        assert "diagram_path" in result
        assert os.path.exists(result["diagram_path"])

        # Clean up the generated file
        if os.path.exists(result["diagram_path"]):
            os.remove(result["diagram_path"])

    @pytest.mark.asyncio
    async def test_redis_cache_architecture(self):
        """Test Redis cache architecture generation."""
        message = "design a microservices architecture with Redis for caching"

        result = await self.agent.chat_with_assistant(message)

        assert result["type"] == "diagram"
        assert "diagram_path" in result
        assert os.path.exists(result["diagram_path"])

        # Clean up the generated file
        if os.path.exists(result["diagram_path"]):
            os.remove(result["diagram_path"])


if __name__ == "__main__":
    # For manual testing
    async def run_tests():
        """Run tests manually for debugging."""
        print("🧪 Running LLM Integration Tests...")

        # Test mock client
        mock_client = MockLLMClient()
        response = await mock_client.assistant_chat(
            "create a diagram with nginx and api", ["ec2", "rds", "alb", "general"]
        )
        print(f"Mock client response: {response[:200]}...")

        # Test agent
        agent = create_test_agent()
        result = await agent.chat_with_assistant("create a simple web app")
        print(f"Agent result type: {result.get('type')}")

        # Cleanup
        agent.diagram_tools.cleanup()

    asyncio.run(run_tests())
