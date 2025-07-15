#!/usr/bin/env python3
"""
Minimal working test
"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that imports work"""
    try:
        from src.generators.video_generator import VideoGenerator
        print("✅ VideoGenerator import successful")
        
        from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory
        print("✅ Models import successful")
        
        # Test basic instantiation
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY not set")
            return False
        
        generator = VideoGenerator(
            api_key=api_key,
            use_real_veo2=True,
            use_vertex_ai=True,
            vertex_project_id="viralgen-464411",
            vertex_location="us-central1",
            vertex_gcs_bucket="viral-veo2-results",
            prefer_veo3=False
        )
        print("✅ VideoGenerator instantiation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import/instantiation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Running minimal test...")
    success = test_imports()
    if success:
        print("🎉 Minimal test passed!")
    else:
        print("❌ Minimal test failed!")
