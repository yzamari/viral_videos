"""VEO video generation service implementation."""
import os
import time
from typing import Optional, Dict, Any

from src.ai.interfaces.base import AIServiceConfig, AIProvider
from src.ai.interfaces.video_generation import (
    VideoGenerationService,
    VideoGenerationRequest,
    VideoGenerationResponse,
    VideoStatus,
    VideoJobStatus
)
from src.generators.veo_client_factory import VeoClientFactory
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class VEOVideoGenerationService(VideoGenerationService):
    """VEO implementation of video generation service."""
    
    def __init__(self, config: AIServiceConfig):
        """Initialize VEO video generation service.
        
        Args:
            config: Service configuration
        """
        super().__init__(config)
        
        # Initialize VEO client factory
        self.veo_factory = VeoClientFactory()
        
        # Get preferences from config
        self.prefer_veo = config.custom_config.get('prefer_veo', False)
        self.disable_veo3 = config.custom_config.get('disable_veo3', False)
        self.output_dir = config.custom_config.get('output_dir', 'outputs/veo_videos')
        
        logger.info(f"Initialized VEO video generation service (prefer_veo={self.prefer_veo}, disable_veo3={self.disable_veo3})")
    
    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResponse:
        """Generate video using VEO.
        
        Args:
            request: Video generation request
            
        Returns:
            Video generation response
        """
        start_time = time.time()
        
        try:
            # Get appropriate VEO client from factory with aspect ratio awareness
            # Extract aspect ratio from request if available
            aspect_ratio = getattr(request, 'aspect_ratio', '16:9')
            if hasattr(request, 'config') and hasattr(request.config, 'aspect_ratio'):
                aspect_ratio = request.config.aspect_ratio
            
            client = self.veo_factory.get_aspect_ratio_aware_client(
                output_dir=self.output_dir,
                aspect_ratio=aspect_ratio
            )
            
            if not client:
                logger.error("Failed to get VEO client from factory")
                return VideoGenerationResponse(
                    video_path=None,
                    job_id=None,
                    metadata={'error': 'No VEO client available'},
                    provider_used='veo',
                    generation_time=0,
                    status=VideoStatus.FAILED,
                    error_message='No VEO client available'
                )
            
            # Prepare prompt with style if provided
            prompt = request.prompt
            if request.style:
                prompt = f"{request.style} style: {prompt}"
            
            # Generate video using the client
            result = client.generate_video_from_prompt(
                prompt=prompt,
                duration=request.duration,
                aspect_ratio=request.aspect_ratio or "16:9"
            )
            
            generation_time = time.time() - start_time
            
            # Map result to response
            if result and 'video_path' in result:
                return VideoGenerationResponse(
                    video_path=result['video_path'],
                    job_id=result.get('job_id'),
                    metadata={
                        'prompt': prompt,
                        'duration': request.duration,
                        'aspect_ratio': request.aspect_ratio,
                        'model_version': result.get('model_version', 'unknown'),
                        'provider': f"veo_{result.get('model_version', 'unknown')}"
                    },
                    provider_used=f"veo_{result.get('model_version', 'unknown')}",
                    generation_time=generation_time,
                    status=VideoStatus.COMPLETED
                )
            else:
                # Job-based generation (async)
                return VideoGenerationResponse(
                    video_path=None,
                    job_id=result.get('job_id') if result else None,
                    metadata=result or {},
                    provider_used='veo',
                    generation_time=generation_time,
                    status=VideoStatus.PROCESSING if result and 'job_id' in result else VideoStatus.FAILED,
                    error_message=result.get('error') if result else 'Generation failed'
                )
                
        except Exception as e:
            logger.error(f"Error generating video with VEO: {str(e)}")
            return VideoGenerationResponse(
                video_path=None,
                job_id=None,
                metadata={'error': str(e)},
                provider_used='veo',
                generation_time=time.time() - start_time,
                status=VideoStatus.FAILED,
                error_message=str(e)
            )
    
    async def check_status(self, job_id: str) -> VideoJobStatus:
        """Check status of a VEO video generation job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Current job status
        """
        # VEO clients typically wait for completion in generate_video_from_prompt
        # This is here for future async support
        logger.warning(f"check_status called for job {job_id} but VEO currently uses sync generation")
        
        return VideoJobStatus(
            job_id=job_id,
            status=VideoStatus.COMPLETED,
            progress=1.0,
            video_path=None,
            error_message="VEO uses synchronous generation",
            metadata={}
        )
    
    def validate_config(self) -> None:
        """Validate service configuration."""
        # VEO uses Google Cloud credentials
        # Factory will handle authentication
        pass
    
    async def estimate_cost(self, request: Any) -> float:
        """Estimate cost for video generation.
        
        VEO pricing is not publicly available yet.
        
        Args:
            request: Video generation request
            
        Returns:
            Estimated cost in USD
        """
        if isinstance(request, VideoGenerationRequest):
            # Rough estimate based on duration
            # Actual pricing TBD
            return request.duration * 0.10  # $0.10 per second estimate
        return 0.0