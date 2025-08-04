#!/usr/bin/env python3
"""
Professional News Overlay Templates
Inspired by CNN, BBC, Fox News, ESPN, TMZ, E!, Bloomberg, etc.
"""

import os
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import math


def get_fonts(large_size=48, medium_size=36, small_size=24):
    """Get fonts with fallback"""
    font_paths = [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Avenir.ttc"
    ]
    
    for path in font_paths:
        if os.path.exists(path):
            try:
                return {
                    'large': ImageFont.truetype(path, large_size),
                    'medium': ImageFont.truetype(path, medium_size),
                    'small': ImageFont.truetype(path, small_size)
                }
            except:
                continue
    
    # Fallback
    return {
        'large': ImageFont.load_default(),
        'medium': ImageFont.load_default(),
        'small': ImageFont.load_default()
    }


def draw_text_with_shadow(draw, position, text, font, fill=(255, 255, 255, 255), shadow_offset=2):
    """Draw text with shadow for better visibility"""
    x, y = position
    # Shadow
    draw.text((x + shadow_offset, y + shadow_offset), text, 
              fill=(0, 0, 0, 255), font=font)
    # Main text
    draw.text((x, y), text, fill=fill, font=font)


def create_logo(draw, logo_type, position, size=(150, 60)):
    """Create simple logos for different channels"""
    x, y = position
    w, h = size
    
    if logo_type == "cnn":
        # CNN-style red box with white text
        draw.rectangle([x, y, x+w, y+h], fill=(204, 0, 0, 255))
        draw.rectangle([x, y, x+w, y+h], outline=(255, 255, 255, 255), width=2)
        font = get_fonts(large_size=40)['large']
        draw_text_with_shadow(draw, (x+w//2-40, y+10), "WNN", font)
        
    elif logo_type == "bbc":
        # BBC-style black boxes
        for i in range(3):
            box_x = x + i * 55
            draw.rectangle([box_x, y, box_x+50, y+h], fill=(0, 0, 0, 255))
            draw.rectangle([box_x, y, box_x+50, y+h], outline=(255, 255, 255, 255), width=2)
        font = get_fonts(large_size=32)['large']
        letters = ["W", "N", "N"]
        for i, letter in enumerate(letters):
            draw.text((x + i*55 + 15, y+12), letter, fill=(255, 255, 255, 255), font=font)
            
    elif logo_type == "fox":
        # Fox-style blue background
        draw.rectangle([x, y, x+w, y+h], fill=(0, 51, 102, 255))
        font = get_fonts(large_size=36)['large']
        draw_text_with_shadow(draw, (x+20, y+10), "NEWS", font)
        
    elif logo_type == "espn":
        # ESPN-style red background
        draw.rectangle([x, y, x+w, y+h], fill=(255, 0, 0, 255))
        font = get_fonts(large_size=36)['large']
        draw_text_with_shadow(draw, (x+15, y+10), "SPORT", font)
        
    elif logo_type == "tmz":
        # TMZ-style yellow/black
        draw.rectangle([x, y, x+w//2, y+h], fill=(255, 215, 0, 255))
        draw.rectangle([x+w//2, y, x+w, y+h], fill=(0, 0, 0, 255))
        font = get_fonts(large_size=36)['large']
        draw.text((x+10, y+10), "GOS", fill=(0, 0, 0, 255), font=font)
        draw.text((x+w//2+10, y+10), "SIP", fill=(255, 215, 0, 255), font=font)
        
    elif logo_type == "bloomberg":
        # Bloomberg-style gradient
        for i in range(h):
            color = int(255 * (1 - i/h))
            draw.rectangle([x, y+i, x+w, y+i+1], fill=(color, color, 255, 255))
        font = get_fonts(medium_size=28)['medium']
        draw_text_with_shadow(draw, (x+15, y+15), "FINANCE", font)
        
    elif logo_type == "tech":
        # Tech-style neon
        draw.rectangle([x, y, x+w, y+h], fill=(0, 255, 157, 255))
        draw.rectangle([x, y, x+w, y+h], outline=(255, 255, 255, 255), width=2)
        font = get_fonts(large_size=36)['large']
        draw.text((x+25, y+10), "TECH", fill=(0, 0, 0, 255), font=font)
        
    elif logo_type == "weather":
        # Weather channel style
        draw.ellipse([x, y, x+h, y+h], fill=(255, 165, 0, 255))
        draw.rectangle([x+h-5, y, x+w, y+h], fill=(0, 119, 190, 255))
        font = get_fonts(medium_size=28)['medium']
        draw_text_with_shadow(draw, (x+h+5, y+15), "WEATHER", font)
        
    elif logo_type == "entertainment":
        # E! style
        draw.ellipse([x, y, x+h, y+h], fill=(255, 0, 255, 255))
        font = get_fonts(large_size=40)['large']
        draw.text((x+18, y+8), "E", fill=(255, 255, 255, 255), font=font)
        draw.text((x+h+10, y+15), "NEWS", fill=(255, 0, 255, 255), font=get_fonts(medium_size=28)['medium'])
        
    elif logo_type == "documentary":
        # Documentary style - film reel
        draw.ellipse([x, y+10, x+40, y+50], fill=(50, 50, 50, 255))
        draw.ellipse([x+10, y+20, x+30, y+40], fill=(200, 200, 200, 255))
        font = get_fonts(medium_size=28)['medium']
        draw_text_with_shadow(draw, (x+50, y+18), "DOCS", font)


def create_general_news_overlay(width=1920, height=1080):
    """CNN-style general news overlay"""
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    fonts = get_fonts()
    
    # Top banner - CNN style
    draw.rectangle([0, 0, width, 120], fill=(0, 0, 0, 240))
    draw.rectangle([0, 120, width, 125], fill=(204, 0, 0, 255))
    
    # Logo
    create_logo(draw, "cnn", (50, 25))
    
    # Breaking news box
    draw.rectangle([250, 30, 450, 90], fill=(204, 0, 0, 255))
    draw_text_with_shadow(draw, (280, 45), "BREAKING", fonts['medium'])
    
    # Live indicator
    draw.ellipse([width-180, 40, width-160, 60], fill=(255, 0, 0, 255))
    draw_text_with_shadow(draw, (width-150, 35), "LIVE", fonts['medium'])
    
    # Bottom ticker area
    draw.rectangle([0, height-160, width, height], fill=(0, 0, 0, 240))
    draw.rectangle([0, height-160, width, height-155], fill=(204, 0, 0, 255))
    
    # Time box
    draw.rectangle([width-200, height-120, width-40, height-60], fill=(204, 0, 0, 255))
    
    return overlay


def create_sports_overlay(width=1920, height=1080):
    """ESPN-style sports overlay"""
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    fonts = get_fonts()
    
    # Top banner - ESPN style
    draw.rectangle([0, 0, width, 130], fill=(20, 20, 20, 240))
    draw.rectangle([0, 130, width, 135], fill=(255, 0, 0, 255))
    
    # Logo
    create_logo(draw, "espn", (50, 30))
    
    # Score boxes
    draw.rectangle([300, 20, 600, 110], fill=(40, 40, 40, 255))
    draw.rectangle([620, 20, 920, 110], fill=(40, 40, 40, 255))
    draw.rectangle([300, 20, 600, 25], fill=(255, 0, 0, 255))
    draw.rectangle([620, 20, 920, 25], fill=(0, 123, 255, 255))
    
    # Bottom bar
    draw.rectangle([0, height-140, width, height], fill=(20, 20, 20, 240))
    draw.rectangle([0, height-140, width, height-135], fill=(255, 215, 0, 255))
    
    # Stats boxes
    for i in range(3):
        x = 50 + i * 400
        draw.rectangle([x, height-120, x+350, height-40], fill=(40, 40, 40, 255), outline=(255, 255, 255, 100))
    
    return overlay


def create_gossip_overlay(width=1920, height=1080):
    """TMZ-style gossip overlay"""
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    fonts = get_fonts()
    
    # Top banner - TMZ style with angle
    points = [(0, 0), (width, 0), (width, 100), (0, 120)]
    draw.polygon(points, fill=(0, 0, 0, 240))
    draw.rectangle([0, 120, width, 125], fill=(255, 215, 0, 255))
    
    # Logo
    create_logo(draw, "tmz", (50, 25))
    
    # Exclusive banner
    draw.rectangle([300, 30, 500, 90], fill=(255, 215, 0, 255))
    draw_text_with_shadow(draw, (320, 45), "EXCLUSIVE", fonts['medium'], fill=(0, 0, 0, 255))
    
    # Bottom area with angle
    points = [(0, height-150), (width, height-130), (width, height), (0, height)]
    draw.polygon(points, fill=(0, 0, 0, 240))
    
    # Social media style comments area
    draw.rectangle([50, height-120, 400, height-40], fill=(40, 40, 40, 200), outline=(255, 215, 0, 255))
    
    return overlay


def create_tv_show_overlay(width=1920, height=1080):
    """Late night TV show style overlay"""
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    fonts = get_fonts()
    
    # Elegant top banner
    for i in range(100):
        alpha = int(240 * (1 - i/100))
        draw.rectangle([0, i, width, i+1], fill=(0, 0, 50, alpha))
    
    # Show name area
    draw.rectangle([width//2-200, 20, width//2+200, 80], fill=(138, 43, 226, 255))
    draw.rectangle([width//2-200, 20, width//2+200, 80], outline=(255, 255, 255, 255), width=3)
    
    # Bottom third
    draw.rectangle([0, height-200, width, height], fill=(0, 0, 0, 0))
    for i in range(200):
        alpha = int(240 * (i/200))
        draw.rectangle([0, height-200+i, width, height-199+i], fill=(0, 0, 50, alpha))
    
    # Guest name plate
    draw.rectangle([100, height-150, 600, height-50], fill=(138, 43, 226, 255))
    draw.rectangle([100, height-150, 600, height-50], outline=(255, 255, 255, 255), width=2)
    
    return overlay


def create_finance_overlay(width=1920, height=1080):
    """Bloomberg-style finance overlay"""
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    fonts = get_fonts()
    
    # Top banner
    draw.rectangle([0, 0, width, 100], fill=(0, 0, 0, 240))
    draw.rectangle([0, 100, width, 102], fill=(0, 100, 255, 255))
    
    # Logo
    create_logo(draw, "bloomberg", (50, 20))
    
    # Market indicators
    for i in range(4):
        x = 300 + i * 350
        draw.rectangle([x, 20, x+320, 80], fill=(20, 20, 20, 255))
        if i % 2 == 0:
            draw.polygon([(x+290, 40), (x+300, 30), (x+310, 40)], fill=(0, 255, 0, 255))
        else:
            draw.polygon([(x+290, 40), (x+300, 50), (x+310, 40)], fill=(255, 0, 0, 255))
    
    # Bottom ticker
    draw.rectangle([0, height-120, width, height], fill=(0, 0, 0, 240))
    draw.rectangle([0, height-120, width, height-118], fill=(0, 100, 255, 255))
    
    # Data grid
    for i in range(3):
        y = height-100 + i * 30
        draw.line([(50, y), (width-50, y)], fill=(100, 100, 100, 255))
    
    return overlay


def create_tech_overlay(width=1920, height=1080):
    """Tech news futuristic overlay"""
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    fonts = get_fonts()
    
    # Cyber-style top banner
    draw.rectangle([0, 0, width, 110], fill=(0, 20, 40, 230))
    for i in range(5):
        draw.rectangle([0, 110+i*2, width, 111+i*2], fill=(0, 255, 157, 255-i*50))
    
    # Logo
    create_logo(draw, "tech", (50, 25))
    
    # Data stream effect boxes
    for i in range(3):
        x = 300 + i * 400
        draw.rectangle([x, 30, x+350, 90], fill=(0, 40, 80, 200), outline=(0, 255, 157, 255))
    
    # Bottom area
    draw.rectangle([0, height-150, width, height], fill=(0, 20, 40, 230))
    
    # Circuit pattern decoration
    for i in range(5):
        x = 100 + i * 350
        draw.ellipse([x-5, height-80, x+5, height-70], fill=(0, 255, 157, 255))
        if i < 4:
            draw.line([(x+5, height-75), (x+345, height-75)], fill=(0, 255, 157, 100), width=2)
    
    return overlay


def create_weather_overlay(width=1920, height=1080):
    """Weather channel style overlay"""
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    fonts = get_fonts()
    
    # Top banner with gradient
    for i in range(120):
        blue = int(190 - i * 0.5)
        draw.rectangle([0, i, width, i+1], fill=(0, 119, blue, 230))
    
    # Logo
    create_logo(draw, "weather", (50, 30))
    
    # Temperature display
    draw.rectangle([width-250, 20, width-50, 100], fill=(255, 255, 255, 200))
    draw.rectangle([width-250, 20, width-50, 100], outline=(0, 119, 190, 255), width=3)
    
    # Bottom forecast bar
    draw.rectangle([0, height-180, width, height], fill=(0, 0, 0, 230))
    draw.rectangle([0, height-180, width, height-175], fill=(255, 165, 0, 255))
    
    # Forecast boxes
    for i in range(7):
        x = 50 + i * 260
        draw.rectangle([x, height-160, x+240, height-40], fill=(40, 40, 40, 200), outline=(255, 255, 255, 100))
    
    return overlay


def create_entertainment_overlay(width=1920, height=1080):
    """E! Entertainment style overlay"""
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    fonts = get_fonts()
    
    # Glamorous top banner
    draw.rectangle([0, 0, width, 110], fill=(255, 0, 255, 200))
    draw.rectangle([0, 110, width, 115], fill=(255, 255, 255, 255))
    
    # Logo
    create_logo(draw, "entertainment", (50, 25))
    
    # Star burst decoration
    for angle in range(0, 360, 45):
        x1 = 300 + 30 * math.cos(math.radians(angle))
        y1 = 55 + 30 * math.sin(math.radians(angle))
        x2 = 300 + 50 * math.cos(math.radians(angle))
        y2 = 55 + 50 * math.sin(math.radians(angle))
        draw.line([(x1, y1), (x2, y2)], fill=(255, 255, 255, 255), width=2)
    
    # Bottom area
    draw.rectangle([0, height-140, width, height], fill=(0, 0, 0, 200))
    draw.rectangle([0, height-140, width, height-135], fill=(255, 0, 255, 255))
    
    # Celebrity name plate
    draw.rectangle([100, height-110, 600, height-40], fill=(255, 255, 255, 200))
    draw.rectangle([100, height-110, 600, height-40], outline=(255, 0, 255, 255), width=3)
    
    return overlay


def create_breaking_news_overlay(width=1920, height=1080):
    """Urgent breaking news overlay"""
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    fonts = get_fonts()
    
    # Urgent red banner
    draw.rectangle([0, 0, width, 140], fill=(139, 0, 0, 240))
    for i in range(5):
        draw.rectangle([0, 140+i*3, width, 142+i*3], fill=(255, 0, 0, 255-i*50))
    
    # Flashing breaking news
    draw.rectangle([width//2-200, 30, width//2+200, 100], fill=(255, 255, 255, 255))
    draw.rectangle([width//2-200, 30, width//2+200, 100], outline=(139, 0, 0, 255), width=5)
    draw_text_with_shadow(draw, (width//2-100, 50), "BREAKING NEWS", fonts['large'], fill=(139, 0, 0, 255))
    
    # Alert indicators
    for i in range(2):
        x = 100 if i == 0 else width-150
        draw.rectangle([x, 40, x+50, 90], fill=(255, 255, 0, 255))
        draw_text_with_shadow(draw, (x+5, 55), "ALERT", get_fonts(small_size=20)['small'], fill=(0, 0, 0, 255))
    
    # Bottom urgent ticker
    draw.rectangle([0, height-160, width, height], fill=(139, 0, 0, 240))
    draw.rectangle([0, height-160, width, height-155], fill=(255, 255, 255, 255))
    
    return overlay


def create_documentary_overlay(width=1920, height=1080):
    """Documentary style minimal overlay"""
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    fonts = get_fonts()
    
    # Minimal top area
    for i in range(80):
        alpha = int(200 * (1 - i/80))
        draw.rectangle([0, i, width, i+1], fill=(0, 0, 0, alpha))
    
    # Logo
    create_logo(draw, "documentary", (50, 15))
    
    # Bottom area - cinematic letterbox
    for i in range(100):
        alpha = int(220 * (i/100))
        draw.rectangle([0, height-100+i, width, height-99+i], fill=(0, 0, 0, alpha))
    
    # Title area
    draw.rectangle([0, height-80, 800, height-20], fill=(0, 0, 0, 180))
    
    # Film frame decoration
    for i in range(width//100):
        x = i * 100
        draw.rectangle([x, 0, x+5, 10], fill=(255, 255, 255, 100))
        draw.rectangle([x, height-10, x+5, height], fill=(255, 255, 255, 100))
    
    return overlay


def create_all_templates():
    """Create all overlay templates"""
    templates = {
        'general_news': create_general_news_overlay(),
        'sports': create_sports_overlay(),
        'gossip': create_gossip_overlay(),
        'tv_show': create_tv_show_overlay(),
        'finance': create_finance_overlay(),
        'tech': create_tech_overlay(),
        'weather': create_weather_overlay(),
        'entertainment': create_entertainment_overlay(),
        'breaking_news': create_breaking_news_overlay(),
        'documentary': create_documentary_overlay()
    }
    
    # Save all templates
    os.makedirs("overlay_templates", exist_ok=True)
    
    for name, overlay in templates.items():
        overlay.save(f"overlay_templates/{name}_overlay.png")
        print(f"✅ Created: {name}_overlay.png")
    
    return templates


def preview_all_templates():
    """Create a preview image showing all templates"""
    # Create preview grid
    preview = Image.new('RGBA', (1920*2, 1080*5), (50, 50, 50, 255))
    templates = create_all_templates()
    
    positions = [
        ('general_news', 0, 0), ('sports', 1920, 0),
        ('gossip', 0, 1080), ('tv_show', 1920, 1080),
        ('finance', 0, 2160), ('tech', 1920, 2160),
        ('weather', 0, 3240), ('entertainment', 1920, 3240),
        ('breaking_news', 0, 4320), ('documentary', 1920, 4320)
    ]
    
    # Create background
    for name, x, y in positions:
        # Add dark background
        bg = Image.new('RGBA', (1920, 1080), (30, 30, 30, 255))
        preview.paste(bg, (x, y))
        
        # Add overlay
        overlay = templates[name]
        preview.paste(overlay, (x, y), overlay)
        
        # Add label
        draw = ImageDraw.Draw(preview)
        fonts = get_fonts(large_size=60)
        draw_text_with_shadow(draw, (x+50, y+500), name.upper().replace('_', ' '), 
                            fonts['large'], fill=(255, 255, 0, 255), shadow_offset=3)
    
    # Save preview
    preview_resized = preview.resize((1920, 5400), Image.Resampling.LANCZOS)
    preview_resized.save("overlay_templates/all_templates_preview.png")
    print("\n✅ Created preview: all_templates_preview.png")


if __name__ == "__main__":
    print("🎨 Creating Professional Overlay Templates...")
    print("=" * 50)
    
    # Create all templates
    create_all_templates()
    
    # Create preview
    preview_all_templates()
    
    print("\n📁 Templates saved in: overlay_templates/")
    print("\n🎬 Template Types:")
    print("1. General News - CNN-style professional news")
    print("2. Sports - ESPN-style with score displays")
    print("3. Gossip - TMZ-style celebrity news")
    print("4. TV Show - Late night talk show style")
    print("5. Finance - Bloomberg-style market data")
    print("6. Tech - Futuristic tech news design")
    print("7. Weather - Weather channel forecast style")
    print("8. Entertainment - E! glamorous style")
    print("9. Breaking News - Urgent alert design")
    print("10. Documentary - Cinematic minimal style")
    
    print("\n✨ Each template includes:")
    print("- Unique branding/logo design")
    print("- Category-specific styling")
    print("- Professional color schemes")
    print("- Text areas with shadows for visibility")
    print("- Industry-standard layouts")