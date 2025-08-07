#!/usr/bin/env python3
"""
Test script for link-following media extraction feature
Tests the ability to follow links within scraped content and extract media from those pages
"""

import asyncio
import json
from src.news_aggregator.scrapers.universal_scraper import UniversalNewsScraper

async def test_link_following():
    """Test the link-following feature with a sample configuration"""
    
    # Create a test configuration that enables link following
    test_config = {
        "name": "Test News Site with Link Following",
        "base_url": "https://www.cnn.com",
        "selectors": {
            "article_container": "article",
            "title": "h1, h2, h3",
            "url": "a[href]",
            "description": "p",
            "image": "img[src]"
        },
        "media_extraction": {
            "image_selector": "img[src]",
            "video_selector": "video source[src]"
        },
        "follow_embedded_links": True,  # Enable link following
        "max_link_depth": 1,  # Follow links up to 1 level deep
        "max_links_to_follow": 3,  # Follow up to 3 links per article
        "language": "en",
        "encoding": "utf-8",
        "headers": {
            "User-Agent": "Mozilla/5.0 (compatible; NewsBot/1.0)"
        }
    }
    
    # Initialize scraper
    scraper = UniversalNewsScraper()
    
    # Add test configuration
    scraper.add_website_config("test_link_follow", test_config)
    
    print("🔗 Testing Link-Following Media Extraction Feature")
    print("=" * 60)
    
    try:
        # Scrape with link following enabled
        print("\n📰 Scraping articles with link following enabled...")
        articles = await scraper.scrape_website("test_link_follow", max_items=2, fetch_article_media=True)
        
        # Display results
        for i, article in enumerate(articles, 1):
            print(f"\n📄 Article {i}:")
            print(f"   Title: {article.get('title', 'N/A')[:80]}...")
            print(f"   URL: {article.get('url', 'N/A')}")
            
            # Show media from main article
            images = article.get('article_images', [])
            videos = article.get('article_videos', [])
            
            print(f"\n   📸 Media found:")
            print(f"      - Images: {len(images)} total")
            if images:
                print(f"        First image: {images[0][:80]}...")
            
            print(f"      - Videos: {len(videos)} total")
            if videos:
                print(f"        First video: {videos[0][:80]}...")
            
            # Check for media from embedded links
            media_items = article.get('media_items', [])
            link_media = [m for m in media_items if m.get('source')]
            if link_media:
                print(f"\n   🔗 Media from embedded links: {len(link_media)} items")
                for media in link_media[:3]:
                    print(f"      - {media['type']}: from {media.get('source', 'unknown')[:50]}...")
        
        print("\n" + "=" * 60)
        print("✅ Link-following test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

async def test_with_disabled_link_following():
    """Test with link following disabled for comparison"""
    
    # Configuration with link following disabled
    config_disabled = {
        "name": "Test without Link Following",
        "base_url": "https://www.cnn.com",
        "selectors": {
            "article_container": "article",
            "title": "h1, h2, h3",
            "url": "a[href]",
            "description": "p"
        },
        "follow_embedded_links": False,  # Disable link following
        "language": "en"
    }
    
    scraper = UniversalNewsScraper()
    scraper.add_website_config("test_no_links", config_disabled)
    
    print("\n🚫 Testing WITHOUT Link Following (for comparison)")
    print("=" * 60)
    
    articles = await scraper.scrape_website("test_no_links", max_items=2)
    
    for i, article in enumerate(articles, 1):
        print(f"\n📄 Article {i}:")
        print(f"   Title: {article.get('title', 'N/A')[:80]}...")
        images = article.get('article_images', [])
        print(f"   Images found: {len(images)}")

def main():
    """Run all tests"""
    print("🔗 Link-Following Media Extraction Test Suite")
    print("=" * 60)
    
    # Run tests
    asyncio.run(test_link_following())
    asyncio.run(test_with_disabled_link_following())
    
    print("\n📊 Summary:")
    print("The link-following feature allows the scraper to:")
    print("1. Detect links within article content")
    print("2. Follow those links to external/internal pages")
    print("3. Extract media (images/videos) from linked pages")
    print("4. Add that media to the article's media collection")
    print("5. Respect depth limits to prevent infinite recursion")
    print("6. Be configured per website (enable/disable, max links, depth)")

if __name__ == "__main__":
    main()