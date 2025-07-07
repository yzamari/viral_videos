#!/usr/bin/env python3
"""
Test Frame Continuity Mode - Creates seamless continuous videos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.generators.video_generator import VideoGenerator
from src.generators.director import Director
from src.models.video_models import (
    VideoAnalysis, Platform, VideoCategory, 
    Narrative, Feeling, GeneratedVideoConfig
)
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_frame_continuity():
    """Test frame continuity mode with a story-based video"""
    
    # Initialize with API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Please set GEMINI_API_KEY environment variable")
        return
    
    # Create output directory
    output_dir = "outputs/continuity_test"
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize video generator
    video_gen = VideoGenerator(
        api_key=api_key,
        output_dir=output_dir,
        use_real_veo2=False  # Use fallback for testing
    )
    
    # Initialize director
    director = Director(api_key=api_key)
    
    print("\n🎬 FRAME CONTINUITY MODE TEST")
    print("=" * 50)
    
    # Test 1: Story-based video (should use continuity)
    print("\n📖 Test 1: Story/Journey Video (Should use continuity)")
    
    topic = "A day in the life of a startup founder"
    style = "documentary journey"
    platform = Platform.YOUTUBE
    category = VideoCategory.LIFESTYLE
    duration = 60
    
    continuity_decision = director.decide_frame_continuity(
        topic=topic,
        style=style,
        category=category,
        duration=duration,
        platform=platform
    )
    
    print(f"\n🎯 Continuity Decision:")
    print(f"   Use continuity: {'✅ YES' if continuity_decision['use_frame_continuity'] else '❌ NO'}")
    print(f"   Score: {continuity_decision['continuity_score']}")
    print(f"   Reasoning:")
    for reason in continuity_decision['reasoning']:
        print(f"     - {reason}")
    
    if continuity_decision['transition_strategy']:
        print(f"\n🔄 Transition Strategy:")
        print(f"   Type: {continuity_decision['transition_strategy']['type']}")
        print(f"   Description: {continuity_decision['transition_strategy']['config']['description']}")
    
    # Test 2: Compilation video (should NOT use continuity)
    print("\n\n🎬 Test 2: Compilation Video (Should NOT use continuity)")
    
    topic2 = "Top 10 viral moments of the week"
    style2 = "compilation highlights"
    
    continuity_decision2 = director.decide_frame_continuity(
        topic=topic2,
        style=style2,
        category=VideoCategory.ENTERTAINMENT,
        duration=30,
        platform=Platform.TIKTOK
    )
    
    print(f"\n🎯 Continuity Decision:")
    print(f"   Use continuity: {'✅ YES' if continuity_decision2['use_frame_continuity'] else '❌ NO'}")
    print(f"   Score: {continuity_decision2['continuity_score']}")
    print(f"   Reasoning:")
    for reason in continuity_decision2['reasoning']:
        print(f"     - {reason}")
    
    # Generate a video with continuity
    print("\n\n🎥 Generating video with frame continuity...")
    
    # Create config manually for testing
    config = GeneratedVideoConfig(
        target_platform=platform,
        category=category,
        duration_seconds=30,  # Shorter for testing
        topic=topic,
        style=style,
        tone="inspiring",
        target_audience="entrepreneurs",
        hook="Ever wondered what it's really like to run a startup?",
        main_content=[
            "5am wake up - the grind begins",
            "Morning standup with the team",
            "Investor meeting preparation",
            "Product launch crisis management",
            "Late night coding session"
        ],
        call_to_action="Follow for more startup insights!",
        visual_style="cinematic documentary",
        color_scheme=["blue", "white", "gray"],
        text_overlays=[{"text": "The Startup Journey", "position": "center"}],
        transitions=["smooth"],
        background_music_style="motivational",
        voiceover_style="professional",
        sound_effects=["typing", "notifications"],
        inspired_by_videos=["test123"],
        predicted_viral_score=0.85,
        narrative=Narrative.PRO_TECHNOLOGY,
        feeling=Feeling.INSPIRATIONAL,
        frame_continuity=True,  # Enable continuity
        fallback_only=True,  # Use fallback for testing
        image_only_mode=False,
        use_image_fallback=True
    )
    
    # Store continuity details
    config._continuity_details = continuity_decision
    
    try:
        # Generate the video
        generated = video_gen.generate_video(config)
        
        print(f"\n✅ Video generated successfully!")
        print(f"   File: {generated.file_path}")
        print(f"   Duration: {generated.config.duration_seconds}s")
        print(f"   Frame continuity: ENABLED")
        print(f"   Transition type: {continuity_decision['transition_strategy']['type']}")
        
    except Exception as e:
        print(f"\n❌ Error generating video: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Different continuity types
    print("\n\n🎨 Testing Different Continuity Types")
    print("=" * 50)
    
    test_cases = [
        ("A virtual tour of Tokyo", "exploration tour", VideoCategory.LIFESTYLE),
        ("How to build a mobile app", "tutorial process", VideoCategory.EDUCATION),
        ("The evolution of smartphones", "technology evolution", VideoCategory.TECHNOLOGY),
        ("Best memes of 2024", "meme compilation", VideoCategory.ENTERTAINMENT)
    ]
    
    for topic, style, category in test_cases:
        decision = director.decide_frame_continuity(
            topic=topic,
            style=style,
            category=category,
            duration=60,
            platform=Platform.YOUTUBE
        )
        
        print(f"\n📹 {topic}")
        print(f"   Style: {style}")
        print(f"   Continuity: {'✅' if decision['use_frame_continuity'] else '❌'} (score: {decision['continuity_score']})")
        if decision['transition_strategy']:
            print(f"   Transition: {decision['transition_strategy']['type']}")

if __name__ == "__main__":
    test_frame_continuity() 