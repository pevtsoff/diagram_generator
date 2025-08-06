from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator

from ..entities.diagram_connection import DiagramConnection
from ..entities.diagram_node import DiagramNode
from ..value_objects.diagram_id import DiagramId
from ..value_objects.node_type import NodeType


class Diagram(BaseModel):
    """Aggregate root representing a complete diagram."""

    id: DiagramId = Field(..., description="Unique diagram identifier")
    name: str = Field(..., min_length=1, max_length=100, description="Diagram name")
    nodes: List[DiagramNode] = Field(default_factory=list, description="Diagram nodes")
    connections: List[DiagramConnection] = Field(
        default_factory=list, description="Diagram connections"
    )
    clusters: List[Dict[str, Any]] = Field(
        default_factory=list, description="Diagram clusters"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )

    @validator("name")
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Diagram name cannot be empty")
        return v.strip()

    def add_node(self, node: DiagramNode) -> None:
        """Add a node to the diagram."""
        # Check if node ID already exists
        if any(n.id == node.id for n in self.nodes):
            raise ValueError(f"Node with ID {node.id} already exists")

        self.nodes.append(node)
        self.updated_at = datetime.utcnow()

    def add_connection(self, connection: DiagramConnection) -> None:
        """Add a connection to the diagram."""
        # Validate that both nodes exist
        source_exists = any(n.id == connection.source for n in self.nodes)
        target_exists = any(n.id == connection.target for n in self.nodes)

        if not source_exists:
            raise ValueError(f"Source node {connection.source} does not exist")
        if not target_exists:
            raise ValueError(f"Target node {connection.target} does not exist")

        # Check if connection already exists
        if any(
            c.source == connection.source and c.target == connection.target
            for c in self.connections
        ):
            raise ValueError(
                f"Connection from {connection.source} to {connection.target} already exists"
            )

        self.connections.append(connection)
        self.updated_at = datetime.utcnow()

    def get_node_by_id(self, node_id: str) -> Optional[DiagramNode]:
        """Get a node by its ID."""
        return next((node for node in self.nodes if node.id == node_id), None)

    def get_nodes_by_type(self, node_type: NodeType) -> List[DiagramNode]:
        """Get all nodes of a specific type."""
        return [node for node in self.nodes if node.type == node_type]

    def get_connections_for_node(self, node_id: str) -> List[DiagramConnection]:
        """Get all connections involving a specific node."""
        return [
            conn
            for conn in self.connections
            if conn.source == node_id or conn.target == node_id
        ]

    def is_valid(self) -> bool:
        """Check if the diagram is valid (has nodes and valid connections)."""
        if not self.nodes:
            return False

        # Check that all connections reference existing nodes
        node_ids = {node.id for node in self.nodes}
        for connection in self.connections:
            if connection.source not in node_ids or connection.target not in node_ids:
                return False

        return True

    def get_node_count(self) -> int:
        """Get the number of nodes in the diagram."""
        return len(self.nodes)

    def get_connection_count(self) -> int:
        """Get the number of connections in the diagram."""
        return len(self.connections)

    class Config:
        arbitrary_types_allowed = True
