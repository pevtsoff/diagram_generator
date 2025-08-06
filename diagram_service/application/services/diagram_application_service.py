import logging
from typing import List, Optional

from ...domain.repositories.diagram_repository import DiagramRepository

logger = logging.getLogger(__name__)
from ...domain.services.diagram_generation_service import DiagramGenerationService
from ...domain.value_objects.diagram_id import DiagramId
from ..commands.generate_diagram_command import (
    CreateDiagramCommand,
    GenerateDiagramCommand,
)
from ..dtos.diagram_dtos import (
    CreateDiagramResponse,
    DiagramDetailsResponse,
    GenerateDiagramFromDescriptionResponse,
)
from ..queries.get_diagram_query import (
    GetAllDiagramsQuery,
    GetDiagramByIdQuery,
    GetDiagramByNameQuery,
)


class DiagramApplicationService:
    """Application service for diagram operations."""

    def __init__(
        self,
        diagram_repository: DiagramRepository,
        diagram_generation_service: DiagramGenerationService,
        diagram_rendering_service=None,
    ):
        self.diagram_repository = diagram_repository
        self.diagram_generation_service = diagram_generation_service
        self.diagram_rendering_service = diagram_rendering_service

    @classmethod
    def create(
        cls,
        diagram_repository: DiagramRepository,
        diagram_generation_service: DiagramGenerationService,
        diagram_rendering_service=None,
    ):
        return cls(
            diagram_repository=diagram_repository,
            diagram_generation_service=diagram_generation_service,
            diagram_rendering_service=diagram_rendering_service,
        )

    async def generate_diagram_from_description(
        self, command: GenerateDiagramCommand
    ) -> GenerateDiagramFromDescriptionResponse:
        """Generate a diagram from natural language description."""
        try:
            # Get LLM service and rendering service from container
            # For now, we'll create a simple diagram specification
            # In a full implementation, this would call the LLM service

            # Parse the description to determine the architecture type
            description_lower = command.description.lower()

            if "ec2" in description_lower and "rds" in description_lower:
                # EC2 + RDS Architecture
                diagram_spec = {
                    "name": "EC2 + RDS Architecture",
                    "nodes": [
                        {
                            "id": "internet",
                            "type": "aws_internet_gateway",
                            "label": "Internet Gateway",
                        },
                        {"id": "vpc", "type": "aws_vpc", "label": "VPC"},
                        {
                            "id": "subnet",
                            "type": "aws_subnet",
                            "label": "Public Subnet",
                        },
                        {"id": "ec2", "type": "aws_ec2", "label": "EC2 Instance"},
                        {"id": "rds", "type": "aws_rds", "label": "RDS Database"},
                        {
                            "id": "security_group",
                            "type": "aws_security_group",
                            "label": "Security Group",
                        },
                    ],
                    "connections": [
                        {
                            "source": "internet",
                            "target": "vpc",
                            "label": "Internet Access",
                        },
                        {"source": "vpc", "target": "subnet", "label": "Contains"},
                        {"source": "subnet", "target": "ec2", "label": "Hosts"},
                        {
                            "source": "ec2",
                            "target": "rds",
                            "label": "Database Connection",
                        },
                        {
                            "source": "security_group",
                            "target": "ec2",
                            "label": "Protects",
                        },
                        {
                            "source": "security_group",
                            "target": "rds",
                            "label": "Protects",
                        },
                    ],
                }
            elif "fastapi" in description_lower and "sqs" in description_lower:
                # FastAPI + SQS Architecture
                diagram_spec = {
                    "name": "FastAPI + SQS Architecture",
                    "nodes": [
                        {
                            "id": "api_gateway",
                            "type": "aws_api_gateway",
                            "label": "API Gateway",
                        },
                        {
                            "id": "fastapi",
                            "type": "aws_lambda",
                            "label": "FastAPI Lambda",
                        },
                        {"id": "sqs", "type": "aws_sqs", "label": "SQS Queue"},
                        {
                            "id": "worker",
                            "type": "aws_lambda",
                            "label": "Worker Lambda",
                        },
                        {"id": "dynamodb", "type": "aws_dynamodb", "label": "DynamoDB"},
                    ],
                    "connections": [
                        {"source": "api_gateway", "target": "fastapi", "label": "HTTP"},
                        {"source": "fastapi", "target": "sqs", "label": "Send Message"},
                        {"source": "sqs", "target": "worker", "label": "Trigger"},
                        {"source": "worker", "target": "dynamodb", "label": "Write"},
                    ],
                }
            else:
                # Default architecture
                diagram_spec = {
                    "name": "AWS Architecture",
                    "nodes": [
                        {"id": "vpc", "type": "aws_vpc", "label": "VPC"},
                        {"id": "ec2", "type": "aws_ec2", "label": "EC2 Instance"},
                        {"id": "rds", "type": "aws_rds", "label": "RDS Database"},
                    ],
                    "connections": [
                        {"source": "vpc", "target": "ec2", "label": "Contains"},
                        {"source": "ec2", "target": "rds", "label": "Connects"},
                    ],
                }

            # Create diagram domain object
            diagram = self.diagram_generation_service.create_diagram_from_specification(
                name=diagram_spec["name"],
                nodes=diagram_spec["nodes"],
                connections=diagram_spec["connections"],
            )

            # Save to repository
            await self.diagram_repository.save(diagram)

            # Generate actual image if rendering service is available
            image_path = ""
            logger.info(
                f"Diagram rendering service available: {self.diagram_rendering_service is not None}"
            )
            if self.diagram_rendering_service:
                try:
                    logger.info("Attempting to create diagram image...")
                    image_path = self.diagram_rendering_service.create_diagram(
                        name=diagram_spec["name"],
                        nodes=diagram_spec["nodes"],
                        connections=diagram_spec["connections"],
                        clusters=diagram_spec.get("clusters"),
                    )
                    logger.info(f"Successfully created diagram image at: {image_path}")
                except Exception as e:
                    logger.error(f"Error generating image: {e}")
                    logger.error(f"Error type: {type(e)}")
                    import traceback

                    logger.error(f"Traceback: {traceback.format_exc()}")
                    # Continue without image if rendering fails

            return GenerateDiagramFromDescriptionResponse(
                success=True,
                diagram_id=str(diagram.id),
                image_path=image_path,
                specification=diagram_spec,
                message=f"{diagram_spec['name']} diagram generated successfully",
            )
        except Exception as e:
            return GenerateDiagramFromDescriptionResponse(
                success=False,
                image_path="",
                specification={},
                message="Failed to generate diagram",
                error=str(e),
            )

    async def create_diagram(
        self, command: CreateDiagramCommand
    ) -> CreateDiagramResponse:
        """Create a diagram from specification."""
        # Validate specification
        if not self.diagram_generation_service.validate_diagram_specification(
            command.nodes, command.connections
        ):
            raise ValueError("Invalid diagram specification")

        # Create diagram domain object
        diagram = self.diagram_generation_service.create_diagram_from_specification(
            command.name, command.nodes, command.connections, command.clusters
        )

        # Save to repository
        await self.diagram_repository.save(diagram)

        # Return response
        return CreateDiagramResponse(
            diagram_id=str(diagram.id),
            name=diagram.name,
            image_path="/tmp/diagram.png",  # This would be generated by infrastructure
            node_count=diagram.get_node_count(),
            connection_count=diagram.get_connection_count(),
            created_at=diagram.created_at,
        )

    async def get_diagram_by_id(
        self, query: GetDiagramByIdQuery
    ) -> Optional[DiagramDetailsResponse]:
        """Get diagram by ID."""
        diagram_id = DiagramId(value=query.diagram_id)
        diagram = await self.diagram_repository.find_by_id(diagram_id)

        if not diagram:
            return None

        return DiagramDetailsResponse(
            diagram_id=str(diagram.id),
            name=diagram.name,
            nodes=[
                {
                    "id": node.id,
                    "type": str(node.type),
                    "label": node.label,
                    "cluster": node.cluster,
                }
                for node in diagram.nodes
            ],
            connections=[
                {"source": conn.source, "target": conn.target, "label": conn.label}
                for conn in diagram.connections
            ],
            clusters=diagram.clusters,
            image_path="/tmp/diagram.png",  # This would be generated by infrastructure
            statistics=self.diagram_generation_service.get_diagram_statistics(diagram),
            created_at=diagram.created_at,
            updated_at=diagram.updated_at,
        )

    async def get_diagram_by_name(
        self, query: GetDiagramByNameQuery
    ) -> Optional[DiagramDetailsResponse]:
        """Get diagram by name."""
        diagram = await self.diagram_repository.find_by_name(query.name)

        if not diagram:
            return None

        return DiagramDetailsResponse(
            diagram_id=str(diagram.id),
            name=diagram.name,
            nodes=[
                {
                    "id": node.id,
                    "type": str(node.type),
                    "label": node.label,
                    "cluster": node.cluster,
                }
                for node in diagram.nodes
            ],
            connections=[
                {"source": conn.source, "target": conn.target, "label": conn.label}
                for conn in diagram.connections
            ],
            clusters=diagram.clusters,
            image_path="/tmp/diagram.png",  # This would be generated by infrastructure
            statistics=self.diagram_generation_service.get_diagram_statistics(diagram),
            created_at=diagram.created_at,
            updated_at=diagram.updated_at,
        )

    async def get_all_diagrams(
        self, query: GetAllDiagramsQuery
    ) -> List[DiagramDetailsResponse]:
        """Get all diagrams with optional pagination."""
        diagrams = await self.diagram_repository.find_all()

        # Apply pagination
        if query.offset:
            diagrams = diagrams[query.offset :]
        if query.limit:
            diagrams = diagrams[: query.limit]

        return [
            DiagramDetailsResponse(
                diagram_id=str(diagram.id),
                name=diagram.name,
                nodes=[
                    {
                        "id": node.id,
                        "type": str(node.type),
                        "label": node.label,
                        "cluster": node.cluster,
                    }
                    for node in diagram.nodes
                ],
                connections=[
                    {"source": conn.source, "target": conn.target, "label": conn.label}
                    for conn in diagram.connections
                ],
                clusters=diagram.clusters,
                image_path="/tmp/diagram.png",  # This would be generated by infrastructure
                statistics=self.diagram_generation_service.get_diagram_statistics(
                    diagram
                ),
                created_at=diagram.created_at,
                updated_at=diagram.updated_at,
            )
            for diagram in diagrams
        ]
