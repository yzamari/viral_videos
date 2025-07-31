"""Content Models for News Aggregator"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from enum import Enum, auto
import hashlib


class SourceType(Enum):
    """Types of content sources"""
    TELEGRAM = "telegram"
    RSS = "rss"
    WEB = "web"
    SOCIAL_MEDIA = "social_media"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    REDDIT = "reddit"


class AssetType(Enum):
    """Types of media assets"""
    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"
    GIF = "gif"
    DOCUMENT = "document"


class ContentStatus(Enum):
    """Status of content items"""
    SCRAPED = "scraped"
    PROCESSED = "processed"
    SUMMARIZED = "summarized"
    TRANSLATED = "translated"
    COMPOSED = "composed"
    PUBLISHED = "published"
    FAILED = "failed"


@dataclass
class ScrapingConfig:
    """Configuration for content scraping"""
    max_items: int = 100
    time_window_hours: int = 24
    include_media: bool = True
    min_media_quality: int = 720  # minimum resolution for videos
    languages: List[str] = field(default_factory=lambda: ["en"])
    keywords: List[str] = field(default_factory=list)
    exclude_keywords: List[str] = field(default_factory=list)
    custom_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NewsSource:
    """Represents a news/content source"""
    id: str
    name: str
    source_type: SourceType
    url: str
    credentials: Optional[Dict[str, str]] = None
    scraping_config: ScrapingConfig = field(default_factory=ScrapingConfig)
    last_scraped: Optional[datetime] = None
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.id:
            # Generate ID from source info
            content = f"{self.source_type.value}:{self.url}"
            self.id = hashlib.md5(content.encode()).hexdigest()[:8]


@dataclass
class TimeSegment:
    """Represents a time segment in media"""
    start_time: float  # seconds
    end_time: float
    confidence: float = 1.0
    description: str = ""
    tags: List[str] = field(default_factory=list)
    
    @property
    def duration(self) -> float:
        return self.end_time - self.start_time


@dataclass
class MediaAsset:
    """Represents a media asset (video, image, audio)"""
    id: str
    asset_type: AssetType
    source_url: str
    local_path: Optional[str] = None
    duration: Optional[float] = None  # seconds, for video/audio
    dimensions: Optional[Tuple[int, int]] = None  # width, height
    file_size: Optional[int] = None  # bytes
    format: Optional[str] = None  # mp4, jpg, etc.
    quality_score: float = 0.0  # 0-1 quality assessment
    interesting_segments: List[TimeSegment] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    processed: bool = False
    
    def __post_init__(self):
        if not self.id:
            self.id = hashlib.md5(self.source_url.encode()).hexdigest()[:12]
    
    def get_best_segment(self, max_duration: Optional[float] = None) -> Optional[TimeSegment]:
        """Get the most interesting segment within duration limit"""
        if not self.interesting_segments:
            return None
        
        valid_segments = self.interesting_segments
        if max_duration:
            valid_segments = [s for s in valid_segments if s.duration <= max_duration]
        
        if not valid_segments:
            return None
            
        return max(valid_segments, key=lambda s: s.confidence)


@dataclass
class ContentItem:
    """Represents a piece of content (article, post, etc.)"""
    id: str
    source: NewsSource
    title: str
    content: str
    summary: Optional[str] = None
    media_assets: List[MediaAsset] = field(default_factory=list)
    published_date: datetime = field(default_factory=datetime.now)
    scraped_date: datetime = field(default_factory=datetime.now)
    language: str = "en"
    author: Optional[str] = None
    url: Optional[str] = None
    status: ContentStatus = ContentStatus.SCRAPED
    relevance_score: float = 0.0  # 0-1 relevance to topic
    sentiment_score: float = 0.0  # -1 to 1 sentiment
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    translations: Dict[str, Dict[str, str]] = field(default_factory=dict)  # lang -> {title, content, summary}
    
    def __post_init__(self):
        if not self.id:
            content = f"{self.source.id}:{self.title}:{self.published_date}"
            self.id = hashlib.md5(content.encode()).hexdigest()[:12]
    
    def get_translation(self, language: str) -> Dict[str, str]:
        """Get translated content for a language"""
        if language == self.language:
            return {
                "title": self.title,
                "content": self.content,
                "summary": self.summary or self.content[:200]
            }
        return self.translations.get(language, {})
    
    def has_video(self) -> bool:
        """Check if content has video assets"""
        return any(asset.asset_type == AssetType.VIDEO for asset in self.media_assets)
    
    def has_images(self) -> bool:
        """Check if content has image assets"""
        return any(asset.asset_type == AssetType.IMAGE for asset in self.media_assets)
    
    def get_primary_media(self) -> Optional[MediaAsset]:
        """Get the primary media asset (prefer video over image)"""
        videos = [a for a in self.media_assets if a.asset_type == AssetType.VIDEO]
        if videos:
            return max(videos, key=lambda v: v.quality_score)
        
        images = [a for a in self.media_assets if a.asset_type == AssetType.IMAGE]
        if images:
            return max(images, key=lambda i: i.quality_score)
        
        return None


@dataclass
class ContentCollection:
    """Collection of related content items"""
    id: str
    name: str
    description: str
    items: List[ContentItem] = field(default_factory=list)
    created_date: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_item(self, item: ContentItem):
        """Add content item to collection"""
        if item not in self.items:
            self.items.append(item)
    
    def get_by_source(self, source_type: SourceType) -> List[ContentItem]:
        """Get items from specific source type"""
        return [item for item in self.items if item.source.source_type == source_type]
    
    def get_by_date_range(self, start: datetime, end: datetime) -> List[ContentItem]:
        """Get items within date range"""
        return [item for item in self.items 
                if start <= item.published_date <= end]
    
    def get_top_items(self, n: int = 5, by: str = "relevance") -> List[ContentItem]:
        """Get top N items by specified criteria"""
        if by == "relevance":
            return sorted(self.items, key=lambda x: x.relevance_score, reverse=True)[:n]
        elif by == "date":
            return sorted(self.items, key=lambda x: x.published_date, reverse=True)[:n]
        elif by == "sentiment":
            return sorted(self.items, key=lambda x: x.sentiment_score, reverse=True)[:n]
        else:
            return self.items[:n]