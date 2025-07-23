#!/usr/bin/env python3
"""Test cheap mode video generation for Persian news"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory
from src.generators.video_generator import VideoGenerator
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

async def test_cheap_persian_news():
    """Test cheap mode generation with simple config"""
    
    # Create simple config
    config = GeneratedVideoConfig(
        topic="Persian news: Water crisis report. Anchor with hijab.",
        hook="Breaking news from Iran",
        main_content=["Government forms water committee", "Citizens concerned about drought"],
        call_to_action="Stay informed",
        target_platform=Platform.TIKTOK,
        category=VideoCategory.ENTERTAINMENT,
        duration_seconds=20,
        session_id="test_cheap_persian"
    )
    
    # Set cheap mode
    config.cheap_mode = True
    config.cheap_mode_level = "full"
    config.use_real_veo2 = False
    config.fallback_only = True
    
    logger.info("🎬 Starting cheap mode test...")
    
    # Initialize video generator
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("❌ GOOGLE_API_KEY not set")
        return
        
    generator = VideoGenerator(
        api_key=api_key,
        use_real_veo2=False,
        use_vertex_ai=False
    )
    
    # Generate video
    try:
        result = await generator.generate_video(config)
        
        if result and result.success:
            logger.info(f"✅ Video generated successfully!")
            logger.info(f"📁 File: {result.file_path}")
            logger.info(f"📊 Size: {result.file_size_mb}MB")
            logger.info(f"⏱️ Time: {result.generation_time_seconds:.1f}s")
        else:
            logger.error(f"❌ Generation failed: {result.error_message if result else 'No result'}")
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_cheap_persian_news())