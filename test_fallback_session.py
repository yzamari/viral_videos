#!/usr/bin/env python3
"""
Test script to run a full session with forced fallback
"""

import os
import sys

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.workflows.generate_viral_video import main

if __name__ == "__main__":
    # Run the video generation with specific parameters
    result = main(
        mission="teach kids about stars lifecycle",
        platform="tiktok",  # TikTok for portrait videos
        duration=20,
        category="Educational",
        fallback_only=True,  # Force fallback generation
        visual_style="realistic",  # NOT cartoon
        target_audience="kids",
        tone="educational",
        style="informative",
        mode="enhanced"
    )
    
    if result:
        print(f"\n✅ Video generation completed successfully!")
        print(f"📁 Output: {result}")
    else:
        print("\n❌ Video generation failed!")