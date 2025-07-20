"""
Dependency injection container for the AI Video Generator

This module provides a simple dependency injection container to wire up
all the components of the clean architecture.
"""

from typing import Dict, Any, Optional

from ..core.interfaces.repositories import (
    VideoRepository,
    SessionRepository,
    AgentRepository
)
from ..core.interfaces.services import (
    VideoGenerationService,
    ScriptGenerationService,
    AudioGenerationService
)
from ..core.use_cases.video_generation_use_case import VideoGenerationUseCase
from ..core.use_cases.session_management_use_case import SessionManagementUseCase
from ..core.use_cases.agent_orchestration_use_case import AgentOrchestrationUseCase

from .repositories.file_video_repository import FileVideoRepository
from .repositories.file_session_repository import FileSessionRepository
from .repositories.file_agent_repository import FileAgentRepository
from .services.existing_video_generation_service import ExistingVideoGenerationService
from .services.existing_script_generation_service import ExistingScriptGenerationService
from .services.existing_audio_generation_service import ExistingAudioGenerationService

class DIContainer:
    """
    Simple dependency injection container

    This container manages the lifecycle and dependencies of all components
    in the clean architecture.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize container with configuration

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self._repositories: Dict[str, Any] = {}
        self._services: Dict[str, Any] = {}
        self._use_cases: Dict[str, Any] = {}

        # Initialize components
        self._setup_repositories()
        self._setup_services()
        self._setup_use_cases()

    def _setup_repositories(self) -> None:
        """Setup repository implementations"""
        base_data_path = self.config.get("data_path", "data")

        self._repositories["video"] = FileVideoRepository(
            base_path=f"{base_data_path}/videos"
        )

        self._repositories["session"] = FileSessionRepository(
            base_path=f"{base_data_path}/sessions"
        )

        self._repositories["agent"] = FileAgentRepository(
            base_path=f"{base_data_path}/agents"
        )

    def _setup_services(self) -> None:
        """Setup service implementations"""
        output_base_path = self.config.get("output_path", "outputs")

        self._services["video_generation"] = ExistingVideoGenerationService(
            output_base_path=output_base_path
        )

        self._services["script_generation"] = ExistingScriptGenerationService()

        self._services["audio_generation"] = ExistingAudioGenerationService(
            output_base_path=output_base_path
        )

    def _setup_use_cases(self) -> None:
        """Setup use case implementations"""
        self._use_cases["video_generation"] = VideoGenerationUseCase(
            video_repository=self.get_video_repository(),
            session_repository=self.get_session_repository(),
            agent_repository=self.get_agent_repository(),
            video_generation_service=self.get_video_generation_service(),
            script_generation_service=self.get_script_generation_service(),
            audio_generation_service=self.get_audio_generation_service()
        )

        self._use_cases["session_management"] = SessionManagementUseCase(
            session_repository=self.get_session_repository(),
            video_repository=self.get_video_repository()
        )

        self._use_cases["agent_orchestration"] = AgentOrchestrationUseCase(
            agent_repository=self.get_agent_repository(),
            video_repository=self.get_video_repository(),
            session_repository=self.get_session_repository()
        )

    # Repository getters
    def get_video_repository(self) -> VideoRepository:
        """Get video repository"""
        return self._repositories["video"]

    def get_session_repository(self) -> SessionRepository:
        """Get session repository"""
        return self._repositories["session"]

    def get_agent_repository(self) -> AgentRepository:
        """Get agent repository"""
        return self._repositories["agent"]

    # Service getters
    def get_video_generation_service(self) -> VideoGenerationService:
        """Get video generation service"""
        return self._services["video_generation"]

    def get_script_generation_service(self) -> ScriptGenerationService:
        """Get script generation service"""
        return self._services["script_generation"]

    def get_audio_generation_service(self) -> AudioGenerationService:
        """Get audio generation service"""
        return self._services["audio_generation"]

    # Use case getters
    def get_video_generation_use_case(self) -> VideoGenerationUseCase:
        """Get video generation use case"""
        return self._use_cases["video_generation"]

    def get_session_management_use_case(self) -> SessionManagementUseCase:
        """Get session management use case"""
        return self._use_cases["session_management"]

    def get_agent_orchestration_use_case(self) -> AgentOrchestrationUseCase:
        """Get agent orchestration use case"""
        return self._use_cases["agent_orchestration"]

    def get_all_repositories(self) -> Dict[str, Any]:
        """Get all repositories"""
        return self._repositories.copy()

    def get_all_services(self) -> Dict[str, Any]:
        """Get all services"""
        return self._services.copy()

    def get_all_use_cases(self) -> Dict[str, Any]:
        """Get all use cases"""
        return self._use_cases.copy()

    def get_config(self) -> Dict[str, Any]:
        """Get configuration"""
        return self.config.copy()

    def update_config(self, config: Dict[str, Any]) -> None:
        """Update configuration"""
        self.config.update(config)

    def reset(self) -> None:
        """Reset container (for testing)"""
        self._repositories.clear()
        self._services.clear()
        self._use_cases.clear()
        self._setup_repositories()
        self._setup_services()
        self._setup_use_cases()

# Global container instance
_container: Optional[DIContainer] = None

def get_container(config: Optional[Dict[str, Any]] = None) -> DIContainer:
    """
    Get global container instance

    Args:
        config: Configuration dictionary

    Returns:
        Container instance
    """
    global _container

    if _container is None:
        _container = DIContainer(config)
    elif config:
        _container.update_config(config)

    return _container

def reset_container() -> None:
    """Reset global container (for testing)"""
    global _container
    _container = None

def configure_container(config: Dict[str, Any]) -> DIContainer:
    """
    Configure and return container

    Args:
        config: Configuration dictionary

    Returns:
        Configured container instance
    """
    return get_container(config)
