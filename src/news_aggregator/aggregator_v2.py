"""News Aggregator V2 - Enhanced with CSV support and media scraping"""

import asyncio
import os
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

from ..utils.logging_config import get_logger
from ..utils.session_manager import SessionManager
from ..ai.manager import AIServiceManager
from ..core.decision_framework import DecisionFramework
from ..workflows.generate_viral_video import main as generate_viral_video

from .parsers.csv_parser import NewsCSVParser
from .scrapers.web_scraper import WebNewsScraper
from .scrapers.israeli_scrapers import YnetScraper, RotterScraper
from .scrapers.cnn_scraper import CNNScraper
from .scrapers.social_media_scraper import SocialMediaScraper
from .processors.content_analyzer import ContentAnalyzer
from .processors.news_grouper import NewsGrouper
from .processors.media_downloader import MediaDownloader
from .composers.news_edition_composer import NewsEditionComposer
from .models.content_models import (
    ContentItem, NewsSource, ContentCollection,
    SourceType, ContentStatus, MediaAsset, AssetType
)
from .models.composition_models import CompositionProject, NewsTemplate

logger = get_logger(__name__)


class NewsAggregatorV2:
    """Enhanced news aggregator with CSV support and media handling"""
    
    def __init__(
        self,
        session_manager: Optional[SessionManager] = None,
        ai_manager: Optional[AIServiceManager] = None,
        output_dir: str = "outputs/news_videos"
    ):
        # Initialize core components
        self.session_manager = session_manager or SessionManager(base_output_dir=output_dir)
        self.ai_manager = ai_manager or AIServiceManager()
        self.decision_framework = DecisionFramework()
        
        # Initialize parsers
        self.csv_parser = NewsCSVParser()
        
        # Initialize scrapers
        self.scrapers = {
            SourceType.WEB: WebNewsScraper(),
            SourceType.SOCIAL_MEDIA: SocialMediaScraper()
        }
        self.ynet_scraper = YnetScraper()
        self.rotter_scraper = RotterScraper()
        self.cnn_scraper = CNNScraper()
        
        # Initialize processors
        self.content_analyzer = ContentAnalyzer(self.ai_manager)
        self.news_grouper = NewsGrouper(self.ai_manager)
        self.media_downloader = MediaDownloader()
        
        # Initialize composer
        self.edition_composer = NewsEditionComposer(
            self.session_manager,
            self.ai_manager,
            self.decision_framework,
            self.media_downloader
        )
        
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    async def create_news_edition_from_csv(
        self,
        csv_path: str,
        edition_type: str = "general",
        style: str = "professional",
        tone: str = "informative",
        visual_style: str = "modern",
        language: str = "en",
        duration_minutes: int = 5,
        use_ai_agents: bool = True,
        use_scraped_media: bool = True,
        output_filename: Optional[str] = None
    ) -> str:
        """Create news edition from CSV file"""
        
        logger.info(f"🎬 Creating news edition from CSV: {csv_path}")
        
        # 1. Parse CSV file
        csv_data = self.csv_parser.parse_csv_file(csv_path)
        content_items = await self._process_csv_data(csv_data, csv_path)
        
        logger.info(f"📰 Processed {len(content_items)} items from CSV")
        
        # 2. Continue with standard flow
        return await self._create_edition_from_content(
            content_items,
            edition_type,
            style,
            tone,
            visual_style,
            language,
            duration_minutes,
            use_ai_agents,
            use_scraped_media,
            output_filename
        )
    
    async def create_news_edition_from_sources(
        self,
        sources: List[str],
        edition_type: str = "general",
        style: str = "professional",
        tone: str = "informative",
        visual_style: str = "modern",
        language: str = "en",
        duration_minutes: int = 5,
        use_ai_agents: bool = True,
        use_scraped_media: bool = True,
        output_filename: Optional[str] = None
    ) -> str:
        """Create news edition from URL sources"""
        
        logger.info(f"🎬 Creating news edition from {len(sources)} sources")
        
        # 1. Scrape content from sources
        content_items = await self._collect_content_from_sources(sources)
        
        logger.info(f"📰 Collected {len(content_items)} articles")
        
        # 2. Continue with standard flow
        return await self._create_edition_from_content(
            content_items,
            edition_type,
            style,
            tone,
            visual_style,
            language,
            duration_minutes,
            use_ai_agents,
            use_scraped_media,
            output_filename
        )
    
    async def _process_csv_data(
        self,
        csv_data: List[Dict[str, Any]],
        csv_path: str
    ) -> List[ContentItem]:
        """Process CSV data into ContentItems"""
        
        content_items = []
        
        # Determine CSV type
        if csv_data and 'title' in csv_data[0]:
            # Articles CSV
            for row in csv_data:
                # Create news source
                source = NewsSource(
                    id="csv_import",
                    name=row.get('source_name', 'CSV Import'),
                    source_type=SourceType.WEB,
                    url=row.get('url', csv_path)
                )
                
                # Create content item
                item = ContentItem(
                    id="",
                    source=source,
                    title=row['title'],
                    content=row['content'],
                    summary=row.get('summary'),
                    published_date=row.get('published_date', datetime.now()),
                    author=row.get('author'),
                    url=row.get('url'),
                    tags=row.get('tags', []),
                    categories=[row.get('category', 'general')],
                    status=ContentStatus.SCRAPED
                )
                
                # Add media assets
                for media_url in row.get('media_urls', []):
                    asset = MediaAsset(
                        id="",
                        asset_type=self._detect_asset_type(media_url),
                        source_url=media_url
                    )
                    item.media_assets.append(asset)
                
                content_items.append(item)
        
        elif csv_data and 'url' in csv_data[0]:
            # Sources CSV - scrape each source
            sources = [row['url'] for row in csv_data]
            content_items = await self._collect_content_from_sources(sources)
        
        elif csv_data and 'event_name' in csv_data[0]:
            # Events CSV
            for row in csv_data:
                source = NewsSource(
                    id="event_import",
                    name="Event Import",
                    source_type=SourceType.WEB,
                    url=csv_path
                )
                
                # Create content from event
                content = f"{row.get('highlights', '')}\n\nResult: {row.get('result', '')}"
                
                item = ContentItem(
                    id="",
                    source=source,
                    title=row['event_name'],
                    content=content,
                    published_date=row.get('date', datetime.now()),
                    categories=[row.get('event_type', 'sports')],
                    status=ContentStatus.SCRAPED,
                    metadata={
                        "event_type": row.get('event_type'),
                        "location": row.get('location'),
                        "participants": row.get('participants', []),
                        "stats": row.get('stats', {})
                    }
                )
                
                # Add media
                for media_url in row.get('media_urls', []):
                    asset = MediaAsset(
                        id="",
                        asset_type=self._detect_asset_type(media_url),
                        source_url=media_url
                    )
                    item.media_assets.append(asset)
                
                content_items.append(item)
        
        return content_items
    
    def _detect_asset_type(self, url: str) -> AssetType:
        """Detect asset type from URL"""
        url_lower = url.lower()
        
        if any(ext in url_lower for ext in ['.mp4', '.webm', '.mov', '.avi']):
            return AssetType.VIDEO
        elif any(ext in url_lower for ext in ['.jpg', '.jpeg', '.png', '.gif']):
            return AssetType.IMAGE
        elif any(ext in url_lower for ext in ['.mp3', '.wav', '.m4a']):
            return AssetType.AUDIO
        else:
            return AssetType.IMAGE  # Default
    
    async def _collect_content_from_sources(
        self,
        sources: List[str]
    ) -> List[ContentItem]:
        """Collect content from URL sources"""
        
        all_content = []
        
        for source_url in sources:
            try:
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
                
                else:
                    # Generic scraper
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
        
        return all_content
    
    async def _create_edition_from_content(
        self,
        content_items: List[ContentItem],
        edition_type: str,
        style: str,
        tone: str,
        visual_style: str,
        language: str,
        duration_minutes: int,
        use_ai_agents: bool,
        use_scraped_media: bool,
        output_filename: Optional[str]
    ) -> str:
        """Create news edition from content items"""
        
        # 2. Analyze content
        analyzed_content = await self._analyze_content(
            content_items,
            edition_type,
            language
        )
        
        # 3. Group related news
        news_groups = await self._group_related_news(
            analyzed_content,
            edition_type
        )
        logger.info(f"📊 Created {len(news_groups)} news groups")
        
        # 4. Create composition project
        composition = await self._create_composition_project(
            news_groups,
            edition_type,
            visual_style,
            duration_minutes
        )
        
        # 5. Use AI agents and compose edition
        if use_ai_agents:
            edition_data = await self.edition_composer.compose_news_edition(
                news_groups,
                edition_type,
                composition,
                use_scraped_media
            )
        else:
            # Simple composition without AI agents
            edition_data = await self._simple_composition(
                news_groups,
                composition,
                use_scraped_media
            )
        
        # 6. Generate video
        video_path = await self._generate_video(
            edition_data,
            composition,
            style,
            tone,
            visual_style,
            language,
            output_filename
        )
        
        logger.info(f"✅ News edition created: {video_path}")
        return video_path
    
    async def _analyze_content(
        self,
        content_items: List[ContentItem],
        edition_type: str,
        language: str
    ) -> List[ContentItem]:
        """Analyze content items"""
        
        analyzed_items = []
        
        for item in content_items:
            try:
                analysis = await self.content_analyzer.analyze(
                    item,
                    edition_type,
                    language
                )
                
                item.relevance_score = analysis["relevance_score"]
                item.sentiment_score = analysis["sentiment_score"]
                item.summary = analysis["summary"]
                item.tags = analysis["tags"]
                item.categories = analysis["categories"]
                item.metadata.update(analysis["metadata"])
                
                if item.relevance_score > 0.3:
                    analyzed_items.append(item)
                    
            except Exception as e:
                logger.warning(f"Failed to analyze item: {str(e)}")
        
        analyzed_items.sort(key=lambda x: x.relevance_score, reverse=True)
        return analyzed_items
    
    async def _group_related_news(
        self,
        content_items: List[ContentItem],
        edition_type: str
    ) -> List[ContentCollection]:
        """Group related news items"""
        
        return await self.news_grouper.group_content(
            content_items,
            edition_type
        )
    
    async def _create_composition_project(
        self,
        news_groups: List[ContentCollection],
        edition_type: str,
        visual_style: str,
        duration_minutes: int
    ) -> CompositionProject:
        """Create composition project"""
        
        template = NewsTemplate(
            id=f"template_{datetime.now().timestamp()}",
            name=f"{edition_type.title()} News Edition",
            description=f"Auto-generated {edition_type} news",
            category=edition_type,
            duration_range=(duration_minutes * 60 - 30, duration_minutes * 60 + 30)
        )
        
        composition = CompositionProject(
            id=f"composition_{datetime.now().timestamp()}",
            name=f"{edition_type.title()} News - {datetime.now().strftime('%Y-%m-%d')}",
            template=template
        )
        
        return composition
    
    async def _simple_composition(
        self,
        news_groups: List[ContentCollection],
        composition: CompositionProject,
        use_scraped_media: bool
    ) -> Dict[str, Any]:
        """Simple composition without AI agents"""
        
        # Download media if needed
        media_assets = {}
        if use_scraped_media:
            all_urls = []
            for group in news_groups:
                for item in group.items:
                    for asset in item.media_assets:
                        all_urls.append(asset.source_url)
            
            downloaded = await self.media_downloader.download_media_batch(all_urls)
            for media in downloaded:
                content_id = media.get('metadata', {}).get('content_id')
                if content_id:
                    if content_id not in media_assets:
                        media_assets[content_id] = []
                    media_assets[content_id].append(media)
        
        # Create simple script
        script = {
            "edition_type": composition.template.category,
            "total_duration": 0,
            "segments": []
        }
        
        # Add segments
        for i, group in enumerate(news_groups[:10]):  # Max 10 stories
            segment = {
                "type": "news_story",
                "title": group.name,
                "duration": 30,
                "narration": group.description[:200]
            }
            script["segments"].append(segment)
            script["total_duration"] += 30
        
        return {
            "script": script,
            "media_assets": media_assets,
            "composition_plan": {},
            "video_segments": []
        }
    
    async def _generate_video(
        self,
        edition_data: Dict[str, Any],
        composition: CompositionProject,
        style: str,
        tone: str,
        visual_style: str,
        language: str,
        output_filename: Optional[str]
    ) -> str:
        """Generate final video"""
        
        # Create mission from script
        script = edition_data["script"]
        segments = script["segments"]
        
        mission = f"Create a {style} {script['edition_type']} news video with {len(segments)} stories. "
        for i, seg in enumerate(segments[:3]):
            mission += f"Story {i+1}: {seg.get('title', 'News')}. "
        
        # Store edition data in session
        self.session_manager.session_data["edition_data"] = edition_data
        self.session_manager.session_data["composition"] = composition
        
        # Video parameters
        video_params = {
            "mission": mission,
            "category": "News",
            "platform": "youtube",
            "duration": int(script["total_duration"]),
            "style": style,
            "tone": tone,
            "visual_style": visual_style,
            "languages": [language],
            "theme": "news_edition",
            "discussions": "enhanced" if edition_data.get("agent_insights") else "simple",
            "mode": "enhanced",
            "voice": self._get_voice_for_language(language),
            "veo_model_order": "veo3-fast,veo3,veo2",
            "business_name": composition.name,
            "show_business_info": True
        }
        
        # Generate video
        output_path = await generate_viral_video(**video_params)
        
        if output_filename and output_path:
            import shutil
            final_path = os.path.join(self.output_dir, output_filename)
            shutil.move(output_path, final_path)
            return final_path
        
        return output_path
    
    def _get_voice_for_language(self, language: str) -> str:
        """Get voice for language"""
        voices = {
            "en": "en-US-Standard-D",
            "he": "he-IL-Standard-A",
            "es": "es-US-Standard-B",
            "fr": "fr-FR-Standard-D"
        }
        return voices.get(language, "en-US-Standard-D")


# Convenience functions
async def create_news_edition_from_csv(
    csv_path: str,
    edition_type: str = "general",
    **kwargs
) -> str:
    """Create news edition from CSV file"""
    aggregator = NewsAggregatorV2()
    return await aggregator.create_news_edition_from_csv(
        csv_path,
        edition_type,
        **kwargs
    )


async def create_news_edition_from_sources(
    sources: List[str],
    edition_type: str = "general",
    **kwargs
) -> str:
    """Create news edition from URL sources"""
    aggregator = NewsAggregatorV2()
    return await aggregator.create_news_edition_from_sources(
        sources,
        edition_type,
        **kwargs
    )