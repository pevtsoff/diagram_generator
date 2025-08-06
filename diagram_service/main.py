import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from diagram_service.infrastructure.config.container import Container
from diagram_service.presentation.controllers.diagram_controller import (
    router as diagram_router,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global container instance
container = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global container

    # Startup
    logger.info("Starting Diagram Service...")

    # Initialize container
    container = Container()
    container.config.from_dict(
        {"gemini_api_key": os.getenv("GEMINI_API_KEY", "your-api-key-here")}
    )

    # Wire container
    container.wire(
        modules=["diagram_service.presentation.controllers.diagram_controller"]
    )

    logger.info("Diagram Service started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Diagram Service...")

    # Cleanup
    if container:
        # Cleanup rendering service
        rendering_service = container.diagram_rendering_service()
        if hasattr(rendering_service, "cleanup"):
            rendering_service.cleanup()

    logger.info("Diagram Service shut down complete")


# Create FastAPI app
app = FastAPI(
    title="Diagram Generation Service",
    description="A service for generating diagrams from natural language descriptions",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(diagram_router, prefix="/api/v1", tags=["diagrams"])


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Diagram Generation Service",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/api")
async def api_info():
    """API information endpoint."""
    return {
        "name": "Diagram Generation Service API",
        "version": "1.0.0",
        "endpoints": {
            "diagrams": "/api/v1/diagrams",
            "generate": "/api/v1/diagrams/generate",
            "chat": "/api/v1/chat",
            "health": "/api/v1/health",
        },
    }
