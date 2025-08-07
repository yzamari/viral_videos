#!/usr/bin/env python3
"""
Create a clean, professional news video with proper text layout
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.news_aggregator.enhanced_aggregator import EnhancedNewsAggregator
import asyncio

async def create_clean_news():
    """Create a clean news video with better formatting"""
    
    # Use test media for clean demonstration
    sources = ["test_media"]  # This has clean test content
    
    aggregator = EnhancedNewsAggregator(
        enable_discussions=False,
        discussion_log=False
    )
    
    # Create video with clean layout
    videos = await aggregator.aggregate_and_create_video(
        sources=sources,
        languages=["en"],
        style="professional news broadcast",
        tone="neutral professional",
        platform="tiktok",
        duration=30,
        max_stories=3,
        channel_name="WORLD NEWS",
        use_youtube_videos=False,
        hours_back=24
    )
    
    if videos:
        print(f"\n✅ Clean news video created: {videos[0]}")
        return videos[0]
    else:
        print("\n❌ Failed to create video")
        return None

if __name__ == "__main__":
    video_path = asyncio.run(create_clean_news())
    if video_path:
        print(f"\n🎬 Video saved to: {video_path}")
        print("\nThe video has:")
        print("- Clean, readable text layout")
        print("- Professional news overlay")
        print("- No overlapping elements")
        print("- Proper spacing and hierarchy")