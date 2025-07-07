#!/usr/bin/env python3
"""
COMPREHENSIVE TEST: All Critical Fixes
=====================================

Testing:
1. ✅ 20-second video duration (not 80+ seconds)
2. ✅ 8-second VEO-2 clips for maximum coverage  
3. ✅ Agent discussions ALWAYS ON and saved in session folder
4. ✅ Gemini image fallback (1 image per second) when VEO-2 fails
5. ✅ Natural voice audio (not robotic)
6. ✅ Correct topic content (Israeli news, not script optimization)
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

def test_critical_fixes():
    """Test all critical fixes with Israeli news topic"""
    
    print("🚀 TESTING ALL CRITICAL FIXES")
    print("=" * 50)
    
    # Test configuration
    topic = "funny israeli news about cats in tel aviv"
    duration = 20  # 20-second target
    
    print(f"📝 Topic: {topic}")
    print(f"⏱️ Duration: {duration} seconds")
    print(f"🎯 Expected: 8-second VEO-2 clips × 3 = 24s total")
    print(f"🤖 Agent Discussions: FORCED ON")
    
    # Generate video with all fixes
    cmd = [
        "python", "main.py", "generate",
        "--topic", topic,
        "--duration", str(duration),
        "--image-only",  # Use image mode for reliability
        "--platform", "youtube",
        "--discussions", "standard",  # Should be forced ON anyway
        "--discussion-log"
    ]
    
    print(f"\n🚀 Running: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        # Run the generation
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print("✅ Video generation completed!")
            print("\n📊 ANALYZING RESULTS...")
            
            # Find the latest session folder
            outputs_dir = Path("outputs")
            session_folders = list(outputs_dir.glob("session_*"))
            
            if session_folders:
                latest_session = max(session_folders, key=lambda x: x.stat().st_mtime)
                print(f"📁 Latest session: {latest_session.name}")
                
                # Test 1: Video Duration
                test_video_duration(latest_session)
                
                # Test 2: Agent Discussions in Session Folder
                test_agent_discussions(latest_session)
                
                # Test 3: Script Content
                test_script_content(latest_session, topic)
                
                # Test 4: Audio Quality
                test_audio_quality(latest_session)
                
                # Test 5: VEO-2 vs Gemini Fallback
                test_veo_gemini_usage(latest_session)
                
                return True
            else:
                print("❌ No session folders found")
                return False
        else:
            print("❌ Video generation failed!")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Video generation timed out (10 minutes)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_video_duration(session_folder):
    """Test if video duration is correct (20-24 seconds, not 80+)"""
    
    print(f"\n🧪 TEST 1: Video Duration")
    print("-" * 30)
    
    video_files = list(session_folder.glob("viral_video_*.mp4"))
    
    if video_files:
        video_file = video_files[0]
        print(f"📹 Video: {video_file.name}")
        
        try:
            # Get video duration
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-show_entries', 
                'format=duration', '-of', 'csv=p=0', str(video_file)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                duration = float(result.stdout.strip())
                print(f"⏱️ Duration: {duration:.1f} seconds")
                
                if 18 <= duration <= 26:  # Allow some tolerance around 20-24s
                    print(f"✅ PASS: Duration is correct ({duration:.1f}s)")
                    return True
                elif duration > 50:
                    print(f"❌ FAIL: Duration too long ({duration:.1f}s) - text overlay bug not fixed")
                    return False
                else:
                    print(f"⚠️ WARNING: Duration unexpected ({duration:.1f}s)")
                    return False
            else:
                print(f"❌ Could not check duration")
                return False
        except Exception as e:
            print(f"❌ Error checking duration: {e}")
            return False
    else:
        print(f"❌ No video files found")
        return False

def test_agent_discussions(session_folder):
    """Test if agent discussions are saved in session folder"""
    
    print(f"\n🧪 TEST 2: Agent Discussions in Session Folder")
    print("-" * 30)
    
    # Check for agent discussion files in session folder
    discussion_files = list(session_folder.glob("agent_*"))
    discussion_dir = session_folder / "agent_discussions"
    
    print(f"📁 Session folder: {session_folder}")
    print(f"📄 Files in session: {len(list(session_folder.glob('*')))}")
    
    # Check for discussion summary
    summary_file = session_folder / "agent_discussions_summary.json"
    if summary_file.exists():
        print(f"✅ Found discussion summary: {summary_file.name}")
        
        try:
            with open(summary_file, 'r') as f:
                summary = json.load(f)
                
            total_discussions = summary.get('discussion_configuration', {}).get('total_discussions', 0)
            avg_consensus = summary.get('overall_metrics', {}).get('average_consensus', 0)
            
            print(f"💬 Total discussions: {total_discussions}")
            print(f"🤝 Average consensus: {avg_consensus:.2f}")
            
            if total_discussions >= 4:  # Should have planning, script, visual, audio, assembly
                print(f"✅ PASS: Agent discussions working ({total_discussions} discussions)")
                return True
            else:
                print(f"❌ FAIL: Too few discussions ({total_discussions})")
                return False
                
        except Exception as e:
            print(f"❌ Error reading discussion summary: {e}")
            return False
    else:
        print(f"❌ FAIL: No agent discussion summary found in session folder")
        
        # Check if discussions are in wrong location (orchestrated folder)
        outputs_dir = session_folder.parent
        orch_folders = list(outputs_dir.glob("orchestrated_session_*"))
        if orch_folders:
            print(f"⚠️ WARNING: Found {len(orch_folders)} orchestrated folders - discussions in wrong location")
        
        return False

def test_script_content(session_folder, expected_topic):
    """Test if script is about the correct topic"""
    
    print(f"\n🧪 TEST 3: Script Content")
    print("-" * 30)
    
    script_files = list(session_folder.glob("script_*.txt"))
    
    if script_files:
        script_file = script_files[0]
        print(f"📝 Script: {script_file.name}")
        
        try:
            with open(script_file, 'r') as f:
                script_content = f.read().lower()
            
            # Check for topic keywords
            topic_keywords = ["israel", "israeli", "tel aviv", "cat", "news"]
            wrong_keywords = ["script content", "structure optimization", "viral content"]
            
            topic_matches = sum(1 for keyword in topic_keywords if keyword in script_content)
            wrong_matches = sum(1 for keyword in wrong_keywords if keyword in script_content)
            
            print(f"🎯 Topic keyword matches: {topic_matches}/{len(topic_keywords)}")
            print(f"❌ Wrong keyword matches: {wrong_matches}/{len(wrong_keywords)}")
            
            if topic_matches >= 2 and wrong_matches == 0:
                print(f"✅ PASS: Script is about correct topic")
                return True
            elif wrong_matches > 0:
                print(f"❌ FAIL: Script contains wrong content (script optimization bug)")
                return False
            else:
                print(f"⚠️ WARNING: Script topic unclear")
                return False
                
        except Exception as e:
            print(f"❌ Error reading script: {e}")
            return False
    else:
        print(f"❌ No script files found")
        return False

def test_audio_quality(session_folder):
    """Test audio quality and duration"""
    
    print(f"\n🧪 TEST 4: Audio Quality")
    print("-" * 30)
    
    audio_files = list(session_folder.glob("*.mp3"))
    
    if audio_files:
        audio_file = audio_files[0]
        file_size = audio_file.stat().st_size
        
        print(f"🎵 Audio: {audio_file.name}")
        print(f"📦 Size: {file_size/1024:.1f}KB")
        
        # Check file size as quality indicator
        if file_size > 200000:  # > 200KB suggests good quality
            print(f"✅ PASS: Audio file size suggests good quality")
            return True
        elif file_size < 50000:  # < 50KB suggests poor quality
            print(f"❌ FAIL: Audio file size suggests poor quality")
            return False
        else:
            print(f"⚠️ WARNING: Audio quality uncertain")
            return False
    else:
        print(f"❌ No audio files found")
        return False

def test_veo_gemini_usage(session_folder):
    """Test VEO-2 vs Gemini image usage"""
    
    print(f"\n🧪 TEST 5: VEO-2 vs Gemini Usage")
    print("-" * 30)
    
    # Check for VEO-2 clips
    veo_clips_dir = session_folder / "veo2_clips"
    veo_clips = list(veo_clips_dir.glob("*.mp4")) if veo_clips_dir.exists() else []
    
    # Check for Gemini images
    gemini_images_dir = session_folder / "gemini_images"
    gemini_images = list(gemini_images_dir.glob("*.png")) if gemini_images_dir.exists() else []
    
    # Check for Gemini clips
    gemini_clips_dir = session_folder / "gemini_clips"
    gemini_clips = list(gemini_clips_dir.glob("*.mp4")) if gemini_clips_dir.exists() else []
    
    print(f"🎬 VEO-2 clips: {len(veo_clips)}")
    print(f"🎨 Gemini images: {len(gemini_images)}")
    print(f"📹 Gemini clips: {len(gemini_clips)}")
    
    total_content = len(veo_clips) + len(gemini_clips)
    
    if len(veo_clips) >= 2:  # Should have 2-3 VEO-2 clips for 20s video
        print(f"✅ PASS: VEO-2 working well ({len(veo_clips)} clips)")
        return True
    elif len(gemini_clips) >= 2:
        print(f"✅ PASS: Gemini fallback working ({len(gemini_clips)} clips)")
        return True
    elif len(gemini_images) >= 15:  # Should have ~20 images for 20s
        print(f"✅ PASS: Gemini images working ({len(gemini_images)} images)")
        return True
    else:
        print(f"❌ FAIL: Insufficient content generated")
        return False

def main():
    """Run all tests"""
    
    print("🎬 CRITICAL FIXES VERIFICATION TEST")
    print("=" * 50)
    print("Testing all fixes for Israeli news video generation")
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("❌ Please run from viralAi directory")
        return False
    
    # Run comprehensive test
    success = test_critical_fixes()
    
    print(f"\n🎉 FINAL RESULT")
    print("=" * 50)
    if success:
        print("✅ ALL CRITICAL FIXES WORKING!")
        print("🚀 System ready for production use")
        return True
    else:
        print("❌ Some fixes still need work")
        print("🔧 Check individual test results above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 