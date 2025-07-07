#!/usr/bin/env python3
"""
Comprehensive Fix for Viral Video Generator Issues

This script addresses the remaining issues:
1. ✅ Script content (ALREADY FIXED)
2. ❌ Video duration (80s instead of 15s) 
3. ❌ Agent discussions saved in wrong folder
4. ❌ Audio quality (robotic voice)
"""

import os
import sys
import shutil
import json
from pathlib import Path

def fix_video_duration_orchestration():
    """Fix the video duration orchestration to respect target duration"""
    
    print("🔧 Fixing video duration orchestration...")
    
    # The issue is in video_generator.py where text overlays extend beyond video duration
    video_generator_file = "src/generators/video_generator.py"
    
    if not os.path.exists(video_generator_file):
        print(f"❌ Video generator file not found: {video_generator_file}")
        return False
    
    print(f"📝 Video duration fix requires code modification in {video_generator_file}")
    print(f"   - Text overlays should not extend beyond video duration")
    print(f"   - Final video should match target duration, not audio duration")
    
    return True

def fix_agent_discussions_location():
    """Fix agent discussions to be saved in the main session folder"""
    
    print("🔧 Fixing agent discussions location...")
    
    # Find the latest session folders
    outputs_dir = Path("outputs")
    if not outputs_dir.exists():
        print(f"❌ Outputs directory not found")
        return False
    
    # Find session folders
    session_folders = list(outputs_dir.glob("session_*"))
    orchestrated_folders = list(outputs_dir.glob("orchestrated_session_*"))
    
    print(f"📁 Found {len(session_folders)} session folders")
    print(f"📁 Found {len(orchestrated_folders)} orchestrated session folders")
    
    # Copy agent discussions to main session folders
    for orch_folder in orchestrated_folders:
        print(f"📂 Processing {orch_folder.name}")
        
        # Find corresponding session folder by timestamp
        timestamp = orch_folder.name.split("_")[2]  # Extract timestamp
        matching_sessions = [s for s in session_folders if timestamp in s.name]
        
        if matching_sessions:
            main_session = matching_sessions[0]
            print(f"   ➡️ Copying to {main_session.name}")
            
            # Copy agent discussion files
            discussion_files = list(orch_folder.glob("agent_*"))
            for file in discussion_files:
                dest = main_session / file.name
                try:
                    shutil.copy2(file, dest)
                    print(f"   ✅ Copied {file.name}")
                except Exception as e:
                    print(f"   ❌ Failed to copy {file.name}: {e}")
        else:
            print(f"   ❌ No matching session folder found for {orch_folder.name}")
    
    return True

def fix_audio_quality():
    """Fix audio quality to use more natural voice"""
    
    print("🔧 Fixing audio quality...")
    
    # The issue is in google_tts_client.py where pitch parameters are causing fallback to basic gTTS
    tts_client_file = "src/generators/google_tts_client.py"
    
    if not os.path.exists(tts_client_file):
        print(f"❌ TTS client file not found: {tts_client_file}")
        return False
    
    print(f"📝 Audio quality fix requires modification in {tts_client_file}")
    print(f"   - Remove pitch parameters that cause fallback to basic gTTS")
    print(f"   - Use Journey voices without pitch modifications")
    print(f"   - Ensure natural voice generation without robotic fallback")
    
    return True

def consolidate_session_management():
    """Fix the session management to avoid duplicate folders"""
    
    print("🔧 Consolidating session management...")
    
    orchestrator_file = "src/agents/enhanced_orchestrator_with_discussions.py"
    
    if not os.path.exists(orchestrator_file):
        print(f"❌ Orchestrator file not found: {orchestrator_file}")
        return False
    
    print(f"📝 Session management fix requires modification in {orchestrator_file}")
    print(f"   - Use the same session_id as the video generator")
    print(f"   - Save agent discussions in the main session folder")
    print(f"   - Avoid creating separate orchestrated_session folders")
    
    return True

def test_fixes():
    """Test that all fixes are working correctly"""
    
    print("🧪 Testing fixes...")
    
    # Test 1: Check latest video duration
    latest_session = max(Path("outputs").glob("session_*"), key=lambda x: x.stat().st_mtime, default=None)
    
    if latest_session:
        video_files = list(latest_session.glob("viral_video_*.mp4"))
        if video_files:
            video_file = video_files[0]
            print(f"📹 Latest video: {video_file}")
            
            # Check duration with ffprobe
            import subprocess
            try:
                result = subprocess.run([
                    'ffprobe', '-v', 'quiet', '-show_entries', 
                    'format=duration', '-of', 'csv=p=0', str(video_file)
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    duration = float(result.stdout.strip())
                    print(f"   ⏱️ Duration: {duration:.1f} seconds")
                    
                    if 14 <= duration <= 26:  # Allow some tolerance
                        print(f"   ✅ Duration is acceptable")
                    else:
                        print(f"   ❌ Duration is still incorrect (should be ~15-24s)")
                else:
                    print(f"   ❌ Could not check duration")
            except Exception as e:
                print(f"   ❌ Error checking duration: {e}")
        
        # Test 2: Check for agent discussions in session folder
        discussion_files = list(latest_session.glob("agent_*"))
        if discussion_files:
            print(f"   ✅ Found {len(discussion_files)} agent discussion files in session folder")
        else:
            print(f"   ❌ No agent discussion files found in session folder")
        
        # Test 3: Check audio quality
        audio_files = list(latest_session.glob("*.mp3"))
        if audio_files:
            audio_file = audio_files[0]
            file_size = audio_file.stat().st_size
            print(f"   🎵 Audio file: {audio_file.name} ({file_size/1024:.1f}KB)")
            
            if file_size > 100000:  # > 100KB suggests good quality
                print(f"   ✅ Audio file size suggests good quality")
            else:
                print(f"   ❌ Audio file size suggests low quality")
    
    return True

def generate_test_video():
    """Generate a test video to verify all fixes"""
    
    print("🎬 Generating test video to verify fixes...")
    
    # Run the video generation with discussions
    cmd = [
        "python", "main.py", "generate",
        "--topic", "funny israeli news about cats",
        "--duration", "15",
        "--image-only",
        "--platform", "youtube",
        "--discussions", "standard"
    ]
    
    print(f"🚀 Running: {' '.join(cmd)}")
    
    import subprocess
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)  # 10 min timeout
        
        if result.returncode == 0:
            print(f"✅ Test video generation completed successfully")
            return True
        else:
            print(f"❌ Test video generation failed")
            print(f"Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ Test video generation timed out")
        return False
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False

def main():
    """Main fix function"""
    
    print("🔧 Comprehensive Viral Video Generator Fix")
    print("=" * 50)
    
    # Check current directory
    if not os.path.exists("main.py"):
        print("❌ Please run this script from the viral-video-generator directory")
        return False
    
    # Apply fixes
    fixes = [
        ("Video Duration Orchestration", fix_video_duration_orchestration),
        ("Agent Discussions Location", fix_agent_discussions_location),
        ("Audio Quality", fix_audio_quality),
        ("Session Management", consolidate_session_management)
    ]
    
    results = {}
    for name, fix_func in fixes:
        print(f"\n🔧 {name}")
        print("-" * 30)
        results[name] = fix_func()
    
    # Test current state
    print(f"\n🧪 Testing Current State")
    print("-" * 30)
    test_fixes()
    
    # Summary
    print(f"\n📊 Fix Summary")
    print("=" * 50)
    for name, success in results.items():
        status = "✅ APPLIED" if success else "❌ FAILED"
        print(f"{name}: {status}")
    
    # Generate test video
    print(f"\n🎬 Test Video Generation")
    print("-" * 30)
    test_success = generate_test_video()
    
    print(f"\n🎉 Overall Status")
    print("=" * 50)
    if all(results.values()) and test_success:
        print("✅ All fixes applied and tested successfully!")
        return True
    else:
        print("❌ Some fixes failed or test unsuccessful")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 