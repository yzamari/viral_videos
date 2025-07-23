"""
Theme Manager
Handles loading, saving, and managing themes
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import shutil

from ..models.theme import Theme, ThemeCategory
from ..presets.news_edition import NewsEditionTheme
from ..presets.sports_theme import SportsTheme
from ..presets.tech_theme import TechTheme
from ..presets.entertainment_theme import EntertainmentTheme
from ..presets.iran_international_news import IranInternationalNewsTheme
from ...utils.logging_config import get_logger

logger = get_logger(__name__)


class ThemeManager:
    """Manages theme storage and retrieval"""
    
    def __init__(self, themes_directory: str = "themes"):
        """
        Initialize theme manager
        
        Args:
            themes_directory: Directory to store custom themes
        """
        self.themes_dir = Path(themes_directory)
        self.themes_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.custom_themes_dir = self.themes_dir / "custom"
        self.custom_themes_dir.mkdir(exist_ok=True)
        
        # Metadata file for theme registry
        self.metadata_file = self.themes_dir / "themes_metadata.json"
        
        # Initialize metadata if not exists
        if not self.metadata_file.exists():
            self._init_metadata()
        
        # Load preset themes
        self.preset_themes = self._load_preset_themes()
    
    def _init_metadata(self):
        """Initialize metadata file"""
        metadata = {
            "version": "1.0.0",
            "themes": {},
            "categories": {cat.value: [] for cat in ThemeCategory},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        self._save_metadata(metadata)
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load metadata from file"""
        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
            self._init_metadata()
            return self._load_metadata()
    
    def _save_metadata(self, metadata: Dict[str, Any]):
        """Save metadata to file"""
        metadata["updated_at"] = datetime.now().isoformat()
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _load_preset_themes(self) -> Dict[str, Theme]:
        """Load all preset themes"""
        presets = {
            "preset_news_edition": NewsEditionTheme(),
            "preset_sports": SportsTheme(),
            "preset_tech": TechTheme(),
            "preset_entertainment": EntertainmentTheme(),
            "preset_iran_international_news": IranInternationalNewsTheme()
        }
        
        logger.info(f"Loaded {len(presets)} preset themes")
        return presets
    
    def save_theme(self, theme: Theme, overwrite: bool = False) -> str:
        """
        Save a custom theme
        
        Args:
            theme: Theme to save
            overwrite: Whether to overwrite if exists
            
        Returns:
            Theme ID
        """
        # Check if theme already exists
        theme_file = self.custom_themes_dir / f"{theme.theme_id}.json"
        if theme_file.exists() and not overwrite:
            raise ValueError(f"Theme {theme.theme_id} already exists")
        
        # Save theme data
        theme_data = theme.to_dict()
        
        # Save associated files if they exist
        if theme.brand_kit:
            theme_data["brand_kit"] = self._save_brand_assets(theme)
        
        # Write theme file
        with open(theme_file, 'w') as f:
            json.dump(theme_data, f, indent=2)
        
        # Update metadata
        metadata = self._load_metadata()
        metadata["themes"][theme.theme_id] = {
            "name": theme.name,
            "category": theme.category.value,
            "version": theme.version,
            "description": theme.description,
            "tags": theme.tags,
            "created_at": theme.created_at.isoformat(),
            "updated_at": theme.updated_at.isoformat(),
            "created_by": theme.created_by,
            "file_path": str(theme_file)
        }
        
        # Update category index
        if theme.theme_id not in metadata["categories"][theme.category.value]:
            metadata["categories"][theme.category.value].append(theme.theme_id)
        
        self._save_metadata(metadata)
        
        logger.info(f"Saved theme: {theme.name} ({theme.theme_id})")
        return theme.theme_id
    
    def _save_brand_assets(self, theme: Theme) -> Dict[str, Any]:
        """Save brand assets and return updated paths"""
        if not theme.brand_kit:
            return {}
        
        # Create assets directory for this theme
        assets_dir = self.custom_themes_dir / theme.theme_id / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)
        
        brand_data = theme.brand_kit.__dict__.copy()
        
        # Copy logo files if they exist
        logo_fields = ["primary_logo", "primary_logo_dark", "primary_logo_light", "secondary_logo"]
        for field in logo_fields:
            logo_path = getattr(theme.brand_kit, field, None)
            if logo_path and os.path.exists(logo_path):
                # Copy to theme assets
                filename = os.path.basename(logo_path)
                new_path = assets_dir / filename
                shutil.copy2(logo_path, new_path)
                brand_data[field] = str(new_path)
        
        return brand_data
    
    def load_theme(self, theme_id: str) -> Optional[Theme]:
        """
        Load a theme by ID
        
        Args:
            theme_id: Theme ID to load
            
        Returns:
            Theme object or None if not found
        """
        # Check presets first
        if theme_id in self.preset_themes:
            return self.preset_themes[theme_id]
        
        # Load from custom themes
        theme_file = self.custom_themes_dir / f"{theme_id}.json"
        if not theme_file.exists():
            logger.warning(f"Theme not found: {theme_id}")
            return None
        
        try:
            with open(theme_file, 'r') as f:
                theme_data = json.load(f)
            
            # Reconstruct theme object
            theme = self._reconstruct_theme(theme_data)
            return theme
            
        except Exception as e:
            logger.error(f"Error loading theme {theme_id}: {e}")
            return None
    
    def _reconstruct_theme(self, theme_data: Dict[str, Any]) -> Theme:
        """Reconstruct theme object from saved data"""
        # This would need proper deserialization logic
        # For now, returning a basic theme
        # In production, this would properly reconstruct all nested objects
        from ..models.theme import ThemeCategory, TransitionStyle
        
        theme = Theme(
            theme_id=theme_data["theme_id"],
            name=theme_data["name"],
            category=ThemeCategory(theme_data["category"]),
            version=theme_data["version"],
            # ... reconstruct other fields
        )
        
        return theme
    
    def load_theme_by_name(self, name: str) -> Optional[Theme]:
        """Load theme by name"""
        # Check presets
        for theme in self.preset_themes.values():
            if theme.name.lower() == name.lower():
                return theme
        
        # Check custom themes
        metadata = self._load_metadata()
        for theme_id, theme_info in metadata["themes"].items():
            if theme_info["name"].lower() == name.lower():
                return self.load_theme(theme_id)
        
        return None
    
    def list_themes(self, category: Optional[ThemeCategory] = None) -> List[Dict[str, Any]]:
        """
        List all available themes
        
        Args:
            category: Filter by category (optional)
            
        Returns:
            List of theme info dictionaries
        """
        themes = []
        
        # Add presets
        for theme_id, theme in self.preset_themes.items():
            if category and theme.category != category:
                continue
            
            themes.append({
                "theme_id": theme_id,
                "name": theme.name,
                "category": theme.category.value,
                "description": theme.description,
                "tags": theme.tags,
                "is_preset": True,
                "version": theme.version
            })
        
        # Add custom themes
        metadata = self._load_metadata()
        for theme_id, theme_info in metadata["themes"].items():
            if category and theme_info["category"] != category.value:
                continue
            
            themes.append({
                "theme_id": theme_id,
                "name": theme_info["name"],
                "category": theme_info["category"],
                "description": theme_info.get("description"),
                "tags": theme_info.get("tags", []),
                "is_preset": False,
                "version": theme_info.get("version", "1.0.0")
            })
        
        return sorted(themes, key=lambda x: x["name"])
    
    def search_themes(self, query: str) -> List[Dict[str, Any]]:
        """Search themes by name, description, or tags"""
        query_lower = query.lower()
        results = []
        
        all_themes = self.list_themes()
        for theme_info in all_themes:
            # Search in name
            if query_lower in theme_info["name"].lower():
                results.append(theme_info)
                continue
            
            # Search in description
            if theme_info.get("description") and query_lower in theme_info["description"].lower():
                results.append(theme_info)
                continue
            
            # Search in tags
            if any(query_lower in tag.lower() for tag in theme_info.get("tags", [])):
                results.append(theme_info)
        
        return results
    
    def delete_theme(self, theme_id: str) -> bool:
        """
        Delete a custom theme
        
        Args:
            theme_id: Theme ID to delete
            
        Returns:
            True if deleted successfully
        """
        # Can't delete presets
        if theme_id in self.preset_themes:
            logger.warning(f"Cannot delete preset theme: {theme_id}")
            return False
        
        # Delete theme file and assets
        theme_file = self.custom_themes_dir / f"{theme_id}.json"
        theme_assets = self.custom_themes_dir / theme_id
        
        if not theme_file.exists():
            logger.warning(f"Theme not found: {theme_id}")
            return False
        
        try:
            # Remove files
            theme_file.unlink()
            if theme_assets.exists():
                shutil.rmtree(theme_assets)
            
            # Update metadata
            metadata = self._load_metadata()
            if theme_id in metadata["themes"]:
                theme_info = metadata["themes"][theme_id]
                category = theme_info["category"]
                
                # Remove from themes
                del metadata["themes"][theme_id]
                
                # Remove from category index
                if theme_id in metadata["categories"][category]:
                    metadata["categories"][category].remove(theme_id)
                
                self._save_metadata(metadata)
            
            logger.info(f"Deleted theme: {theme_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting theme {theme_id}: {e}")
            return False
    
    def duplicate_theme(self, theme_id: str, new_name: str) -> Optional[str]:
        """
        Duplicate an existing theme
        
        Args:
            theme_id: Theme to duplicate
            new_name: Name for the new theme
            
        Returns:
            New theme ID or None if failed
        """
        # Load original theme
        original = self.load_theme(theme_id)
        if not original:
            return None
        
        # Create new theme with new ID
        import uuid
        new_theme = Theme(
            theme_id=f"theme_{uuid.uuid4().hex[:8]}",
            name=new_name,
            category=original.category,
            version="1.0.0",
            style_reference=original.style_reference,
            brand_kit=original.brand_kit,
            intro_template=original.intro_template,
            outro_template=original.outro_template,
            transition_style=original.transition_style,
            transition_duration=original.transition_duration,
            logo_config=original.logo_config,
            lower_thirds_style=original.lower_thirds_style,
            caption_style=original.caption_style,
            intro_music=original.intro_music,
            outro_music=original.outro_music,
            background_music_style=original.background_music_style,
            sound_effects_pack=original.sound_effects_pack,
            content_tone=original.content_tone,
            content_style=original.content_style,
            target_audience=original.target_audience,
            default_duration=original.default_duration,
            default_aspect_ratio=original.default_aspect_ratio,
            default_resolution=original.default_resolution,
            default_frame_rate=original.default_frame_rate,
            description=f"Duplicated from {original.name}",
            tags=original.tags + ["duplicated"],
            parent_theme_id=theme_id
        )
        
        # Save new theme
        try:
            new_id = self.save_theme(new_theme)
            logger.info(f"Duplicated theme {theme_id} as {new_id}")
            return new_id
        except Exception as e:
            logger.error(f"Error duplicating theme: {e}")
            return None
    
    def export_theme(self, theme_id: str, output_path: str) -> bool:
        """
        Export theme to a file for sharing
        
        Args:
            theme_id: Theme to export
            output_path: Path to save exported theme
            
        Returns:
            True if exported successfully
        """
        theme = self.load_theme(theme_id)
        if not theme:
            return False
        
        try:
            # Create export package
            export_data = {
                "version": "1.0.0",
                "exported_at": datetime.now().isoformat(),
                "theme": theme.to_dict()
            }
            
            # Save to file
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Exported theme {theme_id} to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting theme: {e}")
            return False
    
    def import_theme(self, import_path: str, new_name: Optional[str] = None) -> Optional[str]:
        """
        Import theme from exported file
        
        Args:
            import_path: Path to theme file
            new_name: Optional new name for imported theme
            
        Returns:
            Imported theme ID or None if failed
        """
        try:
            with open(import_path, 'r') as f:
                import_data = json.load(f)
            
            theme_data = import_data["theme"]
            
            # Generate new ID
            import uuid
            theme_data["theme_id"] = f"theme_{uuid.uuid4().hex[:8]}"
            
            if new_name:
                theme_data["name"] = new_name
            
            # Reconstruct and save theme
            theme = self._reconstruct_theme(theme_data)
            theme_id = self.save_theme(theme)
            
            logger.info(f"Imported theme from {import_path} as {theme_id}")
            return theme_id
            
        except Exception as e:
            logger.error(f"Error importing theme: {e}")
            return None