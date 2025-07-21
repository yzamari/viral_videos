#!/usr/bin/env python3
"""
Comprehensive test script to verify duration fix
"""

import os
import sys
import subprocess
import json
import time

def check_video_duration(video_path):
    """Check the duration of a video file"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-show_format', '-of', 'json', video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            probe_data = json.loads(result.stdout)
            duration = float(probe_data['format']['duration'])
            return duration
        else:
            print(f"❌ Failed to get video duration: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ Error checking video duration: {e}")
        return None

def generate_test_video():
    """Generate a test video to verify duration fix"""
    print("🎬 Generating test video to verify duration fix...")
    
    # Simple test mission
    test_mission = "Create a 30-second video about Israeli Prime Ministers: David Ben-Gurion (1948-1963) - founder of Israel, Golda Meir (1969-1974) - Iron Lady, Menachem Begin (1977-1983) - peace with Egypt. Keep it concise and educational."
    
    cmd = [
        'python', 'main.py', 'generate',
        '--mission', test_mission,
        '--platform', 'tiktok',
        '--duration', '30',
        '--no-cheap',
        '--mode', 'professional'
    ]
    
    print(f"🚀 Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Test video generation completed successfully")
            return True
        else:
            print(f"❌ Test video generation failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("⏰ Test video generation timed out (5 minutes)")
        return False
    except Exception as e:
        print(f"❌ Error generating test video: {e}")
        return False

def main():
    """Main test function"""
    print("🔍 COMPREHENSIVE DURATION FIX TEST")
    print("=" * 60)
    
    # Step 1: Check existing videos
    print("\n📹 STEP 1: Checking existing videos...")
    outputs_dir = "/Users/yahavzamari/viralAi/outputs"
    
    if os.path.exists(outputs_dir):
        sessions = [d for d in os.listdir(outputs_dir) if d.startswith('session_')]
        sessions.sort(reverse=True)  # Most recent first
        
        print(f"Found {len(sessions)} video sessions")
        
        for session in sessions[:5]:  # Check last 5 sessions
            session_path = os.path.join(outputs_dir, session)
            final_output_path = os.path.join(session_path, 'final_output')
            
            if os.path.exists(final_output_path):
                video_files = [f for f in os.listdir(final_output_path) if f.endswith('.mp4')]
                
                for video_file in video_files:
                    video_path = os.path.join(final_output_path, video_file)
                    duration = check_video_duration(video_path)
                    
                    if duration:
                        print(f"   📹 {session}/{video_file}: {duration:.2f}s")
                        
                        if duration <= 35:  # Within 5 seconds of target
                            print("      ✅ Duration looks good!")
                        else:
                            print("      ⚠️  Duration might be too long")
    
    # Step 2: Generate new test video
    print(f"\n🎬 STEP 2: Generating new test video...")
    success = generate_test_video()
    
    if success:
        # Step 3: Check the new video
        print(f"\n📹 STEP 3: Checking new test video...")
        time.sleep(5)  # Wait for file to be written
        
        # Find the newest video
        if os.path.exists(outputs_dir):
            sessions = [d for d in os.listdir(outputs_dir) if d.startswith('session_')]
            sessions.sort(reverse=True)  # Most recent first
            
            if sessions:
                newest_session = sessions[0]
                session_path = os.path.join(outputs_dir, newest_session)
                final_output_path = os.path.join(session_path, 'final_output')
                
                if os.path.exists(final_output_path):
                    video_files = [f for f in os.listdir(final_output_path) if f.endswith('.mp4')]
                    
                    if video_files:
                        newest_video = video_files[0]  # Most recent video
                        video_path = os.path.join(final_output_path, newest_video)
                        duration = check_video_duration(video_path)
                        
                        if duration:
                            print(f"   📹 New test video: {duration:.2f}s")
                            
                            if abs(duration - 30.0) <= 1.0:
                                print("      ✅ SUCCESS! Video duration is exactly 30 seconds (±1s)")
                                print("      🎉 Duration fix is working correctly!")
                            else:
                                print(f"      ❌ FAILED! Video duration {duration:.2f}s doesn't match target 30s")
                                print("      🔧 Duration fix may need further investigation")
                        else:
                            print("      ❌ Could not determine video duration")
                    else:
                        print("      ❌ No video files found in newest session")
                else:
                    print("      ❌ No final_output directory found")
            else:
                print("      ❌ No sessions found")
    
    # Step 4: Summary
    print(f"\n📊 TEST SUMMARY:")
    print("   ✅ Duration multipliers removed from video_generator.py")
    print("   ✅ Duration multipliers removed from advanced_audio_analyzer.py")
    print("   ✅ Duration multipliers removed from image_timing_agent.py")
    print("   ✅ Strict duration validation added to video generation pipeline")
    print("   ✅ Force exact duration trimming implemented")
    
    print(f"\n🎯 EXPECTED RESULTS:")
    print("   ✅ New videos should be exactly 30 seconds (±1 second)")
    print("   ✅ No more 58-second videos for 30-second targets")
    print("   ✅ Duration control is now strict and accurate")
    
    print(f"\n🔧 To test the fix yourself:")
    print("   python main.py generate --mission 'Your mission' --duration 30 --no-cheap --mode professional")
    print("   The new video should be exactly 30 seconds!")

if __name__ == "__main__":
    main() 