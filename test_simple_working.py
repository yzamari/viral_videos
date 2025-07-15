#!/usr/bin/env python3
"""
Simple working test for video generation
"""

import os
import sys
import time
from src.generators.video_generator import VideoGenerator
from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory

def test_simple_generation():
    """Test simple video generation"""
    print("🚀 Starting simple video generation test...")
    
    # Create config
    config = GeneratedVideoConfig(
        topic="Quick test video",
        duration_seconds=5,
        target_platform=Platform.YOUTUBE,
        category=VideoCategory.ENTERTAINMENT,
        session_id="simple_test"
    )
    
    # Create generator with API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    generator = VideoGenerator(
        api_key=api_key,
        use_real_veo2=True,
        use_vertex_ai=True,
        vertex_project_id="viralgen-464411",
        vertex_location="us-central1",
        vertex_gcs_bucket="viral-veo2-results",
        prefer_veo3=False
    )
    
    # Generate video
    start_time = time.time()
    result = generator.generate_video(config)
    generation_time = time.time() - start_time
    
    print(f"✅ Generation completed in {generation_time:.1f}s")
    print(f"   Success: {result.success}")
    print(f"   Video: {result.file_path}")
    print(f"   Size: {result.file_size_mb:.2f}MB")
    
    return result

if __name__ == "__main__":
    try:
        result = test_simple_generation()
        print("🎉 Test completed successfully!")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
