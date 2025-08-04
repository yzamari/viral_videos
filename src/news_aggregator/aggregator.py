"""Main News Aggregator System - Comprehensive News Video Generation"""

import asyncio
import os
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import re

from ..utils.logging_config import get_logger
from ..utils.session_manager import SessionManager
from ..ai.manager import AIServiceManager
from ..core.decision_framework import DecisionFramework, CoreDecisions
from ..models.video_models import Platform, VideoCategory, Language
from ..workflows.generate_viral_video import main as generate_viral_video

from .scrapers.web_scraper import WebNewsScraper
from .scrapers.israeli_scrapers import YnetScraper, RotterScraper
from .scrapers.social_media_scraper import SocialMediaScraper
from .scrapers.cnn_scraper import CNNScraper
from .processors.content_analyzer import ContentAnalyzer
from .processors.news_grouper import NewsGrouper
from .processors.visual_composer import VisualComposer
from .models.content_models import (
    ContentItem, NewsSource, ContentCollection,
    SourceType, ContentStatus
)
from .models.composition_models import (
    CompositionProject, NewsTemplate, VideoSegment,
    ThemeConfig, PresenterConfig, PresenterStyle
)
from .themes.theme_manager import ThemeManager

logger = get_logger(__name__)


class NewsAggregator:
    """Main news aggregator system for comprehensive news video generation"""
    
    def __init__(
        self,
        session_manager: Optional[SessionManager] = None,
        ai_manager: Optional[AIServiceManager] = None,
        output_dir: str = "outputs/news_videos"
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
        self.scrapers = {
            SourceType.WEB: WebNewsScraper(),
            SourceType.SOCIAL_MEDIA: SocialMediaScraper()
        }
        
        # Specialized scrapers
        self.ynet_scraper = YnetScraper()
        self.rotter_scraper = RotterScraper()
        self.cnn_scraper = CNNScraper()
        
        # Initialize processors
        self.content_analyzer = ContentAnalyzer(self.ai_manager)
        self.news_grouper = NewsGrouper(self.ai_manager)
        self.visual_composer = VisualComposer(self.session_manager)
        
        # Theme manager
        self.theme_manager = ThemeManager()
        
        # Output directory
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    async def create_news_edition(
        self,
        sources: List[str],
        edition_type: str = "general",  # general, gossip, sports, finance, tech
        style: str = "professional",     # professional, casual, humorous, dramatic
        tone: str = "informative",       # informative, entertaining, critical, analytical
        visual_style: str = "modern",    # modern, classic, dynamic, minimalist
        language: str = "en",
        duration_minutes: int = 5,
        presenter_enabled: bool = True,
        output_filename: Optional[str] = None
    ) -> str:
        """Create a comprehensive news edition video from multiple sources"""
        
        logger.info(f"🎬 Starting News Edition Generation")
        logger.info(f"Edition Type: {edition_type}, Style: {style}, Sources: {sources}")
        
        # 1. Collect content from all sources
        all_content = await self._collect_content_from_sources(sources)
        logger.info(f"📰 Collected {len(all_content)} total articles")
        
        # 2. Analyze content for relevance and interest
        analyzed_content = await self._analyze_content(
            all_content, 
            edition_type,
            language
        )
        
        # 3. Group related news together
        news_groups = await self._group_related_news(
            analyzed_content,
            edition_type
        )
        logger.info(f"📊 Created {len(news_groups)} news groups")
        
        # 4. Create video structure
        video_structure = await self._create_video_structure(
            news_groups,
            edition_type,
            style,
            tone,
            visual_style,
            duration_minutes,
            presenter_enabled
        )
        
        # 5. Generate theme and overlays
        theme = await self._create_edition_theme(
            edition_type,
            visual_style,
            sources
        )
        
        # 6. Create composition project
        composition = await self._create_composition(
            video_structure,
            theme,
            language,
            presenter_enabled
        )
        
        # 7. Generate video using existing infrastructure
        video_path = await self._generate_video(
            composition,
            video_structure,
            style,
            tone,
            visual_style,
            language,
            output_filename
        )
        
        logger.info(f"✅ News edition video created: {video_path}")
        return video_path
    
    async def _collect_content_from_sources(
        self, 
        sources: List[str]
    ) -> List[ContentItem]:
        """Collect content from all specified sources"""
        all_content = []
        
        for source_url in sources:
            try:
                # Determine source type and scraper
                if "ynet.co.il" in source_url:
                    articles = await self.ynet_scraper.scrape_ynet_homepage()
                    articles.extend(await self.ynet_scraper.scrape_ynet_bizarre())
                    all_content.extend(articles)
                
                elif "cnn.com" in source_url:
                    articles = await self.cnn_scraper.scrape_cnn_homepage()
                    all_content.extend(articles)
                
                elif "rotter.net" in source_url:
                    articles = await self.rotter_scraper.scrape_rotter_scoops()
                    all_content.extend(articles)
                
                elif "telegram" in source_url or "t.me" in source_url:
                    # Social media scraper for Telegram
                    source = NewsSource(
                        id="",
                        name="Telegram",
                        source_type=SourceType.SOCIAL_MEDIA,
                        url=source_url
                    )
                    articles = await self.scrapers[SourceType.SOCIAL_MEDIA].scrape(source)
                    all_content.extend(articles)
                
                else:
                    # Generic web scraper
                    source = NewsSource(
                        id="",
                        name=source_url.split('/')[2],
                        source_type=SourceType.WEB,
                        url=source_url
                    )
                    articles = await self.scrapers[SourceType.WEB].scrape(source)
                    all_content.extend(articles)
                    
            except Exception as e:
                logger.error(f"Failed to scrape {source_url}: {str(e)}")
                continue
        
        return all_content
    
    async def _analyze_content(
        self,
        content_items: List[ContentItem],
        edition_type: str,
        language: str
    ) -> List[ContentItem]:
        """Analyze content for relevance and scoring"""
        analyzed_items = []
        
        for item in content_items:
            try:
                # Analyze with AI
                analysis = await self.content_analyzer.analyze(
                    item,
                    edition_type,
                    language
                )
                
                # Update item with analysis results
                item.relevance_score = analysis["relevance_score"]
                item.sentiment_score = analysis["sentiment_score"]
                item.summary = analysis["summary"]
                item.tags = analysis["tags"]
                item.categories = analysis["categories"]
                item.metadata.update(analysis["metadata"])
                
                # Only include relevant content
                if item.relevance_score > 0.3:
                    analyzed_items.append(item)
                    
            except Exception as e:
                logger.warning(f"Failed to analyze content item: {str(e)}")
                continue
        
        # Sort by relevance
        analyzed_items.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return analyzed_items
    
    async def _group_related_news(
        self,
        content_items: List[ContentItem],
        edition_type: str
    ) -> List[ContentCollection]:
        """Group related news items together"""
        return await self.news_grouper.group_content(
            content_items,
            edition_type
        )
    
    async def _create_video_structure(
        self,
        news_groups: List[ContentCollection],
        edition_type: str,
        style: str,
        tone: str,
        visual_style: str,
        duration_minutes: int,
        presenter_enabled: bool
    ) -> Dict[str, Any]:
        """Create structured video composition from news groups"""
        
        # Calculate time allocation
        total_seconds = duration_minutes * 60
        intro_outro_time = 10  # 5 seconds each
        content_time = total_seconds - intro_outro_time
        
        # Select top groups based on available time
        segments = []
        current_duration = 0
        segment_duration = content_time / min(len(news_groups), 10)  # Max 10 segments
        
        for i, group in enumerate(news_groups[:10]):
            if current_duration + segment_duration > content_time:
                break
                
            segment = await self._create_segment_from_group(
                group,
                segment_duration,
                style,
                tone,
                position=i
            )
            segments.append(segment)
            current_duration += segment_duration
        
        # Create complete structure
        structure = {
            "intro": self._create_intro_segment(edition_type, style),
            "segments": segments,
            "outro": self._create_outro_segment(edition_type, style),
            "transitions": self._create_transitions(len(segments)),
            "metadata": {
                "edition_type": edition_type,
                "style": style,
                "tone": tone,
                "visual_style": visual_style,
                "total_duration": total_seconds,
                "presenter_enabled": presenter_enabled
            }
        }
        
        return structure
    
    async def _create_segment_from_group(
        self,
        group: ContentCollection,
        duration: float,
        style: str,
        tone: str,
        position: int
    ) -> Dict[str, Any]:
        """Create video segment from content group"""
        
        # Get primary content item
        primary_item = group.get_top_items(1, by="relevance")[0]
        
        # Create title and summary
        if len(group.items) > 1:
            title = f"{group.name} - {len(group.items)} Related Stories"
            summary = await self._create_group_summary(group, tone)
        else:
            title = primary_item.title
            summary = primary_item.summary or primary_item.content[:200]
        
        # Get media assets
        all_media = []
        for item in group.items[:3]:  # Top 3 items' media
            all_media.extend(item.media_assets)
        
        segment = {
            "id": f"segment_{position}",
            "group_id": group.id,
            "title": title,
            "summary": summary,
            "duration": duration,
            "style": style,
            "tone": tone,
            "content_items": [item.id for item in group.items],
            "media": {
                "primary": primary_item.get_primary_media(),
                "additional": all_media[:5]  # Max 5 media assets
            },
            "hooks": await self._generate_hooks(group, style, tone),
            "overlays": await self._generate_overlays(group, position)
        }
        
        return segment
    
    async def _create_group_summary(
        self, 
        group: ContentCollection,
        tone: str
    ) -> str:
        """Create summary for a group of related news"""
        
        # Combine summaries from top items
        summaries = []
        for item in group.items[:3]:
            if item.summary:
                summaries.append(item.summary)
        
        # Use AI to create cohesive summary
        prompt = f"""Create a cohesive summary of these related news items.
        Tone: {tone}
        Individual summaries:
        {chr(10).join(summaries)}
        
        Create a single paragraph summary that captures the essence of all stories."""
        
        response = await self.ai_manager.generate_text(prompt)
        return response.strip()
    
    async def _generate_hooks(
        self,
        group: ContentCollection,
        style: str,
        tone: str
    ) -> List[str]:
        """Generate attention-grabbing hooks for the segment"""
        
        # Get key points from group
        key_points = []
        for item in group.items[:3]:
            if item.tags:
                key_points.extend(item.tags[:2])
        
        prompt = f"""Generate 3 attention-grabbing hooks for this news segment.
        Topic: {group.name}
        Style: {style}
        Tone: {tone}
        Key points: {', '.join(key_points)}
        
        Each hook should be one short sentence that makes viewers want to watch."""
        
        response = await self.ai_manager.generate_text(prompt)
        hooks = [line.strip() for line in response.strip().split('\n') if line.strip()]
        
        return hooks[:3]
    
    async def _generate_overlays(
        self,
        group: ContentCollection,
        position: int
    ) -> Dict[str, Any]:
        """Generate overlay specifications for the segment"""
        
        overlays = {
            "headline": {
                "text": group.name,
                "position": "top",
                "style": "bold",
                "animation": "slide_in"
            },
            "subtitle": {
                "text": f"{len(group.items)} stories",
                "position": "below_headline",
                "style": "normal",
                "animation": "fade_in"
            }
        }
        
        # Add source attribution
        sources = list(set(item.source.name for item in group.items))
        if sources:
            overlays["source"] = {
                "text": f"Sources: {', '.join(sources[:3])}",
                "position": "bottom_left",
                "style": "small",
                "animation": "fade_in"
            }
        
        # Add position indicator
        overlays["position"] = {
            "text": f"Story {position + 1}",
            "position": "top_right",
            "style": "badge",
            "animation": "none"
        }
        
        return overlays
    
    async def _create_edition_theme(
        self,
        edition_type: str,
        visual_style: str,
        sources: List[str]
    ) -> ThemeConfig:
        """Create theme configuration for the news edition"""
        
        # Base themes for different edition types
        theme_presets = {
            "general": {
                "primary_color": "#1E3A8A",
                "secondary_color": "#3B82F6",
                "accent_color": "#EF4444",
                "font_family": "Arial"
            },
            "gossip": {
                "primary_color": "#EC4899",
                "secondary_color": "#F472B6",
                "accent_color": "#FCD34D",
                "font_family": "Helvetica"
            },
            "sports": {
                "primary_color": "#10B981",
                "secondary_color": "#34D399",
                "accent_color": "#F59E0B",
                "font_family": "Impact"
            },
            "finance": {
                "primary_color": "#059669",
                "secondary_color": "#10B981",
                "accent_color": "#DC2626",
                "font_family": "Georgia"
            },
            "tech": {
                "primary_color": "#7C3AED",
                "secondary_color": "#8B5CF6",
                "accent_color": "#06B6D4",
                "font_family": "Roboto"
            }
        }
        
        base_theme = theme_presets.get(edition_type, theme_presets["general"])
        
        theme = ThemeConfig(
            name=f"{edition_type.title()} News Edition",
            **base_theme,
            background_color="#000000",
            font_sizes={
                "headline": 56,
                "subtitle": 36,
                "body": 28,
                "caption": 20,
                "ticker": 24
            }
        )
        
        # Adjust for visual style
        if visual_style == "minimalist":
            theme.font_sizes = {k: int(v * 0.8) for k, v in theme.font_sizes.items()}
        elif visual_style == "dynamic":
            theme.font_sizes = {k: int(v * 1.2) for k, v in theme.font_sizes.items()}
        
        # Save theme
        self.theme_manager.save_theme(theme, f"{edition_type}_{visual_style}.json")
        
        return theme
    
    async def _create_composition(
        self,
        video_structure: Dict[str, Any],
        theme: ThemeConfig,
        language: str,
        presenter_enabled: bool
    ) -> CompositionProject:
        """Create composition project from video structure"""
        
        # Create news template
        template = NewsTemplate(
            id=f"news_template_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            name=video_structure["metadata"]["edition_type"],
            description="Generated news edition",
            category=video_structure["metadata"]["edition_type"],
            theme_config=theme,
            presenter_config=PresenterConfig(
                presenter_style=PresenterStyle.FORMAL_NEWS,
                model_id="default_presenter",
                voice_id=f"{language}-news-voice"
            ) if presenter_enabled else None
        )
        
        # Create composition project
        composition = CompositionProject(
            id=f"composition_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            name=f"{video_structure['metadata']['edition_type']} News Edition",
            template=template,
            primary_language=language
        )
        
        # Add segments
        for segment_data in video_structure["segments"]:
            segment = VideoSegment(
                id=segment_data["id"],
                content_item_id=segment_data["group_id"],
                duration=segment_data["duration"],
                narration_text=segment_data["summary"],
                subtitle_text=segment_data["title"]
            )
            composition.add_segment(segment)
        
        return composition
    
    async def _generate_video(
        self,
        composition: CompositionProject,
        video_structure: Dict[str, Any],
        style: str,
        tone: str,
        visual_style: str,
        language: str,
        output_filename: Optional[str] = None
    ) -> str:
        """Generate video using existing ViralAI infrastructure"""
        
        # Create mission string
        mission = self._create_mission_from_structure(video_structure)
        
        # Store composition in session for processors
        self.session_manager.session_data["composition"] = composition
        self.session_manager.session_data["video_structure"] = video_structure
        
        # Video generation parameters
        video_params = {
            "mission": mission,
            "category": "News",
            "platform": "youtube",
            "duration": int(composition.get_total_duration()),
            "style": style,
            "tone": tone,
            "visual_style": visual_style,
            "languages": [language],
            "theme": "custom_news_edition",
            "discussions": "enhanced",
            "mode": "enhanced",
            "voice": self._get_voice_for_language(language),
            "veo_model_order": "veo3-fast,veo3,veo2",
            "business_name": f"{video_structure['metadata']['edition_type'].title()} News",
            "show_business_info": True
        }
        
        # Generate video
        output_path = await generate_viral_video(**video_params)
        
        # Apply final overlays and branding
        if output_path:
            final_path = await self.visual_composer.apply_final_composition(
                output_path,
                composition,
                output_filename
            )
            return final_path
        
        raise Exception("Failed to generate video")
    
    def _create_mission_from_structure(self, structure: Dict[str, Any]) -> str:
        """Create mission string from video structure"""
        edition_type = structure["metadata"]["edition_type"]
        style = structure["metadata"]["style"]
        
        mission = f"Create a {style} {edition_type} news edition video with {len(structure['segments'])} stories. "
        
        # Add segment summaries
        for i, segment in enumerate(structure["segments"]):
            mission += f"Story {i+1}: {segment['title'][:50]}... "
        
        mission += f"Use {structure['metadata']['visual_style']} visual style with professional news presentation."
        
        return mission
    
    def _get_voice_for_language(self, language: str) -> str:
        """Get appropriate voice for language"""
        voice_map = {
            "en": "en-US-Standard-D",
            "he": "he-IL-Standard-A",
            "es": "es-US-Standard-B",
            "fr": "fr-FR-Standard-D",
            "de": "de-DE-Standard-B"
        }
        return voice_map.get(language, "en-US-Standard-D")
    
    def _create_intro_segment(self, edition_type: str, style: str) -> Dict[str, Any]:
        """Create intro segment configuration"""
        intros = {
            "general": "Welcome to today's news roundup",
            "gossip": "Get ready for the latest celebrity gossip",
            "sports": "Here are today's top sports highlights",
            "finance": "Let's dive into today's financial news",
            "tech": "Welcome to the latest in technology"
        }
        
        return {
            "text": intros.get(edition_type, intros["general"]),
            "duration": 5,
            "style": "dramatic" if style == "professional" else "energetic",
            "animation": "zoom_in"
        }
    
    def _create_outro_segment(self, edition_type: str, style: str) -> Dict[str, Any]:
        """Create outro segment configuration"""
        outros = {
            "general": "That's all for today's news. Stay informed!",
            "gossip": "Thanks for watching! More gossip coming soon!",
            "sports": "That's a wrap on today's sports action!",
            "finance": "Stay tuned for more market updates",
            "tech": "Thanks for joining us in the world of tech"
        }
        
        return {
            "text": outros.get(edition_type, outros["general"]),
            "duration": 5,
            "style": "casual",
            "animation": "fade_out"
        }
    
    def _create_transitions(self, num_segments: int) -> List[str]:
        """Create transition types between segments"""
        transitions = ["fade", "slide", "dissolve", "wipe"]
        return [transitions[i % len(transitions)] for i in range(num_segments - 1)]


async def create_news_edition(
    sources: List[str],
    edition_type: str = "general",
    style: str = "professional",
    tone: str = "informative",
    visual_style: str = "modern",
    language: str = "en",
    duration_minutes: int = 5,
    presenter_enabled: bool = True,
    output_filename: Optional[str] = None
) -> str:
    """Main entry point for creating news edition videos"""
    aggregator = NewsAggregator()
    return await aggregator.create_news_edition(
        sources=sources,
        edition_type=edition_type,
        style=style,
        tone=tone,
        visual_style=visual_style,
        language=language,
        duration_minutes=duration_minutes,
        presenter_enabled=presenter_enabled,
        output_filename=output_filename
    )