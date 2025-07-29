import os
import tempfile
from typing import List, Dict, Any, Optional
from pathlib import Path
import uuid
from diagrams import Diagram, Cluster
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB, ALB, Route53
from diagrams.aws.integration import SQS
from diagrams.aws.management import Cloudwatch
from diagrams.aws.general import General
from diagrams.aws.security import IAM
from diagrams.aws.storage import S3
from diagrams.gcp.compute import ComputeEngine, GKE
from diagrams.gcp.database import SQL
from diagrams.gcp.network import LoadBalancing
from diagrams.azure.compute import VM
from diagrams.azure.database import SQLDatabases
from diagrams.azure.network import LoadBalancers


class DiagramTools:
    """Tools for creating diagrams using the diagrams package."""
    
    def __init__(self):
        # Use a shared images directory for easier serving
        import os
        self.images_dir = os.path.join(tempfile.gettempdir(), "diagram_service_images")
        os.makedirs(self.images_dir, exist_ok=True)
        self.supported_node_types = {
            # AWS Services
            "ec2": EC2,
            "rds": RDS,
            "elb": ELB,
            "alb": ALB,
            "sqs": SQS,
            "s3": S3,
            "cloudwatch": Cloudwatch,
            "route53": Route53,
            "iam": IAM,
            "general": General,
            # GCP Services  
            "compute_engine": ComputeEngine,
            "gke": GKE,
            "cloud_sql": SQL,
            "gcp_load_balancer": LoadBalancing,
            # Azure Services
            "virtual_machines": VM,
            "azure_sql": SQLDatabases,
            "azure_load_balancer": LoadBalancers,
        }
        
    def create_node(self, node_type: str, label: str) -> Any:
        """Create a diagram node of the specified type with given label."""
        if node_type.lower() not in self.supported_node_types:
            raise ValueError(f"Unsupported node type: {node_type}. Supported types: {list(self.supported_node_types.keys())}")
        
        node_class = self.supported_node_types[node_type.lower()]
        return node_class(label)
    
    def create_diagram(self, name: str, nodes: List[Dict[str, Any]], 
                      connections: List[Dict[str, Any]], 
                      clusters: Optional[List[Dict[str, Any]]] = None) -> str:
        """Create a complete diagram and return the file path."""
        diagram_id = str(uuid.uuid4())
        output_path = os.path.join(self.images_dir, f"{diagram_id}")
        
        # Clean the diagram name for filename
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        
        with Diagram(safe_name, filename=output_path, show=False, direction="LR"):
            created_nodes = {}
            created_clusters = {}
            
            # Create clusters first if specified
            if clusters:
                for cluster_info in clusters:
                    cluster_name = cluster_info["name"]
                    cluster_nodes = cluster_info.get("nodes", [])
                    
                    with Cluster(cluster_name) as cluster:
                        created_clusters[cluster_name] = cluster
                        # Create nodes within this cluster
                        for node_id in cluster_nodes:
                            node_info = next((n for n in nodes if n["id"] == node_id), None)
                            if node_info:
                                node = self.create_node(node_info["type"], node_info["label"])
                                created_nodes[node_id] = node
            
            # Create remaining nodes (those not in clusters)
            for node_info in nodes:
                node_id = node_info["id"]
                if node_id not in created_nodes:
                    node = self.create_node(node_info["type"], node_info["label"])
                    created_nodes[node_id] = node
            
            # Create connections
            for connection in connections:
                source_id = connection["source"]
                target_id = connection["target"]
                
                if source_id in created_nodes and target_id in created_nodes:
                    created_nodes[source_id] >> created_nodes[target_id]
        
        return f"{output_path}.png"
    
    def get_supported_node_types(self) -> List[str]:
        """Return list of supported node types."""
        return list(self.supported_node_types.keys())
    
    def cleanup(self):
        """Clean up temporary files."""
        # Don't clean up the shared images directory as other agents might be using it
        # In production, implement proper cleanup strategy (e.g., TTL-based cleanup)
        pass

    def get_node_description(self, node_type: str) -> str:
        """Get description of what a node type represents."""
        descriptions = {
            "ec2": "Amazon EC2 compute instances for running applications",
            "rds": "Amazon RDS managed database service", 
            "elb": "Elastic Load Balancer for distributing traffic",
            "alb": "Application Load Balancer for HTTP/HTTPS traffic",
            "sqs": "Simple Queue Service for message queuing",
            "s3": "Simple Storage Service for object storage",
            "cloudwatch": "CloudWatch monitoring and logging service",
            "route53": "Route 53 DNS service",
            "iam": "Identity and Access Management service",
            "general": "General AWS service component",
            "compute_engine": "Google Compute Engine virtual machines",
            "gke": "Google Kubernetes Engine for containers",
            "cloud_sql": "Google Cloud SQL managed database",
            "gcp_load_balancer": "Google Cloud Load Balancer",
            "virtual_machines": "Azure Virtual Machines",
            "azure_sql": "Azure SQL Database service",
            "azure_load_balancer": "Azure Load Balancer"
        }
        return descriptions.get(node_type.lower(), f"Unknown node type: {node_type}") 