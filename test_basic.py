#!/usr/bin/env python3
"""
Simple test to verify the system works
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic():
    try:
        from src.generators.video_generator import VideoGenerator
        from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory
        
        print("✅ Imports successful")
        
        # Test basic config creation
        config = GeneratedVideoConfig(
            topic="Test video",
            duration_seconds=5,
            target_platform=Platform.YOUTUBE,
            category=VideoCategory.ENTERTAINMENT,
            session_id="test_session"
        )
        
        print("✅ Config creation successful")
        
        # Test generator creation
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            generator = VideoGenerator(
                api_key=api_key,
                use_real_veo2=True,
                use_vertex_ai=True,
                vertex_project_id="viralgen-464411",
                vertex_location="us-central1",
                vertex_gcs_bucket="viral-veo2-results"
            )
            print("✅ Generator creation successful")
        else:
            print("⚠️ No API key, skipping generator test")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Running basic test...")
    success = test_basic()
    if success:
        print("🎉 Basic test passed!")
    else:
        print("❌ Basic test failed!")
