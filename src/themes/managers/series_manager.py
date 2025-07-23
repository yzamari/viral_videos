"""Series Manager for handling video series operations."""

import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
import json
import shutil
from datetime import datetime

from ..models.series import Series, Episode, SeriesTemplate

logger = logging.getLogger(__name__)


class SeriesManager:
    """Manager for video series operations."""
    
    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize series manager.
        
        Args:
            base_dir: Base directory for series storage
        """
        self.base_dir = base_dir or Path.home() / ".viralai" / "series"
        self.series_dir = self.base_dir / "series"
        self.templates_dir = self.base_dir / "templates"
        
        # Create directories
        self.series_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize templates
        self._init_default_templates()
        
    def create_series(
        self,
        name: str,
        theme_id: str,
        description: str = "",
        template_id: Optional[str] = None,
        **kwargs
    ) -> Series:
        """Create a new video series.
        
        Args:
            name: Series name
            theme_id: Theme ID for the series
            description: Series description
            template_id: Optional template ID to use
            **kwargs: Additional series attributes
            
        Returns:
            Created series
        """
        if template_id:
            template = self.get_template(template_id)
            if template:
                series = template.create_series(
                    name,
                    theme_id=theme_id,
                    description=description or template.description,
                    **kwargs
                )
            else:
                logger.warning(f"Template not found: {template_id}")
                series = Series(name=name, theme_id=theme_id, description=description, **kwargs)
        else:
            series = Series(name=name, theme_id=theme_id, description=description, **kwargs)
            
        # Save series
        self.save_series(series)
        logger.info(f"Created series: {series.name} ({series.id})")
        
        return series
        
    def get_series(self, series_id: str) -> Optional[Series]:
        """Get series by ID.
        
        Args:
            series_id: Series ID
            
        Returns:
            Series or None if not found
        """
        series_file = self.series_dir / f"{series_id}.json"
        return Series.load_from_file(series_file)
        
    def get_series_by_name(self, name: str) -> Optional[Series]:
        """Get series by name.
        
        Args:
            name: Series name
            
        Returns:
            Series or None if not found
        """
        for series_file in self.series_dir.glob("*.json"):
            series = Series.load_from_file(series_file)
            if series and series.name == name:
                return series
        return None
        
    def list_series(self) -> List[Series]:
        """List all series.
        
        Returns:
            List of all series
        """
        series_list = []
        for series_file in self.series_dir.glob("*.json"):
            series = Series.load_from_file(series_file)
            if series:
                series_list.append(series)
                
        return sorted(series_list, key=lambda s: s.updated_at, reverse=True)
        
    def save_series(self, series: Series) -> None:
        """Save series to disk.
        
        Args:
            series: Series to save
        """
        series_file = self.series_dir / f"{series.id}.json"
        series.save_to_file(series_file)
        
    def delete_series(self, series_id: str) -> bool:
        """Delete a series.
        
        Args:
            series_id: Series ID
            
        Returns:
            Success status
        """
        series_file = self.series_dir / f"{series_id}.json"
        if series_file.exists():
            series_file.unlink()
            logger.info(f"Deleted series: {series_id}")
            return True
        return False
        
    def add_episode_to_series(
        self,
        series_id: str,
        title: str,
        description: str,
        session_id: str,
        **kwargs
    ) -> Optional[Episode]:
        """Add episode to series.
        
        Args:
            series_id: Series ID
            title: Episode title
            description: Episode description
            session_id: Session ID for the episode
            **kwargs: Additional episode attributes
            
        Returns:
            Created episode or None if series not found
        """
        series = self.get_series(series_id)
        if not series:
            logger.error(f"Series not found: {series_id}")
            return None
            
        episode = series.add_episode(title, description, session_id, **kwargs)
        self.save_series(series)
        
        logger.info(
            f"Added episode {episode.episode_number} to series: {series.name}"
        )
        
        return episode
        
    def update_episode(
        self,
        series_id: str,
        episode_number: int,
        **updates
    ) -> bool:
        """Update episode information.
        
        Args:
            series_id: Series ID
            episode_number: Episode number
            **updates: Fields to update
            
        Returns:
            Success status
        """
        series = self.get_series(series_id)
        if not series:
            return False
            
        episode = series.get_episode(episode_number)
        if not episode:
            return False
            
        # Update episode fields
        for key, value in updates.items():
            if hasattr(episode, key):
                setattr(episode, key, value)
                
        series.updated_at = datetime.now()
        self.save_series(series)
        
        return True
        
    def get_series_stats(self, series_id: str) -> Dict[str, Any]:
        """Get statistics for a series.
        
        Args:
            series_id: Series ID
            
        Returns:
            Series statistics
        """
        series = self.get_series(series_id)
        if not series:
            return {}
            
        total_duration = sum(
            e.duration for e in series.episodes if e.duration
        )
        
        return {
            "series_name": series.name,
            "total_episodes": len(series.episodes),
            "published_episodes": len(series.get_published_episodes()),
            "total_duration_seconds": total_duration,
            "total_duration_formatted": self._format_duration(total_duration),
            "created_at": series.created_at.isoformat(),
            "last_updated": series.updated_at.isoformat(),
            "last_episode": series.get_latest_episode().to_dict() if series.episodes else None
        }
        
    def export_series(self, series_id: str, export_path: Path) -> bool:
        """Export series configuration.
        
        Args:
            series_id: Series ID
            export_path: Path to export to
            
        Returns:
            Success status
        """
        series = self.get_series(series_id)
        if not series:
            return False
            
        export_data = {
            "series": series.to_dict(),
            "export_date": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        export_path.parent.mkdir(parents=True, exist_ok=True)
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2)
            
        logger.info(f"Exported series to: {export_path}")
        return True
        
    def import_series(self, import_path: Path) -> Optional[Series]:
        """Import series configuration.
        
        Args:
            import_path: Path to import from
            
        Returns:
            Imported series or None
        """
        try:
            with open(import_path, 'r') as f:
                data = json.load(f)
                
            series_data = data.get("series", {})
            series = Series.from_dict(series_data)
            
            # Generate new ID to avoid conflicts
            import uuid
            series.id = str(uuid.uuid4())
            
            self.save_series(series)
            logger.info(f"Imported series: {series.name}")
            
            return series
            
        except Exception as e:
            logger.error(f"Failed to import series: {e}")
            return None
            
    # Template Management
    
    def create_template(self, template: SeriesTemplate) -> None:
        """Create a series template.
        
        Args:
            template: Template to create
        """
        template_file = self.templates_dir / f"{template.id}.json"
        with open(template_file, 'w') as f:
            json.dump(template.__dict__, f, indent=2)
            
    def get_template(self, template_id: str) -> Optional[SeriesTemplate]:
        """Get template by ID.
        
        Args:
            template_id: Template ID
            
        Returns:
            Template or None
        """
        template_file = self.templates_dir / f"{template_id}.json"
        if not template_file.exists():
            return None
            
        with open(template_file, 'r') as f:
            data = json.load(f)
            
        return SeriesTemplate(**data)
        
    def list_templates(self) -> List[SeriesTemplate]:
        """List all templates.
        
        Returns:
            List of templates
        """
        templates = []
        for template_file in self.templates_dir.glob("*.json"):
            with open(template_file, 'r') as f:
                data = json.load(f)
            templates.append(SeriesTemplate(**data))
            
        return templates
        
    def _init_default_templates(self) -> None:
        """Initialize default series templates."""
        default_templates = [
            SeriesTemplate(
                id="news-daily",
                name="Daily News Show",
                description="Professional daily news broadcast",
                category="news",
                theme_id="news-edition",
                default_duration=180,
                episode_title_template="{series_name} - {date}",
                requires_character=True,
                requires_voice=True,
                suggested_schedule="daily",
                target_platforms=["youtube", "instagram", "tiktok"]
            ),
            SeriesTemplate(
                id="tech-weekly",
                name="Weekly Tech Review",
                description="Weekly technology news and reviews",
                category="technology",
                theme_id="tech-theme",
                default_duration=300,
                episode_title_template="Tech Weekly - Episode {episode_number}",
                requires_character=True,
                requires_voice=True,
                suggested_schedule="weekly",
                target_platforms=["youtube", "twitter"]
            ),
            SeriesTemplate(
                id="documentary",
                name="Documentary Series",
                description="In-depth documentary series",
                category="documentary",
                theme_id="entertainment",
                default_duration=600,
                episode_title_template="{series_name} - Part {episode_number}",
                requires_character=False,
                requires_voice=True,
                suggested_schedule="monthly",
                target_platforms=["youtube"]
            )
        ]
        
        for template in default_templates:
            template_file = self.templates_dir / f"{template.id}.json"
            if not template_file.exists():
                self.create_template(template)
                
    def _format_duration(self, seconds: float) -> str:
        """Format duration in seconds to readable string.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted duration string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"