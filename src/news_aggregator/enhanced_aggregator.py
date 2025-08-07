"""Enhanced News Aggregator with Multi-language, Duplicate Detection, and AI Discussions"""

import asyncio
import os
import csv
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional, Set, Tuple
from collections import defaultdict
import json

from ..utils.logging_config import get_logger
from ..utils.session_manager import SessionManager
from ..ai.manager import AIServiceManager
from ..core.decision_framework import DecisionFramework

from .scrapers.universal_scraper import UniversalNewsScraper
# Generic scrapers only
try:
    from .scrapers.telegram_api_scraper import TelegramAPIScraper
    TELEGRAM_API_AVAILABLE = True
except ImportError:
    TelegramAPIScraper = None
    TELEGRAM_API_AVAILABLE = False
# No hardcoded website scrapers - use universal scraper
from .scrapers.web_scraper import WebNewsScraper

from .processors.content_analyzer import ContentAnalyzer
from .processors.media_downloader import MediaDownloader
from .processors.duplicate_detector import DuplicateDetector

from .composers.scraped_media_composer import ScrapedMediaComposer
from .composers.multi_language_composer import MultiLanguageComposer

from .agents.news_orchestrator import NewsOrchestrator
from .agents.news_discussion_agents import NewsDiscussionModerator

from .models.content_models import ContentItem, MediaAsset, AssetType, NewsSource, SourceType

logger = get_logger(__name__)


class EnhancedNewsAggregator:
    """Enhanced news aggregator with all requested features"""
    
    def __init__(self, enable_discussions: bool = True, discussion_log: bool = False):
        self.session_manager = SessionManager()
        self.ai_manager = AIServiceManager()
        self.media_downloader = MediaDownloader()
        
        # Components will be initialized after session creation
        self.decision_framework = None
        self.content_analyzer = None
        self.duplicate_detector = None
        self.scraped_media_composer = None
        self.multi_language_composer = None
        
        # AI agents
        self.enable_discussions = enable_discussions
        self.discussion_log = discussion_log
        self.orchestrator = None
        self.discussion_moderator = None
        
        # Initialize generic scrapers only
        self.universal_scraper = UniversalNewsScraper()  # Configurable universal scraper
        self.web_scraper = WebNewsScraper()
        
        # Initialize Telegram scraper
        if TELEGRAM_API_AVAILABLE and os.getenv('TELEGRAM_API_ID'):
            try:
                self.telegram_scraper = TelegramAPIScraper()
                logger.info("✅ Using Telegram API scraper")
            except Exception as e:
                logger.warning(f"Failed to initialize Telegram API: {e}")
                logger.info("⚠️ Telegram scraping disabled - no API credentials")
                self.telegram_scraper = None
        else:
            logger.info("⚠️ Telegram API not available or no credentials")
            self.telegram_scraper = None
        
        # Load all available source configurations from config files
        self._load_source_configurations()
    
    def _load_source_configurations(self):
        """Load all source configurations from config files in scraper_configs/"""
        import json
        import os
        
        config_dir = "scraper_configs"
        if not os.path.exists(config_dir):
            logger.info(f"📁 Config directory {config_dir} not found, creating it...")
            os.makedirs(config_dir, exist_ok=True)
            return
            
        # Load all JSON config files
        config_files = [f for f in os.listdir(config_dir) if f.endswith('.json')]
        
        for config_file in config_files:
            try:
                config_path = os.path.join(config_dir, config_file)
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                site_id = config_file.replace('.json', '')
                self.universal_scraper.add_website_config(site_id, config)
                logger.info(f"✅ Loaded configuration for {config.get('name', site_id)}")
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to load config {config_file}: {e}")
        
        if not config_files:
            logger.info("📋 No source configurations found in scraper_configs/")
            logger.info("💡 Add JSON configuration files to enable website scraping")
    
    async def aggregate_news(
        self,
        sources: List[str],
        csv_file: Optional[str] = None,
        languages: List[str] = ['en'],
        style: str = "professional",
        tone: str = "informative",
        platform: str = "youtube",
        duration_seconds: int = 60,
        max_stories: int = 10,
        enable_ai_discussion: bool = True,
        discussion_log: bool = False,
        overlay_style: str = "modern",
        output_dir: str = "outputs/news",
        hours_back: int = 24,
        telegram_channels: List[str] = [],
        use_youtube_videos: bool = False,
        logo_path: str = None,
        channel_name: str = "NEWS",
        dynamic_transitions: bool = True
    ) -> Dict[str, str]:
        """
        Main aggregation method supporting all features
        
        Args:
            sources: List of URLs or source names
            csv_file: Optional CSV file with additional items
            languages: List of output languages (creates one video per language)
            style: Free-form style description for AI agents
            tone: Free-form tone description for AI agents
            platform: Target platform (youtube, tiktok, instagram, twitter)
            duration_seconds: Duration per video
            max_stories: Maximum stories to include
            enable_ai_discussion: Enable AI agent discussions
            discussion_log: Show detailed discussion logs
            overlay_style: Overlay style (modern, classic, minimal)
            output_dir: Output directory
            
        Returns:
            Dict mapping language to output video path
        """
        
        logger.info("🎬 Enhanced News Aggregator Starting")
        logger.info(f"📰 Sources: {sources}")
        logger.info(f"🌐 Languages: {languages}")
        logger.info(f"🎨 Style: {style}, Tone: {tone}")
        logger.info(f"📱 Platform: {platform}")
        logger.info(f"📺 Channel Name: {channel_name}")
        
        # Create session
        session_id = self.session_manager.create_session(
            mission=f"News aggregation from {len(sources)} sources",
            platform=platform,
            duration=duration_seconds,
            category="news"
        )
        
        # Initialize components with session
        await self._initialize_components(session_id)
        
        # 1. Collect all content
        all_content = await self._collect_all_content(sources, csv_file, hours_back, telegram_channels)
        
        if not all_content:
            raise ValueError("No content found from any source!")
        
        logger.info(f"📊 Collected {len(all_content)} total items")
        
        # 2. Detect and merge duplicates
        unique_content = await self._detect_and_merge_duplicates(all_content)
        logger.info(f"🔍 After duplicate detection: {len(unique_content)} unique stories")
        
        # 3. AI agent discussions (if enabled)
        visual_styles = {}
        if enable_ai_discussion:
            selected_content = await self._run_ai_discussions(
                unique_content,
                style,
                tone,
                platform,
                max_stories,
                discussion_log
            )
            # Get visual style recommendations
            if self.orchestrator:
                visual_styles = await self.orchestrator.select_visual_styles(
                    style, tone, platform, languages[0]
                )
                logger.info(f"🎨 AI selected visual styles: {visual_styles}")
                
                # 3.5. AI Content Rephrasing (NEW!)
                selected_content = await self.orchestrator.rephrase_content_with_tone(
                    selected_content, style, tone, languages[0]
                )
        else:
            # Simple selection based on relevance
            selected_content = self._simple_select_content(unique_content, max_stories)
        
        logger.info(f"✅ Selected {len(selected_content)} stories for final video")
        
        # 4. Download all media
        await self._download_all_media(selected_content, use_youtube_videos)
        
        # 5. Create videos for each language
        output_videos = {}
        for language in languages:
            logger.info(f"🎥 Creating video for language: {language}")
            
            output_path = await self._create_language_video(
                selected_content,
                language,
                style,
                tone,
                platform,
                duration_seconds,
                overlay_style,
                output_dir,
                visual_styles,
                use_youtube_videos,
                logo_path,
                channel_name,
                dynamic_transitions
            )
            
            output_videos[language] = output_path
            logger.info(f"✅ Created {language} video: {output_path}")
        
        # 6. Save session report
        self._save_session_report(selected_content, output_videos, style, tone)
        
        return output_videos
    
    async def _initialize_components(self, session_id: str):
        """Initialize components that need session context"""
        from ..utils.session_context import SessionContext
        
        session_context = SessionContext(
            session_id=session_id,
            session_manager_instance=self.session_manager
        )
        
        self.decision_framework = DecisionFramework(session_context)
        self.content_analyzer = ContentAnalyzer(self.ai_manager)
        self.duplicate_detector = DuplicateDetector(self.ai_manager)
        
        self.scraped_media_composer = ScrapedMediaComposer(
            self.session_manager,
            self.media_downloader
        )
        
        self.multi_language_composer = MultiLanguageComposer(
            self.session_manager,
            self.ai_manager,
            self.scraped_media_composer
        )
        
        if self.enable_discussions:
            self.orchestrator = NewsOrchestrator(
                self.ai_manager,
                self.decision_framework
            )
            self.discussion_moderator = NewsDiscussionModerator()
    
    async def _collect_all_content(
        self,
        sources: List[str],
        csv_file: Optional[str] = None,
        hours_back: int = 24,
        telegram_channels: List[str] = []
    ) -> List[Dict[str, Any]]:
        """Collect content from all sources including CSV"""
        all_content = []
        
        # 1. Scrape from URLs/sources
        for source in sources:
            try:
                if source.startswith('http'):
                    # It's a URL
                    content = await self._scrape_url(source, hours_back)
                else:
                    # It's a source name
                    content = await self._scrape_known_source(source, hours_back)
                
                all_content.extend(content)
                
            except Exception as e:
                logger.error(f"Failed to scrape {source}: {e}")
        
        # 2. Scrape Telegram channels
        for channel in telegram_channels:
            if not self.telegram_scraper:
                logger.warning(f"Cannot scrape Telegram channel {channel} - no Telegram scraper available")
                continue
            try:
                # Use appropriate scraping method based on scraper type
                if hasattr(self.telegram_scraper, 'scrape_channel'):
                    telegram_content = await self.telegram_scraper.scrape_channel(channel, hours_back)
                    # Convert to dict format
                    for item in telegram_content:
                        all_content.append(self._content_item_to_dict(item))
                else:
                    logger.warning(f"Telegram scraper doesn't support channel scraping")
            except Exception as e:
                logger.error(f"Failed to scrape Telegram {channel}: {e}")
        
        # 3. Load from CSV if provided
        if csv_file:
            csv_content = await self._load_csv_content(csv_file)
            all_content.extend(csv_content)
        
        return all_content
    
    async def _scrape_url(self, url: str, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Scrape content from a URL using universal scraper"""
        from .models.content_models import NewsSource, SourceType
        from urllib.parse import urlparse
        
        # Extract domain name for identification
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace('www.', '')
        source_name = domain.split('.')[0].title()
        
        logger.info(f"🌐 Scraping {source_name} ({url}) using universal scraper")
        
        # Create source object
        source = NewsSource(
            id=url.replace('https://', '').replace('/', '_'),
            name=source_name,
            source_type=SourceType.WEB,
            url=url
        )
        
        # Always use universal scraper - no hardcoded logic
        content_items = await self.universal_scraper.scrape(source, hours_back)
        
        # Convert to dict format
        return [self._content_item_to_dict(item) for item in content_items]
    
    async def _scrape_known_source(self, source_name: str, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Scrape from a known source by name using config files"""
        # Look up the source in the universal scraper configs
        logger.info(f"🔍 Looking for source config: {source_name.lower()}")
        logger.info(f"📋 Available configs: {list(self.universal_scraper.configs.keys())}")
        
        if source_name.lower() in self.universal_scraper.configs:
            config = self.universal_scraper.configs[source_name.lower()]
            logger.info(f"✅ Found config for {source_name}, scraping {config.base_url}")
            # Use universal scraper directly instead of _scrape_url to avoid double processing
            articles = await self.universal_scraper.scrape_website(source_name.lower(), max_items=20)
            # Convert to dict format with proper media fields
            result = []
            for article in articles:
                item = {
                    'title': article.get('title', ''),
                    'content': article.get('description', ''),
                    'url': article.get('url', config.base_url),
                    'source': config.name,
                    'category': article.get('category', 'news')
                }
                
                # Handle images - prioritize article_images, then images array
                images = article.get('article_images', []) or article.get('images', [])
                if images and len(images) > 0:
                    item['image_url'] = images[0]
                    item['article_images'] = images
                
                # Handle videos - prioritize article_videos, then videos array  
                videos = article.get('article_videos', []) or article.get('videos', [])
                if videos and len(videos) > 0:
                    item['video_url'] = videos[0]
                    item['article_videos'] = videos
                
                result.append(item)
            
            return result
        else:
            logger.warning(f"❌ Unknown source: {source_name}")
            logger.info(f"💡 Add a {source_name.lower()}.json config file to scraper_configs/ directory")
            return []
    
    def _content_item_to_dict(self, item) -> Dict[str, Any]:
        """Convert ContentItem to dict format"""
        media_assets = []
        for asset in item.media_assets:
            media_assets.append({
                'url': asset.url,
                'type': asset.asset_type.value,
                'caption': asset.caption
            })
        
        return {
            'title': item.title,
            'content': item.content,
            'url': item.url,
            'source': item.source.name,
            'source_url': item.source.url,
            'image_url': media_assets[0]['url'] if media_assets and media_assets[0]['type'] == 'image' else None,
            'video_url': media_assets[0]['url'] if media_assets and media_assets[0]['type'] == 'video' else None,
            'media_assets': media_assets,
            'published_date': item.published_date.isoformat() if item.published_date else None,
            'language': item.language,
            'categories': item.categories,
            'metadata': item.metadata
        }
    
    async def _load_csv_content(self, csv_file: str) -> List[Dict[str, Any]]:
        """Load content from CSV file"""
        content = []
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            # Try to detect if it's a simple list or structured CSV
            first_line = f.readline().strip()
            f.seek(0)
            
            if ',' in first_line and any(header in first_line.lower() for header in ['title', 'url', 'content']):
                # Structured CSV
                reader = csv.DictReader(f)
                for row in reader:
                    content.append({
                        'title': row.get('title', row.get('item', '')),
                        'content': row.get('content', row.get('description', '')),
                        'url': row.get('url', ''),
                        'source': row.get('source', 'CSV'),
                        'image_url': row.get('image_url', row.get('image', '')),
                        'video_url': row.get('video_url', row.get('video', '')),
                        'language': row.get('language', 'en'),
                        'priority': float(row.get('priority', 0.5))
                    })
            else:
                # Simple list of strings
                for line in f:
                    line = line.strip()
                    if line:
                        content.append({
                            'title': line,
                            'content': '',
                            'url': '',
                            'source': 'CSV',
                            'language': 'en',
                            'priority': 0.5
                        })
        
        logger.info(f"📄 Loaded {len(content)} items from CSV")
        return content
    
    async def _detect_and_merge_duplicates(
        self,
        all_content: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect and merge duplicate stories from different sources"""
        
        # Group by similarity
        groups = await self.duplicate_detector.group_similar_content(all_content)
        
        merged_content = []
        for group in groups:
            if len(group) > 1:
                # Merge duplicates
                merged = await self._merge_duplicate_group(group)
                merged_content.append(merged)
            else:
                # Single item, no duplicates
                merged_content.append(group[0])
        
        return merged_content
    
    async def _merge_duplicate_group(
        self,
        group: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Merge a group of duplicate stories"""
        
        # Use the most complete version as base
        base = max(group, key=lambda x: len(x.get('content', '')))
        
        # Merge information
        merged = base.copy()
        merged['sources'] = list(set([item['source'] for item in group]))
        merged['source'] = ' + '.join(merged['sources'])
        
        # Collect all media
        all_images = []
        all_videos = []
        for item in group:
            if item.get('image_url'):
                all_images.append(item['image_url'])
            if item.get('video_url'):
                all_videos.append(item['video_url'])
        
        # Use best quality media
        if all_images:
            merged['image_url'] = all_images[0]  # TODO: Select best quality
        if all_videos:
            merged['video_url'] = all_videos[0]
        
        # Boost priority for multi-source stories
        merged['priority'] = min(1.0, max(item.get('priority', 0.5) for item in group) + 0.2)
        merged['duplicate_count'] = len(group)
        
        logger.info(f"🔀 Merged {len(group)} duplicate stories: {merged['title'][:50]}...")
        
        return merged
    
    async def _run_ai_discussions(
        self,
        content: List[Dict[str, Any]],
        style: str,
        tone: str,
        platform: str,
        max_stories: int,
        discussion_log: bool
    ) -> List[Dict[str, Any]]:
        """Run AI agent discussions to select and order content"""
        
        logger.info("🤖 Starting AI agent discussions...")
        
        # Create discussion context
        context = {
            'content': content,
            'style': style,
            'tone': tone,
            'platform': platform,
            'max_stories': max_stories,
            'criteria': {
                'relevance': 'How newsworthy and current is this story?',
                'engagement': f'How engaging will this be for {platform} audience?',
                'visual_appeal': 'Does this have good visual media available?',
                'diversity': 'Does this add variety to our news selection?',
                'multi_source': 'Is this confirmed by multiple sources?'
            }
        }
        
        # Run orchestrated discussion
        discussion_result = await self.orchestrator.run_news_selection_discussion(
            context,
            enable_logging=discussion_log
        )
        
        # Extract selected content
        selected_indices = discussion_result.get('selected_indices', [])
        selected_content = [content[i] for i in selected_indices if i < len(content)]
        
        # Add AI insights to each item
        insights = discussion_result.get('insights', {})
        for i, item in enumerate(selected_content):
            item['ai_insights'] = insights.get(str(i), {})
            item['ai_reasoning'] = discussion_result.get('reasoning', {}).get(str(i), '')
        
        if discussion_log:
            self._save_discussion_log(discussion_result)
        
        return selected_content
    
    def _simple_select_content(
        self,
        content: List[Dict[str, Any]],
        max_stories: int
    ) -> List[Dict[str, Any]]:
        """Simple content selection without AI"""
        
        # Sort by priority and duplicate count
        sorted_content = sorted(
            content,
            key=lambda x: (
                x.get('priority', 0.5),
                x.get('duplicate_count', 1),
                len(x.get('content', ''))
            ),
            reverse=True
        )
        
        # If no items have media URLs, return all items (will use text-only segments)
        with_media = [
            item for item in sorted_content
            if item.get('image_url') or item.get('video_url')
        ]
        
        if not with_media:
            logger.warning("No items with media found, using text-only content")
            return sorted_content[:max_stories]
        
        return with_media[:max_stories]
    
    async def _download_all_media(self, content: List[Dict[str, Any]], use_youtube_videos: bool = False):
        """Download all media for selected content"""
        
        logger.info("📥 Downloading media assets...")
        
        # Initialize YouTube enhancer if needed
        youtube_enhancer = None
        if use_youtube_videos:
            from .scrapers.youtube_scraper import YouTubeNewsEnhancer
            youtube_enhancer = YouTubeNewsEnhancer()
            logger.info("🔍 YouTube video search enabled")
        
        for item in content:
            # Prioritize article images (from full article page) over preview images
            image_to_download = None
            
            # Check for article images (fetched from article page)
            if item.get('primary_image'):
                image_to_download = item['primary_image']
                logger.info(f"📸 Using primary image from article: {item['title'][:50]}...")
            elif item.get('article_images') and len(item['article_images']) > 0:
                image_to_download = item['article_images'][0]
                logger.info(f"📸 Using article image from article page: {item['title'][:50]}...")
            elif item.get('image_url'):
                image_to_download = item['image_url']
            
            # Download the best available image
            if image_to_download:
                try:
                    result = await self.media_downloader.download_media(
                        image_to_download,
                        metadata={'title': item['title'], 'source': item['source']}
                    )
                    if result and result.get('local_path'):
                        item['local_image'] = result.get('local_path')
                        logger.info(f"✅ Downloaded image for: {item['title'][:50]}...")
                except Exception as e:
                    logger.warning(f"Failed to download image: {e}")
            
            # Download video (prioritize article videos)
            video_to_download = None
            if item.get('article_videos') and len(item['article_videos']) > 0:
                video_to_download = item['article_videos'][0]
                logger.info(f"🎥 Using video from article page: {item['title'][:50]}...")
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
                        logger.info(f"✅ Downloaded video for: {item['title'][:50]}...")
                except Exception as e:
                    logger.warning(f"Failed to download video: {e}")
            
            # Search and download YouTube videos if enabled
            if use_youtube_videos and youtube_enhancer:
                try:
                    # Create better search terms from Hebrew titles
                    title = item['title']
                    
                    # Extract key terms for better YouTube search
                    search_query = title
                    if 'חיזבאללה' in title:
                        search_query = "Hezbollah Lebanon news"
                    elif 'לבנון' in title:
                        search_query = "Lebanon news"
                    elif 'ממשלה' in title or 'שר' in title:
                        search_query = "Israel government news"
                    elif 'הייטק' in title:
                        search_query = "Israel tech news"
                    elif 'נפל' in title or 'מות' in title:
                        search_query = "Israel accident news"
                    elif 'צבא' in title or 'כוח' in title:
                        search_query = "Israel military news"
                    else:
                        search_query = "Israel news"
                    
                    logger.info(f"🔍 Searching YouTube for: {search_query} (from '{title[:50]}...')")
                    # Convert to format expected by YouTube enhancer
                    news_items = [{'title': search_query, 'media_assets': []}]
                    enhanced = await youtube_enhancer.enhance_news_items(news_items, True)
                    
                    if enhanced and enhanced[0].get('media_assets'):
                        # Find video assets from YouTube
                        for asset in enhanced[0]['media_assets']:
                            if asset.get('type') == 'video' and asset.get('source') == 'youtube':
                                item['youtube_video'] = asset['url']  # Local path to downloaded video
                                logger.info(f"✅ Found YouTube video: {asset.get('title', 'Unknown')}")
                                break
                        else:
                            logger.info(f"❌ No YouTube video asset found for: {search_query}")
                    else:
                        logger.info(f"❌ No YouTube video found for: {search_query}")
                        
                except Exception as e:
                    logger.warning(f"Failed to get YouTube video for '{item['title'][:50]}...': {e}")
    
    async def _create_language_video(
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
        """Create video for a specific language"""
        
        # Convert to ContentItem format
        content_items = []
        for item in content:
            # Create ContentItem with local media
            content_item = self._dict_to_content_item(item)
            content_items.append(content_item)
        
        # Use "news" overlay style if channel name suggests news
        final_overlay_style = overlay_style
        if channel_name and any(word in channel_name.lower() for word in ['news', 'doom', 'gloom', 'breaking']):
            final_overlay_style = "news"
        
        # Use multi-language composer
        output_path = await self.multi_language_composer.create_news_video(
            content_items=content_items,
            language=language,
            style=style,
            tone=tone,
            platform=platform,
            duration_seconds=duration_seconds,
            overlay_style=final_overlay_style,
            output_filename=f"news_{language}_{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4",
            visual_styles=visual_styles,
            use_youtube_videos=use_youtube_videos,
            logo_path=logo_path,
            channel_name=channel_name,
            dynamic_transitions=dynamic_transitions
        )
        
        return output_path
    
    def _content_item_to_dict(self, item: ContentItem) -> Dict[str, Any]:
        """Convert ContentItem to dict"""
        return {
            'title': item.title,
            'content': item.content,
            'url': item.source.url if item.source else '',
            'source': item.source.name if item.source else 'Unknown',
            'image_url': item.media_assets[0].source_url if item.media_assets and item.media_assets[0].asset_type == AssetType.IMAGE else '',
            'video_url': next((asset.source_url for asset in item.media_assets if asset.asset_type == AssetType.VIDEO), ''),
            'categories': item.categories,
            'priority': item.relevance_score
        }
    
    def _dict_to_content_item(self, data: Dict[str, Any]) -> ContentItem:
        """Convert dict to ContentItem"""
        # Create source
        source = NewsSource(
            id=data.get('source', 'unknown'),
            name=data.get('source', 'Unknown'),
            source_type=SourceType.WEB,
            url=data.get('url', '')
        )
        
        # Create media assets
        media_assets = []
        if data.get('local_image'):
            media_assets.append(MediaAsset(
                id='img_0',
                asset_type=AssetType.IMAGE,
                source_url=data.get('image_url', ''),
                local_path=data['local_image']
            ))
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
    
    def _save_discussion_log(self, discussion_result: Dict[str, Any]):
        """Save AI discussion log"""
        session_dir = self.session_manager.session_data.get('session_dir', 'outputs')
        log_path = os.path.join(
            session_dir,
            'ai_discussion_log.json'
        )
        
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(discussion_result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💬 AI discussion log saved: {log_path}")
    
    def _save_session_report(
        self,
        content: List[Dict[str, Any]],
        output_videos: Dict[str, str],
        style: str,
        tone: str
    ):
        """Save comprehensive session report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'style': style,
            'tone': tone,
            'total_stories': len(content),
            'output_videos': output_videos,
            'stories': []
        }
        
        for item in content:
            report['stories'].append({
                'title': item['title'],
                'sources': item.get('sources', [item['source']]),
                'has_image': bool(item.get('local_image')),
                'has_video': bool(item.get('local_video')),
                'ai_reasoning': item.get('ai_reasoning', ''),
                'priority': item.get('priority', 0.5)
            })
        
        session_dir = self.session_manager.session_data.get('session_dir', 'outputs')
        report_path = os.path.join(
            session_dir,
            'news_aggregation_report.json'
        )
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 Session report saved: {report_path}")


# CLI integration function
async def create_enhanced_news_edition(
    sources: List[str],
    csv_file: Optional[str] = None,
    languages: List[str] = ['en'],
    style: str = "professional",
    tone: str = "informative", 
    platform: str = "youtube",
    duration_seconds: int = 60,
    max_stories: int = 10,
    enable_ai_discussion: bool = True,
    discussion_log: bool = False,
    overlay_style: str = "modern",
    output_dir: str = "outputs/news",
    hours_back: int = 24,
    telegram_channels: List[str] = [],
    use_youtube_videos: bool = False,
    logo_path: str = None,
    channel_name: str = "NEWS",
    dynamic_transitions: bool = True
) -> Dict[str, str]:
    """Create news edition with enhanced aggregator"""
    
    logger.info(f"📺 create_enhanced_news_edition received channel_name: {channel_name}")
    
    aggregator = EnhancedNewsAggregator(
        enable_discussions=enable_ai_discussion,
        discussion_log=discussion_log
    )
    
    return await aggregator.aggregate_news(
        sources=sources,
        csv_file=csv_file,
        languages=languages,
        style=style,
        tone=tone,
        platform=platform,
        duration_seconds=duration_seconds,
        max_stories=max_stories,
        enable_ai_discussion=enable_ai_discussion,
        discussion_log=discussion_log,
        overlay_style=overlay_style,
        output_dir=output_dir,
        hours_back=hours_back,
        telegram_channels=telegram_channels,
        use_youtube_videos=use_youtube_videos,
        logo_path=logo_path,
        channel_name=channel_name,
        dynamic_transitions=dynamic_transitions
    )