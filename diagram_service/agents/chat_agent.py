import json
import logging
from typing import Any, Dict

from diagram_service.api.models import DiagramRequest
from diagram_service.llm.gemini_client import GeminiClient
from diagram_service.tools.diagram_tools import DiagramTools


class ChatAgent:
    """Handles chat and assistant interactions for diagram generation."""

    def __init__(self, gemini_api_key: str):
        """Initialize the chat agent with LLM client and tools."""
        self.llm_client = GeminiClient(gemini_api_key)
        self.diagram_tools = DiagramTools()
        self.logger = logging.getLogger(__name__)

    async def chat_with_assistant(self, user_message: str) -> Dict[str, Any]:
        """
        Assistant-style interaction for more complex workflows.

        Args:
            user_message: User's message or question

        Returns:
            Response containing either text response or diagram specification
        """
        self.logger.info(f"Processing assistant chat: {user_message}")

        try:
            # Get supported node types
            supported_node_types = self.diagram_tools.get_supported_node_types()

            # Use LLM for assistant-style response
            response = await self.llm_client.assistant_chat(
                user_message, supported_node_types
            )

            self.logger.info(f"LLM Response: {response}")

            # Try to detect if response contains a diagram specification
            if self._looks_like_diagram_request(response):
                return self._parse_and_create_diagram(response)

            # Return as text response
            return {
                "type": "text",
                "response": response,
                "supported_node_types": supported_node_types,
            }

        except Exception as e:
            self.logger.error(f"Error in assistant chat: {e}")
            return {"type": "error", "message": f"Unexpected error: {e}"}

    def _looks_like_diagram_request(self, response: str) -> bool:
        """Heuristic to detect if response contains a diagram specification."""
        diagram_indicators = [
            '"nodes":',
            '"connections":',
            '"clusters":',
            "diagram",
            "architecture",
            "create",
            "generate",
        ]
        response_lower = response.lower()
        return any(indicator in response_lower for indicator in diagram_indicators)

    def _parse_and_create_diagram(self, response: str) -> Dict[str, Any]:
        """Parse response for diagram specification and create diagram if found."""
        try:
            # Try to parse as diagram specification and generate image
            # Extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1

            if json_start != -1 and json_end > json_start:
                json_content = response[json_start:json_end]
                self.logger.info(f"Extracted JSON: {json_content}")

                try:
                    diagram_data = json.loads(json_content)
                    self.logger.info(f"Parsed diagram data: {diagram_data}")

                    # Validate and create diagram
                    diagram_spec = DiagramRequest(**diagram_data)
                    image_path = self.diagram_tools.create_diagram(
                        name=diagram_spec.name,
                        nodes=diagram_spec.nodes,
                        connections=diagram_spec.connections,
                        clusters=diagram_spec.clusters,
                    )

                    return {
                        "type": "diagram",
                        "diagram_path": image_path,
                        "message": "Diagram generated successfully!",
                        "specification": diagram_spec.model_dump(),
                        "response": response,
                    }

                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON decode error: {e}")
                    return {
                        "type": "error",
                        "message": f"Failed to parse JSON response: {e}",
                    }
                except Exception as e:
                    self.logger.error(f"Diagram creation error: {e}")
                    return {
                        "type": "error",
                        "message": f"Failed to create diagram: {e}",
                    }
            else:
                self.logger.warning("No JSON found in response")
                return {"type": "text", "response": response}

        except Exception as e:
            self.logger.error(f"Failed to parse diagram from assistant response: {e}")
            return {"type": "error", "message": f"Failed to parse diagram: {e}"}

    def get_supported_components(self) -> Dict[str, str]:
        """Get list of supported diagram components with descriptions."""
        node_types = self.diagram_tools.get_supported_node_types()
        return {
            node_type: self.diagram_tools.get_node_description(node_type)
            for node_type in node_types
        }

    async def health_check(self) -> Dict[str, bool]:
        """Check health of all chat agent components."""
        llm_health = await self.llm_client.health_check()
        return {
            "llm_client": llm_health,
            "diagram_tools": True,  # DiagramTools doesn't have async dependencies
        }

    def cleanup(self):
        """Clean up chat agent resources."""
        self.diagram_tools.cleanup()
