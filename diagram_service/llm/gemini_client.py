import os
import json
import logging
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from pydantic import BaseModel


class DiagramRequest(BaseModel):
    """Structured request for diagram generation."""
    name: str
    nodes: List[Dict[str, Any]]
    connections: List[Dict[str, Any]]
    clusters: Optional[List[Dict[str, Any]]] = None


class GeminiClient:
    """Client for interacting with Google's Gemini API."""
    
    def __init__(self, api_key: str):
        """Initialize the Gemini client with API key."""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.logger = logging.getLogger(__name__)
        
    def _build_diagram_generation_prompt(self, user_description: str, supported_node_types: List[str]) -> str:
        """Build the prompt for diagram generation - visible prompt logic as required."""
        
        # Core prompt template - this is the visible prompt logic
        prompt_template = """
You are a cloud architecture diagram expert. Your task is to analyze a user's description and create a structured diagram specification.

SUPPORTED NODE TYPES: {node_types}

USER DESCRIPTION: "{description}"

INSTRUCTIONS:
1. Analyze the user's description and identify the components needed
2. Map each component to one of the supported node types
3. Create connections between components based on logical relationships
4. Group related components into clusters when appropriate
5. Return a valid JSON structure with the exact schema below

REQUIRED JSON SCHEMA:
{{
    "name": "Diagram Title",
    "nodes": [
        {{
            "id": "unique_node_id",
            "type": "node_type_from_supported_list", 
            "label": "Display Name"
        }}
    ],
    "connections": [
        {{
            "source": "source_node_id",
            "target": "target_node_id"
        }}
    ],
    "clusters": [
        {{
            "name": "Cluster Name",
            "nodes": ["node_id1", "node_id2"]
        }}
    ]
}}

RULES:
- Only use node types from the supported list
- Each node must have a unique ID
- Connections must reference valid node IDs
- Clusters are optional but recommended for logical grouping
- Return ONLY valid JSON, no other text

EXAMPLES OF MAPPINGS:
- "web server" → "ec2"
- "database" → "rds" 
- "load balancer" → "alb"
- "message queue" → "sqs"
- "monitoring" → "cloudwatch"
"""
        
        return prompt_template.format(
            node_types=", ".join(supported_node_types),
            description=user_description
        )
    
    def _build_assistant_prompt(self, user_message: str, supported_node_types: List[str]) -> str:
        """Build the prompt for assistant-style interactions."""
        
        assistant_prompt = """
You are a helpful cloud architecture diagram assistant. You can:
1. Generate diagram specifications based on descriptions
2. Explain how to build diagrams
3. Suggest improvements to architectures
4. Answer questions about cloud components

SUPPORTED COMPONENTS: {node_types}

USER MESSAGE: "{message}"

INSTRUCTIONS:
- If the user wants a diagram, provide a JSON specification
- If the user asks questions, provide helpful explanations
- If the user's request is unclear, ask clarifying questions
- Always be helpful and educational

RESPONSE FORMAT:
- For diagram requests: Return JSON specification
- For questions: Provide clear explanations
- For unclear requests: Ask specific clarifying questions
"""
        
        return assistant_prompt.format(
            node_types=", ".join(supported_node_types),
            message=user_message
        )

    async def generate_diagram_specification(self, user_description: str, supported_node_types: List[str]) -> DiagramRequest:
        """Generate a diagram specification from user description."""
        
        self.logger.info(f"Generating diagram specification for: {user_description}")
        
        # Build the prompt using visible prompt logic
        prompt = self._build_diagram_generation_prompt(user_description, supported_node_types)
        
        try:
            # Call Gemini API
            response = await self.model.generate_content_async(prompt)
            response_text = response.text.strip()
            
            self.logger.info(f"Raw LLM response: {response_text}")
            
            # Clean the response to extract JSON
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No valid JSON found in response")
                
            json_content = response_text[json_start:json_end]
            
            # Parse and validate the JSON
            diagram_data = json.loads(json_content)
            
            # Convert to Pydantic model for validation
            return DiagramRequest(**diagram_data)
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {e}")
            raise ValueError(f"Invalid JSON response from LLM: {e}")
        except Exception as e:
            self.logger.error(f"Error generating diagram specification: {e}")
            raise

    async def assistant_chat(self, user_message: str, supported_node_types: List[str]) -> str:
        """Handle assistant-style chat interactions."""
        
        self.logger.info(f"Processing assistant chat: {user_message}")
        
        # Check if this looks like a diagram request
        diagram_keywords = ['diagram', 'create', 'generate', 'show', 'draw', 'build', 'architecture']
        user_lower = user_message.lower()
        is_diagram_request = any(keyword in user_lower for keyword in diagram_keywords)
        
        if is_diagram_request:
            # Use the diagram generation prompt for diagram requests
            prompt = self._build_diagram_generation_prompt(user_message, supported_node_types)
        else:
            # Use the assistant prompt for general questions
            prompt = self._build_assistant_prompt(user_message, supported_node_types)
        
        try:
            # Call Gemini API
            response = await self.model.generate_content_async(prompt)
            return str(response.text.strip())
            
        except Exception as e:
            self.logger.error(f"Error in assistant chat: {e}")
            raise

    async def health_check(self) -> bool:
        """Check if the LLM client is working properly."""
        try:
            test_response = await self.model.generate_content_async("Hello, respond with 'OK'")
            return "OK" in test_response.text
        except Exception:
            return False 