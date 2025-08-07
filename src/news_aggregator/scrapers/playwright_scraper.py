"""
Playwright-based web scraper for sites that block regular HTTP requests
"""

import asyncio
from typing import Dict, List, Optional, Any
import json
import os
from datetime import datetime

try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    async_playwright = None
    Browser = None
    Page = None

try:
    from ...utils.logging_config import get_logger
except ImportError:
    import logging
    def get_logger(name):
        return logging.getLogger(name)

logger = get_logger(__name__)


class PlaywrightScraper:
    """Advanced web scraper using Playwright for JavaScript rendering and anti-bot bypass"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.playwright = None
        
    async def __aenter__(self):
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright not available. Install with: pip install playwright")
        
        self.playwright = await async_playwright().start()
        
        # Create browser context with stealth settings and user agent
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def scrape_website(self, config: Dict[str, Any], max_items: int = 20) -> List[Dict[str, Any]]:
        """Scrape website using Playwright with stealth mode"""
        
        if not self.browser:
            raise RuntimeError("Browser not initialized. Use async context manager.")
        
        url = config['base_url']
        selectors = config.get('selectors', {})
        name = config.get('name', 'Unknown')
        
        logger.info(f"🎭 Playwright scraping {name} from {url}")
        
        # Create browser context with user agent and viewport
        context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={"width": 1920, "height": 1080},
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9,he;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        )
        
        # Create new page from context
        page = await context.new_page()
        
        try:
            
            # Navigate to the page with timeout
            logger.info(f"📄 Loading page: {url}")
            response = await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            if not response or not response.ok:
                logger.error(f"❌ Failed to load page: status {response.status if response else 'None'}")
                return []
            
            # Wait for content to load
            await page.wait_for_timeout(2000)
            
            # Extract articles using configured selectors
            articles = await self._extract_articles_playwright(page, selectors, max_items)
            
            logger.info(f"✅ Playwright found {len(articles)} articles from {name}")
            return articles
            
        except Exception as e:
            logger.error(f"❌ Playwright scraping failed for {name}: {e}")
            return []
        finally:
            await page.close()
            await context.close()
    
    async def _extract_articles_playwright(self, page: Page, selectors: Dict[str, str], max_items: int) -> List[Dict[str, Any]]:
        """Extract articles using Playwright page methods"""
        
        articles = []
        container_selector = selectors.get('article_container', 'article')
        
        # Find article containers
        containers = await page.query_selector_all(container_selector)
        logger.info(f"🔍 Found {len(containers)} article containers with selector '{container_selector}'")
        
        if not containers:
            # Try alternative selectors if main one fails
            alternative_selectors = [
                'article', '.article', '.news-item', '.post', '.story',
                '[data-testid*="article"]', '[data-testid*="story"]',
                '.content-item', '.news-card', '.article-card'
            ]
            
            for alt_selector in alternative_selectors:
                containers = await page.query_selector_all(alt_selector)
                if containers:
                    logger.info(f"🎯 Found {len(containers)} containers with alternative selector '{alt_selector}'")
                    break
        
        # Process each container
        for i, container in enumerate(containers[:max_items]):
            try:
                article_data = await self._extract_single_article(container, selectors, page.url)
                if article_data and article_data.get('title'):
                    articles.append(article_data)
                    
            except Exception as e:
                logger.warning(f"⚠️ Failed to extract article {i}: {e}")
                continue
        
        return articles
    
    async def _extract_single_article(self, container, selectors: Dict[str, str], page_url: str = None) -> Optional[Dict[str, Any]]:
        """Extract data from a single article container"""
        
        article_data = {
            'title': '',
            'description': '',
            'url': '',
            'images': [],
            'videos': [],
            'category': 'news'
        }
        
        try:
            # Extract title
            title_selector = selectors.get('title', 'h1, h2, h3')
            if title_selector:
                title_element = await container.query_selector(title_selector)
                if title_element:
                    article_data['title'] = (await title_element.text_content() or '').strip()
                else:
                    # If title selector doesn't match, try getting first substantial text
                    all_text = (await container.text_content() or '').strip()
                    if all_text and len(all_text) > 20:
                        # Use first line or first 100 chars as title
                        article_data['title'] = all_text.split('\n')[0][:100]
            else:
                # If no title selector, use the container text itself
                article_data['title'] = (await container.text_content() or '').strip()[:100]
            
            # Extract description
            desc_selector = selectors.get('description', '.summary, .excerpt, p')
            if desc_selector:
                desc_element = await container.query_selector(desc_selector)
                if desc_element:
                    article_data['description'] = (await desc_element.text_content() or '').strip()
            
            # Extract URL
            url_selector = selectors.get('url', 'a')
            if url_selector:
                url_element = await container.query_selector(url_selector)
                if url_element:
                    href = await url_element.get_attribute('href')
                    if href:
                        # Handle relative URLs
                        if href.startswith('/'):
                            from urllib.parse import urljoin
                            article_data['url'] = urljoin(page_url, href) if page_url else href
                        else:
                            article_data['url'] = href
            else:
                # If container is an <a> element, use its href
                if await container.evaluate('element => element.tagName.toLowerCase()') == 'a':
                    href = await container.get_attribute('href')
                    if href:
                        from urllib.parse import urljoin
                        article_data['url'] = urljoin(page_url, href) if href.startswith('/') and page_url else href
            
            # Extract images
            img_selector = selectors.get('image', 'img')
            img_elements = await container.query_selector_all(img_selector)
            for img in img_elements:
                src = await img.get_attribute('src')
                if src and not src.startswith('data:'):
                    article_data['images'].append(src)
            
            # Extract videos  
            video_selector = selectors.get('video', 'video')
            video_elements = await container.query_selector_all(video_selector)
            for video in video_elements:
                src = await video.get_attribute('src')
                if src:
                    article_data['videos'].append(src)
            
            return article_data if article_data['title'] else None
            
        except Exception as e:
            logger.warning(f"⚠️ Error extracting article data: {e}")
            return None


async def test_playwright_scraping():
    """Test function to validate Playwright scraping"""
    
    test_configs = [
        {
            'name': 'Ynet',
            'base_url': 'https://www.ynet.co.il',
            'selectors': {
                'article_container': 'article, .element-article, [data-tb-region]',
                'title': 'h1, h2, h3, .title, .slotTitle',
                'description': '.summary, .subtitle, .slotSubTitle',
                'url': 'a'
            }
        },
        {
            'name': 'Rotter',
            'base_url': 'https://rotter.net/scoopscache.html',
            'selectors': {
                'article_container': 'tr, table tbody tr',
                'title': 'font b, b, strong, td',
                'description': 'td:nth-child(2)',
                'url': 'a'
            }
        }
    ]
    
    async with PlaywrightScraper() as scraper:
        for config in test_configs:
            articles = await scraper.scrape_website(config, max_items=5)
            print(f"\n{config['name']}:")
            for i, article in enumerate(articles):
                print(f"  {i+1}. {article['title'][:80]}...")
                if article['description']:
                    print(f"     {article['description'][:100]}...")


if __name__ == "__main__":
    if PLAYWRIGHT_AVAILABLE:
        asyncio.run(test_playwright_scraping())
    else:
        print("Playwright not available. Install with: pip install playwright")