"""
Theme Models
Core models for the theme system
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum
import uuid

from ...style_reference.models.style_reference import StyleReference


class ThemeCategory(Enum):
    """Theme categories"""
    NEWS = "news"
    SPORTS = "sports"
    TECH = "tech"
    ENTERTAINMENT = "entertainment"
    EDUCATION = "education"
    BUSINESS = "business"
    LIFESTYLE = "lifestyle"
    CUSTOM = "custom"


class TransitionStyle(Enum):
    """Video transition styles"""
    CUT = "cut"
    FADE = "fade"
    SLIDE = "slide"
    WIPE = "wipe"
    ZOOM = "zoom"
    DISSOLVE = "dissolve"


@dataclass
class VideoTemplate:
    """Template for intro/outro sequences"""
    template_id: str
    duration: float  # seconds
    
    # Visual elements
    background_type: str  # "solid", "gradient", "video", "image"
    background_content: Optional[str]  # color/path
    
    # Text elements
    title_text: Optional[str]
    subtitle_text: Optional[str]
    title_animation: Optional[str]
    
    # Audio
    music_path: Optional[str]
    sound_effects: List[str] = field(default_factory=list)
    
    # Timing
    fade_in_duration: float = 0.5
    fade_out_duration: float = 0.5


@dataclass
class LogoConfiguration:
    """Logo display configuration"""
    logo_path: str
    position: str  # "top-left", "top-right", "bottom-left", "bottom-right", "center"
    size_percentage: float  # Percentage of frame width
    opacity: float = 1.0
    
    # Display timing
    always_visible: bool = True
    appear_at: Optional[float] = None  # seconds
    disappear_at: Optional[float] = None  # seconds
    
    # Animation
    entrance_animation: Optional[str] = None
    exit_animation: Optional[str] = None
    
    # Safe zones
    margin_percentage: float = 2.0  # Margin from edges


@dataclass
class LowerThirdsStyle:
    """Lower thirds configuration for themes"""
    enabled: bool = True
    
    # Visual style
    background_type: str = "gradient"  # "solid", "gradient", "blur"
    background_color_primary: str = "#000000"
    background_color_secondary: Optional[str] = "#333333"
    background_opacity: float = 0.8
    
    # Text style
    title_font_size_ratio: float = 0.06  # Relative to frame height
    subtitle_font_size_ratio: float = 0.04
    title_color: str = "#FFFFFF"
    subtitle_color: str = "#CCCCCC"
    
    # Animation
    entrance_animation: str = "slide-left"
    exit_animation: str = "slide-left"
    animation_duration: float = 0.5
    
    # Position
    position_y_percentage: float = 75.0  # From top
    height_percentage: float = 15.0
    margin_x_percentage: float = 5.0


@dataclass
class CaptionStyle:
    """Caption/subtitle style for themes"""
    # Font settings
    font_family: Optional[str] = None
    font_size_ratio: float = 0.04  # Relative to frame height
    font_color: str = "#FFFFFF"
    font_weight: str = "bold"
    
    # Background
    background_enabled: bool = True
    background_color: str = "#000000"
    background_opacity: float = 0.7
    background_padding: float = 10.0  # pixels
    
    # Shadow/outline
    shadow_enabled: bool = True
    shadow_color: str = "#000000"
    shadow_offset: float = 2.0
    
    # Position
    position_y_percentage: float = 85.0  # From top
    max_width_percentage: float = 80.0


@dataclass
class BrandKit:
    """Brand assets and guidelines"""
    # Logos
    primary_logo: str
    primary_logo_dark: Optional[str] = None  # Dark background variant
    primary_logo_light: Optional[str] = None  # Light background variant
    secondary_logo: Optional[str] = None
    
    # Colors
    color_primary: str = "#000000"
    color_secondary: str = "#FFFFFF"
    color_accent: str = "#FF0000"
    color_background: str = "#F5F5F5"
    color_text_primary: str = "#000000"
    color_text_secondary: str = "#666666"
    
    # Typography
    fonts: Dict[str, str] = field(default_factory=dict)  # {"heading": "Arial", "body": "Helvetica"}
    
    # Brand guidelines
    logo_safe_zones: Dict[str, float] = field(default_factory=dict)  # {"top": 10, "right": 10, ...}
    minimum_logo_size_percentage: float = 5.0  # Minimum size as % of frame width
    clear_space_ratio: float = 1.5  # Clear space around logo as ratio of logo size
    
    # Usage rules
    allow_logo_on_dark: bool = True
    allow_logo_on_light: bool = True
    allow_logo_rotation: bool = False
    allow_logo_effects: bool = False


@dataclass
class Theme:
    """Represents a complete theme configuration"""
    # Identification
    theme_id: str = field(default_factory=lambda: f"theme_{uuid.uuid4().hex[:8]}")
    name: str = "Untitled Theme"
    category: ThemeCategory = ThemeCategory.CUSTOM
    version: str = "1.0.0"
    
    # Visual identity
    style_reference: Optional[StyleReference] = None
    brand_kit: Optional[BrandKit] = None
    
    # Content structure
    intro_template: Optional[VideoTemplate] = None
    outro_template: Optional[VideoTemplate] = None
    transition_style: TransitionStyle = TransitionStyle.CUT
    transition_duration: float = 0.5
    
    # Overlay configuration
    logo_config: Optional[LogoConfiguration] = None
    lower_thirds_style: Optional[LowerThirdsStyle] = None
    caption_style: Optional[CaptionStyle] = None
    
    # Audio identity
    intro_music: Optional[str] = None
    outro_music: Optional[str] = None
    background_music_style: Optional[str] = None
    sound_effects_pack: Optional[str] = None
    
    # Content guidelines
    content_tone: Optional[str] = None  # "professional", "casual", "energetic"
    content_style: Optional[str] = None  # "informative", "entertaining", "educational"
    target_audience: Optional[str] = None
    
    # Technical settings
    default_duration: Optional[int] = None
    default_aspect_ratio: str = "16:9"
    default_resolution: str = "1920x1080"
    default_frame_rate: int = 30
    
    # Metadata
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None
    
    # Theme inheritance
    parent_theme_id: Optional[str] = None  # For theme variations
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert theme to dictionary for serialization"""
        return {
            "theme_id": self.theme_id,
            "name": self.name,
            "category": self.category.value,
            "version": self.version,
            "style_reference_id": self.style_reference.reference_id if self.style_reference else None,
            "brand_kit": self._serialize_brand_kit(),
            "intro_template": self._serialize_template(self.intro_template),
            "outro_template": self._serialize_template(self.outro_template),
            "transition_style": self.transition_style.value,
            "transition_duration": self.transition_duration,
            "logo_config": self._serialize_logo_config(),
            "lower_thirds_style": self._serialize_lower_thirds(),
            "caption_style": self._serialize_caption_style(),
            "audio": {
                "intro_music": self.intro_music,
                "outro_music": self.outro_music,
                "background_music_style": self.background_music_style,
                "sound_effects_pack": self.sound_effects_pack
            },
            "content_guidelines": {
                "tone": self.content_tone,
                "style": self.content_style,
                "target_audience": self.target_audience
            },
            "technical_settings": {
                "default_duration": self.default_duration,
                "default_aspect_ratio": self.default_aspect_ratio,
                "default_resolution": self.default_resolution,
                "default_frame_rate": self.default_frame_rate
            },
            "metadata": {
                "description": self.description,
                "tags": self.tags,
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat(),
                "created_by": self.created_by,
                "parent_theme_id": self.parent_theme_id
            }
        }
    
    def _serialize_brand_kit(self) -> Optional[Dict[str, Any]]:
        """Serialize brand kit"""
        if not self.brand_kit:
            return None
        
        return {
            "primary_logo": self.brand_kit.primary_logo,
            "primary_logo_dark": self.brand_kit.primary_logo_dark,
            "primary_logo_light": self.brand_kit.primary_logo_light,
            "secondary_logo": self.brand_kit.secondary_logo,
            "colors": {
                "primary": self.brand_kit.color_primary,
                "secondary": self.brand_kit.color_secondary,
                "accent": self.brand_kit.color_accent,
                "background": self.brand_kit.color_background,
                "text_primary": self.brand_kit.color_text_primary,
                "text_secondary": self.brand_kit.color_text_secondary
            },
            "fonts": self.brand_kit.fonts,
            "guidelines": {
                "logo_safe_zones": self.brand_kit.logo_safe_zones,
                "minimum_logo_size_percentage": self.brand_kit.minimum_logo_size_percentage,
                "clear_space_ratio": self.brand_kit.clear_space_ratio,
                "allow_logo_on_dark": self.brand_kit.allow_logo_on_dark,
                "allow_logo_on_light": self.brand_kit.allow_logo_on_light,
                "allow_logo_rotation": self.brand_kit.allow_logo_rotation,
                "allow_logo_effects": self.brand_kit.allow_logo_effects
            }
        }
    
    def _serialize_template(self, template: Optional[VideoTemplate]) -> Optional[Dict[str, Any]]:
        """Serialize video template"""
        if not template:
            return None
        
        return {
            "template_id": template.template_id,
            "duration": template.duration,
            "background_type": template.background_type,
            "background_content": template.background_content,
            "title_text": template.title_text,
            "subtitle_text": template.subtitle_text,
            "title_animation": template.title_animation,
            "music_path": template.music_path,
            "sound_effects": template.sound_effects,
            "fade_in_duration": template.fade_in_duration,
            "fade_out_duration": template.fade_out_duration
        }
    
    def _serialize_logo_config(self) -> Optional[Dict[str, Any]]:
        """Serialize logo configuration"""
        if not self.logo_config:
            return None
        
        return {
            "logo_path": self.logo_config.logo_path,
            "position": self.logo_config.position,
            "size_percentage": self.logo_config.size_percentage,
            "opacity": self.logo_config.opacity,
            "always_visible": self.logo_config.always_visible,
            "appear_at": self.logo_config.appear_at,
            "disappear_at": self.logo_config.disappear_at,
            "entrance_animation": self.logo_config.entrance_animation,
            "exit_animation": self.logo_config.exit_animation,
            "margin_percentage": self.logo_config.margin_percentage
        }
    
    def _serialize_lower_thirds(self) -> Optional[Dict[str, Any]]:
        """Serialize lower thirds style"""
        if not self.lower_thirds_style:
            return None
        
        return {
            "enabled": self.lower_thirds_style.enabled,
            "background_type": self.lower_thirds_style.background_type,
            "background_color_primary": self.lower_thirds_style.background_color_primary,
            "background_color_secondary": self.lower_thirds_style.background_color_secondary,
            "background_opacity": self.lower_thirds_style.background_opacity,
            "title_font_size_ratio": self.lower_thirds_style.title_font_size_ratio,
            "subtitle_font_size_ratio": self.lower_thirds_style.subtitle_font_size_ratio,
            "title_color": self.lower_thirds_style.title_color,
            "subtitle_color": self.lower_thirds_style.subtitle_color,
            "entrance_animation": self.lower_thirds_style.entrance_animation,
            "exit_animation": self.lower_thirds_style.exit_animation,
            "animation_duration": self.lower_thirds_style.animation_duration,
            "position_y_percentage": self.lower_thirds_style.position_y_percentage,
            "height_percentage": self.lower_thirds_style.height_percentage,
            "margin_x_percentage": self.lower_thirds_style.margin_x_percentage
        }
    
    def _serialize_caption_style(self) -> Optional[Dict[str, Any]]:
        """Serialize caption style"""
        if not self.caption_style:
            return None
        
        return {
            "font_family": self.caption_style.font_family,
            "font_size_ratio": self.caption_style.font_size_ratio,
            "font_color": self.caption_style.font_color,
            "font_weight": self.caption_style.font_weight,
            "background_enabled": self.caption_style.background_enabled,
            "background_color": self.caption_style.background_color,
            "background_opacity": self.caption_style.background_opacity,
            "background_padding": self.caption_style.background_padding,
            "shadow_enabled": self.caption_style.shadow_enabled,
            "shadow_color": self.caption_style.shadow_color,
            "shadow_offset": self.caption_style.shadow_offset,
            "position_y_percentage": self.caption_style.position_y_percentage,
            "max_width_percentage": self.caption_style.max_width_percentage
        }