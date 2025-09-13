"""
Video Session Entity - Enhanced domain entity for video generation sessions.

This entity builds upon the existing SessionEntity to provide video-specific business logic.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from src.core.entities.session_entity import SessionEntity, SessionStatus


class VideoSessionStatus(Enum):
    """Extended video session status with more granular states"""
    CREATED = "created"
    QUEUED = "queued"
    GENERATING = "generating"
    POST_PROCESSING = "post_processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


@dataclass
class VideoGenerationConfig:
    """
    Video generation configuration with validation and business rules.
    
    Encapsulates all video generation parameters and their constraints.
    """
    
    # Core generation parameters
    mission: str
    category: Optional[str] = None
    platform: str = 'youtube'
    duration: int = 20
    
    # Generation options
    image_only: bool = False
    fallback_only: bool = False
    force_generation: bool = False
    skip_auth_test: bool = False
    
    # AI and discussion settings
    discussion_mode: str = 'enhanced'
    show_discussion_logs: bool = True
    
    # Style and presentation
    style: Optional[str] = None
    visual_style: Optional[str] = None
    language: str = 'english'
    voice_preference: Optional[str] = None
    
    # Advanced options
    use_premium_models: bool = False
    enable_subtitles: bool = True
    background_music: bool = True
    
    def __post_init__(self):
        """Validate configuration parameters"""
        self._validate_core_parameters()
        self._validate_duration()
        self._validate_platform()
        self._apply_platform_constraints()
    
    def _validate_core_parameters(self) -> None:
        """Validate core generation parameters"""
        if not self.mission or not self.mission.strip():
            raise ValueError("Mission cannot be empty")
            
        if len(self.mission) < 10:
            raise ValueError("Mission must be at least 10 characters long")
            
        if len(self.mission) > 1000:
            raise ValueError("Mission cannot exceed 1000 characters")
    
    def _validate_duration(self) -> None:
        """Validate video duration constraints"""
        if self.duration < 5:
            raise ValueError("Video duration must be at least 5 seconds")
            
        if self.duration > 300:  # 5 minutes
            raise ValueError("Video duration cannot exceed 300 seconds")
    
    def _validate_platform(self) -> None:
        """Validate platform-specific constraints"""
        valid_platforms = ['youtube', 'tiktok', 'instagram', 'facebook', 'twitter']
        if self.platform not in valid_platforms:
            raise ValueError(f"Platform must be one of: {', '.join(valid_platforms)}")
    
    def _apply_platform_constraints(self) -> None:
        """Apply platform-specific constraints and adjustments"""
        platform_constraints = {
            'tiktok': {'max_duration': 60, 'aspect_ratio': '9:16'},
            'instagram': {'max_duration': 90, 'aspect_ratio': '9:16'},
            'youtube': {'max_duration': 300, 'aspect_ratio': '16:9'},
            'facebook': {'max_duration': 240, 'aspect_ratio': '16:9'},
            'twitter': {'max_duration': 140, 'aspect_ratio': '16:9'}
        }
        
        constraints = platform_constraints.get(self.platform, {})
        max_duration = constraints.get('max_duration')
        
        if max_duration and self.duration > max_duration:
            self.duration = max_duration
    
    def get_estimated_generation_time(self) -> int:
        """Estimate generation time in seconds based on configuration"""
        base_time = 60  # Base 1 minute
        
        # Duration multiplier
        duration_multiplier = self.duration / 20.0  # Normalized to 20 seconds
        
        # Mode multipliers
        mode_multipliers = {
            'simple': 1.0,
            'enhanced': 2.0,
            'professional': 3.0
        }
        
        mode_multiplier = mode_multipliers.get(self.discussion_mode, 1.5)
        
        # Options that increase generation time
        if self.use_premium_models:
            mode_multiplier *= 1.5
        if not self.fallback_only:
            mode_multiplier *= 1.3
        if self.enable_subtitles:
            mode_multiplier *= 1.1
        
        return int(base_time * duration_multiplier * mode_multiplier)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "mission": self.mission,
            "category": self.category,
            "platform": self.platform,
            "duration": self.duration,
            "image_only": self.image_only,
            "fallback_only": self.fallback_only,
            "force_generation": self.force_generation,
            "skip_auth_test": self.skip_auth_test,
            "discussion_mode": self.discussion_mode,
            "show_discussion_logs": self.show_discussion_logs,
            "style": self.style,
            "visual_style": self.visual_style,
            "language": self.language,
            "voice_preference": self.voice_preference,
            "use_premium_models": self.use_premium_models,
            "enable_subtitles": self.enable_subtitles,
            "background_music": self.background_music
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VideoGenerationConfig":
        """Create from dictionary"""
        return cls(**data)


@dataclass
class VideoSession:
    """
    Video Session domain entity with enhanced business logic.
    
    This entity extends the core SessionEntity with video-specific functionality
    while maintaining proper separation of concerns.
    """
    
    # Core session data (delegates to SessionEntity)
    _session_entity: SessionEntity
    
    # Video-specific data
    user_id: str
    config: VideoGenerationConfig
    status: VideoSessionStatus = VideoSessionStatus.CREATED
    
    # Generation tracking
    current_phase: str = "Initialization"
    progress_percentage: float = 0.0
    estimated_completion_time: Optional[datetime] = None
    
    # Quality metrics
    generation_quality_score: Optional[float] = None
    user_satisfaction_rating: Optional[int] = None  # 1-5 stars
    
    # Resource usage
    compute_time_seconds: float = 0.0
    storage_used_mb: float = 0.0
    ai_tokens_used: int = 0
    
    # Output tracking
    output_video_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    metadata_path: Optional[str] = None
    
    def __post_init__(self):
        """Post-initialization setup"""
        if not self.user_id or not self.user_id.strip():
            raise ValueError("User ID cannot be empty")
            
        # Estimate completion time
        estimated_seconds = self.config.get_estimated_generation_time()
        self.estimated_completion_time = datetime.now().replace(
            second=datetime.now().second + estimated_seconds
        )
    
    @classmethod
    def create_new_session(cls, 
                          session_id: str,
                          user_id: str, 
                          config: VideoGenerationConfig,
                          session_name: Optional[str] = None) -> "VideoSession":
        """
        Factory method to create a new video session.
        
        Encapsulates session creation logic with proper validation.
        """
        if not session_name:
            session_name = f"Video: {config.mission[:50]}..."
            
        session_entity = SessionEntity(
            id=session_id,
            name=session_name,
            session_config=config.to_dict()
        )
        
        return cls(
            _session_entity=session_entity,
            user_id=user_id,
            config=config
        )
    
    @property
    def id(self) -> str:
        """Get session ID from underlying entity"""
        return self._session_entity.id
    
    @property
    def name(self) -> str:
        """Get session name from underlying entity"""
        return self._session_entity.name
    
    @property
    def created_at(self) -> datetime:
        """Get creation timestamp"""
        return self._session_entity.created_at
    
    @property
    def updated_at(self) -> datetime:
        """Get last update timestamp"""
        return self._session_entity.updated_at
    
    def start_generation(self) -> None:
        """Start video generation process"""
        if self.status != VideoSessionStatus.CREATED:
            raise ValueError(f"Cannot start generation from status: {self.status.value}")
            
        self.status = VideoSessionStatus.QUEUED
        self.current_phase = "Queued for generation"
        self._update_timestamps()
    
    def begin_processing(self) -> None:
        """Begin actual video processing"""
        if self.status != VideoSessionStatus.QUEUED:
            raise ValueError(f"Cannot begin processing from status: {self.status.value}")
            
        self.status = VideoSessionStatus.GENERATING
        self.current_phase = "AI Discussion & Planning"
        self.progress_percentage = 10.0
        self._update_timestamps()
    
    def update_progress(self, phase: str, percentage: float, message: Optional[str] = None) -> None:
        """Update generation progress"""
        if not 0 <= percentage <= 100:
            raise ValueError("Progress percentage must be between 0 and 100")
            
        self.current_phase = phase
        self.progress_percentage = percentage
        
        # Update status based on progress
        if percentage >= 90:
            self.status = VideoSessionStatus.POST_PROCESSING
        elif self.status == VideoSessionStatus.CREATED:
            self.status = VideoSessionStatus.GENERATING
            
        self._update_timestamps()
    
    def complete_successfully(self, 
                            output_video_path: str,
                            thumbnail_path: Optional[str] = None,
                            metadata_path: Optional[str] = None) -> None:
        """Mark session as successfully completed"""
        if not output_video_path or not output_video_path.strip():
            raise ValueError("Output video path cannot be empty")
            
        self.status = VideoSessionStatus.COMPLETED
        self.current_phase = "Completed"
        self.progress_percentage = 100.0
        self.output_video_path = output_video_path
        self.thumbnail_path = thumbnail_path
        self.metadata_path = metadata_path
        
        # Update underlying session entity
        self._session_entity.complete_session()
        self._update_timestamps()
    
    def fail_with_error(self, error_message: str) -> None:
        """Mark session as failed with error details"""
        self.status = VideoSessionStatus.FAILED
        self.current_phase = f"Failed: {error_message}"
        
        # Store error in session config for debugging
        self._session_entity.session_config["error"] = {
            "message": error_message,
            "timestamp": datetime.now().isoformat(),
            "phase": self.current_phase
        }
        
        self._session_entity.fail_session()
        self._update_timestamps()
    
    def cancel_session(self) -> None:
        """Cancel the video generation session"""
        if self.status in [VideoSessionStatus.COMPLETED, VideoSessionStatus.FAILED]:
            raise ValueError(f"Cannot cancel session in {self.status.value} status")
            
        self.status = VideoSessionStatus.CANCELLED
        self.current_phase = "Cancelled by user"
        self._session_entity.cancel_session()
        self._update_timestamps()
    
    def pause_session(self) -> None:
        """Pause the video generation session"""
        if self.status not in [VideoSessionStatus.QUEUED, VideoSessionStatus.GENERATING]:
            raise ValueError(f"Cannot pause session in {self.status.value} status")
            
        self.status = VideoSessionStatus.PAUSED
        self.current_phase = "Paused"
        self._update_timestamps()
    
    def resume_session(self) -> None:
        """Resume paused session"""
        if self.status != VideoSessionStatus.PAUSED:
            raise ValueError("Can only resume paused sessions")
            
        self.status = VideoSessionStatus.GENERATING
        self.current_phase = "Resumed generation"
        self._update_timestamps()
    
    def record_resource_usage(self, 
                            compute_seconds: float = 0,
                            storage_mb: float = 0,
                            ai_tokens: int = 0) -> None:
        """Record resource usage for billing/analytics"""
        if compute_seconds > 0:
            self.compute_time_seconds += compute_seconds
            
        if storage_mb > 0:
            self.storage_used_mb += storage_mb
            
        if ai_tokens > 0:
            self.ai_tokens_used += ai_tokens
            
        self._update_timestamps()
    
    def set_quality_metrics(self, 
                          quality_score: Optional[float] = None,
                          user_rating: Optional[int] = None) -> None:
        """Set quality metrics for analytics"""
        if quality_score is not None:
            if not 0 <= quality_score <= 1:
                raise ValueError("Quality score must be between 0 and 1")
            self.generation_quality_score = quality_score
            
        if user_rating is not None:
            if not 1 <= user_rating <= 5:
                raise ValueError("User rating must be between 1 and 5")
            self.user_satisfaction_rating = user_rating
            
        self._update_timestamps()
    
    def _update_timestamps(self) -> None:
        """Update timestamps on both this entity and the underlying session"""
        now = datetime.now()
        self._session_entity.updated_at = now
    
    def is_active(self) -> bool:
        """Check if session is actively processing"""
        return self.status in [VideoSessionStatus.QUEUED, VideoSessionStatus.GENERATING]
    
    def is_completed(self) -> bool:
        """Check if session is completed"""
        return self.status == VideoSessionStatus.COMPLETED
    
    def is_failed(self) -> bool:
        """Check if session failed"""
        return self.status == VideoSessionStatus.FAILED
    
    def can_be_cancelled(self) -> bool:
        """Check if session can be cancelled"""
        return self.status in [VideoSessionStatus.CREATED, VideoSessionStatus.QUEUED, 
                              VideoSessionStatus.GENERATING, VideoSessionStatus.PAUSED]
    
    def get_estimated_time_remaining(self) -> Optional[int]:
        """Get estimated time remaining in seconds"""
        if not self.estimated_completion_time or self.is_completed():
            return None
            
        remaining = self.estimated_completion_time - datetime.now()
        return max(0, int(remaining.total_seconds()))
    
    def to_dict(self, include_entity: bool = True) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "config": self.config.to_dict(),
            "status": self.status.value,
            "current_phase": self.current_phase,
            "progress_percentage": self.progress_percentage,
            "estimated_completion_time": self.estimated_completion_time.isoformat() if self.estimated_completion_time else None,
            "generation_quality_score": self.generation_quality_score,
            "user_satisfaction_rating": self.user_satisfaction_rating,
            "compute_time_seconds": self.compute_time_seconds,
            "storage_used_mb": self.storage_used_mb,
            "ai_tokens_used": self.ai_tokens_used,
            "output_video_path": self.output_video_path,
            "thumbnail_path": self.thumbnail_path,
            "metadata_path": self.metadata_path
        }
        
        if include_entity:
            data["session_entity"] = self._session_entity.to_dict()
            
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VideoSession":
        """Create from dictionary"""
        session_entity_data = data.get("session_entity", {})
        session_entity = SessionEntity.from_dict(session_entity_data) if session_entity_data else None
        
        if not session_entity:
            # Create minimal session entity if not provided
            session_entity = SessionEntity(
                id=data["id"],
                name=f"Video Session {data['id'][:8]}",
                session_config=data["config"]
            )
        
        return cls(
            _session_entity=session_entity,
            user_id=data["user_id"],
            config=VideoGenerationConfig.from_dict(data["config"]),
            status=VideoSessionStatus(data["status"]),
            current_phase=data.get("current_phase", "Initialization"),
            progress_percentage=data.get("progress_percentage", 0.0),
            estimated_completion_time=datetime.fromisoformat(data["estimated_completion_time"]) if data.get("estimated_completion_time") else None,
            generation_quality_score=data.get("generation_quality_score"),
            user_satisfaction_rating=data.get("user_satisfaction_rating"),
            compute_time_seconds=data.get("compute_time_seconds", 0.0),
            storage_used_mb=data.get("storage_used_mb", 0.0),
            ai_tokens_used=data.get("ai_tokens_used", 0),
            output_video_path=data.get("output_video_path"),
            thumbnail_path=data.get("thumbnail_path"),
            metadata_path=data.get("metadata_path")
        )