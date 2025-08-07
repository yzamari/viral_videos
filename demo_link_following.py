#!/usr/bin/env python3
"""
Demo of link-following feature with mock data
Shows how the scraper follows links in articles to get additional media
"""

import asyncio
from datetime import datetime

async def demo_link_following():
    """Demonstrate the link-following feature with example output"""
    
    print("🔗 Link-Following Media Extraction Demo")
    print("=" * 70)
    print("This demonstrates how the scraper follows links in articles")
    print("to extract media from linked pages\n")
    
    # Simulate scraping results
    mock_articles = [
        {
            "title": "Breaking: Major Tech Conference Announces New Products",
            "url": "https://example-news.com/tech-conference-2025",
            "description": "Several companies unveiled groundbreaking products at the annual tech conference",
            
            # Media from the main article page
            "article_images": [
                "https://example-news.com/images/conference-hall.jpg",
                "https://example-news.com/images/keynote-speaker.jpg"
            ],
            "article_videos": [],
            
            # NEW: Media extracted from links within the article
            "linked_media": [
                {
                    "type": "image",
                    "url": "https://techcompany.com/products/new-phone-hero.jpg",
                    "source": "https://techcompany.com/announcement",
                    "description": "Found by following link to tech company announcement"
                },
                {
                    "type": "image", 
                    "url": "https://gadgetblog.com/reviews/images/hands-on-photo.jpg",
                    "source": "https://gadgetblog.com/first-look",
                    "description": "Found by following link to gadget blog review"
                },
                {
                    "type": "video",
                    "url": "https://youtube.com/watch?v=demo123",
                    "source": "https://youtube.com/techChannel",
                    "description": "Found by following embedded YouTube link"
                }
            ]
        },
        {
            "title": "Environmental Report: Ocean Cleanup Progress",
            "url": "https://example-news.com/ocean-cleanup-2025",
            "description": "New technology shows promising results in removing plastic from oceans",
            
            # Media from the main article
            "article_images": [
                "https://example-news.com/images/ocean-cleanup-device.jpg"
            ],
            "article_videos": [
                "https://example-news.com/videos/cleanup-process.mp4"
            ],
            
            # Media from linked pages
            "linked_media": [
                {
                    "type": "image",
                    "url": "https://oceanproject.org/data/before-after-comparison.jpg",
                    "source": "https://oceanproject.org/results",
                    "description": "Found by following link to research organization"
                },
                {
                    "type": "image",
                    "url": "https://sciencejournal.com/figures/plastic-reduction-chart.png",
                    "source": "https://sciencejournal.com/study",
                    "description": "Found by following link to scientific paper"
                }
            ]
        },
        {
            "title": "Sports: Local Team Wins Championship",
            "url": "https://example-news.com/championship-victory",
            "description": "Historic victory after 20 years",
            
            # Media from main article
            "article_images": [
                "https://example-news.com/images/team-celebration.jpg",
                "https://example-news.com/images/trophy-ceremony.jpg"
            ],
            "article_videos": [],
            
            # Media from linked pages
            "linked_media": [
                {
                    "type": "image",
                    "url": "https://sportsteam.com/gallery/victory-parade-01.jpg",
                    "source": "https://sportsteam.com/gallery",
                    "description": "Found by following link to team's official gallery"
                },
                {
                    "type": "video",
                    "url": "https://sportsnetwork.com/highlights/final-goal.mp4",
                    "source": "https://sportsnetwork.com/highlights",
                    "description": "Found by following link to sports network highlights"
                },
                {
                    "type": "image",
                    "url": "https://fansite.com/photos/crowd-reaction.jpg",
                    "source": "https://fansite.com/match-report",
                    "description": "Found by following link to fan website"
                }
            ]
        }
    ]
    
    # Display results
    total_direct_media = 0
    total_linked_media = 0
    
    for i, article in enumerate(mock_articles, 1):
        print(f"{'='*70}")
        print(f"📰 Article #{i}")
        print(f"{'='*70}")
        
        print(f"📝 Title: {article['title']}")
        print(f"🔗 URL: {article['url']}")
        print(f"📄 {article['description']}\n")
        
        # Direct media from article
        images = article.get('article_images', [])
        videos = article.get('article_videos', [])
        direct_media = len(images) + len(videos)
        total_direct_media += direct_media
        
        print(f"📸 Media from article page:")
        print(f"   - {len(images)} images")
        print(f"   - {len(videos)} videos")
        print(f"   Total: {direct_media} items\n")
        
        # Media from linked pages
        linked = article.get('linked_media', [])
        total_linked_media += len(linked)
        
        print(f"🔗 Media from embedded links: {len(linked)} items")
        
        if linked:
            # Group by source
            sources = {}
            for media in linked:
                source = media['source']
                if source not in sources:
                    sources[source] = []
                sources[source].append(media)
            
            print(f"   Found media from {len(sources)} linked pages:")
            for source, items in sources.items():
                from urllib.parse import urlparse
                domain = urlparse(source).netloc
                types = [item['type'] for item in items]
                print(f"     • {domain}: {', '.join(types)}")
            
            print(f"\n   Detailed findings:")
            for j, media in enumerate(linked, 1):
                print(f"     {j}. {media['type'].upper()}: {media['url'][:50]}...")
                print(f"        Source: {media['source'][:50]}...")
                print(f"        Note: {media['description']}")
        
        print()
    
    # Summary
    print("=" * 70)
    print("📊 SUMMARY - Link Following Benefits")
    print("=" * 70)
    print(f"📰 Articles processed: {len(mock_articles)}")
    print(f"📸 Direct media (from articles): {total_direct_media} items")
    print(f"🔗 Linked media (from followed links): {total_linked_media} items")
    print(f"📈 Total media collected: {total_direct_media + total_linked_media} items")
    
    if total_linked_media > 0:
        increase = (total_linked_media / total_direct_media) * 100
        print(f"\n✨ Link following increased media by {increase:.0f}%!")
        print(f"   Without link following: {total_direct_media} items")
        print(f"   With link following: {total_direct_media + total_linked_media} items")
    
    print("\n" + "=" * 70)
    print("💡 KEY BENEFITS of Link Following:")
    print("=" * 70)
    print("1. 📸 Richer Media: Get original high-quality images from source sites")
    print("2. 🎥 Video Discovery: Find videos embedded or linked in articles")
    print("3. 📊 Data Visualization: Extract charts, graphs from research links")
    print("4. 🖼️ Gallery Access: Get full photo sets from linked galleries")
    print("5. 📰 Source Material: Access original content referenced in articles")
    
    print("\n" + "=" * 70)
    print("⚙️ CONFIGURATION OPTIONS:")
    print("=" * 70)
    print("""
In your scraper config JSON:
{
  "follow_embedded_links": true,    // Enable/disable feature
  "max_link_depth": 1,              // How deep to follow (1 = direct links only)
  "max_links_to_follow": 5,         // Max links per article (prevent overload)
  "link_follow_config": {
    "exclude_domains": ["facebook.com", "twitter.com"],  // Skip social media
    "priority_domains": ["youtube.com", "vimeo.com"]      // Prioritize video sites
  }
}
""")

def main():
    """Run the demo"""
    print("🚀 Link-Following Media Extraction Feature Demo\n")
    asyncio.run(demo_link_following())
    
    print("\n✅ Demo completed!")
    print("\nThis feature is now active in the universal scraper.")
    print("When configured, it will automatically follow links in articles")
    print("to extract additional media from linked pages.")

if __name__ == "__main__":
    main()