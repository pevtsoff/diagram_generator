import json
import logging
from typing import List
from diagram_service.llm.gemini_client import DiagramRequest


class MockLLMClient:
    """Mock LLM client for local development and testing."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    async def generate_diagram_specification(self, user_description: str, supported_node_types: List[str]) -> DiagramRequest:
        """Generate a mock diagram specification."""
        
        self.logger.info(f"Mock LLM: Processing description: {user_description}")
        
        # Simple heuristics to generate reasonable diagrams based on keywords
        description_lower = user_description.lower()
        
        # Check for specific patterns in the user's request
        if "nginx" in description_lower and "api" in description_lower:
            return self._create_nginx_api_diagram(user_description)
        elif "user" in description_lower and "api" in description_lower:
            return self._create_user_api_diagram(user_description)
        elif "redis" in description_lower:
            return self._create_redis_diagram(user_description)
        elif "database" in description_lower and "api" in description_lower:
            return self._create_api_database_diagram(user_description)
        # Determine diagram type and components based on keywords
        elif "microservices" in description_lower:
            return self._create_microservices_diagram(user_description)
        elif "web app" in description_lower or "web application" in description_lower:
            return self._create_web_app_diagram(user_description)
        elif "database" in description_lower and "load balancer" in description_lower:
            return self._create_simple_web_db_diagram(user_description)
        else:
            return self._create_default_diagram(user_description)
    
    async def assistant_chat(self, user_message: str, supported_node_types: List[str]) -> str:
        """Handle mock assistant chat interactions."""
        
        self.logger.info(f"Mock Assistant: Processing message: {user_message}")
        
        message_lower = user_message.lower()
        
        # Check if this is a diagram request
        diagram_keywords = ['diagram', 'create', 'generate', 'show', 'draw', 'build', 'architecture']
        is_diagram_request = any(keyword in message_lower for keyword in diagram_keywords)
        
        if is_diagram_request:
            # Generate a diagram specification in JSON format
            try:
                diagram_spec = await self.generate_diagram_specification(user_message, supported_node_types)
                return json.dumps(diagram_spec.model_dump(), indent=2)
            except Exception as e:
                self.logger.error(f"Failed to generate diagram specification: {e}")
                return self._general_response(user_message)
        elif "components" in message_lower or "supported" in message_lower:
            return self._list_components_response(supported_node_types)
        elif "help" in message_lower or "how" in message_lower:
            return self._help_response()
        else:
            return self._general_response(user_message)
    
    async def health_check(self) -> bool:
        """Mock health check - always returns True."""
        return True
    
    def _create_microservices_diagram(self, description: str) -> DiagramRequest:
        """Create a mock microservices diagram."""
        return DiagramRequest(
            name="Microservices Architecture",
            nodes=[
                {"id": "gateway", "type": "aws_alb", "label": "API Gateway"},
                {"id": "auth", "type": "aws_ec2", "label": "Auth Service"},
                {"id": "payment", "type": "aws_ec2", "label": "Payment Service"},
                {"id": "order", "type": "aws_ec2", "label": "Order Service"},
                {"id": "queue", "type": "aws_sqs", "label": "Message Queue"},
                {"id": "db", "type": "aws_rds", "label": "Shared Database"},
                {"id": "monitor", "type": "aws_cloudwatch", "label": "Monitoring"}
            ],
            connections=[
                {"source": "gateway", "target": "auth"},
                {"source": "gateway", "target": "payment"},
                {"source": "gateway", "target": "order"},
                {"source": "auth", "target": "db"},
                {"source": "payment", "target": "db"},
                {"source": "order", "target": "db"},
                {"source": "payment", "target": "queue"},
                {"source": "order", "target": "queue"},
                {"source": "monitor", "target": "auth"},
                {"source": "monitor", "target": "payment"},
                {"source": "monitor", "target": "order"}
            ],
            clusters=[
                {"name": "Microservices", "nodes": ["auth", "payment", "order"]}
            ]
        )
    
    def _create_web_app_diagram(self, description: str) -> DiagramRequest:
        """Create a mock web application diagram."""
        return DiagramRequest(
            name="Web Application Architecture",
            nodes=[
                {"id": "lb", "type": "aws_alb", "label": "Load Balancer"},
                {"id": "web1", "type": "aws_ec2", "label": "Web Server 1"},
                {"id": "web2", "type": "aws_ec2", "label": "Web Server 2"},
                {"id": "db", "type": "aws_rds", "label": "Database"}
            ],
            connections=[
                {"source": "lb", "target": "web1"},
                {"source": "lb", "target": "web2"},
                {"source": "web1", "target": "db"},
                {"source": "web2", "target": "db"}
            ],
            clusters=[
                {"name": "Web Tier", "nodes": ["web1", "web2"]}
            ]
        )
    
    def _create_simple_web_db_diagram(self, description: str) -> DiagramRequest:
        """Create a simple web-database diagram."""
        return DiagramRequest(
            name="Simple Web Application",
            nodes=[
                {"id": "lb", "type": "aws_alb", "label": "Load Balancer"},
                {"id": "web", "type": "aws_ec2", "label": "Web Server"},
                {"id": "db", "type": "aws_rds", "label": "Database"}
            ],
            connections=[
                {"source": "lb", "target": "web"},
                {"source": "web", "target": "db"}
            ]
        )
    
    def _create_default_diagram(self, description: str) -> DiagramRequest:
        """Create a default diagram when no specific pattern is detected."""
        return DiagramRequest(
            name="Cloud Architecture",
            nodes=[
                {"id": "web", "type": "aws_ec2", "label": "Application Server"},
                {"id": "db", "type": "aws_rds", "label": "Database"},
                {"id": "storage", "type": "aws_s3", "label": "File Storage"}
            ],
            connections=[
                {"source": "web", "target": "db"},
                {"source": "web", "target": "storage"}
            ]
        )
    
    def _create_nginx_api_diagram(self, description: str) -> DiagramRequest:
        """Create a diagram with Nginx, API, and Redis."""
        return DiagramRequest(
            name="Nginx API Architecture",
            nodes=[
                {"id": "user", "type": "onprem_user", "label": "User"},
                {"id": "nginx", "type": "aws_alb", "label": "Nginx"},
                {"id": "api", "type": "aws_ec2", "label": "API Server"},
                {"id": "redis", "type": "onprem_redis", "label": "Redis Cache"},
                {"id": "database", "type": "aws_rds", "label": "Database"}
            ],
            connections=[
                {"source": "user", "target": "nginx"},
                {"source": "nginx", "target": "api"},
                {"source": "api", "target": "redis"},
                {"source": "api", "target": "database"}
            ]
        )
    
    def _create_user_api_diagram(self, description: str) -> DiagramRequest:
        """Create a diagram with User and API components."""
        return DiagramRequest(
            name="User API Architecture",
            nodes=[
                {"id": "user", "type": "onprem_user", "label": "User"},
                {"id": "api", "type": "aws_ec2", "label": "API Server"},
                {"id": "database", "type": "aws_rds", "label": "Database"}
            ],
            connections=[
                {"source": "user", "target": "api"},
                {"source": "api", "target": "database"}
            ]
        )
    
    def _create_redis_diagram(self, description: str) -> DiagramRequest:
        """Create a diagram with Redis cache."""
        return DiagramRequest(
            name="Redis Cache Architecture",
            nodes=[
                {"id": "api", "type": "aws_ec2", "label": "API Server"},
                {"id": "redis", "type": "onprem_redis", "label": "Redis Cache"},
                {"id": "database", "type": "aws_rds", "label": "Database"}
            ],
            connections=[
                {"source": "api", "target": "redis"},
                {"source": "api", "target": "database"}
            ]
        )
    
    def _create_api_database_diagram(self, description: str) -> DiagramRequest:
        """Create a diagram with API and Database."""
        return DiagramRequest(
            name="API Database Architecture",
            nodes=[
                {"id": "api", "type": "aws_ec2", "label": "API Server"},
                {"id": "database", "type": "aws_rds", "label": "Database"}
            ],
            connections=[
                {"source": "api", "target": "database"}
            ]
        )
    
    def _generate_diagram_response(self, message: str, supported_types: List[str]) -> str:
        """Generate a response about creating diagrams."""
        return f"""I can help you create cloud architecture diagrams! Based on your message, I can generate a diagram specification.

Available components: {', '.join(supported_types[:10])}{'...' if len(supported_types) > 10 else ''}

Try describing your architecture like:
- "Create a web application with load balancer and database"
- "Design a microservices system with API gateway"
- "Build a simple 3-tier architecture"

Would you like me to create a diagram for a specific architecture?"""
    
    def _list_components_response(self, supported_types: List[str]) -> str:
        """List available components."""
        return f"""Here are the supported cloud components:

AWS Services: ec2, rds, alb, elb, sqs, s3, cloudwatch, route53, iam
GCP Services: compute_engine, gke, cloud_sql, gcp_load_balancer  
Azure Services: virtual_machines, azure_sql, azure_load_balancer

Total: {len(supported_types)} components available.

You can use these in your architecture descriptions, and I'll map them to the appropriate diagram elements."""
    
    def _help_response(self) -> str:
        """Provide help information."""
        return """I'm a cloud architecture diagram assistant! Here's how I can help:

🏗️ **Create Diagrams**: Describe your architecture in natural language
   - "Build a web app with load balancer and 2 servers"
   - "Design microservices with API gateway and databases"

❓ **Answer Questions**: Ask about cloud architecture patterns
   - "What's the best way to design a scalable web app?"
   - "How do I set up monitoring for microservices?"

📋 **List Components**: See what cloud services are available
   - "What components are supported?"
   - "Show me AWS services"

Just describe what you want to build, and I'll help you create a diagram or explain the concepts!"""
    
    def _general_response(self, message: str) -> str:
        """General response for other messages."""
        return f"""I'm here to help with cloud architecture diagrams! 

Your message: "{message}"

I can help you:
- Create diagrams from descriptions
- Explain cloud architecture patterns  
- List available components
- Answer questions about cloud design

Try asking me to "create a diagram for..." or "explain how to..." and I'll assist you!""" 