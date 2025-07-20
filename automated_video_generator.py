#!/usr/bin/env python3
"""
Automated Video Generation Script
Generates multiple videos with specified intervals for different platforms
"""

import time
import subprocess
import sys
import os
from datetime import datetime
from typing import List, Dict

# Video generation configurations
VIDEO_CONFIGS = [
    {
        "platform": "youtube",
        "style": "cinematic",
        "duration": 30,
        "description": "YouTube - Cinematic style"
    },
    {
        "platform": "tiktok", 
        "style": "viral",
        "duration": 25,
        "description": "TikTok - Viral style"
    },
    {
        "platform": "instagram",
        "style": "dynamic", 
        "duration": 20,
        "description": "Instagram - Dynamic style"
    },
    {
        "platform": "facebook",
        "style": "professional",
        "duration": 35,
        "description": "Facebook - Professional style"
    },
    {
        "platform": "youtube",
        "style": "educational",
        "duration": 40,
        "description": "YouTube - Educational style"
    }
]

MISSION = "Families day in July 22 2025 in Bajuria. Howitzer vehicles will be shown 10 seconds each."
CATEGORY = "Entertainment"
WAIT_MINUTES = 10

def log_message(message: str):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def wait_minutes(minutes: int):
    """Wait for specified minutes with progress updates"""
    log_message(f"⏳ Waiting {minutes} minutes before next video...")
    
    total_seconds = minutes * 60
    for remaining in range(total_seconds, 0, -30):  # Update every 30 seconds
        mins, secs = divmod(remaining, 60)
        print(f"\r⏱️  Time remaining: {mins:02d}:{secs:02d}", end="", flush=True)
        time.sleep(30 if remaining >= 30 else remaining)
    
    print("\n✅ Wait complete!")

def generate_video(config: Dict, video_num: int) -> bool:
    """Generate a single video with the specified configuration"""
    log_message(f"🎬 Starting Video {video_num}/5: {config['description']}")
    
    # Build command
    cmd = [
        "python", "main.py", "generate",
        "--mission", MISSION,
        "--platform", config["platform"],
        "--category", CATEGORY,
        "--duration", str(config["duration"]),
        "--style", config["style"],
        "--visual-style", config["style"],
        "--tone", "engaging",
        "--mode", "enhanced",
        "--no-cheap",  # Disable cheap mode for premium quality
        "--auto-post",  # Enable auto-posting
        "--skip-auth-test"
    ]
    
    log_message(f"🚀 Executing: {' '.join(cmd)}")
    
    try:
        # Run the video generation command
        result = subprocess.run(
            cmd,
            cwd="/Users/yahavzamari/viralAi",
            capture_output=True,
            text=True,
            timeout=1800  # 30 minute timeout
        )
        
        if result.returncode == 0:
            log_message(f"✅ Video {video_num} completed successfully!")
            log_message(f"📤 Auto-posted to {config['platform']}")
            return True
        else:
            log_message(f"❌ Video {video_num} failed!")
            log_message(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        log_message(f"⏰ Video {video_num} timed out after 30 minutes")
        return False
    except Exception as e:
        log_message(f"💥 Error generating video {video_num}: {e}")
        return False

def main():
    """Main execution function"""
    log_message("🎯 Starting Automated Video Generation")
    log_message(f"📝 Mission: {MISSION}")
    log_message(f"⏱️  Interval: {WAIT_MINUTES} minutes between videos")
    log_message(f"🎬 Total videos: {len(VIDEO_CONFIGS)}")
    log_message("💎 Quality: Premium (no cheap mode)")
    log_message("📱 Auto-posting: Enabled")
    
    successful_videos = 0
    failed_videos = 0
    
    for i, config in enumerate(VIDEO_CONFIGS, 1):
        # Wait before each video (except the first)
        if i > 1:
            wait_minutes(WAIT_MINUTES)
        
        # Generate the video
        success = generate_video(config, i)
        
        if success:
            successful_videos += 1
        else:
            failed_videos += 1
        
        log_message(f"📊 Progress: {i}/{len(VIDEO_CONFIGS)} videos processed")
    
    # Final summary
    log_message("🎉 Automated Video Generation Complete!")
    log_message(f"✅ Successful: {successful_videos}")
    log_message(f"❌ Failed: {failed_videos}")
    log_message(f"📈 Success Rate: {(successful_videos/len(VIDEO_CONFIGS)*100):.1f}%")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log_message("🛑 Automated generation stopped by user")
        sys.exit(0)
    except Exception as e:
        log_message(f"💥 Fatal error: {e}")
        sys.exit(1)