#!/usr/bin/env python3
"""
Test Hebrew text visibility with maximum contrast
"""

from PIL import Image, ImageDraw, ImageFont
import os


def test_hebrew_text_rendering():
    """Create test image showing Hebrew text with maximum visibility"""
    
    # Create image
    img = Image.new('RGB', (1920, 1080), color=(0, 50, 150))
    draw = ImageDraw.Draw(img)
    
    # Load font
    font_paths = [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Helvetica.ttc"
    ]
    
    font = None
    for path in font_paths:
        if os.path.exists(path):
            try:
                font = ImageFont.truetype(path, 80)
                break
            except:
                continue
    
    if not font:
        font = ImageFont.load_default()
    
    # Test texts
    texts = [
        "מכבי תל אביב ניצחה 3-1",
        "הפועל תל אביב - דרבי",
        "נבחרת ישראל מול רומניה",
        "ליגת העל - סיכום המחזור"
    ]
    
    y_pos = 200
    
    for text in texts:
        # Draw background box
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x_center = (1920 - text_width) // 2
        
        # Black background box
        draw.rectangle(
            [(x_center - 50, y_pos - 20), (x_center + text_width + 50, y_pos + text_height + 20)],
            fill=(0, 0, 0)
        )
        
        # Draw text with strong shadow
        # Multiple shadow layers
        for dx in [-3, -2, -1, 0, 1, 2, 3]:
            for dy in [-3, -2, -1, 0, 1, 2, 3]:
                if dx != 0 or dy != 0:
                    draw.text((x_center + dx, y_pos + dy), text, font=font, fill=(0, 0, 0))
        
        # Main text in bright white
        draw.text((x_center, y_pos), text, font=font, fill=(255, 255, 255))
        
        # Also show the reversed version
        reversed_text = text[::-1]
        draw.text((x_center, y_pos + 100), f"Reversed: {reversed_text}", 
                 font=ImageFont.truetype(font_paths[0], 40) if font_paths[0] and os.path.exists(font_paths[0]) else font, 
                 fill=(255, 255, 0))
        
        y_pos += 200
    
    # Add instructions
    draw.rectangle([(50, 50), (1870, 150)], fill=(255, 255, 255))
    draw.text((100, 70), "Hebrew Text Visibility Test - Check if text appears correctly", 
             font=ImageFont.truetype(font_paths[0], 40) if font_paths[0] and os.path.exists(font_paths[0]) else font,
             fill=(0, 0, 0))
    
    # Save
    img.save("hebrew_text_visibility_test.png")
    print("Created: hebrew_text_visibility_test.png")
    print("\nText rendering features:")
    print("- White text on black background boxes")
    print("- Multiple shadow layers for contrast")
    print("- Large 80pt font size")
    print("- Shows both normal and reversed Hebrew")
    

if __name__ == "__main__":
    test_hebrew_text_rendering()