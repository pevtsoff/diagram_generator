import uuid

from pydantic import BaseModel, Field, validator


class DiagramId(BaseModel):
    """Value object for diagram identifier."""

    value: str = Field(..., description="Unique diagram identifier")

    @validator("value")
    def validate_diagram_id(cls, v):
        if not v or not v.strip():
            raise ValueError("Diagram ID cannot be empty")
        return v.strip()

    @classmethod
    def generate(cls) -> "DiagramId":
        """Generate a new diagram ID."""
        return cls(value=str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value

    class Config:
        frozen = True
