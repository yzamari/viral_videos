#!/usr/bin/env python3
"""Simple Ynet news aggregator with real scraping"""

import asyncio
import sys
sys.path.append('.')

from src.news_aggregator.scrapers.universal_scraper import UniversalNewsScraper
from src.workflows.generate_viral_video import async_main as generate_video

async def create_ynet_news_video():
    """Create news video from real Ynet articles"""
    
    print("🎬 Creating news video from real Ynet articles...")
    
    # Initialize scraper
    scraper = UniversalNewsScraper()
    
    # Scrape Ynet
    print("📰 Scraping Ynet...")
    articles = await scraper.scrape_website('ynet', max_items=5)
    
    if not articles:
        print("❌ No articles found!")
        return
    
    print(f"✅ Found {len(articles)} articles")
    
    # Create mission from real articles
    headlines = []
    for i, article in enumerate(articles[:3], 1):
        title = article.get('title', 'No title')
        headlines.append(f"{i}. {title}")
        print(f"  • {title}")
    
    mission = f"""Create a Hebrew news broadcast video featuring real news from Ynet.
    
    Headlines:
    {chr(10).join(headlines)}
    
    Style: Professional Israeli news broadcast
    Language: Hebrew
    Include commentary and analysis in Hebrew.
    """
    
    print("\n🎥 Generating video...")
    
    # Generate video
    video_path = await generate_video(
        mission=mission,
        category="News",
        platform="youtube",
        duration=60,
        languages=["he"],
        style="professional",
        tone="informative",
        mode="simple",
        theme="israeli_news"
    )
    
    print(f"\n✅ Video created: {video_path}")
    return video_path

if __name__ == "__main__":
    asyncio.run(create_ynet_news_video())