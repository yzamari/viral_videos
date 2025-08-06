#!/usr/bin/env python3
"""Direct test of Ynet scraping"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import certifi
import ssl

async def test_direct_ynet():
    """Directly test Ynet HTML structure"""
    
    url = "https://www.ynet.co.il"
    
    # Create SSL context
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'he,en;q=0.9',
    }
    
    print(f"🔍 Fetching {url}...")
    
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        async with session.get(url, headers=headers) as response:
            print(f"📊 Status: {response.status}")
            
            if response.status == 200:
                html = await response.text()
                print(f"📄 HTML length: {len(html)} chars")
                
                soup = BeautifulSoup(html, 'html.parser')
                
                # Try different selectors
                selectors_to_try = [
                    ("article.slotView", "slotView articles"),
                    ("div.article-short", "article-short divs"),
                    ("a[href*='/articles/']", "article links"),
                    ("h2", "h2 headers"),
                    ("h3", "h3 headers"),
                    (".slotTitle", "slotTitle elements"),
                    ("article", "article elements"),
                    ("div[class*='article']", "divs with article class"),
                    ("div[class*='slot']", "divs with slot class"),
                ]
                
                print("\n🔍 Testing selectors:")
                for selector, desc in selectors_to_try:
                    elements = soup.select(selector)
                    print(f"  • {desc}: {len(elements)} found")
                    
                    if elements and len(elements) > 0:
                        print(f"    First item: {elements[0].get_text(strip=True)[:100]}...")
                
                # Print some actual content
                print("\n📰 Sample content:")
                # Find any links that look like articles
                article_links = soup.find_all('a', href=True)
                article_count = 0
                for link in article_links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    if '/articles/' in href and len(text) > 20:
                        print(f"  • {text[:100]}")
                        print(f"    URL: {href}")
                        article_count += 1
                        if article_count >= 5:
                            break
                            
            else:
                print(f"❌ Failed with status: {response.status}")
                print(f"Headers: {response.headers}")

if __name__ == "__main__":
    asyncio.run(test_direct_ynet())