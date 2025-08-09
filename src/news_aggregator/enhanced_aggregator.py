"""
Enhanced News Aggregator - Refactored facade using SOLID principles.

This class now acts as a facade over the new orchestrator-based architecture,
maintaining backward compatibility while delegating to properly separated components.
"""

from typing import List, Dict, Any, Optional
from .orchestrators.aggregator_orchestrator import NewsAggregatorOrchestrator
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class EnhancedNewsAggregator:
    """
    Facade class that maintains backward compatibility while using the new architecture.
    
    This class now delegates all operations to the NewsAggregatorOrchestrator,
    following the Facade pattern to hide the complexity of the refactored system.
    """
    
    def __init__(self, enable_discussions: bool = True, discussion_log: bool = False):
        """
        Initialize the enhanced news aggregator facade.
        
        Args:
            enable_discussions: Whether to enable AI discussions
            discussion_log: Whether to enable detailed discussion logging
        """
        # Delegate to the new orchestrator
        self.orchestrator = NewsAggregatorOrchestrator(
            enable_discussions=enable_discussions,
            discussion_log=discussion_log
        )
        
        logger.info("✅ EnhancedNewsAggregator initialized with new SOLID architecture")
    
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
        """
        Main aggregation method supporting all features.
        
        This method now delegates to the NewsAggregatorOrchestrator while maintaining
        the same interface for backward compatibility.
        
        Args:
            sources: List of URLs or source names
            csv_file: Optional CSV file with additional items
            languages: List of output languages (creates one video per language)
            style: Free-form style description for AI agents
            tone: Free-form tone description for AI agents
            platform: Target platform (youtube, tiktok, instagram, twitter)
            duration_seconds: Duration per video
            max_stories: Maximum stories to include
            enable_ai_discussion: Enable AI agent discussions
            discussion_log: Show detailed discussion logs
            overlay_style: Overlay style (modern, classic, minimal)
            output_dir: Output directory
            hours_back: How many hours back to collect content
            telegram_channels: List of Telegram channels to scrape
            use_youtube_videos: Whether to search and download YouTube videos
            logo_path: Path to logo for branding
            channel_name: Channel name for branding
            dynamic_transitions: Whether to use dynamic transitions
            
        Returns:
            Dict mapping language to output video path
        """
        # Delegate to the orchestrator
        return await self.orchestrator.aggregate_news(
            sources=sources,
            csv_file=csv_file,
            languages=languages,
            style=style,
            tone=tone,
            platform=platform,
            duration_seconds=duration_seconds,
            max_stories=max_stories,
            enable_ai_discussion=enable_ai_discussion,
            discussion_log=discussion_log,
            overlay_style=overlay_style,
            output_dir=output_dir,
            hours_back=hours_back,
            telegram_channels=telegram_channels,
            use_youtube_videos=use_youtube_videos,
            logo_path=logo_path,
            channel_name=channel_name,
            dynamic_transitions=dynamic_transitions
        )


# CLI integration function
async def create_enhanced_news_edition(
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
    """Create news edition with enhanced aggregator"""
    
    logger.info(f"📺 create_enhanced_news_edition received channel_name: {channel_name}")
    
    aggregator = EnhancedNewsAggregator(
        enable_discussions=enable_ai_discussion,
        discussion_log=discussion_log
    )
    
    return await aggregator.aggregate_news(
        sources=sources,
        csv_file=csv_file,
        languages=languages,
        style=style,
        tone=tone,
        platform=platform,
        duration_seconds=duration_seconds,
        max_stories=max_stories,
        enable_ai_discussion=enable_ai_discussion,
        discussion_log=discussion_log,
        overlay_style=overlay_style,
        output_dir=output_dir,
        hours_back=hours_back,
        telegram_channels=telegram_channels,
        use_youtube_videos=use_youtube_videos,
        logo_path=logo_path,
        channel_name=channel_name,
        dynamic_transitions=dynamic_transitions
    )