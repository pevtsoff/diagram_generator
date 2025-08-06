from pydantic import BaseModel, Field, validator


class NodeType(BaseModel):
    """Value object for diagram node type."""

    value: str = Field(..., description="Node type identifier")

    @validator("value")
    def validate_node_type(cls, v):
        if not v or not v.strip():
            raise ValueError("Node type cannot be empty")
        return v.strip().lower()

    def get_provider(self) -> str:
        """Extract provider from node type (e.g., 'aws' from 'aws_ec2')."""
        parts = self.value.split("_", 1)
        return parts[0] if parts else ""

    def get_service(self) -> str:
        """Extract service from node type (e.g., 'ec2' from 'aws_ec2')."""
        parts = self.value.split("_", 1)
        return parts[1] if len(parts) > 1 else ""

    def __str__(self) -> str:
        return self.value

    class Config:
        frozen = True
