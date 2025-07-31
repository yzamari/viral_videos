"""Composition Models for Video Creation"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum, auto
from datetime import datetime


class LayerType(Enum):
    """Types of composition layers"""
    BACKGROUND = "background"  # Base video/image
    OVERLAY = "overlay"  # Graphics, logos, watermarks
    TEXT = "text"  # Headlines, subtitles, info
    PRESENTER = "presenter"  # AI presenter/avatar
    EFFECTS = "effects"  # Transitions, animations
    AUDIO = "audio"  # Background music, narration


class TransitionType(Enum):
    """Types of transitions between segments"""
    CUT = "cut"
    FADE = "fade"
    DISSOLVE = "dissolve"
    WIPE = "wipe"
    SLIDE = "slide"
    ZOOM = "zoom"
    MORPH = "morph"
    CUSTOM = "custom"


class PresenterStyle(Enum):
    """Styles of AI presenters"""
    FORMAL_NEWS = "formal_news"
    CASUAL_VLOG = "casual_vlog"
    ENERGETIC_SPORTS = "energetic_sports"
    TECH_REVIEWER = "tech_reviewer"
    DOCUMENTARY = "documentary"
    COMEDY = "comedy"
    EDUCATIONAL = "educational"


@dataclass
class Position:
    """Position in video frame"""
    x: int
    y: int
    anchor: str = "top-left"  # top-left, center, bottom-right, etc.
    
    def to_dict(self) -> Dict[str, Any]:
        return {"x": self.x, "y": self.y, "anchor": self.anchor}


@dataclass
class AnimationKeyframe:
    """Animation keyframe for effects"""
    time: float  # seconds
    position: Optional[Position] = None
    scale: float = 1.0
    rotation: float = 0.0
    opacity: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VideoLayer:
    """Represents a single layer in video composition"""
    layer_type: LayerType
    z_index: int  # stacking order
    start_time: float = 0.0
    duration: Optional[float] = None  # None means full video duration
    position: Optional[Position] = None
    size: Optional[Tuple[int, int]] = None  # width, height
    opacity: float = 1.0
    blend_mode: str = "normal"
    animations: List[AnimationKeyframe] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TransitionEffect:
    """Transition between video segments"""
    transition_type: TransitionType
    duration: float = 1.0  # seconds
    easing: str = "ease-in-out"
    properties: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def quick_cut(cls) -> 'TransitionEffect':
        return cls(TransitionType.CUT, duration=0.0)
    
    @classmethod
    def smooth_fade(cls, duration: float = 1.0) -> 'TransitionEffect':
        return cls(TransitionType.FADE, duration=duration)


@dataclass
class GraphicAsset:
    """Graphic overlay asset"""
    id: str
    asset_path: str
    asset_type: str  # logo, lower_third, banner, etc.
    default_position: Position
    default_size: Tuple[int, int]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThemeConfig:
    """Visual theme configuration"""
    name: str
    primary_color: str  # hex color
    secondary_color: str
    accent_color: str
    background_color: str
    font_family: str
    font_sizes: Dict[str, int] = field(default_factory=lambda: {
        "headline": 48,
        "subtitle": 32,
        "body": 24,
        "caption": 18
    })
    text_colors: Dict[str, str] = field(default_factory=lambda: {
        "primary": "#FFFFFF",
        "secondary": "#CCCCCC",
        "accent": "#FF0000"
    })
    logo_path: Optional[str] = None
    watermark_path: Optional[str] = None
    background_music: Optional[str] = None
    overlay_graphics: List[GraphicAsset] = field(default_factory=list)
    animations: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def professional_news(cls) -> 'ThemeConfig':
        """Professional news theme preset"""
        return cls(
            name="Professional News",
            primary_color="#1E3A8A",
            secondary_color="#3B82F6",
            accent_color="#EF4444",
            background_color="#000000",
            font_family="Arial",
            font_sizes={
                "headline": 56,
                "subtitle": 36,
                "body": 28,
                "caption": 20,
                "ticker": 24
            }
        )
    
    @classmethod
    def modern_tech(cls) -> 'ThemeConfig':
        """Modern tech theme preset"""
        return cls(
            name="Modern Tech",
            primary_color="#10B981",
            secondary_color="#34D399",
            accent_color="#8B5CF6",
            background_color="#111827",
            font_family="Roboto"
        )


@dataclass
class VideoSegment:
    """A single segment in the video composition"""
    id: str
    content_item_id: Optional[str] = None  # Link to ContentItem
    duration: float = 5.0  # seconds
    layers: List[VideoLayer] = field(default_factory=list)
    narration_text: Optional[str] = None
    subtitle_text: Optional[str] = None
    transition_in: Optional[TransitionEffect] = None
    transition_out: Optional[TransitionEffect] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PresenterConfig:
    """Configuration for AI presenter"""
    presenter_style: PresenterStyle
    model_id: str  # ID of the presenter model/avatar
    voice_id: str  # ID of the voice model
    position: Position = field(default_factory=lambda: Position(100, 100))
    size: Tuple[int, int] = (400, 400)
    speaking_speed: float = 1.0
    emotion_level: float = 0.7  # 0-1, how expressive
    gestures_enabled: bool = True
    background_removal: bool = True
    custom_animations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NewsTemplate:
    """Template for news-style video creation"""
    id: str
    name: str
    description: str
    category: str  # daily_news, sports, tech, etc.
    duration_range: Tuple[int, int] = (180, 300)  # 3-5 minutes
    
    # Sequence components
    intro_duration: float = 5.0
    outro_duration: float = 5.0
    segment_duration_range: Tuple[float, float] = (15.0, 45.0)
    
    # Visual configuration
    theme_config: ThemeConfig = field(default_factory=ThemeConfig.professional_news)
    presenter_config: Optional[PresenterConfig] = None
    
    # Layout configuration
    headline_position: Position = field(default_factory=lambda: Position(50, 50))
    subtitle_position: Position = field(default_factory=lambda: Position(50, 920))
    ticker_position: Position = field(default_factory=lambda: Position(0, 1000))
    presenter_position: Optional[Position] = None
    
    # Transitions
    default_transition: TransitionEffect = field(default_factory=TransitionEffect.smooth_fade)
    segment_transitions: List[TransitionEffect] = field(default_factory=list)
    
    # Content rules
    max_segments: int = 10
    min_segments: int = 3
    require_media: bool = True
    
    # Additional properties
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompositionProject:
    """Complete video composition project"""
    id: str
    name: str
    template: NewsTemplate
    segments: List[VideoSegment] = field(default_factory=list)
    content_collection_id: Optional[str] = None
    
    # Output configuration
    output_resolution: Tuple[int, int] = (1920, 1080)
    output_fps: int = 30
    output_format: str = "mp4"
    output_codec: str = "h264"
    
    # Audio configuration
    background_music_volume: float = 0.3
    narration_volume: float = 1.0
    enable_subtitles: bool = True
    
    # Multi-language
    primary_language: str = "en"
    additional_languages: List[str] = field(default_factory=list)
    
    # Status tracking
    status: str = "draft"  # draft, processing, completed, failed
    created_date: datetime = field(default_factory=datetime.now)
    render_start: Optional[datetime] = None
    render_complete: Optional[datetime] = None
    
    # Output paths
    output_path: Optional[str] = None
    preview_path: Optional[str] = None
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_segment(self, segment: VideoSegment):
        """Add a segment to the composition"""
        self.segments.append(segment)
    
    def get_total_duration(self) -> float:
        """Calculate total video duration"""
        total = self.template.intro_duration + self.template.outro_duration
        total += sum(segment.duration for segment in self.segments)
        # Add transition durations
        for i in range(len(self.segments) - 1):
            if self.segments[i].transition_out:
                total += self.segments[i].transition_out.duration
        return total
    
    def validate(self) -> List[str]:
        """Validate the composition project"""
        errors = []
        
        if len(self.segments) < self.template.min_segments:
            errors.append(f"Too few segments: {len(self.segments)} < {self.template.min_segments}")
        
        if len(self.segments) > self.template.max_segments:
            errors.append(f"Too many segments: {len(self.segments)} > {self.template.max_segments}")
        
        total_duration = self.get_total_duration()
        min_dur, max_dur = self.template.duration_range
        
        if total_duration < min_dur:
            errors.append(f"Video too short: {total_duration}s < {min_dur}s")
        
        if total_duration > max_dur:
            errors.append(f"Video too long: {total_duration}s > {max_dur}s")
        
        return errors