"""
Configuration management for the viral video generator
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with comprehensive environment variable support"""

    # Core API Keys
    google_api_key: str = ""
    gemini_api_key: str = ""
    openai_api_key: str = ""
    elevenlabs_api_key: str = ""

    # Google Cloud Configuration
    google_cloud_project_id: str = "viralgen-464411"
    google_cloud_location: str = "us-central1"
    google_application_credentials: Optional[str] = None

    # VEO Video Generation
    veo_project_id: str = "viralgen-464411"
    veo_location: str = "us-central1"
    use_real_veo2: bool = True
    veo_fallback_enabled: bool = True
    force_veo_only: bool = False  # NEW: Force VEO-only, no fallbacks
    prefer_google_ai_veo: bool = True  # NEW: Prefer Google AI Studio VEO over Vertex AI
    disable_veo3: bool = False  # NEW: Disable VEO3 completely (force VEO2 only)
    disable_veo2: bool = True  # NEW: Disable VEO2 completely
    prefer_veo2_over_veo3: bool = False  # NEW: Always prefer VEO2 over VEO3
    prefer_veo3_fast: bool = True  # NEW: Prefer VEO3-fast model ($0.25/second)
    veo_model_preference_order: str = "veo3-fast"  # NEW: Only VEO3-fast is allowed

    # Google Cloud TTS Configuration
    google_tts_voice_type: str = "en-US-Neural2-F"
    google_tts_enabled: bool = True
    google_tts_fallback_to_gtts: bool = True

    # Audio Generation Settings
    default_audio_feeling: str = "excited"
    default_audio_narrative: str = "energetic"
    audio_sample_rate: int = 24000
    audio_effects_profile: str = "headphone-class-device"

    # Video Generation Settings
    default_video_duration: int = 15
    default_platform: str = "youtube"
    default_category: str = "Comedy"
    default_frame_continuity: bool = True

    # AI Agent Discussion Settings
    default_discussion_mode: str = "standard"
    max_discussion_rounds: int = 3
    discussion_consensus_threshold: float = 0.5
    discussion_timeout_seconds: int = 60
    enable_discussion_logging: bool = True

    # Agent Configuration
    total_ai_agents: int = 25
    discussion_phases: int = 5
    enable_enhanced_orchestration: bool = True

    # Output Settings
    output_directory: str = "outputs"
    clips_directory: str = "clips"
    logs_directory: str = "logs"
    enable_comprehensive_logging: bool = True

    # Performance Settings
    max_concurrent_generations: int = 3
    video_render_threads: int = 4
    audio_processing_threads: int = 2

    # Development Settings
    debug_mode: bool = False
    verbose_logging: bool = False
    enable_performance_metrics: bool = True
    cleanup_temp_files: bool = True

    # Platform Specific Settings
    youtube_shorts_aspect_ratio: str = "9:16"
    tiktok_max_duration: int = 60
    instagram_reels_max_duration: int = 90
    twitter_video_max_duration: int = 140

    # Quality Settings
    video_quality: str = "high"
    audio_quality: str = "high"
    compression_level: str = "medium"
    target_file_size_mb: int = 50

    # Backup and Fallback Settings
    enable_fallback_generation: bool = True
    fallback_to_placeholder: bool = True
    backup_sessions: bool = True
    auto_retry_failed_generations: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

        # Environment variable prefixes
        env_prefix = ""

        # Allow extra fields for flexibility
        extra = "allow"


# Create global settings instance
settings = Settings()

# Backward compatibility - ensure google_api_key is set
if not settings.google_api_key and settings.gemini_api_key:
    settings.google_api_key = settings.gemini_api_key

# Validate critical settings
if not settings.google_api_key:
    print("⚠️ Warning: GOOGLE_API_KEY not set in environment variables")

# Export commonly used settings
PROJECT_ID = settings.veo_project_id
LOCATION = settings.veo_location
GOOGLE_API_KEY = settings.google_api_key
USE_REAL_VEO2 = settings.use_real_veo2
GOOGLE_TTS_ENABLED = settings.google_tts_enabled

# Gemini Configuration
# Latest model with excellent quota
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
# Use same model for consistency
GEMINI_FALLBACK_MODEL = os.getenv('GEMINI_FALLBACK_MODEL', 'gemini-2.5-flash')
