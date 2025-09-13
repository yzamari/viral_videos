"""
RunwayML Video Generation Provider
Shows how easy it is to add new providers with the interface
"""
import time
import aiohttp
from typing import Optional, List, Dict, Any
from ...interfaces.video_generation_enhanced import (
    VideoGenerationProvider,
    VideoGenerationConfig,
    EnhancedVideoRequest,
    EnhancedVideoResponse,
    VideoAsset,
    VideoProvider,
    VideoStyle,
    VideoQuality
)
from ..auth.api_key_auth import APIKeyAuthProvider

class RunwayMLVideoProvider(VideoGenerationProvider):
    """RunwayML Gen-3 video generation implementation"""
    
    # Provider capabilities
    SUPPORTED_STYLES = [
        VideoStyle.REALISTIC,
        VideoStyle.CINEMATIC,
        VideoStyle.ANIME,
        VideoStyle.ARTISTIC,
        VideoStyle.MUSIC_VIDEO
    ]
    
    SUPPORTED_RESOLUTIONS = [
        "1280x768",
        "768x1280",
        "1024x1024",
        "1280x720",
        "1920x1080"
    ]
    
    MAX_DURATION = 10.0  # Gen-3 supports up to 10 seconds
    SUPPORTS_AUDIO = False  # RunwayML doesn't generate audio natively
    
    def __init__(self, config: VideoGenerationConfig):
        super().__init__(config)
        
        # RunwayML API configuration
        self.api_base = "https://api.runwayml.com/v1"
        self.model = config.custom_config.get('model', 'gen3')
        
        # Ensure we have API key auth
        if not isinstance(config.auth_provider, APIKeyAuthProvider):
            # Create API key auth from config
            api_key = config.custom_config.get('api_key')
            if not api_key:
                raise ValueError("RunwayML requires an API key")
            self.auth_provider = APIKeyAuthProvider(api_key, "Authorization", "Bearer")
    
    async def generate_video(self, request: EnhancedVideoRequest) -> EnhancedVideoResponse:
        """Generate video using RunwayML"""
        try:
            start_time = time.time()
            
            # Get auth headers
            credentials = await self._ensure_authenticated()
            headers = credentials.get_headers()
            headers['Content-Type'] = 'application/json'
            
            # Prepare RunwayML request
            runway_request = self._prepare_runway_request(request)
            
            # Make API call to start generation
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/generate",
                    json=runway_request,
                    headers=headers
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return EnhancedVideoResponse(
                            success=False,
                            error_message=f"RunwayML API error: {error_text}",
                            provider_used=VideoProvider.RUNWAY_ML
                        )
                    
                    result = await response.json()
            
            # Get job ID
            job_id = result.get('id')
            
            return EnhancedVideoResponse(
                success=True,
                job_id=job_id,
                provider_used=VideoProvider.RUNWAY_ML,
                generation_time=time.time() - start_time,
                metadata=result
            )
            
        except Exception as e:
            return EnhancedVideoResponse(
                success=False,
                error_message=str(e),
                provider_used=VideoProvider.RUNWAY_ML
            )
    
    async def check_job_status(self, job_id: str) -> EnhancedVideoResponse:
        """Check status of RunwayML generation job"""
        try:
            credentials = await self._ensure_authenticated()
            headers = credentials.get_headers()
            
            # Check job status
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base}/tasks/{job_id}",
                    headers=headers
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return EnhancedVideoResponse(
                            success=False,
                            error_message=f"Failed to check job status: {error_text}"
                        )
                    
                    result = await response.json()
            
            # Check status
            status = result.get('status')
            
            if status == 'SUCCEEDED':
                # Get video URL
                video_url = result.get('output', {}).get('video_url')
                
                if video_url:
                    video_asset = VideoAsset(
                        url=video_url,
                        duration=result.get('output', {}).get('duration', request.duration),
                        format="mp4",
                        resolution=result.get('output', {}).get('resolution'),
                        metadata=result
                    )
                    
                    # Store video if storage provider is configured
                    if self.storage_provider:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(video_url) as resp:
                                video_data = await resp.read()
                        
                        storage_key = f"videos/runwayml/{job_id}.mp4"
                        await self.store_video(video_data, storage_key)
                        video_asset.storage_key = storage_key
                    
                    return EnhancedVideoResponse(
                        success=True,
                        video_asset=video_asset,
                        job_id=job_id,
                        provider_used=VideoProvider.RUNWAY_ML
                    )
            
            elif status == 'FAILED':
                error = result.get('error', 'Generation failed')
                return EnhancedVideoResponse(
                    success=False,
                    error_message=error,
                    job_id=job_id,
                    provider_used=VideoProvider.RUNWAY_ML
                )
            
            else:
                # Still processing
                return EnhancedVideoResponse(
                    success=False,
                    job_id=job_id,
                    error_message=f"Job status: {status}",
                    provider_used=VideoProvider.RUNWAY_ML
                )
            
        except Exception as e:
            return EnhancedVideoResponse(
                success=False,
                error_message=str(e),
                provider_used=VideoProvider.RUNWAY_ML
            )
    
    def _prepare_runway_request(self, request: EnhancedVideoRequest) -> Dict[str, Any]:
        """Prepare request for RunwayML API"""
        # Map our style enum to RunwayML styles
        style_mapping = {
            VideoStyle.REALISTIC: "photorealistic",
            VideoStyle.CINEMATIC: "cinematic",
            VideoStyle.ANIME: "anime",
            VideoStyle.ARTISTIC: "artistic",
            VideoStyle.MUSIC_VIDEO: "music_video"
        }
        
        runway_style = style_mapping.get(request.style, "cinematic")
        
        # Build RunwayML request
        runway_request = {
            "model": self.model,
            "prompt": request.prompt,
            "duration_seconds": min(request.duration, self.MAX_DURATION),
            "aspect_ratio": request.aspect_ratio or "16:9",
            "style": runway_style,
            "options": {
                "resolution": request.resolution or "1280x768",
                "fps": request.fps or 24
            }
        }
        
        # Add camera motion if specified
        if request.camera_motion:
            runway_request["options"]["camera_motion"] = request.camera_motion
        
        # Add seed for reproducibility
        if request.seed:
            runway_request["seed"] = request.seed
        
        return runway_request
    
    def supports_audio(self) -> bool:
        """RunwayML doesn't generate audio"""
        return False
    
    def supports_style(self, style: VideoStyle) -> bool:
        """Check if provider supports specific style"""
        return style in self.SUPPORTED_STYLES
    
    def get_max_duration(self) -> float:
        """Get maximum supported video duration"""
        return self.MAX_DURATION
    
    def get_supported_resolutions(self) -> List[str]:
        """Get list of supported resolutions"""
        return self.SUPPORTED_RESOLUTIONS
    
    async def estimate_cost(self, request: EnhancedVideoRequest) -> float:
        """Estimate generation cost"""
        # RunwayML pricing: ~$0.05 per second for Gen-3
        base_cost = 0.05
        
        # Quality affects generation time, not direct cost
        quality_multiplier = {
            VideoQuality.DRAFT: 0.8,
            VideoQuality.STANDARD: 1.0,
            VideoQuality.HIGH: 1.2,
            VideoQuality.PREMIUM: 1.5
        }.get(request.quality or VideoQuality.STANDARD, 1.0)
        
        return base_cost * request.duration * quality_multiplier
    
    def is_available(self) -> bool:
        """Check if provider is available"""
        # Check if we have API key configured
        return isinstance(self.auth_provider, APIKeyAuthProvider)