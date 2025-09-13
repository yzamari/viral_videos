"""
Enhanced Video Generation Service Interface
Provider-agnostic video generation with full abstraction
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Protocol, runtime_checkable
from enum import Enum
from .base import AIService, AIServiceConfig
from .auth import AuthProvider, Credentials
from .storage import StorageProvider, StorageObject

class VideoProvider(Enum):
    """Available video generation providers"""
    VEO3 = "veo3"
    VEO3_FAST = "veo3_fast"
    RUNWAY_ML = "runway_ml"
    STABILITY_AI = "stability_ai"
    PIKA_LABS = "pika_labs"
    HAIPER = "haiper"
    LUMA_DREAM = "luma_dream"
    SYNTHETIC_MEDIA = "synthetic_media"
    LOCAL_DIFFUSION = "local_diffusion"

class VideoQuality(Enum):
    """Video quality levels"""
    DRAFT = "draft"      # Fast, lower quality
    STANDARD = "standard" # Balanced
    HIGH = "high"        # High quality
    PREMIUM = "premium"  # Maximum quality

class VideoStyle(Enum):
    """Video generation styles"""
    REALISTIC = "realistic"
    CINEMATIC = "cinematic"
    ANIME = "anime"
    CARTOON = "cartoon"
    ARTISTIC = "artistic"
    DOCUMENTARY = "documentary"
    COMMERCIAL = "commercial"
    MUSIC_VIDEO = "music_video"

@dataclass
class VideoGenerationConfig:
    """Enhanced video generation configuration"""
    provider: VideoProvider
    auth_provider: AuthProvider
    storage_provider: Optional[StorageProvider] = None
    quality: VideoQuality = VideoQuality.STANDARD
    max_retries: int = 3
    timeout: int = 300
    fallback_providers: List[VideoProvider] = field(default_factory=list)
    custom_config: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EnhancedVideoRequest:
    """Enhanced video generation request"""
    prompt: str
    duration: float
    style: Optional[VideoStyle] = None
    quality: Optional[VideoQuality] = None
    aspect_ratio: Optional[str] = "16:9"
    resolution: Optional[str] = "1920x1080"
    fps: Optional[int] = 30
    audio_prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    seed: Optional[int] = None
    camera_motion: Optional[str] = None
    lighting: Optional[str] = None
    color_grading: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class VideoAsset:
    """Represents a video asset"""
    url: str
    storage_key: Optional[str] = None
    duration: float = 0
    format: str = "mp4"
    resolution: Optional[str] = None
    fps: Optional[int] = None
    size_bytes: Optional[int] = None
    thumbnail_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EnhancedVideoResponse:
    """Enhanced video generation response"""
    success: bool
    video_asset: Optional[VideoAsset] = None
    job_id: Optional[str] = None
    provider_used: Optional[VideoProvider] = None
    generation_time: float = 0
    cost_estimate: float = 0
    error_message: Optional[str] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@runtime_checkable
class VideoGenerationCapabilities(Protocol):
    """Protocol defining video generation capabilities"""
    
    def supports_audio(self) -> bool:
        """Check if provider supports audio generation"""
        ...
    
    def supports_style(self, style: VideoStyle) -> bool:
        """Check if provider supports specific style"""
        ...
    
    def get_max_duration(self) -> float:
        """Get maximum supported video duration"""
        ...
    
    def get_supported_resolutions(self) -> List[str]:
        """Get list of supported resolutions"""
        ...

class VideoGenerationProvider(ABC):
    """Abstract video generation provider with full capabilities"""
    
    def __init__(self, config: VideoGenerationConfig):
        self.config = config
        self.auth_provider = config.auth_provider
        self.storage_provider = config.storage_provider
        self._credentials: Optional[Credentials] = None
    
    async def _ensure_authenticated(self) -> Credentials:
        """Ensure we have valid authentication"""
        self._credentials = await self.auth_provider.ensure_valid_credentials(self._credentials)
        return self._credentials
    
    @abstractmethod
    async def generate_video(self, request: EnhancedVideoRequest) -> EnhancedVideoResponse:
        """Generate video from request"""
        pass
    
    @abstractmethod
    async def check_job_status(self, job_id: str) -> EnhancedVideoResponse:
        """Check status of async generation job"""
        pass
    
    @abstractmethod
    def supports_audio(self) -> bool:
        """Check if provider supports audio generation"""
        pass
    
    @abstractmethod
    def supports_style(self, style: VideoStyle) -> bool:
        """Check if provider supports specific style"""
        pass
    
    @abstractmethod
    def get_max_duration(self) -> float:
        """Get maximum supported video duration"""
        pass
    
    @abstractmethod
    def get_supported_resolutions(self) -> List[str]:
        """Get list of supported resolutions"""
        pass
    
    @abstractmethod
    async def estimate_cost(self, request: EnhancedVideoRequest) -> float:
        """Estimate generation cost"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is currently available"""
        pass
    
    async def store_video(self, video_data: bytes, key: str) -> StorageObject:
        """Store generated video using configured storage provider"""
        if not self.storage_provider:
            raise ValueError("No storage provider configured")
        return await self.storage_provider.save(key, video_data, content_type="video/mp4")

class VideoGenerationOrchestrator:
    """Orchestrates video generation across multiple providers"""
    
    def __init__(self, providers: Dict[VideoProvider, VideoGenerationProvider]):
        self.providers = providers
        self.fallback_chain: List[VideoProvider] = []
    
    def set_fallback_chain(self, chain: List[VideoProvider]):
        """Set provider fallback chain"""
        self.fallback_chain = chain
    
    async def generate_with_fallback(self, request: EnhancedVideoRequest,
                                    preferred_provider: Optional[VideoProvider] = None) -> EnhancedVideoResponse:
        """Generate video with automatic fallback"""
        providers_to_try = []
        
        if preferred_provider and preferred_provider in self.providers:
            providers_to_try.append(preferred_provider)
        
        providers_to_try.extend([p for p in self.fallback_chain if p != preferred_provider])
        
        if not providers_to_try:
            providers_to_try = list(self.providers.keys())
        
        last_error = None
        for provider_enum in providers_to_try:
            provider = self.providers.get(provider_enum)
            if not provider or not provider.is_available():
                continue
            
            try:
                response = await provider.generate_video(request)
                if response.success:
                    response.provider_used = provider_enum
                    return response
            except Exception as e:
                last_error = e
                continue
        
        # All providers failed
        return EnhancedVideoResponse(
            success=False,
            error_message=f"All providers failed. Last error: {last_error}"
        )
    
    def get_best_provider_for_request(self, request: EnhancedVideoRequest) -> Optional[VideoProvider]:
        """Determine best provider for specific request"""
        for provider_enum, provider in self.providers.items():
            if not provider.is_available():
                continue
            
            # Check capabilities
            if request.audio_prompt and not provider.supports_audio():
                continue
            
            if request.style and not provider.supports_style(request.style):
                continue
            
            if request.duration > provider.get_max_duration():
                continue
            
            return provider_enum
        
        return None