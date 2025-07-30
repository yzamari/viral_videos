#!/usr/bin/env python3
"""
Fix Audio Issues in Final Videos
=================================
Root Cause: MoviePy sometimes corrupts audio when adding overlays, especially
when multiple text clips are composited. The audio_only version has good audio,
but the final version has corrupted/missing audio.

Solution: Re-compose final videos by:
1. Taking the audio_only version (which has good audio)
2. Adding subtitles from the SRT file
3. Creating a new final video with proper audio
"""

import os
import subprocess
import json
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

def check_audio_quality(video_path: str) -> Dict[str, any]:
    """Check audio stream properties"""
    cmd = [
        'ffprobe', '-v', 'error',
        '-select_streams', 'a:0',
        '-show_entries', 'stream=codec_name,sample_rate,channels,bit_rate',
        '-of', 'json',
        video_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        if data.get('streams'):
            return data['streams'][0]
        return {}
    except Exception as e:
        print(f"❌ Error checking audio: {e}")
        return {}

def get_video_duration(video_path: str) -> float:
    """Get video duration in seconds"""
    cmd = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        video_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except:
        return 0.0

def find_subtitle_file(session_dir: Path) -> Path:
    """Find the subtitle file in session directory"""
    # Try multiple possible locations
    subtitle_paths = [
        session_dir / 'subtitles' / 'subtitles.srt',
        session_dir / 'subtitles' / 'subtitle.srt',
        session_dir / 'subtitles.srt'
    ]
    
    for path in subtitle_paths:
        if path.exists():
            return path
    
    # Search for any .srt file
    for srt_file in session_dir.rglob('*.srt'):
        return srt_file
    
    return None

def fix_episode_audio(episode_dir: Path) -> bool:
    """Fix audio in a single episode"""
    print(f"\n🔧 Processing: {episode_dir.name}")
    
    # Find required files
    final_output_dir = episode_dir / 'final_output'
    if not final_output_dir.exists():
        print(f"  ⚠️  No final_output directory found")
        return False
    
    # Find audio_only and final videos
    audio_only_file = None
    final_file = None
    
    for file in final_output_dir.iterdir():
        if file.name.endswith('__audio_only.mp4'):
            audio_only_file = file
        elif file.name.endswith('__final.mp4'):
            final_file = file
    
    if not audio_only_file:
        print(f"  ⚠️  No audio_only file found")
        return False
    
    if not final_file:
        print(f"  ⚠️  No final file found")
        return False
    
    # Check audio quality in both files
    print(f"  📊 Checking audio quality...")
    audio_only_info = check_audio_quality(str(audio_only_file))
    final_info = check_audio_quality(str(final_file))
    
    print(f"  🎵 Audio_only: {audio_only_info.get('codec_name', 'N/A')} @ {audio_only_info.get('sample_rate', 'N/A')}Hz")
    print(f"  🎵 Final: {final_info.get('codec_name', 'N/A')} @ {final_info.get('sample_rate', 'N/A')}Hz")
    
    # Root cause analysis
    if audio_only_info.get('codec_name') == 'aac' and final_info.get('codec_name') == 'mp3':
        print(f"  🔍 ROOT CAUSE: Audio codec changed from AAC to MP3 during overlay processing")
        print(f"  🔍 This can cause audio corruption or quality loss")
    
    # Find subtitle file
    subtitle_file = find_subtitle_file(episode_dir)
    if not subtitle_file:
        print(f"  ⚠️  No subtitle file found - skipping subtitle overlay")
        # Still fix audio by copying from audio_only version
        return fix_audio_without_subtitles(audio_only_file, final_file)
    
    print(f"  📝 Found subtitles: {subtitle_file.name}")
    
    # Create fixed version
    return create_fixed_final_video(audio_only_file, subtitle_file, final_file)

def fix_audio_without_subtitles(audio_only_file: Path, final_file: Path) -> bool:
    """Fix audio by copying from audio_only version"""
    try:
        # Backup original
        backup_file = final_file.with_suffix('.mp4.backup')
        if not backup_file.exists():
            shutil.copy2(final_file, backup_file)
            print(f"  💾 Created backup: {backup_file.name}")
        
        # Copy audio from audio_only to final
        temp_file = final_file.parent / f"{final_file.stem}_temp.mp4"
        
        cmd = [
            'ffmpeg', '-y',
            '-i', str(final_file),      # Video from final
            '-i', str(audio_only_file),  # Audio from audio_only
            '-map', '0:v',               # Take video from first input
            '-map', '1:a',               # Take audio from second input
            '-c:v', 'copy',              # Copy video codec
            '-c:a', 'aac',               # Ensure AAC audio codec
            '-b:a', '192k',              # Audio bitrate
            str(temp_file)
        ]
        
        print(f"  🔄 Copying audio from audio_only version...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and temp_file.exists():
            # Replace original with fixed version
            shutil.move(str(temp_file), str(final_file))
            print(f"  ✅ Audio fixed successfully!")
            return True
        else:
            print(f"  ❌ Failed to fix audio: {result.stderr}")
            if temp_file.exists():
                temp_file.unlink()
            return False
            
    except Exception as e:
        print(f"  ❌ Error fixing audio: {e}")
        return False

def create_fixed_final_video(audio_only_file: Path, subtitle_file: Path, final_file: Path) -> bool:
    """Create a new final video with good audio and subtitles"""
    try:
        # Backup original
        backup_file = final_file.with_suffix('.mp4.backup')
        if not backup_file.exists():
            shutil.copy2(final_file, backup_file)
            print(f"  💾 Created backup: {backup_file.name}")
        
        # Create temp file with proper extension
        temp_file = final_file.parent / f"{final_file.stem}_fixed.mp4"
        
        # Use ffmpeg to add subtitles to audio_only version
        cmd = [
            'ffmpeg', '-y',
            '-i', str(audio_only_file),
            '-vf', f"subtitles='{str(subtitle_file)}':force_style='Alignment=2,MarginV=60,Fontsize=20,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,BorderStyle=3,Outline=2'",
            '-c:a', 'copy',  # Preserve original audio
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            str(temp_file)
        ]
        
        print(f"  🎬 Re-composing video with subtitles...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and temp_file.exists():
            # Verify audio in new file
            fixed_info = check_audio_quality(str(temp_file))
            print(f"  🎵 Fixed audio: {fixed_info.get('codec_name', 'N/A')} @ {fixed_info.get('sample_rate', 'N/A')}Hz")
            
            # Replace original with fixed version
            shutil.move(str(temp_file), str(final_file))
            print(f"  ✅ Video fixed successfully with good audio and subtitles!")
            return True
        else:
            print(f"  ❌ Failed to create fixed video: {result.stderr}")
            if temp_file.exists():
                temp_file.unlink()
            return False
            
    except Exception as e:
        print(f"  ❌ Error creating fixed video: {e}")
        return False

def main():
    """Fix audio issues in all Greek mythology episodes"""
    print("🎬 Audio Issue Fixer for Video Episodes")
    print("=" * 50)
    print("\n🔍 ROOT CAUSE ANALYSIS:")
    print("  • MoviePy sometimes corrupts audio when compositing multiple text overlays")
    print("  • Audio codec changes from AAC to MP3 during processing")
    print("  • The audio_only version preserves good audio quality")
    print("\n💡 SOLUTION:")
    print("  • Re-compose final videos using audio_only version + subtitles")
    print("  • Preserve original AAC audio codec")
    print("=" * 50)
    
    # Find all episode directories
    outputs_dir = Path('/Users/yahavzamari/viralAi/outputs')
    
    # Pattern for Greek mythology episodes
    greek_episodes = list(outputs_dir.glob('greek_*_ep*'))
    
    # Add any other series patterns
    other_episodes = []
    # other_episodes.extend(list(outputs_dir.glob('israeli_pm_*')))
    # other_episodes.extend(list(outputs_dir.glob('dragon_calculus_*')))
    
    all_episodes = greek_episodes + other_episodes
    
    if not all_episodes:
        print("\n❌ No episode directories found!")
        return
    
    print(f"\n📁 Found {len(all_episodes)} episode directories to check")
    
    # Process each episode
    fixed_count = 0
    skipped_count = 0
    failed_count = 0
    
    for episode_dir in sorted(all_episodes):
        if fix_episode_audio(episode_dir):
            fixed_count += 1
        else:
            # Check if it was skipped or failed
            final_output_dir = episode_dir / 'final_output'
            if final_output_dir.exists():
                failed_count += 1
            else:
                skipped_count += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")
    print(f"  ✅ Fixed: {fixed_count} episodes")
    print(f"  ❌ Failed: {failed_count} episodes") 
    print(f"  ⏭️  Skipped: {skipped_count} episodes")
    print(f"  📁 Total processed: {len(all_episodes)} episodes")
    
    print("\n💡 RECOMMENDATIONS:")
    print("  1. Test the fixed videos to ensure audio is working")
    print("  2. Original files are backed up as .backup")
    print("  3. To prevent this issue in future generations:")
    print("     - Update MoviePy audio handling in video_generator.py")
    print("     - Use consistent audio codec throughout pipeline")
    print("     - Consider using FFmpeg directly for overlay composition")

if __name__ == "__main__":
    main()