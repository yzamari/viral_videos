"""
AI Service Manager (Dependency Injection)
"""
from typing import Dict, Optional, TypeVar, Type, List
from .factory import AIServiceFactory, AIServiceType
from .config import AIConfiguration
from .interfaces.base import AIService, AIProvider
from .interfaces.text_generation import TextGenerationService

T = TypeVar('T', bound=AIService)

class AIServiceManager:
    """Central manager for all AI services with dependency injection"""
    
    def __init__(self, config: Optional[AIConfiguration] = None):
        self.config = config or AIConfiguration.create_default()
        self._services: Dict[str, AIService] = {}
        self._fallback_chains: Dict[AIServiceType, List[AIProvider]] = {}
    
    def get_text_service(self, provider: Optional[AIProvider] = None) -> TextGenerationService:
        """Get text generation service"""
        return self._get_service(AIServiceType.TEXT_GENERATION, TextGenerationService, provider)
    
    def _get_service(self, 
                    service_type: AIServiceType, 
                    service_class: Type[T], 
                    provider: Optional[AIProvider] = None) -> T:
        """Get or create a service instance"""
        
        # Build cache key
        cache_key = f"{service_type.value}_{provider.value if provider else 'default'}"
        
        # Check cache
        if cache_key in self._services:
            return self._services[cache_key]
        
        # Get configuration
        config = self.config.get_service_config(service_type, provider)
        
        # Create service
        service = AIServiceFactory.create(service_type, config)
        
        # Cache and return
        self._services[cache_key] = service
        return service
    
    def set_fallback_chain(self, 
                          service_type: AIServiceType, 
                          providers: List[AIProvider]):
        """Set fallback provider chain for resilience"""
        self._fallback_chains[service_type] = providers
    
    async def execute_with_fallback(self, 
                                   service_type: AIServiceType, 
                                   operation: str, 
                                   *args, 
                                   **kwargs):
        """Execute operation with automatic fallback"""
        
        providers = self._fallback_chains.get(service_type, [])
        if not providers:
            # Use default provider only
            service = self._get_service(service_type, AIService)
            method = getattr(service, operation)
            return await method(*args, **kwargs)
        
        # Try each provider in order
        last_error = None
        for provider in providers:
            try:
                service = self._get_service(service_type, AIService, provider)
                method = getattr(service, operation)
                return await method(*args, **kwargs)
            except Exception as e:
                last_error = e
                continue
        
        # All providers failed
        raise RuntimeError(f"All providers failed for {operation}: {last_error}")