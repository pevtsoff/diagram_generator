from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class GenerateDiagramCommand(BaseModel):
    """Command for generating a diagram from description."""

    description: str = Field(
        ..., min_length=1, description="Natural language description"
    )

    @validator("description")
    def validate_description(cls, v):
        if not v or not v.strip():
            raise ValueError("Description cannot be empty")
        return v.strip()


class CreateDiagramCommand(BaseModel):
    """Command for creating a diagram from specification."""

    name: str = Field(..., min_length=1, max_length=100, description="Diagram name")
    nodes: List[Dict[str, Any]] = Field(..., description="Diagram nodes")
    connections: List[Dict[str, Any]] = Field(..., description="Diagram connections")
    clusters: Optional[List[Dict[str, Any]]] = Field(
        None, description="Diagram clusters"
    )

    @validator("name")
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Diagram name cannot be empty")
        return v.strip()

    @validator("nodes")
    def validate_nodes(cls, v):
        if not v:
            raise ValueError("At least one node is required")
        return v

    @validator("connections")
    def validate_connections(cls, v):
        # Connections are optional but if provided, they should be valid
        return v
