"""
AI Service Factory & Registry
"""
from typing import Dict, Type, Optional, List
from .interfaces.base import AIService, AIProvider, AIServiceConfig, AIServiceType
from .interfaces.text_generation import TextGenerationService

# Provider implementations
from .providers.gemini.text_generation import GeminiTextService

class AIServiceFactory:
    """Factory for creating AI service instances"""
    
    # Registry of available implementations
    _registry: Dict[AIServiceType, Dict[AIProvider, Type[AIService]]] = {
        AIServiceType.TEXT_GENERATION: {
            AIProvider.GEMINI: GeminiTextService,
        },
        # Will add more service types and providers here
    }
    
    @classmethod
    def create(cls, 
               service_type: AIServiceType, 
               config: AIServiceConfig) -> AIService:
        """Create an AI service instance"""
        
        if service_type not in cls._registry:
            raise ValueError(f"Unknown service type: {service_type}")
        
        providers = cls._registry[service_type]
        if config.provider not in providers:
            raise ValueError(
                f"Provider {config.provider} not available for {service_type}. "
                f"Available providers: {list(providers.keys())}"
            )
        
        service_class = providers[config.provider]
        return service_class(config)
    
    @classmethod
    def register(cls, 
                service_type: AIServiceType, 
                provider: AIProvider, 
                implementation: Type[AIService]):
        """Register a new implementation"""
        if service_type not in cls._registry:
            cls._registry[service_type] = {}
        cls._registry[service_type][provider] = implementation
    
    @classmethod
    def get_available_providers(cls, service_type: AIServiceType) -> List[AIProvider]:
        """Get list of available providers for a service type"""
        if service_type not in cls._registry:
            return []
        return list(cls._registry[service_type].keys())
    
    @classmethod
    def initialize_providers(cls):
        """Initialize all providers - call this after factory is loaded"""
        from .providers import register_all_providers
        register_all_providers()