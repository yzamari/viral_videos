#!/usr/bin/env python3
"""
Fix All Videos - Complete with Overlays
"""

import os
import subprocess
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional

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

def load_overlay_metadata(episode_dir: Path) -> Optional[Dict]:
    """Load overlay metadata from episode directory"""
    overlay_file = episode_dir / 'overlays' / 'timed_overlay_metadata.json'
    if overlay_file.exists():
        with open(overlay_file, 'r') as f:
            return json.load(f)
    return None

def extract_overlay_filters(overlay_data: Dict) -> List[str]:
    """Extract drawtext filters from overlay metadata"""
    if not overlay_data or 'filter_complex' not in overlay_data:
        return []
    
    # Get the filter string
    filter_str = overlay_data['filter_complex']
    
    # Split into individual drawtext commands
    filters = []
    
    # Handle the filter string that has multiple drawtext commands
    parts = filter_str.split(',drawtext=')
    
    for i, part in enumerate(parts):
        if i == 0 and not part.startswith('drawtext='):
            if part:  # Only add if not empty
                part = 'drawtext=' + part
        elif i > 0:
            part = 'drawtext=' + part
        
        # Clean up
        part = part.strip().rstrip(',')
        
        if part.startswith('drawtext=') and len(part) > 10:
            filters.append(part)
    
    return filters

def fix_episode_complete(episode_dir: Path, add_overlays: bool = True) -> bool:
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
    
    # Load overlay metadata
    overlay_data = None
    overlay_filters = []
    if add_overlays:
        overlay_data = load_overlay_metadata(episode_dir)
        if overlay_data:
            overlay_filters = extract_overlay_filters(overlay_data)
            print(f"  🎯 Found {len(overlay_filters)} overlay filters")
    
    # Backup original if not already done
    backup_file = final_file.with_suffix('.mp4.original')
    if not backup_file.exists():
        shutil.copy2(final_file, backup_file)
        print(f"  💾 Created backup: {backup_file.name}")
    
    # Create temp file
    temp_file = final_file.parent / f"{final_file.stem}_fixed.mp4"
    
    # Build filter complex
    filters = []
    
    # Add subtitles
    subtitle_filter = (
        f"subtitles='{str(subtitle_file)}'"
        f":force_style='Alignment=2,MarginV=120"
        f",Fontsize={subtitle_font_size}"
        f",PrimaryColour=&HFFFFFF"
        f",OutlineColour=&H000000"
        f",BorderStyle=3,Outline=2,Bold=1"
        f",Spacing=0.5'"
    )
    filters.append(subtitle_filter)
    
    # Add overlays if available
    if overlay_filters:
        filters.extend(overlay_filters)
    
    # Combine all filters
    filter_complex = ','.join(filters)
    
    # Build FFmpeg command
    cmd = [
        'ffmpeg', '-y', 
        '-i', str(audio_only_file),
        '-vf', filter_complex,
        '-c:a', 'copy',
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        str(temp_file)
    ]
    
    print(f"  🎬 Applying subtitles and overlays...")
    
    # Run FFmpeg
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0 and temp_file.exists():
        # Replace original with fixed version
        shutil.move(str(temp_file), str(final_file))
        print(f"  ✅ Video fixed successfully!")
        print(f"  📝 Applied subtitles with {subtitle_font_size}px font")
        if overlay_filters:
            print(f"  🎯 Applied {len(overlay_filters)} overlays")
        return True
    else:
        print(f"  ❌ Failed to create fixed video")
        if result.stderr:
            print(f"  Error: {result.stderr[:500]}...")
        if temp_file.exists():
            temp_file.unlink()
        return False

def main():
    """Fix all Greek mythology episodes"""
    print("🎬 Complete Video Fixer - Audio + Subtitles + Overlays")
    print("=" * 55)
    
    # Greek mythology episodes
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
    
    fixed_count = 0
    failed_count = 0
    
    for episode_name in episodes:
        episode_dir = outputs_dir / episode_name
        if episode_dir.exists():
            if fix_episode_complete(episode_dir):
                fixed_count += 1
            else:
                failed_count += 1
        else:
            print(f"\n⚠️  Episode directory not found: {episode_name}")
            failed_count += 1
    
    # Summary
    print("\n" + "=" * 55)
    print("📊 SUMMARY:")
    print(f"  ✅ Fixed: {fixed_count} episodes")
    print(f"  ❌ Failed: {failed_count} episodes")
    print(f"  📁 Total: {len(episodes)} episodes")
    
    print("\n💡 IMPROVEMENTS MADE:")
    print("  • Subtitle font size reduced to 2.5-2.8% of video height")
    print("  • Original overlays preserved (hook, CTA, etc.)")
    print("  • Audio preserved from audio_only version (AAC)")
    print("  • Original files backed up as .original")

if __name__ == "__main__":
    main()