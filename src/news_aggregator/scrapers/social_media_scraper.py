"""Social Media Scraper for various platforms"""

import aiohttp
import asyncio
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlparse, parse_qs

from ...utils.logging_config import get_logger
from ..models.content_models import (
    ContentItem, NewsSource, MediaAsset,
    AssetType, SourceType, ContentStatus
)
from .base_scraper import BaseScraper

logger = get_logger(__name__)


class SocialMediaScraper(BaseScraper):
    """Scraper for social media platforms (Telegram, Instagram, Twitter, etc.)"""
    
    def __init__(self):
        self.supported_platforms = {
            "telegram": self._scrape_telegram,
            "instagram": self._scrape_instagram,
            "twitter": self._scrape_twitter,
            "facebook": self._scrape_facebook,
            "reddit": self._scrape_reddit
        }
    
    async def scrape(self, source: NewsSource) -> List[ContentItem]:
        """Scrape content from social media source"""
        if source.source_type != SourceType.SOCIAL_MEDIA:
            raise ValueError(f"Invalid source type: {source.source_type}")
        
        # Determine platform from URL
        platform = self._detect_platform(source.url)
        if not platform:
            logger.error(f"Unsupported social media platform: {source.url}")
            return []
        
        logger.info(f"Scraping {platform} source: {source.url}")
        
        # Call platform-specific scraper
        scraper_func = self.supported_platforms.get(platform)
        if scraper_func:
            return await scraper_func(source)
        
        return []
    
    async def validate_source(self, source: NewsSource) -> bool:
        """Validate if social media source is accessible"""
        try:
            # Basic URL validation
            parsed = urlparse(source.url)
            return bool(parsed.scheme and parsed.netloc)
        except:
            return False
    
    def _detect_platform(self, url: str) -> Optional[str]:
        """Detect social media platform from URL"""
        url_lower = url.lower()
        
        if "telegram" in url_lower or "t.me" in url_lower:
            return "telegram"
        elif "instagram" in url_lower:
            return "instagram"
        elif "twitter" in url_lower or "x.com" in url_lower:
            return "twitter"
        elif "facebook" in url_lower or "fb.com" in url_lower:
            return "facebook"
        elif "reddit" in url_lower:
            return "reddit"
        
        return None
    
    async def _scrape_telegram(self, source: NewsSource) -> List[ContentItem]:
        """Scrape Telegram channel/group"""
        articles = []
        
        try:
            # Parse Telegram URL
            # Format: https://t.me/channel_name or https://t.me/s/channel_name
            parsed = urlparse(source.url)
            path_parts = parsed.path.strip('/').split('/')
            
            if not path_parts:
                return []
            
            channel_name = path_parts[-1] if path_parts[-1] != 's' else path_parts[-2]
            
            # Use Telegram preview page (t.me/s/channel)
            preview_url = f"https://t.me/s/{channel_name}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(preview_url, timeout=30) as response:
                    if response.status != 200:
                        logger.error(f"Failed to access Telegram channel: {channel_name}")
                        return []
                    
                    html = await response.text()
            
            # Parse messages from preview page
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find message containers
            messages = soup.select('.tgme_widget_message')
            
            for msg in messages[:source.scraping_config.max_items]:
                try:
                    # Extract message content
                    content_elem = msg.select_one('.tgme_widget_message_text')
                    if not content_elem:
                        continue
                    
                    content = content_elem.get_text(strip=True)
                    if len(content) < 20:  # Skip very short messages
                        continue
                    
                    # Extract date
                    date_elem = msg.select_one('.tgme_widget_message_date time')
                    published_date = self._parse_telegram_date(date_elem)
                    
                    # Extract media
                    media_assets = self._extract_telegram_media(msg)
                    
                    # Extract views
                    views_elem = msg.select_one('.tgme_widget_message_views')
                    views = self._parse_views(views_elem.get_text(strip=True)) if views_elem else 0
                    
                    # Create content item
                    article = ContentItem(
                        id="",
                        source=source,
                        title=content[:100] + "..." if len(content) > 100 else content,
                        content=content,
                        media_assets=media_assets,
                        published_date=published_date,
                        url=msg.get('data-post', preview_url),
                        status=ContentStatus.SCRAPED,
                        language=self._detect_language(content),
                        metadata={
                            "views": views,
                            "platform": "telegram",
                            "channel": channel_name
                        }
                    )
                    
                    articles.append(article)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse Telegram message: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"Failed to scrape Telegram channel: {str(e)}")
        
        return articles
    
    async def _scrape_instagram(self, source: NewsSource) -> List[ContentItem]:
        """Scrape Instagram profile/posts"""
        # Note: Instagram scraping is complex due to their anti-bot measures
        # This is a simplified implementation
        logger.warning("Instagram scraping requires authentication or API access")
        
        articles = []
        
        # Parse Instagram URL
        # Format: https://www.instagram.com/username/ or https://www.instagram.com/p/post_id/
        parsed = urlparse(source.url)
        path_parts = parsed.path.strip('/').split('/')
        
        if not path_parts:
            return []
        
        if path_parts[0] == 'p':
            # Single post
            post_id = path_parts[1] if len(path_parts) > 1 else None
            if post_id:
                article = await self._scrape_instagram_post(post_id, source)
                if article:
                    articles.append(article)
        else:
            # Profile
            username = path_parts[0]
            # Would need Instagram API or web scraping with authentication
            logger.info(f"Instagram profile scraping for {username} requires API access")
        
        return articles
    
    async def _scrape_instagram_post(self, post_id: str, source: NewsSource) -> Optional[ContentItem]:
        """Scrape single Instagram post"""
        # Simplified implementation - would need proper API access
        post_url = f"https://www.instagram.com/p/{post_id}/"
        
        try:
            # This would require proper Instagram API access or advanced scraping
            logger.warning(f"Instagram post {post_id} scraping requires API access")
            
            # Placeholder implementation
            return ContentItem(
                id="",
                source=source,
                title=f"Instagram Post {post_id}",
                content="Instagram content requires API access for proper scraping",
                url=post_url,
                status=ContentStatus.SCRAPED,
                language="en",
                metadata={
                    "platform": "instagram",
                    "post_id": post_id,
                    "requires_api": True
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to scrape Instagram post: {str(e)}")
            return None
    
    async def _scrape_twitter(self, source: NewsSource) -> List[ContentItem]:
        """Scrape Twitter/X profile or tweets"""
        # Note: Twitter API v2 requires authentication
        logger.warning("Twitter scraping requires API access with authentication")
        
        articles = []
        
        # Parse Twitter URL
        parsed = urlparse(source.url)
        path_parts = parsed.path.strip('/').split('/')
        
        if len(path_parts) >= 1:
            username = path_parts[0]
            
            # Placeholder for Twitter API implementation
            logger.info(f"Twitter profile {username} scraping requires API v2 access")
            
            # Would implement Twitter API v2 calls here
            # Example: GET /2/users/by/username/:username/tweets
        
        return articles
    
    async def _scrape_facebook(self, source: NewsSource) -> List[ContentItem]:
        """Scrape Facebook page/posts"""
        logger.warning("Facebook scraping requires Graph API access")
        
        # Facebook Graph API would be needed for proper implementation
        # This is a placeholder
        return []
    
    async def _scrape_reddit(self, source: NewsSource) -> List[ContentItem]:
        """Scrape Reddit subreddit or posts"""
        articles = []
        
        try:
            # Parse Reddit URL
            parsed = urlparse(source.url)
            path_parts = parsed.path.strip('/').split('/')
            
            if len(path_parts) >= 2 and path_parts[0] == 'r':
                subreddit = path_parts[1]
                
                # Reddit JSON API (no auth required for public data)
                api_url = f"https://www.reddit.com/r/{subreddit}/hot.json"
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (compatible; NewsAggregator/1.0)'
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(api_url, headers=headers, timeout=30) as response:
                        if response.status != 200:
                            logger.error(f"Failed to access Reddit API: {response.status}")
                            return []
                        
                        data = await response.json()
                
                # Parse Reddit posts
                posts = data.get('data', {}).get('children', [])
                
                for post in posts[:source.scraping_config.max_items]:
                    post_data = post.get('data', {})
                    
                    # Skip if no title
                    if not post_data.get('title'):
                        continue
                    
                    # Create content item
                    article = ContentItem(
                        id="",
                        source=source,
                        title=post_data['title'],
                        content=post_data.get('selftext', '') or post_data.get('title', ''),
                        url=f"https://reddit.com{post_data.get('permalink', '')}",
                        published_date=datetime.fromtimestamp(post_data.get('created_utc', 0)),
                        author=post_data.get('author'),
                        status=ContentStatus.SCRAPED,
                        language="en",
                        metadata={
                            "platform": "reddit",
                            "subreddit": subreddit,
                            "score": post_data.get('score', 0),
                            "num_comments": post_data.get('num_comments', 0),
                            "upvote_ratio": post_data.get('upvote_ratio', 0),
                            "is_video": post_data.get('is_video', False),
                            "post_hint": post_data.get('post_hint', '')
                        }
                    )
                    
                    # Add media if present
                    if post_data.get('url'):
                        media_url = post_data['url']
                        if self._is_image_url(media_url):
                            article.media_assets.append(MediaAsset(
                                id="",
                                asset_type=AssetType.IMAGE,
                                source_url=media_url
                            ))
                        elif self._is_video_url(media_url) or post_data.get('is_video'):
                            # Reddit video URLs are complex
                            if post_data.get('media'):
                                video_url = post_data['media'].get('reddit_video', {}).get('fallback_url')
                                if video_url:
                                    article.media_assets.append(MediaAsset(
                                        id="",
                                        asset_type=AssetType.VIDEO,
                                        source_url=video_url
                                    ))
                    
                    articles.append(article)
                    
        except Exception as e:
            logger.error(f"Failed to scrape Reddit: {str(e)}")
        
        return articles
    
    def _extract_telegram_media(self, message_elem) -> List[MediaAsset]:
        """Extract media from Telegram message"""
        media_assets = []
        
        # Images
        for img in message_elem.select('.tgme_widget_message_photo_wrap img'):
            src = img.get('src', '')
            if src:
                asset = MediaAsset(
                    id="",
                    asset_type=AssetType.IMAGE,
                    source_url=src
                )
                media_assets.append(asset)
        
        # Videos
        video_elem = message_elem.select_one('.tgme_widget_message_video_wrap')
        if video_elem:
            # Telegram videos are more complex to extract
            # This is a placeholder
            media_assets.append(MediaAsset(
                id="",
                asset_type=AssetType.VIDEO,
                source_url="",
                metadata={"requires_processing": True}
            ))
        
        return media_assets
    
    def _parse_telegram_date(self, date_elem) -> datetime:
        """Parse Telegram date"""
        if date_elem and date_elem.get('datetime'):
            try:
                return datetime.fromisoformat(date_elem['datetime'].replace('Z', '+00:00'))
            except:
                pass
        return datetime.now()
    
    def _parse_views(self, views_text: str) -> int:
        """Parse view count from text"""
        try:
            # Remove non-numeric characters
            num_str = re.sub(r'[^\d.]', '', views_text)
            
            # Handle K, M suffixes
            if 'K' in views_text:
                return int(float(num_str) * 1000)
            elif 'M' in views_text:
                return int(float(num_str) * 1000000)
            else:
                return int(float(num_str))
        except:
            return 0
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection"""
        # Hebrew
        if re.search(r'[\u0590-\u05FF]', text):
            return "he"
        # Arabic
        elif re.search(r'[\u0600-\u06FF]', text):
            return "ar"
        # Cyrillic (Russian)
        elif re.search(r'[\u0400-\u04FF]', text):
            return "ru"
        # Default to English
        return "en"
    
    def _is_image_url(self, url: str) -> bool:
        """Check if URL points to an image"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
        return any(url.lower().endswith(ext) for ext in image_extensions)
    
    def _is_video_url(self, url: str) -> bool:
        """Check if URL points to a video"""
        video_extensions = ['.mp4', '.webm', '.mov', '.avi', '.mkv']
        return any(url.lower().endswith(ext) for ext in video_extensions)