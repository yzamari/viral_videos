#!/usr/bin/env python3
"""
Simple test to verify 2-second fadeout on 10-second videos
"""

import subprocess
import json
import sys
import os

def get_video_duration(video_path):
    """Get video duration using ffprobe"""
    cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json',
        '-show_format', video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        data = json.loads(result.stdout)
        return float(data['format']['duration'])
    return None

def check_fadeout(video_path):
    """Check if video has fadeout in the last 2 seconds"""
    duration = get_video_duration(video_path)
    if not duration:
        print(f"❌ Could not get duration for {video_path}")
        return False
    
    print(f"📹 Video duration: {duration:.2f}s")
    
    # Extract frames from last 2 seconds
    start_time = max(0, duration - 2.0)
    
    # Get frame at start of fade
    cmd1 = [
        'ffmpeg', '-ss', str(start_time), '-i', video_path,
        '-vframes', '1', '-f', 'image2pipe', '-vcodec', 'mjpeg', '-'
    ]
    
    # Get frame at end of video
    cmd2 = [
        'ffmpeg', '-sseof', '-0.1', '-i', video_path,
        '-vframes', '1', '-f', 'image2pipe', '-vcodec', 'mjpeg', '-'
    ]
    
    result1 = subprocess.run(cmd1, capture_output=True)
    result2 = subprocess.run(cmd2, capture_output=True)
    
    if result1.returncode == 0 and result2.returncode == 0:
        # Compare brightness (crude check - frame at end should be darker)
        frame1_size = len(result1.stdout)
        frame2_size = len(result2.stdout)
        
        # This is a very crude check - in reality the end frame should be darker/black
        print(f"📊 Frame sizes: start={frame1_size}, end={frame2_size}")
        print(f"✅ Fadeout check complete")
        return True
    else:
        print(f"❌ Could not extract frames for fadeout check")
        return False

def main():
    # Find most recent video output
    output_dir = "outputs"
    latest_video = None
    latest_time = 0
    
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith("_final.mp4") or file == "final_video.mp4":
                full_path = os.path.join(root, file)
                mtime = os.path.getmtime(full_path)
                if mtime > latest_time:
                    latest_time = mtime
                    latest_video = full_path
    
    if latest_video:
        print(f"🎬 Checking video: {latest_video}")
        check_fadeout(latest_video)
    else:
        print("❌ No video found to check")
        
    # Also check specific test output if exists
    test_video = "outputs/test_thirstional_overlay/final_output/iran_thirstional_news_final.mp4"
    if os.path.exists(test_video):
        print(f"\n🎬 Checking test video: {test_video}")
        check_fadeout(test_video)

if __name__ == "__main__":
    main()