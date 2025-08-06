#!/usr/bin/env python3
"""Test script to debug concatenation issue"""

import sys
import os
import asyncio
import logging

# Add the project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.news_aggregator.composers.scraped_media_composer import ScrapedMediaComposer
from src.news_aggregator.models.content_models import ContentItem, MediaAsset
from src.utils.session_manager import SessionManager
from src.utils.logging_config import get_logger

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = get_logger(__name__)

async def test_concat():
    """Test the concatenation with simple content"""
    
    # Create session manager
    session_manager = SessionManager()
    session_dir = session_manager.create_session(
        mission="Test concatenation debug",
        platform="tiktok",
        duration=60,
        category="news"
    )
    
    # Create composer
    composer = ScrapedMediaComposer(
        output_dir=session_dir,
        session_manager=session_manager
    )
    
    # Set platform for TikTok
    composer.platform = "tiktok"
    composer.channel_name = "DOOM & GLOOM NEWS"
    
    # Create test content items
    content_items = []
    for i in range(5):
        item = ContentItem(
            id=f"test_{i}",
            source="test",
            title=f"Test Story {i+1}: This is a test headline",
            content=f"This is test content for story {i+1}. It should create a video clip.",
            categories=["test"],
            media_assets=[],
            relevance_score=1.0,
            metadata={"index": i+1}
        )
        content_items.append(item)
    
    logger.info(f"Creating video with {len(content_items)} content items")
    
    # Create video
    try:
        output_path = await composer.create_video_from_scraped_media(
            content_items=content_items,
            duration_seconds=60,
            style="dark comedy news satire",
            output_filename="test_concat_60s.mp4",
            platform="tiktok"
        )
        
        logger.info(f"✅ Video created: {output_path}")
        
        # Check the duration
        import subprocess
        probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                     '-of', 'default=noprint_wrappers=1:nokey=1', output_path]
        result = subprocess.run(probe_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            duration = float(result.stdout.strip())
            logger.info(f"📹 Final video duration: {duration:.1f}s")
            if duration < 50:
                logger.error(f"❌ Duration too short! Expected ~60s, got {duration:.1f}s")
            else:
                logger.info(f"✅ Duration looks good!")
        
    except Exception as e:
        logger.error(f"Failed to create video: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_concat())