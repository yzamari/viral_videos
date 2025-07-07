#!/usr/bin/env python3
"""
Test script to fix Israeli news video generation issues:
1. Correct topic usage (not "Script Content and Structure Optimization")
2. Proper video duration (24 seconds, not 92 seconds)
3. Agent discussions saved in session folder
4. Natural voice (not robotic)
5. Ensure VEO-2 content matches topic
"""

import os
import sys
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.generators.video_generator import VideoGenerator
from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

def test_israeli_news_generation():
    """Test Israeli news video generation with all fixes"""
    
    # Configuration
    topic = "funny news from israel"
    duration = 15
    platform = Platform.YOUTUBE
    category = VideoCategory.COMEDY
    
    print(f"🎬 Testing Israeli News Video Generation")
    print(f"📝 Topic: {topic}")
    print(f"⏱️ Duration: {duration} seconds")
    print(f"📱 Platform: {platform.value}")
    print(f"🎭 Category: {category.value}")
    
    try:
        # Create video generator
        generator = VideoGenerator(
            api_key=os.getenv('GOOGLE_AI_API_KEY'),
            use_real_veo2=True
        )
        
        # Create configuration with explicit topic
        config = GeneratedVideoConfig(
            target_platform=platform,
            category=category,
            duration_seconds=duration,
            topic=topic,  # Explicit topic
            style='viral',
            tone='funny',
            target_audience='18-34 viral content consumers',
            hook='Stop scrolling! You won\'t believe this Israeli news...',
            main_content=[
                f"Funny and lighthearted news stories from Israel",
                f"Humorous take on Israeli daily life and culture",
                f"Comedic perspective on Israeli current events"
            ],
            call_to_action='Follow for more funny Israeli content!',
            visual_style='dynamic',
            color_scheme=['#FF6B6B', '#4ECDC4', '#FFFFFF'],
            text_overlays=[],
            transitions=['fade', 'slide'],
            background_music_style='upbeat',
            voiceover_style='natural',
            sound_effects=[],
            inspired_by_videos=[],
            predicted_viral_score=0.85,
            frame_continuity=True,
            image_only_mode=True  # Use image mode for reliability
        )
        
        print(f"📊 Configuration created successfully")
        print(f"🎯 Topic in config: {config.topic}")
        
        # Generate video
        print(f"🚀 Starting video generation...")
        result = generator.generate_video(config)
        
        if result and result.success:
            print(f"✅ Video generation successful!")
            print(f"📁 Video file: {result.file_path}")
            print(f"📝 Script: {result.script[:100]}...")
            
            # Check if script is about the correct topic
            if "israeli" in result.script.lower() or "israel" in result.script.lower():
                print(f"✅ Script contains Israeli content")
            else:
                print(f"❌ Script does NOT contain Israeli content")
                print(f"📝 Full script: {result.script}")
            
            # Check session folder for agent discussions
            session_folder = os.path.dirname(result.file_path)
            print(f"📁 Session folder: {session_folder}")
            
            # List all files in session folder
            if os.path.exists(session_folder):
                files = os.listdir(session_folder)
                print(f"📄 Files in session folder:")
                for file in files:
                    print(f"   - {file}")
                
                # Check for agent discussions
                discussion_files = [f for f in files if 'discussion' in f.lower() or 'agent' in f.lower()]
                if discussion_files:
                    print(f"✅ Found agent discussion files: {discussion_files}")
                else:
                    print(f"❌ No agent discussion files found")
            
            # Check video duration
            if hasattr(result, 'duration'):
                print(f"⏱️ Video duration: {result.duration} seconds")
                if abs(result.duration - duration) <= 2:  # Allow 2 second tolerance
                    print(f"✅ Duration is correct")
                else:
                    print(f"❌ Duration mismatch: expected {duration}s, got {result.duration}s")
            
            # Check for audio file
            audio_files = [f for f in files if f.endswith('.mp3') or f.endswith('.wav')]
            if audio_files:
                print(f"✅ Found audio files: {audio_files}")
            else:
                print(f"❌ No audio files found")
            
            return True
            
        else:
            print(f"❌ Video generation failed")
            if result:
                print(f"Error: {result.error}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_agent_discussions():
    """Test with agent discussions enabled"""
    
    print(f"\n🤖 Testing with Agent Discussions")
    
    try:
        # Import the discussion-enhanced orchestrator
        from agents.enhanced_orchestrator_with_discussions import create_discussion_enhanced_orchestrator
        
        # Create orchestrator
        orchestrator = create_discussion_enhanced_orchestrator(
            api_key=os.getenv('GOOGLE_AI_API_KEY'),
            topic="funny news from israel",
            category="comedy",
            platform="youtube",
            duration=15,
            discussion_mode="standard"
        )
        
        # Configuration
        config = {
            'image_only': True,
            'use_real_veo2': True,
            'enable_discussions': True
        }
        
        print(f"🚀 Starting orchestrated generation with discussions...")
        result = orchestrator.orchestrate_complete_generation(config)
        
        if result.get('success'):
            print(f"✅ Orchestrated generation successful!")
            print(f"📁 Video file: {result.get('final_video_path')}")
            
            # Check discussion results
            discussions = result.get('discussion_results', {})
            print(f"💬 Discussions conducted: {len(discussions)}")
            
            for topic, discussion in discussions.items():
                print(f"   - {topic}: {discussion.consensus_level:.2f} consensus")
            
            # Check if discussions are saved in session folder
            session_id = result.get('session_id')
            if session_id:
                session_folder = f"outputs/orchestrated_session_{session_id}"
                if os.path.exists(session_folder):
                    files = os.listdir(session_folder)
                    print(f"📁 Orchestrated session files: {files}")
                    
                    # Check for discussion summary
                    summary_file = os.path.join(session_folder, "agent_discussions_summary.json")
                    if os.path.exists(summary_file):
                        print(f"✅ Found discussion summary file")
                        with open(summary_file, 'r') as f:
                            summary = json.load(f)
                            print(f"📊 Discussion summary:")
                            print(f"   - Topic: {summary.get('topic')}")
                            print(f"   - Total discussions: {summary.get('discussion_configuration', {}).get('total_discussions')}")
                            print(f"   - Average consensus: {summary.get('overall_metrics', {}).get('average_consensus')}")
                    else:
                        print(f"❌ Discussion summary file not found")
                else:
                    print(f"❌ Orchestrated session folder not found: {session_folder}")
            
            return True
            
        else:
            print(f"❌ Orchestrated generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Agent discussion test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print(f"🎬 Israeli News Video Generation Fix Test")
    print(f"=" * 50)
    
    # Check API key
    if not os.getenv('GOOGLE_AI_API_KEY'):
        print(f"❌ GOOGLE_AI_API_KEY environment variable not set")
        sys.exit(1)
    
    # Test 1: Basic video generation
    print(f"\n🧪 Test 1: Basic Video Generation")
    success1 = test_israeli_news_generation()
    
    # Test 2: With agent discussions
    print(f"\n🧪 Test 2: With Agent Discussions")
    success2 = test_with_agent_discussions()
    
    # Summary
    print(f"\n📊 Test Summary")
    print(f"=" * 50)
    print(f"Basic Generation: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Agent Discussions: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print(f"🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"❌ Some tests failed")
        sys.exit(1) 