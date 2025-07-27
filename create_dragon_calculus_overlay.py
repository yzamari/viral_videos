#!/usr/bin/env python3
"""
Create Dragon Calculus Academy overlay with baby dragon and epsilon chicks
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_dragon_overlay():
    """Create a PNG overlay for the Dragon Calculus series"""
    
    # Create transparent image (1080x1920 for Instagram portrait)
    width, height = 1080, 1920
    overlay = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Try to load a font, fallback to default if not available
    try:
        # Try different font paths
        font_paths = [
            '/System/Library/Fonts/Helvetica.ttc',
            '/Library/Fonts/Arial.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
        ]
        title_font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                title_font = ImageFont.truetype(font_path, 36)
                small_font = ImageFont.truetype(font_path, 24)
                break
        if not title_font:
            title_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
    except:
        title_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Draw main logo area (top left corner)
    logo_x, logo_y = 50, 50
    logo_size = 150
    
    # Dragon circle background
    draw.ellipse([logo_x, logo_y, logo_x + logo_size, logo_y + logo_size], 
                 fill=(147, 51, 234, 200), outline=(75, 0, 130, 255), width=3)
    
    # Dragon features (simplified representation)
    # Eyes
    eye_size = 20
    draw.ellipse([logo_x + 40, logo_y + 50, logo_x + 40 + eye_size, logo_y + 50 + eye_size],
                 fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=2)
    draw.ellipse([logo_x + 90, logo_y + 50, logo_x + 90 + eye_size, logo_y + 50 + eye_size],
                 fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=2)
    
    # Pupils
    draw.ellipse([logo_x + 45, logo_y + 55, logo_x + 55, logo_y + 65],
                 fill=(0, 0, 0, 255))
    draw.ellipse([logo_x + 95, logo_y + 55, logo_x + 105, logo_y + 65],
                 fill=(0, 0, 0, 255))
    
    # Cute smile
    draw.arc([logo_x + 50, logo_y + 80, logo_x + 100, logo_y + 110],
             start=0, end=180, fill=(255, 182, 193, 255), width=3)
    
    # Tiny glasses
    draw.ellipse([logo_x + 35, logo_y + 45, logo_x + 65, logo_y + 75],
                 fill=(255, 255, 255, 0), outline=(0, 0, 0, 255), width=2)
    draw.ellipse([logo_x + 85, logo_y + 45, logo_x + 115, logo_y + 75],
                 fill=(255, 255, 255, 0), outline=(0, 0, 0, 255), width=2)
    draw.line([logo_x + 65, logo_y + 60, logo_x + 85, logo_y + 60],
              fill=(0, 0, 0, 255), width=2)
    
    # Title text
    draw.text((logo_x + logo_size + 20, logo_y + 30), "Dragon Calculus", 
              font=title_font, fill=(147, 51, 234, 255))
    draw.text((logo_x + logo_size + 20, logo_y + 70), "Academy", 
              font=title_font, fill=(147, 51, 234, 255))
    
    # Epsilon chicks in bottom right
    chick_x = width - 250
    chick_y = height - 200
    
    # Draw 3 epsilon chicks
    for i in range(3):
        x = chick_x + i * 70
        y = chick_y + (i % 2) * 20  # Slight vertical offset
        
        # Chick body (epsilon shape)
        draw.text((x, y), "ε", font=ImageFont.truetype(font_path, 60) if 'font_path' in locals() else title_font,
                  fill=(255, 215, 0, 255))
        
        # Thought bubble
        bubble_x = x - 10
        bubble_y = y - 50
        draw.ellipse([bubble_x, bubble_y, bubble_x + 80, bubble_y + 40],
                     fill=(255, 255, 255, 200), outline=(0, 0, 0, 255), width=2)
        
        # Thinking dots
        for j in range(3):
            dot_x = bubble_x + 15 + j * 20
            dot_y = bubble_y + 15
            draw.ellipse([dot_x, dot_y, dot_x + 8, dot_y + 8],
                         fill=(0, 0, 0, 255))
    
    # Add subtle math symbols floating around
    math_symbols = ["∫", "∂", "∑", "∞", "π", "√"]
    symbol_positions = [
        (200, 300), (800, 400), (150, 600), 
        (900, 800), (100, 1000), (850, 1200)
    ]
    
    for symbol, pos in zip(math_symbols, symbol_positions):
        draw.text(pos, symbol, font=small_font, 
                  fill=(147, 51, 234, 50))  # Very transparent
    
    # Episode number placeholder (bottom left)
    draw.rectangle([50, height - 150, 200, height - 50],
                   fill=(147, 51, 234, 180), outline=(75, 0, 130, 255), width=3)
    draw.text((75, height - 120), "Episode", font=small_font, fill=(255, 255, 255, 255))
    draw.text((95, height - 85), "#", font=title_font, fill=(255, 255, 255, 255))
    
    # Save the overlay
    output_path = "dragon_calculus_overlay.png"
    overlay.save(output_path, "PNG")
    print(f"✅ Overlay created: {output_path}")
    print(f"📐 Dimensions: {width}x{height}")
    print(f"🐉 Features: Baby dragon logo, epsilon chicks, math symbols")
    
    return output_path

if __name__ == "__main__":
    create_dragon_overlay()
    print("\n🎨 To use this overlay:")
    print("1. The overlay is transparent - perfect for video composition")
    print("2. Episode numbers can be added dynamically")
    print("3. The design maintains Family Guy animation style")
    print("4. Consistent branding across all episodes")