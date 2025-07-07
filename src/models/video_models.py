"""
Data models for video analysis and generation
"""
from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum

class Platform(str, Enum):
    """Supported social media platforms"""
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"

class VideoCategory(str, Enum):
    """Video content categories"""
    MUSIC = "Music"
    GAMING = "Gaming"
    ENTERTAINMENT = "Entertainment"
    COMEDY = "Comedy"
    EDUCATION = "Education"
    TECHNOLOGY = "Technology"
    SPORTS = "Sports"
    NEWS = "News"
    LIFESTYLE = "Lifestyle"
    OTHER = "Other"

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

class VideoAnalysis(BaseModel):
    """Analysis results for a trending video"""
    video_id: str
    platform: Platform
    analyzed_at: datetime = Field(default_factory=datetime.now)
    
    # Content analysis
    content_themes: List[str]
    emotional_tone: str
    target_audience: str
    key_moments: List[Dict[str, Any]]
    
    # Viral factors
    viral_score: float = Field(ge=0, le=1)  # 0-1 score
    viral_velocity: float  # Views per hour
    engagement_rate: float  # (likes + comments + shares) / views
    
    # Title and description analysis
    title_keywords: List[str]
    title_sentiment: str
    hook_analysis: str
    cta_present: bool
    
    # Comment analysis
    comment_themes: List[str]
    comment_sentiment: Dict[str, float]  # positive, negative, neutral percentages
    top_comments: List[str]
    
    # Technical analysis
    video_quality: str
    editing_style: str
    music_genre: Optional[str] = None
    speech_pace: Optional[str] = None
    
    # Recommendations
    success_factors: List[str]
    improvement_suggestions: List[str]

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

class GeneratedVideoConfig(BaseModel):
    """Configuration for generating a new video"""
    target_platform: Platform
    category: VideoCategory
    duration_seconds: int = 30
    
    # NEW: Narrative and feeling inputs
    narrative: Narrative = Narrative.NEUTRAL
    feeling: Feeling = Feeling.FUNNY
    
    # NEW: Multi-language support
    primary_language: Language = Language.ENGLISH
    additional_languages: List[Language] = Field(default_factory=list)
    tts_voice: TTSVoice = TTSVoice.AUTO
    
    # NEW: Frame continuity for seamless video generation
    frame_continuity: bool = False
    
    # NEW: Fallback-only mode for testing without VEO2/VEO3
    fallback_only: bool = False
    
    # NEW: Image-only mode and use-image fallback
    image_only_mode: bool = False
    use_image_fallback: bool = True
    
    # NEW: Number of images per second for image mode
    images_per_second: int = 2
    
    # Content specifications
    topic: str
    style: str
    tone: str
    target_audience: str
    
    # Script elements
    hook: str
    main_content: List[str]
    call_to_action: str
    
    # Visual elements
    visual_style: str
    color_scheme: List[str]
    text_overlays: List[Dict[str, Any]]
    transitions: List[str]
    
    # Audio elements
    background_music_style: str
    voiceover_style: Optional[str] = None
    sound_effects: List[str] = Field(default_factory=list)
    
    # Based on analysis
    inspired_by_videos: List[str]  # Video IDs that inspired this config
    predicted_viral_score: float

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

class GeneratedVideo(BaseModel):
    """Model for a generated video"""
    video_id: str
    config: GeneratedVideoConfig
    
    # File information
    file_path: str
    gcs_url: Optional[HttpUrl] = None
    file_size_mb: float
    
    # Generation metadata
    generated_at: datetime = Field(default_factory=datetime.now)
    generation_time_seconds: float
    ai_models_used: List[str]
    
    # Content details
    script: str
    scene_descriptions: List[str]
    audio_transcript: Optional[str] = None
    
    # Publishing status
    published: bool = False
    published_at: Optional[datetime] = None
    published_urls: Dict[Platform, HttpUrl] = Field(default_factory=dict)
    
    # Performance tracking
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)

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