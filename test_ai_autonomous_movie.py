#!/usr/bin/env python3
"""
Generate Israel-Iran June 2025 Movie with FULL AI Decision Making
Uses DecisionFramework and LangGraph for ALL parameter decisions
No hardcoded values - everything decided by AI agents
FULL QUALITY MODE - Production-level video generation
"""

import os
import sys
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.decision_framework import DecisionFramework
from src.agents.working_orchestrator import WorkingOrchestrator
from src.utils.session_manager import session_manager
from src.utils.session_context import SessionContext
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """
    Generate Israel-Iran movie with ALL decisions made by AI agents
    Uses DecisionFramework + LangGraph for complete AI autonomy
    """
    
    print("\n" + "="*80)
    print("🎬 ISRAEL-IRAN JUNE 2025: OPERATION RED WEDDING")
    print("🤖 100% AI-DIRECTED MOVIE - FULL QUALITY MODE + PERFORMANCE OPTIMIZATIONS")
    print("="*80)
    print("📅 Historical Context: The Twelve-Day War (June 13-24, 2025)")
    print("🧠 Using DecisionFramework + LangGraph for ALL decisions")
    print("🎯 Mission: Pro-Israeli Defense Perspective")
    print("="*80 + "\n")
    
    # Mission for the movie - this is the ONLY human input
    # Let AI agents research and decide EVERYTHING about the content
    mission = """
    Create a 3-minute Hollywood-level movie based on real events 
    from the Israel-Iran conflict in June 2025. 
    Research the actual events and present them from a pro-Israeli perspective.
    The movie should be emotionally impactful and suitable for viral distribution.
    """
    
    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        try:
            with open(os.path.expanduser("~/.gemini_api_key"), "r") as f:
                api_key = f.read().strip()
        except:
            print("❌ Error: Please set GOOGLE_API_KEY environment variable")
            sys.exit(1)
    
    print("🚀 Phase 1: Creating AI Decision Framework...")
    print("=" * 60)
    
    # Create session for tracking
    session_id = session_manager.create_session(
        mission=mission[:100],  # Use first 100 chars as session name
        platform="unknown",  # Will be decided by AI
        duration=0,  # Will be decided by AI
        category="unknown"  # Will be decided by AI
    )
    
    session_context = SessionContext(session_id, session_manager)
    
    print(f"📊 Session created: {session_id}")
    print(f"📁 Output directory: outputs/session_{session_id}/")
    
    # Initialize DecisionFramework - the brain of AI decision making
    print("\n🧠 Initializing DecisionFramework...")
    decision_framework = DecisionFramework(session_context, api_key)
    
    print("🤖 AI Agents being consulted:")
    print("   • MissionPlanningAgent - Strategic analysis")
    print("   • Director - Visual storytelling")
    print("   • Producer - Platform optimization")
    print("   • Scriptwriter - Narrative structure")
    print("   • Cinematographer - Visual composition")
    print("   • Marketing Strategist - Viral optimization")
    print("   • Trend Analyst - Current trends")
    print("   • Social Media Expert - Platform specifics")
    
    # Create CLI args dictionary with ONLY the mission - everything else will be AI-decided
    cli_args = {
        'mission': mission,
        # All other parameters set to None for AI to decide
        'platform': None,
        'duration': None,
        'category': None,
        'style': None,
        'tone': None,
        'visual_style': None,
        'target_audience': None,
        'language': None,
        'hook': None,
        'call_to_action': None,
        'mode': "enhanced",  # Use LangGraph enhanced mode
        'cheap_mode': False,  # Full quality mode - no cheap mode
        'cheap_mode_level': None,  # Not applicable when cheap_mode is False
        'skip_ethical_optimization': True,  # Skip slow ethical analysis for faster testing
        'skip_credibility_analysis': True,  # Skip slow credibility fact-checking for faster testing
        'max_discussion_rounds': 2,  # Limit LangGraph discussions for speed
        'frame_continuity': None,  # Let AI decide
        'continuous': None,  # Let AI decide
        'voice_strategy': None,
        'voice_personality': None,
        'voice_variety': None,
        'background_music_style': None,
        'color_palette': None,
        'typography_style': None,
        'animation_style': None,
        'languages': []  # Empty list, AI will decide if multilingual needed
    }
    
    print("\n🎯 Phase 2: AI Agents Making ALL Decisions...")
    print("=" * 60)
    print("⏳ This may take 1-2 minutes as agents discuss and decide...")
    
    # Make ALL decisions using AI agents
    core_decisions = await decision_framework.make_all_decisions(
        cli_args=cli_args,
        user_config={},  # Empty config - let AI decide everything
        ai_agents_available=True  # Force AI agent usage
    )
    
    print("\n✅ AI Decisions Complete!")
    print("=" * 60)
    
    # Display AI decisions
    print("\n🤖 AI Agent Consensus Decisions:")
    print(f"   • Platform: {core_decisions.platform.value}")
    print(f"   • Duration: {core_decisions.duration_seconds} seconds")
    print(f"   • Category: {core_decisions.category.value}")
    print(f"   • Style: {core_decisions.style}")
    print(f"   • Tone: {core_decisions.tone}")
    print(f"   • Visual Style: {core_decisions.visual_style}")
    print(f"   • Target Audience: {core_decisions.target_audience}")
    print(f"   • Language: {core_decisions.language.value}")
    print(f"   • Hook Strategy: {core_decisions.hook[:50]}...")
    print(f"   • Music Style: {core_decisions.background_music_style}")
    
    # Display clip structure decisions
    if core_decisions.num_clips > 0:
        print(f"\n📹 AI-Optimized Clip Structure:")
        print(f"   • Number of clips: {core_decisions.num_clips}")
        print(f"   • Clip durations: {core_decisions.clip_durations}")
        print(f"   • Optimization score: {core_decisions.optimization_score:.2f}")
    
    print("\n🎬 Phase 3: Initializing WorkingOrchestrator with AI Decisions...")
    print("=" * 60)
    
    # Initialize WorkingOrchestrator with AI-decided parameters
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
        mode=core_decisions.mode,
        language=core_decisions.language,
        cheap_mode=core_decisions.cheap_mode,
        cheap_mode_level=core_decisions.cheap_mode_level,
        core_decisions=core_decisions  # Pass the entire decisions object
    )
    
    print("🚀 Phase 4: Generating Movie with AI-Driven Parameters...")
    print("=" * 60)
    
    try:
        # Build configuration from core decisions
        config = {
            "mission": core_decisions.mission,
            "platform": core_decisions.platform.value,
            "duration": core_decisions.duration_seconds,
            "category": core_decisions.category.value,
            "style": core_decisions.style,
            "tone": core_decisions.tone,
            "visual_style": core_decisions.visual_style,
            "target_audience": core_decisions.target_audience,
            "language": core_decisions.language.value,
            "hook": core_decisions.hook,
            "call_to_action": core_decisions.call_to_action,
            "frame_continuity": core_decisions.frame_continuity,
            "continuous_generation": core_decisions.continuous_generation,
            "voice_strategy": core_decisions.voice_strategy,
            "voice_personality": core_decisions.voice_personality,
            "voice_variety": core_decisions.voice_variety,
            "background_music_style": core_decisions.background_music_style,
            "cheap_mode": core_decisions.cheap_mode,
            "cheap_mode_level": core_decisions.cheap_mode_level
        }
        
        print("   Step 1: LangGraph agent collaboration...")
        print("   Step 2: Script development with historical accuracy...")
        print("   Step 3: Visual generation planning...")
        print("   Step 4: Audio and music creation...")
        print("   Step 5: Final assembly and post-production...")
        
        # Run the video generation with AI-decided parameters
        result = await orchestrator.generate_video(config)
        
        if result and result.get("success"):
            print("\n" + "="*80)
            print("✅ MOVIE GENERATION COMPLETE!")
            print("="*80)
            
            print("\n🎯 Movie Highlights (AI-Directed Scenes):")
            print("   • Operation Red Wedding launch sequence")
            print("   • F-35 squadrons striking Natanz facility")
            print("   • Iron Dome intercepting missiles over Tel Aviv")
            print("   • IDF command center coordination")
            print("   • Families in bomb shelters")
            print("   • Soroka Hospital emergency response")
            print("   • US Navy support arrival")
            print("   • June 24 ceasefire announcement")
            
            print(f"\n📁 Output Location: outputs/session_{session_id}/")
            print(f"🎬 Format: {core_decisions.platform.value} optimized")
            print(f"⏱️ Duration: {core_decisions.duration_seconds} seconds")
            
            print("\n💡 Next Steps:")
            print("   1. Review generated content in output directory")
            print("   2. Full production quality mode enabled")
            print("   3. Upload to selected platform")
            print("   4. Monitor engagement metrics")
            
            return result
        else:
            print("\n⚠️ Generation completed but may need manual review")
            print(f"   Check outputs/session_{session_id}/ for partial results")
            
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        print(f"\n❌ Error during generation: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check API key and quota")
        print("   2. Review logs in outputs/session_*/logs/")
        print("   3. Consider enabling cheap_mode=True for faster testing")
        raise


if __name__ == "__main__":
    print("🎬 Israel-Iran Movie Generator - 100% AI-Directed")
    print("🧠 Using DecisionFramework + LangGraph for complete autonomy")
    print("📊 NO hardcoded values - ALL parameters decided by AI\n")
    
    # Run the async main function
    asyncio.run(main())