#!/usr/bin/env python3
"""
Fix Subtitle Timing by Merging Short Segments
This script processes existing SRT files to improve timing
"""

import os
import sys
import click
from pathlib import Path


def parse_srt_time(time_str):
    """Parse SRT time format to seconds"""
    time_str = time_str.strip()
    hours, minutes, seconds = time_str.split(':')
    seconds, millis = seconds.split(',')
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(millis) / 1000


def format_srt_time(seconds):
    """Format seconds to SRT time format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


@click.command()
@click.option('--srt', '-s', required=True, help='Path to SRT file to fix')
@click.option('--min-duration', '-m', default=2.0, type=float, help='Minimum subtitle duration in seconds')
@click.option('--output', '-o', help='Output SRT file (default: input_fixed.srt)')
def fix_timing(srt, min_duration, output):
    """Fix subtitle timing by merging short segments"""
    
    if not os.path.exists(srt):
        print(f"❌ SRT file not found: {srt}")
        return
    
    if not output:
        output = srt.replace('.srt', '_fixed.srt')
    
    print(f"📝 Processing: {srt}")
    print(f"⏱️  Minimum duration: {min_duration}s")
    
    # Read the SRT file
    with open(srt, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse SRT entries
    entries = []
    blocks = content.strip().split('\n\n')
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            try:
                index = int(lines[0])
                timing = lines[1]
                text = ' '.join(lines[2:])
                
                # Parse timing
                start_str, end_str = timing.split(' --> ')
                start_time = parse_srt_time(start_str)
                end_time = parse_srt_time(end_str)
                
                entries.append({
                    'index': index,
                    'start': start_time,
                    'end': end_time,
                    'text': text.strip(),
                    'duration': end_time - start_time
                })
            except:
                continue
    
    print(f"📊 Found {len(entries)} subtitle entries")
    
    # Merge short segments
    merged_entries = []
    i = 0
    
    while i < len(entries):
        current = entries[i].copy()
        
        # Look ahead to merge short segments
        while i + 1 < len(entries) and current['duration'] < min_duration:
            next_entry = entries[i + 1]
            
            # Check if gap between segments is small
            gap = next_entry['start'] - current['end']
            if gap < 0.5:  # Less than 0.5 second gap
                # Merge entries
                current['text'] = current['text'].rstrip('.!?') + ' ' + next_entry['text']
                current['end'] = next_entry['end']
                current['duration'] = current['end'] - current['start']
                i += 1
            else:
                # Gap too large, don't merge
                break
        
        merged_entries.append(current)
        i += 1
    
    print(f"✅ Merged to {len(merged_entries)} entries")
    
    # Write the fixed SRT file
    with open(output, 'w', encoding='utf-8') as f:
        for i, entry in enumerate(merged_entries, 1):
            f.write(f"{i}\n")
            f.write(f"{format_srt_time(entry['start'])} --> {format_srt_time(entry['end'])}\n")
            f.write(f"{entry['text']}\n\n")
    
    print(f"💾 Saved fixed subtitles to: {output}")
    
    # Show statistics
    short_count = sum(1 for e in entries if e['duration'] < min_duration)
    merged_short = sum(1 for e in merged_entries if e['duration'] < min_duration)
    
    print(f"\n📊 Statistics:")
    print(f"   Original short segments: {short_count}/{len(entries)} ({short_count/len(entries)*100:.1f}%)")
    print(f"   Fixed short segments: {merged_short}/{len(merged_entries)} ({merged_short/len(merged_entries)*100:.1f}% if merged_entries else 0)")


if __name__ == '__main__':
    fix_timing()