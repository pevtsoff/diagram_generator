from typing import Optional

from pydantic import BaseModel, Field, validator


class GetDiagramByIdQuery(BaseModel):
    """Query for getting a diagram by ID."""

    diagram_id: str = Field(..., description="Diagram ID to retrieve")

    @validator("diagram_id")
    def validate_diagram_id(cls, v):
        if not v or not v.strip():
            raise ValueError("Diagram ID cannot be empty")
        return v.strip()


class GetDiagramByNameQuery(BaseModel):
    """Query for getting a diagram by name."""

    name: str = Field(..., description="Diagram name to retrieve")

    @validator("name")
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Diagram name cannot be empty")
        return v.strip()


class GetAllDiagramsQuery(BaseModel):
    """Query for getting all diagrams."""

    limit: Optional[int] = Field(
        None, ge=1, le=100, description="Maximum number of diagrams to return"
    )
    offset: Optional[int] = Field(None, ge=0, description="Number of diagrams to skip")

    @validator("limit")
    def validate_limit(cls, v):
        if v is not None and v < 1:
            raise ValueError("Limit must be at least 1")
        return v

    @validator("offset")
    def validate_offset(cls, v):
        if v is not None and v < 0:
            raise ValueError("Offset must be non-negative")
        return v
