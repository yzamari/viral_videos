#!/usr/bin/env python3
"""Test script for news aggregator functionality"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_news_aggregator():
    """Test basic news aggregation"""
    print("🎬 Testing News Aggregator\n")
    
    # Test 1: Check if scrapers work
    print("1. Testing Web Scraper...")
    try:
        from src.news_aggregator.scrapers.web_scraper import WebNewsScraper
        from src.news_aggregator.models.content_models import NewsSource, SourceType
        
        scraper = WebNewsScraper()
        
        # Create test source
        source = NewsSource(
            id="test",
            name="Test Source",
            source_type=SourceType.WEB,
            url="https://www.cnn.com"
        )
        
        # Try to validate
        is_valid = await scraper.validate_source(source)
        print(f"   ✅ CNN.com is accessible: {is_valid}")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 2: Check Ynet scraper
    print("\n2. Testing Ynet Scraper...")
    try:
        from src.news_aggregator.scrapers.israeli_scrapers import YnetScraper
        
        ynet_scraper = YnetScraper()
        articles = await ynet_scraper.scrape_ynet_homepage()
        
        print(f"   ✅ Found {len(articles)} articles from Ynet")
        if articles:
            print(f"   📰 First article: {articles[0].title[:50]}...")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 3: Check CNN scraper
    print("\n3. Testing CNN Scraper...")
    try:
        from src.news_aggregator.scrapers.cnn_scraper import CNNScraper
        
        cnn_scraper = CNNScraper()
        articles = await cnn_scraper.scrape_cnn_homepage(max_articles=5)
        
        print(f"   ✅ Found {len(articles)} articles from CNN")
        if articles:
            print(f"   📰 First article: {articles[0].title[:50]}...")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 4: Check content analyzer
    print("\n4. Testing Content Analyzer...")
    try:
        from src.news_aggregator.processors.content_analyzer import ContentAnalyzer
        from src.ai.manager import AIServiceManager
        
        # Mock AI manager
        class MockAIManager:
            async def generate_text(self, prompt, max_tokens=100):
                return "This is a test summary."
        
        analyzer = ContentAnalyzer(MockAIManager())
        
        if articles:
            analysis = await analyzer.analyze(
                articles[0],
                "general",
                "en"
            )
            print(f"   ✅ Analysis complete:")
            print(f"      - Relevance: {analysis['relevance_score']:.2f}")
            print(f"      - Sentiment: {analysis['sentiment_score']:.2f}")
            print(f"      - Tags: {', '.join(analysis['tags'][:3])}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 5: Simple aggregation
    print("\n5. Testing Simple News Aggregation...")
    try:
        # Collect articles from multiple sources
        all_articles = []
        
        # Add Ynet articles
        ynet_articles = await ynet_scraper.scrape_ynet_homepage()
        all_articles.extend(ynet_articles[:3])
        
        # Add CNN articles  
        cnn_articles = await cnn_scraper.scrape_cnn_homepage(max_articles=3)
        all_articles.extend(cnn_articles[:3])
        
        print(f"   ✅ Collected {len(all_articles)} total articles")
        print(f"   📊 Sources: Ynet ({len(ynet_articles[:3])}), CNN ({len(cnn_articles[:3])})")
        
        # Group by language
        hebrew_articles = [a for a in all_articles if a.language == "he"]
        english_articles = [a for a in all_articles if a.language == "en"]
        
        print(f"   🌐 Languages: Hebrew ({len(hebrew_articles)}), English ({len(english_articles)})")
        
        # Show titles
        print("\n   📰 Article Titles:")
        for i, article in enumerate(all_articles[:5]):
            print(f"      {i+1}. [{article.language}] {article.title[:60]}...")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print("\n✅ Test complete!")

if __name__ == "__main__":
    asyncio.run(test_news_aggregator())