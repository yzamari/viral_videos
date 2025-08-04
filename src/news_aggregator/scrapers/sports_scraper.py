"""Sports Video Scraper - Gets actual sports highlights and fail videos"""

import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

from ...utils.logging_config import get_logger
from ..models.content_models import (
    ContentItem, NewsSource, MediaAsset,
    AssetType, SourceType, ContentStatus
)
from .base_scraper import BaseScraper

logger = get_logger(__name__)


class SportsScraper(BaseScraper):
    """Scraper for sports videos and highlights"""
    
    def __init__(self):
        self.sources = {
            "reddit_sports": "https://www.reddit.com/r/sports/top/.json?t=day",
            "reddit_fails": "https://www.reddit.com/r/SportsFails/top/.json?t=week",
            "reddit_highlights": "https://www.reddit.com/r/sportshighlights/hot/.json",
            "reddit_funny": "https://www.reddit.com/r/funny/search.json?q=sports&sort=top&t=week"
        }
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; SportsAggregator/1.0)'
        }
    
    async def scrape_sports_videos(self, max_items: int = 20) -> List[ContentItem]:
        """Scrape sports videos from multiple sources"""
        
        all_content = []
        
        # Scrape each source
        for source_name, url in self.sources.items():
            try:
                items = await self._scrape_reddit_source(source_name, url, max_items)
                all_content.extend(items)
            except Exception as e:
                logger.error(f"Failed to scrape {source_name}: {str(e)}")
        
        # Sort by relevance/score
        all_content.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return all_content[:max_items]
    
    async def _scrape_reddit_source(
        self,
        source_name: str,
        url: str,
        max_items: int
    ) -> List[ContentItem]:
        """Scrape Reddit source for sports content"""
        
        content_items = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status != 200:
                        return []
                    
                    data = await response.json()
            
            # Parse posts
            posts = data.get('data', {}).get('children', [])
            
            for post in posts[:max_items]:
                post_data = post.get('data', {})
                
                # Check if it has video/media
                if not self._has_media(post_data):
                    continue
                
                # Create content item
                item = self._create_content_item(post_data, source_name)
                if item:
                    content_items.append(item)
            
        except Exception as e:
            logger.error(f"Error scraping {source_name}: {str(e)}")
        
        return content_items
    
    def _has_media(self, post_data: Dict[str, Any]) -> bool:
        """Check if post has video or image media"""
        
        # Reddit video
        if post_data.get('is_video'):
            return True
        
        # External video links
        url = post_data.get('url', '')
        video_domains = ['youtube.com', 'youtu.be', 'streamable.com', 'gfycat.com', 
                        'v.redd.it', 'imgur.com', 'twitter.com']
        
        if any(domain in url for domain in video_domains):
            return True
        
        # Image content
        if post_data.get('post_hint') in ['image', 'hosted:video']:
            return True
        
        # Gallery
        if post_data.get('is_gallery'):
            return True
        
        return False
    
    def _create_content_item(
        self,
        post_data: Dict[str, Any],
        source_name: str
    ) -> Optional[ContentItem]:
        """Create content item from Reddit post"""
        
        try:
            # Create source
            source = NewsSource(
                id=f"reddit_{source_name}",
                name=f"Reddit {source_name}",
                source_type=SourceType.SOCIAL_MEDIA,
                url=f"https://reddit.com{post_data.get('permalink', '')}"
            )
            
            # Extract media
            media_assets = self._extract_media(post_data)
            
            if not media_assets:
                return None
            
            # Calculate relevance based on score and comments
            score = post_data.get('score', 0)
            num_comments = post_data.get('num_comments', 0)
            relevance = min(1.0, (score / 10000) + (num_comments / 1000))
            
            # Boost for recent content
            created = post_data.get('created_utc', 0)
            age_hours = (datetime.now().timestamp() - created) / 3600
            if age_hours < 24:
                relevance += 0.2
            
            # Create content item
            item = ContentItem(
                id=f"reddit_{post_data.get('id', '')}",
                source=source,
                title=post_data.get('title', ''),
                content=post_data.get('selftext', '') or post_data.get('title', ''),
                media_assets=media_assets,
                published_date=datetime.fromtimestamp(created),
                author=post_data.get('author', 'unknown'),
                url=post_data.get('url', ''),
                status=ContentStatus.SCRAPED,
                relevance_score=min(1.0, relevance),
                metadata={
                    "score": score,
                    "comments": num_comments,
                    "subreddit": post_data.get('subreddit', ''),
                    "is_video": post_data.get('is_video', False),
                    "post_hint": post_data.get('post_hint', '')
                },
                tags=self._extract_tags(post_data),
                categories=["sports", "entertainment"]
            )
            
            return item
            
        except Exception as e:
            logger.error(f"Failed to create content item: {str(e)}")
            return None
    
    def _extract_media(self, post_data: Dict[str, Any]) -> List[MediaAsset]:
        """Extract media assets from Reddit post"""
        
        media_assets = []
        
        # Reddit hosted video
        if post_data.get('is_video') and post_data.get('media'):
            reddit_video = post_data['media'].get('reddit_video', {})
            if reddit_video.get('fallback_url'):
                media_assets.append(MediaAsset(
                    id=f"reddit_video_{post_data.get('id')}",
                    asset_type=AssetType.VIDEO,
                    source_url=reddit_video['fallback_url'],
                    duration=reddit_video.get('duration', 0),
                    metadata={
                        "width": reddit_video.get('width'),
                        "height": reddit_video.get('height'),
                        "has_audio": not reddit_video.get('is_gif', False)
                    }
                ))
        
        # Direct media URL
        url = post_data.get('url', '')
        
        # Image
        if self._is_image_url(url):
            media_assets.append(MediaAsset(
                id=f"reddit_img_{post_data.get('id')}",
                asset_type=AssetType.IMAGE,
                source_url=url
            ))
        
        # Video platforms
        elif 'youtube.com' in url or 'youtu.be' in url:
            media_assets.append(MediaAsset(
                id=f"youtube_{post_data.get('id')}",
                asset_type=AssetType.VIDEO,
                source_url=url,
                metadata={"platform": "youtube"}
            ))
        
        elif 'streamable.com' in url:
            media_assets.append(MediaAsset(
                id=f"streamable_{post_data.get('id')}",
                asset_type=AssetType.VIDEO,
                source_url=url,
                metadata={"platform": "streamable"}
            ))
        
        # Gallery images
        if post_data.get('is_gallery') and post_data.get('gallery_data'):
            for item in post_data['gallery_data'].get('items', []):
                media_id = item.get('media_id')
                if media_id:
                    # Reddit gallery URL format
                    img_url = f"https://i.redd.it/{media_id}.jpg"
                    media_assets.append(MediaAsset(
                        id=f"gallery_{media_id}",
                        asset_type=AssetType.IMAGE,
                        source_url=img_url
                    ))
        
        # Preview images
        if not media_assets and post_data.get('preview'):
            images = post_data['preview'].get('images', [])
            if images:
                source = images[0].get('source', {})
                if source.get('url'):
                    # Decode Reddit preview URL
                    url = source['url'].replace('&amp;', '&')
                    media_assets.append(MediaAsset(
                        id=f"preview_{post_data.get('id')}",
                        asset_type=AssetType.IMAGE,
                        source_url=url
                    ))
        
        return media_assets
    
    def _extract_tags(self, post_data: Dict[str, Any]) -> List[str]:
        """Extract tags from post"""
        
        tags = []
        title = post_data.get('title', '').lower()
        
        # Sport types
        sports = ['football', 'basketball', 'soccer', 'baseball', 'hockey',
                 'tennis', 'golf', 'boxing', 'mma', 'nfl', 'nba', 'mlb']
        
        for sport in sports:
            if sport in title:
                tags.append(sport)
        
        # Content types
        if any(word in title for word in ['fail', 'blooper', 'mistake', 'error']):
            tags.append('fails')
        
        if any(word in title for word in ['highlight', 'amazing', 'best', 'top']):
            tags.append('highlights')
        
        if any(word in title for word in ['funny', 'hilarious', 'lol', 'comedy']):
            tags.append('funny')
        
        # Add subreddit as tag
        subreddit = post_data.get('subreddit', '')
        if subreddit:
            tags.append(f"r/{subreddit}")
        
        return tags
    
    def _is_image_url(self, url: str) -> bool:
        """Check if URL is an image"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        return any(url.lower().endswith(ext) for ext in image_extensions)
    
    async def scrape(self, source: NewsSource) -> List[ContentItem]:
        """Implementation of abstract method"""
        return await self.scrape_sports_videos()
    
    async def validate_source(self, source: NewsSource) -> bool:
        """Implementation of abstract method"""
        return True  # Reddit is generally available


async def scrape_funny_sports_videos(max_items: int = 20) -> List[ContentItem]:
    """Convenience function to scrape funny sports videos"""
    scraper = SportsScraper()
    return await scraper.scrape_sports_videos(max_items)