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
async def async_main(mission: str, category: str = "Comedy", platform: str = "youtube",
         duration: int = 20, image_only: bool = False, fallback_only: bool = False,
         force: bool = False, discussions: str = "enhanced", discussion_log: bool = False,
         session_id: Optional[str] = None, visual_continuity: bool = True,
         content_continuity: bool = True, target_audience: Optional[str] = None, style: Optional[str] = None,
         tone: Optional[str] = None, visual_style: Optional[str] = None,
         mode: str = "enhanced", cheap_mode: bool = True, cheap_mode_level: str = "full", 
         theme: Optional[str] = None, style_template: Optional[str] = None, 
         reference_style: Optional[str] = None, character: Optional[str] = None,
         scene: Optional[str] = None, **kwargs):
    """
    Main video generation workflow

    Args:
        mission: Video mission
        category: Video category
        platform: Target platform
        duration: Video duration in seconds
        image_only: Force image-only generation
        fallback_only: Use fallback generation only
        force: Force generation even with quota warnings:
        discussions: AI agent discussion mode
        discussion_log: Show detailed discussion logs
        session_id: Custom session ID
        visual_continuity: Visual continuity between clips (default: True)
        content_continuity: Content/narrative continuity (default: True)
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
    logger.info(f"🎬 Visual Continuity: {'✅' if visual_continuity else '❌'} {'Enabled' if visual_continuity else 'Disabled'}")
    logger.info(f"📝 Content Continuity: {'✅' if content_continuity else '❌'} {'Enabled' if content_continuity else 'Disabled'}")
    logger.info(f"🤖 AI System: 🎯 {discussions.title()} ({_get_agent_count(mode)} agents with discussions, best viral content)")
    
    # Cost-saving mode information
    if cheap_mode:
        logger.info("💰 CHEAP MODE: Enabled (saves costs - no VEO, basic TTS, minimal AI)")
        logger.info("💡 Use --no-cheap to disable and use premium features")
    else:
        logger.info("💎 PREMIUM MODE: Using VEO video generation and premium voices")

    try:
        # Create config dictionary for orchestrator
        config = {
            "topic": mission,
            "platform": platform,
            "category": category,
            "duration": duration,
            "style": style,  # Don't override user's style choice
            "tone": tone,    # Don't override user's tone choice
            "target_audience": target_audience or "general audience",
            "visual_style": visual_style,  # Don't override user's visual style choice
            "use_subtitle_overlays": True,
            "frame_continuity": visual_continuity,
            "continuous_generation": content_continuity,
            "cheap_mode": cheap_mode
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

        # Apply cost-saving optimizations in cheap mode
        if cheap_mode:
            # Force fallback mode to avoid VEO costs
            fallback_only = True
            # Use simpler discussion mode to save API calls
            discussions = "off" if discussions == "enhanced" else discussions
            # Use simple mode with fewer agents
            mode = "simple"
            logger.info("💰 Applied cheap mode optimizations: fallback_only=True, discussions=off, mode=simple")
        
        # STEP 1: CENTRALIZED DECISION MAKING
        from ..core.decision_framework import DecisionFramework
        from ..utils.session_context import create_session_context
        
        # Create or get session context
        if session_id:
            session_context = create_session_context(session_id)
        else:
            from ..utils.session_manager import session_manager
            session_id = session_manager.create_session(
                mission=mission,
                platform=platform,
                duration=duration,
                category=category
            )
            session_context = create_session_context(session_id)
        
        # Initialize decision framework with API key for Mission Planning Agent
        api_key = os.getenv("GOOGLE_AI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        decision_framework = DecisionFramework(session_context, api_key)
        
        # Make all decisions upfront
        cli_args = {
            'mission': mission,
            'platform': platform,
            'category': category,
            'duration': duration,
            'style': style,
            'tone': tone,
            'target_audience': target_audience,
            'visual_style': visual_style,
            'mode': mode,
            'cheap_mode': cheap_mode,
            'cheap_mode_level': cheap_mode_level,
            'theme': theme,
            'style_reference': style_template or reference_style,
            'continuous': content_continuity,
            'frame_continuity': visual_continuity,
            'character': character,
            'scene': scene
        }
        
        # CRITICAL: Make all decisions before any generation
        core_decisions = await decision_framework.make_all_decisions(cli_args, ai_agents_available=True)
        
        logger.info("✅ All decisions made upfront - propagating to system")
        
        # Initialize working orchestrator with decisions
        orchestrator = WorkingOrchestrator(
            api_key=api_key,
            mission=core_decisions.mission,
            platform=core_decisions.platform,
            category=core_decisions.category,
            duration=core_decisions.duration_seconds,
            style=core_decisions.style,
            tone=core_decisions.tone,
            target_audience=core_decisions.target_audience,
            visual_style=core_decisions.visual_style,
            mode=OrchestratorMode(core_decisions.mode.lower()) if core_decisions.mode else OrchestratorMode.ENHANCED,
            session_id=session_id,
            cheap_mode=core_decisions.cheap_mode,
            cheap_mode_level=core_decisions.cheap_mode_level,
            core_decisions=core_decisions  # Pass all decisions to orchestrator
        )

        # Create config dictionary for orchestrator
        config = {
            'mission': mission,
            'platform': platform,
            'category': category,
            'duration': duration,
            'style': style,
            'tone': tone,
            'target_audience': target_audience,
            'visual_style': visual_style,
            'mode': mode,
            'cheap_mode': cheap_mode,
            'cheap_mode_level': cheap_mode_level,
            'theme': theme,
            'style_template': style_template,
            'reference_style': reference_style,
            'character': character,
            'scene': scene,
            'session_id': session_id,
            'core_decisions': core_decisions
        }
        
        # Generate video
        logger.info("🎬 Starting enhanced AI agent video generation")
        result = await orchestrator.generate_video(config)

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


def main(*args, **kwargs):
    """Synchronous wrapper for async_main"""
    import asyncio
    return asyncio.run(async_main(*args, **kwargs))

if __name__ == "__main__":
    # Example usage
    main(
        mission="Create a funny video about cats learning to use computers",
        platform="youtube",
        duration=20,
        category="Comedy"
    )
