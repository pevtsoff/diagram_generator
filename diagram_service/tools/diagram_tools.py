import os
import tempfile
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import uuid
import importlib
import inspect
from diagrams import Diagram, Cluster

class DiagramTools:
    """Tools for creating diagrams using the diagrams package with dynamic node discovery."""
    
    def __init__(self):
        # Use environment variable for images directory or fallback to temp directory
        images_dir = os.getenv("IMAGES_DIR")
        if images_dir:
            self.images_dir = images_dir
        else:
            self.images_dir = os.path.join(tempfile.gettempdir(), "diagram_service_images")
        
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Log the images directory being used
        logger = logging.getLogger(__name__)
        logger.info(f"Using images directory: {self.images_dir}")
        
        # Dynamically discover all available nodes
        self.supported_node_types = self._discover_available_nodes()
        logger.info(f"Discovered {len(self.supported_node_types)} node types")
        
    def _discover_available_nodes(self) -> Dict[str, Any]:
        """Dynamically discover all available node types from the diagrams package."""
        discovered_nodes = {}
        
        # Dynamically discover all available providers and their modules
        import os
        import diagrams
        
        # Get the diagrams package directory
        diagrams_path = os.path.dirname(diagrams.__file__)
        
        # Discover all provider directories
        for item in os.listdir(diagrams_path):
            provider_dir = os.path.join(diagrams_path, item)
            
            # Skip if not a directory or if it's a special directory
            if not os.path.isdir(provider_dir) or item.startswith('_') or item in ['__pycache__']:
                continue
                
            provider = item
            
            # Discover all modules within this provider
            for module_file in os.listdir(provider_dir):
                if module_file.endswith('.py') and not module_file.startswith('_') and module_file != '__init__.py':
                    module_name = f'diagrams.{provider}.{module_file[:-3]}'  # Remove .py extension
                    
                    try:
                        module = importlib.import_module(module_name)
                        self._discover_nodes_in_module(module, discovered_nodes, provider)
                    except ImportError:
                        logging.debug(f"Module {module_name} not available")
                    except Exception as e:
                        logging.debug(f"Error exploring module {module_name}: {e}")
        
        return discovered_nodes
    
    def _discover_nodes_in_module(self, module: Any, discovered_nodes: Dict[str, Any], provider: str):
        """Discover node classes in a module."""
        for item_name in dir(module):
            if item_name.startswith('_'):
                continue
                
            item = getattr(module, item_name)
            
            # Check if it's a class that could be a diagram node
            if (inspect.isclass(item) and 
                hasattr(item, '__module__') and 
                'diagrams' in item.__module__ and
                not item_name.startswith('_') and
                item_name not in ['Node', 'Edge', 'Diagram', 'Cluster']):
                
                # Create a normalized key for the node type
                # Convert CamelCase to snake_case and create a unique identifier
                node_key = self._normalize_node_name(item_name, provider)
                
                if node_key and node_key not in discovered_nodes:
                    discovered_nodes[node_key] = item
                    logging.debug(f"Discovered node: {node_key} -> {item.__name__}")
    
    def _normalize_node_name(self, class_name: str, provider: str) -> str:
        """Convert class name to a normalized node type identifier."""
        # Convert CamelCase to snake_case
        import re
        name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', class_name).lower()
        
        # Add provider prefix for uniqueness
        return f"{provider}_{name}"
        
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
    
    def cleanup(self) -> None:
        """Clean up temporary files."""
        # Don't clean up the shared images directory as other agents might be using it
        # In production, implement proper cleanup strategy (e.g., TTL-based cleanup)
        pass

    def get_node_description(self, node_type: str) -> str:
        """Get description of what a node type represents."""
        if node_type.lower() not in self.supported_node_types:
            return f"Unknown node type: {node_type}"
        
        # Extract provider and service from the node type
        parts = node_type.lower().split('_', 1)
        if len(parts) >= 2:
            provider, service = parts[0], parts[1]
            
            # Create a human-readable description
            provider_names = {
                'aws': 'Amazon Web Services',
                'azure': 'Microsoft Azure', 
                'gcp': 'Google Cloud Platform',
                'k8s': 'Kubernetes',
                'onprem': 'On-Premises',
                'generic': 'Generic',
                'programming': 'Programming',
                'alibabacloud': 'Alibaba Cloud',
                'digitalocean': 'DigitalOcean',
                'elastic': 'Elastic',
                'firebase': 'Firebase',
                'gis': 'GIS',
                'ibm': 'IBM Cloud',
                'oci': 'Oracle Cloud',
                'openstack': 'OpenStack',
                'outscale': 'Outscale',
                'saas': 'SaaS'
            }
            
            provider_name = provider_names.get(provider, provider.upper())
            service_name = service.replace('_', ' ').title()
            
            return f"{provider_name} {service_name} service"
        
        return f"Cloud service component: {node_type}"
    
    def get_nodes_by_provider(self, provider: str) -> Dict[str, Any]:
        """Get all nodes for a specific provider."""
        provider_nodes = {}
        for node_type, node_class in self.supported_node_types.items():
            if node_type.startswith(f"{provider}_"):
                provider_nodes[node_type] = node_class
        return provider_nodes
    
    def get_providers(self) -> List[str]:
        """Get list of available providers."""
        providers = set()
        for node_type in self.supported_node_types.keys():
            provider = node_type.split('_')[0]
            providers.add(provider)
        return sorted(list(providers)) 