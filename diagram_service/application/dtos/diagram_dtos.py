from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CreateDiagramRequest(BaseModel):
    """Request DTO for creating a diagram."""

    name: str = Field(..., min_length=1, max_length=100, description="Diagram name")
    nodes: List[Dict[str, Any]] = Field(..., description="Diagram nodes")
    connections: List[Dict[str, Any]] = Field(..., description="Diagram connections")
    clusters: Optional[List[Dict[str, Any]]] = Field(
        None, description="Diagram clusters"
    )


class CreateDiagramResponse(BaseModel):
    """Response DTO for diagram creation."""

    diagram_id: str = Field(..., description="Created diagram ID")
    name: str = Field(..., description="Diagram name")
    image_path: str = Field(..., description="Path to generated image")
    node_count: int = Field(..., description="Number of nodes")
    connection_count: int = Field(..., description="Number of connections")
    created_at: datetime = Field(..., description="Creation timestamp")


class DiagramDetailsResponse(BaseModel):
    """Response DTO for diagram details."""

    diagram_id: str = Field(..., description="Diagram ID")
    name: str = Field(..., description="Diagram name")
    nodes: List[Dict[str, Any]] = Field(..., description="Diagram nodes")
    connections: List[Dict[str, Any]] = Field(..., description="Diagram connections")
    clusters: List[Dict[str, Any]] = Field(..., description="Diagram clusters")
    image_path: str = Field(..., description="Path to diagram image")
    statistics: Dict[str, Any] = Field(..., description="Diagram statistics")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class GenerateDiagramFromDescriptionRequest(BaseModel):
    """Request DTO for generating diagram from description."""

    description: str = Field(
        ..., min_length=1, description="Natural language description"
    )


class GenerateDiagramFromDescriptionResponse(BaseModel):
    """Response DTO for diagram generation from description."""

    success: bool = Field(..., description="Generation success status")
    diagram_id: Optional[str] = Field(None, description="Generated diagram ID")
    image_path: str = Field(..., description="Path to generated image")
    specification: Dict[str, Any] = Field(..., description="Generated specification")
    message: str = Field("", description="Response message")
    error: Optional[str] = Field(None, description="Error message if failed")


class ChatRequest(BaseModel):
    """Request DTO for chat interaction."""

    message: str = Field(..., min_length=1, description="User message")


class ChatResponse(BaseModel):
    """Response DTO for chat interaction."""

    type: str = Field(..., description="Response type: 'text' or 'diagram'")
    response: str = Field(..., description="Response message")
    image_path: str = Field("", description="Path to generated image")
    specification: Dict[str, Any] = Field({}, description="Diagram specification")
    supported_node_types: List[str] = Field([], description="Supported node types")


class HealthResponse(BaseModel):
    """Response DTO for health check."""

    status: str = Field(..., description="Service status")
    components: Dict[str, bool] = Field(..., description="Component health status")
    supported_node_types: List[str] = Field(..., description="Supported node types")
