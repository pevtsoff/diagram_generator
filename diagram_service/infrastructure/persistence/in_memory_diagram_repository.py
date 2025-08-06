from typing import Dict, List, Optional

from ...domain.aggregates.diagram import Diagram
from ...domain.repositories.diagram_repository import DiagramRepository
from ...domain.value_objects.diagram_id import DiagramId


class InMemoryDiagramRepository(DiagramRepository):
    """In-memory implementation of diagram repository."""

    def __init__(self):
        self._diagrams: Dict[str, Diagram] = {}

    async def save(self, diagram: Diagram) -> None:
        """Save a diagram to memory."""
        self._diagrams[str(diagram.id)] = diagram

    async def find_by_id(self, diagram_id: DiagramId) -> Optional[Diagram]:
        """Find a diagram by ID."""
        return self._diagrams.get(str(diagram_id))

    async def find_all(self) -> List[Diagram]:
        """Get all diagrams."""
        return list(self._diagrams.values())

    async def delete(self, diagram_id: DiagramId) -> None:
        """Delete a diagram by ID."""
        self._diagrams.pop(str(diagram_id), None)

    async def find_by_name(self, name: str) -> Optional[Diagram]:
        """Find a diagram by name."""
        for diagram in self._diagrams.values():
            if diagram.name == name:
                return diagram
        return None
