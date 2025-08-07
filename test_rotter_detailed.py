#!/usr/bin/env python3
"""Detailed test of Rotter.net structure"""

import asyncio
from playwright.async_api import async_playwright

async def test_rotter_detailed():
    print("🔍 Detailed Rotter.net analysis...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        print("📄 Loading https://rotter.net/forum/scoops1/")
        await page.goto("https://rotter.net/forum/scoops1/", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)
        
        # Get all tr[bgcolor] elements
        rows = await page.query_selector_all("tr[bgcolor]")
        print(f"\n✅ Found {len(rows)} tr[bgcolor] elements")
        
        news_items = []
        
        for i, row in enumerate(rows[:10]):  # Check first 10
            try:
                # Get all text in the row
                row_text = await row.text_content()
                if not row_text or len(row_text.strip()) < 10:
                    continue
                
                # Look for links within the row
                links = await row.query_selector_all("a")
                
                for link in links:
                    href = await link.get_attribute("href")
                    text = await link.text_content()
                    
                    # Check if it's a forum post link
                    if href and "om=" in href and text and len(text.strip()) > 10:
                        # Check if link is in bold (likely a title)
                        parent_html = await link.evaluate("el => el.parentElement.outerHTML")
                        is_bold = "<b>" in parent_html or "font-weight" in parent_html
                        
                        if is_bold or len(text.strip()) > 30:
                            news_items.append({
                                "title": text.strip(),
                                "url": href,
                                "row_index": i
                            })
                            print(f"\n📰 Row {i+1} - Found news item:")
                            print(f"   Title: {text.strip()[:100]}")
                            print(f"   URL: {href[:50]}...")
                            break
                
            except Exception as e:
                print(f"❌ Error in row {i+1}: {e}")
        
        print(f"\n📊 Total news items found: {len(news_items)}")
        
        if len(news_items) == 0:
            # Try alternative approach - look for all bold links
            print("\n🔍 Alternative approach - finding all bold links...")
            bold_links = await page.query_selector_all("b a, a b")
            
            for link_elem in bold_links[:10]:
                try:
                    # Get the actual link element
                    if await link_elem.evaluate("el => el.tagName") == "B":
                        link = await link_elem.query_selector("a")
                        if not link:
                            link = await link_elem.evaluate("el => el.parentElement")
                    else:
                        link = link_elem
                    
                    if link:
                        href = await link.get_attribute("href") if hasattr(link, 'get_attribute') else await link_elem.evaluate("el => el.getAttribute('href') || el.parentElement.getAttribute('href')")
                        text = await link_elem.text_content()
                        
                        if href and "om=" in str(href) and text and len(text.strip()) > 20:
                            news_items.append({
                                "title": text.strip(),
                                "url": href
                            })
                            print(f"   Found: {text.strip()[:80]}")
                except Exception as e:
                    pass
        
        print(f"\n📊 Final count: {len(news_items)} news items")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_rotter_detailed())