"""Real Ynet scraper that actually works - NO MOCK DATA"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List
import ssl

from ...utils.logging_config import get_logger
from ..models.content_models import ContentItem, NewsSource, MediaAsset, AssetType, ContentStatus, SourceType

logger = get_logger(__name__)


class RealYnetScraper:
    """Real scraper for Ynet that actually gets current news"""
    
    async def scrape_ynet(self) -> List[ContentItem]:
        """Scrape real news from Ynet"""
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'he,en;q=0.9',
        }
        
        # Disable SSL verification for Ynet (cert issues)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            try:
                # Ynet main page
                async with session.get('https://www.ynet.co.il', headers=headers, allow_redirects=True) as resp:
                    if resp.status != 200:
                        logger.error(f"Failed to fetch Ynet: status {resp.status}")
                        return []
                    
                    html = await resp.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    articles = []
                    
                    # Multiple selectors to catch different article formats
                    selectors = [
                        'div.layoutItem',
                        'article',
                        'div[class*="article"]',
                        'div.slotView'
                    ]
                    
                    source = NewsSource(
                        id="ynet_real",
                        name="Ynet",
                        source_type=SourceType.WEB,
                        url="https://www.ynet.co.il"
                    )
                    
                    for selector in selectors:
                        elements = soup.select(selector)[:10]  # Limit to 10 per selector
                        
                        for elem in elements:
                            # Extract title
                            title = None
                            for title_sel in ['h2', 'h3', '.titleRow', '.title', 'a[title]']:
                                title_elem = elem.select_one(title_sel)
                                if title_elem:
                                    title = title_elem.get_text(strip=True)
                                    if not title and title_elem.get('title'):
                                        title = title_elem.get('title')
                                    if title and len(title) > 10:
                                        break
                            
                            if not title:
                                continue
                            
                            # Extract content
                            content = None
                            for content_sel in ['.textRow', '.subtitle', '.text', 'p']:
                                content_elem = elem.select_one(content_sel)
                                if content_elem:
                                    content = content_elem.get_text(strip=True)
                                    if content and len(content) > 20:
                                        break
                            
                            # Extract image
                            media_assets = []
                            img_elem = elem.select_one('img')
                            if img_elem:
                                image = img_elem.get('src') or img_elem.get('data-src')
                                if image:
                                    if not image.startswith('http'):
                                        image = f"https://www.ynet.co.il{image}"
                                    media_assets.append(MediaAsset(
                                        id=f"img_{len(articles)}",
                                        asset_type=AssetType.IMAGE,
                                        source_url=image
                                    ))
                            
                            # Extract URL
                            url = None
                            link_elem = elem.select_one('a[href]')
                            if link_elem:
                                url = link_elem.get('href')
                                if url and not url.startswith('http'):
                                    url = f"https://www.ynet.co.il{url}"
                            
                            if title:
                                article = ContentItem(
                                    id=f"ynet_{datetime.now().timestamp()}_{len(articles)}",
                                    source=source,
                                    title=title,
                                    content=content or '',
                                    url=url or '',
                                    media_assets=media_assets,
                                    published_date=datetime.now(),
                                    language='he',
                                    categories=['news'],
                                    status=ContentStatus.SCRAPED,
                                    metadata={'real_scrape': True}
                                )
                                articles.append(article)
                    
                    # Deduplicate by title
                    seen_titles = set()
                    unique_articles = []
                    for article in articles:
                        if article.title not in seen_titles:
                            seen_titles.add(article.title)
                            unique_articles.append(article)
                    
                    logger.info(f"✅ Scraped {len(unique_articles)} REAL articles from Ynet")
                    return unique_articles
                    
            except Exception as e:
                logger.error(f"Error scraping Ynet: {e}")
                return []
        
        return []