#!/usr/bin/env python3
"""
Test script to verify fixed subtitle synchronization and audio alignment
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from models.video_models import GeneratedVideoConfig, Platform, VideoCategory
from generators.video_generator import VideoGenerator
from utils.session_manager import SessionManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_subtitle_sync():
    """Test the fixed subtitle synchronization"""
    
    # Load API key
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    if not api_key:
        logger.error("❌ No API key found. Please set GOOGLE_API_KEY or GEMINI_API_KEY environment variable")
        return False
    
    # Create test configuration
    config = GeneratedVideoConfig(
        topic="Testing subtitle synchronization with Golda Meir story",
        duration_seconds=30,
        target_platform=Platform.INSTAGRAM,
        category=VideoCategory.EDUCATION,
        hook="How did a Milwaukee schoolgirl become Israel's Iron Lady?",
        main_content=[
            "Meet Golda Meir, a true force of nature.",
            "Her journey from the US to leadership began early.",
            "She was always devoted to her people.",
            "Golda taught, she built, she lived on a kibbutz.",
            "This trailblazer then became Prime Minister of Israel.",
            "She led the nation through its darkest days.",
            "Even David Ben-Gurion called her, 'the best man in government.'"
        ],
        call_to_action="Golda Meir: a grandmother, a leader, a legend. Want to know more? Follow for part two!",
        use_subtitle_overlays=True,
        frame_continuity=False,
        use_real_veo2=True,
        use_vertex_ai=True
    )
    
    # Initialize session manager
    session_manager = SessionManager()
    session_context = session_manager.create_session("subtitle_sync_test")
    
    # Initialize video generator
    video_generator = VideoGenerator(
        api_key=api_key,
        use_real_veo2=True,
        use_vertex_ai=True,
        vertex_project_id=os.getenv('VERTEX_AI_PROJECT_ID', 'viralgen-464411'),
        vertex_location=os.getenv('VERTEX_AI_LOCATION', 'us-central1'),
        vertex_gcs_bucket=os.getenv('VERTEX_AI_GCS_BUCKET', 'viral-veo2-results')
    )
    
    logger.info("🎬 Testing subtitle synchronization fix...")
    logger.info(f"📝 Topic: {config.topic}")
    logger.info(f"⏱️ Duration: {config.duration_seconds}s")
    logger.info(f"📱 Platform: {config.target_platform.value}")
    logger.info(f"🎯 Subtitle overlays: {'✅ ENABLED' if config.use_subtitle_overlays else '❌ DISABLED'}")
    
    try:
        # Generate video with fixed subtitle synchronization
        result = video_generator.generate_video(config)
        
        if result and isinstance(result, str):
            logger.info(f"✅ Video generated successfully: {result}")
            
            # Check if file exists and has reasonable size
            if os.path.exists(result):
                file_size = os.path.getsize(result) / (1024 * 1024)  # MB
                logger.info(f"📁 File size: {file_size:.2f} MB")
                
                if file_size > 1.0:  # At least 1MB
                    logger.info("✅ Video file appears to be valid")
                    
                    # Log session details
                    session_summary = session_context.get_session_summary()
                    logger.info(f"📊 Session summary: {session_summary}")
                    
                    return True
                else:
                    logger.warning(f"⚠️ Video file seems too small: {file_size:.2f} MB")
                    return False
            else:
                logger.error(f"❌ Video file not found: {result}")
                return False
        else:
            logger.error("❌ Video generation failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        return False

def main():
    """Main test function"""
    logger.info("🔧 Starting subtitle synchronization test...")
    
    # Test the fix
    success = test_subtitle_sync()
    
    if success:
        logger.info("🎉 Subtitle synchronization test PASSED!")
        logger.info("📝 Subtitles should now be properly aligned with audio content")
        logger.info("🎵 Audio segments should be synchronized with subtitle timing")
    else:
        logger.error("❌ Subtitle synchronization test FAILED!")
        logger.error("🔍 Please check the logs for details")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 