#!/usr/bin/env python3
"""
Create properly segmented subtitles using the generation log data
"""

import json
from pathlib import Path

def create_proper_subtitles():
    session_dir = Path("/Users/yahavzamari/viralAi/outputs/session_20250716_220750")
    
    # Read the generation log
    log_file = session_dir / "logs" / "generation_log.json"
    if not log_file.exists():
        print("❌ Generation log not found")
        return
    
    with open(log_file, 'r') as f:
        log_data = json.load(f)
    
    # Get script segments
    script_result = log_data.get('script_result', {})
    segments = script_result.get('segments', [])
    
    if not segments:
        print("❌ No script segments found")
        return
    
    print(f"📝 Creating subtitles for {len(segments)} segments")
    
    # Create SRT content using the actual segment durations but scaling to 15s
    srt_content = ""
    current_time = 0.0
    target_duration = 15.0
    
    # Use the actual segment durations from the script
    for i, segment in enumerate(segments):
        text = segment.get('text', '')
        segment_duration = segment.get('duration', 3.0)
        
        # Scale duration to fit 15s target
        scaled_duration = (segment_duration / 14.0) * target_duration
        
        # Adjust if this is the last segment to ensure we end exactly at 15s
        if i == len(segments) - 1:
            scaled_duration = target_duration - current_time
        
        if scaled_duration <= 0:
            break
        
        # Format SRT timing
        start_time = format_srt_time(current_time)
        end_time = format_srt_time(current_time + scaled_duration)
        
        srt_content += f"{i+1}\n"
        srt_content += f"{start_time} --> {end_time}\n"
        srt_content += f"{text}\n\n"
        
        print(f"   Segment {i+1}: {start_time} --> {end_time} | {text}")
        
        current_time += scaled_duration
    
    # Write SRT file
    srt_file = session_dir / "subtitles" / "subtitles.srt"
    with open(srt_file, 'w') as f:
        f.write(srt_content)
    
    # Create VTT content
    vtt_content = "WEBVTT\n\n"
    current_time = 0.0
    
    for i, segment in enumerate(segments):
        text = segment.get('text', '')
        segment_duration = segment.get('duration', 3.0)
        
        # Scale duration to fit 15s target
        scaled_duration = (segment_duration / 14.0) * target_duration
        
        # Adjust if this is the last segment
        if i == len(segments) - 1:
            scaled_duration = target_duration - current_time
        
        if scaled_duration <= 0:
            break
        
        # Format VTT timing
        start_time = format_vtt_time(current_time)
        end_time = format_vtt_time(current_time + scaled_duration)
        
        vtt_content += f"{start_time} --> {end_time}\n"
        vtt_content += f"{text}\n\n"
        
        current_time += scaled_duration
    
    # Write VTT file
    vtt_file = session_dir / "subtitles" / "subtitles.vtt"
    with open(vtt_file, 'w') as f:
        f.write(vtt_content)
    
    print(f"✅ Created {len(segments)} properly segmented subtitles")
    print(f"   Total duration: {current_time:.1f}s (target: {target_duration}s)")
    print(f"   SRT: {srt_file}")
    print(f"   VTT: {vtt_file}")

def format_srt_time(seconds):
    """Format seconds to SRT time format (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def format_vtt_time(seconds):
    """Format seconds to VTT time format (MM:SS.mmm)"""
    minutes = int(seconds // 60)
    secs = seconds % 60
    
    return f"{minutes:02d}:{secs:06.3f}"

if __name__ == "__main__":
    create_proper_subtitles()