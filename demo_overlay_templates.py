#!/usr/bin/env python3
"""
Demo: Using Professional Overlay Templates
Shows how to use different templates for different content types
"""

import os
import subprocess
from datetime import datetime
from src.news_aggregator.overlays.professional_templates import (
    create_general_news_overlay,
    create_sports_overlay,
    create_gossip_overlay,
    create_finance_overlay,
    create_tech_overlay,
    create_breaking_news_overlay
)


def create_demo_video(template_name, overlay_func, title, duration=10):
    """Create a demo video with the specified overlay template"""
    
    print(f"\n🎬 Creating {template_name} demo...")
    
    # Create overlay
    overlay = overlay_func()
    overlay_path = f"demo_{template_name}_overlay.png"
    overlay.save(overlay_path)
    
    # Create base video with appropriate color
    colors = {
        'general_news': '0x003366',  # Dark blue
        'sports': '0x006600',        # Dark green
        'gossip': '0x660066',        # Purple
        'finance': '0x000033',       # Very dark blue
        'tech': '0x001133',          # Dark tech blue
        'breaking_news': '0x330000'  # Dark red
    }
    
    color = colors.get(template_name, '0x333333')
    output = f"demo_{template_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    
    # Create video with overlay
    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi',
        '-i', f'color=c={color}:size=1920x1080:duration={duration}',
        '-i', overlay_path,
        '-filter_complex',
        '[0:v][1:v]overlay=0:0',
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-t', str(duration),
        output
    ]
    
    subprocess.run(cmd, capture_output=True)
    
    # Cleanup
    os.remove(overlay_path)
    
    print(f"✅ Created: {output}")
    return output


def main():
    print("""
🎨 PROFESSIONAL OVERLAY TEMPLATES DEMO
=====================================
Creating demo videos with each template...
""")
    
    demos = [
        ('general_news', create_general_news_overlay, "CNN-Style General News"),
        ('sports', create_sports_overlay, "ESPN-Style Sports Coverage"),
        ('gossip', create_gossip_overlay, "TMZ-Style Celebrity News"),
        ('finance', create_finance_overlay, "Bloomberg-Style Finance"),
        ('tech', create_tech_overlay, "Tech News Futuristic"),
        ('breaking_news', create_breaking_news_overlay, "Urgent Breaking News")
    ]
    
    created_videos = []
    
    for template_name, overlay_func, title in demos:
        video = create_demo_video(template_name, overlay_func, title, duration=5)
        created_videos.append(video)
    
    # Create compilation
    print("\n🎬 Creating compilation of all templates...")
    
    with open("templates_concat.txt", "w") as f:
        for video in created_videos:
            f.write(f"file '{os.path.abspath(video)}'\n")
    
    output = f"overlay_templates_showcase_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    
    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', 'templates_concat.txt',
        '-c', 'copy',
        output
    ]
    
    subprocess.run(cmd, check=True)
    
    # Cleanup
    os.remove("templates_concat.txt")
    for video in created_videos:
        if os.path.exists(video):
            os.remove(video)
    
    print(f"""
✅ OVERLAY TEMPLATES SHOWCASE COMPLETE!
======================================
📹 Output: {os.path.abspath(output)}
📏 Duration: 30 seconds (6 templates × 5 seconds)

🎨 Templates Included:
1. General News (CNN-style)
2. Sports (ESPN-style)
3. Gossip (TMZ-style)
4. Finance (Bloomberg-style)
5. Tech (Futuristic style)
6. Breaking News (Urgent alerts)

💡 Usage Examples:

# For general news:
from src.news_aggregator.overlays.professional_templates import create_general_news_overlay
overlay = create_general_news_overlay()

# For sports:
from src.news_aggregator.overlays.professional_templates import create_sports_overlay
overlay = create_sports_overlay()

# Apply to your video processing pipeline!
""")


if __name__ == "__main__":
    main()