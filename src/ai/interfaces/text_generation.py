"""
Text Generation Service Interface
"""
from abc import abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from .base import AIService

@dataclass
class TextGenerationRequest:
    prompt: str
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    top_p: float = 0.9
    stop_sequences: Optional[List[str]] = None
    system_prompt: Optional[str] = None
    response_format: Optional[str] = None  # "text" or "json"
    
@dataclass
class TextGenerationResponse:
    text: str
    usage: Dict[str, int]  # tokens used, etc.
    model: str
    provider: str
    cost_estimate: float
    metadata: Dict[str, Any] = None

class TextGenerationService(AIService):
    """Interface for text generation services"""
    
    @abstractmethod
    async def generate(self, request: TextGenerationRequest) -> TextGenerationResponse:
        """Generate text based on prompt"""
        pass
    
    @abstractmethod
    async def generate_structured(self, 
                                prompt: str, 
                                schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured output matching schema"""
        pass
    
    @abstractmethod
    async def chat(self, 
                  messages: List[Dict[str, str]], 
                  **kwargs) -> TextGenerationResponse:
        """Chat-based generation with message history"""
        pass