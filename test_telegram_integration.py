#!/usr/bin/env python3
"""Test script for Telegram API integration"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.news_aggregator.enhanced_aggregator import EnhancedNewsAggregator
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

async def test_telegram_scraping():
    """Test Telegram channel scraping functionality"""
    
    print("🧪 Testing Telegram API Integration")
    print("=" * 50)
    
    # Check if credentials are configured
    has_credentials = all([
        os.getenv('TELEGRAM_API_ID'),
        os.getenv('TELEGRAM_API_HASH'),
        os.getenv('TELEGRAM_PHONE')
    ])
    
    if has_credentials:
        print("✅ Telegram API credentials found in environment")
    else:
        print("⚠️  No Telegram API credentials found")
        print("📝 Using test Telegram scraper with sample data")
    
    # Create aggregator
    aggregator = EnhancedNewsAggregator()
    
    try:
        # Test Telegram channel scraping
        print("\n📱 Testing Telegram channel scraping...")
        
        # Sources for testing
        sources = ['https://www.ynet.co.il']
        telegram_channels = ['@ynet_news', '@channel13news']
        
        # Run aggregation with Telegram channels
        result = await aggregator.aggregate_news(
            sources=sources,
            telegram_channels=telegram_channels,
            languages=['he'],
            style="modern news",
            tone="professional",
            platform="tiktok",
            duration_seconds=60,
            max_stories=5,
            enable_ai_discussion=False,  # Skip AI for faster testing
            hours_back=24
        )
        
        print("\n✅ Test completed successfully!")
        print(f"📹 Output videos: {result}")
        
        # Check session report
        session_dir = aggregator.session_manager.session_data.get('session_dir', 'outputs')
        report_path = Path(session_dir) / 'news_aggregation_report.json'
        
        if report_path.exists():
            import json
            with open(report_path, 'r', encoding='utf-8') as f:
                report = json.load(f)
            
            print(f"\n📊 Aggregated {report['total_stories']} stories:")
            for story in report['stories']:
                print(f"  - {story['title']}")
                print(f"    Sources: {', '.join(story['sources'])}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_telegram_setup():
    """Test Telegram credential setup"""
    
    print("\n🔧 Testing Telegram Setup")
    print("=" * 50)
    
    env_path = Path(".env")
    if env_path.exists():
        content = env_path.read_text()
        has_telegram = "TELEGRAM_API_ID=" in content
        
        if has_telegram:
            print("✅ Telegram credentials found in .env file")
        else:
            print("❌ No Telegram credentials in .env file")
            print("Run: python setup_telegram.py")
    else:
        print("❌ No .env file found")
        print("Run: python setup_telegram.py")

if __name__ == "__main__":
    print("🚀 ViralAI Telegram Integration Test")
    print("=" * 50)
    
    # Test setup
    asyncio.run(test_telegram_setup())
    
    # Test scraping
    asyncio.run(test_telegram_scraping())