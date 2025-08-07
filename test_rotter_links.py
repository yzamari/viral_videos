#!/usr/bin/env python3
"""
Test Rotter.net scraping with link-following feature
This will scrape Rotter scoops and follow embedded links to get media from linked pages
"""

import asyncio
import json
from datetime import datetime
from src.news_aggregator.scrapers.universal_scraper import UniversalNewsScraper

async def scrape_rotter_with_links():
    """Scrape Rotter.net scoops and follow links for additional media"""
    
    print("🔍 Rotter.net Scoops Scraper with Link Following")
    print("=" * 70)
    print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔗 Link following: ENABLED (will fetch media from linked pages)")
    print("=" * 70)
    
    # Initialize scraper (it will load the updated rotter.json config)
    scraper = UniversalNewsScraper()
    
    try:
        # Scrape Rotter.net with link following
        print("\n📰 Fetching latest scoops from Rotter.net...")
        articles = await scraper.scrape_website(
            site_id="rotter",
            max_items=5,  # Get 5 scoops
            fetch_article_media=True  # Enable media fetching from article pages
        )
        
        if not articles:
            print("❌ No articles found")
            return
        
        print(f"\n✅ Found {len(articles)} scoops\n")
        
        # Display results
        total_images = 0
        total_videos = 0
        total_linked_media = 0
        
        for i, article in enumerate(articles, 1):
            print(f"{'='*70}")
            print(f"📌 Scoop #{i}")
            print(f"{'='*70}")
            
            # Title
            title = article.get('title', 'No title')
            print(f"📝 Title: {title}")
            
            # URL
            url = article.get('url', 'No URL')
            print(f"🔗 URL: {url}")
            
            # Description
            desc = article.get('description', '')
            if desc:
                print(f"📄 Description: {desc[:200]}...")
            
            # Media from main page
            preview_images = article.get('images', [])
            preview_videos = article.get('videos', [])
            
            print(f"\n📸 Media from preview:")
            print(f"   - Images: {len(preview_images)}")
            print(f"   - Videos: {len(preview_videos)}")
            
            # Media from article page
            article_images = article.get('article_images', [])
            article_videos = article.get('article_videos', [])
            
            print(f"\n📸 Media from article page:")
            print(f"   - Images: {len(article_images)}")
            if article_images:
                for j, img in enumerate(article_images[:3], 1):
                    print(f"     {j}. {img[:80]}...")
            
            print(f"   - Videos: {len(article_videos)}")
            if article_videos:
                for j, vid in enumerate(article_videos[:3], 1):
                    print(f"     {j}. {vid[:80]}...")
            
            # Check for media from embedded links
            media_items = article.get('media_items', [])
            if media_items:
                linked_media = [m for m in media_items if m.get('source')]
                if linked_media:
                    print(f"\n🔗 Media from embedded links: {len(linked_media)} items")
                    unique_sources = set(m.get('source', '') for m in linked_media)
                    print(f"   Sources: {len(unique_sources)} different websites")
                    for source in list(unique_sources)[:3]:
                        if source:
                            from urllib.parse import urlparse
                            domain = urlparse(source).netloc
                            print(f"     - {domain}")
                    total_linked_media += len(linked_media)
            
            # Category
            category = article.get('category', 'general')
            print(f"\n🏷️ Category: {category}")
            
            # Update totals
            total_images += len(article_images) + len(preview_images)
            total_videos += len(article_videos) + len(preview_videos)
            
            print()
        
        # Summary
        print("=" * 70)
        print("📊 SUMMARY")
        print("=" * 70)
        print(f"📰 Total scoops scraped: {len(articles)}")
        print(f"📸 Total images found: {total_images}")
        print(f"🎥 Total videos found: {total_videos}")
        print(f"🔗 Media from embedded links: {total_linked_media}")
        print(f"💾 Total media items: {total_images + total_videos + total_linked_media}")
        
        # Save results
        output_file = f"rotter_scoops_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Results saved to: {output_file}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

async def compare_with_and_without_links():
    """Compare results with and without link following"""
    
    print("\n\n" + "=" * 70)
    print("📊 COMPARISON: With vs Without Link Following")
    print("=" * 70)
    
    scraper = UniversalNewsScraper()
    
    # Test WITHOUT link following
    print("\n1️⃣ WITHOUT Link Following:")
    config_no_links = scraper.configs['rotter'].__dict__.copy()
    config_no_links['follow_embedded_links'] = False
    scraper.configs['rotter_no_links'] = type('obj', (object,), config_no_links)()
    
    articles_no_links = await scraper.scrape_website("rotter_no_links", max_items=3)
    
    total_media_no_links = 0
    for article in articles_no_links:
        total_media_no_links += len(article.get('images', []))
        total_media_no_links += len(article.get('videos', []))
        total_media_no_links += len(article.get('article_images', []))
        total_media_no_links += len(article.get('article_videos', []))
    
    print(f"   Articles: {len(articles_no_links)}")
    print(f"   Total media: {total_media_no_links}")
    
    # Test WITH link following
    print("\n2️⃣ WITH Link Following:")
    articles_with_links = await scraper.scrape_website("rotter", max_items=3, fetch_article_media=True)
    
    total_media_with_links = 0
    linked_media_count = 0
    for article in articles_with_links:
        total_media_with_links += len(article.get('images', []))
        total_media_with_links += len(article.get('videos', []))
        total_media_with_links += len(article.get('article_images', []))
        total_media_with_links += len(article.get('article_videos', []))
        
        # Count linked media
        media_items = article.get('media_items', [])
        linked = [m for m in media_items if m.get('source')]
        linked_media_count += len(linked)
    
    print(f"   Articles: {len(articles_with_links)}")
    print(f"   Total media: {total_media_with_links}")
    print(f"   Media from links: {linked_media_count}")
    
    print("\n📈 IMPROVEMENT:")
    if total_media_with_links > total_media_no_links:
        improvement = ((total_media_with_links - total_media_no_links) / max(total_media_no_links, 1)) * 100
        print(f"   +{improvement:.1f}% more media with link following")
    else:
        print("   No additional media found from links")

def main():
    """Run the Rotter.net scraper with link following"""
    
    print("🚀 Starting Rotter.net Scraper with Link Following")
    print("This will follow links in scoops to find additional media\n")
    
    # Run main scraping
    asyncio.run(scrape_rotter_with_links())
    
    # Run comparison
    asyncio.run(compare_with_and_without_links())
    
    print("\n✅ Scraping completed!")
    print("The link-following feature extracted media from pages linked within the scoops.")

if __name__ == "__main__":
    main()