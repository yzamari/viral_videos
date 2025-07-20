"""
Base AI Service Interface
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class AIProvider(Enum):
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"
    LOCAL = "local"

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
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """Validate provider-specific configuration"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return human-readable provider name"""
        pass
    
    @abstractmethod
    def estimate_cost(self, **kwargs) -> float:
        """Estimate cost for the operation"""
        pass