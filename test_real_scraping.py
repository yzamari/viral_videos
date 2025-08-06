#!/usr/bin/env python3
"""Test real news scraping - NO MOCK DATA"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json
from datetime import datetime

async def scrape_ynet_real():
    """Actually scrape Ynet for REAL news"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'he,en;q=0.9',
    }
    
    # Disable SSL verification for testing (Ynet has cert issues)
    import ssl
    import certifi
    
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            # Ynet main page
            async with session.get('https://www.ynet.co.il', headers=headers, allow_redirects=True) as resp:
                if resp.status == 200:
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
                            image = None
                            img_elem = elem.select_one('img')
                            if img_elem:
                                image = img_elem.get('src') or img_elem.get('data-src')
                                if image and not image.startswith('http'):
                                    image = f"https://www.ynet.co.il{image}"
                            
                            # Extract URL
                            url = None
                            link_elem = elem.select_one('a[href]')
                            if link_elem:
                                url = link_elem.get('href')
                                if url and not url.startswith('http'):
                                    url = f"https://www.ynet.co.il{url}"
                            
                            if title:
                                articles.append({
                                    'title': title,
                                    'content': content or '',
                                    'image': image,
                                    'url': url,
                                    'source': 'Ynet',
                                    'scraped_at': datetime.now().isoformat()
                                })
                    
                    # Deduplicate by title
                    seen_titles = set()
                    unique_articles = []
                    for article in articles:
                        if article['title'] not in seen_titles:
                            seen_titles.add(article['title'])
                            unique_articles.append(article)
                    
                    return unique_articles
                    
        except Exception as e:
            print(f"Error scraping Ynet: {e}")
            return []
    
    return []

async def main():
    print("🔍 Scraping REAL news from Ynet...")
    articles = await scrape_ynet_real()
    
    print(f"\n✅ Found {len(articles)} REAL articles")
    
    for i, article in enumerate(articles[:5], 1):  # Show first 5
        print(f"\n📰 Article {i}:")
        print(f"  Title: {article['title'][:80]}...")
        if article['content']:
            print(f"  Content: {article['content'][:100]}...")
        if article['image']:
            print(f"  Image: {article['image'][:80]}...")
        if article['url']:
            print(f"  URL: {article['url'][:80]}...")
    
    # Save to file
    with open('real_scraped_news.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Saved {len(articles)} articles to real_scraped_news.json")

if __name__ == "__main__":
    asyncio.run(main())