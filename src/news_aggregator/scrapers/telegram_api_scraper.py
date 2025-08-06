"""Telegram API scraper using Telethon"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path

# Telethon imports
try:
    from telethon import TelegramClient
    from telethon.tl.types import Message, MessageMediaPhoto, MessageMediaDocument
    from telethon.errors import SessionPasswordNeededError
    TELETHON_AVAILABLE = True
except ImportError:
    TELETHON_AVAILABLE = False
    print("Warning: Telethon not installed. Install with: pip install telethon")

from ...utils.logging_config import get_logger
from ..models.content_models import (
    ContentItem, NewsSource, MediaAsset, 
    AssetType, SourceType, ContentStatus
)

logger = get_logger(__name__)


class TelegramAPIScraper:
    """Scraper for Telegram channels using official API"""
    
    def __init__(self, api_id: Optional[int] = None, api_hash: Optional[str] = None, 
                 phone: Optional[str] = None, session_name: str = "news_scraper"):
        """
        Initialize Telegram scraper
        
        Args:
            api_id: Telegram API ID (get from https://my.telegram.org)
            api_hash: Telegram API Hash
            phone: Phone number for authentication
            session_name: Name for session file
        """
        if not TELETHON_AVAILABLE:
            raise ImportError("Telethon is required for Telegram scraping. Install with: pip install telethon")
        
        # Try to load credentials from environment or config
        self.api_id = api_id or os.getenv('TELEGRAM_API_ID')
        self.api_hash = api_hash or os.getenv('TELEGRAM_API_HASH')
        self.phone = phone or os.getenv('TELEGRAM_PHONE')
        
        if not all([self.api_id, self.api_hash]):
            raise ValueError(
                "Telegram API credentials required. Set TELEGRAM_API_ID and TELEGRAM_API_HASH "
                "environment variables or pass them to constructor. "
                "Get credentials from https://my.telegram.org"
            )
        
        self.session_name = session_name
        self.client = None
        self.media_dir = "outputs/telegram_media"
        os.makedirs(self.media_dir, exist_ok=True)
    
    async def initialize(self):
        """Initialize Telegram client and authenticate if needed"""
        if self.client:
            return
        
        self.client = TelegramClient(self.session_name, int(self.api_id), self.api_hash)
        await self.client.start(phone=self.phone)
        
        logger.info("✅ Telegram client initialized and authenticated")
    
    async def scrape_channel(self, channel_name: str, hours_back: int = 24, 
                           limit: int = 100) -> List[ContentItem]:
        """
        Scrape messages from a Telegram channel
        
        Args:
            channel_name: Channel username (with or without @)
            hours_back: How many hours back to scrape
            limit: Maximum number of messages to fetch
        """
        await self.initialize()
        
        # Ensure channel name starts with @
        if not channel_name.startswith('@'):
            channel_name = f'@{channel_name}'
        
        logger.info(f"📱 Scraping Telegram channel {channel_name} (last {hours_back} hours)")
        
        try:
            # Get the channel entity
            channel = await self.client.get_entity(channel_name)
            
            # Calculate time threshold
            time_threshold = datetime.now() - timedelta(hours=hours_back)
            
            # Fetch messages
            messages = []
            async for message in self.client.iter_messages(channel, limit=limit):
                if message.date.replace(tzinfo=None) < time_threshold:
                    break
                if message.text or message.media:
                    messages.append(message)
            
            logger.info(f"📨 Found {len(messages)} messages from {channel_name}")
            
            # Convert messages to ContentItems
            content_items = []
            for msg in messages:
                content_item = await self._message_to_content_item(msg, channel_name)
                if content_item:
                    content_items.append(content_item)
            
            return content_items
            
        except Exception as e:
            logger.error(f"Failed to scrape {channel_name}: {str(e)}")
            return []
    
    async def _message_to_content_item(self, message: 'Message', 
                                     channel_name: str) -> Optional[ContentItem]:
        """Convert Telegram message to ContentItem"""
        
        # Skip if no text content
        if not message.text and not message.media:
            return None
        
        # Create source
        source = NewsSource(
            id=f"telegram_{channel_name}",
            name=f"Telegram: {channel_name}",
            url=f"https://t.me/{channel_name.replace('@', '')}/{message.id}",
            source_type=SourceType.TELEGRAM
        )
        
        # Extract text
        title = ""
        content = message.text or ""
        
        # Try to extract title from first line or bold text
        if content:
            lines = content.split('\n')
            if lines:
                title = lines[0][:100]  # First line as title (max 100 chars)
                if len(lines) > 1:
                    content = '\n'.join(lines[1:])
        
        # Handle media
        media_assets = []
        if message.media:
            media_asset = await self._download_media(message, channel_name)
            if media_asset:
                media_assets.append(media_asset)
        
        # Create content item
        return ContentItem(
            id=f"telegram_{channel_name}_{message.id}",
            source=source,
            title=title,
            content=content,
            media_assets=media_assets,
            published_date=message.date.replace(tzinfo=None),
            language=self._detect_language(content),
            author=channel_name,
            url=f"https://t.me/{channel_name.replace('@', '')}/{message.id}",
            status=ContentStatus.SCRAPED,
            categories=["telegram"],
            metadata={
                "channel": channel_name,
                "message_id": message.id,
                "views": getattr(message, 'views', 0),
                "forwards": getattr(message, 'forwards', 0),
                "is_forwarded": message.fwd_from is not None
            }
        )
    
    async def _download_media(self, message: 'Message', 
                            channel_name: str) -> Optional[MediaAsset]:
        """Download media from Telegram message"""
        
        try:
            if isinstance(message.media, MessageMediaPhoto):
                # Download photo
                filename = f"{channel_name}_{message.id}_photo.jpg"
                filepath = os.path.join(self.media_dir, filename)
                
                await self.client.download_media(message.media, filepath)
                
                return MediaAsset(
                    id=f"telegram_photo_{message.id}",
                    asset_type=AssetType.IMAGE,
                    source_url=filepath
                )
                
            elif isinstance(message.media, MessageMediaDocument):
                # Check if it's a video
                if message.media.document.mime_type.startswith('video/'):
                    filename = f"{channel_name}_{message.id}_video.mp4"
                    filepath = os.path.join(self.media_dir, filename)
                    
                    await self.client.download_media(message.media, filepath)
                    
                    return MediaAsset(
                        id=f"telegram_video_{message.id}",
                        asset_type=AssetType.VIDEO,
                        source_url=filepath
                    )
                    
        except Exception as e:
            logger.error(f"Failed to download media: {str(e)}")
        
        return None
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection based on character ranges"""
        if not text:
            return "en"
        
        # Hebrew
        if any('\u0590' <= char <= '\u05FF' for char in text):
            return "he"
        # Arabic
        elif any('\u0600' <= char <= '\u06FF' for char in text):
            return "ar"
        # Russian
        elif any('\u0400' <= char <= '\u04FF' for char in text):
            return "ru"
        else:
            return "en"
    
    async def close(self):
        """Close Telegram client connection"""
        if self.client:
            await self.client.disconnect()
    
    async def __aenter__(self):
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class TelegramConfig:
    """Configuration helper for Telegram API"""
    
    @staticmethod
    def setup_credentials():
        """Interactive setup for Telegram API credentials"""
        print("\n🔧 Telegram API Setup")
        print("━" * 50)
        print("To use Telegram scraping, you need to:")
        print("1. Go to https://my.telegram.org")
        print("2. Log in with your phone number")
        print("3. Go to 'API development tools'")
        print("4. Create an application to get api_id and api_hash")
        print("━" * 50)
        
        api_id = input("Enter your API ID: ").strip()
        api_hash = input("Enter your API Hash: ").strip()
        phone = input("Enter your phone number (with country code, e.g., +1234567890): ").strip()
        
        # Save to .env file
        env_path = Path(".env")
        env_content = ""
        
        if env_path.exists():
            env_content = env_path.read_text()
        
        # Add or update Telegram credentials
        lines = env_content.split('\n')
        new_lines = []
        added = set()
        
        for line in lines:
            if line.startswith('TELEGRAM_API_ID='):
                new_lines.append(f'TELEGRAM_API_ID={api_id}')
                added.add('api_id')
            elif line.startswith('TELEGRAM_API_HASH='):
                new_lines.append(f'TELEGRAM_API_HASH={api_hash}')
                added.add('api_hash')
            elif line.startswith('TELEGRAM_PHONE='):
                new_lines.append(f'TELEGRAM_PHONE={phone}')
                added.add('phone')
            else:
                new_lines.append(line)
        
        # Add missing credentials
        if 'api_id' not in added:
            new_lines.append(f'TELEGRAM_API_ID={api_id}')
        if 'api_hash' not in added:
            new_lines.append(f'TELEGRAM_API_HASH={api_hash}')
        if 'phone' not in added:
            new_lines.append(f'TELEGRAM_PHONE={phone}')
        
        # Write back
        env_path.write_text('\n'.join(new_lines))
        
        print("\n✅ Credentials saved to .env file")
        print("You can now use Telegram scraping!")
        
        return {
            'api_id': int(api_id),
            'api_hash': api_hash,
            'phone': phone
        }


# Example usage
async def example_usage():
    """Example of how to use the Telegram scraper"""
    
    # Initialize scraper (credentials from environment)
    scraper = TelegramAPIScraper()
    
    try:
        # Scrape channels
        channels = ["@ynet_news", "@channel13news", "@kann_news"]
        
        for channel in channels:
            print(f"\nScraping {channel}...")
            items = await scraper.scrape_channel(channel, hours_back=24, limit=50)
            
            print(f"Found {len(items)} items:")
            for item in items[:3]:  # Show first 3
                print(f"- {item.title}")
                print(f"  Media: {len(item.media_assets)} assets")
                print(f"  Views: {item.metadata.get('views', 0)}")
    
    finally:
        await scraper.close()


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())