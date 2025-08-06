import logging
import tempfile
from typing import Any, Dict, List, Optional, Protocol


class DiagramRenderingService(Protocol):
    """Protocol for diagram rendering service."""

    def create_diagram(
        self,
        name: str,
        nodes: List[Dict[str, Any]],
        connections: List[Dict[str, Any]],
        clusters: Optional[List[Dict[str, Any]]] = None,
    ) -> str: ...

    def get_supported_node_types(self) -> List[str]: ...

    def get_node_description(self, node_type: str) -> str: ...


class DiagramsPackageRenderingService:
    """Diagrams package-based rendering service implementation."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def create_diagram(
        self,
        name: str,
        nodes: List[Dict[str, Any]],
        connections: List[Dict[str, Any]],
        clusters: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Create a diagram and return the image path."""
        try:
            from diagrams import Diagram
            from diagrams.aws.compute import EC2, Lambda
            from diagrams.aws.database import RDS
            from diagrams.aws.integration import SQS
            from diagrams.aws.management import CloudWatch
            from diagrams.aws.network import VPC, InternetGateway, SecurityGroup, Subnet
            from diagrams.aws.storage import S3

            # Create a temporary file for the diagram
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                image_path = tmp_file.name

            # Create the diagram
            with Diagram(
                name,
                show=False,
                filename=image_path.replace(".png", ""),
                direction="TB",
            ):
                # Create node mapping
                node_objects = {}

                for node in nodes:
                    node_id = node["id"]
                    node_type = node["type"]
                    node_label = node.get("label", node_id)

                    # Map node types to diagram components
                    if node_type == "aws_ec2":
                        node_objects[node_id] = EC2(node_label)
                    elif node_type == "aws_lambda":
                        node_objects[node_id] = Lambda(node_label)
                    elif node_type == "aws_rds":
                        node_objects[node_id] = RDS(node_label)
                    elif node_type == "aws_vpc":
                        node_objects[node_id] = VPC(node_label)
                    elif node_type == "aws_internet_gateway":
                        node_objects[node_id] = InternetGateway(node_label)
                    elif node_type == "aws_subnet":
                        node_objects[node_id] = Subnet(node_label)
                    elif node_type == "aws_security_group":
                        node_objects[node_id] = SecurityGroup(node_label)
                    elif node_type == "aws_sqs":
                        node_objects[node_id] = SQS(node_label)
                    elif node_type == "aws_s3":
                        node_objects[node_id] = S3(node_label)
                    elif node_type == "aws_cloudwatch":
                        node_objects[node_id] = CloudWatch(node_label)
                    elif node_type == "aws_api_gateway":
                        # Use Lambda as a proxy for API Gateway
                        node_objects[node_id] = Lambda(f"API Gateway - {node_label}")
                    elif node_type == "aws_dynamodb":
                        # Use RDS as a proxy for DynamoDB
                        node_objects[node_id] = RDS(f"DynamoDB - {node_label}")
                    else:
                        # Default to EC2 for unknown types
                        node_objects[node_id] = EC2(node_label)

                # Create connections
                for connection in connections:
                    source_id = connection["source"]
                    target_id = connection["target"]

                    if source_id in node_objects and target_id in node_objects:
                        node_objects[source_id] >> node_objects[target_id]

            self.logger.info(f"Created diagram at: {image_path}")
            return image_path

        except Exception as e:
            self.logger.error(f"Error creating diagram: {e}")
            raise

    def get_supported_node_types(self) -> List[str]:
        """Get list of supported node types."""
        return [
            "aws_ec2",
            "aws_lambda",
            "aws_rds",
            "aws_vpc",
            "aws_internet_gateway",
            "aws_subnet",
            "aws_security_group",
            "aws_sqs",
            "aws_s3",
            "aws_cloudwatch",
            "aws_api_gateway",
            "aws_dynamodb",
        ]

    def get_node_description(self, node_type: str) -> str:
        """Get description of a node type."""
        descriptions = {
            "aws_ec2": "Amazon EC2 Instance",
            "aws_lambda": "AWS Lambda Function",
            "aws_rds": "Amazon RDS Database",
            "aws_vpc": "Amazon VPC",
            "aws_internet_gateway": "Internet Gateway",
            "aws_subnet": "VPC Subnet",
            "aws_security_group": "Security Group",
            "aws_sqs": "Amazon SQS Queue",
            "aws_s3": "Amazon S3 Bucket",
            "aws_cloudwatch": "Amazon CloudWatch",
            "aws_api_gateway": "Amazon API Gateway",
            "aws_dynamodb": "Amazon DynamoDB",
        }
        return descriptions.get(node_type, "Unknown node type")

    def get_nodes_by_provider(self, provider: str) -> Dict[str, Any]:
        """Get all nodes for a specific provider."""
        if provider.lower() == "aws":
            return {
                "compute": ["aws_ec2", "aws_lambda"],
                "database": ["aws_rds", "aws_dynamodb"],
                "network": [
                    "aws_vpc",
                    "aws_internet_gateway",
                    "aws_subnet",
                    "aws_security_group",
                ],
                "integration": ["aws_sqs", "aws_api_gateway"],
                "storage": ["aws_s3"],
                "management": ["aws_cloudwatch"],
            }
        return {}

    def get_providers(self) -> List[str]:
        """Get list of available providers."""
        return ["aws"]

    def cleanup(self) -> None:
        """Clean up resources."""
        # Clean up temporary files
        pass
