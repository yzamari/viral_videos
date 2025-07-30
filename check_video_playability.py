#!/usr/bin/env python3
"""
Check Video Playability and Integrity
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, List

def check_video_integrity(video_path: str) -> Dict[str, any]:
    """Check if video is playable and get its properties"""
    result = {
        'path': video_path,
        'playable': False,
        'error': None,
        'properties': {}
    }
    
    # First check with ffprobe
    cmd = [
        'ffprobe', '-v', 'error',
        '-show_format', '-show_streams',
        '-print_format', 'json',
        video_path
    ]
    
    try:
        output = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(output.stdout)
        
        # Check if we have video and audio streams
        has_video = False
        has_audio = False
        video_codec = None
        audio_codec = None
        duration = 0
        
        for stream in data.get('streams', []):
            if stream['codec_type'] == 'video':
                has_video = True
                video_codec = stream.get('codec_name', 'unknown')
                result['properties']['video_codec'] = video_codec
                result['properties']['width'] = stream.get('width', 0)
                result['properties']['height'] = stream.get('height', 0)
                result['properties']['fps'] = eval(stream.get('r_frame_rate', '0/1'))
            elif stream['codec_type'] == 'audio':
                has_audio = True
                audio_codec = stream.get('codec_name', 'unknown')
                result['properties']['audio_codec'] = audio_codec
                result['properties']['sample_rate'] = stream.get('sample_rate', 0)
        
        if 'format' in data:
            duration = float(data['format'].get('duration', 0))
            result['properties']['duration'] = duration
            result['properties']['size_mb'] = int(data['format'].get('size', 0)) / (1024 * 1024)
            result['properties']['bitrate'] = data['format'].get('bit_rate', 0)
        
        # Check playability criteria
        if has_video and has_audio and duration > 0:
            result['playable'] = True
        else:
            issues = []
            if not has_video:
                issues.append("No video stream")
            if not has_audio:
                issues.append("No audio stream")
            if duration == 0:
                issues.append("Zero duration")
            result['error'] = "; ".join(issues)
            
    except subprocess.CalledProcessError as e:
        result['error'] = f"FFprobe error: {e.stderr if e.stderr else str(e)}"
    except json.JSONDecodeError:
        result['error'] = "Invalid video format - cannot parse metadata"
    except Exception as e:
        result['error'] = f"Unexpected error: {str(e)}"
    
    # Additional check - try to read first few frames
    if result['playable']:
        check_cmd = [
            'ffmpeg', '-i', video_path,
            '-frames:v', '1',
            '-f', 'null', '-'
        ]
        try:
            check_result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=5)
            if check_result.returncode != 0:
                result['playable'] = False
                result['error'] = "Cannot decode video frames"
        except subprocess.TimeoutExpired:
            result['playable'] = False
            result['error'] = "Video decoding timeout"
        except Exception:
            pass  # Keep existing result
    
    return result

def main():
    """Check all Greek mythology videos"""
    print("🎬 Video Playability Check")
    print("=" * 50)
    
    episodes = [
        "greek_zeus_ep1",
        "greek_athena_ep2",
        "greek_hercules_ep3",
        "greek_achilles_ep4",
        "greek_odysseus_ep5",
        "greek_medusa_ep6",
        "greek_prometheus_ep7",
        "greek_aphrodite_ep8"
    ]
    
    outputs_dir = Path('/Users/yahavzamari/viralAi/outputs')
    
    playable_count = 0
    unplayable_count = 0
    unplayable_videos = []
    
    for episode_name in episodes:
        print(f"\n📁 Checking {episode_name}...")
        episode_dir = outputs_dir / episode_name / 'final_output'
        
        if not episode_dir.exists():
            print(f"  ⚠️  Directory not found")
            continue
        
        # Check all video files in final_output
        for video_file in episode_dir.glob('*.mp4'):
            # Skip backup files
            if 'backup' in video_file.name or 'original' in video_file.name or 'temp' in video_file.name:
                continue
                
            result = check_video_integrity(str(video_file))
            
            if result['playable']:
                playable_count += 1
                props = result['properties']
                print(f"  ✅ {video_file.name}")
                print(f"     • Dimensions: {props.get('width')}x{props.get('height')}")
                print(f"     • Duration: {props.get('duration', 0):.1f}s")
                print(f"     • Size: {props.get('size_mb', 0):.1f} MB")
                print(f"     • Codecs: {props.get('video_codec')}/{props.get('audio_codec')}")
            else:
                unplayable_count += 1
                unplayable_videos.append((episode_name, video_file.name, result['error']))
                print(f"  ❌ {video_file.name}")
                print(f"     • Error: {result['error']}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")
    print(f"  ✅ Playable: {playable_count} videos")
    print(f"  ❌ Unplayable: {unplayable_count} videos")
    
    if unplayable_videos:
        print("\n🚨 UNPLAYABLE VIDEOS:")
        for episode, filename, error in unplayable_videos:
            print(f"  • {episode}/{filename}: {error}")
    
    return unplayable_count == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)