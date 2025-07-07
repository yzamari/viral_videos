#!/usr/bin/env python3
"""
Test script for image-only mode
"""
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.generators.video_generator import VideoGenerator
from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory

def test_image_only_mode():
    """Test the new image-only mode"""
    
    # Setup
    api_key = os.getenv('GOOGLE_API_KEY', os.getenv('GEMINI_API_KEY'))
    if not api_key:
        print("❌ No API key found. Set GOOGLE_API_KEY or GEMINI_API_KEY")
        return
    
    output_dir = "outputs/test_image_mode"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create video generator
    generator = VideoGenerator(api_key, output_dir)
    
    # Create test config
    config = GeneratedVideoConfig(
        topic="Test image-only mode with funny cats",
        duration_seconds=10,  # 10 seconds = 20 images at 2 images/second
        target_platform=Platform.TIKTOK,
        video_category=VideoCategory.ENTERTAINMENT,
        predicted_viral_score=0.85,
        image_only_mode=True,  # Enable image-only mode
        images_per_second=2,
        # Required fields
        category=VideoCategory.ENTERTAINMENT,
        style="fun",
        tone="humorous",
        target_audience="Gen Z",
        hook="Watch these funny cats!",
        main_content="Hilarious cat moments",
        call_to_action="Like and follow!",
        visual_style="colorful",
        color_scheme="vibrant",
        text_overlays=["Funny cats!", "LOL"],
        transitions=["cut", "fade"],
        background_music_style="upbeat",
        inspired_by_videos=[]
    )
    
    print("🖼️ Testing Image-Only Mode")
    print(f"📝 Topic: {config.topic}")
    print(f"⏱️ Duration: {config.duration_seconds}s")
    print(f"📸 Images per second: {config.images_per_second}")
    print(f"🎯 Expected images: {config.duration_seconds * config.images_per_second}")
    print("=" * 60)
    
    # Generate video with images
    try:
        generated_video = generator.generate_video(config)
        
        print(f"\n✅ Success!")
        print(f"📁 Output: {generated_video.file_path}")
        print(f"📏 Size: {generated_video.file_size_mb:.2f} MB")
        print(f"⏱️ Duration: {generated_video.config.duration_seconds}s")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_image_only_mode() 