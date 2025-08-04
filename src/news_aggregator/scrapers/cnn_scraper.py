"""CNN News Scraper"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re

from ...utils.logging_config import get_logger
from ..models.content_models import (
    ContentItem, NewsSource, MediaAsset,
    AssetType, SourceType, ContentStatus
)
from .web_scraper import WebNewsScraper

logger = get_logger(__name__)


class CNNScraper(WebNewsScraper):
    """Scraper for CNN.com news articles"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.cnn.com"
        
        # CNN-specific selectors
        self.cnn_config = {
            "homepage": {
                "article_links": "a[href*='/2024/'], a[href*='/2025/']",
                "top_stories": ".container__headline",
                "featured": ".card--media__content",
                "sections": {
                    "politics": "/politics",
                    "business": "/business", 
                    "tech": "/business/tech",
                    "entertainment": "/entertainment",
                    "sports": "/sport"
                }
            },
            "article": {
                "title": "h1.headline__text",
                "content": ".article__content p, .paragraph",
                "image": ".image__container img, .media__image img",
                "video": ".pui-video-player, video",
                "author": ".byline__name",
                "date": ".timestamp",
                "category": ".article__category"
            }
        }
    
    async def scrape_cnn_homepage(self, max_articles: int = 20) -> List[ContentItem]:
        """Scrape CNN homepage for latest articles"""
        logger.info("Scraping CNN homepage...")
        
        articles = []
        
        try:
            # Get homepage HTML
            html = await self._fetch_url(self.base_url)
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find article links
            article_links = set()
            
            # Get links from different sections
            link_selectors = [
                self.cnn_config["homepage"]["article_links"],
                ".container__headline a",
                ".card--media a",
                ".zone a[href]"
            ]
            
            for selector in link_selectors:
                for link in soup.select(selector)[:max_articles]:
                    href = link.get('href', '')
                    if href and self._is_article_url(href):
                        full_url = self._make_full_url(href)
                        article_links.add(full_url)
            
            logger.info(f"Found {len(article_links)} article links")
            
            # Scrape each article
            tasks = [self._scrape_cnn_article(url) for url in list(article_links)[:max_articles]]
            article_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in article_results:
                if isinstance(result, ContentItem):
                    articles.append(result)
                elif isinstance(result, Exception):
                    logger.warning(f"Failed to scrape article: {str(result)}")
            
        except Exception as e:
            logger.error(f"Failed to scrape CNN homepage: {str(e)}")
        
        return articles
    
    async def scrape_cnn_section(self, section: str, max_articles: int = 10) -> List[ContentItem]:
        """Scrape specific CNN section"""
        section_path = self.cnn_config["homepage"]["sections"].get(section, f"/{section}")
        section_url = f"{self.base_url}{section_path}"
        
        logger.info(f"Scraping CNN section: {section}")
        
        try:
            html = await self._fetch_url(section_url)
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find article links in section
            article_links = set()
            for link in soup.select("a[href*='/2024/'], a[href*='/2025/']")[:max_articles * 2]:
                href = link.get('href', '')
                if href and self._is_article_url(href):
                    full_url = self._make_full_url(href)
                    article_links.add(full_url)
            
            # Scrape articles
            articles = []
            for url in list(article_links)[:max_articles]:
                try:
                    article = await self._scrape_cnn_article(url)
                    if article:
                        article.categories.append(section)
                        articles.append(article)
                except Exception as e:
                    logger.warning(f"Failed to scrape {url}: {str(e)}")
            
            return articles
            
        except Exception as e:
            logger.error(f"Failed to scrape CNN section {section}: {str(e)}")
            return []
    
    async def _scrape_cnn_article(self, url: str) -> Optional[ContentItem]:
        """Scrape individual CNN article"""
        try:
            html = await self._fetch_url(url)
            soup = BeautifulSoup(html, 'html.parser')
            
            config = self.cnn_config["article"]
            
            # Extract title
            title_elem = soup.select_one(config["title"])
            if not title_elem:
                return None
            title = title_elem.get_text(strip=True)
            
            # Extract content
            content_elems = soup.select(config["content"])
            content = "\n".join([p.get_text(strip=True) for p in content_elems])
            
            # Skip if content is too short
            if len(content) < 100:
                return None
            
            # Extract media
            media_assets = await self._extract_cnn_media(soup, url)
            
            # Extract metadata
            author = self._extract_text(soup, config["author"])
            date_text = self._extract_text(soup, config["date"])
            published_date = self._parse_cnn_date(date_text)
            category = self._extract_text(soup, config["category"])
            
            # Create content item
            source = NewsSource(
                id="cnn_main",
                name="CNN",
                source_type=SourceType.WEB,
                url=self.base_url
            )
            
            article = ContentItem(
                id="",
                source=source,
                title=title,
                content=content,
                media_assets=media_assets,
                published_date=published_date,
                author=author,
                url=url,
                status=ContentStatus.SCRAPED,
                language="en"
            )
            
            # Add category if found
            if category:
                article.categories.append(category)
            
            # Add metadata for interest scoring
            article.metadata["has_video"] = any(
                asset.asset_type == AssetType.VIDEO for asset in media_assets
            )
            article.metadata["content_length"] = len(content)
            article.metadata["is_breaking"] = "breaking" in title.lower() or "breaking" in url
            
            return article
            
        except Exception as e:
            logger.error(f"Failed to scrape CNN article {url}: {str(e)}")
            return None
    
    async def _extract_cnn_media(self, soup: BeautifulSoup, base_url: str) -> List[MediaAsset]:
        """Extract media assets from CNN article"""
        media_assets = []
        
        # Extract images
        image_selectors = [
            ".image__container img",
            ".media__image img",
            ".image__dam-img",
            "picture img"
        ]
        
        for selector in image_selectors:
            for img in soup.select(selector):
                src = img.get('src', img.get('data-src', ''))
                if src and not src.startswith('data:'):
                    # CNN uses responsive images
                    if 'w_' in src:
                        # Get highest quality version
                        src = re.sub(r'w_\d+', 'w_1920', src)
                    
                    asset = MediaAsset(
                        id="",
                        asset_type=AssetType.IMAGE,
                        source_url=src,
                        metadata={
                            "alt_text": img.get('alt', ''),
                            "caption": self._find_image_caption(img)
                        }
                    )
                    media_assets.append(asset)
        
        # Extract videos
        video_containers = soup.select(".pui-video-player, .video-resource")
        for container in video_containers:
            video_id = container.get('data-video-id', '')
            if video_id:
                # CNN video URLs typically follow a pattern
                video_url = f"https://www.cnn.com/videos/{video_id}"
                asset = MediaAsset(
                    id="",
                    asset_type=AssetType.VIDEO,
                    source_url=video_url,
                    metadata={
                        "video_id": video_id,
                        "title": container.get('data-video-title', '')
                    }
                )
                media_assets.append(asset)
        
        return media_assets
    
    def _is_article_url(self, url: str) -> bool:
        """Check if URL is a CNN article"""
        # CNN article URLs contain date pattern
        article_pattern = r'/\d{4}/\d{2}/\d{2}/'
        return bool(re.search(article_pattern, url))
    
    def _make_full_url(self, url: str) -> str:
        """Convert relative URL to full URL"""
        if url.startswith('http'):
            return url
        elif url.startswith('//'):
            return f"https:{url}"
        elif url.startswith('/'):
            return f"{self.base_url}{url}"
        else:
            return f"{self.base_url}/{url}"
    
    def _extract_text(self, soup: BeautifulSoup, selector: str) -> Optional[str]:
        """Extract text from selector"""
        elem = soup.select_one(selector)
        return elem.get_text(strip=True) if elem else None
    
    def _parse_cnn_date(self, date_text: Optional[str]) -> datetime:
        """Parse CNN date format"""
        if not date_text:
            return datetime.now()
        
        try:
            # CNN uses various date formats
            # Try common patterns
            patterns = [
                "%B %d, %Y",  # January 1, 2024
                "%b %d, %Y",  # Jan 1, 2024
                "%Y-%m-%d",   # 2024-01-01
            ]
            
            for pattern in patterns:
                try:
                    return datetime.strptime(date_text.strip(), pattern)
                except:
                    continue
            
            # If no pattern matches, try to extract relative time
            if "hour" in date_text.lower():
                hours = int(re.search(r'(\d+)', date_text).group(1))
                return datetime.now() - timedelta(hours=hours)
            elif "minute" in date_text.lower():
                minutes = int(re.search(r'(\d+)', date_text).group(1))
                return datetime.now() - timedelta(minutes=minutes)
                
        except:
            pass
        
        return datetime.now()
    
    def _find_image_caption(self, img_elem) -> Optional[str]:
        """Find caption for image"""
        # Look for caption in parent figure
        parent = img_elem.find_parent('figure')
        if parent:
            caption = parent.find('figcaption')
            if caption:
                return caption.get_text(strip=True)
        
        # Look for nearby caption elements
        next_elem = img_elem.find_next_sibling()
        if next_elem and next_elem.name in ['figcaption', 'div', 'p']:
            if 'caption' in next_elem.get('class', []):
                return next_elem.get_text(strip=True)
        
        return None