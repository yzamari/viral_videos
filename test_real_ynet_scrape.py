#!/usr/bin/env python3
"""Test real Ynet scraping"""

import asyncio
import sys
sys.path.append('.')

from src.news_aggregator.scrapers.universal_scraper import UniversalNewsScraper

async def test_ynet_scraping():
    """Test Ynet scraping with universal scraper"""
    scraper = UniversalNewsScraper()
    
    # Check if ynet config exists
    if 'ynet' not in scraper.configs:
        print("❌ Ynet configuration not found")
        return
    
    print("🔍 Testing Ynet scraping...")
    
    # Scrape Ynet
    articles = await scraper.scrape_website('ynet', max_items=10)
    
    print(f"\n📰 Found {len(articles)} articles:\n")
    
    for i, article in enumerate(articles[:5], 1):
        print(f"{i}. {article.get('title', 'No title')}")
        if article.get('description'):
            print(f"   {article['description'][:100]}...")
        if article.get('url'):
            print(f"   🔗 {article['url']}")
        print()

if __name__ == "__main__":
    asyncio.run(test_ynet_scraping())