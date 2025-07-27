"""
Base AI Service Interface
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class AIServiceType(Enum):
    TEXT_GENERATION = "text_generation"
    VIDEO_GENERATION = "video_generation"
    AUDIO_GENERATION = "audio_generation"
    IMAGE_GENERATION = "image_generation"
    SPEECH_SYNTHESIS = "speech_synthesis"  # For TTS services

class AIProvider(Enum):
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"
    LOCAL = "local"
    VERTEX = "vertex"  # For Vertex AI services
    GOOGLE = "google"  # For Google Cloud services (TTS, etc.)

@dataclass
class AIServiceConfig:
    provider: AIProvider
    api_key: Optional[str]
    model_name: str
    max_retries: int = 3
    timeout: int = 60
    custom_config: Dict[str, Any] = None

class AIService(ABC):
    """Base interface for all AI services"""
    
    def __init__(self, config: AIServiceConfig):
        self.config = config
        if not config.custom_config:
            config.custom_config = {}
        self.validate_config()
    
    def validate_config(self) -> None:
        """Validate provider-specific configuration. Override if needed."""
        pass
    
    def get_provider_name(self) -> str:
        """Return human-readable provider name"""
        return self.config.provider.value
    
    @abstractmethod
    async def estimate_cost(self, request: Any) -> float:
        """Estimate cost for the operation"""
        pass