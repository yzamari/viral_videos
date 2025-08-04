#!/usr/bin/env python3
"""
Demonstrate All 100 News Transitions
Creates a showcase video with every transition type
"""

import os
import subprocess
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import asyncio
from src.news_aggregator.transitions.transition_library import NewsTransitions


def create_transition_demo_frame(transition_name, category, number, total):
    """Create a frame showing transition info"""
    
    img = Image.new('RGB', (1920, 1080))
    draw = ImageDraw.Draw(img)
    
    # Background gradient
    for y in range(1080):
        gray = int(30 + (y / 1080) * 50)
        draw.rectangle([(0, y), (1920, y+1)], fill=(gray, gray, gray))
    
    # Load fonts
    try:
        font_huge = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 120)
        font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 80)
        font_medium = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
    except:
        font_huge = ImageFont.load_default()
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Category color coding
    category_colors = {
        "classic": (100, 100, 255),
        "slide": (100, 255, 100),
        "fade": (255, 100, 100),
        "geometric": (255, 255, 100),
        "squeeze": (255, 100, 255),
        "creative": (100, 255, 255),
        "digital": (255, 150, 50),
        "news": (255, 50, 50),
        "sports": (50, 255, 50),
        "special": (255, 50, 255)
    }
    
    color = category_colors.get(category, (200, 200, 200))
    
    # Draw transition number
    draw.text((100, 100), f"{number}", fill=color, font=font_huge)
    draw.text((300, 150), f"/ {total}", fill=(150, 150, 150), font=font_medium)
    
    # Draw transition name
    draw.text((960, 400), transition_name.upper(), fill=(255, 255, 255), 
              font=font_large, anchor="ma")
    
    # Draw category
    draw.rectangle([(710, 550), (1210, 650)], fill=color)
    draw.text((960, 580), category.upper(), fill=(0, 0, 0), 
              font=font_medium, anchor="ma")
    
    # Progress bar
    progress = (number / total) * 1920
    draw.rectangle([(0, 1060), (1920, 1080)], fill=(50, 50, 50))
    draw.rectangle([(0, 1060), (progress, 1080)], fill=color)
    
    return img


async def create_transition_showcase():
    """Create a video showcasing all 100 transitions"""
    
    print("""
🎬 CREATING TRANSITION SHOWCASE VIDEO
====================================
📊 100 unique transitions
🎨 10 categories
⏱️  ~3 minutes total
""")
    
    transitions = NewsTransitions()
    os.makedirs("transition_showcase", exist_ok=True)
    
    # Get all transitions
    all_transitions = list(transitions.transitions.items())
    total = len(all_transitions)
    
    print(f"\n📊 Creating {total} transition demonstrations...")
    
    segments = []
    frame_duration = 1.5  # Show each transition for 1.5 seconds
    
    # Create intro
    print("\n🎬 Creating intro...")
    intro_img = Image.new('RGB', (1920, 1080), color=(20, 20, 20))
    draw = ImageDraw.Draw(intro_img)
    
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 100)
        font_sub = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
    except:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
    
    draw.text((960, 300), "100 NEWS TRANSITIONS", fill=(255, 255, 255), 
              font=font_title, anchor="ma")
    draw.text((960, 450), "Professional Broadcast Effects", fill=(200, 200, 200), 
              font=font_sub, anchor="ma")
    draw.text((960, 600), "Transition Library Showcase", fill=(150, 150, 150), 
              font=font_sub, anchor="ma")
    
    # Category legend
    categories = transitions.get_categories()
    y_pos = 750
    x_start = 300
    for i, cat in enumerate(categories[:5]):
        cat_color = {
            "classic": (100, 100, 255),
            "slide": (100, 255, 100),
            "fade": (255, 100, 100),
            "geometric": (255, 255, 100),
            "squeeze": (255, 100, 255)
        }.get(cat, (200, 200, 200))
        
        draw.rectangle([(x_start + i*280, y_pos), (x_start + i*280 + 20, y_pos + 20)], 
                      fill=cat_color)
        draw.text((x_start + i*280 + 30, y_pos), cat.upper(), 
                 fill=(200, 200, 200), font=font_sub)
    
    intro_path = "transition_showcase/intro.jpg"
    intro_img.save(intro_path)
    
    # Convert to video
    intro_video = "transition_showcase/intro.mp4"
    cmd = [
        'ffmpeg', '-y',
        '-loop', '1',
        '-i', intro_path,
        '-t', '5',
        '-vf', 'fade=t=in:d=1,fade=t=out:st=4:d=1',
        '-c:v', 'libx264',
        '-preset', 'fast',
        intro_video
    ]
    subprocess.run(cmd, capture_output=True)
    segments.append(intro_video)
    os.remove(intro_path)
    
    # Create frames for each transition
    print("\n📹 Creating transition demonstrations...")
    
    current_category = None
    for i, (name, transition_data) in enumerate(all_transitions):
        category = transition_data["category"]
        
        # Add category intro if new category
        if category != current_category:
            print(f"\n🎨 {category.upper()} transitions:")
            current_category = category
            
            # Create category intro frame
            cat_img = Image.new('RGB', (1920, 1080))
            draw = ImageDraw.Draw(cat_img)
            
            # Category background
            cat_color = {
                "classic": (100, 100, 255),
                "slide": (100, 255, 100),
                "fade": (255, 100, 100),
                "geometric": (255, 255, 100),
                "squeeze": (255, 100, 255),
                "creative": (100, 255, 255),
                "digital": (255, 150, 50),
                "news": (255, 50, 50),
                "sports": (50, 255, 50),
                "special": (255, 50, 255)
            }.get(category, (200, 200, 200))
            
            for y in range(1080):
                fade = 1 - (y / 1080) * 0.7
                r = int(cat_color[0] * fade)
                g = int(cat_color[1] * fade)
                b = int(cat_color[2] * fade)
                draw.rectangle([(0, y), (1920, y+1)], fill=(r, g, b))
            
            draw.text((960, 450), category.upper(), fill=(255, 255, 255), 
                     font=font_title, anchor="ma")
            draw.text((960, 600), f"{len(transitions.get_transitions_by_category(category))} Transitions", 
                     fill=(255, 255, 255), font=font_sub, anchor="ma")
            
            cat_path = f"transition_showcase/cat_{category}.jpg"
            cat_img.save(cat_path)
            
            cat_video = f"transition_showcase/cat_{category}.mp4"
            cmd = [
                'ffmpeg', '-y',
                '-loop', '1',
                '-i', cat_path,
                '-t', '2',
                '-vf', 'fade=t=in:d=0.5,fade=t=out:st=1.5:d=0.5',
                '-c:v', 'libx264',
                '-preset', 'fast',
                cat_video
            ]
            subprocess.run(cmd, capture_output=True)
            segments.append(cat_video)
            os.remove(cat_path)
        
        # Create transition demo frame
        if i % 10 == 0:
            print(f"  Processing transitions {i+1}-{min(i+10, total)}...")
        
        frame = create_transition_demo_frame(name, category, i+1, total)
        frame_path = f"transition_showcase/trans_{i:03d}.jpg"
        frame.save(frame_path)
        
        # Convert to video
        video_path = f"transition_showcase/trans_{i:03d}.mp4"
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', frame_path,
            '-t', str(frame_duration),
            '-vf', 'scale=1920:1080',
            '-c:v', 'libx264',
            '-preset', 'fast',
            video_path
        ]
        subprocess.run(cmd, capture_output=True)
        segments.append(video_path)
        os.remove(frame_path)
    
    # Create outro
    print("\n🎬 Creating outro...")
    outro_img = Image.new('RGB', (1920, 1080), color=(20, 20, 20))
    draw = ImageDraw.Draw(outro_img)
    
    draw.text((960, 350), "100 TRANSITIONS", fill=(255, 255, 255), 
              font=font_title, anchor="ma")
    draw.text((960, 500), "Ready for Professional Broadcasting", fill=(200, 200, 200), 
              font=font_sub, anchor="ma")
    draw.text((960, 650), f"{len(categories)} Categories • {total} Effects", 
              fill=(150, 150, 150), font=font_sub, anchor="ma")
    
    outro_path = "transition_showcase/outro.jpg"
    outro_img.save(outro_path)
    
    outro_video = "transition_showcase/outro.mp4"
    cmd = [
        'ffmpeg', '-y',
        '-loop', '1',
        '-i', outro_path,
        '-t', '3',
        '-vf', 'fade=t=in:d=1,fade=t=out:st=2:d=1',
        '-c:v', 'libx264',
        '-preset', 'fast',
        outro_video
    ]
    subprocess.run(cmd, capture_output=True)
    segments.append(outro_video)
    os.remove(outro_path)
    
    # Compile final video
    print("\n🎬 Compiling showcase video...")
    concat_file = "transition_showcase/concat.txt"
    with open(concat_file, 'w') as f:
        for segment in segments:
            f.write(f"file '{os.path.abspath(segment)}'\n")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"transition_showcase/transitions_showcase_{timestamp}.mp4"
    
    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', concat_file,
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        output_path
    ]
    subprocess.run(cmd, capture_output=True)
    
    # Cleanup
    os.remove(concat_file)
    for segment in segments:
        if os.path.exists(segment):
            os.remove(segment)
    
    # Calculate duration
    total_duration = 5 + (len(categories) * 2) + (total * frame_duration) + 3
    minutes = int(total_duration // 60)
    seconds = int(total_duration % 60)
    
    print(f"""
✅ TRANSITION SHOWCASE COMPLETE!
===============================
📹 Video: {output_path}
⏱️  Duration: {minutes}:{seconds:02d}
🎬 Transitions: {total}
📊 Categories: {len(categories)}

📋 CATEGORIES SHOWCASED:
""")
    
    for cat in categories:
        cat_trans = transitions.get_transitions_by_category(cat)
        print(f"  • {cat.upper()}: {len(cat_trans)} transitions")
    
    print("""
🎯 USAGE:
- Use for selecting transitions
- Reference for effect names
- Category comparisons
- Speed demonstrations

✨ All 100 transitions ready for your news broadcasts!
""")
    
    return output_path


if __name__ == "__main__":
    # First create the Hebrew video
    print("=" * 60)
    print("PART 1: Creating Hebrew News Video")
    print("=" * 60)
    asyncio.run(create_professional_hebrew_video())
    
    # Then create the transition showcase
    print("\n" + "=" * 60)
    print("PART 2: Creating Transition Showcase")
    print("=" * 60)
    asyncio.run(create_transition_showcase())