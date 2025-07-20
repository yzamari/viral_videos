#!/usr/bin/env python3
"""
Create properly segmented subtitles for the session
"""

import json
from pathlib import Path

def create_segmented_subtitles():
    session_dir = Path("/Users/yahavzamari/viralAi/outputs/session_20250716_220750")
    
    # Read the session data
    session_data_file = session_dir / "session_data.json"
    if not session_data_file.exists():
        print("❌ Session data not found")
        return
    
    with open(session_data_file, 'r') as f:
        session_data = json.load(f)
    
    # Get script segments
    script_result = session_data.get('script_result', {})
    segments = script_result.get('segments', [])
    
    if not segments:
        print("❌ No script segments found")
        return
    
    print(f"📝 Creating subtitles for {len(segments)} segments")
    
    # Create SRT content
    srt_content = ""
    current_time = 0.0
    target_duration = 15.0
    
    for i, segment in enumerate(segments):
        text = segment.get('text', '')
        words = len(text.split())
        
        # Calculate duration based on word count and segment importance
        if i == 0:  # Hook segment
            duration = 3.0
        elif i == len(segments) - 1:  # CTA segment
            duration = 2.0
        else:
            duration = max(2.0, min(words * 0.4, (target_duration - current_time) / (len(segments) - i)))
        
        # Adjust if this is the last segment
        if i == len(segments) - 1:
            duration = target_duration - current_time
        
        if duration <= 0:
            break
        
        # Format SRT timing
        start_time = format_srt_time(current_time)
        end_time = format_srt_time(current_time + duration)
        
        srt_content += f"{i+1}\n"
        srt_content += f"{start_time} --> {end_time}\n"
        srt_content += f"{text}\n\n"
        
        print(f"   Segment {i+1}: {start_time} --> {end_time} | {text[:50]}...")
        
        current_time += duration
    
    # Write SRT file
    srt_file = session_dir / "subtitles" / "subtitles.srt"
    with open(srt_file, 'w') as f:
        f.write(srt_content)
    
    # Create VTT content
    vtt_content = "WEBVTT\n\n"
    current_time = 0.0
    
    for i, segment in enumerate(segments):
        text = segment.get('text', '')
        
        # Calculate duration (same logic as SRT)
        if i == 0:  # Hook segment
            duration = 3.0
        elif i == len(segments) - 1:  # CTA segment
            duration = 2.0
        else:
            words = len(text.split())
            duration = max(2.0, min(words * 0.4, (target_duration - current_time) / (len(segments) - i)))
        
        # Adjust if this is the last segment
        if i == len(segments) - 1:
            duration = target_duration - current_time
        
        if duration <= 0:
            break
        
        # Format VTT timing
        start_time = format_vtt_time(current_time)
        end_time = format_vtt_time(current_time + duration)
        
        vtt_content += f"{start_time} --> {end_time}\n"
        vtt_content += f"{text}\n\n"
        
        current_time += duration
    
    # Write VTT file
    vtt_file = session_dir / "subtitles" / "subtitles.vtt"
    with open(vtt_file, 'w') as f:
        f.write(vtt_content)
    
    print(f"✅ Created {len(segments)} properly segmented subtitles")
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
    create_segmented_subtitles()