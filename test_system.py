#!/usr/bin/env python3
"""
Test script to verify system components
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all major components can be imported"""
    print("🧪 Testing imports...")
    
    try:
        # Test models
        from src.models.video_models import TrendingVideo, VideoAnalysis, GeneratedVideoConfig
        print("✅ Models imported successfully")
        
        # Test scrapers
        from src.scrapers.youtube_scraper import YouTubeScraper
        from src.scrapers.news_scraper import NewsScraper
        print("✅ Scrapers imported successfully")
        
        # Test analyzers
        from src.analyzers.video_analyzer import VideoAnalyzer
        print("✅ Analyzers imported successfully")
        
        # Test generators
        from src.generators.video_generator import VideoGenerator
        from src.generators.director import Director
        print("✅ Generators imported successfully")
        
        # Test utils
        from src.utils.logging_config import get_logger
        from src.utils.exceptions import VVGException
        print("✅ Utils imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_logging():
    """Test logging configuration"""
    print("\n🧪 Testing logging...")
    
    try:
        from src.utils.logging_config import get_logger
        logger = get_logger("test")
        
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        print("✅ Logging works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Logging error: {e}")
        return False

def test_models():
    """Test data models"""
    print("\n🧪 Testing data models...")
    
    try:
        from src.models.video_models import TrendingVideo, Platform, VideoCategory
        from datetime import datetime
        
        # Create a test video with all required fields
        video = TrendingVideo(
            video_id="test123",
            platform=Platform.YOUTUBE,
            url="https://youtube.com/watch?v=test123",
            title="Test Video",
            category=VideoCategory.ENTERTAINMENT,
            view_count=1000000,
            like_count=50000,
            comment_count=5000,
            upload_date=datetime.now(),
            channel_id="channel123",
            channel_name="Test Channel",
            duration_seconds=300,
            trending_position=1
        )
        
        print(f"✅ Created test video: {video.title}")
        print(f"   - Platform: {video.platform.value}")
        print(f"   - Views: {video.view_count:,}")
        print(f"   - Category: {video.category.value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Viral Video Generator System Test\n")
    
    tests = [
        test_imports,
        test_logging,
        test_models
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "="*50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All tests passed! ({passed}/{total})")
        print("\n🎉 Your system is ready to use!")
        print("\nNext steps:")
        print("1. Add your API keys to the .env file")
        print("2. Run: python main.py --help")
        print("3. Try: python main.py trends")
    else:
        print(f"⚠️  Some tests failed ({passed}/{total})")
        print("\nPlease check the errors above.")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main()) 