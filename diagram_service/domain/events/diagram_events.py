from datetime import datetime

from pydantic import BaseModel, Field

from ..entities import DiagramConnection, DiagramNode
from ..value_objects import DiagramId


class DiagramEvent(BaseModel):
    """Base class for all diagram-related domain events."""

    event_id: str = Field(..., description="Unique event identifier")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Event timestamp"
    )
    diagram_id: DiagramId = Field(..., description="Related diagram ID")

    class Config:
        arbitrary_types_allowed = True


class DiagramCreated(DiagramEvent):
    """Event raised when a new diagram is created."""

    diagram_name: str = Field(..., description="Name of the created diagram")


class DiagramNodeAdded(DiagramEvent):
    """Event raised when a node is added to a diagram."""

    node: DiagramNode = Field(..., description="Added node")


class DiagramConnectionAdded(DiagramEvent):
    """Event raised when a connection is added to a diagram."""

    connection: DiagramConnection = Field(..., description="Added connection")


class DiagramGenerationStarted(DiagramEvent):
    """Event raised when diagram generation starts."""

    description: str = Field(..., description="User description for diagram generation")


class DiagramGenerationCompleted(DiagramEvent):
    """Event raised when diagram generation completes."""

    image_path: str = Field(..., description="Path to generated image")
    node_count: int = Field(..., description="Number of nodes in diagram")
    connection_count: int = Field(..., description="Number of connections in diagram")


class DiagramGenerationFailed(DiagramEvent):
    """Event raised when diagram generation fails."""

    error_message: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Type of error")
