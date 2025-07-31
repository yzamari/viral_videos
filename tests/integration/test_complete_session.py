#!/usr/bin/env python3
"""
Test script to run a complete session and verify all components
"""

import os
import sys

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.workflows.generate_viral_video import main

if __name__ == "__main__":
    print("🎬 Starting complete session test...")
    print("Mission: Explain quantum physics to teenagers")
    print("Platform: TikTok (portrait)")
    print("Duration: 15 seconds")
    print("Visual Style: realistic (NOT cartoon)")
    print("=" * 50)
    
    # Run the video generation with specific parameters
    result = main(
        mission="Explain quantum physics to teenagers",
        platform="tiktok",  # TikTok for portrait videos
        duration=15,  # 15 seconds
        category="Educational",
        visual_style="realistic",  # NOT cartoon
        target_audience="teenagers",
        tone="educational",
        style="informative",
        mode="enhanced"  # Full enhanced mode
    )
    
    if result:
        print(f"\n✅ Video generation completed successfully!")
        print(f"📁 Output: {result}")
        
        # Extract session ID from result path
        session_id = None
        if 'session_' in result:
            session_id = result.split('session_')[1].split('/')[0]
            session_id = f"session_{session_id}"
            
        if session_id:
            print(f"📊 Session ID: {session_id}")
            print(f"📂 Session folder: outputs/{session_id}")
        
    else:
        print("\n❌ Video generation failed!")