"""
JSON-Based Prompt System for VEO2/VEO3 and Image Generation
Provides structured, predictable, and powerful control over AI generation
"""

from typing import Dict, Any, List, Optional, Union
from enum import Enum
from dataclasses import dataclass, field, asdict
import json
from datetime import datetime

# Import existing models
try:
    from ..models.video_models import Platform
    from ..utils.logging_config import get_logger
except ImportError:
    from models.video_models import Platform
    from utils.logging_config import get_logger

logger = get_logger(__name__)


class GeneratorType(Enum):
    """Supported AI generators"""
    VEO2 = "veo2"
    VEO3 = "veo3"
    IMAGEN = "imagen"
    

class CameraMovement(Enum):
    """Standard camera movements"""
    STATIC = "static"
    PAN_LEFT = "pan_left"
    PAN_RIGHT = "pan_right"
    TILT_UP = "tilt_up"
    TILT_DOWN = "tilt_down"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    DOLLY_IN = "dolly_in"
    DOLLY_OUT = "dolly_out"
    ORBIT = "orbit"
    TRACKING = "tracking"
    HANDHELD = "handheld"
    STEADICAM = "steadicam"
    CRANE = "crane"
    DRONE = "drone"


class ShotType(Enum):
    """Standard shot types"""
    EXTREME_WIDE = "extreme_wide_shot"
    WIDE = "wide_shot"
    MEDIUM_WIDE = "medium_wide_shot"
    MEDIUM = "medium_shot"
    MEDIUM_CLOSE = "medium_close_shot"
    CLOSE = "close_shot"
    EXTREME_CLOSE = "extreme_close_shot"
    OVER_SHOULDER = "over_shoulder"
    POV = "point_of_view"
    AERIAL = "aerial"
    LOW_ANGLE = "low_angle"
    HIGH_ANGLE = "high_angle"
    DUTCH_ANGLE = "dutch_angle"


class LightingStyle(Enum):
    """Lighting presets"""
    NATURAL = "natural"
    STUDIO = "studio"
    DRAMATIC = "dramatic"
    SOFT = "soft"
    HARD = "hard"
    GOLDEN_HOUR = "golden_hour"
    BLUE_HOUR = "blue_hour"
    NIGHT = "night"
    NEON = "neon"
    CINEMATIC = "cinematic"
    HIGH_KEY = "high_key"
    LOW_KEY = "low_key"
    SILHOUETTE = "silhouette"


class VisualStyle(Enum):
    """Visual style presets"""
    REALISTIC = "realistic"
    CINEMATIC = "cinematic"
    DOCUMENTARY = "documentary"
    ANIMATION = "animation"
    CARTOON = "cartoon"
    ANIME = "anime"
    RETRO = "retro"
    FUTURISTIC = "futuristic"
    MINIMALIST = "minimalist"
    VINTAGE = "vintage"
    NOIR = "noir"
    VIBRANT = "vibrant"
    MUTED = "muted"
    DREAMY = "dreamy"


@dataclass
class CameraConfig:
    """Camera configuration"""
    shot_type: ShotType = ShotType.MEDIUM
    movement: CameraMovement = CameraMovement.STATIC
    lens: str = "50mm"
    aperture: str = "f/2.8"
    frame_rate: str = "24fps"
    camera_model: Optional[str] = None
    speed: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with enum values as strings"""
        return {
            "shot_type": self.shot_type.value,
            "movement": self.movement.value,
            "lens": self.lens,
            "aperture": self.aperture,
            "frame_rate": self.frame_rate,
            "camera_model": self.camera_model,
            "speed": self.speed
        }


@dataclass
class LightingConfig:
    """Lighting configuration"""
    style: LightingStyle = LightingStyle.NATURAL
    mood: str = "neutral"
    key_light: Optional[str] = None
    fill_light: Optional[str] = None
    color_temperature: Optional[str] = None
    shadows: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "style": self.style.value,
            "mood": self.mood,
            "key_light": self.key_light,
            "fill_light": self.fill_light,
            "color_temperature": self.color_temperature,
            "shadows": self.shadows
        }


@dataclass
class SubjectConfig:
    """Subject/character configuration"""
    description: str
    wardrobe: Optional[str] = None
    pose: Optional[str] = None
    expression: Optional[str] = None
    action: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SceneConfig:
    """Scene/environment configuration"""
    location: str
    time_of_day: str = "day"
    weather: Optional[str] = None
    environment_details: Optional[str] = None
    props: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EffectsConfig:
    """Visual effects configuration"""
    color_grading: Optional[str] = None
    film_grain: Optional[str] = None
    blur_type: Optional[str] = None
    vignette: Optional[bool] = None
    lens_flare: Optional[bool] = None
    particles: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class TransitionConfig:
    """Transition configuration for video segments"""
    type: str = "cut"
    duration: float = 0.0
    easing: str = "linear"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AudioCueConfig:
    """Audio cue for synchronization"""
    time: float
    event: str
    intensity: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SegmentConfig:
    """Individual segment configuration"""
    duration: float
    description: str
    camera: Optional[CameraConfig] = None
    subject: Optional[SubjectConfig] = None
    scene: Optional[SceneConfig] = None
    transition: Optional[TransitionConfig] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "duration": self.duration,
            "description": self.description
        }
        if self.camera:
            result["camera"] = self.camera.to_dict()
        if self.subject:
            result["subject"] = self.subject.to_dict()
        if self.scene:
            result["scene"] = self.scene.to_dict()
        if self.transition:
            result["transition"] = self.transition.to_dict()
        return result


@dataclass
class VEOJsonPrompt:
    """Complete JSON prompt for VEO generation"""
    # Required fields
    description: str
    style: Union[VisualStyle, str]
    duration: float
    
    # Optional configurations
    camera: Optional[CameraConfig] = None
    lighting: Optional[LightingConfig] = None
    subject: Optional[SubjectConfig] = None
    scene: Optional[SceneConfig] = None
    effects: Optional[EffectsConfig] = None
    
    # Multi-segment support
    segments: List[SegmentConfig] = field(default_factory=list)
    
    # Platform-specific
    platform: Platform = Platform.INSTAGRAM
    aspect_ratio: str = "9:16"
    
    # Advanced
    audio_cues: List[AudioCueConfig] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    
    # Metadata
    template: Optional[str] = None
    version: str = "1.0"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary suitable for JSON serialization"""
        result = {
            "description": self.description,
            "style": self.style.value if isinstance(self.style, VisualStyle) else self.style,
            "duration": self.duration,
            "platform": self.platform.value,
            "aspect_ratio": self.aspect_ratio,
            "version": self.version,
            "created_at": self.created_at
        }
        
        # Add optional configurations
        if self.camera:
            result["camera"] = self.camera.to_dict()
        if self.lighting:
            result["lighting"] = self.lighting.to_dict()
        if self.subject:
            result["subject"] = self.subject.to_dict()
        if self.scene:
            result["scene"] = self.scene.to_dict()
        if self.effects:
            result["effects"] = self.effects.to_dict()
        
        # Add lists
        if self.segments:
            result["segments"] = [seg.to_dict() for seg in self.segments]
        if self.audio_cues:
            result["audio_cues"] = [cue.to_dict() for cue in self.audio_cues]
        if self.keywords:
            result["keywords"] = self.keywords
        if self.constraints:
            result["constraints"] = self.constraints
        
        if self.template:
            result["template"] = self.template
            
        return result
    
    def to_json(self, pretty: bool = True) -> str:
        """Convert to JSON string"""
        if pretty:
            return json.dumps(self.to_dict(), indent=2)
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VEOJsonPrompt':
        """Create from dictionary"""
        # Convert string enums back to enum types
        if isinstance(data.get('style'), str):
            try:
                data['style'] = VisualStyle(data['style'])
            except ValueError:
                pass  # Keep as string if not a valid enum
        
        if isinstance(data.get('platform'), str):
            data['platform'] = Platform(data['platform'])
        
        # Convert nested configs
        if data.get('camera'):
            data['camera'] = CameraConfig(**data['camera'])
        if data.get('lighting'):
            data['lighting'] = LightingConfig(**data['lighting'])
        if data.get('subject'):
            data['subject'] = SubjectConfig(**data['subject'])
        if data.get('scene'):
            data['scene'] = SceneConfig(**data['scene'])
        if data.get('effects'):
            data['effects'] = EffectsConfig(**data['effects'])
        
        # Convert lists
        if data.get('segments'):
            data['segments'] = [SegmentConfig(**seg) for seg in data['segments']]
        if data.get('audio_cues'):
            data['audio_cues'] = [AudioCueConfig(**cue) for cue in data['audio_cues']]
        
        return cls(**data)


class JSONPromptValidator:
    """Validate and enhance JSON prompts"""
    
    @staticmethod
    def validate(prompt: VEOJsonPrompt, target: GeneratorType) -> tuple[bool, List[str]]:
        """Validate prompt for target generator"""
        errors = []
        
        # Basic validation
        if not prompt.description:
            errors.append("Description is required")
        
        if prompt.duration <= 0:
            errors.append("Duration must be positive")
        
        # Generator-specific validation
        if target == GeneratorType.VEO2:
            if prompt.duration > 60:
                errors.append("VEO2 supports max 60 seconds")
        elif target == GeneratorType.VEO3:
            if prompt.duration > 120:
                errors.append("VEO3 supports max 120 seconds")
        
        # Segment validation
        if prompt.segments:
            total_segment_duration = sum(seg.duration for seg in prompt.segments)
            if abs(total_segment_duration - prompt.duration) > 0.1:
                errors.append(f"Segment durations ({total_segment_duration}s) don't match total duration ({prompt.duration}s)")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def enhance(prompt: VEOJsonPrompt, platform: Platform) -> VEOJsonPrompt:
        """Enhance prompt with platform-specific defaults"""
        # Set aspect ratio based on platform
        if platform == Platform.INSTAGRAM:
            prompt.aspect_ratio = "9:16"
            if not prompt.keywords:
                prompt.keywords = ["instagram", "reels", "viral"]
        elif platform == Platform.TIKTOK:
            prompt.aspect_ratio = "9:16"
            if not prompt.keywords:
                prompt.keywords = ["tiktok", "fyp", "trending"]
        elif platform == Platform.YOUTUBE:
            prompt.aspect_ratio = "16:9"
            if not prompt.keywords:
                prompt.keywords = ["youtube", "hd", "cinematic"]
        
        # Add default camera if not specified
        if not prompt.camera:
            prompt.camera = CameraConfig()
        
        # Add default lighting if not specified
        if not prompt.lighting:
            prompt.lighting = LightingConfig()
        
        return prompt


class JSONPromptTemplates:
    """Pre-built templates for common scenarios"""
    
    @staticmethod
    def product_reveal(product_name: str, brand: str, duration: float = 15.0) -> VEOJsonPrompt:
        """Product reveal template"""
        return VEOJsonPrompt(
            description=f"Cinematic product reveal of {brand} {product_name}",
            style=VisualStyle.CINEMATIC,
            duration=duration,
            camera=CameraConfig(
                shot_type=ShotType.CLOSE,
                movement=CameraMovement.ORBIT,
                lens="85mm",
                aperture="f/1.8"
            ),
            lighting=LightingConfig(
                style=LightingStyle.STUDIO,
                mood="luxurious",
                key_light="soft box from right",
                fill_light="reflector from left"
            ),
            effects=EffectsConfig(
                color_grading="warm and rich",
                lens_flare=True,
                film_grain="subtle"
            ),
            keywords=["product", "reveal", "commercial", "professional"],
            template="product_reveal"
        )
    
    @staticmethod
    def educational(topic: str, duration: float = 30.0) -> VEOJsonPrompt:
        """Educational content template"""
        return VEOJsonPrompt(
            description=f"Clear educational explanation of {topic}",
            style=VisualStyle.DOCUMENTARY,
            duration=duration,
            camera=CameraConfig(
                shot_type=ShotType.MEDIUM,
                movement=CameraMovement.STATIC,
                frame_rate="30fps"
            ),
            lighting=LightingConfig(
                style=LightingStyle.NATURAL,
                mood="bright and clear"
            ),
            keywords=["educational", "informative", "clear", "professional"],
            constraints=["no distracting elements", "clear visuals", "readable text"],
            template="educational"
        )
    
    @staticmethod
    def viral_hook(hook_text: str, platform: Platform) -> VEOJsonPrompt:
        """Viral hook template"""
        return VEOJsonPrompt(
            description=f"Attention-grabbing viral hook: {hook_text}",
            style=VisualStyle.VIBRANT,
            duration=3.0,
            platform=platform,
            camera=CameraConfig(
                shot_type=ShotType.CLOSE,
                movement=CameraMovement.ZOOM_IN,
                speed="fast"
            ),
            lighting=LightingConfig(
                style=LightingStyle.NEON,
                mood="energetic"
            ),
            effects=EffectsConfig(
                color_grading="high saturation",
                lens_flare=True
            ),
            keywords=["viral", "hook", "attention", "trending"],
            template="viral_hook"
        )


# Example usage
if __name__ == "__main__":
    # Create a complex multi-segment prompt
    prompt = VEOJsonPrompt(
        description="A day in the life of a software developer",
        style=VisualStyle.CINEMATIC,
        duration=30.0,
        platform=Platform.INSTAGRAM,
        segments=[
            SegmentConfig(
                duration=5.0,
                description="Morning routine with coffee",
                camera=CameraConfig(
                    shot_type=ShotType.CLOSE,
                    movement=CameraMovement.HANDHELD
                ),
                scene=SceneConfig(
                    location="modern kitchen",
                    time_of_day="early morning",
                    props=["coffee machine", "laptop", "notebook"]
                )
            ),
            SegmentConfig(
                duration=10.0,
                description="Coding session with multiple monitors",
                camera=CameraConfig(
                    shot_type=ShotType.MEDIUM,
                    movement=CameraMovement.DOLLY_IN
                ),
                scene=SceneConfig(
                    location="home office",
                    environment_details="clean desk setup with RGB lighting"
                )
            ),
            SegmentConfig(
                duration=10.0,
                description="Video call with team",
                camera=CameraConfig(
                    shot_type=ShotType.OVER_SHOULDER,
                    movement=CameraMovement.STATIC
                )
            ),
            SegmentConfig(
                duration=5.0,
                description="Evening wind down",
                camera=CameraConfig(
                    shot_type=ShotType.WIDE,
                    movement=CameraMovement.PAN_LEFT
                ),
                scene=SceneConfig(
                    location="living room",
                    time_of_day="golden hour"
                )
            )
        ],
        keywords=["developer", "coding", "tech", "lifestyle", "productivity"]
    )
    
    # Validate
    valid, errors = JSONPromptValidator.validate(prompt, GeneratorType.VEO2)
    print(f"Valid: {valid}, Errors: {errors}")
    
    # Convert to JSON
    print(prompt.to_json())