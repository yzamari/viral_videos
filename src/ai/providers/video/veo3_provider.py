"""
Google Veo3 Video Generation Provider
Refactored to use clean interfaces
"""
import os
import time
import json
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
from ...interfaces.auth import Credentials
from ..auth.google_auth import GoogleCloudAuthProvider

class Veo3VideoProvider(VideoGenerationProvider):
    """Google Veo3 video generation implementation"""
    
    # Provider capabilities
    SUPPORTED_STYLES = [
        VideoStyle.REALISTIC,
        VideoStyle.CINEMATIC,
        VideoStyle.DOCUMENTARY,
        VideoStyle.COMMERCIAL,
        VideoStyle.ARTISTIC
    ]
    
    SUPPORTED_RESOLUTIONS = [
        "1920x1080",
        "1280x720",
        "3840x2160",
        "768x768",
        "1024x1024"
    ]
    
    MAX_DURATION = 10.0  # seconds
    SUPPORTS_AUDIO = True  # Veo3 supports native audio
    
    def __init__(self, config: VideoGenerationConfig):
        super().__init__(config)
        
        # Veo3 specific configuration
        self.project_id = config.custom_config.get('project_id')
        self.location = config.custom_config.get('location', 'us-central1')
        self.model_name = config.custom_config.get('model', 'veo-3.0-generate-preview')
        
        # Use fast mode if specified
        if config.quality == VideoQuality.DRAFT:
            self.model_name = 'veo-3.0-fast-generate-001'
            self.SUPPORTS_AUDIO = False
        
        # API endpoint
        self.api_base = f"https://{self.location}-aiplatform.googleapis.com/v1beta1"
        self.endpoint = f"{self.api_base}/projects/{self.project_id}/locations/{self.location}/models/{self.model_name}:predict"
    
    async def generate_video(self, request: EnhancedVideoRequest) -> EnhancedVideoResponse:
        """Generate video using Veo3"""
        try:
            start_time = time.time()
            
            # Ensure authentication
            credentials = await self._ensure_authenticated()
            
            # Prepare Veo3 request
            veo_request = self._prepare_veo_request(request)
            
            # Make API call
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {credentials.access_token}',
                    'Content-Type': 'application/json'
                }
                
                async with session.post(
                    self.endpoint,
                    json=veo_request,
                    headers=headers
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return EnhancedVideoResponse(
                            success=False,
                            error_message=f"Veo3 API error: {error_text}",
                            provider_used=VideoProvider.VEO3
                        )
                    
                    result = await response.json()
            
            # Parse response
            job_id = result.get('name', '').split('/')[-1]
            
            # For async generation, return job ID
            return EnhancedVideoResponse(
                success=True,
                job_id=job_id,
                provider_used=VideoProvider.VEO3,
                generation_time=time.time() - start_time,
                metadata=result
            )
            
        except Exception as e:
            return EnhancedVideoResponse(
                success=False,
                error_message=str(e),
                provider_used=VideoProvider.VEO3
            )
    
    async def check_job_status(self, job_id: str) -> EnhancedVideoResponse:
        """Check status of Veo3 generation job"""
        try:
            credentials = await self._ensure_authenticated()
            
            # Get job status
            job_endpoint = f"{self.api_base}/projects/{self.project_id}/locations/{self.location}/operations/{job_id}"
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {credentials.access_token}'
                }
                
                async with session.get(job_endpoint, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return EnhancedVideoResponse(
                            success=False,
                            error_message=f"Failed to check job status: {error_text}"
                        )
                    
                    result = await response.json()
            
            # Check if job is done
            if result.get('done'):
                # Get video URL from response
                video_url = result.get('response', {}).get('videoUrl')
                
                if video_url:
                    # Download and store video if storage provider is configured
                    video_asset = VideoAsset(
                        url=video_url,
                        duration=result.get('response', {}).get('duration', 0),
                        metadata=result
                    )
                    
                    if self.storage_provider:
                        # Download video
                        async with aiohttp.ClientSession() as session:
                            async with session.get(video_url) as resp:
                                video_data = await resp.read()
                        
                        # Store video
                        storage_key = f"videos/veo3/{job_id}.mp4"
                        storage_obj = await self.store_video(video_data, storage_key)
                        video_asset.storage_key = storage_key
                        video_asset.url = await self.storage_provider.get_url(storage_key)
                    
                    return EnhancedVideoResponse(
                        success=True,
                        video_asset=video_asset,
                        job_id=job_id,
                        provider_used=VideoProvider.VEO3
                    )
                else:
                    # Job failed
                    error = result.get('error', {}).get('message', 'Unknown error')
                    return EnhancedVideoResponse(
                        success=False,
                        error_message=error,
                        job_id=job_id
                    )
            else:
                # Job still processing
                return EnhancedVideoResponse(
                    success=False,
                    job_id=job_id,
                    error_message="Job still processing"
                )
            
        except Exception as e:
            return EnhancedVideoResponse(
                success=False,
                error_message=str(e)
            )
    
    def _prepare_veo_request(self, request: EnhancedVideoRequest) -> Dict[str, Any]:
        """Prepare request for Veo3 API"""
        # Build prompt with style and camera instructions
        prompt_parts = [request.prompt]
        
        if request.style:
            prompt_parts.append(f"{request.style.value} style")
        
        if request.camera_motion:
            prompt_parts.append(f"Camera: {request.camera_motion}")
        
        if request.lighting:
            prompt_parts.append(f"Lighting: {request.lighting}")
        
        if request.color_grading:
            prompt_parts.append(f"Color grading: {request.color_grading}")
        
        full_prompt = ", ".join(prompt_parts)
        
        # Build Veo3 request
        veo_request = {
            "instances": [{
                "prompt": full_prompt,
                "duration": min(request.duration, self.MAX_DURATION),
                "aspect_ratio": request.aspect_ratio,
                "resolution": request.resolution or "1920x1080"
            }],
            "parameters": {
                "temperature": 0.7,
                "top_p": 0.9
            }
        }
        
        # Add audio prompt if supported
        if self.SUPPORTS_AUDIO and request.audio_prompt:
            veo_request["instances"][0]["audio_prompt"] = request.audio_prompt
        
        # Add negative prompt
        if request.negative_prompt:
            veo_request["instances"][0]["negative_prompt"] = request.negative_prompt
        
        # Add seed for reproducibility
        if request.seed:
            veo_request["parameters"]["seed"] = request.seed
        
        return veo_request
    
    def supports_audio(self) -> bool:
        """Check if provider supports audio generation"""
        return self.SUPPORTS_AUDIO
    
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
        # Veo3 pricing (example rates)
        base_cost = 0.05  # Base cost per second
        
        # Quality multiplier
        quality_multiplier = {
            VideoQuality.DRAFT: 0.5,
            VideoQuality.STANDARD: 1.0,
            VideoQuality.HIGH: 1.5,
            VideoQuality.PREMIUM: 2.0
        }.get(request.quality or VideoQuality.STANDARD, 1.0)
        
        # Resolution multiplier
        resolution = request.resolution or "1920x1080"
        resolution_multiplier = 1.0
        if "3840" in resolution:  # 4K
            resolution_multiplier = 2.0
        elif "1280" in resolution:  # 720p
            resolution_multiplier = 0.8
        
        # Calculate total cost
        total_cost = base_cost * request.duration * quality_multiplier * resolution_multiplier
        
        # Add audio generation cost if applicable
        if self.SUPPORTS_AUDIO and request.audio_prompt:
            total_cost += 0.02 * request.duration
        
        return total_cost
    
    def is_available(self) -> bool:
        """Check if provider is currently available"""
        # Check if we have valid project configuration
        return bool(self.project_id and self.location)