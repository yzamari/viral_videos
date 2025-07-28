"""Series models for managing video series and episodes."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path
import json
import uuid


@dataclass
class Episode:
    """Represents a single episode in a series."""
    
    episode_number: int
    title: str
    description: str
    session_id: str
    video_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    duration: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.now)
    published: bool = False
    published_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def formatted_title(self) -> str:
        """Get formatted episode title."""
        return f"Episode {self.episode_number}: {self.title}"
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert episode to dictionary."""
        return {
            "episode_number": self.episode_number,
            "title": self.title,
            "description": self.description,
            "session_id": self.session_id,
            "video_path": self.video_path,
            "thumbnail_path": self.thumbnail_path,
            "duration": self.duration,
            "created_at": self.created_at.isoformat(),
            "published": self.published,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "metadata": self.metadata
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Episode":
        """Create episode from dictionary."""
        data = data.copy()
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data.get("published_at"):
            data["published_at"] = datetime.fromisoformat(data["published_at"])
        return cls(**data)


@dataclass
class Series:
    """Represents a video series with consistent theme and style."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    theme_id: str = ""
    character_id: Optional[str] = None
    voice_id: Optional[str] = None
    style_reference_id: Optional[str] = None
    
    # Series configuration
    default_duration: int = 64
    default_model: str = "veo-3"
    default_quality: str = "professional"
    
    # Branding
    series_logo_path: Optional[str] = None
    series_intro_path: Optional[str] = None
    series_outro_path: Optional[str] = None
    
    # Episodes
    episodes: List[Episode] = field(default_factory=list)
    next_episode_number: int = 1
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Publishing
    publish_schedule: Optional[str] = None  # cron expression
    auto_publish: bool = False
    social_platforms: List[str] = field(default_factory=list)
    
    def add_episode(
        self,
        title: str,
        description: str,
        session_id: str,
        **kwargs
    ) -> Episode:
        """Add a new episode to the series.
        
        Args:
            title: Episode title
            description: Episode description
            session_id: Session ID for the episode
            **kwargs: Additional episode attributes
            
        Returns:
            Created episode
        """
        episode = Episode(
            episode_number=self.next_episode_number,
            title=title,
            description=description,
            session_id=session_id,
            **kwargs
        )
        
        self.episodes.append(episode)
        self.next_episode_number += 1
        self.updated_at = datetime.now()
        
        return episode
        
    def get_episode(self, episode_number: int) -> Optional[Episode]:
        """Get episode by number.
        
        Args:
            episode_number: Episode number
            
        Returns:
            Episode or None if not found
        """
        for episode in self.episodes:
            if episode.episode_number == episode_number:
                return episode
        return None
        
    def get_latest_episode(self) -> Optional[Episode]:
        """Get the most recent episode.
        
        Returns:
            Latest episode or None if no episodes
        """
        if not self.episodes:
            return None
        return max(self.episodes, key=lambda e: e.created_at)
        
    def get_published_episodes(self) -> List[Episode]:
        """Get all published episodes.
        
        Returns:
            List of published episodes
        """
        return [e for e in self.episodes if e.published]
        
    def mark_episode_published(
        self,
        episode_number: int,
        video_path: str,
        thumbnail_path: Optional[str] = None
    ) -> bool:
        """Mark an episode as published.
        
        Args:
            episode_number: Episode number
            video_path: Path to published video
            thumbnail_path: Optional thumbnail path
            
        Returns:
            Success status
        """
        episode = self.get_episode(episode_number)
        if not episode:
            return False
            
        episode.published = True
        episode.published_at = datetime.now()
        episode.video_path = video_path
        if thumbnail_path:
            episode.thumbnail_path = thumbnail_path
            
        self.updated_at = datetime.now()
        return True
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert series to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "theme_id": self.theme_id,
            "character_id": self.character_id,
            "voice_id": self.voice_id,
            "style_reference_id": self.style_reference_id,
            "default_duration": self.default_duration,
            "default_model": self.default_model,
            "default_quality": self.default_quality,
            "series_logo_path": self.series_logo_path,
            "series_intro_path": self.series_intro_path,
            "series_outro_path": self.series_outro_path,
            "episodes": [e.to_dict() for e in self.episodes],
            "next_episode_number": self.next_episode_number,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
            "publish_schedule": self.publish_schedule,
            "auto_publish": self.auto_publish,
            "social_platforms": self.social_platforms
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Series":
        """Create series from dictionary."""
        data = data.copy()
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        data["episodes"] = [Episode.from_dict(e) for e in data.get("episodes", [])]
        return cls(**data)
        
    def save_to_file(self, filepath: Path) -> None:
        """Save series to JSON file.
        
        Args:
            filepath: Path to save file
        """
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
            
    @classmethod
    def load_from_file(cls, filepath: Path) -> Optional["Series"]:
        """Load series from JSON file.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            Series object or None if file doesn't exist
        """
        if not filepath.exists():
            return None
            
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        return cls.from_dict(data)


@dataclass
class SeriesTemplate:
    """Template for creating new series with predefined settings."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    category: str = ""  # news, documentary, tutorial, etc.
    
    # Default settings
    theme_id: str = ""
    default_duration: int = 64
    default_model: str = "veo-3"
    default_quality: str = "professional"
    
    # Episode structure
    episode_title_template: str = "{series_name} - Episode {episode_number}"
    episode_description_template: str = ""
    
    # Visual identity
    requires_character: bool = False
    requires_voice: bool = True
    style_notes: str = ""
    
    # Publishing
    suggested_schedule: str = ""  # e.g., "weekly", "daily"
    target_platforms: List[str] = field(default_factory=list)
    
    def create_series(self, series_name: str, **overrides) -> Series:
        """Create a new series from this template.
        
        Args:
            series_name: Name for the new series
            **overrides: Override default settings
            
        Returns:
            New series instance
        """
        series_data = {
            "name": series_name,
            "description": self.description,
            "theme_id": self.theme_id,
            "default_duration": self.default_duration,
            "default_model": self.default_model,
            "default_quality": self.default_quality,
            "metadata": {
                "template_id": self.id,
                "template_name": self.name,
                "category": self.category
            }
        }
        
        # Apply overrides
        series_data.update(overrides)
        
        return Series(**series_data)