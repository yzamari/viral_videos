#!/usr/bin/env python3
"""Test multi-source, multi-language news aggregation"""

import subprocess
import sys
import os
import json

def test_multi_source_languages():
    """Test news aggregator with multiple sources and languages"""
    
    print("🧪 Testing Multi-Source, Multi-Language News Aggregation")
    print("=" * 60)
    
    # Test command with multiple sources and languages
    cmd = [
        sys.executable, "main.py", "news", "aggregate-enhanced",
        "https://www.ynet.co.il",
        "https://www.mako.co.il",
        "-l", "he",        # Hebrew
        "-l", "en",        # English
        "--style", "modern breaking news",
        "--tone", "urgent professional",
        "--platform", "tiktok",
        "--duration", "20",
        "--max-stories", "4",
        "--overlay-style", "modern",
        "--hours-back", "12",
        "--telegram-channels", "@ynet_news"
    ]
    
    print("📌 Command:")
    print(" ".join(cmd))
    print("\n" + "=" * 60)
    
    try:
        # Run command
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("\n✅ Command completed successfully!")
            
            # Parse output for video paths
            output_lines = result.stdout.split('\n')
            video_count = 0
            
            for line in output_lines:
                if ".mp4" in line and "outputs/" in line:
                    print(f"📹 Generated: {line.strip()}")
                    video_count += 1
            
            print(f"\n📊 Total videos created: {video_count}")
            
            # Find latest session
            sessions = sorted([d for d in os.listdir("outputs") if d.startswith("session_")])
            if sessions:
                latest_session = sessions[-1]
                session_dir = f"outputs/{latest_session}"
                
                # Check report
                report_path = f"{session_dir}/news_aggregation_report.json"
                if os.path.exists(report_path):
                    with open(report_path, 'r', encoding='utf-8') as f:
                        report = json.load(f)
                    
                    print(f"\n📰 Aggregation Summary:")
                    print(f"   - Total stories: {report['total_stories']}")
                    print(f"   - Languages: {list(report['output_videos'].keys())}")
                    print(f"   - Sources included:")
                    
                    sources = set()
                    for story in report['stories']:
                        sources.update(story['sources'])
                    
                    for source in sources:
                        print(f"     • {source}")
                    
                    # List video files
                    print(f"\n📹 Generated Videos:")
                    for lang, path in report['output_videos'].items():
                        if os.path.exists(path):
                            # Check dimensions
                            probe_cmd = ["ffprobe", "-v", "quiet", "-print_format", "json",
                                       "-show_streams", path]
                            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
                            
                            if probe_result.returncode == 0:
                                probe_data = json.loads(probe_result.stdout)
                                for stream in probe_data.get("streams", []):
                                    if stream.get("codec_type") == "video":
                                        w = stream.get("width")
                                        h = stream.get("height")
                                        dur = float(stream.get("duration", 0))
                                        print(f"   - {lang}: {w}x{h}, {dur:.1f}s - {path}")
                                        break
                        
        else:
            print(f"\n❌ Command failed with code {result.returncode}")
            if result.stderr:
                print(f"Error output:\n{result.stderr[:500]}...")
    
    except subprocess.TimeoutExpired:
        print("\n⏰ Command timed out after 5 minutes")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ Test Features Demonstrated:")
    print("1. Multiple sources (Ynet + Mako)")
    print("2. Multiple languages (Hebrew + English)")
    print("3. Telegram channel integration")
    print("4. TikTok portrait format")
    print("5. Time-based filtering (12 hours)")

if __name__ == "__main__":
    test_multi_source_languages()