"""Specialized scrapers for Israeli news sites"""

import re
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import aiohttp

from ...utils.logging_config import get_logger
from ..models.content_models import ContentItem, NewsSource, MediaAsset, AssetType, ContentStatus
from .web_scraper import WebNewsScraper

logger = get_logger(__name__)


class IsraeliNewsScraper(WebNewsScraper):
    """Enhanced scraper for Israeli news sites with humor detection"""
    
    def __init__(self, media_cache_dir: str = "outputs/news_media_cache"):
        super().__init__(media_cache_dir)
        
        # Add Israeli site configs
        self.site_configs.update({
            "ynet.co.il": {
                "article_selector": ".slotView, .element-group, article.art",
                "title_selector": "h1.mainTitle, .element-title, .art_header_title",
                "content_selector": ".element-preview, .art_body, p.text14",
                "image_selector": ".element-image img, .art_img_border img",
                "video_selector": ".mediaPlayer, video",
                "date_selector": ".element-time, .art_header_footer_author",
                "author_selector": ".element-author, .art_header_author",
                "comments_selector": ".comment-count"
            },
            "rotter.net": {
                "article_selector": ".scoop-item, .forum-post",
                "title_selector": "h2, .post-title",
                "content_selector": "p, .post-content",
                "image_selector": "img",
                "date_selector": ".time, .post-time",
                "author_selector": ".author, .post-author"
            }
        })
        
        # Humor and interest scoring keywords (Hebrew)
        self.humor_keywords = [
            "מביך", "נתפס", "בושה", "פדיחה", "קרה", "מצחיק", "ביזיון",
            "סקנדל", "דרמה", "הלם", "לא יאומן", "בלעדי", "חשיפה"
        ]
        
        self.dark_humor_patterns = [
            r"למרות ש.*עדיין",  # Despite... still...
            r"לפחות.*לא",      # At least... not...
            r"טוב ש.*אחרת",     # Good that... otherwise...
        ]
    
    async def scrape_with_scoring(self, source: NewsSource) -> List[ContentItem]:
        """Scrape and score articles for interest and humor"""
        articles = await self.scrape(source)
        
        # Score each article
        for article in articles:
            article.metadata["humor_score"] = self._calculate_humor_score(article)
            article.metadata["interest_score"] = self._calculate_interest_score(article)
            article.metadata["is_bizarre"] = self._is_bizarre_news(article)
        
        # Sort by combined score
        articles.sort(key=lambda x: (
            x.metadata.get("interest_score", 0) + 
            x.metadata.get("humor_score", 0)
        ), reverse=True)
        
        return articles
    
    def _calculate_humor_score(self, article: ContentItem) -> float:
        """Calculate humor potential score (0-1)"""
        score = 0.0
        text = f"{article.title} {article.content}".lower()
        
        # Check humor keywords
        for keyword in self.humor_keywords:
            if keyword in text:
                score += 0.1
        
        # Check dark humor patterns
        for pattern in self.dark_humor_patterns:
            if re.search(pattern, text):
                score += 0.15
        
        # Boost score for certain categories
        if any(cat in article.categories for cat in ["תרבות", "בידור", "ספורט"]):
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_interest_score(self, article: ContentItem) -> float:
        """Calculate general interest score (0-1)"""
        score = 0.5  # Base score
        
        # Has media
        if article.has_video():
            score += 0.2
        elif article.has_images():
            score += 0.1
        
        # Has many comments (if available)
        comments = article.metadata.get("comments_count", 0)
        if comments > 100:
            score += 0.2
        elif comments > 50:
            score += 0.1
        
        # Recent news
        if article.published_date > datetime.now() - timedelta(hours=6):
            score += 0.2
        
        # Controversial topics
        controversial_keywords = ["פוליטי", "ביבי", "בחירות", "מחאה", "שחיתות"]
        if any(kw in article.content for kw in controversial_keywords):
            score += 0.15
        
        return min(score, 1.0)
    
    def _is_bizarre_news(self, article: ContentItem) -> bool:
        """Check if article is bizarre/unusual news"""
        bizarre_indicators = [
            "מוזר", "תמוה", "חריג", "נדיר", "פלא", "לא שגרתי",
            "מפתיע", "יוצא דופן", "מטורף", "הזוי"
        ]
        
        text = f"{article.title} {article.content}".lower()
        return any(indicator in text for indicator in bizarre_indicators)


class YnetScraper(IsraeliNewsScraper):
    """Specialized Ynet scraper"""
    
    async def scrape_ynet_homepage(self) -> List[ContentItem]:
        """Scrape Ynet homepage for top stories"""
        source = NewsSource(
            id="ynet_homepage",
            name="Ynet Homepage",
            source_type=SourceType.WEB,
            url="https://www.ynet.co.il",
            scraping_config=ScrapingConfig(max_items=20)
        )
        
        return await self.scrape_with_scoring(source)
    
    async def scrape_ynet_bizarre(self) -> List[ContentItem]:
        """Scrape Ynet's bizarre news section"""
        source = NewsSource(
            id="ynet_bizarre",
            name="Ynet Bizarre",
            source_type=SourceType.WEB,
            url="https://www.ynet.co.il/news/category/184",  # מוזר section
            scraping_config=ScrapingConfig(max_items=10)
        )
        
        articles = await self.scrape_with_scoring(source)
        # Boost humor scores for bizarre section
        for article in articles:
            article.metadata["humor_score"] = min(
                article.metadata.get("humor_score", 0) + 0.3, 1.0
            )
        
        return articles


class RotterScraper(IsraeliNewsScraper):
    """Specialized Rotter.net scraper for scoops"""
    
    async def scrape_rotter_scoops(self) -> List[ContentItem]:
        """Scrape Rotter scoops section"""
        source = NewsSource(
            id="rotter_scoops",
            name="Rotter Scoops",
            source_type=SourceType.WEB,
            url="https://rotter.net/scoops",
            scraping_config=ScrapingConfig(max_items=15)
        )
        
        # Rotter often has gossip and political scoops
        articles = await self.scrape_with_scoring(source)
        
        # Boost scores for exclusive/scoop content
        for article in articles:
            if any(word in article.title for word in ["בלעדי", "חשיפה", "דחוף"]):
                article.metadata["interest_score"] = min(
                    article.metadata.get("interest_score", 0) + 0.3, 1.0
                )
        
        return articles
    
    async def _extract_articles(
        self, 
        soup: BeautifulSoup, 
        source: NewsSource,
        config: Dict[str, str]
    ) -> List[ContentItem]:
        """Override to handle Rotter's unique structure"""
        articles = await super()._extract_articles(soup, source, config)
        
        # Rotter specific: extract user reactions/votes if available
        for article, element in zip(articles, soup.select(config["article_selector"])):
            votes = element.select_one(".votes, .reactions")
            if votes:
                article.metadata["user_votes"] = votes.get_text(strip=True)
        
        return articles