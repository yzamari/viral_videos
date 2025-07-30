#!/usr/bin/env python3
"""
Complete Video Fix - Properly handle all issues
==============================================
Fixes:
1. Audio codec preservation (AAC)
2. Subtitle font size (2.5-2.8% of height)
3. Overlay preservation
4. Proper file handling
"""

import os
import subprocess
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

def get_video_info(video_path: str) -> Dict:
    """Get comprehensive video information"""
    cmd = [
        'ffprobe', '-v', 'error',
        '-show_streams',
        '-print_format', 'json',
        video_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        video_stream = None
        audio_stream = None
        
        for stream in data.get('streams', []):
            if stream['codec_type'] == 'video' and not video_stream:
                video_stream = stream
            elif stream['codec_type'] == 'audio' and not audio_stream:
                audio_stream = stream
        
        return {
            'width': int(video_stream['width']) if video_stream else 0,
            'height': int(video_stream['height']) if video_stream else 0,
            'video_codec': video_stream.get('codec_name', 'unknown') if video_stream else 'none',
            'audio_codec': audio_stream.get('codec_name', 'unknown') if audio_stream else 'none',
            'duration': float(video_stream.get('duration', 0)) if video_stream else 0
        }
    except Exception as e:
        print(f"Error getting video info: {e}")
        return {'width': 1920, 'height': 1080, 'video_codec': 'unknown', 'audio_codec': 'unknown'}

def calculate_subtitle_font_size(width: int, height: int) -> int:
    """Calculate appropriate subtitle font size based on video dimensions"""
    is_portrait = height > width
    
    if is_portrait:
        # 2.8% of height for portrait (Instagram/TikTok)
        font_size = int(height * 0.028)
        # Minimum 28px, maximum 3.5% of height
        font_size = max(font_size, 28)
        font_size = min(font_size, int(height * 0.035))
    else:
        # 2.5% of height for landscape (YouTube)
        font_size = int(height * 0.025)
        # Minimum 24px, maximum 3.5% of height
        font_size = max(font_size, 24)
        font_size = min(font_size, int(height * 0.035))
    
    return font_size

def load_overlay_metadata(episode_dir: Path) -> Optional[Dict]:
    """Load overlay metadata from episode directory"""
    overlay_file = episode_dir / 'overlays' / 'timed_overlay_metadata.json'
    if overlay_file.exists():
        try:
            with open(overlay_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return None

def extract_drawtext_filters(overlay_data: Dict) -> List[str]:
    """Extract individual drawtext filters from overlay metadata"""
    if not overlay_data or 'filter_complex' not in overlay_data:
        return []
    
    filter_str = overlay_data['filter_complex']
    filters = []
    
    # Split by drawtext= and reconstruct
    parts = filter_str.split('drawtext=')
    
    for i, part in enumerate(parts):
        if i == 0 and not part:
            continue
        
        # Find the end of this drawtext command
        # It ends at the next ,drawtext= or end of string
        end_pos = len(part)
        
        # Look for the next drawtext (if any)
        next_drawtext = part.find(',drawtext=')
        if next_drawtext != -1:
            end_pos = next_drawtext
        
        # Extract this drawtext command
        drawtext_cmd = part[:end_pos].rstrip(',')
        
        if drawtext_cmd:
            filters.append(f"drawtext={drawtext_cmd}")
    
    return filters

def restore_original_if_needed(final_file: Path) -> bool:
    """Restore original file if current one is corrupted"""
    original_file = final_file.with_suffix('.mp4.original')
    backup_file = final_file.with_suffix('.mp4.backup')
    
    # Check if current file is corrupted
    info = get_video_info(str(final_file))
    if info['width'] == 0 or info['height'] == 0:
        print(f"  ⚠️  Current file is corrupted")
        
        # Try to restore from original
        if original_file.exists():
            shutil.copy2(original_file, final_file)
            print(f"  ♻️  Restored from .original backup")
            return True
        elif backup_file.exists():
            shutil.copy2(backup_file, final_file)
            print(f"  ♻️  Restored from .backup")
            return True
    
    return False

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
        elif file.name.endswith('__final.mp4') and not file.name.endswith('_fixed.mp4'):
            final_file = file
    
    if not audio_only_file:
        print(f"  ❌ No audio_only file found")
        return False
    
    if not final_file:
        print(f"  ❌ No final file found")
        return False
    
    # Check and restore if corrupted
    restore_original_if_needed(final_file)
    
    # Get video information
    audio_info = get_video_info(str(audio_only_file))
    print(f"  📐 Video: {audio_info['width']}x{audio_info['height']}")
    print(f"  🎵 Audio codec: {audio_info['audio_codec']}")
    
    # Calculate subtitle font size
    font_size = calculate_subtitle_font_size(audio_info['width'], audio_info['height'])
    print(f"  📏 Subtitle font size: {font_size}px")
    
    # Find subtitle file
    subtitle_file = episode_dir / 'subtitles' / 'subtitles.srt'
    if not subtitle_file.exists():
        print(f"  ⚠️  No subtitle file found")
        return False
    
    # Load overlay metadata
    overlay_data = load_overlay_metadata(episode_dir)
    overlay_filters = []
    if overlay_data:
        overlay_filters = extract_drawtext_filters(overlay_data)
        if overlay_filters:
            print(f"  🎯 Found {len(overlay_filters)} overlays")
    
    # Backup original if not already done
    original_file = final_file.with_suffix('.mp4.original')
    if not original_file.exists():
        shutil.copy2(final_file, original_file)
        print(f"  💾 Created backup: {original_file.name}")
    
    # Create properly named temp file
    temp_file = final_file.with_name(f"{final_file.stem}_temp.mp4")
    
    # Build complex filter
    filters = []
    
    # 1. Add subtitles with proper styling
    subtitle_filter = (
        f"subtitles='{str(subtitle_file)}'"
        f":force_style='"
        f"Alignment=2"  # Bottom center
        f",MarginV=120"  # Distance from bottom
        f",Fontsize={font_size}"
        f",PrimaryColour=&HFFFFFF"  # White text
        f",OutlineColour=&H000000"  # Black outline
        f",BorderStyle=3"  # Opaque box + outline
        f",Outline=2"  # Outline thickness
        f",Bold=1"  # Bold text
        f",Spacing=0.5'"  # Letter spacing
    )
    
    # Build filter complex
    filter_complex = subtitle_filter
    
    # 2. Add overlays if available
    if overlay_filters:
        filter_complex += "," + ",".join(overlay_filters)
    
    # Build FFmpeg command
    cmd = [
        'ffmpeg', '-y',
        '-i', str(audio_only_file),  # Use audio_only for good audio
        '-vf', filter_complex,
        '-c:a', 'copy',  # Preserve AAC audio
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-pix_fmt', 'yuv420p',  # Ensure compatibility
        str(temp_file)
    ]
    
    print(f"  🎬 Creating fixed video...")
    
    # Run FFmpeg
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0 and temp_file.exists():
        # Verify the output
        output_info = get_video_info(str(temp_file))
        if output_info['width'] > 0 and output_info['audio_codec'] != 'none':
            # Replace final with fixed version
            shutil.move(str(temp_file), str(final_file))
            print(f"  ✅ Fixed successfully!")
            print(f"  📝 Subtitles: {font_size}px")
            print(f"  🎵 Audio: {output_info['audio_codec']}")
            if overlay_filters:
                print(f"  🎯 Overlays: {len(overlay_filters)}")
            return True
        else:
            print(f"  ❌ Output verification failed")
            temp_file.unlink()
    else:
        print(f"  ❌ FFmpeg failed")
        if result.stderr:
            print(f"  Error: {result.stderr[:300]}...")
        if temp_file.exists():
            temp_file.unlink()
    
    return False

def main():
    """Fix all Greek mythology episodes"""
    print("🎬 Complete Video Fixer")
    print("=" * 50)
    print("Fixes:")
    print("  • Preserves AAC audio from audio_only version")
    print("  • Applies subtitles with correct font size (2.5-2.8%)")
    print("  • Preserves original overlays")
    print("  • Handles corrupted files")
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
            print(f"\n⚠️  Episode not found: {episode_name}")
            failed_count += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")
    print(f"  ✅ Fixed: {fixed_count} episodes")
    print(f"  ❌ Failed: {failed_count} episodes")
    print(f"  📁 Total: {len(episodes)} episodes")

if __name__ == "__main__":
    main()