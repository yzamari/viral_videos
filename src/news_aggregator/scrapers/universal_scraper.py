#!/usr/bin/env python3
"""
Universal News Scraper - Configurable scraper for any news website
No need to write new code for each website!
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
import json
import os
import re
from datetime import datetime
import ssl
import certifi

try:
    from .playwright_scraper import PlaywrightScraper
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PlaywrightScraper = None
    PLAYWRIGHT_AVAILABLE = False


class ScraperConfig:
    """Configuration for a specific website"""
    
    def __init__(self, config_dict: Dict):
        self.name = config_dict['name']
        self.base_url = config_dict['base_url']
        self.selectors = config_dict.get('selectors', {})
        self.patterns = config_dict.get('patterns', {})
        self.headers = config_dict.get('headers', {})
        self.encoding = config_dict.get('encoding', 'utf-8')
        self.language = config_dict.get('language', 'en')
        self.category_mapping = config_dict.get('category_mapping', {})
        self.media_extraction = config_dict.get('media_extraction', {})
        self.fallback_content = config_dict.get('fallback_content', [])
        self.follow_embedded_links = config_dict.get('follow_embedded_links', True)  # Enable by default
        self.max_link_depth = config_dict.get('max_link_depth', 1)  # How deep to follow links
        self.max_links_to_follow = config_dict.get('max_links_to_follow', 5)  # Max links per article


class UniversalNewsScraper:
    """Universal scraper that works with any news website using configuration"""
    
    def __init__(self):
        self.configs = {}
        self.load_configurations()
        
    def load_configurations(self):
        """Load all website configurations"""
        config_dir = "scraper_configs"
        os.makedirs(config_dir, exist_ok=True)
        
        # Load existing configs
        for filename in os.listdir(config_dir):
            if filename.endswith('.json'):
                with open(os.path.join(config_dir, filename), 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    site_id = filename.replace('.json', '')
                    self.configs[site_id] = ScraperConfig(config)
    
    def add_website_config(self, site_id: str, config: Dict):
        """Add configuration for a new website"""
        # Save config
        config_path = f"scraper_configs/{site_id}.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        # Load into memory
        self.configs[site_id] = ScraperConfig(config)
        print(f"✅ Added configuration for {config['name']}")
    
    async def scrape_website(self, site_id: str, max_items: int = 20, fetch_article_media: bool = True) -> List[Dict]:
        """Scrape any configured website"""
        
        if site_id not in self.configs:
            raise ValueError(f"No configuration found for site: {site_id}")
        
        config = self.configs[site_id]
        print(f"🔍 Scraping {config.name}...")
        
        articles = []
        
        # Check if this is a fallback content config (for testing/demo)
        if hasattr(config, 'fallback_content') and config.fallback_content:
            print(f"  💡 Using fallback content for {config.name}")
            for item in config.fallback_content:
                articles.append({
                    'title': item.get('title', ''),
                    'description': item.get('description', ''),
                    'url': item.get('url', config.base_url),
                    'images': item.get('images', []),
                    'videos': item.get('videos', []),
                    'category': item.get('category', 'news'),
                    'article_images': item.get('images', []),  # Add images as article_images too
                    'article_videos': item.get('videos', []),  # Add videos as article_videos too
                    'embedded_links': item.get('embedded_links', [])
                })
            print(f"  ✅ Found {len(articles)} fallback articles from {config.name}")
            return articles
        
        # Create SSL context - disable verification for problematic sites
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            try:
                # Add default headers if not specified
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    **config.headers
                }
                
                async with session.get(config.base_url, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract articles using configured selectors
                        articles = self._extract_articles(soup, config, max_items)
                        
                        # Fetch media from article pages if requested
                        if fetch_article_media and len(articles) > 0:
                            print(f"  📸 Fetching media from article pages...")
                            articles = await self._enhance_articles_with_media(articles, config, session)
                        
                        print(f"  ✅ Found {len(articles)} articles from {config.name}")
                        if len(articles) == 0:
                            # Debug: Show what containers were found
                            containers = soup.select(config.selectors.get('article_container', ''))
                            print(f"  🔍 Debug: Found {len(containers)} article containers with selector '{config.selectors.get('article_container', '')}'")
                            if len(containers) > 0:
                                print(f"  🔍 First container HTML: {str(containers[0])[:200]}...")
                            
                            # If no articles found, try Playwright as fallback
                            print(f"  🎭 No articles extracted, trying Playwright for {config.name}...")
                            articles = await self._try_playwright_scraping(config, max_items)
                    else:
                        print(f"  ❌ Failed to fetch {config.name}: Status {response.status}")
                        if response.status == 403:
                            print(f"  🎭 Trying Playwright for {config.name}...")
                            articles = await self._try_playwright_scraping(config, max_items)
                        
            except Exception as e:
                print(f"  ❌ Error scraping {config.name}: {e}")
                if "403" in str(e) or "blocked" in str(e).lower():
                    print(f"  🎭 Trying Playwright for {config.name}...")
                    articles = await self._try_playwright_scraping(config, max_items)
        
        return articles
    
    async def _try_playwright_scraping(self, config: ScraperConfig, max_items: int) -> List[Dict]:
        """Try scraping with Playwright when regular scraping fails"""
        
        if not PLAYWRIGHT_AVAILABLE:
            print("  ⚠️ Playwright not available, skipping advanced scraping")
            return []
        
        try:
            playwright_config = {
                'name': config.name,
                'base_url': config.base_url,
                'selectors': config.selectors
            }
            
            async with PlaywrightScraper() as scraper:
                articles = await scraper.scrape_website(playwright_config, max_items)
                print(f"  ✅ Playwright found {len(articles)} articles from {config.name}")
                return articles
                
        except Exception as e:
            print(f"  ❌ Playwright scraping also failed for {config.name}: {e}")
            return []
    
    def _extract_articles(self, soup: BeautifulSoup, config: ScraperConfig, 
                         max_items: int) -> List[Dict]:
        """Extract articles using configuration"""
        
        articles = []
        
        # Find article containers
        article_elements = soup.select(config.selectors.get('article_container', 'article'))
        
        for element in article_elements[:max_items]:
            article = self._parse_article_element(element, config)
            if article and self._validate_article(article):
                articles.append(article)
        
        return articles
    
    def _parse_article_element(self, element, config: ScraperConfig) -> Optional[Dict]:
        """Parse a single article element"""
        
        try:
            article = {
                'source': config.name,
                'language': config.language,
                'scraped_at': datetime.now().isoformat()
            }
            
            # Extract title
            title_selector = config.selectors.get('title', 'h1, h2, h3, h4')
            title_elem = element.select_one(title_selector)
            if title_elem:
                article['title'] = title_elem.get_text(strip=True)
            else:
                return None
            
            # Extract URL
            url_selector = config.selectors.get('url', 'a[href]')
            url_elem = element.select_one(url_selector)
            if url_elem and url_elem.get('href'):
                url = url_elem['href']
                if not url.startswith('http'):
                    url = config.base_url.rstrip('/') + '/' + url.lstrip('/')
                article['url'] = url
                article['article_url'] = url  # Store for later media extraction
            
            # Extract description
            desc_selector = config.selectors.get('description', 'p')
            if desc_selector:
                desc_elem = element.select_one(desc_selector)
                if desc_elem:
                    article['description'] = desc_elem.get_text(strip=True)
            
            # Extract media from preview (may be enhanced later from full article)
            article['media_items'] = self._extract_media(element, config)
            
            # Extract category
            article['category'] = self._determine_category(article, config)
            
            # Extract metadata
            self._extract_metadata(element, article, config)
            
            return article
            
        except Exception as e:
            return None
    
    def _extract_media(self, element, config: ScraperConfig) -> List[Dict]:
        """Extract media items from article"""
        
        media_items = []
        
        # Extract images
        img_selector = config.media_extraction.get('image_selector', 'img[src]')
        for img in element.select(img_selector):
            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            if src:
                if not src.startswith('http'):
                    src = config.base_url.rstrip('/') + '/' + src.lstrip('/')
                
                media_items.append({
                    'type': 'image',
                    'url': src,
                    'alt': img.get('alt', ''),
                    'caption': img.get('title', '')
                })
        
        # Extract videos
        video_selector = config.media_extraction.get('video_selector', 'video source[src]')
        for video in element.select(video_selector):
            src = video.get('src')
            if src:
                if not src.startswith('http'):
                    src = config.base_url.rstrip('/') + '/' + src.lstrip('/')
                
                media_items.append({
                    'type': 'video',
                    'url': src
                })
        
        return media_items
    
    def _determine_category(self, article: Dict, config: ScraperConfig) -> str:
        """Determine article category"""
        
        # Check URL patterns
        url = article.get('url', '')
        for pattern, category in config.patterns.get('category_patterns', {}).items():
            if pattern in url:
                return category
        
        # Check content keywords
        text = f"{article.get('title', '')} {article.get('description', '')}".lower()
        
        # Use configured category mapping
        for category, keywords in config.category_mapping.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return 'general'
    
    def _extract_metadata(self, element, article: Dict, config: ScraperConfig):
        """Extract additional metadata"""
        
        # Author
        author_selector = config.selectors.get('author')
        if author_selector:
            author_elem = element.select_one(author_selector)
            if author_elem:
                article['author'] = author_elem.get_text(strip=True)
        
        # Date
        date_selector = config.selectors.get('date')
        if date_selector:
            date_elem = element.select_one(date_selector)
            if date_elem:
                article['published_date'] = date_elem.get_text(strip=True)
        
        # Tags
        tag_selector = config.selectors.get('tags')
        if tag_selector:
            tags = [tag.get_text(strip=True) for tag in element.select(tag_selector)]
            if tags:
                article['tags'] = tags
    
    def _validate_article(self, article: Dict) -> bool:
        """Validate that article has minimum required fields"""
        return bool(article.get('title') and len(article.get('title', '')) > 10)
    
    async def _extract_and_follow_links(self, soup: BeautifulSoup, config: ScraperConfig, session: aiohttp.ClientSession, depth: int = 1, max_depth: int = 2) -> List[Dict]:
        """Extract and follow links within article content to find additional media"""
        
        if depth > max_depth:
            return []
        
        media_from_links = []
        processed_urls = set()  # Avoid processing same URL twice
        
        try:
            # Find links in article content
            # Look for links in common article content areas
            content_selectors = [
                'article a[href]',
                '.article-content a[href]',
                '.entry-content a[href]',
                '.content a[href]',
                'main a[href]',
                'p a[href]'  # Links within paragraphs
            ]
            
            links = []
            for selector in content_selectors:
                links.extend(soup.select(selector))
            
            # Filter links to external sites (likely to have media)
            external_links = []
            for link in links[:10]:  # Limit to first 10 links to avoid too many requests
                href = link.get('href', '')
                
                # Skip if already processed
                if href in processed_urls:
                    continue
                    
                # Filter relevant links (skip social media sharing, navigation, etc.)
                if any(skip in href.lower() for skip in ['facebook', 'twitter', 'whatsapp', 'telegram', 'mailto:', 'javascript:', '#', 'share', 'print']):
                    continue
                
                # Check if it's a full URL
                if href.startswith('http'):
                    # Check if it's external (different domain)
                    if config.base_url not in href:
                        external_links.append(href)
                        processed_urls.add(href)
                elif href.startswith('/'):
                    # Internal link - might still have media
                    full_url = config.base_url.rstrip('/') + href
                    external_links.append(full_url)
                    processed_urls.add(full_url)
            
            # Follow each link and extract media
            max_links = config.max_links_to_follow if hasattr(config, 'max_links_to_follow') else 5
            for url in external_links[:max_links]:  # Limit to configured max links
                try:
                    print(f"      🔍 Following link: {url[:50]}...")
                    
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1'
                    }
                    
                    async with session.get(url, headers=headers, timeout=5, allow_redirects=True) as response:
                        if response.status == 200:
                            html = await response.text()
                            link_soup = BeautifulSoup(html, 'html.parser')
                            
                            # Extract images from linked page
                            img_selectors = [
                                'img[src*="upload"]',
                                'img[src*="media"]',
                                'img[src*="image"]',
                                'article img',
                                'main img',
                                '.content img',
                                'figure img',
                                'picture img'
                            ]
                            
                            found_images = set()
                            for selector in img_selectors:
                                for img in link_soup.select(selector):
                                    src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                                    if src:
                                        # Make URL absolute
                                        if not src.startswith('http'):
                                            # Get base URL of the linked page
                                            from urllib.parse import urlparse, urljoin
                                            base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
                                            src = urljoin(base, src)
                                        
                                        # Filter out small images (likely icons)
                                        width = img.get('width')
                                        if width:
                                            width_str = str(width).replace('px', '').strip()
                                            if width_str and width_str.isdigit() and int(width_str) < 100:
                                                continue
                                        
                                        if src not in found_images:
                                            found_images.add(src)
                                            media_from_links.append({
                                                'type': 'image',
                                                'url': src,
                                                'source': url,
                                                'alt': img.get('alt', '')
                                            })
                            
                            # Extract videos from linked page
                            video_selectors = [
                                'video source[src]',
                                'video[src]',
                                'iframe[src*="youtube"]',
                                'iframe[src*="vimeo"]',
                                'iframe[src*="dailymotion"]'
                            ]
                            
                            for selector in video_selectors:
                                for video in link_soup.select(selector):
                                    src = video.get('src')
                                    if src:
                                        if not src.startswith('http'):
                                            from urllib.parse import urlparse, urljoin
                                            base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
                                            src = urljoin(base, src)
                                        
                                        media_from_links.append({
                                            'type': 'video',
                                            'url': src,
                                            'source': url
                                        })
                            
                            if found_images or media_from_links:
                                print(f"        ✅ Found {len(found_images)} images from {urlparse(url).netloc}")
                            
                except Exception as e:
                    print(f"        ⚠️ Could not fetch {url[:30]}...: {str(e)[:50]}")
                    continue
            
        except Exception as e:
            print(f"      ⚠️ Error extracting links: {e}")
        
        return media_from_links
    
    async def _enhance_articles_with_media(self, articles: List[Dict], config: ScraperConfig, session: aiohttp.ClientSession) -> List[Dict]:
        """Fetch media from individual article pages and follow embedded links"""
        enhanced_articles = []
        
        for article in articles[:5]:  # Limit to first 5 to avoid too many requests
            try:
                if article.get('article_url'):
                    # Fetch the article page
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        **config.headers
                    }
                    
                    async with session.get(article['article_url'], headers=headers, timeout=5) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Extract links from article content for additional media (if enabled)
                            embedded_links = []
                            if config.follow_embedded_links:
                                embedded_links = await self._extract_and_follow_links(
                                    soup, config, session, 
                                    depth=1, 
                                    max_depth=config.max_link_depth
                                )
                            
                            # Extract images from article page
                            images = []
                            
                            # Common selectors for article images
                            img_selectors = [
                                'article img',
                                '.article-content img',
                                '.entry-content img',
                                'main img',
                                'img[src*="upload"]',
                                'img[src*="media"]',
                                'img[src*="image"]'
                            ]
                            
                            for selector in img_selectors:
                                for img in soup.select(selector)[:3]:  # Max 3 images per article
                                    src = img.get('src') or img.get('data-src')
                                    if src:
                                        if not src.startswith('http'):
                                            src = config.base_url.rstrip('/') + '/' + src.lstrip('/')
                                        if src not in images and 'icon' not in src.lower() and 'logo' not in src.lower():
                                            images.append(src)
                            
                            # Extract videos from article page
                            videos = []
                            video_selectors = [
                                'video source',
                                'iframe[src*="youtube"]',
                                'iframe[src*="vimeo"]',
                                '.video-container iframe'
                            ]
                            
                            for selector in video_selectors:
                                for video in soup.select(selector)[:2]:  # Max 2 videos per article
                                    src = video.get('src')
                                    if src and src not in videos:
                                        videos.append(src)
                            
                            # Update article with found media
                            if images:
                                article['article_images'] = images
                                article['primary_image'] = images[0]
                                print(f"    📷 Found {len(images)} images for: {article['title'][:50]}...")
                            
                            if videos:
                                article['article_videos'] = videos
                                print(f"    🎥 Found {len(videos)} videos for: {article['title'][:50]}...")
                            
                            # Add media from embedded links
                            if embedded_links:
                                for link_media in embedded_links:
                                    if link_media['type'] == 'image' and link_media['url'] not in images:
                                        images.append(link_media['url'])
                                    elif link_media['type'] == 'video' and link_media['url'] not in videos:
                                        videos.append(link_media['url'])
                                
                                if embedded_links:
                                    print(f"    🔗 Found {len(embedded_links)} media items from embedded links")
                                    # Update article with additional media
                                    article['article_images'] = images
                                    article['article_videos'] = videos
            
            except Exception as e:
                print(f"    ⚠️ Could not fetch media from article: {e}")
            
            enhanced_articles.append(article)
        
        # Add remaining articles without enhancement
        enhanced_articles.extend(articles[5:])
        
        return enhanced_articles
    
    async def scrape(self, source, hours_back: int = 24) -> List:
        """Scrape method to match the expected interface"""
        from ..models.content_models import ContentItem, MediaAsset, AssetType, ContentStatus
        
        # Determine site_id from URL
        site_id = None
        if "ynet" in source.url.lower():
            site_id = "ynet"
        elif "rotter" in source.url.lower():
            site_id = "rotter"
        elif "mako" in source.url.lower():
            site_id = "mako"
        elif "sport5" in source.url.lower():
            site_id = "sport5"
        elif "cnn" in source.url.lower():
            site_id = "cnn"
        elif "i24" in source.url.lower():
            site_id = "i24news"
        
        if not site_id or site_id not in self.configs:
            # Try to scrape as generic website
            return await self._scrape_generic_website(source, hours_back)
        
        # Use configured scraper
        articles_data = await self.scrape_website(site_id, max_items=20)
        
        # Convert to ContentItem format
        content_items = []
        for data in articles_data:
            media_assets = []
            
            # Add image assets
            for img in data.get('images', []):
                media_assets.append(MediaAsset(
                    id=f"img_{len(media_assets)}",
                    asset_type=AssetType.IMAGE,
                    source_url=img
                ))
            
            # Add video assets
            for vid in data.get('videos', []):
                media_assets.append(MediaAsset(
                    id=f"vid_{len(media_assets)}",
                    asset_type=AssetType.VIDEO,
                    source_url=vid
                ))
            
            content_item = ContentItem(
                id=f"{site_id}_{datetime.now().timestamp()}_{len(content_items)}",
                source=source,
                title=data.get('title', ''),
                content=data.get('description', ''),
                url=data.get('url', ''),
                media_assets=media_assets,
                published_date=datetime.now(),
                language=self.configs[site_id].language if site_id in self.configs else 'en',
                categories=[data.get('category', 'general')],
                status=ContentStatus.SCRAPED,
                metadata=data
            )
            content_items.append(content_item)
        
        return content_items
    
    async def _scrape_generic_website(self, source, hours_back: int) -> List:
        """Fallback generic website scraping"""
        from ..models.content_models import ContentItem, ContentStatus
        import logging
        
        logger = logging.getLogger(__name__)
        logger.warning(f"No specific configuration for {source.url}, attempting generic scraping")
        
        # For now, return empty list - you can implement generic scraping logic here
        return []
    
    async def _scrape_url(self, url: str, site_id: str) -> Optional[Dict]:
        """Scrape a specific URL using the site configuration"""
        if site_id not in self.configs:
            return None
        
        config = self.configs[site_id]
        
        # Create SSL context - disable verification for problematic sites
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    **config.headers
                }
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract data using configured selectors
                        article = {
                            'url': url,
                            'title': '',
                            'description': '',
                            'content': '',
                            'media_url': None
                        }
                        
                        # Extract title
                        title_elem = soup.select_one(config.selectors.get('title', 'h1'))
                        if title_elem:
                            article['title'] = title_elem.get_text(strip=True)
                        
                        # Extract description/content
                        desc_selector = config.selectors.get('description', 'p')
                        desc_elems = soup.select(desc_selector)
                        if desc_elems:
                            article['description'] = ' '.join([elem.get_text(strip=True) for elem in desc_elems[:3]])
                            article['content'] = ' '.join([elem.get_text(strip=True) for elem in desc_elems])
                        
                        # Extract first image
                        img_selector = config.media_extraction.get('image_selector', 'img')
                        img_elem = soup.select_one(img_selector)
                        if img_elem:
                            src = img_elem.get('src') or img_elem.get('data-src')
                            if src:
                                if not src.startswith('http'):
                                    src = config.base_url.rstrip('/') + '/' + src.lstrip('/')
                                article['media_url'] = src
                        
                        return article
                        
            except Exception as e:
                print(f"Error scraping URL {url}: {e}")
                return None


# Pre-configured website configurations
WEBSITE_CONFIGS = {
    'ynet': {
        'name': 'Ynet',
        'base_url': 'https://www.ynet.co.il',
        'language': 'he',
        'encoding': 'utf-8',
        'selectors': {
            'article_container': 'article, div.art',
            'title': 'h1, h2, .art_header_title',
            'url': 'a[href]',
            'description': 'p, .art_header_sub_title',
            'author': '.art_author_name',
            'date': '.art_date',
            'tags': '.art_tags a'
        },
        'media_extraction': {
            'image_selector': 'img[src], img[data-src]',
            'video_selector': 'video source, iframe[src*="youtube"], iframe[src*="video"]'
        },
        'patterns': {
            'category_patterns': {
                '/sport/': 'sports',
                '/economy/': 'finance',
                '/news/': 'general',
                '/pplus/': 'entertainment'
            }
        },
        'category_mapping': {
            'sports': ['ספורט', 'כדורגל', 'כדורסל', 'משחק'],
            'politics': ['פוליטי', 'ממשלה', 'כנסת', 'בחירות'],
            'finance': ['כלכלה', 'בורסה', 'שקל', 'דולר'],
            'security': ['צבא', 'ביטחון', 'צה"ל', 'מלחמה']
        }
    },
    
    'rotter': {
        'name': 'Rotter.net',
        'base_url': 'https://rotter.net/forum/scoops1',
        'language': 'he',
        'encoding': 'windows-1255',
        'selectors': {
            'article_container': 'tr.forum, div.forum_entry',
            'title': 'td.text a, .forum_title',
            'url': 'a[href*="scoops"]',
            'description': 'td.text',
            'author': '.forum_user',
            'date': '.forum_date'
        },
        'patterns': {
            'category_patterns': {
                'politic': 'politics',
                'sport': 'sports',
                'economy': 'finance'
            }
        },
        'category_mapping': {
            'breaking_news': ['דחוף', 'בהול', 'זה עתה', 'עכשיו'],
            'politics': ['פוליטי', 'ממשלה', 'ראש הממשלה', 'שר'],
            'security': ['צבא', 'ביטחון', 'פיגוע', 'מלחמה']
        }
    },
    
    'cnn': {
        'name': 'CNN',
        'base_url': 'https://www.cnn.com',
        'language': 'en',
        'selectors': {
            'article_container': 'article, div[class*="card"]',
            'title': 'h3, h2, span[class*="headline"]',
            'url': 'a[href]',
            'description': 'p, div[class*="description"]',
            'author': 'span[class*="byline"]',
            'date': 'time, span[class*="date"]'
        },
        'media_extraction': {
            'image_selector': 'img[src], picture img',
            'video_selector': 'video source, div[class*="video"] iframe'
        },
        'category_mapping': {
            'politics': ['president', 'congress', 'election', 'government'],
            'breaking_news': ['breaking', 'urgent', 'just in'],
            'sports': ['game', 'player', 'team', 'score'],
            'technology': ['tech', 'ai', 'startup', 'app']
        }
    },
    
    'bbc': {
        'name': 'BBC News',
        'base_url': 'https://www.bbc.com/news',
        'language': 'en',
        'selectors': {
            'article_container': 'article, div[data-testid="card"]',
            'title': 'h3, h2, a[class*="title"]',
            'url': 'a[href]',
            'description': 'p[class*="summary"]',
            'author': 'span[class*="author"]',
            'date': 'time'
        },
        'category_mapping': {
            'politics': ['parliament', 'government', 'minister', 'election'],
            'world': ['international', 'global', 'foreign'],
            'technology': ['tech', 'digital', 'internet', 'ai']
        }
    },
    
    'reddit': {
        'name': 'Reddit',
        'base_url': 'https://www.reddit.com/r/{subreddit}/top.json',
        'language': 'en',
        'headers': {
            'User-Agent': 'Mozilla/5.0 (compatible; NewsBot/1.0)'
        },
        'selectors': {
            # Reddit uses JSON API, so selectors work differently
            'json_path': 'data.children[].data'
        },
        'media_extraction': {
            'image_field': 'url',
            'video_field': 'media.reddit_video.fallback_url'
        }
    }
}


def create_website_config_wizard():
    """Interactive wizard to create configuration for a new website"""
    
    print("""
🧙 WEBSITE CONFIGURATION WIZARD
==============================
Let's add a new website to scrape!
""")
    
    config = {}
    
    # Basic info
    config['name'] = input("Website name (e.g., 'The Guardian'): ")
    config['base_url'] = input("Base URL (e.g., 'https://www.theguardian.com'): ")
    config['language'] = input("Language code (en/he/ar/etc.): ") or 'en'
    config['encoding'] = input("Encoding (utf-8/windows-1255/etc.) [utf-8]: ") or 'utf-8'
    
    # Selectors
    print("\n📍 CSS Selectors (press Enter for defaults):")
    config['selectors'] = {
        'article_container': input("Article container selector [article]: ") or 'article',
        'title': input("Title selector [h1, h2, h3]: ") or 'h1, h2, h3',
        'url': input("URL selector [a[href]]: ") or 'a[href]',
        'description': input("Description selector [p]: ") or 'p'
    }
    
    # Categories
    print("\n📂 Category keywords (comma-separated):")
    config['category_mapping'] = {}
    
    categories = ['politics', 'sports', 'technology', 'finance', 'entertainment']
    for cat in categories:
        keywords = input(f"{cat} keywords: ")
        if keywords:
            config['category_mapping'][cat] = [k.strip() for k in keywords.split(',')]
    
    # Save configuration
    site_id = config['name'].lower().replace(' ', '_')
    
    scraper = UniversalNewsScraper()
    scraper.add_website_config(site_id, config)
    
    print(f"""
✅ Configuration saved!

To scrape this website:
    scraper = UniversalNewsScraper()
    articles = await scraper.scrape_website('{site_id}')
""")
    
    return site_id, config


async def demo_universal_scraper():
    """Demo the universal scraper"""
    
    # Initialize scraper and add pre-configured sites
    scraper = UniversalNewsScraper()
    
    # Add pre-configured websites
    for site_id, config in WEBSITE_CONFIGS.items():
        scraper.add_website_config(site_id, config)
    
    print("""
🌐 UNIVERSAL NEWS SCRAPER DEMO
=============================
""")
    
    # Show available sites
    print("Available websites:")
    for site_id, config in scraper.configs.items():
        print(f"  • {site_id}: {config.name} ({config.language})")
    
    # Scrape multiple sites
    print("\n📰 Scraping news from multiple sources...")
    
    all_articles = []
    
    for site_id in ['ynet', 'cnn', 'bbc']:
        if site_id in scraper.configs:
            articles = await scraper.scrape_website(site_id, max_items=5)
            all_articles.extend(articles)
    
    # Display results
    print(f"\n📊 Total articles scraped: {len(all_articles)}")
    
    # Group by source
    by_source = {}
    for article in all_articles:
        source = article['source']
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(article)
    
    print("\n📰 Articles by source:")
    for source, articles in by_source.items():
        print(f"\n{source} ({len(articles)} articles):")
        for article in articles[:3]:
            print(f"  • {article['title'][:60]}...")
            if article.get('media_items'):
                print(f"    Media: {len(article['media_items'])} items")


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_universal_scraper())
    
    # Optionally create new configuration
    print("\n" + "="*50)
    create_new = input("\nWould you like to add a new website? (y/n): ")
    if create_new.lower() == 'y':
        create_website_config_wizard()