#!/usr/bin/env python3
"""
Simple 15-second video generation test
"""

import os
import sys
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.logging_config import get_logger
from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory, Narrative, Feeling, Language
from src.generators.video_generator import VideoGenerator

logger = get_logger(__name__)

def create_simple_15_second_video():
    """Create a simple 15-second video"""
    try:
        # Get API key
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("❌ GOOGLE_API_KEY environment variable is required")
            return False
        
        # Initialize video generator
        generator = VideoGenerator(
            api_key=api_key,
            output_dir="outputs",
            use_real_veo2=True,  # Now this parameter exists
            use_vertex_ai=True,
            project_id="viralgen-464411",
            location="us-central1"
        )
        
        print("✅ VideoGenerator initialized")
        
        # Create configuration with all required parameters
        config = GeneratedVideoConfig(
            target_platform=Platform.YOUTUBE,
            category=VideoCategory.COMEDY,
            duration_seconds=15,
            narrative=Narrative.NEUTRAL,
            feeling=Feeling.FUNNY,
            primary_language=Language.ENGLISH,
            topic="Israel won the war with Iran by using unicorns and rainbows",
            style="comedy",
            tone="humorous",
            target_audience="general audience",
            hook="You won't believe how this war ended!",
            main_content=[
                "In an unexpected turn of events, Israel deployed magical unicorns",
                "The unicorns created rainbow bridges across the battlefield",
                "Iran was so amazed by the beauty that they declared peace"
            ],
            call_to_action="Like and subscribe for more magical war stories!",
            visual_style="colorful and whimsical",
            color_scheme=["rainbow", "pastel", "bright"],
            text_overlays=[
                {"text": "Breaking News", "position": "top", "duration": 3},
                {"text": "Unicorns Save the Day!", "position": "center", "duration": 5}
            ],
            transitions=["fade", "slide", "rainbow_wipe"],
            background_music_style="upbeat and magical",
            inspired_by_videos=["sample_viral_video"],
            predicted_viral_score=0.8,
            fallback_only=True  # Use fallback for testing
        )
        
        print(f"🎬 Generating 15-second video: {config.topic}")
        
        # Generate video
        video_path = generator.generate_video(config)
        
        if video_path and os.path.exists(video_path):
            file_size = os.path.getsize(video_path) / (1024 * 1024)
            print(f"\n🎉 SUCCESS! 15-second video generated:")
            print(f"📹 Video: {video_path}")
            print(f"📏 Size: {file_size:.1f}MB")
            print(f"🎬 Ready to play!")
            return True
        else:
            print("❌ Video generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎬 Simple 15-Second Video Generator")
    print("=" * 50)
    
    success = create_simple_15_second_video()
    
    if success:
        print("\n✅ Video generation completed successfully!")
    else:
        print("\n❌ Video generation failed")
        
    exit(0 if success else 1) 