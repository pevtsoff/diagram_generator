import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from diagram_service.api.routes import router, set_agent_pool
from diagram_service.agents.diagram_agent import DiagramAgentPool

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Global variables
agent_pool = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    global agent_pool
    
    # Startup
    logger.info("Starting Diagram Service...")
    
    # Get Gemini API key (optional for mock mode)
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    use_mock = os.getenv("USE_MOCK_LLM", "false").lower() == "true"
    
    if not gemini_api_key and not use_mock:
        logger.error("GEMINI_API_KEY environment variable is required (or set USE_MOCK_LLM=true)")
        raise ValueError("GEMINI_API_KEY environment variable is required (or set USE_MOCK_LLM=true)")
    
    # Initialize agent pool
    pool_size = int(os.getenv("AGENT_POOL_SIZE", "3"))
    agent_pool = DiagramAgentPool(gemini_api_key or "mock", pool_size, use_mock=use_mock)
    set_agent_pool(agent_pool)
    
    if use_mock:
        logger.warning("Using MOCK LLM client - for development/testing only")
    
    logger.info(f"Initialized agent pool with {pool_size} agents")
    logger.info("Diagram Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Diagram Service...")
    if agent_pool:
        # Cleanup would go here if needed
        pass
    logger.info("Diagram Service shut down complete")


# Create FastAPI app
app = FastAPI(
    title="AI Diagram Generation Service",
    description="""
    An async, stateless Python API service that creates diagrams using AI agents powered by LLM.
    
    ## Features
    - Generate cloud architecture diagrams from natural language descriptions
    - Assistant-style interface for interactive diagram creation
    - Support for AWS, GCP, and Azure components
    - Stateless design with no database required
    
    ## Endpoints
    - `/api/generate-diagram`: Main diagram generation endpoint
    - `/api/assistant-chat`: Interactive assistant for complex workflows
    - `/api/health`: Service health check
    - `/api/supported-components`: List of available diagram components
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "AI Diagram Generation Service",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    # Configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    ) 