from typing import Optional

from pydantic import BaseModel, Field, validator

from ..value_objects.node_type import NodeType


class DiagramNode(BaseModel):
    """Domain entity representing a node in a diagram."""

    id: str = Field(..., description="Unique node identifier")
    type: NodeType = Field(..., description="Type of the node")
    label: str = Field(
        ..., min_length=1, max_length=200, description="Display label for the node"
    )
    cluster: Optional[str] = Field(None, description="Cluster this node belongs to")

    @validator("label")
    def validate_label(cls, v):
        if not v or not v.strip():
            raise ValueError("Node label cannot be empty")
        return v.strip()

    def is_in_cluster(self) -> bool:
        """Check if this node belongs to a cluster."""
        return self.cluster is not None

    class Config:
        arbitrary_types_allowed = True
