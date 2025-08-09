"""
Interface definitions for the News Aggregator components following SOLID principles.

This module defines the contracts that each component must implement,
enabling dependency inversion and interface segregation.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from ..models.content_models import ContentItem, NewsSource


class IContentCollector(ABC):
    """Interface for content collection from various sources"""
    
    @abstractmethod
    async def collect_from_sources(
        self, 
        sources: List[str], 
        hours_back: int = 24
    ) -> List[Dict[str, Any]]:
        """Collect content from web sources and configurations"""
        pass
    
    @abstractmethod
    async def collect_from_csv(self, csv_file: str) -> List[Dict[str, Any]]:
        """Collect content from CSV file"""
        pass
    
    @abstractmethod
    async def collect_from_telegram(
        self, 
        channels: List[str], 
        hours_back: int = 24
    ) -> List[Dict[str, Any]]:
        """Collect content from Telegram channels"""
        pass


class IContentProcessor(ABC):
    """Interface for content processing and analysis"""
    
    @abstractmethod
    async def analyze_content(
        self, 
        content: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Analyze content for relevance and metadata"""
        pass
    
    @abstractmethod
    async def detect_and_merge_duplicates(
        self, 
        content: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect and merge duplicate content from different sources"""
        pass
    
    @abstractmethod
    async def run_ai_discussions(
        self,
        content: List[Dict[str, Any]],
        style: str,
        tone: str,
        platform: str,
        max_stories: int,
        discussion_log: bool
    ) -> List[Dict[str, Any]]:
        """Run AI agent discussions for content selection and ordering"""
        pass
    
    @abstractmethod
    def select_content_simple(
        self,
        content: List[Dict[str, Any]],
        max_stories: int
    ) -> List[Dict[str, Any]]:
        """Simple content selection without AI"""
        pass


class IMediaHandler(ABC):
    """Interface for media downloading and management"""
    
    @abstractmethod
    async def download_all_media(
        self, 
        content: List[Dict[str, Any]], 
        use_youtube_videos: bool = False
    ) -> List[Dict[str, Any]]:
        """Download all media assets for content items"""
        pass


class IVideoComposer(ABC):
    """Interface for video composition"""
    
    @abstractmethod
    async def create_language_video(
        self,
        content: List[Dict[str, Any]],
        language: str,
        style: str,
        tone: str,
        platform: str,
        duration_seconds: int,
        overlay_style: str,
        output_dir: str,
        visual_styles: Dict[str, Any] = None,
        use_youtube_videos: bool = False,
        logo_path: str = None,
        channel_name: str = "NEWS",
        dynamic_transitions: bool = True
    ) -> str:
        """Create video for a specific language"""
        pass


class ISessionReporter(ABC):
    """Interface for session reporting and data export"""
    
    @abstractmethod
    def save_discussion_log(self, discussion_result: Dict[str, Any]) -> None:
        """Save AI discussion log"""
        pass
    
    @abstractmethod
    def save_session_report(
        self,
        content: List[Dict[str, Any]],
        output_videos: Dict[str, str],
        style: str,
        tone: str
    ) -> None:
        """Save comprehensive session report"""
        pass
    
    @abstractmethod
    def export_to_csv(self, content: List[Dict[str, Any]]) -> None:
        """Export scraped articles to CSV format"""
        pass


class IAggregatorOrchestrator(ABC):
    """Main orchestrator interface that coordinates all components"""
    
    @abstractmethod
    async def aggregate_news(
        self,
        sources: List[str],
        csv_file: Optional[str] = None,
        languages: List[str] = ['en'],
        style: str = "professional",
        tone: str = "informative",
        platform: str = "youtube",
        duration_seconds: int = 60,
        max_stories: int = 10,
        enable_ai_discussion: bool = True,
        discussion_log: bool = False,
        overlay_style: str = "modern",
        output_dir: str = "outputs/news",
        hours_back: int = 24,
        telegram_channels: List[str] = [],
        use_youtube_videos: bool = False,
        logo_path: str = None,
        channel_name: str = "NEWS",
        dynamic_transitions: bool = True
    ) -> Dict[str, str]:
        """Main aggregation method that orchestrates the entire workflow"""
        pass


class IContentConverter(ABC):
    """Interface for converting between different content formats"""
    
    @abstractmethod
    def content_item_to_dict(self, item: ContentItem) -> Dict[str, Any]:
        """Convert ContentItem to dict format"""
        pass
    
    @abstractmethod
    def dict_to_content_item(self, data: Dict[str, Any]) -> ContentItem:
        """Convert dict to ContentItem format"""
        pass