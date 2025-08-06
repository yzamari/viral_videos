"""News Aggregator using SCRAPED MEDIA ONLY - NO VEO Generation"""

import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
import os

from ..utils.logging_config import get_logger
from ..utils.session_manager import SessionManager

from .scrapers.cnn_scraper import CNNScraper
from .scrapers.israeli_scrapers import YnetScraper
from .scrapers.social_media_scraper import SocialMediaScraper

from .processors.content_analyzer import ContentAnalyzer
from .processors.news_grouper import NewsGrouper
from .processors.media_downloader import MediaDownloader
from ..ai.manager import AIServiceManager
from ..core.decision_framework import DecisionFramework

from .composers.news_edition_composer import NewsEditionComposer
from .composers.scraped_media_composer import ScrapedMediaComposer

from .models.content_models import ContentItem, ContentStatus, NewsSource, SourceType

logger = get_logger(__name__)


class ScrapedMediaNewsAggregator:
    """News aggregator that uses ONLY scraped media - NO VEO generation"""
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.media_downloader = MediaDownloader()
        self.ai_manager = AIServiceManager()
        self.decision_framework = DecisionFramework()
        self.content_analyzer = ContentAnalyzer(self.ai_manager)
        self.news_grouper = NewsGrouper(self.ai_manager)
        self.edition_composer = NewsEditionComposer(
            self.session_manager,
            self.ai_manager,
            self.decision_framework,
            self.media_downloader
        )
        self.scraped_media_composer = ScrapedMediaComposer(
            self.session_manager,
            self.media_downloader
        )
        
        # Initialize scrapers
        self.scrapers = {
            'cnn': CNNScraper(),
            'ynet': YnetScraper(),
            'social': SocialMediaScraper()
        }
    
    async def create_news_edition_from_sources(
        self,
        source_urls: List[str],
        edition_type: str = "general",
        style: str = "professional", 
        tone: str = "informative",
        duration_minutes: int = 5,
        language: str = "en",
        output_filename: Optional[str] = None
    ) -> str:
        """Create news edition video using ONLY scraped media"""
        
        logger.info("🎬 Creating news edition using SCRAPED MEDIA ONLY")
        logger.info("📸 NO VEO/AI video generation will be used")
        logger.info(f"📰 Sources: {source_urls}")
        
        # 1. Scrape content from sources
        logger.info("🔍 Scraping news content...")
        all_content = await self._scrape_all_sources(source_urls)
        
        if not all_content:
            raise ValueError("No content found from sources!")
        
        logger.info(f"✅ Scraped {len(all_content)} articles with media")
        
        # 2. Analyze content
        logger.info("🧠 Analyzing content...")
        for content in all_content:
            await self.content_analyzer.analyze(content)
        
        # 3. Group related news
        logger.info("🔗 Grouping related stories...")
        news_groups = await self.news_grouper.group_content(all_content)
        
        # 4. AI agent discussions for editorial decisions
        logger.info("🤖 AI agents discussing editorial flow...")
        edition_plan = await self.edition_composer.create_edition_plan(
            news_groups,
            edition_type=edition_type,
            target_duration=duration_minutes * 60,
            style=style,
            tone=tone
        )
        
        # 5. Select best content with media
        selected_content = self._select_best_content_with_media(
            all_content,
            edition_plan,
            duration_minutes
        )
        
        # 6. Create video using ONLY scraped media
        logger.info("🎥 Creating video from scraped media...")
        output_path = await self.scraped_media_composer.create_video_from_scraped_media(
            content_items=selected_content,
            duration_seconds=duration_minutes * 60,
            style=self._map_style_to_video_style(style),
            output_filename=output_filename
        )
        
        logger.info(f"✅ News edition created: {output_path}")
        logger.info("📸 Used ONLY scraped media - NO AI generation")
        
        return output_path
    
    async def _scrape_all_sources(self, source_urls: List[str]) -> List[ContentItem]:
        """Scrape content from all sources"""
        all_content = []
        
        for url in source_urls:
            try:
                # Determine scraper based on URL
                if 'cnn.com' in url:
                    scraper = self.scrapers['cnn']
                elif 'ynet.co.il' in url:
                    scraper = self.scrapers['ynet']
                elif any(social in url for social in ['reddit.com', 't.me', 'telegram']):
                    scraper = self.scrapers['social']
                else:
                    logger.warning(f"No specific scraper for {url}, skipping")
                    continue
                
                # Create source
                source = NewsSource(
                    id=url.replace('https://', '').replace('/', '_'),
                    name=self._extract_source_name(url),
                    source_type=SourceType.WEB,
                    url=url
                )
                
                # Scrape content
                content = await scraper.scrape(source)
                
                # Filter for content with media
                content_with_media = [
                    item for item in content 
                    if item.media_assets and len(item.media_assets) > 0
                ]
                
                all_content.extend(content_with_media)
                logger.info(f"✅ Scraped {len(content_with_media)} articles with media from {url}")
                
            except Exception as e:
                logger.error(f"Failed to scrape {url}: {str(e)}")
        
        return all_content
    
    def _select_best_content_with_media(
        self,
        all_content: List[ContentItem],
        edition_plan: Dict[str, Any],
        duration_minutes: int
    ) -> List[ContentItem]:
        """Select best content that has media assets"""
        
        # Sort by relevance and media quality
        scored_content = []
        
        for content in all_content:
            # Calculate score based on relevance and media
            score = content.relevance_score
            
            # Boost for video content
            has_video = any(asset.asset_type.value == 'video' for asset in content.media_assets)
            if has_video:
                score += 0.3
            
            # Boost for multiple media assets
            media_count = len(content.media_assets)
            score += min(0.2, media_count * 0.05)
            
            # Consider edition plan priorities
            if edition_plan and content.categories:
                for category in content.categories:
                    if category in edition_plan.get('priority_topics', []):
                        score += 0.2
            
            scored_content.append((score, content))
        
        # Sort by score
        scored_content.sort(key=lambda x: x[0], reverse=True)
        
        # Select top content based on duration
        # Estimate ~30 seconds per story
        num_stories = min(len(scored_content), duration_minutes * 2)
        
        selected = [content for _, content in scored_content[:num_stories]]
        
        logger.info(f"📰 Selected {len(selected)} stories with media for {duration_minutes} minute video")
        
        return selected
    
    def _extract_source_name(self, url: str) -> str:
        """Extract source name from URL"""
        if 'cnn.com' in url:
            return 'CNN'
        elif 'ynet.co.il' in url:
            return 'Ynet'
        elif 'reddit.com' in url:
            return 'Reddit'
        elif 't.me' in url or 'telegram' in url:
            return 'Telegram'
        else:
            # Extract domain name
            domain = url.replace('https://', '').replace('http://', '').split('/')[0]
            return domain.split('.')[0].title()
    
    def _map_style_to_video_style(self, style: str) -> str:
        """Map news style to video composition style"""
        style_mapping = {
            'professional': 'normal',
            'casual': 'fast-paced',
            'humorous': 'fast-paced',
            'dramatic': 'dramatic'
        }
        return style_mapping.get(style, 'normal')


async def create_scraped_media_news_edition(
    source_urls: List[str],
    **kwargs
) -> str:
    """Create news edition using scraped media only"""
    aggregator = ScrapedMediaNewsAggregator()
    return await aggregator.create_news_edition_from_sources(
        source_urls,
        **kwargs
    )