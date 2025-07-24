"""
Data models for video analysis and generation
"""
from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum
from dataclasses import dataclass

class Platform(str, Enum):
    """
    Target destination platforms for video publishing and optimization.

    This represents the social media platform where the generated video will be published.
    The AI agents optimize content, format, duration, and
            style specifically for each platform's:
    - Algorithm preferences
    - Audience behavior patterns
    - Technical requirements (aspect ratio, duration limits)
    - Content policies and trends

    Example: A TikTok video will be optimized for vertical format, trending sounds,
    and quick engagement hooks, while a YouTube video focuses on longer retention
    and search optimization.
    """
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"

class VideoCategory(str, Enum):
    """Video content categories"""
    COMEDY = "Comedy"
    ENTERTAINMENT = "Entertainment"
    EDUCATION = "Education"
    EDUCATIONAL = "Educational"  # Alias for Education
    TECHNOLOGY = "Technology"
    GAMING = "Gaming"
    MUSIC = "Music"
    SPORTS = "Sports"
    NEWS = "News"
    LIFESTYLE = "Lifestyle"
    FOOD = "Food"
    TRAVEL = "Travel"
    FITNESS = "Fitness"
    FASHION = "Fashion"
    SCIENCE = "Science"
    BUSINESS = "Business"
    HEALTH = "Health"
    ARTS = "Arts"
    AUTOMOTIVE = "Automotive"
    PETS = "Pets"
    OTHER = "Other"

class ForceGenerationMode(str, Enum):
    AUTO = "auto"  # Use normal fallback chain
    FORCE_VEO3 = "force_veo3"  # Force VEO-3 only
    FORCE_VEO2 = "force_veo2"  # Force VEO-2 only
    FORCE_IMAGE_GEN = "force_image_gen"  # Force Image Generation only
    FORCE_CONTINUOUS = "force_continuous"  # Force continuous generation (no stopping)

class VideoOrientation(str, Enum):
    PORTRAIT = "portrait"  # 9:16 (TikTok, Instagram Stories)
    LANDSCAPE = "landscape"  # 16:9 (YouTube, traditional video)
    SQUARE = "square"  # 1:1 (Instagram Posts)
    AUTO = "auto"  # Let AI agents decide based on platform

class TrendingVideo(BaseModel):
    """Model for a trending video from any platform"""
    video_id: str
    platform: Platform
    url: HttpUrl
    title: str
    description: Optional[str] = None
    category: VideoCategory
    tags: List[str] = Field(default_factory=list)

    # Metrics
    view_count: int
    like_count: int
    comment_count: int
    share_count: Optional[int] = None

    # Temporal data
    upload_date: datetime
    scraped_at: datetime = Field(default_factory=datetime.now)
    trending_position: Optional[int] = None

    # Creator info
    channel_id: str
    channel_name: str
    channel_subscribers: Optional[int] = None

    # Additional metadata
    duration_seconds: int
    thumbnail_url: Optional[HttpUrl] = None
    has_captions: bool = False
    language: Optional[str] = None

@dataclass
class GeneratedVideoConfig:
    mission: str
    duration_seconds: int
    target_platform: Platform
    category: VideoCategory

    # Session tracking
    session_id: Optional[str] = None

    # Visual and audio settings
    visual_style: str = "cinematic"
    tone: str = "engaging"
    style: str = "professional"
    target_audience: str = "general audience"  # Add target_audience parameter
    
    # Platform alias for backward compatibility
    @property
    def platform(self) -> Platform:
        return self.target_platform

    # Content structure
    hook: Optional[str] = None  # AI-generated, no hardcoded default
    main_content: Optional[List[str]] = None
    call_to_action: Optional[str] = None  # AI-generated, no hardcoded default

    # Visual design parameters
    color_scheme: Optional[List[str]] = None
    text_overlays: Optional[List[Dict]] = None
    transitions: Optional[List[str]] = None

    # Audio parameters
    background_music_style: Optional[str] = None  # AI-generated, no hardcoded default
    voiceover_style: Optional[str] = None  # AI-generated, no hardcoded default
    sound_effects: Optional[List[str]] = None

    # Inspiration and scoring
    inspired_by_videos: Optional[List[str]] = None

    # Technical settings
    use_real_veo2: bool = True
    use_vertex_ai: bool = True
    realistic_audio: bool = True

    # NEW: Force generation options
    force_generation_mode: ForceGenerationMode = ForceGenerationMode.AUTO
    continuous_generation: bool = False  # Keep generating until stopped

    # NEW: Video orientation settings
    video_orientation: VideoOrientation = VideoOrientation.AUTO
    ai_decide_orientation: bool = True  # Let AI agents decide orientation
    
    # NEW: Core decision integration
    num_clips: Optional[int] = None
    clip_durations: Optional[List[float]] = None

    # Advanced settings
    frame_continuity: bool = False
    predicted_viral_score: float = 0.0

    # NEW: Subtitle overlay settings
    use_subtitle_overlays: bool = True  # Use audio-based subtitle overlays instead of generic text overlays

    # Generation mode settings
    image_only_mode: bool = False
    fallback_only: bool = False
    use_image_fallback: bool = True
    images_per_second: int = 2
    cheap_mode: bool = False  # Enable cost-saving mode
    cheap_mode_level: str = "full"  # Granular cheap mode: full, audio, video

    def __post_init__(self):
        if self.main_content is None:
            self.main_content = []
        if self.color_scheme is None:
            self.color_scheme = ["#FF6B6B", "#4ECDC4", "#FFFFFF"]
        if self.text_overlays is None:
            self.text_overlays = []
        if self.transitions is None:
            self.transitions = ["fade", "slide"]
        if self.sound_effects is None:
            self.sound_effects = []
        if self.inspired_by_videos is None:
            self.inspired_by_videos = []

    def get_aspect_ratio(self) -> str:
        """Get aspect ratio based on orientation and platform"""
        if self.video_orientation == VideoOrientation.PORTRAIT:
            return "9:16"
        elif self.video_orientation == VideoOrientation.LANDSCAPE:
            return "16:9"
        elif self.video_orientation == VideoOrientation.SQUARE:
            return "1:1"
        else:  # AUTO
            # Default platform-based aspect ratios
            if self.target_platform == Platform.TIKTOK:
                return "9:16"
            elif self.target_platform == Platform.YOUTUBE:
                return "9:16"  # YouTube Shorts are also 9:16
            elif self.target_platform == Platform.INSTAGRAM:
                return "9:16"  # Instagram Reels are 9:16
            else:
                return "16:9"  # Facebook defaults to landscape

    def get_resolution(self) -> tuple:
        """Get video resolution based on orientation and platform"""
        aspect_ratio = self.get_aspect_ratio()
        if aspect_ratio == "9:16":
            return (1080, 1920)  # Portrait - TikTok, Instagram Reels, YouTube Shorts
        elif aspect_ratio == "16:9":
            return (1920, 1080)  # Landscape - Facebook, traditional video
        elif aspect_ratio == "1:1":
            return (1080, 1080)  # Square - Instagram Posts
        else:
            return (1080, 1920)  # Default to portrait for modern social media

class Narrative(str, Enum):
    """Video narrative/viewpoint options"""
    PRO_AMERICAN_GOVERNMENT = "pro_american_government"
    PRO_SOCCER = "pro_soccer"
    AGAINST_ANIMAL_ABUSE = "against_animal_abuse"
    PRO_ENVIRONMENT = "pro_environment"
    PRO_TECHNOLOGY = "pro_technology"
    PRO_HEALTH = "pro_health"
    PRO_EDUCATION = "pro_education"
    PRO_FAMILY = "pro_family"
    NEUTRAL = "neutral"

class Feeling(str, Enum):
    """Video emotional tone options"""
    SERIOUS = "serious"
    FUNNY = "funny"
    CYNICAL = "cynical"
    INSPIRATIONAL = "inspirational"
    DRAMATIC = "dramatic"
    PLAYFUL = "playful"
    EMOTIONAL = "emotional"
    ENERGETIC = "energetic"
    CALM = "calm"

class Language(str, Enum):
    """Supported languages for multi-language video generation"""
    # English variants
    ENGLISH_US = "en-US"  # American English
    ENGLISH_UK = "en-GB"  # British English
    ENGLISH_IN = "en-IN"  # Indian English

    # European languages
    FRENCH = "fr"
    GERMAN = "de"

    # Middle Eastern languages (RTL support)
    ARABIC = "ar"
    PERSIAN = "fa"  # Persian/Farsi
    HEBREW = "he"

    # Asian languages
    THAI = "th"

    # Additional supported languages
    SPANISH = "es"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    CHINESE = "zh"
    JAPANESE = "ja"

class TTSVoice(str, Enum):
    """TTS voice types for different languages and emotions"""
    # American English voices
    EN_US_MALE_NATURAL = "en-US-male-natural"
    EN_US_FEMALE_NATURAL = "en-US-female-natural"
    EN_US_MALE_WAVENET = "en-US-Wavenet-D"
    EN_US_FEMALE_WAVENET = "en-US-Wavenet-F"

    # British English voices
    EN_GB_MALE_NATURAL = "en-GB-male-natural"
    EN_GB_FEMALE_NATURAL = "en-GB-female-natural"
    EN_GB_MALE_WAVENET = "en-GB-Wavenet-B"
    EN_GB_FEMALE_WAVENET = "en-GB-Wavenet-A"

    # Indian English voices
    EN_IN_MALE_NATURAL = "en-IN-male-natural"
    EN_IN_FEMALE_NATURAL = "en-IN-female-natural"
    EN_IN_MALE_WAVENET = "en-IN-Wavenet-B"
    EN_IN_FEMALE_WAVENET = "en-IN-Wavenet-A"

    # French voices
    FR_MALE_NATURAL = "fr-FR-male-natural"
    FR_FEMALE_NATURAL = "fr-FR-female-natural"
    FR_MALE_WAVENET = "fr-FR-Wavenet-B"
    FR_FEMALE_WAVENET = "fr-FR-Wavenet-A"

    # German voices
    DE_MALE_NATURAL = "de-DE-male-natural"
    DE_FEMALE_NATURAL = "de-DE-female-natural"
    DE_MALE_WAVENET = "de-DE-Wavenet-B"
    DE_FEMALE_WAVENET = "de-DE-Wavenet-A"

    # Arabic voices (RTL)
    AR_MALE_NATURAL = "ar-XA-male-natural"
    AR_FEMALE_NATURAL = "ar-XA-female-natural"
    AR_MALE_WAVENET = "ar-XA-Wavenet-B"
    AR_FEMALE_WAVENET = "ar-XA-Wavenet-A"

    # Persian voices (RTL)
    FA_MALE_NATURAL = "fa-IR-male-natural"
    FA_FEMALE_NATURAL = "fa-IR-female-natural"

    # Hebrew voices (RTL)
    HE_MALE_NATURAL = "he-IL-male-natural"
    HE_FEMALE_NATURAL = "he-IL-female-natural"

    # Thai voices
    TH_MALE_NATURAL = "th-TH-male-natural"
    TH_FEMALE_NATURAL = "th-TH-female-natural"

    # Auto-select based on language and emotion
    AUTO = "auto"

class LanguageVersion(BaseModel):
    """Single language version of a video"""
    language: Language
    language_name: str  # Human-readable name

    # File paths
    audio_path: str
    video_path: str
    subtitle_path: Optional[str] = None

    # Content
    translated_script: str
    translated_overlays: List[Dict[str, Any]]

    # Metadata
    tts_voice_used: str
    word_count: int
    audio_duration: float

    # Generation info
    generated_at: datetime = Field(default_factory=datetime.now)
    translation_model: str = "gemini-2.5-pro"

class MultiLanguageVideo(BaseModel):
    """Multi-language video with shared visual content"""
    base_video_id: str
    master_config: GeneratedVideoConfig

    # Shared visual elements (same for all languages)
    shared_clips_dir: str
    veo2_clips: List[Dict[str, Any]]

    # Language-specific versions
    language_versions: Dict[Language, LanguageVersion] = Field(default_factory=dict)

    # Master metadata
    created_at: datetime = Field(default_factory=datetime.now)
    total_generation_time: float
    master_script: str

    # Statistics
    total_languages: int = Field(default=1)
    primary_language: Language
    supported_languages: List[Language] = Field(default_factory=list)

@dataclass
class VideoAnalysis:
    video_id: str
    analysis_timestamp: datetime
    content_score: float
    engagement_prediction: float
    viral_potential: float
    platform_optimization: Dict[str, float]
    recommended_improvements: List[str]
    ai_confidence: float

@dataclass
class GeneratedVideo:
    video_id: str
    config: GeneratedVideoConfig
    file_path: str
    file_size_mb: float
    generation_time_seconds: float
    ai_models_used: List[str]
    script: str
    scene_descriptions: List[str]
    audio_transcript: str
    analysis: Optional[VideoAnalysis] = None

    # NEW: Generation method tracking
    generation_method_used: str = "auto"
    clips_generated: int = 0
    fallback_clips: int = 0

    @property
    def success_rate(self) -> float:
        """Calculate success rate of video generation"""
        if self.clips_generated == 0:
            return 0.0
        return (self.clips_generated - self.fallback_clips) / self.clips_generated

class VideoPerformance(BaseModel):
    """Track performance of published videos"""
    video_id: str
    platform: Platform

    # Metrics over time
    metrics_history: List[Dict[str, Any]]  # Timestamp, views, likes, etc.

    # Calculated metrics
    growth_rate: float
    peak_hour: Optional[int] = None
    viral_achieved: bool = False
    viral_achieved_at: Optional[datetime] = None

    # Comparison with predictions
    predicted_viral_score: float
    actual_viral_score: float
    prediction_accuracy: float

    # Learnings
    success_factors: List[str]
    failure_factors: List[str]
    recommendations: List[str]
