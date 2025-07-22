"""
Style Attributes Models
Detailed style attributes for video style analysis and reference
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple
from enum import Enum


class ReferenceType(Enum):
    """Type of style reference source"""
    VIDEO = "video"
    IMAGE = "image"
    TEMPLATE = "template"


@dataclass
class ColorPalette:
    """Represents color scheme of a video/image"""
    primary_color: str  # Hex color
    secondary_color: str
    accent_color: str
    background_colors: List[str]
    text_colors: List[str]
    
    # Color properties
    saturation_level: float  # 0-1
    brightness_level: float  # 0-1
    contrast_ratio: float
    
    # Color mood
    mood: str  # e.g., "warm", "cool", "neutral", "vibrant"
    

@dataclass
class Typography:
    """Typography and text style information"""
    primary_font_family: Optional[str]
    secondary_font_family: Optional[str]
    
    # Text properties
    title_size_ratio: float  # Relative to frame height
    body_size_ratio: float
    
    # Style properties
    font_weight: str  # e.g., "light", "regular", "bold"
    letter_spacing: float
    line_height: float
    
    # Text effects
    has_shadow: bool
    has_outline: bool
    text_animation_style: Optional[str]


@dataclass
class Composition:
    """Visual composition and layout information"""
    rule_of_thirds_adherence: float  # 0-1 score
    symmetry_score: float
    
    # Layout patterns
    primary_layout: str  # e.g., "centered", "left-aligned", "grid"
    text_placement_zones: List[str]  # e.g., ["lower-third", "center", "top-right"]
    
    # Spacing
    margin_ratio: float  # Margins relative to frame size
    padding_ratio: float
    
    # Visual hierarchy
    focal_point_strategy: str
    depth_layers: int  # Number of visual depth layers


@dataclass
class MotionStyle:
    """Motion and animation characteristics"""
    camera_movement: str  # e.g., "static", "slow-pan", "dynamic"
    transition_style: str  # e.g., "cut", "fade", "slide"
    
    # Motion properties
    average_shot_duration: float  # seconds
    movement_intensity: float  # 0-1
    
    # Animation
    text_animation_type: Optional[str]
    element_animation_style: Optional[str]
    
    # Pacing
    pacing: str  # e.g., "slow", "medium", "fast", "variable"
    rhythm_pattern: Optional[str]


@dataclass
class VisualEffect:
    """Individual visual effect"""
    effect_type: str  # e.g., "blur", "glow", "grain"
    intensity: float  # 0-1
    apply_to: str  # e.g., "background", "text", "full-frame"
    parameters: Dict[str, any]


@dataclass
class LogoPlacement:
    """Logo placement configuration"""
    position: str  # e.g., "top-left", "bottom-right"
    size_ratio: float  # Relative to frame size
    opacity: float
    
    # Animation
    entrance_animation: Optional[str]
    exit_animation: Optional[str]
    
    # Timing
    display_duration: Optional[float]  # None means always visible
    fade_in_time: float
    fade_out_time: float


@dataclass
class Watermark:
    """Watermark configuration"""
    text: Optional[str]
    image_path: Optional[str]
    position: str
    opacity: float
    size_ratio: float


@dataclass
class LowerThirds:
    """Lower thirds style configuration"""
    background_style: str  # e.g., "solid", "gradient", "blur"
    background_color: str
    background_opacity: float
    
    # Text style
    title_color: str
    subtitle_color: str
    
    # Animation
    entrance_style: str  # e.g., "slide", "fade", "wipe"
    exit_style: str
    
    # Layout
    height_ratio: float  # Relative to frame height
    margin_ratio: float