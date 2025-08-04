#!/usr/bin/env python3
"""
Create test funny video with colored rectangles to demonstrate the system
"""

import os
import subprocess
from datetime import datetime

def create_test_media():
    """Create test video clips with text"""
    
    print("🎨 Creating test media files...")
    
    test_clips = [
        {"text": "Reporter Falls in Pool", "color": "red", "duration": 4},
        {"text": "Weather Shows 1000F", "color": "blue", "duration": 4},
        {"text": "Mascot Trips Over", "color": "green", "duration": 4},
        {"text": "Anchor Laughing", "color": "yellow", "duration": 4},
        {"text": "Cat Zoom Bomb", "color": "purple", "duration": 4}
    ]
    
    os.makedirs("test_media", exist_ok=True)
    clip_files = []
    
    for i, clip in enumerate(test_clips):
        output = f"test_media/clip_{i}.mp4"
        
        # Create video with colored background and text
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', f'color=c={clip["color"]}:size=1920x1080:duration={clip["duration"]}',
            '-vf', f'drawtext=text=\'{clip["text"]}\':fontsize=80:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2',
            '-c:v', 'libx264',
            '-t', str(clip["duration"]),
            output
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            clip_files.append(output)
            print(f"✅ Created: {clip['text']} ({clip['duration']}s)")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create {clip['text']}: {e}")
    
    return clip_files

def create_final_video(clip_files, output_path="funny_news_test_20sec.mp4"):
    """Concatenate clips into final video"""
    
    print("\n🎬 Creating final video...")
    
    # Create concat file
    concat_file = "test_media/concat.txt"
    with open(concat_file, 'w') as f:
        for clip in clip_files:
            f.write(f"file '{os.path.abspath(clip)}'\n")
    
    # Concatenate
    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', concat_file,
        '-c:v', 'libx264',
        '-preset', 'medium',
        output_path
    ]
    
    subprocess.run(cmd, check=True)
    
    print(f"✅ Video created: {output_path}")
    return output_path

def main():
    print("""
🎬 FUNNY NEWS TEST VIDEO CREATOR
================================
📸 Demonstrating scraped media system
⏱️  Duration: 20 seconds
🎨 Using colored test clips
""")
    
    # Create test media
    clips = create_test_media()
    
    if not clips:
        print("❌ No clips created!")
        return
    
    # Create final video
    output = create_final_video(clips)
    
    # Cleanup
    for clip in clips:
        os.remove(clip)
    os.remove("test_media/concat.txt")
    os.rmdir("test_media")
    
    # Get file info
    size = os.path.getsize(output) / (1024 * 1024)  # MB
    
    print(f"""
✅ SUCCESS!
============
📹 Video: {output}
📏 Size: {size:.2f} MB
⏱️  Duration: 20 seconds
🎬 Clips: {len(clips)} funny moments

This demonstrates how the system would work with:
- Real scraped news bloopers
- Actual funny moments from broadcasts
- Downloaded media from news sites
- NO VEO/AI generation
""")

if __name__ == "__main__":
    main()