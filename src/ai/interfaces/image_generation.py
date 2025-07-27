"""Image generation service interface."""
from abc import abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from src.ai.interfaces.base import AIService


@dataclass
class ImageGenerationRequest:
    """Request for image generation."""
    prompt: str
    style: Optional[str] = None
    aspect_ratio: str = "1:1"
    negative_prompt: Optional[str] = None
    num_images: int = 1
    width: Optional[int] = None
    height: Optional[int] = None
    session_context: Optional[Any] = None  # SessionContext
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls."""
        return {
            'prompt': self.prompt,
            'style': self.style,
            'aspect_ratio': self.aspect_ratio,
            'negative_prompt': self.negative_prompt,
            'num_images': self.num_images,
            'width': self.width,
            'height': self.height
        }


@dataclass
class ImageGenerationResponse:
    """Response from image generation."""
    image_paths: List[str]
    metadata: Dict[str, Any]
    provider_used: str
    generation_time: float
    
    @property
    def first_image(self) -> Optional[str]:
        """Get the first image path if available."""
        return self.image_paths[0] if self.image_paths else None


class ImageGenerationService(AIService):
    """Abstract interface for image generation services."""
    
    @abstractmethod
    async def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        """Generate image from prompt.
        
        Args:
            request: Image generation request
            
        Returns:
            Image generation response with paths and metadata
        """
        pass
    
    @abstractmethod
    async def generate_batch(self, requests: List[ImageGenerationRequest]) -> List[ImageGenerationResponse]:
        """Generate multiple images in batch.
        
        Args:
            requests: List of image generation requests
            
        Returns:
            List of image generation responses
        """
        pass