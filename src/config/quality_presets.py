"""
Quality Presets Configuration - Professional video quality settings
Following SOLID principles for extensible configuration management
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum


class QualityTier(Enum):
    """Quality tiers for video production"""
    DRAFT = "draft"
    STANDARD = "standard"
    HIGH = "high"
    PROFESSIONAL = "professional"
    BROADCAST = "broadcast"
    CINEMA = "cinema"


class Platform(Enum):
    """Target platforms with specific requirements"""
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    VIMEO = "vimeo"
    BROADCAST = "broadcast"


@dataclass
class VideoPreset:
    """Video encoding preset"""
    resolution: str
    fps: int
    bitrate: str
    codec: str
    pixel_format: str
    color_space: str
    profile: str
    preset: str  # FFmpeg preset (ultrafast, fast, medium, slow, veryslow)
    crf: int  # Constant Rate Factor for quality


@dataclass
class AudioPreset:
    """Audio encoding preset"""
    sample_rate: int
    bitrate: str
    channels: int
    codec: str
    normalization: bool
    compression: bool
    noise_reduction: bool


@dataclass
class EffectsPreset:
    """Effects and transitions preset"""
    enable_transitions: bool
    transition_type: str
    transition_duration: float
    enable_color_grading: bool
    color_lut: str
    enable_stabilization: bool
    enable_motion_blur: bool
    enable_text_animations: bool


@dataclass
class QualityCheckPreset:
    """Quality validation thresholds"""
    min_sharpness: float
    min_brightness: float
    min_contrast: float
    max_noise: float
    min_audio_clarity: float
    min_sync_score: float
    min_narrative_score: float


@dataclass
class QualityPreset:
    """Complete quality preset configuration"""
    name: str
    tier: QualityTier
    video: VideoPreset
    audio: AudioPreset
    effects: EffectsPreset
    quality_checks: QualityCheckPreset
    description: str
    use_cases: List[str] = field(default_factory=list)


# Preset Definitions
QUALITY_PRESETS = {
    # Draft Quality - Fast preview
    'draft': QualityPreset(
        name='Draft Preview',
        tier=QualityTier.DRAFT,
        video=VideoPreset(
            resolution='854x480',
            fps=24,
            bitrate='1M',
            codec='libx264',
            pixel_format='yuv420p',
            color_space='bt709',
            profile='baseline',
            preset='ultrafast',
            crf=30
        ),
        audio=AudioPreset(
            sample_rate=22050,
            bitrate='64k',
            channels=1,
            codec='aac',
            normalization=False,
            compression=False,
            noise_reduction=False
        ),
        effects=EffectsPreset(
            enable_transitions=False,
            transition_type='cut',
            transition_duration=0,
            enable_color_grading=False,
            color_lut='none',
            enable_stabilization=False,
            enable_motion_blur=False,
            enable_text_animations=False
        ),
        quality_checks=QualityCheckPreset(
            min_sharpness=0.3,
            min_brightness=0.3,
            min_contrast=0.3,
            max_noise=0.8,
            min_audio_clarity=0.3,
            min_sync_score=0.3,
            min_narrative_score=0.3
        ),
        description='Quick draft for preview and testing',
        use_cases=['testing', 'preview', 'rapid iteration']
    ),
    
    # Standard Quality - Good for most social media
    'standard': QualityPreset(
        name='Standard Quality',
        tier=QualityTier.STANDARD,
        video=VideoPreset(
            resolution='1280x720',
            fps=30,
            bitrate='3M',
            codec='libx264',
            pixel_format='yuv420p',
            color_space='bt709',
            profile='main',
            preset='fast',
            crf=23
        ),
        audio=AudioPreset(
            sample_rate=44100,
            bitrate='128k',
            channels=2,
            codec='aac',
            normalization=True,
            compression=False,
            noise_reduction=True
        ),
        effects=EffectsPreset(
            enable_transitions=True,
            transition_type='fade',
            transition_duration=0.5,
            enable_color_grading=True,
            color_lut='vibrant',
            enable_stabilization=False,
            enable_motion_blur=False,
            enable_text_animations=True
        ),
        quality_checks=QualityCheckPreset(
            min_sharpness=0.5,
            min_brightness=0.5,
            min_contrast=0.5,
            max_noise=0.5,
            min_audio_clarity=0.6,
            min_sync_score=0.6,
            min_narrative_score=0.6
        ),
        description='Standard quality for social media',
        use_cases=['social media', 'youtube', 'instagram']
    ),
    
    # High Quality - Professional social media
    'high': QualityPreset(
        name='High Quality',
        tier=QualityTier.HIGH,
        video=VideoPreset(
            resolution='1920x1080',
            fps=30,
            bitrate='6M',
            codec='libx264',
            pixel_format='yuv420p',
            color_space='bt709',
            profile='high',
            preset='medium',
            crf=19
        ),
        audio=AudioPreset(
            sample_rate=48000,
            bitrate='192k',
            channels=2,
            codec='aac',
            normalization=True,
            compression=True,
            noise_reduction=True
        ),
        effects=EffectsPreset(
            enable_transitions=True,
            transition_type='slide',
            transition_duration=0.7,
            enable_color_grading=True,
            color_lut='cinematic',
            enable_stabilization=True,
            enable_motion_blur=True,
            enable_text_animations=True
        ),
        quality_checks=QualityCheckPreset(
            min_sharpness=0.7,
            min_brightness=0.6,
            min_contrast=0.6,
            max_noise=0.3,
            min_audio_clarity=0.7,
            min_sync_score=0.7,
            min_narrative_score=0.7
        ),
        description='High quality for professional content',
        use_cases=['professional', 'marketing', 'brand content']
    ),
    
    # Professional Quality
    'professional': QualityPreset(
        name='Professional',
        tier=QualityTier.PROFESSIONAL,
        video=VideoPreset(
            resolution='1920x1080',
            fps=60,
            bitrate='8M',
            codec='libx264',
            pixel_format='yuv422p',
            color_space='bt709',
            profile='high422',
            preset='slow',
            crf=17
        ),
        audio=AudioPreset(
            sample_rate=48000,
            bitrate='256k',
            channels=2,
            codec='aac',
            normalization=True,
            compression=True,
            noise_reduction=True
        ),
        effects=EffectsPreset(
            enable_transitions=True,
            transition_type='zoom',
            transition_duration=1.0,
            enable_color_grading=True,
            color_lut='cinematic',
            enable_stabilization=True,
            enable_motion_blur=True,
            enable_text_animations=True
        ),
        quality_checks=QualityCheckPreset(
            min_sharpness=0.8,
            min_brightness=0.7,
            min_contrast=0.7,
            max_noise=0.2,
            min_audio_clarity=0.8,
            min_sync_score=0.8,
            min_narrative_score=0.8
        ),
        description='Professional grade for high-end content',
        use_cases=['commercial', 'advertising', 'premium content']
    ),
    
    # Broadcast Quality
    'broadcast': QualityPreset(
        name='Broadcast Quality',
        tier=QualityTier.BROADCAST,
        video=VideoPreset(
            resolution='1920x1080',
            fps=50,  # PAL standard, use 59.94 for NTSC
            bitrate='15M',
            codec='libx264',
            pixel_format='yuv422p10le',
            color_space='bt709',
            profile='high422',
            preset='slow',
            crf=15
        ),
        audio=AudioPreset(
            sample_rate=48000,
            bitrate='384k',
            channels=2,
            codec='pcm_s16le',  # Uncompressed for broadcast
            normalization=True,
            compression=True,
            noise_reduction=True
        ),
        effects=EffectsPreset(
            enable_transitions=True,
            transition_type='professional',
            transition_duration=1.0,
            enable_color_grading=True,
            color_lut='broadcast',
            enable_stabilization=True,
            enable_motion_blur=True,
            enable_text_animations=True
        ),
        quality_checks=QualityCheckPreset(
            min_sharpness=0.9,
            min_brightness=0.8,
            min_contrast=0.8,
            max_noise=0.1,
            min_audio_clarity=0.9,
            min_sync_score=0.95,
            min_narrative_score=0.85
        ),
        description='Broadcast television standards',
        use_cases=['television', 'broadcast', 'streaming']
    ),
    
    # Cinema Quality
    'cinema': QualityPreset(
        name='Cinema Quality',
        tier=QualityTier.CINEMA,
        video=VideoPreset(
            resolution='3840x2160',  # 4K
            fps=24,  # Cinema standard
            bitrate='25M',
            codec='libx265',  # H.265 for 4K
            pixel_format='yuv420p10le',  # 10-bit color
            color_space='bt2020',  # Wide color gamut
            profile='main10',
            preset='veryslow',
            crf=14
        ),
        audio=AudioPreset(
            sample_rate=96000,
            bitrate='448k',
            channels=6,  # 5.1 surround
            codec='flac',  # Lossless
            normalization=True,
            compression=True,
            noise_reduction=True
        ),
        effects=EffectsPreset(
            enable_transitions=True,
            transition_type='cinematic',
            transition_duration=1.5,
            enable_color_grading=True,
            color_lut='cinema',
            enable_stabilization=True,
            enable_motion_blur=True,
            enable_text_animations=True
        ),
        quality_checks=QualityCheckPreset(
            min_sharpness=0.95,
            min_brightness=0.85,
            min_contrast=0.85,
            max_noise=0.05,
            min_audio_clarity=0.95,
            min_sync_score=0.98,
            min_narrative_score=0.9
        ),
        description='Cinema-grade production quality',
        use_cases=['film', 'cinema', 'high-end production']
    )
}


# Platform-specific presets
PLATFORM_PRESETS = {
    Platform.YOUTUBE: {
        'standard': QualityPreset(
            name='YouTube Standard',
            tier=QualityTier.STANDARD,
            video=VideoPreset(
                resolution='1920x1080',
                fps=30,
                bitrate='8M',
                codec='libx264',
                pixel_format='yuv420p',
                color_space='bt709',
                profile='high',
                preset='medium',
                crf=18
            ),
            audio=AudioPreset(
                sample_rate=48000,
                bitrate='192k',
                channels=2,
                codec='aac',
                normalization=True,
                compression=True,
                noise_reduction=True
            ),
            effects=EffectsPreset(
                enable_transitions=True,
                transition_type='fade',
                transition_duration=0.5,
                enable_color_grading=True,
                color_lut='vibrant',
                enable_stabilization=True,
                enable_motion_blur=False,
                enable_text_animations=True
            ),
            quality_checks=QualityCheckPreset(
                min_sharpness=0.7,
                min_brightness=0.6,
                min_contrast=0.6,
                max_noise=0.3,
                min_audio_clarity=0.7,
                min_sync_score=0.8,
                min_narrative_score=0.7
            ),
            description='Optimized for YouTube',
            use_cases=['youtube', 'long-form content']
        )
    },
    
    Platform.TIKTOK: {
        'standard': QualityPreset(
            name='TikTok Optimized',
            tier=QualityTier.STANDARD,
            video=VideoPreset(
                resolution='1080x1920',  # Portrait
                fps=30,
                bitrate='6M',
                codec='libx264',
                pixel_format='yuv420p',
                color_space='bt709',
                profile='high',
                preset='fast',
                crf=20
            ),
            audio=AudioPreset(
                sample_rate=44100,
                bitrate='128k',
                channels=2,
                codec='aac',
                normalization=True,
                compression=True,
                noise_reduction=True
            ),
            effects=EffectsPreset(
                enable_transitions=True,
                transition_type='glitch',
                transition_duration=0.3,
                enable_color_grading=True,
                color_lut='vibrant',
                enable_stabilization=False,
                enable_motion_blur=False,
                enable_text_animations=True
            ),
            quality_checks=QualityCheckPreset(
                min_sharpness=0.6,
                min_brightness=0.6,
                min_contrast=0.7,
                max_noise=0.4,
                min_audio_clarity=0.6,
                min_sync_score=0.7,
                min_narrative_score=0.6
            ),
            description='Optimized for TikTok',
            use_cases=['tiktok', 'short-form', 'viral']
        )
    },
    
    Platform.INSTAGRAM: {
        'reels': QualityPreset(
            name='Instagram Reels',
            tier=QualityTier.STANDARD,
            video=VideoPreset(
                resolution='1080x1920',  # Portrait
                fps=30,
                bitrate='5M',
                codec='libx264',
                pixel_format='yuv420p',
                color_space='bt709',
                profile='high',
                preset='fast',
                crf=21
            ),
            audio=AudioPreset(
                sample_rate=44100,
                bitrate='128k',
                channels=2,
                codec='aac',
                normalization=True,
                compression=True,
                noise_reduction=True
            ),
            effects=EffectsPreset(
                enable_transitions=True,
                transition_type='slide',
                transition_duration=0.4,
                enable_color_grading=True,
                color_lut='warm',
                enable_stabilization=True,
                enable_motion_blur=False,
                enable_text_animations=True
            ),
            quality_checks=QualityCheckPreset(
                min_sharpness=0.6,
                min_brightness=0.7,
                min_contrast=0.6,
                max_noise=0.4,
                min_audio_clarity=0.6,
                min_sync_score=0.7,
                min_narrative_score=0.6
            ),
            description='Optimized for Instagram Reels',
            use_cases=['instagram', 'reels', 'stories']
        ),
        
        'feed': QualityPreset(
            name='Instagram Feed',
            tier=QualityTier.STANDARD,
            video=VideoPreset(
                resolution='1080x1080',  # Square
                fps=30,
                bitrate='4M',
                codec='libx264',
                pixel_format='yuv420p',
                color_space='bt709',
                profile='main',
                preset='fast',
                crf=22
            ),
            audio=AudioPreset(
                sample_rate=44100,
                bitrate='128k',
                channels=2,
                codec='aac',
                normalization=True,
                compression=False,
                noise_reduction=True
            ),
            effects=EffectsPreset(
                enable_transitions=True,
                transition_type='fade',
                transition_duration=0.3,
                enable_color_grading=True,
                color_lut='warm',
                enable_stabilization=False,
                enable_motion_blur=False,
                enable_text_animations=True
            ),
            quality_checks=QualityCheckPreset(
                min_sharpness=0.6,
                min_brightness=0.7,
                min_contrast=0.6,
                max_noise=0.4,
                min_audio_clarity=0.6,
                min_sync_score=0.6,
                min_narrative_score=0.6
            ),
            description='Optimized for Instagram Feed',
            use_cases=['instagram', 'feed', 'square video']
        )
    }
}


class QualityPresetManager:
    """Manager for quality presets - Single Responsibility"""
    
    def __init__(self):
        self.presets = QUALITY_PRESETS
        self.platform_presets = PLATFORM_PRESETS
    
    def get_preset(self, name: str) -> Optional[QualityPreset]:
        """Get preset by name"""
        return self.presets.get(name)
    
    def get_platform_preset(self, platform: Platform, variant: str = 'standard') -> Optional[QualityPreset]:
        """Get platform-specific preset"""
        if platform in self.platform_presets:
            return self.platform_presets[platform].get(variant)
        return None
    
    def get_preset_for_quality_tier(self, tier: QualityTier) -> Optional[QualityPreset]:
        """Get preset for quality tier"""
        for preset in self.presets.values():
            if preset.tier == tier:
                return preset
        return None
    
    def get_recommended_preset(self, 
                             platform: Optional[str] = None,
                             duration: Optional[int] = None,
                             purpose: Optional[str] = None) -> QualityPreset:
        """Get recommended preset based on context"""
        
        # Platform-specific recommendations
        if platform:
            platform_lower = platform.lower()
            if 'youtube' in platform_lower:
                return self.get_platform_preset(Platform.YOUTUBE, 'standard')
            elif 'tiktok' in platform_lower:
                return self.get_platform_preset(Platform.TIKTOK, 'standard')
            elif 'instagram' in platform_lower:
                if duration and duration <= 60:
                    return self.get_platform_preset(Platform.INSTAGRAM, 'reels')
                else:
                    return self.get_platform_preset(Platform.INSTAGRAM, 'feed')
        
        # Purpose-based recommendations
        if purpose:
            purpose_lower = purpose.lower()
            if 'broadcast' in purpose_lower or 'tv' in purpose_lower:
                return self.presets['broadcast']
            elif 'cinema' in purpose_lower or 'film' in purpose_lower:
                return self.presets['cinema']
            elif 'professional' in purpose_lower or 'commercial' in purpose_lower:
                return self.presets['professional']
        
        # Default to standard
        return self.presets['standard']
    
    def create_custom_preset(self, 
                           name: str,
                           base_preset: str,
                           overrides: Dict[str, Any]) -> QualityPreset:
        """Create custom preset based on existing one"""
        base = self.get_preset(base_preset)
        if not base:
            base = self.presets['standard']
        
        # Create copy and apply overrides
        import copy
        custom = copy.deepcopy(base)
        custom.name = name
        
        # Apply overrides
        for key, value in overrides.items():
            if hasattr(custom, key):
                setattr(custom, key, value)
        
        return custom
    
    def get_ffmpeg_params(self, preset: QualityPreset) -> Dict[str, str]:
        """Convert preset to FFmpeg parameters"""
        return {
            'vcodec': preset.video.codec,
            'acodec': preset.audio.codec,
            'r': str(preset.video.fps),
            's': preset.video.resolution,
            'b:v': preset.video.bitrate,
            'b:a': preset.audio.bitrate,
            'ar': str(preset.audio.sample_rate),
            'ac': str(preset.audio.channels),
            'crf': str(preset.video.crf),
            'preset': preset.video.preset,
            'profile:v': preset.video.profile,
            'pix_fmt': preset.video.pixel_format
        }


# Global preset manager instance
quality_preset_manager = QualityPresetManager()