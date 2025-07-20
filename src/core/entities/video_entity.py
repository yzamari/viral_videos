"""
Video Entity - Core domain entity for video generation
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

class VideoStatus(Enum):
    """Video generation status"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Platform(Enum):
    """Target platform for video optimization"""
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"

@dataclass
class VideoMetadata:
    """Video metadata information"""
    title: str
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    duration_seconds: int = 30
    resolution: str = "1080p"
    aspect_ratio: str = "16:9"
    frame_rate: int = 30

@dataclass
class VideoEntity:
    """
    Core video entity representing a video generation request

    This entity encapsulates all the business logic and rules
    related to video generation and management.
    """

    # Identity
    id: str
    session_id: str

    # Core attributes
    mission: str
    platform: Platform
    status: VideoStatus = VideoStatus.PENDING

    # Content attributes
    script_content: Optional[Dict[str, Any]] = None
    audio_files: List[str] = field(default_factory=list)
    video_clips: List[str] = field(default_factory=list)
    image_files: List[str] = field(default_factory=list)
    final_video_path: Optional[str] = None

    # Metadata
    metadata: VideoMetadata = field(default_factory=lambda: VideoMetadata(title=""))
    generation_config: Dict[str, Any] = field(default_factory=dict)

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    # Progress tracking
    progress_percentage: float = 0.0
    current_stage: str = "initialized"
    error_message: Optional[str] = None

    def __post_init__(self):
        """Post-initialization validation"""
        if not self.mission.strip():
            raise ValueError("Mission cannot be empty")

        if not self.id.strip():
            raise ValueError("Video ID cannot be empty")

        if not self.session_id.strip():
            raise ValueError("Session ID cannot be empty")

    def start_generation(self) -> None:
        """Start the video generation process"""
        if self.status != VideoStatus.PENDING:
            raise ValueError(f"Cannot start generation from status: {self.status}")

        self.status = VideoStatus.GENERATING
        self.current_stage = "script_generation"
        self.progress_percentage = 0.0
        self.updated_at = datetime.now()

    def update_progress(self, percentage: float, stage: str) -> None:
        """Update generation progress"""
        if not 0 <= percentage <= 100:
            raise ValueError("Progress percentage must be between 0 and 100")

        if self.status != VideoStatus.GENERATING:
            raise ValueError(f"Cannot update progress for status: {self.status}")

        self.progress_percentage = percentage
        self.current_stage = stage
        self.updated_at = datetime.now()

    def complete_generation(self, final_video_path: str) -> None:
        """Mark video generation as completed"""
        if self.status != VideoStatus.GENERATING:
            raise ValueError(f"Cannot complete from status: {self.status}")

        if not final_video_path.strip():
            raise ValueError("Final video path cannot be empty")

        self.status = VideoStatus.COMPLETED
        self.final_video_path = final_video_path
        self.progress_percentage = 100.0
        self.current_stage = "completed"
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()

    def fail_generation(self, error_message: str) -> None:
        """Mark video generation as failed"""
        if self.status not in [VideoStatus.GENERATING, VideoStatus.PENDING]:
            raise ValueError(f"Cannot fail from status: {self.status}")

        self.status = VideoStatus.FAILED
        self.error_message = error_message
        self.current_stage = "failed"
        self.updated_at = datetime.now()

    def cancel_generation(self) -> None:
        """Cancel video generation"""
        if self.status not in [VideoStatus.GENERATING, VideoStatus.PENDING]:
            raise ValueError(f"Cannot cancel from status: {self.status}")

        self.status = VideoStatus.CANCELLED
        self.current_stage = "cancelled"
        self.updated_at = datetime.now()

    def add_audio_file(self, file_path: str) -> None:
        """Add an audio file to the video"""
        if not file_path.strip():
            raise ValueError("Audio file path cannot be empty")

        if file_path not in self.audio_files:
            self.audio_files.append(file_path)
            self.updated_at = datetime.now()

    def add_video_clip(self, file_path: str) -> None:
        """Add a video clip to the video"""
        if not file_path.strip():
            raise ValueError("Video clip path cannot be empty")

        if file_path not in self.video_clips:
            self.video_clips.append(file_path)
            self.updated_at = datetime.now()

    def add_image_file(self, file_path: str) -> None:
        """Add an image file to the video"""
        if not file_path.strip():
            raise ValueError("Image file path cannot be empty")

        if file_path not in self.image_files:
            self.image_files.append(file_path)
            self.updated_at = datetime.now()

    def set_script_content(self, script: Dict[str, Any]) -> None:
        """Set the generated script content"""
        if not script:
            raise ValueError("Script content cannot be empty")

        self.script_content = script
        self.updated_at = datetime.now()

    def is_completed(self) -> bool:
        """Check if video generation is completed"""
        return self.status == VideoStatus.COMPLETED

    def is_failed(self) -> bool:
        """Check if video generation failed"""
        return self.status == VideoStatus.FAILED

    def is_in_progress(self) -> bool:
        """Check if video generation is in progress"""
        return self.status == VideoStatus.GENERATING

    def can_be_cancelled(self) -> bool:
        """Check if video generation can be cancelled"""
        return self.status in [VideoStatus.PENDING, VideoStatus.GENERATING]

    def get_duration_minutes(self) -> float:
        """Get video duration in minutes"""
        return self.metadata.duration_seconds / 60.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary for serialization"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "mission": self.mission,
            "platform": self.platform.value,
            "status": self.status.value,
            "script_content": self.script_content,
            "audio_files": self.audio_files,
            "video_clips": self.video_clips,
            "image_files": self.image_files,
            "final_video_path": self.final_video_path,
            "metadata": {
                "title": self.metadata.title,
                "description": self.metadata.description,
                "tags": self.metadata.tags,
                "duration_seconds": self.metadata.duration_seconds,
                "resolution": self.metadata.resolution,
                "aspect_ratio": self.metadata.aspect_ratio,
                "frame_rate": self.metadata.frame_rate
            },
            "generation_config": self.generation_config,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "progress_percentage": self.progress_percentage,
            "current_stage": self.current_stage,
            "error_message": self.error_message
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VideoEntity":
        """Create entity from dictionary"""
        metadata = VideoMetadata(
            title=data["metadata"]["title"],
            description=data["metadata"].get("description"),
            tags=data["metadata"].get("tags", []),
            duration_seconds=data["metadata"].get("duration_seconds", 30),
            resolution=data["metadata"].get("resolution", "1080p"),
            aspect_ratio=data["metadata"].get("aspect_ratio", "16:9"),
            frame_rate=data["metadata"].get("frame_rate", 30)
        )

        return cls(
            id=data["id"],
            session_id=data["session_id"],
            mission=data["mission"],
            platform=Platform(data["platform"]),
            status=VideoStatus(data["status"]),
            script_content=data.get("script_content"),
            audio_files=data.get("audio_files", []),
            video_clips=data.get("video_clips", []),
            image_files=data.get("image_files", []),
            final_video_path=data.get("final_video_path"),
            metadata=metadata,
            generation_config=data.get("generation_config", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            progress_percentage=data.get("progress_percentage", 0.0),
            current_stage=data.get("current_stage", "initialized"),
            error_message=data.get("error_message")
        )
