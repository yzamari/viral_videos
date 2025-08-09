"""
NewsContentCollector - Responsible for collecting content from various sources.

This class follows the Single Responsibility Principle by focusing solely on
content collection from different sources (web, CSV, Telegram).
"""

import os
import csv
import json
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

from ..interfaces.aggregator_interfaces import IContentCollector
from ..models.content_models import NewsSource, SourceType
from ..scrapers.universal_scraper import UniversalNewsScraper
from ..scrapers.web_scraper import WebNewsScraper
from ..utils.logging_config import get_logger

# Conditional Telegram import
try:
    from ..scrapers.telegram_api_scraper import TelegramAPIScraper
    TELEGRAM_API_AVAILABLE = True
except ImportError:
    TelegramAPIScraper = None
    TELEGRAM_API_AVAILABLE = False

logger = get_logger(__name__)


class NewsContentCollector(IContentCollector):
    """
    Collects content from various sources including web URLs, configuration-based sources,
    CSV files, and Telegram channels.
    
    Responsibilities:
    - Web scraping from URLs using universal scraper
    - Loading content from CSV files (both structured and simple formats)
    - Collecting content from Telegram channels (if configured)
    - Loading source configurations from JSON files
    """
    
    def __init__(self):
        """Initialize the content collector with necessary scrapers"""
        self.universal_scraper = UniversalNewsScraper()
        self.web_scraper = WebNewsScraper()
        
        # Initialize Telegram scraper if available
        self.telegram_scraper = None
        self._initialize_telegram_scraper()
        
        # Load source configurations
        self._load_source_configurations()
    
    def _initialize_telegram_scraper(self) -> None:
        """Initialize Telegram scraper if API credentials are available"""
        if TELEGRAM_API_AVAILABLE and os.getenv('TELEGRAM_API_ID'):
            try:
                self.telegram_scraper = TelegramAPIScraper()
                logger.info("✅ Using Telegram API scraper")
            except Exception as e:
                logger.warning(f"Failed to initialize Telegram API: {e}")
                logger.info("⚠️ Telegram scraping disabled - no API credentials")
        else:
            logger.info("⚠️ Telegram API not available or no credentials")
    
    def _load_source_configurations(self) -> None:
        """Load all source configurations from config files in scraper_configs/"""
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
    
    async def collect_from_sources(
        self, 
        sources: List[str], 
        hours_back: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Collect content from web sources and configurations.
        
        Args:
            sources: List of URLs or source configuration names
            hours_back: How many hours back to look for content
            
        Returns:
            List of content items in dictionary format
        """
        all_content = []
        
        for source in sources:
            try:
                if source.startswith('http'):
                    # It's a URL - scrape directly
                    content = await self._scrape_url(source, hours_back)
                else:
                    # It's a source name - look up in configurations
                    content = await self._scrape_known_source(source, hours_back)
                
                all_content.extend(content)
                
            except Exception as e:
                logger.error(f"Failed to scrape {source}: {e}")
        
        logger.info(f"📊 Collected {len(all_content)} items from {len(sources)} sources")
        return all_content
    
    async def collect_from_csv(self, csv_file: str) -> List[Dict[str, Any]]:
        """
        Collect content from CSV file.
        
        Args:
            csv_file: Path to CSV file
            
        Returns:
            List of content items loaded from CSV
        """
        if not csv_file or not os.path.exists(csv_file):
            logger.warning(f"CSV file not found: {csv_file}")
            return []
        
        content = []
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            # Try to detect if it's a simple list or structured CSV
            first_line = f.readline().strip()
            f.seek(0)
            
            if ',' in first_line and any(header in first_line.lower() for header in ['title', 'url', 'content']):
                # Structured CSV with headers
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
    
    async def collect_from_telegram(
        self, 
        channels: List[str], 
        hours_back: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Collect content from Telegram channels.
        
        Args:
            channels: List of Telegram channel names/IDs
            hours_back: How many hours back to look for content
            
        Returns:
            List of content items from Telegram channels
        """
        if not self.telegram_scraper:
            logger.warning("Telegram scraper not available")
            return []
        
        all_content = []
        
        for channel in channels:
            try:
                if hasattr(self.telegram_scraper, 'scrape_channel'):
                    telegram_content = await self.telegram_scraper.scrape_channel(
                        channel, 
                        hours_back
                    )
                    # Convert ContentItem objects to dict format
                    for item in telegram_content:
                        all_content.append(self._content_item_to_dict(item))
                else:
                    logger.warning(f"Telegram scraper doesn't support channel scraping")
                    
            except Exception as e:
                logger.error(f"Failed to scrape Telegram {channel}: {e}")
        
        logger.info(f"📱 Collected {len(all_content)} items from {len(channels)} Telegram channels")
        return all_content
    
    async def _scrape_url(self, url: str, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Scrape content from a specific URL using universal scraper"""
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
        
        # Use universal scraper for all URLs
        content_items = await self.universal_scraper.scrape(source, hours_back)
        
        # Convert ContentItem objects to dict format
        return [self._content_item_to_dict(item) for item in content_items]
    
    async def _scrape_known_source(self, source_name: str, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Scrape from a known source by name using config files"""
        logger.info(f"🔍 Looking for source config: {source_name.lower()}")
        logger.info(f"📋 Available configs: {list(self.universal_scraper.configs.keys())}")
        
        if source_name.lower() in self.universal_scraper.configs:
            config = self.universal_scraper.configs[source_name.lower()]
            logger.info(f"✅ Found config for {source_name}, scraping {config.base_url}")
            
            # Use universal scraper directly
            articles = await self.universal_scraper.scrape_website(source_name.lower(), max_items=20)
            
            # Convert to standardized dict format
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
        """Convert ContentItem object to standardized dict format"""
        from ..models.content_models import AssetType
        
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