from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from ...application.commands.generate_diagram_command import (
    CreateDiagramCommand,
    GenerateDiagramCommand,
)
from ...application.dtos.diagram_dtos import (
    ChatRequest,
    ChatResponse,
    CreateDiagramRequest,
    CreateDiagramResponse,
    DiagramDetailsResponse,
    GenerateDiagramFromDescriptionRequest,
    GenerateDiagramFromDescriptionResponse,
    HealthResponse,
)
from ...application.queries.get_diagram_query import (
    GetAllDiagramsQuery,
    GetDiagramByIdQuery,
)
from ...application.services.diagram_application_service import (
    DiagramApplicationService,
)
from ...infrastructure.config.container import Container

router = APIRouter()


def get_diagram_service() -> DiagramApplicationService:
    """Get diagram application service from container."""
    container = Container()
    container.config.from_dict(
        {
            "gemini_api_key": "your-api-key-here"  # This should come from environment
        }
    )
    return container.diagram_application_service()


@router.post("/diagrams", response_model=CreateDiagramResponse)
async def create_diagram(
    request: CreateDiagramRequest,
    diagram_service: DiagramApplicationService = Depends(get_diagram_service),
):
    """Create a new diagram from specification."""
    try:
        command = CreateDiagramCommand(
            name=request.name,
            nodes=request.nodes,
            connections=request.connections,
            clusters=request.clusters,
        )
        return await diagram_service.create_diagram(command)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/diagrams/generate", response_model=GenerateDiagramFromDescriptionResponse
)
async def generate_diagram_from_description(
    request: GenerateDiagramFromDescriptionRequest,
    diagram_service: DiagramApplicationService = Depends(get_diagram_service),
):
    """Generate a diagram from natural language description."""
    try:
        command = GenerateDiagramCommand(description=request.description)
        return await diagram_service.generate_diagram_from_description(command)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/diagrams/{diagram_id}", response_model=DiagramDetailsResponse)
async def get_diagram_by_id(
    diagram_id: str,
    diagram_service: DiagramApplicationService = Depends(get_diagram_service),
):
    """Get diagram by ID."""
    query = GetDiagramByIdQuery(diagram_id=diagram_id)
    diagram = await diagram_service.get_diagram_by_id(query)

    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")

    return diagram


@router.get("/diagrams", response_model=List[DiagramDetailsResponse])
async def get_all_diagrams(
    limit: Optional[int] = Query(
        None, ge=1, le=100, description="Maximum number of diagrams"
    ),
    offset: Optional[int] = Query(None, ge=0, description="Number of diagrams to skip"),
    diagram_service: DiagramApplicationService = Depends(get_diagram_service),
):
    """Get all diagrams with optional pagination."""
    query = GetAllDiagramsQuery(limit=limit, offset=offset)
    return await diagram_service.get_all_diagrams(query)


@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(
    request: ChatRequest,
    diagram_service: DiagramApplicationService = Depends(get_diagram_service),
):
    """Chat with the diagram assistant."""
    try:
        # This would integrate with the chat functionality
        # For now, return a mock response
        return ChatResponse(
            type="text",
            response=f"Assistant response to: {request.message}",
            image_path="",
            specification={},
            supported_node_types=[],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # This would check all components
        return HealthResponse(
            status="healthy",
            components={
                "llm_service": True,
                "diagram_rendering_service": True,
                "diagram_repository": True,
            },
            supported_node_types=[],  # This would be populated from rendering service
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
