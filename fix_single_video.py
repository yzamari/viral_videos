#!/usr/bin/env python3
"""
Fix Single Video - Test Script
"""

import os
import subprocess
import json
import shutil
from pathlib import Path
import sys

def get_video_dimensions(video_path: str) -> tuple:
    """Get video width and height"""
    cmd = [
        'ffprobe', '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height',
        '-of', 'json',
        video_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        stream = data['streams'][0]
        return stream['width'], stream['height']
    except:
        return 1920, 1080  # Default

def calculate_subtitle_font_size(width: int, height: int) -> int:
    """Calculate appropriate subtitle font size"""
    is_portrait = height > width
    
    if is_portrait:
        # 2.8% of height for portrait
        font_size = int(height * 0.028)
        font_size = max(font_size, 28)
        font_size = min(font_size, int(height * 0.035))
    else:
        # 2.5% of height for landscape
        font_size = int(height * 0.025)
        font_size = max(font_size, 24)
        font_size = min(font_size, int(height * 0.035))
    
    return font_size

def fix_episode_complete(episode_dir: Path) -> bool:
    """Fix episode with proper audio, subtitles, and overlays"""
    print(f"\n🔧 Processing: {episode_dir.name}")
    
    # Find required files
    final_output_dir = episode_dir / 'final_output'
    audio_only_file = None
    final_file = None
    
    for file in final_output_dir.iterdir():
        if file.name.endswith('__audio_only.mp4'):
            audio_only_file = file
        elif file.name.endswith('__final.mp4'):
            final_file = file
    
    if not audio_only_file or not final_file:
        print(f"  ⚠️  Missing required files")
        return False
    
    # Get video dimensions
    width, height = get_video_dimensions(str(audio_only_file))
    print(f"  📐 Video dimensions: {width}x{height}")
    
    # Calculate subtitle font size
    subtitle_font_size = calculate_subtitle_font_size(width, height)
    print(f"  📏 Subtitle font size: {subtitle_font_size}px")
    
    # Find subtitle file
    subtitle_file = episode_dir / 'subtitles' / 'subtitles.srt'
    if not subtitle_file.exists():
        print(f"  ⚠️  No subtitle file found")
        return False
    
    # Backup original if not already done
    backup_file = final_file.with_suffix('.mp4.original')
    if not backup_file.exists():
        shutil.copy2(final_file, backup_file)
        print(f"  💾 Created backup: {backup_file.name}")
    
    # Create temp file
    temp_file = final_file.parent / f"{final_file.stem}_fixed.mp4"
    
    # Build FFmpeg command - simple version with just subtitles
    cmd = [
        'ffmpeg', '-y', 
        '-i', str(audio_only_file),
        '-vf', f"subtitles='{str(subtitle_file)}':force_style='Alignment=2,MarginV=120,Fontsize={subtitle_font_size},PrimaryColour=&HFFFFFF,OutlineColour=&H000000,BorderStyle=3,Outline=2,Bold=1,Spacing=0.5'",
        '-c:a', 'copy',
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        str(temp_file)
    ]
    
    print(f"  🎬 Applying subtitles with {subtitle_font_size}px font...")
    print(f"  Command: {' '.join(cmd[:8])}...")  # Show partial command
    
    # Run FFmpeg
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0 and temp_file.exists():
        # Replace original with fixed version
        shutil.move(str(temp_file), str(final_file))
        print(f"  ✅ Video fixed successfully!")
        print(f"  📝 Applied subtitles with {subtitle_font_size}px font")
        return True
    else:
        print(f"  ❌ Failed to create fixed video")
        if result.stderr:
            print(f"  Error: {result.stderr[:500]}...")
        if temp_file.exists():
            temp_file.unlink()
        return False

def main():
    """Fix a single episode"""
    if len(sys.argv) > 1:
        episode_name = sys.argv[1]
    else:
        # Default to first episode
        episode_name = "greek_zeus_ep1"
    
    print(f"🎬 Fixing Single Video: {episode_name}")
    print("=" * 50)
    
    outputs_dir = Path('/Users/yahavzamari/viralAi/outputs')
    episode_dir = outputs_dir / episode_name
    
    if episode_dir.exists():
        if fix_episode_complete(episode_dir):
            print("\n✅ Fix completed successfully!")
        else:
            print("\n❌ Fix failed!")
    else:
        print(f"\n⚠️  Episode directory not found: {episode_name}")
        print(f"  Looking in: {outputs_dir}")

if __name__ == "__main__":
    main()