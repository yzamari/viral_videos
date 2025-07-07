#!/usr/bin/env python3
"""
Test Frame Continuity Feature for Seamless Video Generation
This script demonstrates how to generate a 30-40 second video about unicorns loving Israel
with frame continuity enabled for seamless transitions between clips.
"""

import os
import sys
import asyncio
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.generators.video_generator import VideoGenerator
from src.models.video_models import Platform, VideoCategory, GeneratedVideoConfig
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

def create_unicorn_israel_config():
    """Create video configuration for unicorns loving Israel with frame continuity"""
    
    config = GeneratedVideoConfig(
        target_platform=Platform.YOUTUBE,  # Or TIKTOK for vertical format
        category=VideoCategory.ENTERTAINMENT,
        duration_seconds=35,  # 30-40 seconds as requested
        topic="Unicorns Discover Their Love for Israel: The Magical War Victory Story",
        style="magical realism with patriotic elements",
        tone="triumphant and whimsical",
        target_audience="fantasy lovers and Israel supporters",
        hook="What if magical unicorns were Israel's secret allies all along?",
        main_content=[
            "Unicorns gathering in mystical Israeli landscape",
            "Magical unicorns celebrating Israel's victory over Iran", 
            "Unicorns using their magic to protect Israel",
            "Triumphant celebration with Israeli flags and unicorn magic"
        ],
        call_to_action="Follow for more magical geopolitical stories!",
        visual_style="cinematic fantasy with Israeli landmarks",
        color_scheme=["#0038B8", "#FFFFFF", "#FFD700"],  # Israeli flag colors + gold
        text_overlays=[
            {"text": "🦄 UNICORNS ❤️ ISRAEL 🇮🇱", "timing": "0-5", "style": "bold"},
            {"text": "The Magical Victory Story", "timing": "8-13", "style": "normal"},
            {"text": "FOLLOW for Epic Tales! 📖✨", "timing": "30-35", "style": "bold"}
        ],
        transitions=["magical sparkle fade", "triumphant zoom"],
        background_music_style="epic orchestral with Middle Eastern influences",
        voiceover_style="storyteller narrator with excitement",
        sound_effects=["magical chimes", "victory fanfare", "unicorn neighing"],
        inspired_by_videos=[],
        predicted_viral_score=0.85,
        # ENABLE FRAME CONTINUITY FOR SEAMLESS VIDEO
        frame_continuity=True,
        narrative="triumphant",
        feeling="magical",
        realistic_audio=True
    )
    
    return config

def main():
    """Generate seamless unicorn video with frame continuity"""
    
    print("🦄 UNICORN ISRAEL VIDEO GENERATOR 🇮🇱")
    print("=" * 50)
    print("Generating 30-40 second video with FRAME CONTINUITY")
    print("Topic: Unicorns loving Israel and celebrating war victory")
    print("Feature: Seamless transitions (last frame → first frame)")
    print()
    
    # Get API key
    api_key = os.getenv('GOOGLE_API_KEY', os.getenv('GEMINI_API_KEY'))
    if not api_key:
        print("❌ Error: No API key found!")
        print("Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable")
        return
    
    # Initialize video generator
    print("🔧 Initializing Video Generator...")
    generator = VideoGenerator(
        api_key=api_key,
        output_dir="outputs",
        script_model="gemini-2.5-flash",
        refinement_model="gemini-2.5-pro",
        veo_model="veo-2"
    )
    
    # Create configuration with frame continuity
    print("📋 Creating video configuration...")
    config = create_unicorn_israel_config()
    
    print(f"✅ Configuration created:")
    print(f"   Duration: {config.duration_seconds} seconds")
    print(f"   Frame Continuity: {'🎬 ENABLED' if config.frame_continuity else '❌ DISABLED'}")
    print(f"   Topic: {config.topic}")
    print(f"   Platform: {config.target_platform.value}")
    print()
    
    # Generate the video
    print("🎬 Starting video generation with FRAME CONTINUITY...")
    print("This will create seamless transitions between clips!")
    print()
    
    try:
        start_time = datetime.now()
        generated_video = generator.generate_video(config)
        generation_time = (datetime.now() - start_time).total_seconds()
        
        print("✅ VIDEO GENERATION SUCCESSFUL!")
        print("=" * 50)
        print(f"📁 File: {generated_video.file_path}")
        print(f"📏 Size: {generated_video.file_size_mb:.2f} MB")
        print(f"⏱️  Duration: {config.duration_seconds} seconds")
        print(f"🎬 Frame Continuity: ENABLED (seamless video)")
        print(f"⚡ Generation Time: {generation_time:.1f} seconds")
        print(f"🎯 Predicted Viral Score: {config.predicted_viral_score:.2f}")
        print()
        
        print("📝 SCRIPT PREVIEW:")
        print("-" * 30)
        print(generated_video.script[:200] + "..." if len(generated_video.script) > 200 else generated_video.script)
        print("-" * 30)
        print()
        
        print("🎨 VISUAL SCENES:")
        for i, scene in enumerate(generated_video.scene_descriptions, 1):
            print(f"   {i}. {scene}")
        print()
        
        print("🔧 TECHNICAL DETAILS:")
        print(f"   AI Models Used: {', '.join(generated_video.ai_models_used)}")
        print(f"   Audio Transcript: {len(generated_video.audio_transcript)} characters")
        print()
        
        print("🎉 SUCCESS! Your seamless unicorn video is ready!")
        print(f"🎬 Watch it at: {generated_video.file_path}")
        
        # Show frame continuity benefits
        print()
        print("🌟 FRAME CONTINUITY BENEFITS:")
        print("   ✅ Seamless transitions between clips")
        print("   ✅ No jarring cuts or jumps")
        print("   ✅ Professional, cinematic flow")
        print("   ✅ Better viewer retention")
        print("   ✅ Higher perceived production value")
        
    except Exception as e:
        print(f"❌ Error generating video: {e}")
        import traceback
        print(f"🔍 Details: {traceback.format_exc()}")

if __name__ == "__main__":
    main() 