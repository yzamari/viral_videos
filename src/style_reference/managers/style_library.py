"""
Style Library Manager
Manages style templates - save, load, search, and organize styles
"""
import os
import json
import uuid
from typing import List, Optional, Dict
from datetime import datetime
import logging
from pathlib import Path

from ..models.style_reference import StyleReference
from ..models.style_attributes import ReferenceType

logger = logging.getLogger(__name__)


class StyleLibrary:
    """Manages a library of style templates"""
    
    def __init__(self, library_path: str = None):
        """Initialize style library
        
        Args:
            library_path: Path to style library directory
        """
        if library_path is None:
            # Default to user's home directory
            library_path = os.path.join(Path.home(), ".viralai", "style_library")
        
        self.library_path = Path(library_path)
        self.library_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.templates_dir = self.library_path / "templates"
        self.templates_dir.mkdir(exist_ok=True)
        
        self.metadata_file = self.library_path / "library_metadata.json"
        self._ensure_metadata()
        
        logger.info(f"📚 Style library initialized at: {self.library_path}")
    
    def save_style(self, style: StyleReference, template_name: str, 
                   tags: List[str] = None, description: str = None) -> str:
        """Save a style as a reusable template
        
        Args:
            style: Style reference to save
            template_name: Name for the template
            tags: Optional tags for categorization
            description: Optional description
            
        Returns:
            Template ID
        """
        # Generate template ID
        template_id = f"template_{uuid.uuid4().hex[:8]}"
        
        # Update style info
        style.template_id = template_id
        style.name = template_name
        style.tags = tags or []
        style.description = description
        style.reference_type = ReferenceType.TEMPLATE
        
        # Save template file
        template_path = self.templates_dir / f"{template_id}.json"
        self._save_style_to_file(style, template_path)
        
        # Update metadata
        self._update_metadata(template_id, template_name, tags, description)
        
        logger.info(f"✅ Saved style template: {template_name} ({template_id})")
        return template_id
    
    def load_style(self, template_id: str) -> Optional[StyleReference]:
        """Load a style template by ID
        
        Args:
            template_id: Template ID to load
            
        Returns:
            StyleReference or None if not found
        """
        template_path = self.templates_dir / f"{template_id}.json"
        
        if not template_path.exists():
            logger.warning(f"Template not found: {template_id}")
            return None
        
        return self._load_style_from_file(template_path)
    
    def load_style_by_name(self, template_name: str) -> Optional[StyleReference]:
        """Load a style template by name
        
        Args:
            template_name: Template name to load
            
        Returns:
            StyleReference or None if not found
        """
        metadata = self._load_metadata()
        
        for template_id, info in metadata.get("templates", {}).items():
            if info.get("name") == template_name:
                return self.load_style(template_id)
        
        logger.warning(f"Template not found by name: {template_name}")
        return None
    
    def search_styles(self, query: str = None, tags: List[str] = None) -> List[Dict[str, any]]:
        """Search for style templates
        
        Args:
            query: Search query for name/description
            tags: Tags to filter by
            
        Returns:
            List of template info dictionaries
        """
        metadata = self._load_metadata()
        templates = metadata.get("templates", {})
        
        results = []
        
        for template_id, info in templates.items():
            # Check query match
            if query:
                query_lower = query.lower()
                name_match = query_lower in info.get("name", "").lower()
                desc_match = query_lower in info.get("description", "").lower()
                if not (name_match or desc_match):
                    continue
            
            # Check tag match
            if tags:
                template_tags = info.get("tags", [])
                if not any(tag in template_tags for tag in tags):
                    continue
            
            results.append({
                "template_id": template_id,
                "name": info.get("name"),
                "description": info.get("description"),
                "tags": info.get("tags", []),
                "created_at": info.get("created_at"),
                "updated_at": info.get("updated_at")
            })
        
        return results
    
    def list_styles(self) -> List[Dict[str, any]]:
        """List all available style templates
        
        Returns:
            List of template info dictionaries
        """
        return self.search_styles()
    
    def delete_style(self, template_id: str) -> bool:
        """Delete a style template
        
        Args:
            template_id: Template ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        template_path = self.templates_dir / f"{template_id}.json"
        
        if not template_path.exists():
            return False
        
        # Delete file
        template_path.unlink()
        
        # Update metadata
        metadata = self._load_metadata()
        if "templates" in metadata and template_id in metadata["templates"]:
            del metadata["templates"][template_id]
            self._save_metadata(metadata)
        
        logger.info(f"🗑️ Deleted style template: {template_id}")
        return True
    
    def get_preset_styles(self) -> List[Dict[str, any]]:
        """Get list of preset style templates
        
        Returns:
            List of preset template info
        """
        presets = [
            {
                "name": "News Broadcast",
                "description": "Professional news channel style",
                "tags": ["news", "professional", "formal"],
                "template_id": "preset_news"
            },
            {
                "name": "Tech Review",
                "description": "Modern tech channel aesthetic",
                "tags": ["tech", "modern", "clean"],
                "template_id": "preset_tech"
            },
            {
                "name": "Vlog Style",
                "description": "Casual vlogging style",
                "tags": ["vlog", "casual", "personal"],
                "template_id": "preset_vlog"
            },
            {
                "name": "Cinematic",
                "description": "Film-like cinematic style",
                "tags": ["cinematic", "dramatic", "film"],
                "template_id": "preset_cinematic"
            },
            {
                "name": "Minimalist",
                "description": "Clean minimalist design",
                "tags": ["minimal", "clean", "simple"],
                "template_id": "preset_minimal"
            }
        ]
        
        return presets
    
    def _save_style_to_file(self, style: StyleReference, file_path: Path):
        """Save style to JSON file"""
        # Convert to dictionary
        style_dict = {
            "reference_id": style.reference_id,
            "name": style.name,
            "reference_type": style.reference_type.value,
            "source_path": style.source_path,
            "template_id": style.template_id,
            "color_palette": {
                "primary_color": style.color_palette.primary_color,
                "secondary_color": style.color_palette.secondary_color,
                "accent_color": style.color_palette.accent_color,
                "background_colors": style.color_palette.background_colors,
                "text_colors": style.color_palette.text_colors,
                "saturation_level": style.color_palette.saturation_level,
                "brightness_level": style.color_palette.brightness_level,
                "contrast_ratio": style.color_palette.contrast_ratio,
                "mood": style.color_palette.mood
            },
            "typography": {
                "primary_font_family": style.typography.primary_font_family,
                "secondary_font_family": style.typography.secondary_font_family,
                "title_size_ratio": style.typography.title_size_ratio,
                "body_size_ratio": style.typography.body_size_ratio,
                "font_weight": style.typography.font_weight,
                "letter_spacing": style.typography.letter_spacing,
                "line_height": style.typography.line_height,
                "has_shadow": style.typography.has_shadow,
                "has_outline": style.typography.has_outline,
                "text_animation_style": style.typography.text_animation_style
            },
            "composition": {
                "rule_of_thirds_adherence": style.composition.rule_of_thirds_adherence,
                "symmetry_score": style.composition.symmetry_score,
                "primary_layout": style.composition.primary_layout,
                "text_placement_zones": style.composition.text_placement_zones,
                "margin_ratio": style.composition.margin_ratio,
                "padding_ratio": style.composition.padding_ratio,
                "focal_point_strategy": style.composition.focal_point_strategy,
                "depth_layers": style.composition.depth_layers
            },
            "motion_style": {
                "camera_movement": style.motion_style.camera_movement,
                "transition_style": style.motion_style.transition_style,
                "average_shot_duration": style.motion_style.average_shot_duration,
                "movement_intensity": style.motion_style.movement_intensity,
                "text_animation_type": style.motion_style.text_animation_type,
                "element_animation_style": style.motion_style.element_animation_style,
                "pacing": style.motion_style.pacing,
                "rhythm_pattern": style.motion_style.rhythm_pattern
            },
            "visual_effects": [
                {
                    "effect_type": effect.effect_type,
                    "intensity": effect.intensity,
                    "apply_to": effect.apply_to,
                    "parameters": effect.parameters
                }
                for effect in style.visual_effects
            ],
            "technical_details": {
                "aspect_ratio": style.aspect_ratio,
                "resolution": style.resolution,
                "frame_rate": style.frame_rate
            },
            "metadata": {
                "created_at": style.created_at.isoformat(),
                "updated_at": style.updated_at.isoformat(),
                "tags": style.tags,
                "description": style.description,
                "confidence_scores": style.confidence_scores
            }
        }
        
        # Save to file
        with open(file_path, 'w') as f:
            json.dump(style_dict, f, indent=2)
    
    def _load_style_from_file(self, file_path: Path) -> StyleReference:
        """Load style from JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Reconstruct style objects
        from ..models.style_attributes import (
            ColorPalette, Typography, Composition, MotionStyle, VisualEffect
        )
        
        color_palette = ColorPalette(**data["color_palette"])
        typography = Typography(**data["typography"])
        composition = Composition(**data["composition"])
        motion_style = MotionStyle(**data["motion_style"])
        
        visual_effects = [
            VisualEffect(**effect_data)
            for effect_data in data["visual_effects"]
        ]
        
        # Create StyleReference
        style = StyleReference(
            reference_id=data["reference_id"],
            name=data["name"],
            reference_type=ReferenceType(data["reference_type"]),
            source_path=data["source_path"],
            template_id=data["template_id"],
            color_palette=color_palette,
            typography=typography,
            composition=composition,
            motion_style=motion_style,
            visual_effects=visual_effects,
            logo_placement=None,  # TODO: Save/load logo placement
            watermark=None,  # TODO: Save/load watermark
            lower_thirds=None,  # TODO: Save/load lower thirds
            aspect_ratio=data["technical_details"]["aspect_ratio"],
            resolution=data["technical_details"]["resolution"],
            frame_rate=data["technical_details"]["frame_rate"],
            created_at=datetime.fromisoformat(data["metadata"]["created_at"]),
            updated_at=datetime.fromisoformat(data["metadata"]["updated_at"]),
            tags=data["metadata"]["tags"],
            description=data["metadata"]["description"],
            confidence_scores=data["metadata"]["confidence_scores"]
        )
        
        return style
    
    def _ensure_metadata(self):
        """Ensure metadata file exists"""
        if not self.metadata_file.exists():
            metadata = {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "templates": {}
            }
            self._save_metadata(metadata)
    
    def _load_metadata(self) -> Dict:
        """Load library metadata"""
        with open(self.metadata_file, 'r') as f:
            return json.load(f)
    
    def _save_metadata(self, metadata: Dict):
        """Save library metadata"""
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _update_metadata(self, template_id: str, name: str, 
                        tags: List[str], description: str):
        """Update metadata for a template"""
        metadata = self._load_metadata()
        
        metadata["templates"][template_id] = {
            "name": name,
            "tags": tags or [],
            "description": description,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self._save_metadata(metadata)