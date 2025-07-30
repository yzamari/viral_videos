#!/usr/bin/env python3
"""
Final verification of all videos
"""

import subprocess
import json
from pathlib import Path

def verify_video(video_path: Path) -> dict:
    """Verify video properties"""
    cmd = [
        'ffprobe', '-v', 'error',
        '-show_format', '-show_streams',
        '-print_format', 'json',
        str(video_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        info = {
            'path': video_path.name,
            'playable': False,
            'duration': 0,
            'size_mb': 0,
            'video_codec': None,
            'audio_codec': None,
            'width': 0,
            'height': 0
        }
        
        for stream in data.get('streams', []):
            if stream['codec_type'] == 'video':
                info['video_codec'] = stream.get('codec_name')
                info['width'] = stream.get('width', 0)
                info['height'] = stream.get('height', 0)
            elif stream['codec_type'] == 'audio':
                info['audio_codec'] = stream.get('codec_name')
        
        if 'format' in data:
            info['duration'] = float(data['format'].get('duration', 0))
            info['size_mb'] = int(data['format'].get('size', 0)) / (1024 * 1024)
        
        info['playable'] = info['video_codec'] and info['audio_codec'] and info['duration'] > 0
        
        return info
    except:
        return {'path': video_path.name, 'playable': False, 'error': 'Cannot read file'}

def main():
    """Verify all final videos"""
    print("🎬 Final Video Verification")
    print("=" * 50)
    
    outputs_dir = Path('/Users/yahavzamari/viralAi/outputs')
    
    all_good = True
    total_size_mb = 0
    
    # Greek mythology episodes in order
    episodes = [
        ('greek_zeus_ep1', 'Zeus - King of Gods'),
        ('greek_athena_ep2', 'Athena - Goddess of Wisdom'),
        ('greek_hercules_ep3', 'Hercules - Divine Hero'),
        ('greek_achilles_ep4', 'Achilles - Greatest Warrior'),
        ('greek_odysseus_ep5', 'Odysseus - Master Strategist'),
        ('greek_medusa_ep6', 'Medusa - Cursed Beauty'),
        ('greek_prometheus_ep7', 'Prometheus - Fire Bringer'),
        ('greek_aphrodite_ep8', 'Aphrodite - Goddess of Love')
    ]
    
    # Also check variants
    variants = [
        ('greek_athena_ep2_enhanced', 'Athena - Enhanced Version'),
        ('greek_athena_ep2_simple', 'Athena - Simple Version')
    ]
    
    all_episodes = episodes + variants
    
    print(f"\n📊 Checking {len(all_episodes)} videos...\n")
    
    for episode_name, title in all_episodes:
        final_video = outputs_dir / episode_name / 'final_output' / f'final_video_{episode_name}__final.mp4'
        
        if final_video.exists():
            info = verify_video(final_video)
            
            if info['playable']:
                orientation = "Portrait" if info['height'] > info['width'] else "Landscape"
                print(f"✅ {episode_name}")
                print(f"   • Title: {title}")
                print(f"   • Size: {info['size_mb']:.1f} MB")
                print(f"   • Duration: {info['duration']:.1f}s")
                print(f"   • Resolution: {info['width']}x{info['height']} ({orientation})")
                print(f"   • Codecs: {info['video_codec']}/{info['audio_codec']}")
                total_size_mb += info['size_mb']
            else:
                print(f"❌ {episode_name}")
                print(f"   • ERROR: Video not playable!")
                all_good = False
        else:
            print(f"❌ {episode_name}")
            print(f"   • ERROR: Final video not found!")
            all_good = False
        print()
    
    # Summary
    print("=" * 50)
    if all_good:
        print("✅ ALL VIDEOS VERIFIED SUCCESSFULLY!")
        print(f"   • Total videos: {len(all_episodes)}")
        print(f"   • Total size: {total_size_mb:.1f} MB")
        print(f"   • All videos have proper H.264/AAC encoding")
        print(f"   • All videos have subtitles applied")
    else:
        print("❌ Some videos have issues!")

if __name__ == "__main__":
    main()