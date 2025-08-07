#!/usr/bin/env python3
"""Test Telegram scraper functionality"""

import asyncio
import os
from pathlib import Path

async def test_telegram_scraper():
    """Test the Telegram scraper"""
    
    print("🧪 Testing Telegram Scraper")
    print("="*50)
    
    # Check if credentials exist
    has_id = os.getenv('TELEGRAM_API_ID')
    has_hash = os.getenv('TELEGRAM_API_HASH')
    
    if not has_id or not has_hash:
        print("❌ No Telegram credentials found!")
        print("\n📝 To set up Telegram scraping:")
        print("1. Run: python3 setup_telegram.py")
        print("2. Or manually add to .env file:")
        print("   TELEGRAM_API_ID=your_api_id")
        print("   TELEGRAM_API_HASH=your_api_hash")
        print("\n📱 Get credentials from: https://my.telegram.org")
        return
    
    print("✅ Telegram credentials found")
    print(f"   API ID: {has_id}")
    print(f"   API Hash: {has_hash[:10]}...")
    
    try:
        from src.news_aggregator.scrapers.telegram_api_scraper import TelegramAPIScraper
        
        print("\n📱 Initializing Telegram scraper...")
        scraper = TelegramAPIScraper()
        
        # Test with a public channel
        test_channel = "@test"  # Telegram's official test channel
        
        print(f"\n🔍 Testing with channel: {test_channel}")
        print("   (This is Telegram's official test channel)")
        
        async with scraper:
            # Try to get channel info
            try:
                items = await scraper.scrape_channel(test_channel, hours_back=24, limit=5)
                
                if items:
                    print(f"\n✅ Successfully scraped {len(items)} items!")
                    for i, item in enumerate(items[:3], 1):
                        print(f"\n{i}. {item.title[:80]}")
                        if item.content:
                            print(f"   {item.content[:100]}...")
                        if item.media_assets:
                            print(f"   Media: {len(item.media_assets)} items")
                else:
                    print("\n⚠️ No items found (channel might be empty)")
                    
            except Exception as e:
                if "Cannot find any entity" in str(e):
                    print("\n⚠️ Test channel not found. Trying a news channel...")
                    
                    # Try with a real news channel
                    news_channel = "@BBCBreaking"  # BBC Breaking News
                    print(f"\n🔍 Testing with: {news_channel}")
                    
                    items = await scraper.scrape_channel(news_channel, hours_back=48, limit=5)
                    
                    if items:
                        print(f"\n✅ Successfully scraped {len(items)} items from {news_channel}!")
                        for i, item in enumerate(items[:3], 1):
                            print(f"\n{i}. {item.title[:80]}")
                            if item.media_assets:
                                print(f"   Media: {len(item.media_assets)} items")
                    else:
                        print("\n⚠️ No recent items found")
                else:
                    raise e
        
        print("\n✅ Telegram scraper is working correctly!")
        print("\n📺 You can now use it with the news aggregator:")
        print("   python3 main.py news aggregate-enhanced \\")
        print("     --telegram-channels @channel_name")
        
    except ImportError:
        print("\n❌ Telethon not installed!")
        print("Run: pip3 install telethon")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        
        if "API_ID_INVALID" in str(e):
            print("\n⚠️ Invalid API credentials!")
            print("Please run: python3 setup_telegram.py")
        elif "PHONE_NUMBER_INVALID" in str(e):
            print("\n⚠️ Phone number authentication required!")
            print("The scraper will prompt for authentication on first use.")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run test
    asyncio.run(test_telegram_scraper())