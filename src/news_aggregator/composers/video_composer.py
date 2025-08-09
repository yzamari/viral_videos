"""
NewsVideoComposer - Responsible for video composition and media handling.

This class follows the Single Responsibility Principle by focusing solely on
video creation and media asset management.
"""

import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional

from ..interfaces.aggregator_interfaces import IVideoComposer, IMediaHandler
from ..models.content_models import ContentItem, MediaAsset, AssetType, NewsSource, SourceType
from ..processors.media_downloader import MediaDownloader
from ..composers.scraped_media_composer import ScrapedMediaComposer
from ..composers.multi_language_composer import MultiLanguageComposer
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class NewsVideoComposer(IVideoComposer, IMediaHandler):
    """
    Handles video composition and media asset management.
    
    Responsibilities:
    - Downloading media assets (images, videos, YouTube content)
    - Converting between content formats
    - Creating language-specific videos
    - Managing video composition workflow
    """
    
    def __init__(
        self,
        session_manager,
        ai_manager
    ):
        """
        Initialize the video composer with required dependencies.
        
        Args:
            session_manager: Session manager for file operations
            ai_manager: AI service manager for content processing
        """
        self.session_manager = session_manager
        self.ai_manager = ai_manager
        
        # Initialize media handling components
        self.media_downloader = MediaDownloader()
        
        # Initialize video composers
        self.scraped_media_composer = ScrapedMediaComposer(
            session_manager,
            self.media_downloader
        )
        
        self.multi_language_composer = MultiLanguageComposer(
            session_manager,
            ai_manager,
            self.scraped_media_composer
        )
    
    async def download_all_media(
        self, 
        content: List[Dict[str, Any]], 
        use_youtube_videos: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Download all media assets for the content items.
        
        Args:
            content: List of content items requiring media download
            use_youtube_videos: Whether to search and download YouTube videos
            
        Returns:
            Content items with local media paths populated
        """
        logger.info(f"📥 Downloading media assets for {len(content)} items...")
        
        # Initialize YouTube enhancer if needed
        youtube_enhancer = None
        if use_youtube_videos:
            try:
                from ..scrapers.youtube_scraper import YouTubeNewsEnhancer
                youtube_enhancer = YouTubeNewsEnhancer()
                logger.info("🔍 YouTube video search enabled")
            except ImportError:
                logger.warning("YouTube enhancer not available")
        
        enhanced_content = []
        for item in content:
            enhanced_item = await self._download_item_media(
                item, 
                youtube_enhancer if use_youtube_videos else None
            )
            enhanced_content.append(enhanced_item)
        
        logger.info(f"✅ Media download completed for {len(enhanced_content)} items")
        return enhanced_content
    
    async def create_language_video(
        self,
        content: List[Dict[str, Any]],
        language: str,
        style: str,
        tone: str,
        platform: str,
        duration_seconds: int,
        overlay_style: str,
        output_dir: str,
        visual_styles: Dict[str, Any] = None,
        use_youtube_videos: bool = False,
        logo_path: str = None,
        channel_name: str = "NEWS",
        dynamic_transitions: bool = True
    ) -> str:
        """
        Create video for a specific language.
        
        Args:
            content: Content items to include in video
            language: Target language for the video
            style: Style description for video creation
            tone: Tone description for video creation
            platform: Target platform (youtube, tiktok, etc.)
            duration_seconds: Target duration in seconds
            overlay_style: Overlay style (modern, classic, minimal, news)
            output_dir: Output directory for the video
            visual_styles: Visual style configuration from AI
            use_youtube_videos: Whether YouTube videos were downloaded
            logo_path: Path to logo for branding
            channel_name: Channel name for branding
            dynamic_transitions: Whether to use dynamic transitions
            
        Returns:
            Path to the created video file
        """
        logger.info(f"🎥 Creating {language} video for {len(content)} stories...")
        
        # Convert dict format to ContentItem objects
        content_items = [self._dict_to_content_item(item) for item in content]
        
        # Determine final overlay style based on channel name
        final_overlay_style = self._determine_overlay_style(overlay_style, channel_name)
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"news_{language}_{platform}_{timestamp}.mp4"
        
        # Use multi-language composer for video creation
        output_path = await self.multi_language_composer.create_news_video(
            content_items=content_items,
            language=language,
            style=style,
            tone=tone,
            platform=platform,
            duration_seconds=duration_seconds,
            overlay_style=final_overlay_style,
            output_filename=output_filename,
            visual_styles=visual_styles or {},
            use_youtube_videos=use_youtube_videos,
            logo_path=logo_path,
            channel_name=channel_name,
            dynamic_transitions=dynamic_transitions
        )
        
        logger.info(f"✅ Video created successfully: {output_path}")
        return output_path
    
    async def _download_item_media(
        self, 
        item: Dict[str, Any], 
        youtube_enhancer=None
    ) -> Dict[str, Any]:
        """Download media for a single content item"""
        enhanced_item = item.copy()
        
        # Download images - prioritize article images over preview images
        await self._download_images(enhanced_item)
        
        # Download videos - prioritize article videos
        await self._download_videos(enhanced_item)
        
        # Search and download YouTube videos if enabled
        if youtube_enhancer:
            await self._download_youtube_content(enhanced_item, youtube_enhancer)
        
        return enhanced_item
    
    async def _download_images(self, item: Dict[str, Any]) -> None:
        """Download the best available image for an item"""
        image_to_download = None
        
        # Priority order: primary_image > article_images > image_url
        if item.get('primary_image'):
            image_to_download = item['primary_image']
            logger.debug(f"📸 Using primary image: {item['title'][:50]}...")
        elif item.get('article_images') and len(item['article_images']) > 0:
            image_to_download = item['article_images'][0]
            logger.debug(f"📸 Using article image: {item['title'][:50]}...")
        elif item.get('image_url'):
            image_to_download = item['image_url']
        
        if image_to_download:
            try:
                result = await self.media_downloader.download_media(
                    image_to_download,
                    metadata={'title': item['title'], 'source': item['source']}
                )
                if result and result.get('local_path'):
                    item['local_image'] = result.get('local_path')
                    logger.debug(f"✅ Downloaded image: {item['title'][:50]}...")
            except Exception as e:
                logger.warning(f"Failed to download image for '{item['title'][:50]}': {e}")
    
    async def _download_videos(self, item: Dict[str, Any]) -> None:
        """Download the best available video for an item"""
        video_to_download = None
        
        # Priority order: article_videos > video_url
        if item.get('article_videos') and len(item['article_videos']) > 0:
            video_to_download = item['article_videos'][0]
            logger.debug(f"🎥 Using video from article: {item['title'][:50]}...")
        elif item.get('video_url'):
            video_to_download = item['video_url']
        
        if video_to_download:
            try:
                result = await self.media_downloader.download_media(
                    video_to_download,
                    metadata={'title': item['title'], 'source': item['source']}
                )
                if result and result.get('local_path'):
                    item['local_video'] = result.get('local_path')
                    logger.debug(f"✅ Downloaded video: {item['title'][:50]}...")
            except Exception as e:
                logger.warning(f"Failed to download video for '{item['title'][:50]}': {e}")
    
    async def _download_youtube_content(self, item: Dict[str, Any], youtube_enhancer) -> None:
        """Search and download relevant YouTube videos"""
        try:
            # Create search query from title
            search_query = self._create_youtube_search_query(item['title'])
            
            logger.debug(f"🔍 Searching YouTube for: {search_query}")
            
            # Convert to format expected by YouTube enhancer
            news_items = [{'title': search_query, 'media_assets': []}]
            enhanced = await youtube_enhancer.enhance_news_items(news_items, True)
            
            if enhanced and enhanced[0].get('media_assets'):
                # Find video assets from YouTube
                for asset in enhanced[0]['media_assets']:
                    if asset.get('type') == 'video' and asset.get('source') == 'youtube':
                        item['youtube_video'] = asset['url']  # Local path to downloaded video
                        logger.debug(f"✅ Found YouTube video: {asset.get('title', 'Unknown')}")
                        break
                        
        except Exception as e:
            logger.warning(f"Failed to get YouTube video for '{item['title'][:50]}': {e}")
    
    def _create_youtube_search_query(self, title: str) -> str:
        """Create an effective YouTube search query from a news title"""
        # Simple keyword mapping - could be enhanced with ML/NLP
        if 'חיזבאללה' in title:
            return "Hezbollah Lebanon news"
        elif 'לבנון' in title:
            return "Lebanon news"
        elif 'ממשלה' in title or 'שר' in title:
            return "Israel government news"
        elif 'הייטק' in title:
            return "Israel tech news"
        elif 'נפל' in title or 'מות' in title:
            return "Israel accident news"
        elif 'צבא' in title or 'כוח' in title:
            return "Israel military news"
        else:
            return f"Israel news {title[:30]}"  # Fallback with partial title
    
    def _determine_overlay_style(self, overlay_style: str, channel_name: str) -> str:
        """Determine the appropriate overlay style based on channel name"""
        # Use "news" overlay style if channel name suggests news
        if channel_name and any(word in channel_name.lower() for word in ['news', 'doom', 'gloom', 'breaking']):
            return "news"
        return overlay_style
    
    def _dict_to_content_item(self, data: Dict[str, Any]) -> ContentItem:
        """
        Convert dictionary format to ContentItem object.
        
        Args:
            data: Content item in dictionary format
            
        Returns:
            ContentItem object with proper structure
        """
        # Create source
        source = NewsSource(
            id=data.get('source', 'unknown'),
            name=data.get('source', 'Unknown'),
            source_type=SourceType.WEB,
            url=data.get('url', '')
        )
        
        # Create media assets
        media_assets = []
        
        # Add image asset if available
        if data.get('local_image'):
            media_assets.append(MediaAsset(
                id='img_0',
                asset_type=AssetType.IMAGE,
                source_url=data.get('image_url', ''),
                local_path=data['local_image']
            ))
        
        # Add video asset if available
        if data.get('local_video'):
            media_assets.append(MediaAsset(
                id='vid_0',
                asset_type=AssetType.VIDEO,
                source_url=data.get('video_url', ''),
                local_path=data['local_video']
            ))
        
        # Add YouTube video if available
        if data.get('youtube_video'):
            media_assets.append(MediaAsset(
                id='yt_vid_0',
                asset_type=AssetType.VIDEO,
                source_url='youtube',  # Indicate this is a YouTube video
                local_path=data['youtube_video']
            ))
        
        # Create ContentItem
        return ContentItem(
            id=hashlib.md5(data['title'].encode()).hexdigest()[:8],
            source=source,
            title=data['title'],
            content=data.get('content', ''),
            categories=data.get('categories', []),
            media_assets=media_assets,
            relevance_score=data.get('priority', 0.5),
            metadata={
                **data.get('ai_insights', {}),
                'language': data.get('language', 'en'),
                'original_title': data.get('original_title', ''),
                'original_content': data.get('original_content', ''),
                'rephrased': data.get('rephrased', False)
            }
        )