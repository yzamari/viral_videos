#!/usr/bin/env python3
"""
Create funny news video with simple overlay using PNG overlay approach
"""

import os
import subprocess
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

def create_overlay_png():
    """Create news overlay PNG with transparency"""
    
    print("🎨 Creating overlay PNG...")
    
    # Create transparent image
    overlay = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Top banner
    draw.rectangle([0, 0, 1920, 100], fill=(0, 0, 0, 200))
    
    # Breaking news box
    draw.rectangle([50, 20, 250, 70], fill=(255, 0, 0, 255))
    
    # Bottom ticker
    draw.rectangle([0, 950, 1920, 1080], fill=(0, 0, 0, 230))
    
    # Logo area
    draw.rectangle([1700, 20, 1900, 80], fill=(0, 0, 0, 180))
    
    # Try to use system font, fallback to default
    try:
        font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
        font_medium = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 30)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Add text
    draw.text((80, 25), "BREAKING", fill=(255, 255, 255, 255), font=font_medium)
    draw.text((1730, 35), "LIVE", fill=(255, 0, 0, 255), font=font_medium)
    draw.text((50, 970), "FUNNY NEWS NETWORK", fill=(255, 255, 255, 255), font=font_large)
    draw.text((500, 980), "Your source for news bloopers and fails", fill=(255, 255, 255, 200), font=font_small)
    
    # Save overlay
    overlay_path = "news_overlay.png"
    overlay.save(overlay_path)
    print(f"✅ Created overlay: {overlay_path}")
    
    return overlay_path

def create_clips_with_overlay(overlay_png):
    """Create video clips with overlay"""
    
    print("\n🎬 Creating clips with overlay...")
    
    clips_data = [
        {"title": "Reporter Falls in Pool", "location": "Miami Beach", "color": "0x4169E1"},
        {"title": "Weather Shows 1000°F", "location": "Weather Center", "color": "0x228B22"},
        {"title": "Mascot Trips Over", "location": "Sports Arena", "color": "0xFF4500"},
        {"title": "Anchor Can't Stop Laughing", "location": "News Studio", "color": "0x9370DB"},
        {"title": "Cat Interrupts Interview", "location": "Home Office", "color": "0xDC143C"}
    ]
    
    os.makedirs("temp_clips", exist_ok=True)
    clip_files = []
    
    for i, clip in enumerate(clips_data):
        output = f"temp_clips/clip_{i}.mp4"
        
        # Create base video with color and text
        filter_str = (
            f"drawtext=text='{clip['title']}':fontsize=50:fontcolor=white:"
            f"x=300:y=30:enable='between(t,0,4)',"
            f"drawtext=text='{clip['location']}':fontsize=30:fontcolor=white:"
            f"x=100:y=990:enable='between(t,0,4)'"
        )
        
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', f'color=c={clip["color"]}:size=1920x1080:duration=4',
            '-i', overlay_png,
            '-filter_complex',
            f'[0:v]{filter_str}[base];[base][1:v]overlay=0:0',
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-t', '4',
            output
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            clip_files.append(output)
            print(f"✅ Created: {clip['title']}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed: {e.stderr.decode()[:200]}...")
    
    return clip_files

def create_final_video(clip_files):
    """Concatenate clips into final video"""
    
    print("\n🎬 Creating final video...")
    
    # Create concat file
    concat_file = "temp_clips/concat.txt"
    with open(concat_file, 'w') as f:
        for clip in clip_files:
            f.write(f"file '{os.path.abspath(clip)}'\n")
    
    # Concatenate
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = f"funny_news_overlay_{timestamp}.mp4"
    
    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', concat_file,
        '-c:v', 'libx264',
        '-preset', 'medium',
        output
    ]
    
    subprocess.run(cmd, check=True, capture_output=True)
    
    return output

def main():
    print("""
🎬 FUNNY NEWS VIDEO WITH OVERLAY
================================
📸 Professional news broadcast style
⏱️  Duration: 20 seconds
🎨 Features: News ticker, logo, breaking banner
""")
    
    try:
        # Create overlay PNG
        overlay_png = create_overlay_png()
        
        # Create clips with overlay
        clips = create_clips_with_overlay(overlay_png)
        
        if not clips:
            print("❌ No clips created!")
            return
        
        # Create final video
        output = create_final_video(clips)
        
        # Cleanup
        os.remove(overlay_png)
        for clip in clips:
            os.remove(clip)
        if os.path.exists("temp_clips/concat.txt"):
            os.remove("temp_clips/concat.txt")
        if os.path.exists("temp_clips"):
            os.rmdir("temp_clips")
        
        # Get full path
        full_path = os.path.abspath(output)
        size = os.path.getsize(output) / (1024 * 1024)
        
        print(f"""
✅ SUCCESS!
============
📹 Full Path: {full_path}
📏 Size: {size:.2f} MB
⏱️  Duration: 20 seconds
🎬 Clips: 5 funny moments

📺 OVERLAY FEATURES:
- Breaking news banner (red box)
- LIVE indicator
- Bottom news ticker
- Location subtitles
- Professional styling
- Transparent overlay

🚫 NO VEO/AI generation
📸 Ready for real scraped media
""")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Check if PIL is installed
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("Installing required package: Pillow")
        subprocess.run(["pip3", "install", "Pillow"], check=True)
        from PIL import Image, ImageDraw, ImageFont
    
    main()