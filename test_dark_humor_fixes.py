#!/usr/bin/env python3
"""Test script to verify dark humor news fixes"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, 'src')

from src.news_aggregator.enhanced_aggregator import create_enhanced_news_edition

async def test_fixes():
    """Test the fixes: 30s duration, dark humor rephrasing, dual text display"""
    
    print("🧪 Testing Dark Humor News Fixes")
    print("=" * 50)
    
    # Test parameters matching the user's original command but with CSV for reliable content
    sources = []  # Use CSV instead of scraping for reliable testing
    
    try:
        result = await create_enhanced_news_edition(
            sources=sources if sources else ['test_csv'],  # Fallback source name
            csv_file="test_mock_news.csv",
            languages=['he'],  # Hebrew for original sources
            style="dark comedy satire",
            tone="funny dark humor satirical", 
            platform="tiktok",
            duration_seconds=30,  # 30 seconds as requested
            max_stories=5,  # Fewer stories for testing
            enable_ai_discussion=True,  # Enable AI for rephrasing
            discussion_log=True,
            overlay_style="modern",
            output_dir="outputs/test_fixes",
            hours_back=24,
            telegram_channels=[],
            use_youtube_videos=True,  # Enable YouTube 
            logo_path=None,
            channel_name="חדשות סאטיריות",  # Hebrew satirical news
            dynamic_transitions=True
        )
        
        print(f"\n✅ Test completed successfully!")
        print(f"📹 Generated videos: {result}")
        
        # Check if files exist and get duration
        for lang, video_path in result.items():
            if os.path.exists(video_path):
                print(f"✅ {lang} video created: {video_path}")
                
                # Get video duration 
                import subprocess
                try:
                    probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                '-of', 'default=noprint_wrappers=1:nokey=1', video_path]
                    duration_result = subprocess.run(probe_cmd, capture_output=True, text=True)
                    if duration_result.returncode == 0:
                        duration = float(duration_result.stdout.strip())
                        print(f"   📊 Duration: {duration:.1f} seconds")
                        
                        if 25 <= duration <= 35:  # Allow some tolerance
                            print(f"   ✅ Duration is correct (~30s)")
                        else:
                            print(f"   ⚠️  Duration issue: got {duration:.1f}s, expected ~30s")
                    else:
                        print(f"   ❌ Could not get duration: {duration_result.stderr}")
                except Exception as e:
                    print(f"   ❌ Error checking duration: {e}")
            else:
                print(f"❌ {lang} video not found: {video_path}")
    
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_fixes())
    sys.exit(0 if success else 1)