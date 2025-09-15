"""
Comprehensive video generation configuration
All video generation parameters should be defined here, no hardcoding allowed
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class VideoEncodingConfig:
    """Video encoding parameters"""
    # Frame rates by platform
    fps_by_platform: Dict[str, int] = field(default_factory=lambda: {
        'youtube': 30,
        'tiktok': 30,
        'instagram': 30,
        'facebook': 30,
        'twitter': 30,
        'linkedin': 30,
        'default': 30
    })
    
    # Video codec settings
    video_codec: str = 'libx264'
    audio_codec: str = 'aac'
    pixel_format: str = 'yuv420p'
    
    # Quality presets by platform
    encoding_presets: Dict[str, str] = field(default_factory=lambda: {
        'youtube': 'medium',      # Better quality for YouTube
        'tiktok': 'fast',        # Faster encoding for short videos
        'instagram': 'fast',     
        'facebook': 'medium',
        'twitter': 'fast',
        'linkedin': 'medium',
        'default': 'medium'
    })
    
    # CRF (Constant Rate Factor) - lower = better quality, larger file
    crf_by_platform: Dict[str, int] = field(default_factory=lambda: {
        'youtube': 23,          # Good quality
        'tiktok': 25,          # Slightly lower quality for smaller files
        'instagram': 25,
        'facebook': 23,
        'twitter': 25,
        'linkedin': 23,
        'default': 23
    })
    
    # Audio bitrate
    audio_bitrate: str = '128k'
    
    # Fallback/minimal encoding settings
    fallback_fps: int = 24
    fallback_preset: str = 'fast'
    fallback_crf: int = 28


@dataclass
class TextOverlayConfig:
    """Text overlay styling parameters"""
    # Font settings
    default_font: str = 'Arial-Bold'
    rtl_font: str = 'Arial Unicode MS'  # Better RTL support for Hebrew/Arabic/Persian
    
    # Font sizes (relative to video dimensions)
    font_sizes: Dict[str, float] = field(default_factory=lambda: {
        'title': 0.06,          # 6% of video width
        'subtitle': 0.0083,     # 0.83% of video width - optimized for 9px on 1080px width
        'header': 0.05,         # 5% of video width
        'body': 0.04,           # 4% of video width
        'caption': 0.035,       # 3.5% of video width
        'badge': 0.03,          # 3% of video width
        'news_ticker': 0.025,   # 2.5% of video width
        'default': 0.04
    })
    
    # Minimum font sizes (absolute pixels)
    min_font_sizes: Dict[str, int] = field(default_factory=lambda: {
        'title': 48,
        'subtitle': 9,          # Perfect subtitle size - small and readable
        'header': 40,
        'body': 32,
        'caption': 28,
        'badge': 24,
        'news_ticker': 20,
        'default': 32
    })
    
    # Stroke settings - increased for better visibility
    stroke_widths: Dict[str, int] = field(default_factory=lambda: {
        'title': 5,      # Increased from 3
        'subtitle': 1,   # Perfect outline width for small subtitles
        'header': 5,     # Increased from 3
        'body': 3,       # Increased from 2
        'caption': 3,    # Increased from 2
        'badge': 3,      # Increased from 2
        'news_ticker': 2, # Increased from 1
        'default': 3     # Increased from 2
    })
    
    # Colors
    default_text_color: str = 'white'
    default_stroke_color: str = 'black'
    
    # Opacity settings
    default_opacity: float = 1.0
    background_opacity: float = 0.8
    badge_opacity: float = 0.6


@dataclass
class AnimationTimingConfig:
    """Animation and timing parameters"""
    # Fade settings
    fade_in_duration: float = 0.5
    fade_out_duration: float = 2.0
    
    # Display durations
    hook_display_duration: float = 3.0
    cta_display_duration: float = 3.0
    
    # Animation timing
    subtitle_fade_duration: float = 0.2
    overlay_fade_duration: float = 0.3
    
    # Frame timing (calculated from fps)
    @staticmethod
    def get_frame_duration(fps: int) -> float:
        """Get duration of single frame in seconds"""
        return 1.0 / fps
    
    # Transition settings
    default_transition_duration: float = 0.5
    crossfade_duration: float = 1.0
    
    # Continuity settings
    frame_continuity_trim_frames: int = 1
    frame_continuity_blend_frames: int = 2


@dataclass
class DefaultTextConfig:
    """Default text templates"""
    # Platform-specific hooks
    hooks_by_platform: Dict[str, str] = field(default_factory=lambda: {
        'youtube': "Discover something amazing!",
        'tiktok': "Wait for it...",
        'instagram': "You won't believe this!",
        'facebook': "Check this out!",
        'twitter': "Thread below 👇",
        'linkedin': "Key insights ahead",
        'default': "Watch this!"
    })
    
    # Platform-specific CTAs
    ctas_by_platform: Dict[str, str] = field(default_factory=lambda: {
        'youtube': "Subscribe for more!",
        'tiktok': "Follow for more!",
        'instagram': "Follow for daily content!",
        'facebook': "Like and share!",
        'twitter': "Retweet if you agree!",
        'linkedin': "Connect for insights!",
        'default': "Follow for more!"
    })
    
    # Badge texts
    badge_texts: Dict[str, str] = field(default_factory=lambda: {
        'cheap': "💰 CHEAP",
        'premium': "✨ PREMIUM",
        # VEO2 deprecated and removed
        'veo3': "🎬 VEO-3",
        'ai': "🤖 AI",
        'news': "📰 NEWS",
        'breaking': "🚨 BREAKING"
    })
    
    # News-specific text
    news_channel_text: str = "IRAN INTERNATIONAL"
    breaking_news_text: str = "BREAKING NEWS"


@dataclass
class LayoutConfig:
    """Layout and positioning parameters"""
    # Subtitle positioning (from bottom)
    subtitle_bottom_offset: Dict[str, int] = field(default_factory=lambda: {
        'default': 150,
        'news': 250,           # Higher to avoid news ticker
        'minimal': 100,
        'centered': 200
    })
    
    # Overlay positioning (percentage-based to avoid subtitle conflicts)
    overlay_positions: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        'hook': {
            'x': 'center',
            'y_percent': 0.08,    # 8% from top - well above subtitles
            'animation': 'slide_in'
        },
        'cta': {
            'x': 'right-30',
            'y_percent': 0.15,    # 15% from top - above subtitle area
            'animation': 'slide_in'
        },
        'badge': {
            'x': 50,
            'y_percent': 0.20,    # 20% from top - safe from subtitles
            'animation': 'fade'
        },
        'overlay_default': {
            'x': 'center',
            'y_percent': 0.25,    # 25% from top - default overlay position
            'animation': 'fade'
        },
        'news_ticker': {
            'x': 0,
            'y': 'bottom-100',
            'height': 100,
            'animation': 'none'
        },
        'news_banner': {
            'x': 0,
            'y': 0,
            'height': 120,
            'animation': 'none'
        }
    })
    
    # Subtitle positioning percentages (reserved area)
    subtitle_positions: Dict[str, float] = field(default_factory=lambda: {
        'portrait': 0.75,     # 75% down for mobile/portrait
        'landscape': 0.80,    # 80% down for desktop/landscape
        'safe_zone_start': 0.70,  # Overlays should stay above 70%
    })
    
    # Spacing
    overlay_vertical_spacing: int = 80
    overlay_horizontal_padding: int = 30
    
    # Safe zones (percentage of video dimensions)
    safe_zone_percentage: float = 0.05  # 5% margin on all sides
    
    # Text wrapping
    max_subtitle_width_percentage: float = 0.9  # 90% of video width
    max_overlay_width_percentage: float = 0.8   # 80% of video width


@dataclass
class AudioConfig:
    """Audio generation and validation parameters"""
    # Duration tolerance
    duration_tolerance_percent: float = 20.0  # Accept ±20% duration variance (allows quiet time)
    
    # Segment duration constraints
    min_segment_duration: float = 0.1       # Minimum 0.1 seconds per segment (allows one sentence per segment)
    max_segment_duration: float = 8.0       # Maximum 8 seconds per segment
    one_sentence_per_segment: bool = True   # Create one audio segment per sentence for perfect subtitle sync
    
    # Padding between segments
    padding_between_segments: float = 0.3   # 300ms pause between segments
    
    # Quality thresholds
    min_quality_score: float = 0.6          # Minimum quality score to proceed
    block_on_duration_failure: bool = True  # Block generation if duration fails
    
    # Regeneration settings
    max_regeneration_attempts: int = 3      # Max attempts to regenerate audio
    speech_rate_adjustment_step: float = 0.1  # Adjust speech rate by 10% per retry
    
    # Sound effect handling
    sound_effect_patterns: list = field(default_factory=lambda: [
        r'\b(POOF|WHOOSH|BANG|POW|ZAP|BOOM|CRASH|SNAP|KA-POW)\b',
        r'\b(whoosh|poof|bang|pow|zap|boom|crash|snap)\b',
        r'\*[^*]+\*',  # Anything in asterisks like *explosion*
    ])
    min_sound_effect_duration: float = 0.5  # Minimum duration for sound effects
    
    # Voice speed settings by language
    voice_speed_multipliers: Dict[str, float] = field(default_factory=lambda: {
        'en-US': 1.0,
        'en-GB': 0.95,
        'en-IN': 1.05,
        'he': 0.9,      # Hebrew often needs slower speech
        'ar': 0.9,      # Arabic too
        'default': 1.0
    })


@dataclass
class VideoGenerationConfig:
    """Master configuration for video generation"""
    encoding: VideoEncodingConfig = field(default_factory=VideoEncodingConfig)
    text_overlay: TextOverlayConfig = field(default_factory=TextOverlayConfig)
    animation: AnimationTimingConfig = field(default_factory=AnimationTimingConfig)
    default_text: DefaultTextConfig = field(default_factory=DefaultTextConfig)
    layout: LayoutConfig = field(default_factory=LayoutConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    
    def get_fps(self, platform: str) -> int:
        """Get FPS for platform"""
        return self.encoding.fps_by_platform.get(
            platform.lower(), 
            self.encoding.fps_by_platform['default']
        )
    
    def get_encoding_preset(self, platform: str) -> str:
        """Get encoding preset for platform"""
        return self.encoding.encoding_presets.get(
            platform.lower(),
            self.encoding.encoding_presets['default']
        )
    
    def get_crf(self, platform: str) -> int:
        """Get CRF value for platform"""
        return self.encoding.crf_by_platform.get(
            platform.lower(),
            self.encoding.crf_by_platform['default']
        )
    
    def get_font_size(self, text_type: str, video_width: int) -> int:
        """Calculate font size based on video width and text type"""
        percentage = self.text_overlay.font_sizes.get(
            text_type,
            self.text_overlay.font_sizes['default']
        )
        calculated_size = int(video_width * percentage)
        min_size = self.text_overlay.min_font_sizes.get(
            text_type,
            self.text_overlay.min_font_sizes['default']
        )
        return max(calculated_size, min_size)
    
    def get_stroke_width(self, text_type: str) -> int:
        """Get stroke width for text type"""
        return self.text_overlay.stroke_widths.get(
            text_type,
            self.text_overlay.stroke_widths['default']
        )
    
    def get_default_hook(self, platform: str) -> str:
        """Get default hook for platform"""
        return self.default_text.hooks_by_platform.get(
            platform.lower(),
            self.default_text.hooks_by_platform['default']
        )
    
    def get_default_cta(self, platform: str) -> str:
        """Get default CTA for platform"""
        return self.default_text.ctas_by_platform.get(
            platform.lower(),
            self.default_text.ctas_by_platform['default']
        )
    
    def get_subtitle_offset(self, theme: Optional[str] = None) -> int:
        """Get subtitle bottom offset based on theme"""
        if theme and theme in self.layout.subtitle_bottom_offset:
            return self.layout.subtitle_bottom_offset[theme]
        return self.layout.subtitle_bottom_offset['default']


# Global configuration instance
video_config = VideoGenerationConfig()