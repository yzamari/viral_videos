"""Universal news scraper with hardcoded test data for now"""

import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random

from ...utils.logging_config import get_logger
from ..models.content_models import (
    ContentItem, NewsSource, MediaAsset, 
    AssetType, SourceType, ContentStatus
)
from .test_media_scraper import TestMediaScraper

logger = get_logger(__name__)


class TestUniversalNewsScraper:
    """Universal scraper that can scrape any news site"""
    
    def __init__(self):
        self.media_scraper = TestMediaScraper()
        # Test news data - Hebrew news
        self.test_data = {
            "ynet": [
                {
                    "title": "נתניהו בנאום דרמטי: 'המצב דורש החלטות קשות'",
                    "content": "ראש הממשלה נתניהו נשא היום נאום דרמטי בכנסת ואמר כי המצב הביטחוני דורש קבלת החלטות קשות. השרים הגיבו בסערה ודרשו הבהרות לגבי הצעדים המתוכננים. האופוזיציה מתחה ביקורת חריפה על הטיפול במשבר.",
                    "image": "https://ynet-pic1.yit.co.il/cdn-cgi/image/format=auto/picserver6/crop_images/2025/07/14/r1lVEGzUlx/r1lVEGzUlx_0_0_850_479_0_x-large.jpg",
                    "video": None
                },
                {
                    "title": "גל חום קיצוני: 45 מעלות בצל באילת",
                    "content": "גל חום קיצוני פוקד את ישראל. באילת נמדדו 45 מעלות בצל, שיא של כל הזמנים. משרד הבריאות מזהיר.",
                    "image": "https://ynet-pic1.yit.co.il/cdn-cgi/image/format=auto/picserver6/crop_images/2025/08/05/SklEHLiJOeg/SklEHLiJOeg_0_136_1280_718_0_medium.jpg",
                    "video": None
                },
                {
                    "title": "מכבי תל אביב זכתה באליפות אירופה בכדורסל",
                    "content": "ניצחון דרמטי למכבי תל אביב שגברה על ריאל מדריד 89-87 וזכתה בגביע האירופי. האוהדים חגגו ברחובות.",
                    "image": "https://ynet-pic1.yit.co.il/cdn-cgi/image/format=auto/picserver6/crop_images/2022/12/15/HJHFUxFOi/HJHFUxFOi_0_0_850_479_0_medium.jpg",
                    "video": None
                },
                {
                    "title": "תגלית ארכיאולוגית: עיר בת 3000 שנה נחשפה בנגב",
                    "content": "חוקרים מאוניברסיטת בן גוריון חשפו עיר עתיקה בת 3000 שנה בנגב. הממצאים כוללים כלי חרס וכתובות עתיקות.",
                    "image": "https://ynet-pic1.yit.co.il/cdn-cgi/image/format=auto/picserver6/crop_images/2025/07/30/BJ11S2ySDPge/BJ11S2ySDPge_0_187_2000_1130_0_medium.jpg",
                    "video": None
                },
                {
                    "title": "הייטק: חברה ישראלית נמכרה ב-500 מיליון דולר",
                    "content": "חברת הסייבר הישראלית CyberShield נרכשה על ידי ענקית הטכנולוגיה האמריקאית ב-500 מיליון דולר.",
                    "image": "https://ynet-pic1.yit.co.il/cdn-cgi/image/format=auto/picserver6/crop_images/2025/07/31/H1QLVFhOPxl/H1QLVFhOPxl_0_77_1500_845_0_medium.jpg",
                    "video": None
                }
            ],
            "mako": [
                {
                    "title": "סערה בכנסת: ח\"כים הושעו מהדיון",
                    "content": "דיון סוער בכנסת הסתיים בהשעיית שלושה חברי כנסת. יו\"ר הכנסת נאלץ להפסיק את הישיבה.",
                    "image": "https://img.mako.co.il/2024/08/05/knesset_storm.jpg",
                    "video": None
                },
                {
                    "title": "מחקר: קפה מפחית סיכון למחלות לב",
                    "content": "מחקר חדש מגלה ששתיית 3 כוסות קפה ביום מפחיתה ב-20% את הסיכון למחלות לב.",
                    "image": "https://img.mako.co.il/2024/08/04/coffee_health.jpg",
                    "video": None
                }
            ],
            "sport5": [
                {
                    "title": "ליונל מסי מגיע לישראל למשחק ידידות",
                    "content": "הכוכב הארגנטינאי יגיע עם נבחרת ארגנטינה למשחק ידידות מול ישראל בנובמבר.",
                    "image": "https://sport5.co.il/uploads/2024/08/messi_israel.jpg",
                    "video": None
                }
            ]
        }
    
    async def scrape(self, source: NewsSource, hours_back: int = 24) -> List[ContentItem]:
        """Scrape news from source"""
        logger.info(f"Scraping {source.url} (last {hours_back} hours)")
        
        # Determine source type
        source_key = None
        if "ynet" in source.url:
            source_key = "ynet"
        elif "mako" in source.url:
            source_key = "mako"
        elif "sport5" in source.url:
            source_key = "sport5"
        
        if not source_key or source_key not in self.test_data:
            logger.warning(f"No test data for {source.url}")
            return []
        
        # Get test articles
        articles = []
        now = datetime.now()
        
        for idx, data in enumerate(self.test_data[source_key]):
            # Create time within hours_back
            published = now - timedelta(hours=random.randint(1, min(hours_back, 23)))
            
            # Create media assets
            media_assets = []
            if data["image"]:
                media_assets.append(MediaAsset(
                    id=f"{source_key}_{idx}_image",
                    asset_type=AssetType.IMAGE,
                    source_url=data["image"]
                ))
            
            if data.get("video"):
                media_assets.append(MediaAsset(
                    id=f"{source_key}_{idx}_video",
                    asset_type=AssetType.VIDEO,
                    source_url=data["video"]
                ))
            
            # Create content item
            article = ContentItem(
                id=f"{source_key}_{idx}_{published.timestamp()}",
                source=source,
                title=data["title"],
                content=data["content"],
                media_assets=media_assets,
                published_date=published,
                language="he",
                author=source.name,
                url=f"{source.url}/article/{idx}",
                status=ContentStatus.SCRAPED,
                categories=["news"],
                metadata={
                    "scraped_at": datetime.now().isoformat(),
                    "source_type": source_key
                }
            )
            
            articles.append(article)
        
        logger.info(f"Scraped {len(articles)} articles from {source.name}")
        return articles


class TelegramChannelScraper:
    """Scraper for Telegram channels"""
    
    def __init__(self):
        # Test Telegram data
        self.test_channels = {
            "@ynet_news": [
                {
                    "title": "⚡️ דחוף: פיצוץ חזק נשמע בתל אביב",
                    "content": "פיצוץ חזק נשמע לפני דקות ספורות באזור תל אביב. כוחות ההצלה בדרך למקום.",
                    "image": "https://ynet-pic1.yit.co.il/picserver5/wcm_upload/2024/08/05/tel_aviv_explosion.jpg",
                    "video": None
                }
            ],
            "@channel13news": [
                {
                    "title": "🔴 שידור חי: מסיבת עיתונאים של ראש הממשלה",
                    "content": "ראש הממשלה יקיים בעוד דקות ספורות מסיבת עיתונאים בנושא המצב הביטחוני.",
                    "image": None,
                    "video": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"
                }
            ]
        }
    
    async def scrape_channel(self, channel_name: str, hours_back: int = 24) -> List[ContentItem]:
        """Scrape Telegram channel"""
        logger.info(f"Scraping Telegram channel {channel_name}")
        
        if channel_name not in self.test_channels:
            logger.warning(f"No test data for channel {channel_name}")
            return []
        
        articles = []
        now = datetime.now()
        
        # Create fake source
        source = NewsSource(
            id=f"telegram_{channel_name}",
            name=f"Telegram: {channel_name}",
            url=f"https://t.me/{channel_name.replace('@', '')}",
            source_type=SourceType.TELEGRAM
        )
        
        for idx, data in enumerate(self.test_channels[channel_name]):
            # Create recent timestamp
            published = now - timedelta(minutes=random.randint(5, hours_back * 60))
            
            # Create media assets
            media_assets = []
            if data.get("image"):
                media_assets.append(MediaAsset(
                    id=f"telegram_{channel_name}_{idx}_image",
                    asset_type=AssetType.IMAGE,
                    source_url=data["image"]
                ))
            
            if data.get("video"):
                media_assets.append(MediaAsset(
                    id=f"telegram_{channel_name}_{idx}_video",
                    asset_type=AssetType.VIDEO,
                    source_url=data["video"]
                ))
            
            # Create content item
            article = ContentItem(
                id=f"telegram_{channel_name}_{idx}_{published.timestamp()}",
                source=source,
                title=data["title"],
                content=data["content"],
                media_assets=media_assets,
                published_date=published,
                language="he",
                author=channel_name,
                url=f"{source.url}/{idx}",
                status=ContentStatus.SCRAPED,
                categories=["telegram", "breaking"],
                metadata={
                    "channel": channel_name,
                    "is_forwarded": False,
                    "views": random.randint(1000, 50000)
                }
            )
            
            articles.append(article)
        
        logger.info(f"Scraped {len(articles)} messages from {channel_name}")
        return articles