#!/usr/bin/env python3
"""
Complete Video Fix - Subtitles + Overlays
=========================================
Properly recreate videos with:
1. Good audio from audio_only version
2. Subtitles with corrected font size
3. All original overlays (hook, CTA, etc.)
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
        # 2.8% of height for portrait (Instagram/TikTok)
        font_size = int(height * 0.028)
        font_size = max(font_size, 28)  # Minimum
        font_size = min(font_size, int(height * 0.035))  # Maximum
    else:
        # 2.5% of height for landscape (YouTube)
        font_size = int(height * 0.025)
        font_size = max(font_size, 24)  # Minimum
        font_size = min(font_size, int(height * 0.035))  # Maximum
    
    return font_size

def load_overlay_metadata(episode_dir: Path) -> Optional[Dict]:
    """Load overlay metadata from episode directory"""
    overlay_file = episode_dir / 'overlays' / 'timed_overlay_metadata.json'
    if overlay_file.exists():
        with open(overlay_file, 'r') as f:
            return json.load(f)
    return None

def build_overlay_filter(overlay_data: Dict, width: int, height: int) -> str:
    """Build FFmpeg filter string for overlays"""
    if not overlay_data or 'filter_complex' not in overlay_data:
        return ""
    
    # Get the original filter
    filter_str = overlay_data['filter_complex']
    
    # The filter might have temp paths, we need to clean it
    # Just return the drawtext commands
    return filter_str

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
    
    # Load overlay metadata
    overlay_data = load_overlay_metadata(episode_dir)
    
    # Backup original if not already done
    backup_file = final_file.with_suffix('.mp4.original')
    if not backup_file.exists():
        shutil.copy2(final_file, backup_file)
        print(f"  💾 Created backup: {backup_file.name}")
    
    # Create temp file
    temp_file = final_file.parent / f"{final_file.stem}_complete.mp4"
    
    # Build FFmpeg command
    cmd = ['ffmpeg', '-y', '-i', str(audio_only_file)]
    
    # Build filter complex
    filters = []
    
    # Add subtitles with proper font size
    subtitle_filter = (
        f"subtitles='{str(subtitle_file)}'"
        f":force_style='Alignment=2,MarginV=120"
        f",Fontsize={subtitle_font_size}"
        f",PrimaryColour=&HFFFFFF"
        f",OutlineColour=&H000000"
        f",BorderStyle=3,Outline=2,Bold=1"
        f",Spacing=0.5'"  # Add slight letter spacing
    )
    filters.append(subtitle_filter)
    
    # Add overlays if available
    if overlay_data and 'filter_complex' in overlay_data:
        # Extract just the drawtext parts from the filter
        overlay_filter = overlay_data['filter_complex']
        
        # Clean up the filter if needed
        if 'drawtext=' in overlay_filter:
            # Add each drawtext as a separate filter
            drawtext_parts = overlay_filter.split(',drawtext=')
            for i, part in enumerate(drawtext_parts):
                if i == 0 and not part.startswith('drawtext='):
                    part = 'drawtext=' + part
                elif i > 0:
                    part = 'drawtext=' + part
                
                # Clean up any trailing commas
                part = part.rstrip(',')
                
                if part.startswith('drawtext='):
                    filters.append(part)
    
    # Combine all filters
    if filters:
        filter_complex = ','.join(filters)
        cmd.extend(['-vf', filter_complex])
    
    # Output settings
    cmd.extend([
        '-c:a', 'copy',  # Preserve original audio
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        str(temp_file)
    ])
    
    print(f"  🎬 Re-composing video with subtitles and overlays...")
    
    # Run FFmpeg
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0 and temp_file.exists():
        # Replace original with fixed version
        shutil.move(str(temp_file), str(final_file))
        print(f"  ✅ Video fixed successfully!")
        
        # Show what was added
        if overlay_data:
            print(f"  🎯 Added {overlay_data.get('overlays_applied', 0)} overlays")
        print(f"  📝 Added subtitles with {subtitle_font_size}px font")
        
        return True
    else:
        print(f"  ❌ Failed to create fixed video")
        if result.stderr:
            print(f"  Error: {result.stderr[:200]}...")
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