#!/usr/bin/env python3
"""
Simple test to verify cheap mode video generation works
"""

import os
import sys
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.generators.video_generator import VideoGenerator
from src.models.video_models import GeneratedVideoConfig, Language
from src.utils.session_context import create_session_context

async def test_cheap_mode():
    """Test basic cheap mode video generation"""
    print("🧪 Testing cheap mode video generation...")
    
    # Create simple config
    config = GeneratedVideoConfig(
        mission="Test news report about drought",
        duration_seconds=15,
        target_platform="youtube",
        category="news",
        session_id="test_cheap_direct",
        style="news",
        tone="serious",
        target_audience="general",
        hook="Breaking news",
        main_content=["A drought committee has failed to deliver results"],
        call_to_action="Stay tuned",
        visual_style="minimal",
        language=Language.ENGLISH_US,
        languages=[Language.ENGLISH_US],
        cheap_mode=True,
        cheap_mode_level="full",
        fallback_only=True,
        use_real_veo2=False
    )
    
    # Create session context
    session_context = create_session_context("test_cheap_direct")
    
    # Initialize video generator
    generator = VideoGenerator(
        api_key=os.getenv('GOOGLE_API_KEY', ''),
        use_real_veo2=False,
        use_vertex_ai=False
    )
    
    # Generate video (session_context is handled internally)
    result = await generator.generate_video(config)
    
    if result and result.success:
        print(f"✅ Cheap mode video generated successfully!")
        print(f"   Path: {result.file_path}")
        print(f"   Size: {result.file_size_mb} MB")
        print(f"   Duration: {result.generation_time_seconds}s")
        return True
    else:
        print("❌ Cheap mode video generation failed!")
        if result:
            print(f"   Error: {result.error_message}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_cheap_mode())
    sys.exit(0 if success else 1)