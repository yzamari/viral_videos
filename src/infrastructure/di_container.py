"""
Dependency Injection Container
Central configuration and dependency management
"""
from typing import Dict, Any, Optional, Type, TypeVar, Callable
from dataclasses import dataclass
from enum import Enum
import os
import json

# Import all interfaces
from ..ai.interfaces.base import AIProvider, AIServiceType
from ..ai.interfaces.auth import AuthProvider, AuthType
from ..ai.interfaces.storage import StorageProvider, StorageType, StorageConfig
from ..ai.interfaces.video_generation_enhanced import (
    VideoProvider,
    VideoGenerationProvider,
    VideoGenerationConfig,
    VideoGenerationOrchestrator,
    VideoQuality
)
from ..agents.interfaces import AgentRole, AgentInterface, AgentFactory, AgentOrchestrator

T = TypeVar('T')

class ServiceLifetime(Enum):
    """Service lifetime management"""
    SINGLETON = "singleton"  # One instance for entire app
    SCOPED = "scoped"       # One instance per request/session
    TRANSIENT = "transient"  # New instance every time

@dataclass
class ServiceRegistration:
    """Service registration details"""
    interface: Type
    implementation: Type
    lifetime: ServiceLifetime
    factory: Optional[Callable] = None
    config: Optional[Dict[str, Any]] = None

class DIContainer:
    """Dependency Injection Container"""
    
    def __init__(self):
        self._registrations: Dict[Type, ServiceRegistration] = {}
        self._singletons: Dict[Type, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._config: Dict[str, Any] = {}
    
    def register(self,
                interface: Type[T],
                implementation: Type[T],
                lifetime: ServiceLifetime = ServiceLifetime.SINGLETON,
                factory: Optional[Callable] = None,
                config: Optional[Dict[str, Any]] = None):
        """Register a service"""
        self._registrations[interface] = ServiceRegistration(
            interface=interface,
            implementation=implementation,
            lifetime=lifetime,
            factory=factory,
            config=config
        )
    
    def register_factory(self, name: str, factory: Callable):
        """Register a factory function"""
        self._factories[name] = factory
    
    def resolve(self, interface: Type[T]) -> T:
        """Resolve a service"""
        if interface not in self._registrations:
            raise ValueError(f"No registration found for {interface}")
        
        registration = self._registrations[interface]
        
        # Check for singleton
        if registration.lifetime == ServiceLifetime.SINGLETON:
            if interface in self._singletons:
                return self._singletons[interface]
        
        # Create instance
        if registration.factory:
            instance = registration.factory(self, registration.config)
        else:
            # Resolve constructor dependencies
            instance = self._create_instance(registration.implementation, registration.config)
        
        # Store singleton
        if registration.lifetime == ServiceLifetime.SINGLETON:
            self._singletons[interface] = instance
        
        return instance
    
    def _create_instance(self, cls: Type, config: Optional[Dict[str, Any]] = None):
        """Create instance with dependency injection"""
        # Simple instantiation for now
        # In production, would inspect constructor and resolve dependencies
        if config:
            return cls(**config)
        return cls()
    
    def load_config(self, config_path: str):
        """Load configuration from file"""
        with open(config_path, 'r') as f:
            self._config = json.load(f)
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)

class ContainerBuilder:
    """Builder for configuring the DI container"""
    
    def __init__(self):
        self.container = DIContainer()
    
    def register_authentication(self) -> 'ContainerBuilder':
        """Register authentication providers"""
        from ..ai.providers.auth.google_auth import GoogleCloudAuthProvider
        from ..ai.providers.auth.api_key_auth import APIKeyAuthProvider
        
        # Register Google Cloud auth
        self.container.register(
            AuthProvider,
            GoogleCloudAuthProvider,
            ServiceLifetime.SINGLETON,
            config={'project_id': os.getenv('GOOGLE_CLOUD_PROJECT')}
        )
        
        # Factory for API key auth
        def api_key_factory(container, config):
            api_key = config.get('api_key') or os.getenv('API_KEY')
            return APIKeyAuthProvider(api_key)
        
        self.container.register_factory('api_key_auth', api_key_factory)
        
        return self
    
    def register_storage(self) -> 'ContainerBuilder':
        """Register storage providers"""
        from ..ai.providers.storage.local_storage import LocalStorageProvider
        
        # Register local storage
        from ..ai.interfaces.storage import StorageConfig, StorageType
        storage_config = StorageConfig(
            storage_type=StorageType.LOCAL,
            base_path='./storage'
        )
        self.container.register(
            StorageProvider,
            LocalStorageProvider,
            ServiceLifetime.SINGLETON,
            config=storage_config
        )
        
        return self
    
    def register_video_providers(self) -> 'ContainerBuilder':
        """Register video generation providers"""
        from ..ai.providers.video.veo3_provider import Veo3VideoProvider
        from ..ai.providers.video.runwayml_provider import RunwayMLVideoProvider
        
        # Factory for creating video providers
        def video_provider_factory(provider_type: VideoProvider, container: DIContainer):
            auth_provider = container.resolve(AuthProvider)
            storage_provider = container.resolve(StorageProvider)
            
            config = VideoGenerationConfig(
                provider=provider_type,
                auth_provider=auth_provider,
                storage_provider=storage_provider,
                quality=VideoQuality.STANDARD,
                custom_config={
                    'project_id': os.getenv('GOOGLE_CLOUD_PROJECT'),
                    'location': 'us-central1',
                    'api_key': os.getenv('RUNWAYML_API_KEY')
                }
            )
            
            if provider_type == VideoProvider.VEO3:
                return Veo3VideoProvider(config)
            elif provider_type == VideoProvider.RUNWAY_ML:
                return RunwayMLVideoProvider(config)
            else:
                raise ValueError(f"Unknown video provider: {provider_type}")
        
        self.container.register_factory('video_provider', video_provider_factory)
        
        # Register orchestrator
        def orchestrator_factory(container: DIContainer):
            providers = {}
            
            # Create all available providers
            for provider_type in [VideoProvider.VEO3, VideoProvider.RUNWAY_ML]:
                try:
                    provider = container._factories['video_provider'](provider_type, container)
                    if provider.is_available():
                        providers[provider_type] = provider
                except Exception as e:
                    print(f"Failed to create {provider_type}: {e}")
            
            orchestrator = VideoGenerationOrchestrator(providers)
            orchestrator.set_fallback_chain([VideoProvider.VEO3, VideoProvider.RUNWAY_ML])
            return orchestrator
        
        self.container.register(
            VideoGenerationOrchestrator,
            VideoGenerationOrchestrator,
            ServiceLifetime.SINGLETON,
            factory=lambda c, cfg: orchestrator_factory(c)
        )
        
        return self
    
    def register_ai_services(self) -> 'ContainerBuilder':
        """Register AI services"""
        from ..ai.manager import AIServiceManager
        from ..ai.config import AIConfiguration
        
        # Register AI configuration
        self.container.register(
            AIConfiguration,
            AIConfiguration,
            ServiceLifetime.SINGLETON,
            factory=lambda c, cfg: AIConfiguration.create_default()
        )
        
        # Register AI manager
        def ai_manager_factory(container: DIContainer):
            config = container.resolve(AIConfiguration)
            return AIServiceManager(config)
        
        self.container.register(
            AIServiceManager,
            AIServiceManager,
            ServiceLifetime.SINGLETON,
            factory=lambda c, cfg: ai_manager_factory(c)
        )
        
        return self
    
    def register_agents(self) -> 'ContainerBuilder':
        """Register agent system"""
        from ..ai.manager import AIServiceManager
        
        # Register agent factory
        def agent_factory_factory(container: DIContainer):
            ai_manager = container.resolve(AIServiceManager)
            return AgentFactory(ai_manager)
        
        self.container.register(
            AgentFactory,
            AgentFactory,
            ServiceLifetime.SINGLETON,
            factory=lambda c, cfg: agent_factory_factory(c)
        )
        
        # Register agent orchestrator
        def agent_orchestrator_factory(container: DIContainer):
            factory = container.resolve(AgentFactory)
            return AgentOrchestrator(factory)
        
        self.container.register(
            AgentOrchestrator,
            AgentOrchestrator,
            ServiceLifetime.SCOPED,
            factory=lambda c, cfg: agent_orchestrator_factory(c)
        )
        
        return self
    
    def build(self) -> DIContainer:
        """Build and return the configured container"""
        return self.container

# Global container instance
_container: Optional[DIContainer] = None

def get_container() -> DIContainer:
    """Get the global DI container"""
    global _container
    if _container is None:
        _container = (ContainerBuilder()
            .register_authentication()
            .register_storage()
            .register_ai_services()
            .register_video_providers()
            .register_agents()
            .build())
    return _container

def reset_container():
    """Reset the global container (useful for testing)"""
    global _container
    _container = None