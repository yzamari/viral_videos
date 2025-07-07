#!/usr/bin/env python3
"""
Test script to demonstrate news scraping functionality for USA political news
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.scrapers.news_scraper import HotNewsScaper, get_hot_news_video_prompt

def test_political_news_scraping():
    """Test scraping USA political news"""
    print("🔥 Testing USA Political News Scraping...")
    
    scraper = HotNewsScaper()
    
    # Test different political topics
    topics = [
        "USA political news",
        "US election 2024", 
        "Congress news",
        "White House updates",
        "Supreme Court decisions"
    ]
    
    for topic in topics:
        print(f"\n📰 SCRAPING: {topic}")
        print("=" * 50)
        
        try:
            # Get trending articles
            articles = scraper.get_trending_news(topic, max_articles=3, hours_back=24)
            
            if articles:
                print(f"✅ Found {len(articles)} trending articles:")
                
                for i, article in enumerate(articles, 1):
                    print(f"\n📄 Article {i}:")
                    print(f"   Title: {article.title[:80]}...")
                    print(f"   Source: {article.source}")
                    print(f"   Viral Score: {article.viral_score:.2f}")
                    print(f"   Published: {article.published_at}")
                    print(f"   Description: {article.description[:100]}...")
                
                # Generate video prompt from top article
                if articles:
                    print(f"\n🎬 GENERATED VIDEO PROMPT:")
                    print("-" * 30)
                    prompt = scraper.create_video_prompt_from_news(articles[0], "breaking")
                    print(prompt)
                    
            else:
                print("⚠️ No articles found for this topic")
                
        except Exception as e:
            print(f"❌ Error scraping {topic}: {e}")
    
    # Test quick prompt generation
    print(f"\n🚀 QUICK PROMPT GENERATION:")
    print("=" * 50)
    
    quick_prompt = get_hot_news_video_prompt("USA political news", "breaking")
    print(f"Generated prompt: {quick_prompt}")

if __name__ == "__main__":
    test_political_news_scraping() 