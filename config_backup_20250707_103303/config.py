"""
Configuration for Viral Video Generator
"""
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Project paths
    project_root: Path = Path(__file__).parent.parent
    data_dir: Path = project_root / "data"
    output_dir: Path = project_root / "outputs"
    local_storage_dir: Path = project_root / "outputs" / "videos"
    
    # Storage Configuration
    use_local_storage: bool = Field(default=True, env="USE_LOCAL_STORAGE")
    
    # Google Cloud Configuration (Optional - only needed if use_local_storage=False)
    gcp_project_id: Optional[str] = Field(default=None, env="GCP_PROJECT_ID")
    gcp_region: str = Field(default="us-central1", env="GCP_REGION")
    gcs_bucket_name: Optional[str] = Field(default=None, env="GCS_BUCKET_NAME")
    
    # Google AI Studio / Gemini - Multi-model configuration
    google_api_key: str = Field(..., env="GOOGLE_API_KEY")
    gemini_script_model: str = Field(default="gemini-2.5-flash", env="GEMINI_SCRIPT_MODEL")
    gemini_refinement_model: str = Field(default="gemini-2.5-pro", env="GEMINI_REFINEMENT_MODEL")
    veo_model: str = Field(default="veo-2", env="VEO_MODEL")
    
    # Backward compatibility
    gemini_model: str = Field(default="gemini-2.5-flash", env="GEMINI_MODEL")
    
    # YouTube API (Optional - will use mock data if not available)
    youtube_api_key: Optional[str] = Field(default=None, env="YOUTUBE_API_KEY")
    youtube_api_version: str = "v3"
    max_results_per_query: int = 50
    use_mock_youtube_data: bool = Field(default=True, env="USE_MOCK_YOUTUBE_DATA")
    
    # Firestore Collections (for local JSON storage when use_local_storage=True)
    firestore_videos_collection: str = "analyzed_videos"
    firestore_generated_collection: str = "generated_videos"
    firestore_analytics_collection: str = "video_analytics"
    
    # BigQuery Datasets (not used in local mode)
    bigquery_dataset: str = "viral_video_analytics"
    bigquery_trending_table: str = "trending_videos"
    bigquery_performance_table: str = "video_performance"
    
    # Video Generation Settings - Configurable Duration
    video_duration_seconds: int = Field(default=30, env="VIDEO_DURATION")
    video_fps: int = 30
    video_resolution: tuple = (1080, 1920)  # Vertical format for shorts
    supported_platforms: List[str] = ["youtube", "tiktok", "instagram", "facebook"]
    
    # Scraping Settings
    scraping_interval_hours: int = Field(default=6, env="SCRAPING_INTERVAL")
    trending_categories: List[str] = [
        "Music", "Gaming", "Entertainment", "Comedy", 
        "Education", "Technology", "Sports", "News"
    ]
    
    # Analysis Settings
    min_views_threshold: int = 10000
    viral_velocity_threshold: float = 0.8  # Views per hour threshold
    comment_sample_size: int = 100
    
    # Redis Configuration (for Celery)
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # API Settings
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    
    # Video generation settings with proper annotations
    video_duration_override: int = Field(default_factory=lambda: int(os.getenv('VIDEO_DURATION', 30)))
    output_dir_override: str = Field(default_factory=lambda: os.getenv('OUTPUT_DIR', 'outputs'))
    
    # Veo-2 Configuration
    use_real_veo2_override: bool = Field(default_factory=lambda: os.getenv('USE_REAL_VEO2', 'false').lower() == 'true')
    veo2_model_override: str = Field(default_factory=lambda: os.getenv('VEO2_MODEL', 'veo-2.0-generate-001'))
    
    # API Keys  
    gemini_api_key_override: Optional[str] = Field(default_factory=lambda: os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY'))
    
    # Logging configuration
    
    @validator('youtube_api_key')
    def validate_youtube_key(cls, v):
        """Make YouTube API key optional - use mock data if not provided"""
        return v
    
    @validator('gcp_project_id')
    def validate_gcp_config(cls, v, values):
        """Validate GCP configuration only if not using local storage"""
        use_local = values.get('use_local_storage', True)
        if not use_local and not v:
            raise ValueError("GCP_PROJECT_ID is required when use_local_storage=False")
        return v
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        self.data_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        self.local_storage_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for local storage
        (self.local_storage_dir / "raw").mkdir(exist_ok=True)
        (self.local_storage_dir / "generated").mkdir(exist_ok=True)
        (self.data_dir / "metadata").mkdir(exist_ok=True)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"  # Allow extra fields from environment variables

# Create settings instance
settings = Settings() 