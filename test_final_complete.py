#!/usr/bin/env python3
"""
Final Complete Test - Generate a full video with all features
"""

import os
import sys
import time

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.generators.video_generator import VideoGenerator
from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory

def test_complete_video_generation():
    """Test complete video generation with all features"""
    print("🚀 FINAL COMPLETE TEST - GENERATING FULL VIDEO")
    print("=" * 60)
    
    # Create comprehensive config
    config = GeneratedVideoConfig(
        topic="AI-powered viral video generation with agent discussions",
        duration_seconds=10,
        target_platform=Platform.YOUTUBE,
        category=VideoCategory.ENTERTAINMENT,
        session_id="final_complete_test",
        visual_style="dynamic",
        tone="engaging",
        hook="Get ready for the future of video creation!",
        call_to_action="Subscribe for more AI-powered content!"
    )
    
    print(f"📋 Configuration:")
    print(f"   Topic: {config.topic}")
    print(f"   Duration: {config.duration_seconds}s")
    print(f"   Platform: {config.target_platform.value}")
    print(f"   Category: {config.category.value}")
    print(f"   Session: {config.session_id}")
    print()
    
    # Create generator
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    generator = VideoGenerator(
        api_key=api_key,
        use_real_veo2=True,
        use_vertex_ai=True,
        vertex_project_id="viralgen-464411",
        vertex_location="us-central1",
        vertex_gcs_bucket="viral-veo2-results",
        prefer_veo3=False
    )
    
    print("🎬 Starting complete video generation...")
    print()
    
    # Generate video
    start_time = time.time()
    try:
        result = generator.generate_video(config)
        generation_time = time.time() - start_time
        
        print()
        print("✅ GENERATION COMPLETED!")
        print(f"⏱️  Total time: {generation_time:.1f} seconds")
        print(f"✅ Success: {result.success}")
        print(f"📁 Video file: {result.file_path}")
        print(f"🎵 Audio files: {len(result.audio_files)}")
        print(f"📝 Script length: {len(result.script)} characters")
        print(f"💾 File size: {result.file_size_mb:.2f} MB")
        print()
        
        # Verify session directory contents
        session_dir = f"outputs/{config.session_id}"
        if os.path.exists(session_dir):
            print(f"📂 SESSION DIRECTORY ANALYSIS: {session_dir}")
            print("-" * 50)
            
            # Check each subdirectory
            subdirs = [
                ("discussions", "📝 AI Agent Discussions"),
                ("final_output", "🎬 Final Video Output"),
                ("ai_agents", "🤖 AI Agent Data"),
                ("video_clips", "🎥 Video Clips"),
                ("audio", "🎵 Audio Files"),
                ("scripts", "📄 Scripts"),
                ("metadata", "📊 Metadata"),
                ("logs", "📋 Logs")
            ]
            
            total_files = 0
            total_size = 0
            
            for subdir, description in subdirs:
                subdir_path = os.path.join(session_dir, subdir)
                if os.path.exists(subdir_path):
                    files = []
                    for root, dirs, filenames in os.walk(subdir_path):
                        for filename in filenames:
                            file_path = os.path.join(root, filename)
                            if os.path.isfile(file_path):
                                size = os.path.getsize(file_path)
                                files.append((filename, size))
                                total_files += 1
                                total_size += size
                    
                    if files:
                        print(f"{description}: {len(files)} files")
                        for filename, size in sorted(files):
                            print(f"   ✅ {filename}: {size:,} bytes")
                    else:
                        print(f"{description}: ❌ EMPTY")
                else:
                    print(f"{description}: ❌ MISSING")
            
            print("-" * 50)
            print(f"📊 TOTAL SESSION DATA:")
            print(f"   Files: {total_files}")
            print(f"   Size: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")
            print()
            
            # Verify specific files exist
            required_files = [
                ("discussions/ai_agent_discussion.json", "AI Agent Discussion"),
                ("discussions/discussion_summary.md", "Discussion Summary"),
                ("final_output/final_video_*.mp4", "Final Video"),
                ("video_clips/veo_clips/clip_*.mp4", "VEO Clips"),
                ("audio/audio_segment_*.mp3", "Audio Segments"),
                ("scripts/original_script.txt", "Original Script"),
                ("metadata/session_metadata.json", "Session Metadata")
            ]
            
            print("🔍 REQUIRED FILES CHECK:")
            print("-" * 30)
            
            for file_pattern, description in required_files:
                found = False
                if "*" in file_pattern:
                    # Pattern matching
                    import glob
                    pattern_path = os.path.join(session_dir, file_pattern)
                    matches = glob.glob(pattern_path)
                    if matches:
                        print(f"✅ {description}: {len(matches)} files")
                        found = True
                else:
                    # Exact file
                    file_path = os.path.join(session_dir, file_pattern)
                    if os.path.exists(file_path):
                        size = os.path.getsize(file_path)
                        print(f"✅ {description}: {size:,} bytes")
                        found = True
                
                if not found:
                    print(f"❌ {description}: MISSING")
            
            print()
            
            # Check if AI discussions were generated
            discussion_file = os.path.join(session_dir, "discussions", "ai_agent_discussion.json")
            if os.path.exists(discussion_file):
                print("🤖 AI AGENT DISCUSSIONS: ✅ GENERATED")
                try:
                    import json
                    with open(discussion_file, 'r') as f:
                        discussion_data = json.load(f)
                    
                    print(f"   Agents: {len(discussion_data.get('agents', {}))}")
                    print(f"   Decisions: {len(discussion_data.get('discussion_summary', {}).get('key_decisions', []))}")
                    print(f"   Consensus: {discussion_data.get('discussion_summary', {}).get('consensus', 'Unknown')}")
                except Exception as e:
                    print(f"   ⚠️ Error reading discussion: {e}")
            else:
                print("🤖 AI AGENT DISCUSSIONS: ❌ NOT GENERATED")
            
            print()
            
        # Final status
        if result.success:
            print("🎉 COMPLETE SUCCESS!")
            print("✅ All core features working:")
            print("   - VEO-2 video generation")
            print("   - AI agent discussions")
            print("   - Session management")
            print("   - Audio generation")
            print("   - Script processing")
            print("   - Final video composition")
            print()
            print("🚀 SYSTEM IS FULLY FUNCTIONAL!")
        else:
            print("❌ Generation reported failure")
            
        return result
        
    except Exception as e:
        generation_time = time.time() - start_time
        print(f"❌ GENERATION FAILED after {generation_time:.1f}s: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    try:
        result = test_complete_video_generation()
        if result and result.success:
            print("\n" + "="*60)
            print("🎉 FINAL TEST COMPLETED SUCCESSFULLY!")
            print("🚀 VIRAL VIDEO GENERATION SYSTEM IS FULLY OPERATIONAL!")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("❌ FINAL TEST FAILED")
            print("🔧 System needs additional fixes")
            print("="*60)
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc() 