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


class ScraperConfig:
    """Configuration for a specific website"""
    
    def __init__(self, config_dict: Dict):
        self.name = config_dict['name']
        self.base_url = config_dict['base_url']
        self.selectors = config_dict['selectors']
        self.patterns = config_dict.get('patterns', {})
        self.headers = config_dict.get('headers', {})
        self.encoding = config_dict.get('encoding', 'utf-8')
        self.language = config_dict.get('language', 'en')
        self.category_mapping = config_dict.get('category_mapping', {})
        self.media_extraction = config_dict.get('media_extraction', {})


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
    
    async def scrape_website(self, site_id: str, max_items: int = 20) -> List[Dict]:
        """Scrape any configured website"""
        
        if site_id not in self.configs:
            raise ValueError(f"No configuration found for site: {site_id}")
        
        config = self.configs[site_id]
        print(f"🔍 Scraping {config.name}...")
        
        articles = []
        
        async with aiohttp.ClientSession() as session:
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
                        
                        print(f"  ✅ Found {len(articles)} articles from {config.name}")
                    else:
                        print(f"  ❌ Failed to fetch {config.name}: Status {response.status}")
                        
            except Exception as e:
                print(f"  ❌ Error scraping {config.name}: {e}")
        
        return articles
    
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
            
            # Extract description
            desc_selector = config.selectors.get('description', 'p')
            if desc_selector:
                desc_elem = element.select_one(desc_selector)
                if desc_elem:
                    article['description'] = desc_elem.get_text(strip=True)
            
            # Extract media
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