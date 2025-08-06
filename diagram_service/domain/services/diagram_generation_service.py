from typing import Any, Dict, List, Optional

from ..aggregates.diagram import Diagram
from ..entities.diagram_connection import DiagramConnection
from ..entities.diagram_node import DiagramNode
from ..value_objects.diagram_id import DiagramId
from ..value_objects.node_type import NodeType


class DiagramGenerationService:
    """Domain service for diagram generation business logic."""

    def create_diagram_from_specification(
        self,
        name: str,
        nodes: List[Dict[str, Any]],
        connections: List[Dict[str, Any]],
        clusters: Optional[List[Dict[str, Any]]] = None,
    ) -> Diagram:
        """Create a diagram from a specification."""
        diagram_id = DiagramId.generate()

        # Create diagram aggregate
        diagram = Diagram(
            id=diagram_id, name=name, nodes=[], connections=[], clusters=clusters or []
        )

        # Add nodes
        for node_data in nodes:
            node = DiagramNode(
                id=node_data["id"],
                type=NodeType(value=node_data["type"]),
                label=node_data["label"],
                cluster=node_data.get("cluster"),
            )
            diagram.add_node(node)

        # Add connections
        for connection_data in connections:
            connection = DiagramConnection(
                source=connection_data["source"],
                target=connection_data["target"],
                label=connection_data.get("label"),
            )
            diagram.add_connection(connection)

        return diagram

    def validate_diagram_specification(
        self, nodes: List[Dict[str, Any]], connections: List[Dict[str, Any]]
    ) -> bool:
        """Validate diagram specification."""
        if not nodes:
            return False

        # Check for duplicate node IDs
        node_ids = [node["id"] for node in nodes]
        if len(node_ids) != len(set(node_ids)):
            return False

        # Check that all connections reference existing nodes
        for connection in connections:
            if (
                connection["source"] not in node_ids
                or connection["target"] not in node_ids
            ):
                return False

        return True

    def get_diagram_statistics(self, diagram: Diagram) -> Dict[str, Any]:
        """Get statistics about a diagram."""
        return {
            "node_count": diagram.get_node_count(),
            "connection_count": diagram.get_connection_count(),
            "cluster_count": len(diagram.clusters),
            "is_valid": diagram.is_valid(),
            "created_at": diagram.created_at,
            "updated_at": diagram.updated_at,
        }
