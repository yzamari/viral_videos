"""Test script for news aggregator with Telegram support"""

import asyncio
from src.news_aggregator.scrapers.universal_scraper import UniversalNewsScraper, TelegramChannelScraper
from src.news_aggregator.models.content_models import NewsSource, SourceType

async def test_scrapers():
    # Test web scraper
    web_scraper = UniversalNewsScraper()
    
    # Create test sources
    ynet_source = NewsSource(
        id="ynet",
        name="Ynet",
        url="https://www.ynet.co.il",
        source_type=SourceType.WEB
    )
    
    # Scrape Ynet
    print("Scraping Ynet...")
    ynet_articles = await web_scraper.scrape(ynet_source, hours_back=24)
    print(f"Found {len(ynet_articles)} articles from Ynet")
    
    for article in ynet_articles[:2]:
        print(f"- {article.title}")
        print(f"  Media: {len(article.media_assets)} assets")
    
    # Test Telegram scraper
    print("\nScraping Telegram channels...")
    telegram_scraper = TelegramChannelScraper()
    
    # Scrape channels
    channels = ["@ynet_news", "@channel13news"]
    for channel in channels:
        messages = await telegram_scraper.scrape_channel(channel, hours_back=24)
        print(f"\nChannel {channel}: {len(messages)} messages")
        for msg in messages:
            print(f"- {msg.title}")
            print(f"  Media: {len(msg.media_assets)} assets")

if __name__ == "__main__":
    asyncio.run(test_scrapers())