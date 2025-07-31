#!/usr/bin/env python3
"""Test script to verify video duration fix"""

import subprocess
import json
import sys
import time

def get_video_duration(video_path):
    """Get video duration using ffprobe"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_streams', video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    return float(stream.get('duration', 0))
        return None
    except Exception as e:
        print(f"Error getting duration: {e}")
        return None

def main():
    print("🔍 Testing video duration fix...")
    print("=" * 60)
    
    # Run a test generation with a specific duration
    test_duration = 30  # seconds
    print(f"🎬 Generating {test_duration}s test video...")
    
    cmd = [
        'python', 'main.py', 'generate',
        '--mission', 'Test video for duration validation',
        '--duration', str(test_duration),
        '--cheap', 'simple',
        '--platform', 'tiktok'
    ]
    
    print(f"📌 Command: {' '.join(cmd)}")
    print("⏳ Running generation...")
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end_time = time.time()
    
    print(f"⏱️ Generation took: {end_time - start_time:.1f} seconds")
    
    if result.returncode != 0:
        print(f"❌ Generation failed: {result.stderr}")
        return 1
    
    # Parse output to find the session directory
    output = result.stdout
    session_id = None
    for line in output.split('\n'):
        if 'Session ID:' in line or 'session_' in line:
            import re
            match = re.search(r'session_\d{8}_\d{6}', line)
            if match:
                session_id = match.group(0)
                break
    
    if not session_id:
        print("❌ Could not find session ID in output")
        print("Output:", output[:500])
        return 1
    
    print(f"✅ Found session: {session_id}")
    
    # Check the final video duration
    import glob
    video_pattern = f"outputs/{session_id}/final_video/*_final.mp4"
    video_files = glob.glob(video_pattern)
    
    if not video_files:
        print(f"❌ No final video found matching: {video_pattern}")
        return 1
    
    final_video = video_files[0]
    print(f"🎥 Checking video: {final_video}")
    
    actual_duration = get_video_duration(final_video)
    if actual_duration is None:
        print("❌ Could not get video duration")
        return 1
    
    print(f"📊 Target duration: {test_duration}s")
    print(f"📊 Actual duration: {actual_duration:.2f}s")
    print(f"📊 Difference: {abs(actual_duration - test_duration):.2f}s")
    
    # Allow 1 second tolerance
    if abs(actual_duration - test_duration) <= 1.0:
        print("✅ Duration is within acceptable range (±1s)")
        return 0
    else:
        print(f"❌ Duration mismatch exceeds tolerance!")
        return 1

if __name__ == "__main__":
    sys.exit(main())