"""
Session Entity - Core domain entity for session management
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

class SessionStatus(Enum):
    """Session status enumeration"""
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

@dataclass
class SessionEntity:
    """
    Core session entity representing a video generation session

    This entity encapsulates all the business logic and rules
    related to session management and lifecycle.
    """

    # Identity
    id: str

    # Core attributes
    name: str
    status: SessionStatus = SessionStatus.ACTIVE

    # Session paths
    base_path: str = ""
    video_clips_path: str = ""
    audio_path: str = ""
    images_path: str = ""
    scripts_path: str = ""
    metadata_path: str = ""
    final_output_path: str = ""
    logs_path: str = ""

    # Content tracking
    video_ids: List[str] = field(default_factory=list)
    total_videos: int = 0
    completed_videos: int = 0
    failed_videos: int = 0

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    # Configuration
    session_config: Dict[str, Any] = field(default_factory=dict)

    # Statistics
    total_processing_time: float = 0.0
    total_file_size_mb: float = 0.0

    def __post_init__(self):
        """Post-initialization validation"""
        if not self.id.strip():
            raise ValueError("Session ID cannot be empty")

        if not self.name.strip():
            raise ValueError("Session name cannot be empty")

        # Initialize paths if base_path is provided
        if self.base_path:
            self._initialize_paths()

    def _initialize_paths(self) -> None:
        """Initialize all session paths based on base path"""
        self.video_clips_path = f"{self.base_path}/video_clips"
        self.audio_path = f"{self.base_path}/audio"
        self.images_path = f"{self.base_path}/images"
        self.scripts_path = f"{self.base_path}/scripts"
        self.metadata_path = f"{self.base_path}/metadata"
        self.final_output_path = f"{self.base_path}/final_output"
        self.logs_path = f"{self.base_path}/logs"

    def set_base_path(self, base_path: str) -> None:
        """Set the base path for the session"""
        if not base_path.strip():
            raise ValueError("Base path cannot be empty")

        self.base_path = base_path
        self._initialize_paths()
        self.updated_at = datetime.now()

    def add_video(self, video_id: str) -> None:
        """Add a video to the session"""
        if not video_id.strip():
            raise ValueError("Video ID cannot be empty")

        if video_id not in self.video_ids:
            self.video_ids.append(video_id)
            self.total_videos += 1
            self.updated_at = datetime.now()

    def remove_video(self, video_id: str) -> None:
        """Remove a video from the session"""
        if video_id in self.video_ids:
            self.video_ids.remove(video_id)
            self.total_videos -= 1
            self.updated_at = datetime.now()

    def mark_video_completed(self, video_id: str) -> None:
        """Mark a video as completed"""
        if video_id not in self.video_ids:
            raise ValueError(f"Video {video_id} not found in session")

        self.completed_videos += 1
        self.updated_at = datetime.now()

        # Check if session should be completed
        if self.completed_videos >= self.total_videos and self.total_videos > 0:
            self.complete_session()

    def mark_video_failed(self, video_id: str) -> None:
        """Mark a video as failed"""
        if video_id not in self.video_ids:
            raise ValueError(f"Video {video_id} not found in session")

        self.failed_videos += 1
        self.updated_at = datetime.now()

    def complete_session(self) -> None:
        """Mark session as completed"""
        if self.status != SessionStatus.ACTIVE:
            raise ValueError(f"Cannot complete session from status: {self.status}")

        self.status = SessionStatus.COMPLETED
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()

    def complete(self) -> None:
        """Mark session as completed (alias for complete_session)"""
        self.complete_session()

    def update_status(self, new_status: SessionStatus) -> None:
        """Update session status"""
        if not isinstance(new_status, SessionStatus):
            raise ValueError("Status must be a SessionStatus enum value")

        self.status = new_status
        self.updated_at = datetime.now()

        if new_status == SessionStatus.COMPLETED:
            self.completed_at = datetime.now()

    def fail_session(self) -> None:
        """Mark session as failed"""
        if self.status not in [SessionStatus.ACTIVE]:
            raise ValueError(f"Cannot fail session from status: {self.status}")

        self.status = SessionStatus.FAILED
        self.updated_at = datetime.now()

    def cancel_session(self) -> None:
        """Cancel the session"""
        if self.status not in [SessionStatus.ACTIVE]:
            raise ValueError(f"Cannot cancel session from status: {self.status}")

        self.status = SessionStatus.CANCELLED
        self.updated_at = datetime.now()

    def update_processing_time(self, additional_time: float) -> None:
        """Update total processing time"""
        if additional_time < 0:
            raise ValueError("Processing time cannot be negative")

        self.total_processing_time += additional_time
        self.updated_at = datetime.now()

    def update_file_size(self, additional_size_mb: float) -> None:
        """Update total file size"""
        if additional_size_mb < 0:
            raise ValueError("File size cannot be negative")

        self.total_file_size_mb += additional_size_mb
        self.updated_at = datetime.now()

    def get_completion_rate(self) -> float:
        """Get session completion rate as percentage"""
        if self.total_videos == 0:
            return 0.0

        return (self.completed_videos / self.total_videos) * 100.0

    def get_failure_rate(self) -> float:
        """Get session failure rate as percentage"""
        if self.total_videos == 0:
            return 0.0

        return (self.failed_videos / self.total_videos) * 100.0

    def get_duration_minutes(self) -> float:
        """Get session duration in minutes"""
        if self.completed_at:
            duration = self.completed_at - self.created_at
        else:
            duration = datetime.now() - self.created_at

        return duration.total_seconds() / 60.0

    def is_active(self) -> bool:
        """Check if session is active"""
        return self.status == SessionStatus.ACTIVE

    def is_completed(self) -> bool:
        """Check if session is completed"""
        return self.status == SessionStatus.COMPLETED

    def is_failed(self) -> bool:
        """Check if session is failed"""
        return self.status == SessionStatus.FAILED

    def is_cancelled(self) -> bool:
        """Check if session is cancelled"""
        return self.status == SessionStatus.CANCELLED

    def can_add_videos(self) -> bool:
        """Check if videos can be added to session"""
        return self.status == SessionStatus.ACTIVE

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary for serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "base_path": self.base_path,
            "video_clips_path": self.video_clips_path,
            "audio_path": self.audio_path,
            "images_path": self.images_path,
            "scripts_path": self.scripts_path,
            "metadata_path": self.metadata_path,
            "final_output_path": self.final_output_path,
            "logs_path": self.logs_path,
            "video_ids": self.video_ids,
            "total_videos": self.total_videos,
            "completed_videos": self.completed_videos,
            "failed_videos": self.failed_videos,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "session_config": self.session_config,
            "total_processing_time": self.total_processing_time,
            "total_file_size_mb": self.total_file_size_mb
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionEntity":
        """Create entity from dictionary"""
        return cls(
            id=data["id"],
            name=data["name"],
            status=SessionStatus(data["status"]),
            base_path=data.get("base_path", ""),
            video_clips_path=data.get("video_clips_path", ""),
            audio_path=data.get("audio_path", ""),
            images_path=data.get("images_path", ""),
            scripts_path=data.get("scripts_path", ""),
            metadata_path=data.get("metadata_path", ""),
            final_output_path=data.get("final_output_path", ""),
            logs_path=data.get("logs_path", ""),
            video_ids=data.get("video_ids", []),
            total_videos=data.get("total_videos", 0),
            completed_videos=data.get("completed_videos", 0),
            failed_videos=data.get("failed_videos", 0),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            session_config=data.get("session_config", {}),
            total_processing_time=data.get("total_processing_time", 0.0),
            total_file_size_mb=data.get("total_file_size_mb", 0.0)
        )
