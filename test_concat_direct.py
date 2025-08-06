#!/usr/bin/env python3
"""Direct test of news aggregator concatenation"""

import asyncio
import sys
import os

# Add project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.news_aggregator.aggregator_scraped_media import create_scraped_media_news_edition

async def test_concat():
    """Test concatenation directly"""
    
    print("Testing news aggregator concatenation...")
    
    # Test with Ynet source
    result = await create_scraped_media_news_edition(
        source_urls=["https://www.ynet.co.il"],
        platform="tiktok",
        duration=30,  # 30 seconds
        max_stories=3,
        style="news",
        tone="professional",
        languages=["he"],
        channel_name="CONCAT_TEST",
        overlay_style="modern",
        use_youtube_videos=False,
        output_dir="outputs/concat_test"
    )
    
    print(f"Result: {result}")
    
    # Check durations
    if result and 'videos' in result:
        for lang, video_path in result['videos'].items():
            if os.path.exists(video_path):
                import subprocess
                probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                             '-of', 'default=noprint_wrappers=1:nokey=1', video_path]
                duration_result = subprocess.run(probe_cmd, capture_output=True, text=True)
                if duration_result.returncode == 0:
                    duration = float(duration_result.stdout.strip())
                    print(f"✅ Video duration for {lang}: {duration:.1f}s")
                    if duration < 25:
                        print(f"❌ ERROR: Duration too short! Expected ~30s")
                    else:
                        print(f"✅ Duration looks good!")

if __name__ == "__main__":
    asyncio.run(test_concat())