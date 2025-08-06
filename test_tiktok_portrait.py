#!/usr/bin/env python3
"""Test TikTok portrait video generation"""

import subprocess
import sys
import time

def test_tiktok_video():
    """Test creating a TikTok portrait video"""
    
    print("🎥 Testing TikTok Portrait Video Generation")
    print("=" * 60)
    
    # Command for TikTok portrait video
    cmd = [
        sys.executable, "main.py", "news", "aggregate-enhanced",
        "https://www.ynet.co.il",
        "--languages", "he",
        "--platform", "tiktok",  # This should create 1080x1920 portrait
        "--style", "modern breaking news",
        "--tone", "urgent and professional",
        "--max-stories", "3",  # Less stories for faster generation
        "--duration", "30",  # Shorter video for testing
        "--overlay-style", "modern"
    ]
    
    print("\n📌 Command:")
    print(" ".join(cmd))
    print("\n" + "=" * 60)
    
    start_time = time.time()
    
    try:
        # Run command
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("\n✅ Success! Video created.")
            
            # Extract output path from the output
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if "news_he_tiktok_" in line and ".mp4" in line:
                    print(f"\n📹 Output: {line.strip()}")
            
            # Check dimensions of the output
            import os
            import json
            
            # Find the latest session
            sessions = sorted([d for d in os.listdir("outputs") if d.startswith("session_")])
            if sessions:
                latest_session = sessions[-1]
                video_files = [f for f in os.listdir(f"outputs/{latest_session}") 
                             if f.endswith(".mp4") and "tiktok" in f]
                
                if video_files:
                    video_path = f"outputs/{latest_session}/{video_files[0]}"
                    
                    # Check dimensions with ffprobe
                    probe_cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", 
                               "-show_streams", video_path]
                    probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
                    
                    if probe_result.returncode == 0:
                        probe_data = json.loads(probe_result.stdout)
                        for stream in probe_data.get("streams", []):
                            if stream.get("codec_type") == "video":
                                width = stream.get("width")
                                height = stream.get("height")
                                print(f"\n📐 Video dimensions: {width}x{height}")
                                
                                if width == 1080 and height == 1920:
                                    print("✅ Correct TikTok portrait dimensions!")
                                else:
                                    print("❌ Wrong dimensions for TikTok!")
                                break
        else:
            print(f"\n❌ Command failed with exit code {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr}")
                
    except subprocess.TimeoutExpired:
        print("\n⏰ Command timed out after 5 minutes")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    elapsed = time.time() - start_time
    print(f"\n⏱️  Total time: {elapsed:.1f} seconds")

if __name__ == "__main__":
    test_tiktok_video()