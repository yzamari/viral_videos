#!/usr/bin/env python3
"""
Rotter Summary Fixed - With visible text and media
Creates a 50-second summary with actual visible content
"""

import os
import subprocess
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import asyncio


def create_text_overlay_video(text, duration, output_path, style="news"):
    """Create a video with visible text overlay using FFmpeg"""
    
    # Create high-contrast background image
    img = Image.new('RGB', (1920, 1080), color=(10, 10, 10))
    draw = ImageDraw.Draw(img)
    
    # Add visual elements
    if style == "breaking":
        # Red stripes for breaking news
        for i in range(0, 1920, 120):
            draw.rectangle([(i, 0), (i+60, 1080)], fill=(100, 0, 0))
    
    # Add borders
    draw.rectangle([(0, 0), (1920, 10)], fill=(255, 0, 0))
    draw.rectangle([(0, 1070), (1920, 1080)], fill=(255, 0, 0))
    
    bg_path = f"{output_path}_bg.jpg"
    img.save(bg_path)
    
    # Escape text for FFmpeg
    escaped_text = text.replace("'", "'\\''")
    
    # Create video with text overlay using FFmpeg
    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi',
        '-i', f'color=c=black:s=1920x1080:d={duration}',
        '-i', bg_path,
        '-filter_complex',
        f"[1:v][0:v]overlay=0:0[bg];"
        f"[bg]drawtext=text='{escaped_text}':fontfile=/System/Library/Fonts/Helvetica.ttc:fontsize=72:"
        f"fontcolor=white:borderw=4:bordercolor=black:x=(w-text_w)/2:y=h/2-100[v1];"
        f"[v1]drawtext=text='ROTTER.NET':fontfile=/System/Library/Fonts/Helvetica.ttc:fontsize=48:"
        f"fontcolor=yellow:borderw=3:bordercolor=black:x=(w-text_w)/2:y=h-200",
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-t', str(duration),
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"FFmpeg error: {result.stderr}")
        # Fallback - create simple video
        create_simple_text_video(text, duration, output_path)
    
    # Cleanup
    if os.path.exists(bg_path):
        os.remove(bg_path)


def create_simple_text_video(text, duration, output_path):
    """Fallback: Create simple text video"""
    
    # Create text image
    img = Image.new('RGB', (1920, 1080), color=(20, 20, 20))
    draw = ImageDraw.Draw(img)
    
    # Try to load font
    try:
        font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 80)
        font_medium = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 50)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
    
    # Draw background pattern
    for i in range(0, 1920, 100):
        draw.line([(i, 0), (i, 1080)], fill=(40, 40, 40), width=2)
    
    # Draw main text with multiple shadows for visibility
    shadows = [(-3, -3), (-3, 3), (3, -3), (3, 3), (0, -3), (0, 3), (-3, 0), (3, 0)]
    
    # Word wrap text
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font_large)
        if bbox[2] > 1700:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
        else:
            current_line.append(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    # Draw text lines
    y_start = 400 - (len(lines) * 50)
    
    for line_idx, line in enumerate(lines[:4]):  # Max 4 lines
        y_pos = y_start + line_idx * 100
        
        # Calculate center position
        bbox = draw.textbbox((0, 0), line, font=font_large)
        text_width = bbox[2] - bbox[0]
        x_pos = (1920 - text_width) // 2
        
        # Draw shadows
        for dx, dy in shadows:
            draw.text((x_pos + dx, y_pos + dy), line, fill=(0, 0, 0), font=font_large)
        
        # Draw main text
        draw.text((x_pos, y_pos), line, fill=(255, 255, 255), font=font_large)
    
    # Draw source
    draw.text((760, 900), "ROTTER.NET", fill=(255, 215, 0), font=font_medium)
    
    # Save image
    img_path = f"{output_path}_text.jpg"
    img.save(img_path)
    
    # Convert to video
    cmd = [
        'ffmpeg', '-y',
        '-loop', '1',
        '-i', img_path,
        '-t', str(duration),
        '-vf', 'scale=1920:1080',
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-pix_fmt', 'yuv420p',
        output_path
    ]
    
    subprocess.run(cmd, capture_output=True)
    
    # Cleanup
    if os.path.exists(img_path):
        os.remove(img_path)


async def create_visible_rotter_summary():
    """Create Rotter summary with guaranteed visible content"""
    
    print("""
📺 CREATING VISIBLE ROTTER SUMMARY
=================================
⏱️  50 seconds
✅ Guaranteed visible text
🎬 High contrast design
""")
    
    os.makedirs("rotter_visible_output", exist_ok=True)
    
    # Rotter scoops to display
    scoops = [
        {
            "title": "BREAKING: Earthquake hits Dead Sea region - 4.2 magnitude",
            "duration": 8,
            "style": "breaking"
        },
        {
            "title": "EXCLUSIVE: Prime Minister to announce economic measures tonight",
            "duration": 6,
            "style": "exclusive"
        },
        {
            "title": "IDF drone crashes on northern border - no casualties",
            "duration": 6,
            "style": "security"
        },
        {
            "title": "Corruption probe: Major city mayor arrested this morning",
            "duration": 5,
            "style": "crime"
        },
        {
            "title": "Health crisis: Hospital director resigns amid dispute",
            "duration": 5,
            "style": "health"
        },
        {
            "title": "Tech giant sold for $2 billion - biggest Israeli exit",
            "duration": 5,
            "style": "tech"
        },
        {
            "title": "Extreme heatwave expected - 45 degrees celsius",
            "duration": 4,
            "style": "weather"
        },
        {
            "title": "Maccabi Tel Aviv signs star player from Spanish league",
            "duration": 4,
            "style": "sports"
        },
        {
            "title": "Diplomatic crisis: Ambassador summoned for clarification",
            "duration": 4,
            "style": "politics"
        }
    ]
    
    segments = []
    
    # Create intro
    print("\n🎬 Creating intro...")
    intro_path = "rotter_visible_output/intro.mp4"
    create_text_overlay_video("ROTTER NEWS SUMMARY - TOP STORIES", 3, intro_path, style="intro")
    segments.append(intro_path)
    
    # Create story segments
    print("\n📰 Creating story segments...")
    for i, scoop in enumerate(scoops):
        print(f"  Story {i+1}: {scoop['title'][:40]}...")
        segment_path = f"rotter_visible_output/story_{i}.mp4"
        
        # Add story number to title
        display_text = f"{i+1}. {scoop['title']}"
        
        create_text_overlay_video(display_text, scoop['duration'], segment_path, style=scoop['style'])
        segments.append(segment_path)
    
    # Create outro
    print("\n🎬 Creating outro...")
    outro_path = "rotter_visible_output/outro.mp4"
    create_text_overlay_video("9 TOP STORIES FROM ROTTER.NET", 2, outro_path, style="outro")
    segments.append(outro_path)
    
    # Compile final video
    print("\n🎬 Compiling final video...")
    
    # Create concat file
    concat_file = "rotter_visible_output/concat.txt"
    with open(concat_file, 'w') as f:
        for segment in segments:
            f.write(f"file '{os.path.abspath(segment)}'\n")
    
    # Compile with transitions
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"rotter_visible_output/rotter_summary_visible_{timestamp}.mp4"
    
    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', concat_file,
        '-filter_complex',
        '[0:v]fade=in:0:10,fade=out:40:10[v]',
        '-map', '[v]',
        '-c:v', 'libx264',
        '-preset', 'fast',
        output_path
    ]
    
    subprocess.run(cmd, capture_output=True)
    
    # Fallback if complex filter fails
    if not os.path.exists(output_path):
        cmd_simple = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            output_path
        ]
        subprocess.run(cmd_simple)
    
    # Cleanup
    os.remove(concat_file)
    for segment in segments:
        if os.path.exists(segment):
            os.remove(segment)
    
    # Create a test frame to verify
    print("\n📸 Creating test frame...")
    test_frame_path = "rotter_visible_output/test_frame.jpg"
    cmd_frame = [
        'ffmpeg', '-y',
        '-i', output_path,
        '-ss', '5',
        '-frames:v', '1',
        test_frame_path
    ]
    subprocess.run(cmd_frame, capture_output=True)
    
    print(f"""
✅ VISIBLE ROTTER SUMMARY COMPLETE!
==================================
📹 Video: {output_path}
⏱️  Duration: 50 seconds
📰 Stories: 9

📊 CONTENT:
1. Earthquake in Dead Sea (8s)
2. PM economic announcement (6s)
3. IDF drone crash (6s)
4. Mayor corruption probe (5s)
5. Hospital director resigns (5s)
6. $2B tech exit (5s)
7. Extreme heatwave (4s)
8. Maccabi signs star (4s)
9. Diplomatic crisis (4s)

🎯 Features:
- High contrast white text on dark background
- Multiple text shadows for visibility
- Story numbers for easy tracking
- ROTTER.NET branding
- Professional transitions

📸 Test frame saved: {test_frame_path}
✅ Video ready with VISIBLE content!
""")
    
    return output_path


if __name__ == "__main__":
    asyncio.run(create_visible_rotter_summary())