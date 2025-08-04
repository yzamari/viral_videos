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
from ..workflows.generate_viral_video import main as generate_viral_video

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
        
        # Create session context for decision framework
        from ..utils.session_context import SessionContext
        session_context = SessionContext(
            session_id=self.session_manager.session_id,
            output_dir=self.session_manager.session_dir
        )
        self.decision_framework = DecisionFramework(session_context)
        
        # Initialize scrapers
        self.ynet_scraper = YnetScraper()
        self.rotter_scraper = RotterScraper()
        
        # Initialize processors
        self.content_processor = IsraeliContentProcessor(self.decision_framework)
        self.alien = AlienPresenterGenerator()
        
        # Initialize theme manager
        self.theme_manager = ThemeManager()
        
        # Bridge to existing infrastructure
        self.bridge = ViralAIBridge(session_manager, ai_manager, output_dir)
    
    async def create_daily_news_video(
        self,
        style: str = "dark_humor",
        include_alien: bool = True,
        output_filename: Optional[str] = None
    ) -> str:
        """Create daily Israeli news video with selected style"""
        
        logger.info("🎬 Starting Israeli News Video Generation")
        
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
        
        # 5. Generate video using existing infrastructure
        logger.info("🎥 Generating video using ViralAI infrastructure...")
        
        # Set up parameters for existing generate function
        video_params = {
            "mission": mission,
            "category": "News",
            "platform": "youtube",
            "duration": self._calculate_duration(video_structure),
            "style": style if style != "dark_humor" else "humorous",
            "tone": "sarcastic" if style == "dark_humor" else "engaging",
            "visual_style": "dynamic",
            "languages": ["he", "en"],  # Hebrew primary, English secondary
            "theme": "custom_ynet",
            "discussions": "enhanced",  # Use AI agents for better content
            "mode": "enhanced",
            "voice": "he-IL-Standard-A",  # Hebrew male voice
            "character": "alien_zorg" if include_alien else None,
            "scene": "news_studio_bottom_right" if include_alien else None,
            "veo_model_order": "veo3-fast,veo3,veo2",
            "business_name": "חדשות עם זורג",  # News with Zorg
            "show_business_info": False
        }
        
        # Generate using existing workflow
        output_path = await self._generate_with_structure(
            video_structure,
            video_params,
            theme,
            include_alien
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
    
    async def _generate_with_structure(
        self,
        video_structure: Dict[str, Any],
        video_params: Dict[str, Any],
        theme: Dict[str, Any],
        include_alien: bool
    ) -> str:
        """Generate video using structured content"""
        
        # Create detailed script from structure
        script_sections = []
        
        # Intro
        intro = video_structure["intro"]
        script_sections.append({
            "type": "intro",
            "text": intro["text"],
            "duration": intro["duration"],
            "alien_commentary": self.alien.generate_intro("חדשות ישראל היום") if include_alien else None
        })
        
        # Process each segment
        for i, segment in enumerate(video_structure["segments"]):
            # Main content
            script_sections.append({
                "type": "news_segment",
                "title": segment["title"],
                "content": segment["summary"],
                "duration": segment["duration"],
                "style": segment["style"],
                "tone": segment["tone"],
                "media": segment["media"],
                "alien_commentary": segment.get("alien_commentary") if include_alien else None
            })
            
            # Transition
            if segment.get("transition"):
                script_sections.append({
                    "type": "transition",
                    "text": segment["transition"],
                    "duration": 2
                })
        
        # Outro
        outro = video_structure["outro"]
        script_sections.append({
            "type": "outro",
            "text": outro["text"],
            "duration": outro["duration"],
            "alien_commentary": self.alien.generate_outro() if include_alien else None
        })
        
        # Store structure in session for processors to use
        self.session_manager.session_data["video_structure"] = video_structure
        self.session_manager.session_data["script_sections"] = script_sections
        self.session_manager.session_data["theme"] = theme
        
        # Use existing generation with our parameters
        output_path = generate_viral_video(**video_params)
        
        return output_path
    
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