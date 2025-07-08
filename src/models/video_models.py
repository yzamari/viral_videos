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
    The AI agents optimize content, format, duration, and style specifically for each platform's:
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
    topic: str
    duration_seconds: int
    target_platform: Platform
    category: VideoCategory
    
    # Visual and audio settings
    visual_style: str = "cinematic"
    tone: str = "engaging"
    style: str = "professional"
    
    # Content structure
    hook: str = "Amazing content ahead!"
    main_content: Optional[List[str]] = None
    call_to_action: str = "Subscribe for more!"
    
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
    
    # Advanced settings
    frame_continuity: bool = False
    predicted_viral_score: float = 0.0
    
    def __post_init__(self):
        if self.main_content is None:
            self.main_content = []
    
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
                return "16:9"
            elif self.target_platform == Platform.INSTAGRAM:
                return "1:1"
            else:
                return "16:9"  # Default landscape
    
    def get_resolution(self) -> tuple:
        """Get video resolution based on orientation"""
        aspect_ratio = self.get_aspect_ratio()
        if aspect_ratio == "9:16":
            return (1080, 1920)  # Portrait
        elif aspect_ratio == "16:9":
            return (1920, 1080)  # Landscape
        elif aspect_ratio == "1:1":
            return (1080, 1080)  # Square
        else:
            return (1920, 1080)  # Default landscape

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
    ENGLISH = "en"
    ARABIC = "ar"
    HEBREW = "he"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    CHINESE = "zh"
    JAPANESE = "ja"

class TTSVoice(str, Enum):
    """TTS voice types for different languages and emotions"""
    # English voices
    EN_US_MALE_NATURAL = "en-US-male-natural"
    EN_US_FEMALE_NATURAL = "en-US-female-natural"
    EN_UK_MALE_NATURAL = "en-UK-male-natural"
    EN_UK_FEMALE_NATURAL = "en-UK-female-natural"
    
    # Arabic voices
    AR_MALE_NATURAL = "ar-male-natural"
    AR_FEMALE_NATURAL = "ar-female-natural"
    
    # Hebrew voices
    HE_MALE_NATURAL = "he-male-natural"
    HE_FEMALE_NATURAL = "he-female-natural"
    
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