from typing import Optional

from pydantic import BaseModel, Field, validator


class DiagramConnection(BaseModel):
    """Domain entity representing a connection between nodes in a diagram."""

    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    label: Optional[str] = Field(None, description="Connection label")

    @validator("source", "target")
    def validate_node_ids(cls, v):
        if not v or not v.strip():
            raise ValueError("Node ID cannot be empty")
        return v.strip()

    @validator("label")
    def validate_label(cls, v):
        if v is not None and not v.strip():
            return None
        return v.strip() if v else None

    def has_label(self) -> bool:
        """Check if this connection has a label."""
        return self.label is not None and self.label.strip() != ""

    class Config:
        arbitrary_types_allowed = True
