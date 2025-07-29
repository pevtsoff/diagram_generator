import pytest
import tempfile
import os
from diagram_service.tools.diagram_tools import DiagramTools


class TestDiagramTools:
    """Test cases for DiagramTools class."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.diagram_tools = DiagramTools()
    
    def teardown_method(self):
        """Cleanup after each test method."""
        self.diagram_tools.cleanup()
    
    def test_get_supported_node_types(self):
        """Test getting supported node types."""
        node_types = self.diagram_tools.get_supported_node_types()
        
        assert isinstance(node_types, list)
        assert len(node_types) >= 3  # Assignment requires at least 3 types
        assert "ec2" in node_types
        assert "rds" in node_types
        assert "alb" in node_types
    
    def test_get_node_description(self):
        """Test getting node descriptions."""
        description = self.diagram_tools.get_node_description("ec2")
        assert isinstance(description, str)
        assert len(description) > 0
        assert "compute" in description.lower()
        
        # Test unknown node type
        unknown_desc = self.diagram_tools.get_node_description("unknown_type")
        assert "Unknown node type" in unknown_desc
    
    def test_create_node_valid(self):
        """Test creating valid nodes."""
        # Test AWS node
        ec2_node = self.diagram_tools.create_node("ec2", "Web Server")
        assert ec2_node is not None
        
        # Test GCP node
        gcp_node = self.diagram_tools.create_node("compute_engine", "GCP Server")
        assert gcp_node is not None
        
        # Test Azure node
        azure_node = self.diagram_tools.create_node("virtual_machines", "Azure VM")
        assert azure_node is not None
    
    def test_create_node_invalid(self):
        """Test creating invalid nodes."""
        with pytest.raises(ValueError) as exc_info:
            self.diagram_tools.create_node("invalid_type", "Test")
        assert "Unsupported node type" in str(exc_info.value)
    
    def test_create_simple_diagram(self):
        """Test creating a simple diagram."""
        nodes = [
            {"id": "web", "type": "ec2", "label": "Web Server"},
            {"id": "db", "type": "rds", "label": "Database"}
        ]
        connections = [
            {"source": "web", "target": "db"}
        ]
        
        image_path = self.diagram_tools.create_diagram(
            name="Simple Web App",
            nodes=nodes,
            connections=connections
        )
        
        assert isinstance(image_path, str)
        assert image_path.endswith(".png")
        assert os.path.exists(image_path)
    
    def test_create_diagram_with_clusters(self):
        """Test creating a diagram with clusters."""
        nodes = [
            {"id": "web1", "type": "ec2", "label": "Web Server 1"},
            {"id": "web2", "type": "ec2", "label": "Web Server 2"},
            {"id": "db", "type": "rds", "label": "Database"},
            {"id": "lb", "type": "alb", "label": "Load Balancer"}
        ]
        connections = [
            {"source": "lb", "target": "web1"},
            {"source": "lb", "target": "web2"},
            {"source": "web1", "target": "db"},
            {"source": "web2", "target": "db"}
        ]
        clusters = [
            {"name": "Web Tier", "nodes": ["web1", "web2"]}
        ]
        
        image_path = self.diagram_tools.create_diagram(
            name="Clustered Web App",
            nodes=nodes,
            connections=connections,
            clusters=clusters
        )
        
        assert isinstance(image_path, str)
        assert image_path.endswith(".png")
        assert os.path.exists(image_path)
    
    def test_temp_directory_creation(self):
        """Test that temporary directory is created."""
        assert os.path.exists(self.diagram_tools.temp_dir)
        assert os.path.isdir(self.diagram_tools.temp_dir)
    
    def test_cleanup(self):
        """Test cleanup functionality."""
        temp_dir = self.diagram_tools.temp_dir
        assert os.path.exists(temp_dir)
        
        self.diagram_tools.cleanup()
        assert not os.path.exists(temp_dir) 