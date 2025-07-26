#!/usr/bin/env python3
"""
Debug script for multi-language generation
"""
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.models.video_models import Language, GeneratedVideoConfig, Platform, VideoCategory
from src.generators.multi_language_generator import MultiLanguageVideoGenerator

def test_multilang_generator():
    """Test the multi-language generator directly"""
    print("🔧 Testing MultiLanguageVideoGenerator directly...")
    
    try:
        # Create a simple config
        test_config = GeneratedVideoConfig(
            mission="Test multi-language generation",
            duration_seconds=20,
            target_platform=Platform.YOUTUBE,
            category=VideoCategory.NEWS,
            realistic_audio=False,
            use_real_veo2=False,
            style="professional",
            tone="serious",
            target_audience="general audience",
            visual_style="news broadcast"
        )
        
        languages = [Language.ENGLISH_US, Language.HEBREW, Language.PERSIAN]
        
        print(f"✅ Config created: {test_config.mission}")
        print(f"✅ Languages: {[lang.value for lang in languages]}")
        
        # Test generator initialization
        generator = MultiLanguageVideoGenerator(api_key="test", output_dir="outputs")
        print("✅ Generator initialized")
        
        # Check if method exists
        if hasattr(generator, 'generate_multilingual_video'):
            print("✅ Method 'generate_multilingual_video' found")
            print(f"📝 Method signature: {generator.generate_multilingual_video.__annotations__}")
        else:
            print("❌ Method 'generate_multilingual_video' not found")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_multilang_generator()
    if success:
        print("🎉 Debug test completed successfully")
    else:
        print("💥 Debug test failed")