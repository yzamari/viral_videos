"""Vertex AI Imagen image generation service implementation."""
import os
import time
from typing import List, Optional, Dict, Any

from src.ai.interfaces.base import AIServiceConfig, AIProvider
from src.ai.interfaces.image_generation import (
    ImageGenerationService, 
    ImageGenerationRequest, 
    ImageGenerationResponse
)
from src.generators.vertex_imagen_client import VertexImagenClient
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class VertexImagenGenerationService(ImageGenerationService):
    """Vertex AI Imagen implementation of image generation service."""
    
    def __init__(self, config: AIServiceConfig):
        """Initialize Vertex Imagen generation service.
        
        Args:
            config: Service configuration
        """
        super().__init__(config)
        
        # Get project ID and location from config
        project_id = config.custom_config.get('project_id') or os.getenv('GOOGLE_CLOUD_PROJECT')
        location = config.custom_config.get('location', 'us-central1')
        
        # Initialize the underlying Vertex client
        self.client = VertexImagenClient(project_id=project_id, location=location)
        
        if not self.client.initialized:
            logger.warning("Vertex Imagen client failed to initialize - check project ID and credentials")
        else:
            logger.info(f"Initialized Vertex Imagen service for project: {project_id}")
    
    async def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        """Generate image using Vertex AI Imagen.
        
        Args:
            request: Image generation request
            
        Returns:
            Image generation response
        """
        start_time = time.time()
        
        if not self.client.initialized:
            logger.error("Vertex Imagen client not initialized")
            return ImageGenerationResponse(
                image_paths=[],
                metadata={'error': 'Vertex AI not initialized'},
                provider_used='vertex_imagen',
                generation_time=0
            )
        
        try:
            # Generate image using the client
            image_path = self.client.generate_image(
                prompt=request.prompt,
                negative_prompt=request.negative_prompt,
                style=request.style,
                aspect_ratio=request.aspect_ratio,
                number_of_images=request.num_images
            )
            
            generation_time = time.time() - start_time
            
            # The client returns a single path even for multiple images
            # In the future, we might need to handle multiple paths
            image_paths = [image_path] if image_path else []
            
            return ImageGenerationResponse(
                image_paths=image_paths,
                metadata={
                    'prompt': request.prompt,
                    'negative_prompt': request.negative_prompt,
                    'aspect_ratio': request.aspect_ratio,
                    'style': request.style,
                    'provider': 'vertex_imagen',
                    'model': 'imagegeneration@002'
                },
                provider_used='vertex_imagen',
                generation_time=generation_time
            )
            
        except Exception as e:
            logger.error(f"Error generating image with Vertex Imagen: {str(e)}")
            return ImageGenerationResponse(
                image_paths=[],
                metadata={'error': str(e)},
                provider_used='vertex_imagen',
                generation_time=time.time() - start_time
            )
    
    async def generate_batch(self, requests: List[ImageGenerationRequest]) -> List[ImageGenerationResponse]:
        """Generate multiple images in batch.
        
        Vertex Imagen doesn't support true batch generation, so we generate sequentially.
        
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
        # Vertex AI will use ADC (Application Default Credentials) if no explicit credentials
        # So we just need to ensure the client can initialize
        if not self.client.initialized:
            logger.warning("Vertex AI Imagen client not initialized - check credentials and project ID")
    
    async def estimate_cost(self, request: Any) -> float:
        """Estimate cost for image generation.
        
        Vertex AI Imagen pricing (as of 2025):
        - $0.020 per image (1024x1024)
        
        Args:
            request: Image generation request
            
        Returns:
            Estimated cost in USD
        """
        if isinstance(request, ImageGenerationRequest):
            # $0.020 per image
            return 0.020 * request.num_images
        return 0.0