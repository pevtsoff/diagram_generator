import logging
import asyncio
from typing import Optional, Dict, Any, List, Union
from pathlib import Path

from diagram_service.tools.diagram_tools import DiagramTools
from diagram_service.llm.gemini_client import GeminiClient, DiagramRequest


class DiagramAgent:
    """Main agent for creating diagrams from natural language descriptions."""
    
    def __init__(self, gemini_api_key: str, use_mock: bool = False):
        """Initialize the diagram agent with LLM client and tools."""
        self.use_mock = use_mock
        if use_mock:
            from diagram_service.llm.mock_client import MockLLMClient
            self.llm_client: Union[GeminiClient, 'MockLLMClient'] = MockLLMClient()
        else:
            self.llm_client: Union[GeminiClient, 'MockLLMClient'] = GeminiClient(gemini_api_key)
        self.diagram_tools = DiagramTools()
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
            
            self.logger.info(f"Generated diagram specification: {diagram_spec.dict()}")
            
            # Step 3: Create the diagram using tools
            image_path = self.diagram_tools.create_diagram(
                name=diagram_spec.name,
                nodes=diagram_spec.nodes,
                connections=diagram_spec.connections,
                clusters=diagram_spec.clusters
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
        self.logger.info(f"Processing assistant chat: {user_message}")
        
        try:
            # Get supported node types
            supported_node_types = self.diagram_tools.get_supported_node_types()
            
            # Use LLM for assistant-style response
            response = await self.llm_client.assistant_chat(user_message, supported_node_types)
            
            self.logger.info(f"LLM Response: {response}")
            
            # Try to detect if response contains a diagram specification
            if self._looks_like_diagram_request(response):
                try:
                    # Try to parse as diagram specification and generate image
                    import json
                    
                    # Extract JSON from response
                    json_start = response.find('{')
                    json_end = response.rfind('}') + 1
                    
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
                                clusters=diagram_spec.clusters
                            )
                            
                            return {
                                "type": "diagram",
                                "diagram_path": image_path,
                                "message": "Diagram generated successfully!",
                                "specification": diagram_spec.model_dump(),
                                "response": response
                            }
                            
                        except json.JSONDecodeError as e:
                            self.logger.error(f"JSON decode error: {e}")
                            return {
                                "type": "error",
                                "message": f"Failed to parse JSON response: {e}"
                            }
                        except Exception as e:
                            self.logger.error(f"Diagram creation error: {e}")
                            return {
                                "type": "error", 
                                "message": f"Failed to create diagram: {e}"
                            }
                    else:
                        self.logger.warning("No JSON found in response")
                        return {
                            "type": "text",
                            "response": response
                        }
                        
                except Exception as e:
                    self.logger.error(f"Failed to parse diagram from assistant response: {e}")
                    return {
                        "type": "error",
                        "message": f"Failed to parse diagram: {e}"
                    }
            
            # Return as text response
            return {
                "type": "text",
                "response": response,
                "supported_node_types": supported_node_types
            }
            
        except Exception as e:
            self.logger.error(f"Error in assistant chat: {e}")
            return {
                "type": "error",
                "message": f"Unexpected error: {e}"
            }
    
    def _looks_like_diagram_request(self, response: str) -> bool:
        """Heuristic to detect if response contains a diagram specification."""
        diagram_indicators = [
            '"nodes":', '"connections":', '"clusters":',
            'diagram', 'architecture', 'create', 'generate'
        ]
        response_lower = response.lower()
        return any(indicator in response_lower for indicator in diagram_indicators)
    
    def get_supported_components(self) -> Dict[str, str]:
        """Get list of supported diagram components with descriptions."""
        node_types = self.diagram_tools.get_supported_node_types()
        return {
            node_type: self.diagram_tools.get_node_description(node_type)
            for node_type in node_types
        }
    
    def health_check(self) -> Dict[str, bool]:
        """Check health of all agent components."""
        return {
            "llm_client": self.llm_client.health_check(),
            "diagram_tools": True  # DiagramTools doesn't have async dependencies
        }
    
    def cleanup(self):
        """Clean up agent resources."""
        self.diagram_tools.cleanup()


class DiagramAgentPool:
    """Pool of diagram agents for handling concurrent requests."""
    
    def __init__(self, gemini_api_key: str, pool_size: int = 3, use_mock: bool = False):
        """Initialize agent pool."""
        self.gemini_api_key = gemini_api_key
        self.pool_size = pool_size
        self.use_mock = use_mock
        self.agents: List[DiagramAgent] = []
        self.semaphore = asyncio.Semaphore(pool_size)
        
    async def get_agent(self) -> DiagramAgent:
        """Get an available agent from the pool."""
        await self.semaphore.acquire()
        
        # Create new agent for this request (stateless)
        agent = DiagramAgent(self.gemini_api_key, use_mock=self.use_mock)
        return agent
    
    def release_agent(self, agent: DiagramAgent):
        """Release agent back to pool."""
        agent.cleanup()
        self.semaphore.release()
    
    async def execute_with_agent(self, operation):
        """Execute operation with an agent from the pool."""
        agent = await self.get_agent()
        try:
            return await operation(agent)
        finally:
            self.release_agent(agent) 