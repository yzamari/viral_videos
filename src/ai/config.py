"""
AI Configuration Management
"""
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
import os
import json
from .interfaces.base import AIServiceConfig, AIProvider, AIServiceType

@dataclass
class AIConfiguration:
    """Central AI configuration"""
    
    # Default providers for each service type
    default_providers: Dict[AIServiceType, AIProvider] = field(default_factory=dict)
    
    # Service-specific configurations
    service_configs: Dict[str, AIServiceConfig] = field(default_factory=dict)
    
    # API keys (can be overridden by environment variables)
    api_keys: Dict[AIProvider, str] = field(default_factory=dict)
    
    # Global settings
    enable_fallbacks: bool = True
    enable_caching: bool = True
    enable_cost_tracking: bool = True
    max_retries: int = 3
    
    @classmethod
    def from_file(cls, config_path: str) -> 'AIConfiguration':
        """Load configuration from JSON file"""
        with open(config_path, 'r') as f:
            data = json.load(f)
        
        config = cls()
        
        # Load default providers
        for service_type, provider in data.get('default_providers', {}).items():
            config.default_providers[AIServiceType(service_type)] = AIProvider(provider)
        
        # Load API keys (with env var override)
        for provider, key in data.get('api_keys', {}).items():
            env_key = f"{provider.upper()}_API_KEY"
            config.api_keys[AIProvider(provider)] = os.getenv(env_key, key)
        
        # Load service configs
        for name, cfg in data.get('service_configs', {}).items():
            config.service_configs[name] = AIServiceConfig(**cfg)
        
        return config
    
    @classmethod
    def create_default(cls) -> 'AIConfiguration':
        """Create default configuration"""
        config = cls()
        
        # Set default providers
        config.default_providers[AIServiceType.TEXT_GENERATION] = AIProvider.GEMINI
        config.default_providers[AIServiceType.IMAGE_GENERATION] = AIProvider.GEMINI
        config.default_providers[AIServiceType.VIDEO_GENERATION] = AIProvider.GEMINI  # VEO
        config.default_providers[AIServiceType.SPEECH_SYNTHESIS] = AIProvider.GOOGLE
        
        # Load API keys from environment
        config.api_keys[AIProvider.GEMINI] = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        config.api_keys[AIProvider.GOOGLE] = os.getenv('GOOGLE_API_KEY')
        config.api_keys[AIProvider.VERTEX] = os.getenv('GOOGLE_API_KEY')
        
        return config
    
    def get_service_config(self, 
                          service_type: AIServiceType, 
                          provider: Optional[AIProvider] = None) -> AIServiceConfig:
        """Get configuration for a service"""
        
        # Use specified provider or default
        if provider is None:
            provider = self.default_providers.get(service_type)
            if provider is None:
                raise ValueError(f"No default provider configured for {service_type}")
        
        # Build config
        config_key = f"{service_type.value}_{provider.value}"
        
        if config_key in self.service_configs:
            return self.service_configs[config_key]
        
        # Create default config
        return AIServiceConfig(
            provider=provider,
            api_key=self.api_keys.get(provider),
            model_name=self._get_default_model(service_type, provider),
            max_retries=self.max_retries
        )
    
    def _get_default_model(self, service_type: AIServiceType, provider: AIProvider) -> str:
        """Get default model for provider and service type"""
        defaults = {
            (AIServiceType.TEXT_GENERATION, AIProvider.GEMINI): "gemini-1.5-flash",
            (AIServiceType.TEXT_GENERATION, AIProvider.OPENAI): "gpt-4-turbo",
            (AIServiceType.TEXT_GENERATION, AIProvider.ANTHROPIC): "claude-3-opus",
            (AIServiceType.IMAGE_GENERATION, AIProvider.GEMINI): "gemini-pro-vision",
            (AIServiceType.IMAGE_GENERATION, AIProvider.VERTEX): "imagegeneration@002",
            (AIServiceType.VIDEO_GENERATION, AIProvider.GEMINI): "veo",
            (AIServiceType.SPEECH_SYNTHESIS, AIProvider.GOOGLE): "en-US-Neural2-J",
        }
        return defaults.get((service_type, provider), "default")