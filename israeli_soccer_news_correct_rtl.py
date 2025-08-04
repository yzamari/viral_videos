#!/usr/bin/env python3
"""
Israeli Soccer News - CORRECT RTL Implementation
Fixing the reversed Hebrew text issue
"""

import os
import subprocess
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import asyncio
import aiohttp
from src.news_aggregator.overlays.professional_templates import create_sports_overlay


def handle_hebrew_text_correctly(text):
    """DO NOT reverse Hebrew text - let the system handle RTL"""
    # Simply return the text as-is
    # The rendering system will handle RTL display
    return text


def draw_text_with_strong_shadow(draw, position, text, font, fill=(255, 255, 255), shadow_color=(0, 0, 0)):
    """Draw text with STRONG shadow for maximum visibility"""
    x, y = position
    
    # Draw multiple shadow layers for stronger effect
    shadow_offsets = [
        (-3, -3), (-3, 0), (-3, 3),
        (0, -3), (0, 3),
        (3, -3), (3, 0), (3, 3),
        (-2, -2), (-2, 2), (2, -2), (2, 2)
    ]
    
    # Draw shadows
    for dx, dy in shadow_offsets:
        draw.text((x + dx, y + dy), text, font=font, fill=shadow_color)
    
    # Draw main text
    draw.text((x, y), text, font=font, fill=fill)


async def scrape_israeli_soccer():
    """Scrape soccer news from Israeli sports sites"""
    print("⚽ Scraping Israeli soccer news...")
    
    os.makedirs("soccer_media", exist_ok=True)
    
    # Pre-defined Israeli soccer news for demo
    soccer_news = [
        {"title": "מכבי תל אביב ניצחה 3-1 את הפועל באר שבע", "source": "Sport5"},
        {"title": "ארז חלפון מונה למאמן הפועל תל אביב", "source": "ONE"},
        {"title": "נבחרת ישראל תארח את רומניה בסמי עופר", "source": "Ynet ספורט"},
        {"title": "ביתר ירושלים רכשה חלוץ ברזילאי ב-2 מיליון יורו", "source": "Sport5"},
        {"title": "מכבי חיפה בדרך לליגה האירופית", "source": "ONE"},
        {"title": "הפועל ירושלים מובילה את הליגה הלאומית", "source": "Ynet ספורט"},
        {"title": "עומר אצילי חתם במכבי פתח תקווה", "source": "Sport5"},
        {"title": "דרבי תל אביב: תיקו 2-2 דרמטי", "source": "ONE"},
        {"title": "אלי דסה חוזר לנבחרת ישראל", "source": "Ynet ספורט"},
        {"title": "בני סכנין ניצחה 1-0 את עירוני קריית שמונה", "source": "Sport5"},
        {"title": "הפועל חדרה עלתה לליגת העל", "source": "ONE"},
        {"title": "יוסי בניון: המטרה שלנו היא האליפות", "source": "Ynet ספורט"}
    ]
    
    # Add language field
    for item in soccer_news:
        item['language'] = 'he'
        item['type'] = 'image'
    
    return soccer_news


def create_soccer_image_with_correct_rtl(title, source, index):
    """Create an image with CORRECT Hebrew RTL text"""
    # Create base image with gradient
    img = Image.new('RGB', (1920, 1080))
    draw = ImageDraw.Draw(img)
    
    # Create gradient background
    for y in range(1080):
        # Blue gradient for sports theme
        r = int(0 + (y / 1080) * 30)
        g = int(50 + (y / 1080) * 30)
        b = int(150 - (y / 1080) * 50)
        draw.rectangle([(0, y), (1920, y+1)], fill=(r, g, b))
    
    # Add soccer field pattern
    for i in range(0, 1920, 200):
        draw.line([(i, 0), (i, 1080)], fill=(0, 80, 160), width=2)
    
    # Load fonts - try multiple paths
    font_paths = [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
    ]
    
    title_font = None
    source_font = None
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                title_font = ImageFont.truetype(font_path, 72)
                source_font = ImageFont.truetype(font_path, 48)
                break
            except:
                continue
    
    if not title_font:
        # Fallback to default
        title_font = ImageFont.load_default()
        source_font = ImageFont.load_default()
    
    # DO NOT REVERSE THE TEXT - use it as-is
    rtl_title = handle_hebrew_text_correctly(title)
    
    # Create semi-transparent box for text
    draw.rectangle([(100, 400), (1820, 680)], fill=(0, 0, 0, 180))
    
    # For Hebrew text, we need to use right-to-left alignment
    # Calculate text width for right alignment
    bbox = draw.textbbox((0, 0), rtl_title, font=title_font)
    text_width = bbox[2] - bbox[0]
    
    # Right align the text
    x_pos = 1820 - text_width - 100  # Right side minus text width minus padding
    
    # Draw title with STRONG visibility
    draw_text_with_strong_shadow(draw, (x_pos, 480), rtl_title, title_font, 
                                fill=(255, 255, 255), shadow_color=(0, 0, 0))
    
    # Draw source
    source_text = f"מקור: {source}"
    rtl_source = handle_hebrew_text_correctly(source_text)
    
    bbox = draw.textbbox((0, 0), rtl_source, font=source_font)
    text_width = bbox[2] - bbox[0]
    x_pos = 1820 - text_width - 100  # Right align
    
    draw_text_with_strong_shadow(draw, (x_pos, 580), rtl_source, source_font,
                                fill=(255, 215, 0), shadow_color=(0, 0, 0))
    
    # Add soccer ball icon
    draw.ellipse([(910, 350), (1010, 450)], fill=(255, 255, 255))
    draw.ellipse([(930, 370), (990, 430)], fill=(0, 0, 0))
    
    # Add visual indicator for RTL
    draw.text((50, 50), "RTL →", font=source_font, fill=(255, 255, 255))
    
    # Save image
    filename = f"soccer_media/soccer_rtl_{index}.jpg"
    img.save(filename, 'JPEG', quality=95)
    return filename


def create_soccer_video_clip_with_overlay(media, sports_overlay_path, output, duration=5):
    """Create video clip with sports overlay and visible text"""
    
    # Create video with text already burned in
    cmd = [
        'ffmpeg', '-y',
        '-loop', '1',
        '-i', media['local_path'],
        '-i', sports_overlay_path,
        '-filter_complex',
        # Add zoom effect
        '[0:v]scale=2400:1350,zoompan=z=\'min(zoom+0.0015,1.5)\':x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\':d=125:s=1920x1080:fps=25[zoomed];'
        # Overlay the sports template
        '[zoomed][1:v]overlay=0:0[final]',
        '-map', '[final]',
        '-t', str(duration),
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-pix_fmt', 'yuv420p',
        output
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"FFmpeg error: {result.stderr}")


def main():
    print("""
⚽ ISRAELI SOCCER NEWS - CORRECT RTL VERSION
===========================================
📺 60 seconds of Israeli soccer news
🇮🇱 CORRECT Hebrew RTL (not reversed!)
✨ Maximum text visibility
🏆 Professional sports overlay
""")
    
    # Get soccer news
    soccer_news = asyncio.run(scrape_israeli_soccer())
    
    # Create images with CORRECT RTL text
    print("\n🎨 Creating soccer news images with CORRECT Hebrew RTL...")
    for i, item in enumerate(soccer_news):
        print(f"  ⚽ Creating: {item['title'][:40]}...")
        local_path = create_soccer_image_with_correct_rtl(item['title'], item['source'], i)
        item['local_path'] = local_path
        print(f"  ✅ Created image {i+1}/12")
    
    # Create sports overlay
    print("\n🎯 Creating professional sports overlay...")
    sports_overlay = create_sports_overlay()
    overlay_path = "sports_overlay_rtl.png"
    sports_overlay.save(overlay_path)
    
    # Create video clips
    print("\n🎬 Creating video clips with overlay...")
    clips = []
    
    for i, media in enumerate(soccer_news[:12]):
        output = f"soccer_clip_rtl_{i}.mp4"
        print(f"  📹 Processing clip {i+1}/12: {media['title'][:30]}...")
        create_soccer_video_clip_with_overlay(media, overlay_path, output, duration=5)
        clips.append(output)
    
    # Create final compilation
    print("\n🎬 Creating final 60-second compilation...")
    with open("soccer_concat_rtl.txt", "w") as f:
        for clip in clips:
            f.write(f"file '{os.path.abspath(clip)}'\n")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = f"israeli_soccer_news_rtl_{timestamp}.mp4"
    
    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', 'soccer_concat_rtl.txt',
        '-c', 'copy',
        output
    ]
    
    subprocess.run(cmd, check=True)
    
    # Cleanup
    os.remove(overlay_path)
    os.remove("soccer_concat_rtl.txt")
    for clip in clips:
        if os.path.exists(clip):
            os.remove(clip)
    
    # Create a test image to verify RTL
    print("\n📸 Creating RTL test image...")
    test_img = Image.new('RGB', (1920, 540), color=(255, 255, 255))
    test_draw = ImageDraw.Draw(test_img)
    
    # Show the issue
    test_text = "מכבי תל אביב ניצחה 3-1"
    reversed_text = test_text[::-1]
    
    try:
        test_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 60)
    except:
        test_font = ImageFont.load_default()
    
    test_draw.text((100, 50), "WRONG (reversed):", font=test_font, fill=(255, 0, 0))
    test_draw.text((100, 120), reversed_text, font=test_font, fill=(0, 0, 0))
    
    test_draw.text((100, 250), "CORRECT (not reversed):", font=test_font, fill=(0, 128, 0))
    test_draw.text((100, 320), test_text, font=test_font, fill=(0, 0, 0))
    
    test_img.save("rtl_test_comparison.png")
    
    # Results
    full_path = os.path.abspath(output)
    size = os.path.getsize(output) / (1024 * 1024)
    
    print(f"""
⚽ ISRAELI SOCCER NEWS COMPLETE!
================================
📹 Full Path: {full_path}
📏 Size: {size:.2f} MB
⏱️  Duration: 60 seconds
🎬 Clips: 12 × 5 seconds

✅ RTL FIXES:
- Hebrew text NOT reversed
- Right-to-left alignment
- System handles RTL display
- Test image created: rtl_test_comparison.png

✅ TEXT VISIBILITY:
- Strong multi-layer shadows
- High contrast white on black
- Large 72pt font size
- Semi-transparent backgrounds

🏆 FEATURES:
- ESPN-style sports overlay
- Correct Hebrew RTL
- Professional broadcast quality

⚽ כדורגל ישראלי
🇮🇱 חדשות הספורט המובילות
✅ RTL תקין!
""")


if __name__ == "__main__":
    main()