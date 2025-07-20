#!/usr/bin/env python3
"""
Debug session test to verify AI agent discussions and session management
"""

from utils.logging_config import get_logger
from utils.session_context import SessionContext
from utils.session_manager import SessionManager
from agents.working_orchestrator import WorkingOrchestrator, OrchestratorMode
from models.video_models import Platform, VideoCategory
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


logger = get_logger(__name__)


def test_debug_session():
    """Test session with debugging enabled"""

    print("�� DEBUGGING SESSION - Testing AI Agent Discussions")
    print("=" * 60)

    # Load API key
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ No API key found")
        return False

    print(f"✅ API key loaded (length: {len(api_key)})")

    # Create session manager
    session_manager = SessionManager()

    # Create test mission - EXACTLY what you want
    test_mission = "Convince Iranians to drop nuclear weapons through diplomatic dialogue"

    print(f"🎯 Test Mission: {test_mission}")
    print("📱 Platform: YouTube")
    print("📂 Category: News")
    print("⏱️ Duration: 30 seconds")

    # Create session with correct parameters
    session_id = session_manager.create_session(
        mission=test_mission,
        platform="youtube",
        category="News"
    )

    print(f"💾 Session created: {session_id}")

    # Create session context
    SessionContext(session_id, session_manager)

    print("📁 Session context created")

    # Test session directory creation
    session_dir = f"outputs/{session_id}"
    
    # Check if session directory exists
    if not os.path.exists(session_dir):
        print(f"❌ Session directory not found: {session_dir}")
        return
    
    # Check metadata file
    metadata_file = os.path.join(session_dir, "session_metadata.json")
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as f:
            import json
            metadata = json.load(f)
            print("✅ Session metadata found:")
            print(f"   Mission: {metadata.get('mission', 'MISSING')}")
            print(f"   Platform: {metadata.get('platform', 'MISSING')}")
            print(f"   Category: {metadata.get('category', 'MISSING')}")
    else:
        print("❌ Session metadata missing")

    # Create orchestrator with correct parameters
    print("🎬 Creating orchestrator...")
    orchestrator = WorkingOrchestrator(
        api_key=api_key,
        mission=test_mission,
        platform=Platform.YOUTUBE,
        category=VideoCategory.NEWS,
        duration=30,  # Fixed: Use 'duration' not 'duration_seconds'
        style="diplomatic",
        tone="persuasive",
        target_audience="Iranian citizens",
        visual_style="professional",
        mode=OrchestratorMode.ENHANCED
    )

    print("✅ Orchestrator created")
    print(f"   Mission: {orchestrator.mission}")
    print(f"   Platform: {orchestrator.platform}")
    print(f"   Category: {orchestrator.category}")
    print(f"   Duration: {orchestrator.duration}s")
    print(f"   Style: {orchestrator.style}")
    print(f"   Tone: {orchestrator.tone}")
    print(f"   Target Audience: {orchestrator.target_audience}")
    print(f"   Visual Style: {orchestrator.visual_style}")
    print(f"   Mode: {orchestrator.mode}")

    # Test that the orchestrator has the correct mission
    if orchestrator.mission == test_mission:
        print("✅ Mission correctly set in orchestrator")
    else:
        print("❌ Mission mismatch!")
        print(f"   Expected: {test_mission}")
        print(f"   Got: {orchestrator.mission}")

    # Set the session ID in orchestrator
    orchestrator.session_id = session_id
    print(f"🔗 Set orchestrator session ID: {orchestrator.session_id}")

    # Test AI agent discussion preparation
    print("\n🤖 Testing AI Agent Discussion System")
    print(f"   Discussion system available: {orchestrator.discussion_system is not None}")
    print(f"   Agents loaded: {orchestrator._count_agents_used()}")

    # Test script generation (without full video generation)
    print("\n📝 Testing Script Generation")
    try:
        # Create a minimal config for testing
        test_config = {
            'enable_trending': False,
            'incorporate_news': False,
            'language': 'en-US'
        }

        # Test script generation
        script_data = orchestrator._generate_enhanced_script(test_config)

        if script_data:
            print("✅ Script generated successfully")
            print(f"   Script type: {type(script_data)}")
            if isinstance(script_data, dict):
                print(f"   Script keys: {list(script_data.keys())}")
                # Check if script contains the mission topic
                script_str = str(script_data)
                if "Iran" in script_str or "nuclear" in script_str or "diplomatic" in script_str:
                    print("✅ Script contains mission-related content")
                else:
                    print("❌ Script does NOT contain mission-related content")
                    print(f"   Script preview: {script_str[:200]}...")
        else:
            print("❌ Script generation failed")

    except Exception as e:
        print(f"❌ Script generation error: {e}")

    print("\n🎉 Debug session test completed!")
    return True


if __name__ == "__main__":
    test_debug_session()
