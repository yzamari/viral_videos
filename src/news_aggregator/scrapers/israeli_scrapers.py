"""Specialized scrapers for Israeli news sites"""

import re
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import aiohttp

from ...utils.logging_config import get_logger
from ..models.content_models import ContentItem, NewsSource, MediaAsset, AssetType, ContentStatus, SourceType, ScrapingConfig
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
        # For Rotter, we'll bypass the web_scraper issue by directly fetching
        import aiohttp
        import ssl
        import certifi
        from bs4 import BeautifulSoup
        
        url = "https://rotter.net/scoopscache.html"
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"RotterScraper: Directly scraping {url}")
        
        articles = []
        
        try:
            # Create SSL context
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Parse Rotter scoops
                        rows = soup.select('table tbody tr')
                        
                        for row in rows[:15]:  # Limit to 15 items
                            try:
                                # Extract title
                                title_elem = row.select_one('td font[size="3"] b')
                                if not title_elem:
                                    continue
                                    
                                title = title_elem.get_text(strip=True)
                                
                                # Extract content
                                content_elem = row.select('td')[1] if len(row.select('td')) > 1 else None
                                content = content_elem.get_text(strip=True) if content_elem else ""
                                
                                # Extract URL
                                link_elem = row.select_one('a[href*="scoops"]')
                                article_url = f"https://rotter.net{link_elem['href']}" if link_elem and 'href' in link_elem.attrs else url
                                
                                # Create ContentItem
                                from ..models.content_models import ContentItem, NewsSource, SourceType, ContentStatus
                                source = NewsSource(
                                    id="rotter_scoops",
                                    name="Rotter Scoops",
                                    source_type=SourceType.WEB,
                                    url=url
                                )
                                
                                article = ContentItem(
                                    id=f"rotter_{len(articles)}",
                                    source=source,
                                    title=title,
                                    content=content,
                                    url=article_url,
                                    media_assets=[],
                                    published_date=datetime.now(),
                                    language='he',
                                    categories=['gossip', 'politics'],
                                    status=ContentStatus.SCRAPED,
                                    metadata={}
                                )
                                
                                # Add humor and interest scores
                                article.metadata["humor_score"] = self._calculate_humor_score(article)
                                article.metadata["interest_score"] = self._calculate_interest_score(article)
                                article.metadata["is_bizarre"] = self._is_bizarre_news(article)
                                
                                # Boost scores for exclusive/scoop content
                                if any(word in title for word in ["בלעדי", "חשיפה", "דחוף"]):
                                    article.metadata["interest_score"] = min(
                                        article.metadata.get("interest_score", 0) + 0.3, 1.0
                                    )
                                
                                articles.append(article)
                                
                            except Exception as e:
                                logger.warning(f"Failed to parse Rotter article: {e}")
                                continue
                        
                        logger.info(f"✅ Scraped {len(articles)} articles from Rotter")
                    else:
                        logger.error(f"Failed to fetch Rotter: Status {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to scrape Rotter: {e}")
        
        # Sort by combined score
        articles.sort(key=lambda x: (
            x.metadata.get("interest_score", 0) + 
            x.metadata.get("humor_score", 0)
        ), reverse=True)
        
        return articles[:15]  # Return top 15
    
    async def scrape_with_scoring(self, source: NewsSource) -> List[ContentItem]:
        """Override to avoid the web_scraper issue"""
        # For Rotter, we handle everything in scrape_rotter_scoops
        return await self.scrape_rotter_scoops()
    
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