from typing import List, Optional, Protocol

from ..aggregates.diagram import Diagram
from ..value_objects.diagram_id import DiagramId


class DiagramRepository(Protocol):
    """Repository interface for diagram persistence."""

    async def save(self, diagram: Diagram) -> None: ...

    async def find_by_id(self, diagram_id: DiagramId) -> Optional[Diagram]: ...

    async def find_all(self) -> List[Diagram]: ...

    async def delete(self, diagram_id: DiagramId) -> None: ...

    async def find_by_name(self, name: str) -> Optional[Diagram]: ...
