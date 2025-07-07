#!/usr/bin/env python3
"""
Test script to verify comprehensive logging system
"""

import os
import sys
import time
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.comprehensive_logger import ComprehensiveLogger
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

def test_comprehensive_logging():
    """Test all aspects of the comprehensive logging system"""
    print("🧪 Testing Comprehensive Logging System")
    print("=" * 50)
    
    # Create test session
    session_id = datetime.now().strftime('%Y%m%d_%H%M%S') + "_test"
    session_dir = f"outputs/session_{session_id}"
    
    # Initialize logger
    comp_logger = ComprehensiveLogger(session_id, session_dir)
    
    # Test 1: Script Generation Logging
    print("📝 Testing script generation logging...")
    comp_logger.log_script_generation(
        script_type="original",
        content="This is a test script for dancing robots in space. **VOICEOVER:** Welcome to the amazing world of robot dance!",
        model_used="gemini-2.5-flash",
        generation_time=2.5,
        topic="dancing robots in space",
        platform="youtube",
        category="Comedy"
    )
    
    comp_logger.log_script_generation(
        script_type="cleaned",
        content="Welcome to the amazing world of robot dance! These mechanical marvels show their moves in zero gravity.",
        model_used="text_processing",
        generation_time=0.1,
        topic="dancing robots in space",
        platform="youtube",
        category="Comedy"
    )
    
    # Test 2: Audio Generation Logging
    print("🎵 Testing audio generation logging...")
    comp_logger.log_audio_generation(
        audio_type="enhanced_gtts",
        file_path=f"{session_dir}/test_audio.mp3",
        file_size_mb=1.5,
        duration=10.0,
        voice_settings={"lang": "en", "slow": False, "voice": "natural"},
        script_used="Welcome to the amazing world of robot dance!",
        generation_time=15.2,
        success=True
    )
    
    # Test 3: Prompt Generation Logging
    print("🎬 Testing prompt generation logging...")
    comp_logger.log_prompt_generation(
        prompt_type="veo2",
        original_prompt="Robots dancing in space",
        enhanced_prompt="Comedic cartoon robots performing synchronized dance moves in a colorful space station, cinematic style, bright lighting",
        model_used="veo-2",
        duration=8.0,
        aspect_ratio="16:9",
        generation_success=True,
        output_path=f"{session_dir}/veo2_clip_0.mp4",
        file_size_mb=3.2,
        generation_time=45.8
    )
    
    # Test 4: Agent Discussion Logging
    print("🤖 Testing agent discussion logging...")
    comp_logger.log_agent_discussion(
        discussion_id=f"script_development_{session_id}",
        topic="Script Development and Dialogue Optimization",
        participating_agents=["StoryWeaver", "DialogueMaster", "PaceMaster", "AudienceAdvocate"],
        total_rounds=2,
        consensus_level=0.95,
        duration=38.5,
        key_decisions={
            "script_style": "comedic_narrative",
            "pacing": "fast_engaging",
            "dialogue_approach": "natural_conversational"
        },
        key_insights=[
            "Comedy timing is crucial for 10-second format",
            "Robot personalities should be distinct and relatable",
            "Space setting allows for creative visual gags"
        ],
        success=True
    )
    
    # Test 5: Debug Logging
    print("🔧 Testing debug logging...")
    comp_logger.log_debug_info(
        component="VideoGenerator",
        level="INFO",
        message="VEO-2 generation successful",
        data={
            "clip_id": "test_clip_0",
            "duration": 8.0,
            "model": "veo-2",
            "prompt_length": 120
        }
    )
    
    # Test 6: Metrics Update
    print("📊 Testing metrics update...")
    comp_logger.update_metrics(
        topic="dancing robots in space",
        platform="youtube",
        category="Comedy",
        target_duration=10,
        script_generation_time=2.5,
        audio_generation_time=15.2,
        video_generation_time=45.8,
        discussion_time=38.5,
        total_clips_generated=1,
        successful_veo_clips=1,
        fallback_clips=0,
        final_video_size_mb=1.8,
        actual_duration=10.0
    )
    
    # Test 7: Session Finalization
    print("✅ Testing session finalization...")
    comp_logger.finalize_session(success=True)
    
    # Verify files were created
    print("\n📁 Verifying log files...")
    expected_files = [
        "script_generation.json",
        "audio_generation.json", 
        "prompt_generation.json",
        "agent_discussions.json",
        "generation_metrics.json",
        "debug_info.json",
        "session_summary.md"
    ]
    
    logs_dir = os.path.join(session_dir, "comprehensive_logs")
    
    for filename in expected_files:
        filepath = os.path.join(logs_dir, filename)
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"  ✅ {filename}: {file_size} bytes")
        else:
            print(f"  ❌ {filename}: Missing!")
    
    # Show session stats
    print("\n📊 Session Statistics:")
    stats = comp_logger.get_session_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\n🎯 Test completed! Session directory: {session_dir}")
    print("📄 Check the session_summary.md file for a complete overview.")
    
    return session_dir

if __name__ == "__main__":
    try:
        session_dir = test_comprehensive_logging()
        print(f"\n✅ Comprehensive logging test successful!")
        print(f"📁 Results saved to: {session_dir}")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc() 