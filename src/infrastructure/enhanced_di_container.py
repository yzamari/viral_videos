"""
Enhanced Dependency Injection Container for the ViralAI platform.

This container extends the existing DI container with new OOP architecture
components while maintaining backward compatibility with legacy systems.
"""

from typing import Dict, Any, Optional
import logging

# Import the existing DI container
from .di_container import DIContainer as LegacyDIContainer, get_container as get_legacy_container

# New OOP repositories
from src.repositories.interfaces import IUserRepository, IVideoSessionRepository, ICampaignRepository
from src.repositories.user_repository import UserRepository
from src.repositories.video_session_repository import VideoSessionRepository
from src.repositories.campaign_repository import CampaignRepository

# New OOP services
from src.services.interfaces import IAuthenticationService, IVideoGenerationService, ICampaignService
from src.services.authentication_service import AuthenticationService
from src.services.video_generation_service import VideoGenerationService
from src.services.campaign_service import CampaignService

logger = logging.getLogger(__name__)


class EnhancedDIContainer:
    """
    Enhanced Dependency Injection Container that extends the legacy container
    with new OOP architecture components.
    
    This container maintains backward compatibility while providing the new
    domain-driven architecture components.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the enhanced DI container.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        
        # Get legacy container for backward compatibility
        self._legacy_container = get_legacy_container()
        
        # New OOP components
        self._repositories: Dict[str, Any] = {}
        self._services: Dict[str, Any] = {}
        
        # Initialize new components
        self._setup_repositories()
        self._setup_services()
        
        logger.info("Enhanced DI Container initialized")
    
    def _setup_repositories(self) -> None:
        """Setup new OOP repository implementations"""
        try:
            base_data_path = self.config.get("data_path", "data")
            
            # User repository
            self._repositories["user"] = UserRepository(
                base_path=f"{base_data_path}/users"
            )
            
            # Video session repository  
            self._repositories["video_session"] = VideoSessionRepository(
                base_path=f"{base_data_path}/video_sessions"
            )
            
            # Campaign repository
            self._repositories["campaign"] = CampaignRepository(
                base_path=f"{base_data_path}/campaigns"
            )
            
            logger.debug("Enhanced repositories initialized")
            
        except Exception as e:
            logger.error(f"Error setting up repositories: {e}")
            raise
    
    def _setup_services(self) -> None:
        """Setup new business service implementations"""
        try:
            # Authentication service
            jwt_config = self.config.get("jwt", {})
            self._services["authentication"] = AuthenticationService(
                user_repository=self.get_user_repository(),
                secret_key=jwt_config.get("secret_key", "your-secret-key-change-in-production"),
                algorithm=jwt_config.get("algorithm", "HS256"),
                access_token_expire_minutes=jwt_config.get("access_token_expire_minutes", 30)
            )
            
            # Video generation service
            video_config = self.config.get("video_generation", {})
            self._services["video_generation"] = VideoGenerationService(
                user_repository=self.get_user_repository(),
                video_session_repository=self.get_video_session_repository(),
                max_concurrent_generations=video_config.get("max_concurrent_generations", 5)
            )
            
            # Campaign service
            self._services["campaign"] = CampaignService(
                user_repository=self.get_user_repository(),
                campaign_repository=self.get_campaign_repository(),
                video_session_repository=self.get_video_session_repository()
            )
            
            logger.debug("Enhanced services initialized")
            
        except Exception as e:
            logger.error(f"Error setting up services: {e}")
            raise
    
    # New OOP Repository getters
    def get_user_repository(self) -> IUserRepository:
        """Get user repository instance"""
        return self._repositories["user"]
    
    def get_video_session_repository(self) -> IVideoSessionRepository:
        """Get video session repository instance"""
        return self._repositories["video_session"]
    
    def get_campaign_repository(self) -> ICampaignRepository:
        """Get campaign repository instance"""
        return self._repositories["campaign"]
    
    # New OOP Service getters
    def get_authentication_service(self) -> IAuthenticationService:
        """Get authentication service instance"""
        return self._services["authentication"]
    
    def get_video_generation_service(self) -> IVideoGenerationService:
        """Get video generation service instance"""
        return self._services["video_generation"]
    
    def get_campaign_service(self) -> ICampaignService:
        """Get campaign service instance"""
        return self._services["campaign"]
    
    # Legacy container delegation methods
    def get_legacy_container(self) -> LegacyDIContainer:
        """Get the legacy DI container for backward compatibility"""
        return self._legacy_container
    
    def resolve(self, interface_type):
        """Resolve service from legacy container"""
        return self._legacy_container.resolve(interface_type)
    
    def register(self, interface, implementation, **kwargs):
        """Register service in legacy container"""
        return self._legacy_container.register(interface, implementation, **kwargs)
    
    # Utility methods
    def get_all_repositories(self) -> Dict[str, Any]:
        """Get all new OOP repositories"""
        return self._repositories.copy()
    
    def get_all_services(self) -> Dict[str, Any]:
        """Get all new OOP services"""
        return self._services.copy()
    
    def get_config(self) -> Dict[str, Any]:
        """Get configuration"""
        return self.config.copy()
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """
        Update configuration and reinitialize components if needed.
        
        Args:
            config: New configuration to merge
        """
        self.config.update(config)
        logger.info("Enhanced container configuration updated")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all components.
        
        Returns:
            Health status of all components
        """
        health = {
            "status": "healthy",
            "enhanced_components": {
                "repositories": {
                    "user": "healthy" if self._repositories.get("user") else "missing",
                    "video_session": "healthy" if self._repositories.get("video_session") else "missing",
                    "campaign": "healthy" if self._repositories.get("campaign") else "missing"
                },
                "services": {
                    "authentication": "healthy" if self._services.get("authentication") else "missing",
                    "video_generation": "healthy" if self._services.get("video_generation") else "missing",
                    "campaign": "healthy" if self._services.get("campaign") else "missing"
                }
            },
            "legacy_container": "available" if self._legacy_container else "missing"
        }
        
        # Check if any critical component is missing
        critical_missing = []
        if not self._repositories.get("user"):
            critical_missing.append("user_repository")
        if not self._services.get("authentication"):
            critical_missing.append("authentication_service")
        
        if critical_missing:
            health["status"] = "unhealthy"
            health["missing_critical"] = critical_missing
        
        return health


# Global enhanced container instance
_enhanced_container: Optional[EnhancedDIContainer] = None


def get_enhanced_container(config: Optional[Dict[str, Any]] = None) -> EnhancedDIContainer:
    """
    Get global enhanced container instance (Singleton pattern).
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Enhanced container instance
    """
    global _enhanced_container
    
    if _enhanced_container is None:
        _enhanced_container = EnhancedDIContainer(config)
    elif config:
        _enhanced_container.update_config(config)
    
    return _enhanced_container


def reset_enhanced_container() -> None:
    """Reset global enhanced container (for testing)"""
    global _enhanced_container
    _enhanced_container = None


def configure_enhanced_container(config: Dict[str, Any]) -> EnhancedDIContainer:
    """
    Configure and return enhanced container with specific settings.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configured enhanced container instance
    """
    return get_enhanced_container(config)


def get_enhanced_health_status() -> Dict[str, Any]:
    """
    Get health status of the global enhanced container.
    
    Returns:
        Health status information
    """
    container = get_enhanced_container()
    return container.health_check()