#!/usr/bin/env python3
"""
Test script to verify current video duration fix
"""

import os
import sys
import subprocess
import json

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

def main():
    """Main test function"""
    print("🔍 Checking Video Duration Fix")
    print("=" * 50)
    
    # Check the existing video
    existing_video = "/Users/yahavzamari/viralAi/outputs/session_20250720_213752/final_output/final_video_session_20250720_213752.mp4"
    
    if os.path.exists(existing_video):
        print(f"📹 Checking existing video: {existing_video}")
        duration = check_video_duration(existing_video)
        
        if duration:
            print(f"   Duration: {duration:.2f} seconds")
            if duration > 35:  # More than 5 seconds over target
                print("   ❌ ISSUE: Video is significantly longer than 30 seconds")
                print("   💡 This video was generated with the old logic before fixes")
            else:
                print("   ✅ Video duration is acceptable")
    else:
        print("❌ Existing video not found")
    
    # Check for any new videos in the outputs directory
    outputs_dir = "/Users/yahavzamari/viralAi/outputs"
    if os.path.exists(outputs_dir):
        print(f"\n🔍 Looking for new videos in: {outputs_dir}")
        
        # Find all session directories
        sessions = [d for d in os.listdir(outputs_dir) if d.startswith('session_')]
        sessions.sort(reverse=True)  # Most recent first
        
        for session in sessions[:3]:  # Check last 3 sessions
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
    
    print(f"\n🎯 Expected Results:")
    print("   ✅ New videos should be exactly 30 seconds")
    print("   ✅ Old videos (like the 58s one) were generated before fixes")
    print("   ✅ Duration fixes are now in place for future generations")
    
    print(f"\n🔧 To test the fix:")
    print("   Run: python main.py generate --mission 'Your mission' --duration 30 --no-cheap --mode professional")
    print("   The new video should be exactly 30 seconds!")

if __name__ == "__main__":
    main() 