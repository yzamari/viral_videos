"""Unit tests for web scraper"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from bs4 import BeautifulSoup

from src.news_aggregator.scrapers.web_scraper import WebNewsScraper
from src.news_aggregator.models.content_models import NewsSource, SourceType, ScrapingConfig


class TestWebNewsScraper:
    """Test web news scraper functionality"""
    
    @pytest.fixture
    def scraper(self):
        """Create scraper instance"""
        return WebNewsScraper(media_cache_dir="tests/temp_cache")
    
    @pytest.fixture
    def mock_ynet_html(self):
        """Mock Ynet HTML response"""
        return """
        <html>
            <article class="element-article">
                <h1 class="element-title">ישראל משיקה תוכנית חלל חדשה</h1>
                <div class="element-preview">
                    ישראל הודיעה היום על תוכנית חלל שאפתנית שכוללת שיגור חללית למאדים
                </div>
                <time class="element-time" datetime="2024-01-15T10:00:00">15.01.2024</time>
                <span class="element-author">יואב זיתון</span>
                <figure>
                    <img class="element-image" src="/images/space.jpg" alt="חללית">
                </figure>
            </article>
            <article class="element-article">
                <h1 class="element-title">גילוי ארכיאולוגי מרעיש בירושלים</h1>
                <div class="element-preview">
                    ארכיאולוגים גילו ממצא נדיר מתקופת בית המקדש השני
                </div>
            </article>
        </html>
        """
    
    @pytest.fixture
    def mock_rotter_html(self):
        """Mock Rotter HTML response"""
        return """
        <html>
            <div class="scoop-item">
                <h2>בלעדי: פוליטיקאי בכיר נתפס במצב מביך</h2>
                <p>מקורות מדווחים על אירוע מביך שהתרחש אמש במסעדה יוקרתית</p>
                <span class="time">לפני 2 שעות</span>
            </div>
            <div class="scoop-item">
                <h2>חשיפה: החברה הממשלתית שמבזבזת מיליונים</h2>
                <p>דוח חדש חושף בזבוז עתק בחברה ממשלתית מובילה</p>
            </div>
        </html>
        """
    
    @pytest.mark.asyncio
    async def test_scrape_ynet(self, scraper, mock_ynet_html):
        """Test scraping Ynet articles"""
        source = NewsSource(
            id="ynet_test",
            name="Ynet",
            source_type=SourceType.WEB,
            url="https://www.ynet.co.il/news",
            scraping_config=ScrapingConfig(max_items=5)
        )
        
        with patch.object(scraper, '_fetch_url', return_value=mock_ynet_html):
            articles = await scraper.scrape(source)
        
        assert len(articles) == 2
        assert articles[0].title == "ישראל משיקה תוכנית חלל חדשה"
        assert articles[0].language == "he"
        assert "חללית למאדים" in articles[0].content
        assert articles[0].author == "יואב זיתון"
        assert len(articles[0].media_assets) == 1
    
    @pytest.mark.asyncio
    async def test_language_detection(self, scraper):
        """Test Hebrew/English language detection"""
        hebrew_text = "שלום עולם זה טקסט בעברית"
        english_text = "Hello world this is English text"
        
        assert scraper._detect_language(hebrew_text) == "he"
        assert scraper._detect_language(english_text) == "en"
    
    @pytest.mark.asyncio
    async def test_media_download(self, scraper):
        """Test media asset download"""
        from src.news_aggregator.models.content_models import MediaAsset, AssetType
        
        asset = MediaAsset(
            id="test_asset",
            asset_type=AssetType.IMAGE,
            source_url="https://example.com/image.jpg"
        )
        
        mock_response = AsyncMock()
        mock_response.read = AsyncMock(return_value=b"fake_image_data")
        mock_response.raise_for_status = Mock()
        
        with patch('aiohttp.ClientSession.get', return_value=mock_response):
            local_path = await scraper.download_media(asset)
        
        assert local_path is not None
        assert asset.local_path == local_path
        assert asset.file_size == len(b"fake_image_data")


class TestRotterScraper:
    """Test Rotter.net scraper functionality"""
    
    @pytest.mark.asyncio
    async def test_scrape_rotter_scoops(self):
        """Test scraping Rotter scoops"""
        # This would require implementing Rotter-specific scraping logic
        pass