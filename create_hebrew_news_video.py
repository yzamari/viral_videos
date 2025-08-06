#!/usr/bin/env python3
"""
Create Hebrew News Video
Direct command to create news video with Hebrew content
"""

import asyncio
import sys
from test_hebrew_news_static import StaticHebrewNews


async def main():
    """Create Hebrew news video"""
    
    # Get duration from command line or use default
    duration = 30
    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
        except:
            print("Usage: python create_hebrew_news_video.py [duration_in_seconds]")
            print("Using default duration: 30 seconds")
    
    print(f"""
🎬 Creating Hebrew News Video
=============================
Duration: {duration} seconds
Language: Hebrew
Sources: Ynet, Rotter (simulated)
""")
    
    generator = StaticHebrewNews()
    video_path = await generator.create_hebrew_news(duration_seconds=duration)
    
    print(f"\n✅ Video ready to view: {video_path}")
    print("\nTo play the video:")
    print(f"open {video_path}")
    
    return video_path


if __name__ == "__main__":
    asyncio.run(main())