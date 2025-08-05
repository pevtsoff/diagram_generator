from typing import Dict, Any, List, Optional
from pydantic import BaseModel


# API Request/Response Models
class DiagramGenerationRequest(BaseModel):
    description: str


class DiagramGenerationResponse(BaseModel):
    success: bool
    image_url: str
    specification: Dict[str, Any]
    message: str = ""


class AssistantChatRequest(BaseModel):
    message: str


class AssistantChatResponse(BaseModel):
    type: str  # "text" or "diagram"
    response: str
    image_url: str = ""
    specification: Dict[str, Any] = {}
    supported_node_types: list[str] = []


class HealthResponse(BaseModel):
    status: str
    components: Dict[str, bool]
    supported_node_types: list[str]


# LLM/Diagram Models
class DiagramRequest(BaseModel):
    """Structured request for diagram generation."""
    name: str
    nodes: List[Dict[str, Any]]
    connections: List[Dict[str, Any]]
    clusters: Optional[List[Dict[str, Any]]] = None 