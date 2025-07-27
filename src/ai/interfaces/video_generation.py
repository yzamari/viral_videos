"""Video generation service interface."""
from abc import abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum
from src.ai.interfaces.base import AIService


class VideoStatus(Enum):
    """Video generation job status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class VideoGenerationRequest:
    """Request for video generation."""
    prompt: str
    duration: float
    style: Optional[str] = None
    aspect_ratio: Optional[str] = None
    platform: Optional[str] = None
    resolution: Optional[str] = None
    fps: Optional[int] = None
    negative_prompt: Optional[str] = None
    session_context: Optional[Any] = None  # SessionContext
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls."""
        return {
            'prompt': self.prompt,
            'duration': self.duration,
            'style': self.style,
            'aspect_ratio': self.aspect_ratio,
            'platform': self.platform,
            'resolution': self.resolution,
            'fps': self.fps,
            'negative_prompt': self.negative_prompt
        }


@dataclass
class VideoGenerationResponse:
    """Response from video generation."""
    video_path: Optional[str]
    job_id: Optional[str]
    metadata: Dict[str, Any]
    provider_used: str
    generation_time: float
    status: VideoStatus
    error_message: Optional[str] = None


@dataclass
class VideoJobStatus:
    """Status of a video generation job."""
    job_id: str
    status: VideoStatus
    progress: Optional[float] = None
    video_path: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None


class VideoGenerationService(AIService):
    """Abstract interface for video generation services."""
    
    @abstractmethod
    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResponse:
        """Generate video from prompt.
        
        May return immediately with a job_id for async generation.
        
        Args:
            request: Video generation request
            
        Returns:
            Video generation response with path or job_id
        """
        pass
    
    @abstractmethod
    async def check_status(self, job_id: str) -> VideoJobStatus:
        """Check status of a video generation job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Current job status
        """
        pass
    
    async def wait_for_completion(self, job_id: str, timeout: int = 300) -> VideoJobStatus:
        """Wait for a video generation job to complete.
        
        Default implementation polls check_status.
        
        Args:
            job_id: Job identifier
            timeout: Maximum wait time in seconds
            
        Returns:
            Final job status
        """
        import asyncio
        import time
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = await self.check_status(job_id)
            if status.status in [VideoStatus.COMPLETED, VideoStatus.FAILED]:
                return status
            await asyncio.sleep(5)  # Poll every 5 seconds
        
        # Timeout reached
        return VideoJobStatus(
            job_id=job_id,
            status=VideoStatus.FAILED,
            error_message=f"Timeout after {timeout} seconds"
        )