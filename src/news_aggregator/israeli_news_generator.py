"""Israeli News Video Generator - Main Entry Point"""

import asyncio
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..utils.logging_config import get_logger
from ..utils.session_manager import SessionManager
from ..ai.manager import AIServiceManager
from ..core.decision_framework import DecisionFramework, CoreDecisions
from ..models.video_models import Platform, VideoCategory, Language
from .composers.scraped_media_composer import ScrapedMediaComposer
from .processors.media_downloader import MediaDownloader

from .scrapers.israeli_scrapers import YnetScraper, RotterScraper
from .processors.israeli_content_processor import IsraeliContentProcessor
from .processors.alien_presenter import AlienPresenterGenerator, AlienCharacter
from .themes.theme_manager import ThemeManager
from .integration.viralai_bridge import ViralAIBridge

logger = get_logger(__name__)


class IsraeliNewsChannel:
    """Generate Israeli news videos with dark humor and alien presenter"""
    
    def __init__(
        self,
        session_manager: Optional[SessionManager] = None,
        ai_manager: Optional[AIServiceManager] = None,
        output_dir: str = "outputs/israeli_news"
    ):
        # Initialize core components
        self.session_manager = session_manager or SessionManager(base_output_dir=output_dir)
        self.ai_manager = ai_manager or AIServiceManager()
        
        # Decision framework will be initialized after session is created
        self.decision_framework = None
        
        # Initialize scrapers
        self.ynet_scraper = YnetScraper()
        self.rotter_scraper = RotterScraper()
        
        # Initialize alien presenter (doesn't need decision framework)
        self.alien = AlienPresenterGenerator()
        
        # Initialize theme manager
        self.theme_manager = ThemeManager()
        
        # Initialize media components
        self.media_downloader = MediaDownloader()
        self.scraped_media_composer = None  # Will be initialized after session creation
        
        # Content processor and bridge will be initialized after session creation
        self.content_processor = None
        self.bridge = None
        self.output_dir = output_dir
    
    async def create_daily_news_video(
        self,
        style: str = "dark_humor",
        include_alien: bool = True,
        output_filename: Optional[str] = None
    ) -> str:
        """Create daily Israeli news video with selected style"""
        
        logger.info("🎬 Starting Israeli News Video Generation")
        
        # Create session for this generation
        session_id = self.session_manager.create_session(
            mission="Israeli News Video Generation",
            platform="youtube",
            duration=60,  # Default duration
            category="news"
        )
        
        # Initialize decision framework now that we have a session
        from ..utils.session_context import SessionContext
        session_context = SessionContext(
            session_id=session_id,
            session_manager_instance=self.session_manager
        )
        self.decision_framework = DecisionFramework(session_context)
        
        # Re-initialize content processor with decision framework
        self.content_processor = IsraeliContentProcessor(self.decision_framework)
        
        # Initialize bridge now that we have session manager and decision framework
        self.bridge = ViralAIBridge(
            self.session_manager, 
            self.ai_manager, 
            self.output_dir,
            self.decision_framework
        )
        
        # Initialize scraped media composer with session manager
        self.scraped_media_composer = ScrapedMediaComposer(
            self.session_manager,
            self.media_downloader,
            self.output_dir
        )
        
        # 1. Scrape content from sources
        logger.info("📰 Scraping news from Ynet and Rotter...")
        ynet_articles = await self.ynet_scraper.scrape_ynet_homepage()
        ynet_bizarre = await self.ynet_scraper.scrape_ynet_bizarre()
        rotter_scoops = await self.rotter_scraper.scrape_rotter_scoops()
        
        # Combine all articles
        all_articles = ynet_articles + ynet_bizarre + rotter_scoops
        logger.info(f"📊 Found {len(all_articles)} total articles")
        
        # 2. Process content with Israeli processor
        video_structure = self.content_processor.process_for_news_video(
            articles=all_articles,
            target_style=style,
            language=Language.HEBREW
        )
        
        # 3. Create mission string for existing infrastructure
        mission = self._create_mission_string(video_structure, style)
        
        # 4. Load Ynet-style theme
        theme = self._create_ynet_theme()
        
        # 5. Generate video using SCRAPED MEDIA ONLY
        logger.info("🎥 Generating video using SCRAPED MEDIA ONLY...")
        logger.info("📸 NO VEO/AI generation - using actual media from news sources")
        
        # Convert articles to ContentItem format for scraped media composer
        from ..models.content_models import ContentItem, MediaAsset, AssetType, NewsSource, SourceType
        content_items = []
        
        for segment in video_structure["segments"]:
            # Find the original article
            article = next((a for a in all_articles if a.get("title") == segment["title"]), None)
            if not article:
                continue
                
            # Create NewsSource
            source = NewsSource(
                id=article.get("source", "ynet"),
                name=article.get("source", "Ynet"),
                source_type=SourceType.WEB,
                url=article.get("url", "https://www.ynet.co.il")
            )
            
            # Create MediaAssets from article media
            media_assets = []
            if article.get("image_url"):
                media_assets.append(MediaAsset(
                    id=f"img_{len(media_assets)}",
                    asset_type=AssetType.IMAGE,
                    source_url=article["image_url"],
                    metadata={"alt": article.get("title", "")}
                ))
            if article.get("video_url"):
                media_assets.append(MediaAsset(
                    id=f"vid_{len(media_assets)}",
                    asset_type=AssetType.VIDEO,
                    source_url=article["video_url"],
                    metadata={"title": article.get("title", "")}
                ))
            
            # Create ContentItem
            content_item = ContentItem(
                id=f"article_{len(content_items)}",
                source=source,
                title=segment["title"],
                content=segment.get("summary", ""),
                categories=[segment.get("category", "general")],
                media_assets=media_assets,
                relevance_score=0.8
            )
            content_items.append(content_item)
        
        # Generate video using scraped media composer
        duration = self._calculate_duration(video_structure)
        output_path = await self.scraped_media_composer.create_video_from_scraped_media(
            content_items=content_items,
            duration_seconds=duration,
            style="fast-paced" if style == "dark_humor" else "normal",
            output_filename=f"israeli_news_{style}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        )
        
        # 6. Apply Ynet overlays and final touches
        if output_path:
            final_path = await self._apply_final_overlays(
                output_path,
                theme,
                output_filename
            )
            
            logger.info(f"✅ Israeli news video created: {final_path}")
            return final_path
        
        raise Exception("Failed to generate video")
    
    def _create_mission_string(self, video_structure: Dict[str, Any], style: str) -> str:
        """Create mission string from video structure"""
        segments = video_structure["segments"]
        
        if style == "dark_humor":
            mission = "צור סרטון חדשות ישראלי עם הומור שחור וציני. "
        else:
            mission = "צור סרטון חדשות ישראלי מקצועי. "
        
        mission += f"כולל {len(segments)} סיפורים: "
        
        # Add article titles
        for i, segment in enumerate(segments):
            mission += f"{i+1}. {segment['title'][:50]}... "
        
        mission += "השתמש בסגנון של תוכנית חדשות ישראלית עם מנחה חייזר בפינה הימנית התחתונה."
        
        return mission
    
    def _create_ynet_theme(self) -> Dict[str, Any]:
        """Create Ynet-style theme configuration"""
        ynet_theme = {
            "name": "Ynet Israeli News",
            "style": {
                "colors": {
                    "primary": "#D40000",  # Ynet red
                    "secondary": "#FFFFFF",
                    "accent": "#FFD700",  # Gold for highlights
                    "text": "#FFFFFF",
                    "background": "#000000",
                    "ticker_bg": "#D40000",
                    "ticker_text": "#FFFFFF"
                },
                "fonts": {
                    "headline": {
                        "family": "Arial Hebrew",
                        "size": 48,
                        "weight": "bold",
                        "color": "#FFFFFF"
                    },
                    "subtitle": {
                        "family": "Arial Hebrew", 
                        "size": 28,
                        "weight": "normal",
                        "color": "#FFD700"
                    }
                },
                "overlays": {
                    "logo": "src/news_aggregator/assets/ynet_logo.png",
                    "lower_third": "src/news_aggregator/assets/ynet_lower_third.png",
                    "breaking": "src/news_aggregator/assets/ynet_breaking.png",
                    "ticker_bg": "src/news_aggregator/assets/ynet_ticker.png"
                }
            },
            "layout": {
                "headline_position": {"x": 960, "y": 900, "anchor": "center"},
                "logo_position": {"x": 100, "y": 100, "anchor": "top-left"},
                "alien_position": {"x": 1720, "y": 880, "anchor": "bottom-right"},
                "alien_size": {"width": 200, "height": 200},
                "ticker_enabled": True,
                "ticker_position": {"x": 0, "y": 1000, "anchor": "bottom-left"},
                "ticker_rtl": True
            },
            "audio": {
                "background_music": "src/news_aggregator/assets/audio/israeli_news_theme.mp3",
                "music_volume": 0.2,
                "transition_sound": "src/news_aggregator/assets/audio/swoosh.mp3"
            },
            "metadata": {
                "rtl": True,
                "style": "israeli_news"
            }
        }
        
        # Save theme as dictionary for now
        # TODO: Convert to NewsTheme class when available
        # self.theme_manager.save_theme(
        #     NewsTheme(**ynet_theme),
        #     "ynet_israeli.json"
        # )
        
        return ynet_theme
    
    def _calculate_duration(self, video_structure: Dict[str, Any]) -> int:
        """Calculate total video duration"""
        duration = 0
        duration += video_structure["intro"]["duration"]
        duration += video_structure["outro"]["duration"]
        
        for segment in video_structure["segments"]:
            duration += segment["duration"]
        
        # Add transition time
        duration += len(video_structure["segments"]) * 2
        
        return duration
    
    
    async def _apply_final_overlays(
        self,
        video_path: str,
        theme: Dict[str, Any],
        output_filename: Optional[str] = None
    ) -> str:
        """Apply final Ynet-style overlays"""
        # This would use FFmpeg to add:
        # - Ynet logo
        # - News ticker
        # - Lower thirds
        # For now, return the original path
        
        if output_filename:
            import shutil
            final_path = os.path.join(os.path.dirname(video_path), output_filename)
            shutil.copy2(video_path, final_path)
            return final_path
        
        return video_path


async def generate_israeli_news(
    style: str = "dark_humor",
    include_alien: bool = True,
    output_filename: Optional[str] = None
) -> str:
    """Main entry point for Israeli news generation"""
    channel = IsraeliNewsChannel()
    return await channel.create_daily_news_video(
        style=style,
        include_alien=include_alien,
        output_filename=output_filename
    )


if __name__ == "__main__":
    # Example usage
    asyncio.run(generate_israeli_news())