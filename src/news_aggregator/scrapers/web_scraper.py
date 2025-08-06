"""Web scraper for news websites"""

import aiohttp
import asyncio
import ssl
import certifi
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from urllib.parse import urljoin, urlparse
import hashlib
import re
import os

from ...utils.logging_config import get_logger
from ..models.content_models import (
    ContentItem, NewsSource, MediaAsset, 
    AssetType, SourceType, ContentStatus
)
from .base_scraper import BaseScraper

logger = get_logger(__name__)


class WebNewsScraper(BaseScraper):
    """Scraper for news websites"""
    
    def __init__(self, media_cache_dir: str = "outputs/news_media_cache"):
        self.media_cache_dir = media_cache_dir
        os.makedirs(media_cache_dir, exist_ok=True)
        
        # Site-specific selectors
        self.site_configs = {
            "bbc.com": {
                "article_selector": "article, .media-article",
                "title_selector": "h1",
                "content_selector": ".article__body, .story-body__inner",
                "image_selector": "img[src*='/news/'], .image-block img",
                "video_selector": "video, .media-player",
                "date_selector": "time[datetime]",
                "author_selector": ".byline__name"
            },
            "ynet.co.il": {
                "article_selector": ".article-wrap, .element-article",
                "title_selector": "h1, .element-title",
                "content_selector": ".element-preview, .article-body",
                "image_selector": ".element-image img, figure img",
                "video_selector": ".video-element, video",
                "date_selector": ".element-time, time",
                "author_selector": ".element-author"
            },
            "default": {
                "article_selector": "article, main, .content",
                "title_selector": "h1",
                "content_selector": "p",
                "image_selector": "img",
                "video_selector": "video",
                "date_selector": "time",
                "author_selector": ".author, .byline"
            }
        }
    
    async def scrape(self, source: NewsSource) -> List[ContentItem]:
        """Scrape news articles from web source"""
        if source.source_type != SourceType.WEB:
            raise ValueError(f"Invalid source type: {source.source_type}")
        
        logger.info(f"Scraping web source: {source.url}")
        
        try:
            # Get the HTML content
            html = await self._fetch_url(source.url)
            
            # Parse the page
            soup = BeautifulSoup(html, 'html.parser')
            
            # Get site-specific config
            domain = urlparse(source.url).netloc
            config = self._get_site_config(domain)
            
            # Extract articles
            articles = await self._extract_articles(soup, source, config)
            
            logger.info(f"Scraped {len(articles)} articles from {source.url}")
            return articles
            
        except Exception as e:
            logger.error(f"Failed to scrape {source.url}: {str(e)}")
            return []
    
    async def validate_source(self, source: NewsSource) -> bool:
        """Check if source URL is accessible"""
        try:
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.head(source.url, timeout=10) as response:
                    return response.status == 200
        except:
            return False
    
    def _get_site_config(self, domain: str) -> Dict[str, str]:
        """Get site-specific configuration"""
        for key in self.site_configs:
            if key in domain:
                return self.site_configs[key]
        return self.site_configs["default"]
    
    async def _fetch_url(self, url: str) -> str:
        """Fetch URL content"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(url, headers=headers, timeout=30) as response:
                response.raise_for_status()
                return await response.text()
    
    async def _extract_articles(
        self, 
        soup: BeautifulSoup, 
        source: NewsSource,
        config: Dict[str, str]
    ) -> List[ContentItem]:
        """Extract articles from page"""
        articles = []
        
        # Find article containers
        article_elements = soup.select(config["article_selector"])
        
        for element in article_elements[:source.scraping_config.max_items]:
            try:
                article = await self._parse_article(element, source, config)
                if article and self._is_valid_article(article):
                    articles.append(article)
            except Exception as e:
                logger.warning(f"Failed to parse article: {str(e)}")
        
        return articles
    
    async def _parse_article(
        self,
        element: BeautifulSoup,
        source: NewsSource,
        config: Dict[str, str]
    ) -> Optional[ContentItem]:
        """Parse a single article element"""
        
        # Extract title
        title_elem = element.select_one(config["title_selector"])
        if not title_elem:
            return None
        title = title_elem.get_text(strip=True)
        
        # Extract content
        content_elems = element.select(config["content_selector"])
        content = "\n".join([p.get_text(strip=True) for p in content_elems])
        
        # Extract media
        media_assets = await self._extract_media(element, source.url, config)
        
        # Extract date
        published_date = self._extract_date(element, config)
        
        # Extract author
        author_elem = element.select_one(config["author_selector"])
        author = author_elem.get_text(strip=True) if author_elem else None
        
        # Detect language
        language = self._detect_language(title + " " + content)
        
        # Create content item
        return ContentItem(
            id="",  # Will be auto-generated
            source=source,
            title=title,
            content=content,
            media_assets=media_assets,
            published_date=published_date,
            language=language,
            author=author,
            url=source.url,
            status=ContentStatus.SCRAPED
        )
    
    async def _extract_media(
        self,
        element: BeautifulSoup,
        base_url: str,
        config: Dict[str, str]
    ) -> List[MediaAsset]:
        """Extract media assets from article"""
        media_assets = []
        
        # Extract images
        for img in element.select(config["image_selector"]):
            src = img.get('src', img.get('data-src', ''))
            if src:
                full_url = urljoin(base_url, src)
                asset = MediaAsset(
                    id="",  # Will be auto-generated
                    asset_type=AssetType.IMAGE,
                    source_url=full_url,
                    metadata={
                        "alt_text": img.get('alt', ''),
                        "title": img.get('title', '')
                    }
                )
                media_assets.append(asset)
        
        # Extract videos
        for video in element.select(config["video_selector"]):
            src = video.get('src', video.get('data-src', ''))
            if src:
                full_url = urljoin(base_url, src)
                asset = MediaAsset(
                    id="",
                    asset_type=AssetType.VIDEO,
                    source_url=full_url,
                    metadata={
                        "poster": video.get('poster', '')
                    }
                )
                media_assets.append(asset)
        
        return media_assets
    
    def _extract_date(self, element: BeautifulSoup, config: Dict[str, str]) -> datetime:
        """Extract publication date"""
        date_elem = element.select_one(config["date_selector"])
        
        if date_elem:
            # Try to parse datetime attribute
            if date_elem.get('datetime'):
                try:
                    return datetime.fromisoformat(date_elem['datetime'].replace('Z', '+00:00'))
                except:
                    pass
            
            # Try to parse text content
            date_text = date_elem.get_text(strip=True)
            # Add more date parsing logic here if needed
        
        return datetime.now()
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection"""
        # Check for Hebrew characters
        if re.search(r'[\u0590-\u05FF]', text):
            return "he"
        return "en"
    
    def _is_valid_article(self, article: ContentItem) -> bool:
        """Validate article has minimum required content"""
        return (
            len(article.title) > 10 and
            len(article.content) > 50
        )
    
    async def download_media(self, media_asset: MediaAsset) -> Optional[str]:
        """Download media asset to local cache"""
        try:
            # Generate local filename
            url_hash = hashlib.md5(media_asset.source_url.encode()).hexdigest()
            ext = os.path.splitext(urlparse(media_asset.source_url).path)[1] or '.jpg'
            local_filename = f"{url_hash}{ext}"
            local_path = os.path.join(self.media_cache_dir, local_filename)
            
            # Skip if already downloaded
            if os.path.exists(local_path):
                media_asset.local_path = local_path
                return local_path
            
            # Download file
            async with aiohttp.ClientSession() as session:
                async with session.get(media_asset.source_url) as response:
                    response.raise_for_status()
                    content = await response.read()
                    
                    with open(local_path, 'wb') as f:
                        f.write(content)
            
            media_asset.local_path = local_path
            media_asset.file_size = len(content)
            
            logger.info(f"Downloaded media: {media_asset.source_url} -> {local_path}")
            return local_path
            
        except Exception as e:
            logger.error(f"Failed to download media {media_asset.source_url}: {str(e)}")
            return None