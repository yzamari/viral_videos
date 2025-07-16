#!/usr/bin/env python3
"""
Viral Video Generation Workflow
Advanced AI-powered video generation with multi-agent discussions and
        VEO2/3 support
"""

import os
import sys
import time
from typing import Optional, Dict, Any
from datetime import datetime

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.working_orchestrator import WorkingOrchestrator, OrchestratorMode
from src.models.video_models import (
    GeneratedVideoConfig,
    Platform,
    VideoCategory
)
from src.utils.logging_config import get_logger
from src.utils.session_manager import session_manager

logger = get_logger(__name__)
def main(mission: str, category: str = "Comedy", platform: str = "youtube",
         duration: int = 20, image_only: bool = False, fallback_only: bool = False,
         force: bool = False, discussions: str = "enhanced", discussion_log: bool = False,
         session_id: Optional[str] = None, frame_continuity: str = "auto",
         target_audience: Optional[str] = None, style: Optional[str] = None,
         tone: Optional[str] = None, visual_style: Optional[str] = None,
         mode: str = "enhanced", **kwargs):
    """
    Main video generation workflow

    Args:
        mission: Video mission/topic
        category: Video category
        platform: Target platform
        duration: Video duration in seconds
        image_only: Force image-only generation
        fallback_only: Use fallback generation only
        force: Force generation even with quota warnings:
        discussions: AI agent discussion mode
        discussion_log: Show detailed discussion logs
        session_id: Custom session ID
        frame_continuity: Frame continuity mode
        target_audience: Target audience
        style: Content style
        tone: Content tone
        visual_style: Visual style
        mode: Orchestrator mode
    """

    start_time = time.time()

    logger.info(f"🎯 Generating {category} video for mission: {mission}")
    logger.info(f"📱 Platform: {platform}")
    logger.info(f"⏱️ Duration: {duration} seconds")
    logger.info(f"🎭 Mode: {mode} ({_get_agent_count(mode)} agents with discussions)")
    logger.info(f"🎬 Frame Continuity: {_get_frame_continuity_emoji(frame_continuity)} {frame_continuity.title()}")
    logger.info(f"🤖 AI System: 🎯 {discussions.title()} ({_get_agent_count(mode)} agents with discussions, best viral content)")

    try:
        # Create config dictionary for orchestrator
        config = {
            "topic": mission,
            "platform": platform,
            "category": category,
            "duration": duration,
            "style": style or "viral",
            "tone": tone or "engaging",
            "target_audience": target_audience or "general audience",
            "visual_style": visual_style or "dynamic",
            "use_subtitle_overlays": True,
            "frame_continuity": frame_continuity == "on" or (frame_continuity == "auto")
        }

        # Map CLI category to VideoCategory enum
        category_mapping = {
            "Tech": "Technology",
            "Comedy": "Comedy",
            "Educational": "Educational",
            "Entertainment": "Entertainment",
            "News": "News"
        }
        
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise RuntimeError('GOOGLE_API_KEY environment variable is not set. Please set it before running video generation.')

        # Initialize working orchestrator
        orchestrator = WorkingOrchestrator(
            api_key=api_key,
            mission=mission,
            platform=Platform(platform.lower()),
            category=VideoCategory(category_mapping.get(category, category)),
            duration=duration,
            style=style or "viral",
            tone=tone or "engaging",
            target_audience=target_audience or "general audience",
            visual_style=visual_style or "dynamic",
            mode=OrchestratorMode(mode.lower()) if mode else OrchestratorMode.ENHANCED
        )

        # Generate video
        logger.info("🎬 Starting enhanced AI agent video generation")
        result = orchestrator.generate_video(config)

        generation_time = time.time() - start_time
        # Check for success using the correct key from orchestrator result
        if result and isinstance(result, dict) and result.get('success') and result.get('final_video_path'):
            logger.info(f"✅ Video generation completed in {generation_time:.1f}s")
            logger.info(f"📁 Output: {result['final_video_path']}")

            # Get session summary
            if 'session_id' in result:
                try:
                    session_info = session_manager.get_session_path(result['session_id'])
                    logger.info(f"📊 Session: {result['session_id']}")
                    logger.info(f"📂 Session Directory: {session_info}")
                except Exception:
                    pass

            return result['final_video_path']
        else:
            # Log orchestrator error if present
            if result and isinstance(result, dict) and result.get('error'):
                logger.error(f"❌ Video generation failed: {result.get('error')}")
            logger.error(f"❌ Video generation failed after {generation_time:.1f}s")
            return None

    except Exception as e:
        generation_time = time.time() - start_time
        logger.error(f"❌ Video generation failed after {generation_time:.1f}s: {e}")
        raise

def _get_agent_count(mode: str) -> int:
    """Get number of agents for mode"""
    agent_counts = {
        "simple": 3,
        "enhanced": 7,
        "advanced": 15,
        "multilingual": 12,
        "professional": 19
    }
    return agent_counts.get(mode, 7)

def _get_frame_continuity_emoji(mode: str) -> str:
    """Get emoji for frame continuity mode"""
    emojis = {
        "auto": "🤖 AI Agent Decision",
        "on": "✅ ENABLED",
        "of": "❌ DISABLED"
    }
    return emojis.get(mode, "🤖 AI Agent Decision")

if __name__ == "__main__":
    # Example usage
    main(
        mission="Create a funny video about cats learning to use computers",
        platform="youtube",
        duration=20,
        category="Comedy"
    )
