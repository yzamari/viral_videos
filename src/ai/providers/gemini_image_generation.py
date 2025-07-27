"""Gemini image generation service implementation."""
import os
import time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from src.ai.interfaces.base import AIServiceConfig, AIProvider
from src.ai.interfaces.image_generation import (
    ImageGenerationService, 
    ImageGenerationRequest, 
    ImageGenerationResponse
)
from src.generators.gemini_image_client import GeminiImageClient
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class GeminiImageGenerationService(ImageGenerationService):
    """Gemini implementation of image generation service."""
    
    def __init__(self, config: AIServiceConfig):
        """Initialize Gemini image generation service.
        
        Args:
            config: Service configuration
        """
        super().__init__(config)
        
        # Get API key and output directory from config
        api_key = config.api_key or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("Google API key not found in config or environment")
        
        output_dir = config.custom_config.get('output_dir', 'outputs/gemini_images')
        
        # Initialize the underlying Gemini client
        self.client = GeminiImageClient(api_key=api_key, output_dir=output_dir)
        logger.info(f"Initialized Gemini image generation service with output dir: {output_dir}")
    
    async def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        """Generate image using Gemini.
        
        Args:
            request: Image generation request
            
        Returns:
            Image generation response
        """
        start_time = time.time()
        
        try:
            # Prepare prompt with style if provided
            prompt = request.prompt
            if request.style:
                prompt = f"{request.style} style: {prompt}"
            
            # Generate image using the client
            # GeminiImageClient expects: prompt, style, output_path
            output_path = os.path.join(
                self.client.images_dir, 
                f"gemini_{int(time.time())}_{request.aspect_ratio.replace(':', 'x')}.png"
            )
            
            image_path = self.client.generate_image(
                prompt=prompt,
                style=request.style or "",
                output_path=output_path
            )
            
            generation_time = time.time() - start_time
            
            return ImageGenerationResponse(
                image_paths=[image_path] if image_path else [],
                metadata={
                    'prompt': prompt,
                    'aspect_ratio': request.aspect_ratio,
                    'style': request.style,
                    'provider': 'gemini'
                },
                provider_used='gemini',
                generation_time=generation_time
            )
            
        except Exception as e:
            logger.error(f"Error generating image with Gemini: {str(e)}")
            # Return empty response on error
            return ImageGenerationResponse(
                image_paths=[],
                metadata={'error': str(e)},
                provider_used='gemini',
                generation_time=time.time() - start_time
            )
    
    async def generate_batch(self, requests: List[ImageGenerationRequest]) -> List[ImageGenerationResponse]:
        """Generate multiple images in batch.
        
        Gemini doesn't support true batch generation, so we generate sequentially.
        
        Args:
            requests: List of image generation requests
            
        Returns:
            List of image generation responses
        """
        responses = []
        for request in requests:
            response = await self.generate_image(request)
            responses.append(response)
        
        return responses
    
    def validate_config(self) -> None:
        """Validate service configuration."""
        if not self.config.api_key and not os.getenv('GOOGLE_API_KEY'):
            raise ValueError("Google API key is required for Gemini image generation")
    
    async def estimate_cost(self, request: Any) -> float:
        """Estimate cost for image generation.
        
        Gemini 2.0 Flash image generation pricing (as of 2025):
        - $0.04 per image
        
        Args:
            request: Image generation request
            
        Returns:
            Estimated cost in USD
        """
        if isinstance(request, ImageGenerationRequest):
            # $0.04 per image
            return 0.04 * request.num_images
        return 0.0