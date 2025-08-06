from dependency_injector import containers, providers

from ...application.services.diagram_application_service import (
    DiagramApplicationService,
)
from ...domain.services.diagram_generation_service import DiagramGenerationService
from ..external.diagram_rendering_service import DiagramsPackageRenderingService
from ..external.llm_service import GeminiLLMService
from ..persistence.in_memory_diagram_repository import InMemoryDiagramRepository


class Container(containers.DeclarativeContainer):
    """Dependency injection container for diagram service."""

    # Configuration
    config = providers.Configuration()

    # Infrastructure Services
    llm_service = providers.Singleton(GeminiLLMService, api_key=config.gemini_api_key)
    diagram_rendering_service = providers.Singleton(DiagramsPackageRenderingService)

    # Repositories
    diagram_repository = providers.Singleton(InMemoryDiagramRepository)

    # Domain Services
    diagram_generation_service = providers.Singleton(DiagramGenerationService)

    # Application Services
    diagram_application_service = providers.Factory(
        DiagramApplicationService.create,
        diagram_repository=diagram_repository,
        diagram_generation_service=diagram_generation_service,
        diagram_rendering_service=diagram_rendering_service,
    )

    def __init__(self):
        super().__init__()
        # Debug: Check if services are properly initialized
        import logging

        logger = logging.getLogger(__name__)
        logger.info("Container initialized")
        logger.info(
            f"Diagram rendering service provider: {self.diagram_rendering_service}"
        )
