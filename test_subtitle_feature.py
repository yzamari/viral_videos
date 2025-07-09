#!/usr/bin/env python3
"""
Test script to demonstrate the new subtitle overlay feature
"""
import os
import sys
sys.path.append('src')

from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory, ForceGenerationMode
from src.generators.video_generator import VideoGenerator

def test_subtitle_overlays():
    """Test the new subtitle overlay feature"""
    
    # Get API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Please set GEMINI_API_KEY environment variable")
        return
    
    print("🎬 Testing Subtitle Overlay Feature")
    print("=" * 50)
    
    # Create video generator
    generator = VideoGenerator(
        api_key=api_key,
        use_vertex_ai=True,
        use_real_veo2=True
    )
    
    # Test 1: Regular text overlays (default)
    print("\n📝 Test 1: Regular Text Overlays (Default)")
    config1 = GeneratedVideoConfig(
        topic="Benefits of morning exercise",
        duration_seconds=20,
        target_platform=Platform.INSTAGRAM,
        category=VideoCategory.HEALTH,
        force_generation_mode=ForceGenerationMode.FORCE_IMAGE_GEN,  # Use image gen for faster testing
        use_subtitle_overlays=False  # Default behavior
    )
    
    try:
        video1 = generator.generate_video(config1)
        print(f"✅ Regular overlays video generated: {video1}")
    except Exception as e:
        print(f"❌ Regular overlays test failed: {e}")
    
    # Test 2: Subtitle overlays (new feature)
    print("\n🎤 Test 2: Audio-Based Subtitle Overlays (New Feature)")
    config2 = GeneratedVideoConfig(
        topic="Benefits of morning exercise",
        duration_seconds=20,
        target_platform=Platform.INSTAGRAM,
        category=VideoCategory.HEALTH,
        force_generation_mode=ForceGenerationMode.FORCE_IMAGE_GEN,  # Use image gen for faster testing
        use_subtitle_overlays=True  # NEW FEATURE: Use audio-based subtitles
    )
    
    try:
        video2 = generator.generate_video(config2)
        print(f"✅ Subtitle overlays video generated: {video2}")
    except Exception as e:
        print(f"❌ Subtitle overlays test failed: {e}")
    
    print("\n🎉 Subtitle Overlay Feature Test Complete!")
    print("=" * 50)
    print("📋 Summary:")
    print("- Regular overlays: Generic trendy social media text")
    print("- Subtitle overlays: Audio script content as subtitles")
    print("- Both use smart positioning to avoid content cutoff")
    print("- Subtitle overlays are more accessible and informative")

if __name__ == "__main__":
    test_subtitle_overlays() 