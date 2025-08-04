#!/usr/bin/env python3
"""
Enhanced News Overlay with Better Visibility and RTL Support
"""

import os
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime


def reverse_hebrew_text(text):
    """Properly reverse Hebrew text for RTL display"""
    # Check if text contains Hebrew characters
    hebrew_chars = any('\u0590' <= char <= '\u05FF' for char in text)
    
    if hebrew_chars:
        # Split by spaces to preserve word order
        words = text.split()
        # Reverse each word individually
        reversed_words = [word[::-1] for word in words]
        # Join in reverse order
        return ' '.join(reversed(reversed_words))
    
    return text


def create_enhanced_news_overlay(width=1920, height=1080, language='en'):
    """Create professional news overlay with better visibility"""
    
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # --- TOP BANNER ---
    # Darker background for better contrast
    draw.rectangle([0, 0, width, 110], fill=(0, 0, 0, 240))
    
    # Breaking news box - brighter red
    draw.rectangle([40, 15, 270, 80], fill=(220, 20, 20, 255))
    # Add white border for better visibility
    draw.rectangle([40, 15, 270, 80], outline=(255, 255, 255, 255), width=2)
    
    # Live indicator box
    draw.rectangle([width-150, 15, width-40, 80], fill=(255, 0, 0, 255))
    draw.rectangle([width-150, 15, width-40, 80], outline=(255, 255, 255, 255), width=2)
    
    # --- BOTTOM TICKER ---
    # Darker background with gradient
    for i in range(150):
        alpha = int(200 + (i * 0.4))  # Gradient from 200 to 255
        y_pos = height - 150 + i
        draw.rectangle([0, y_pos, width, y_pos + 1], fill=(0, 0, 0, min(alpha, 255)))
    
    # Red accent bar at bottom
    draw.rectangle([0, height-5, width, height], fill=(220, 20, 20, 255))
    
    # --- FONTS ---
    font_paths = [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Avenir.ttc"
    ]
    
    font_large = None
    font_medium = None
    font_small = None
    
    for path in font_paths:
        if os.path.exists(path):
            try:
                font_large = ImageFont.truetype(path, 48)
                font_medium = ImageFont.truetype(path, 36)
                font_small = ImageFont.truetype(path, 24)
                break
            except:
                continue
    
    if not font_large:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # --- TEXT WITH SHADOWS FOR BETTER VISIBILITY ---
    
    # BREAKING text - white with shadow
    shadow_offset = 2
    # Shadow
    draw.text((60 + shadow_offset, 32 + shadow_offset), "BREAKING", 
              fill=(0, 0, 0, 255), font=font_medium)
    # Main text
    draw.text((60, 32), "BREAKING", fill=(255, 255, 255, 255), font=font_medium)
    
    # LIVE text - white with shadow
    # Shadow
    draw.text((width-120 + shadow_offset, 32 + shadow_offset), "LIVE", 
              fill=(0, 0, 0, 255), font=font_medium)
    # Main text
    draw.text((width-120, 32), "LIVE", fill=(255, 255, 255, 255), font=font_medium)
    
    # --- BOTTOM TEXT ---
    if language == 'he':
        # Hebrew text - RTL
        hebrew_text = "רשת החדשות העולמית"
        rtl_text = reverse_hebrew_text(hebrew_text)
        
        # Calculate position for right alignment
        bbox = draw.textbbox((0, 0), rtl_text, font=font_large)
        text_width = bbox[2] - bbox[0]
        x_pos = width - 60 - text_width
        
        # Shadow
        draw.text((x_pos + shadow_offset, height-75 + shadow_offset), rtl_text, 
                  fill=(0, 0, 0, 255), font=font_large)
        # Main text - bright white
        draw.text((x_pos, height-75), rtl_text, fill=(255, 255, 255, 255), font=font_large)
        
        # Time in Hebrew format
        time_text = datetime.now().strftime("%H:%M")
        # Shadow
        draw.text((x_pos + shadow_offset, height-40 + shadow_offset), time_text, 
                  fill=(0, 0, 0, 255), font=font_small)
        # Main text
        draw.text((x_pos, height-40), time_text, fill=(200, 200, 200, 255), font=font_small)
        
    else:
        # English text - LTR
        # Shadow
        draw.text((60 + shadow_offset, height-75 + shadow_offset), "WORLD NEWS NETWORK", 
                  fill=(0, 0, 0, 255), font=font_large)
        # Main text
        draw.text((60, height-75), "WORLD NEWS NETWORK", fill=(255, 255, 255, 255), font=font_large)
        
        # Subtitle
        draw.text((60 + shadow_offset, height-40 + shadow_offset), "Breaking News • Live Coverage • 24/7", 
                  fill=(0, 0, 0, 255), font=font_small)
        draw.text((60, height-40), "Breaking News • Live Coverage • 24/7", 
                  fill=(200, 200, 200, 255), font=font_small)
    
    # Time/Date box (right side)
    time_box_width = 200
    draw.rectangle([width-time_box_width-40, height-100, width-40, height-50], 
                   fill=(220, 20, 20, 255))
    
    # Current time
    current_time = datetime.now().strftime("%H:%M")
    bbox = draw.textbbox((0, 0), current_time, font=font_medium)
    text_width = bbox[2] - bbox[0]
    x_pos = width - 40 - time_box_width//2 - text_width//2
    
    draw.text((x_pos, height-90), current_time, fill=(255, 255, 255, 255), font=font_medium)
    
    return overlay


def apply_text_to_frame(frame_img, title, source, language='en'):
    """Apply text overlays to a video frame with proper RTL support"""
    
    draw = ImageDraw.Draw(frame_img)
    
    # Load fonts
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 56)
        font_source = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 32)
    except:
        font_title = ImageFont.load_default()
        font_source = ImageFont.load_default()
    
    # Process text for RTL if Hebrew
    if language == 'he':
        title = reverse_hebrew_text(title)
        
        # Title - right aligned with shadow
        bbox = draw.textbbox((0, 0), title, font=font_title)
        text_width = bbox[2] - bbox[0]
        x_pos = 1860 - text_width
        
        # Shadow
        draw.text((x_pos + 3, 33), title, fill=(0, 0, 0, 255), font=font_title)
        # Main text - bright white
        draw.text((x_pos, 30), title, fill=(255, 255, 255, 255), font=font_title)
        
        # Source - right aligned
        bbox = draw.textbbox((0, 0), source, font=font_source)
        text_width = bbox[2] - bbox[0]
        x_pos = 1860 - text_width
        
        # Shadow
        draw.text((x_pos + 2, 992), source, fill=(0, 0, 0, 255), font=font_source)
        # Main text
        draw.text((x_pos, 990), source, fill=(255, 255, 255, 255), font=font_source)
        
    else:
        # English - left aligned with shadow
        # Title shadow
        draw.text((303, 33), title, fill=(0, 0, 0, 255), font=font_title)
        # Title main
        draw.text((300, 30), title, fill=(255, 255, 255, 255), font=font_title)
        
        # Source shadow
        draw.text((102, 992), source, fill=(0, 0, 0, 255), font=font_source)
        # Source main
        draw.text((100, 990), source, fill=(255, 255, 255, 255), font=font_source)
    
    return frame_img


if __name__ == "__main__":
    # Test overlay creation
    print("Creating enhanced overlays...")
    
    # English overlay
    overlay_en = create_enhanced_news_overlay(language='en')
    overlay_en.save("news_overlay_enhanced_en.png")
    print("✅ Created: news_overlay_enhanced_en.png")
    
    # Hebrew overlay
    overlay_he = create_enhanced_news_overlay(language='he')
    overlay_he.save("news_overlay_enhanced_he.png")
    print("✅ Created: news_overlay_enhanced_he.png")
    
    print("\nFeatures:")
    print("- Higher contrast backgrounds")
    print("- Text shadows for visibility")
    print("- Proper RTL Hebrew support")
    print("- Brighter text colors")
    print("- Professional design")