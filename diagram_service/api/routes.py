import os
import logging
from pathlib import Path
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from diagram_service.agents.diagram_agent import DiagramAgentPool


# Request/Response models
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


# Global agent pool - will be initialized in main.py
agent_pool: DiagramAgentPool = None


def get_agent_pool() -> DiagramAgentPool:
    """Dependency to get the agent pool."""
    if agent_pool is None:
        raise HTTPException(status_code=500, detail="Agent pool not initialized")
    return agent_pool


def set_agent_pool(pool: DiagramAgentPool):
    """Set the global agent pool."""
    global agent_pool
    agent_pool = pool


# Create router
router = APIRouter()


@router.post("/generate-diagram", response_model=DiagramGenerationResponse)
async def generate_diagram(
    request: DiagramGenerationRequest,
    pool: DiagramAgentPool = Depends(get_agent_pool)
):
    """
    Generate a diagram from a natural language description.
    
    This is the main endpoint that takes a user's description and returns
    a rendered diagram image.
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Received diagram generation request: {request.description}")
    
    try:
        async def create_diagram(agent):
            return await agent.create_diagram_from_description(request.description)
        
        # Execute with agent from pool
        image_path = await pool.execute_with_agent(create_diagram)
        
        # Generate public URL for the image
        filename = Path(image_path).name
        image_url = f"/api/images/{filename}"
        
        # Get diagram specification (we'll need to store this or recreate it)
        async def get_spec(agent):
            supported_types = agent.diagram_tools.get_supported_node_types()
            return await agent.llm_client.generate_diagram_specification(
                request.description, supported_types
            )
        
        diagram_spec = await pool.execute_with_agent(get_spec)
        
        return DiagramGenerationResponse(
            success=True,
            image_url=image_url,
            specification=diagram_spec.dict(),
            message="Diagram generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error generating diagram: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate diagram: {str(e)}"
        )


@router.post("/assistant-chat", response_model=AssistantChatResponse)
async def assistant_chat(
    request: AssistantChatRequest,
    pool: DiagramAgentPool = Depends(get_agent_pool)
):
    """
    Assistant-style endpoint for interactive diagram creation.
    
    This bonus endpoint understands user intent and responds helpfully,
    either by generating diagrams, explaining concepts, or asking questions.
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Received assistant chat request: {request.message}")
    
    try:
        async def chat_with_agent(agent):
            return await agent.chat_with_assistant(request.message)
        
        # Execute with agent from pool
        response = await pool.execute_with_agent(chat_with_agent)
        
        if response["type"] == "diagram":
            # Generate public URL for the image
            filename = Path(response["image_path"]).name
            image_url = f"/api/images/{filename}"
            
            return AssistantChatResponse(
                type="diagram",
                response=response["text_response"],
                image_url=image_url,
                specification=response["specification"]
            )
        else:
            return AssistantChatResponse(
                type="text",
                response=response["text_response"],
                supported_node_types=response.get("supported_node_types", [])
            )
            
    except Exception as e:
        logger.error(f"Error in assistant chat: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Assistant chat failed: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse)
async def health_check(
    pool: DiagramAgentPool = Depends(get_agent_pool)
):
    """
    Health check endpoint to verify service status.
    """
    try:
        async def check_health(agent):
            health = agent.health_check()
            supported_types = agent.get_supported_components()
            return health, list(supported_types.keys())
        
        # Execute with agent from pool
        health_status, supported_types = await pool.execute_with_agent(check_health)
        
        # Determine overall status
        all_healthy = all(health_status.values())
        status = "healthy" if all_healthy else "degraded"
        
        return HealthResponse(
            status=status,
            components=health_status,
            supported_node_types=supported_types
        )
        
    except Exception as e:
        logging.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            components={"error": False},
            supported_node_types=[]
        )


@router.get("/supported-components")
async def get_supported_components(
    pool: DiagramAgentPool = Depends(get_agent_pool)
):
    """
    Get list of supported diagram components with descriptions.
    """
    try:
        async def get_components(agent):
            return agent.get_supported_components()
        
        # Execute with agent from pool
        components = await pool.execute_with_agent(get_components)
        
        return {
            "supported_components": components,
            "total_count": len(components)
        }
        
    except Exception as e:
        logging.error(f"Error getting supported components: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get supported components: {str(e)}"
        )


@router.get("/images/{filename}")
async def get_image(filename: str):
    """
    Serve generated diagram images.
    """
    try:
        import tempfile
        import os
        
        # Use the shared images directory
        images_dir = os.path.join(tempfile.gettempdir(), "diagram_service_images")
        image_path = os.path.join(images_dir, filename)
        
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Image not found")
        
        return FileResponse(
            image_path,
            media_type="image/png",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error serving image {filename}: {e}")
        raise HTTPException(status_code=404, detail="Image not found") 