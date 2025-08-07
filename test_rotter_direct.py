#!/usr/bin/env python3
"""Direct test of Rotter.net scraping"""

import asyncio
from playwright.async_api import async_playwright

async def test_rotter():
    print("🔍 Testing Rotter.net scraping...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        print("📄 Loading https://rotter.net/forum/scoops1/")
        await page.goto("https://rotter.net/forum/scoops1/", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)
        
        # Test different selectors
        selectors_to_test = [
            ("tr[bgcolor]", "Original selector"),
            ("tr", "All table rows"),
            ("table table tr", "Nested table rows"),
            ("a[href*='forum.asp']", "Forum links"),
            ("td[align='right'] a", "Right-aligned links"),
            ("font font a b", "Bold links in fonts"),
        ]
        
        for selector, description in selectors_to_test:
            try:
                elements = await page.query_selector_all(selector)
                print(f"\n✅ {description} ('{selector}'): Found {len(elements)} elements")
                
                if len(elements) > 0 and len(elements) < 10:
                    # Show first few for debugging
                    for i, elem in enumerate(elements[:3]):
                        try:
                            text = await elem.text_content()
                            if text and text.strip():
                                print(f"   {i+1}. {text.strip()[:100]}")
                        except:
                            pass
            except Exception as e:
                print(f"❌ {description}: {e}")
        
        # Try to find actual news titles
        print("\n🔍 Looking for news titles...")
        
        # Get all links that might be news
        all_links = await page.query_selector_all("a")
        news_links = []
        
        for link in all_links:
            try:
                href = await link.get_attribute("href")
                text = await link.text_content()
                
                if href and text and "forum.asp" in href and len(text.strip()) > 20:
                    # Likely a news title
                    news_links.append({
                        "title": text.strip(),
                        "url": href
                    })
            except:
                pass
        
        print(f"\n📰 Found {len(news_links)} potential news items")
        for i, news in enumerate(news_links[:5]):
            print(f"{i+1}. {news['title'][:80]}...")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_rotter())