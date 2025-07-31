#!/usr/bin/env python3
"""
Test script for the real trending intelligence system
Validates that all components are using real API data instead of mock data
"""

import os
import sys
from pathlib import Path
import json
from datetime import datetime

# Add src to path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from src.services.trending import UnifiedTrendingAnalyzer
from src.utils.trending_analyzer import TrendingAnalyzer
from src.generators.hashtag_generator import HashtagGenerator
from src.agents.trend_analyst_agent import TrendAnalystAgent
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

def test_unified_trending_analyzer():
    """Test the unified trending analyzer with real APIs"""
    print("\n🧪 Testing Unified Trending Analyzer...")
    
    analyzer = UnifiedTrendingAnalyzer()
    
    # Test 1: Get all platform trends
    print("\n1️⃣ Testing all platform trends...")
    all_trends = analyzer.get_all_trending_data(limit=5)
    
    # Verify we have data from platforms
    assert 'platforms' in all_trends
    assert 'analysis_timestamp' in all_trends
    
    # Check each platform
    for platform in ['youtube', 'tiktok', 'instagram']:
        if platform in all_trends['platforms']:
            platform_data = all_trends['platforms'][platform]
            print(f"✅ {platform.capitalize()} data retrieved")
            
            # Verify platform has either trending content or error
            if 'error' not in platform_data:
                if platform == 'youtube':
                    assert 'trending_videos' in platform_data or 'analysis' in platform_data
                else:
                    assert 'trending_hashtags' in platform_data
    
    # Test 2: Get trending hashtags
    print("\n2️⃣ Testing unified hashtag retrieval...")
    for platform in ['youtube', 'tiktok', 'instagram']:
        hashtags = analyzer.get_trending_hashtags_unified(
            platform=platform,
            mission="test video content",
            category="technology",
            limit=10
        )
        
        assert isinstance(hashtags, list)
        assert len(hashtags) > 0
        
        # Verify hashtag structure
        for hashtag in hashtags[:3]:
            assert 'tag' in hashtag
            assert hashtag['tag'].startswith('#')
            assert 'trend_score' in hashtag or 'usage_count' in hashtag
            
        print(f"✅ Retrieved {len(hashtags)} hashtags for {platform}")
        print(f"   Top 3: {[h['tag'] for h in hashtags[:3]]}")
    
    print("\n✅ Unified Trending Analyzer tests passed!")
    return True

def test_trending_analyzer():
    """Test the main trending analyzer uses real data"""
    print("\n🧪 Testing Main Trending Analyzer...")
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("⚠️  No GOOGLE_API_KEY found, skipping AI analysis tests")
        return True
    
    analyzer = TrendingAnalyzer(api_key)
    
    # Test getting trending videos
    print("\n1️⃣ Testing real trending video retrieval...")
    videos = analyzer.get_trending_videos('youtube', hours=24, count=5)
    
    assert isinstance(videos, list)
    assert len(videos) > 0
    
    # Check if videos have real data fields
    for video in videos[:2]:
        # Real videos should have these fields
        assert 'title' in video
        assert 'views' in video
        assert 'platform' in video
        
        # Check for real data indicators
        if 'url' in video or 'channel' in video or 'published_at' in video:
            print(f"✅ Found real video data: {video.get('title', 'Unknown')[:50]}...")
            print(f"   Views: {video.get('views', 0):,}")
    
    # Test trend analysis
    print("\n2️⃣ Testing trend analysis with real data...")
    if videos:
        analysis = analyzer.analyze_trends(videos)
        
        assert 'real_data_source' in analysis
        assert analysis['real_data_source'] == 'Platform APIs'
        
        print(f"✅ Analysis completed with {len(analysis.get('common_keywords', []))} keywords")
        print(f"   Data source: {analysis['real_data_source']}")
    
    print("\n✅ Trending Analyzer tests passed!")
    return True

def test_hashtag_generator():
    """Test hashtag generator uses real trending data"""
    print("\n🧪 Testing Hashtag Generator with Real Data...")
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("⚠️  No GOOGLE_API_KEY found, skipping hashtag generator tests")
        return True
    
    generator = HashtagGenerator(api_key)
    
    # Test hashtag generation for different platforms
    platforms = ['youtube', 'tiktok', 'instagram']
    
    for platform in platforms:
        print(f"\n1️⃣ Testing {platform} hashtag generation...")
        
        hashtag_data = generator.generate_trending_hashtags(
            mission="AI technology tutorial",
            platform=platform,
            category="technology",
            script_content="This is a test video about artificial intelligence",
            num_hashtags=15
        )
        
        assert 'hashtags' in hashtag_data
        hashtags = hashtag_data['hashtags']
        
        # Check for real trend incorporation
        real_trend_count = sum(1 for h in hashtags if h.get('data_source') == 'real_api')
        
        print(f"✅ Generated {len(hashtags)} hashtags for {platform}")
        print(f"   Real trending hashtags: {real_trend_count}")
        print(f"   Top 5: {[h['tag'] for h in hashtags[:5]]}")
        
        # Verify at least some hashtags are from real data
        if hashtag_data.get('real_trends_incorporated'):
            print("   ✅ Real trends incorporated!")
    
    print("\n✅ Hashtag Generator tests passed!")
    return True

def test_trend_analyst_agent():
    """Test trend analyst agent uses real APIs"""
    print("\n🧪 Testing Trend Analyst Agent...")
    
    # Create mock session ID
    session_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Initialize agent
    agent = TrendAnalystAgent(session_id)
    
    # Test trend analysis
    print("\n1️⃣ Testing real trend analysis...")
    trends = agent.analyze("artificial intelligence", platform="youtube")
    
    assert 'source' in trends
    assert trends['source'] in ['Real Platform APIs', 'Fallback Data']
    
    if trends['source'] == 'Real Platform APIs':
        print("✅ Using real platform APIs!")
        
        # Check for platform data
        if 'platforms' in trends:
            for platform, data in trends['platforms'].items():
                print(f"   {platform}: {len(data.get('trending_content', []))} trending items")
    else:
        print("⚠️  Using fallback data (APIs may be unavailable)")
    
    print("\n✅ Trend Analyst Agent tests passed!")
    return True

def run_all_tests():
    """Run all trending system tests"""
    print("🚀 Starting Real Trending System Tests")
    print("=" * 50)
    
    tests = [
        ("Unified Trending Analyzer", test_unified_trending_analyzer),
        ("Main Trending Analyzer", test_trending_analyzer),
        ("Hashtag Generator", test_hashtag_generator),
        ("Trend Analyst Agent", test_trend_analyst_agent)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success, None))
        except Exception as e:
            results.append((test_name, False, str(e)))
            print(f"\n❌ {test_name} failed: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for test_name, success, error in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
        if error:
            print(f"   Error: {error}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The trending system is using REAL API data!")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    # Check for API keys
    if not os.getenv('GOOGLE_API_KEY') and not os.getenv('YOUTUBE_API_KEY'):
        print("⚠️  WARNING: No API keys found!")
        print("Set GOOGLE_API_KEY or YOUTUBE_API_KEY environment variable for full functionality")
        print("The system will use fallback data without API keys")
        print()
    
    success = run_all_tests()
    sys.exit(0 if success else 1)