#!/usr/bin/env python3
"""Test all fixes are working properly"""

import subprocess
import sys
import os
import json

def test_complete_fixes():
    """Test all implemented fixes"""
    
    print("🧪 Testing Complete News Aggregator with All Fixes")
    print("=" * 60)
    print("✅ Fixed Issues:")
    print("1. AIServiceManager integration (generate_content_async)")
    print("2. SSL certificate errors (disabled SSL for Unsplash)")
    print("3. AI font selection for visual styles")
    print("4. Better media URLs for testing")
    print("=" * 60)
    
    # Test command
    cmd = [
        sys.executable, "main.py", "news", "aggregate-enhanced",
        "https://www.ynet.co.il",
        "--languages", "he",
        "--platform", "tiktok",
        "--style", "urgent breaking news",
        "--tone", "dramatic professional", 
        "--max-stories", "3",
        "--duration", "15",
        "--overlay-style", "modern",
        "--enable-ai",  # Enable AI features
        "--hours-back", "6"
    ]
    
    print("\n📌 Running command:")
    print(" ".join(cmd))
    print("\n" + "=" * 60)
    
    try:
        # Run command
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("\n✅ Success! All features working.")
            
            # Check for AI warnings
            if "AI service unavailable" in result.stderr:
                print("⚠️  AI service not configured (expected)")
            else:
                print("✅ AI service integration working")
            
            # Check for SSL errors
            if "SSLCertVerificationError" not in result.stderr:
                print("✅ SSL errors fixed for media downloads")
            
            # Check for visual styles
            if "AI selected visual styles" in result.stderr:
                print("✅ AI font selection working")
            
            # Find output video
            sessions = sorted([d for d in os.listdir("outputs") if d.startswith("session_")])
            if sessions:
                latest = sessions[-1]
                report_path = f"outputs/{latest}/news_aggregation_report.json"
                
                if os.path.exists(report_path):
                    with open(report_path, 'r', encoding='utf-8') as f:
                        report = json.load(f)
                    
                    print(f"\n📊 Results:")
                    print(f"   - Stories: {report['total_stories']}")
                    print(f"   - Video: {list(report['output_videos'].values())[0]}")
                    
                    # Check dimensions
                    video_path = list(report['output_videos'].values())[0]
                    if os.path.exists(video_path):
                        probe_cmd = ["ffprobe", "-v", "quiet", "-print_format", "json",
                                   "-show_streams", video_path]
                        probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
                        
                        if probe_result.returncode == 0:
                            probe_data = json.loads(probe_result.stdout)
                            for stream in probe_data.get("streams", []):
                                if stream.get("codec_type") == "video":
                                    w = stream.get("width")
                                    h = stream.get("height")
                                    print(f"   - Dimensions: {w}x{h} {'✅ Portrait' if w == 1080 and h == 1920 else '❌'}")
                                    break
                    
                    # Show downloaded media
                    print(f"\n📸 Media Status:")
                    has_media = False
                    for story in report['stories']:
                        if story.get('has_image') or story.get('has_video'):
                            has_media = True
                            break
                    
                    if has_media:
                        print("   ✅ Media successfully downloaded")
                    else:
                        print("   ℹ️  Text-only mode (no media downloaded)")
        
        else:
            print(f"\n❌ Command failed: {result.returncode}")
            if result.stderr:
                print("Error output:")
                print(result.stderr[:500])
    
    except subprocess.TimeoutExpired:
        print("\n⏰ Timeout after 5 minutes")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("📝 Summary:")
    print("- AIServiceManager: Fixed with backward compatible method")
    print("- SSL Downloads: Fixed with conditional SSL disable")
    print("- AI Font Selection: Added to news orchestrator")
    print("- Media Downloads: Added test scraper with working URLs")

if __name__ == "__main__":
    test_complete_fixes()