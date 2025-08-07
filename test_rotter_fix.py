#!/usr/bin/env python3
"""Test and fix Rotter scraping with improved selectors"""

import asyncio
from playwright.async_api import async_playwright

async def test_rotter_scraping():
    print("🔍 Testing Rotter.net scraping with improved approach...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        print("📄 Loading https://rotter.net/forum/scoops1/")
        await page.goto("https://rotter.net/forum/scoops1/", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)
        
        # Find all table rows with bgcolor
        rows = await page.query_selector_all("tr[bgcolor]")
        print(f"✅ Found {len(rows)} tr[bgcolor] elements")
        
        news_items = []
        
        for i, row in enumerate(rows[:20]):  # Check first 20 rows
            try:
                # Get all links in the row
                links = await row.query_selector_all("a")
                
                for link in links:
                    href = await link.get_attribute("href")
                    text = await link.text_content()
                    
                    # Check if it's a forum link with substantial text
                    if href and "om=" in href and text and len(text.strip()) > 20:
                        # Check if link is bold (news title)
                        parent = await link.evaluate_handle("el => el.parentElement")
                        parent_tag = await parent.evaluate("el => el.tagName")
                        
                        if parent_tag == "B" or len(text.strip()) > 30:
                            # Extract the whole row text for description
                            row_text = await row.text_content()
                            
                            news_items.append({
                                "title": text.strip(),
                                "url": href,
                                "description": row_text.strip() if row_text else text.strip()
                            })
                            print(f"\n📰 Item {len(news_items)}:")
                            print(f"   Title: {text.strip()[:80]}")
                            print(f"   URL: {href[:50]}...")
                            break
                
            except Exception as e:
                continue
        
        print(f"\n📊 Total news items found: {len(news_items)}")
        
        # Now test with the Playwright scraper approach
        print("\n🎭 Testing with Playwright scraper selectors...")
        
        # Test the actual selectors being used
        test_selectors = [
            ("tr[bgcolor] a b", "Bold links in rows"),
            ("tr[bgcolor] b a", "Links in bold"),
            ("a b", "All bold links"),
            ("b a", "All links in bold")
        ]
        
        for selector, desc in test_selectors:
            elements = await page.query_selector_all(selector)
            print(f"\n✅ {desc} ('{selector}'): {len(elements)} elements")
            
            if elements and len(elements) > 0:
                for j, elem in enumerate(elements[:3]):
                    text = await elem.text_content()
                    if text and len(text.strip()) > 20:
                        print(f"   {j+1}. {text.strip()[:80]}")
        
        await browser.close()
        
        return news_items

async def test_with_universal_scraper():
    """Test with the actual universal scraper"""
    from src.news_aggregator.scrapers.universal_scraper import UniversalNewsScraper
    
    print("\n🌐 Testing with Universal Scraper...")
    
    scraper = UniversalNewsScraper()
    
    # Update Rotter config with better selectors
    better_config = {
        "name": "Rotter.net",
        "base_url": "https://rotter.net/forum/scoops1/",
        "language": "he",
        "selectors": {
            "article_container": "tr[bgcolor]",
            "title": "a b, b a",  # Look for bold links
            "url": "a[href*='om=']",  # Links with om= parameter
            "description": "",  # Use whole container text
            "image": "img",
            "video": "video"
        },
        "headers": {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "he-IL,he;q=0.9,en;q=0.8"
        }
    }
    
    scraper.add_website_config('rotter', better_config)
    
    articles = await scraper.scrape_website('rotter', max_items=10)
    
    print(f"\n📊 Universal scraper found {len(articles)} articles")
    for i, article in enumerate(articles[:5]):
        print(f"\n{i+1}. {article.get('title', 'No title')[:80]}")
        if article.get('description'):
            print(f"   {article.get('description')[:100]}...")

if __name__ == "__main__":
    # First test direct scraping
    news = asyncio.run(test_rotter_scraping())
    
    # Then test with universal scraper
    asyncio.run(test_with_universal_scraper())