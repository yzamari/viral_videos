#!/usr/bin/env python3
"""
Create AI University Logo for Dragon Calculus Series
A humorous logo combining AI, university, and dragon elements
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_ai_university_logo():
    """Create a humorous AI University logo with dragon elements"""
    
    # Create a transparent image
    width, height = 400, 150
    logo = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(logo)
    
    # Colors
    purple = (138, 43, 226)  # Dragon purple
    white = (255, 255, 255)
    gold = (255, 215, 0)
    dark_purple = (75, 0, 130)
    
    # Draw shield/badge background
    # Rounded rectangle for university badge feel
    badge_coords = [(10, 10), (width-10, height-10)]
    draw.rounded_rectangle(badge_coords, radius=20, fill=(*purple, 200), outline=(*white, 255), width=3)
    
    # Try to use a good font, fallback to default if not available
    try:
        # Try different font paths based on OS
        font_paths = [
            '/System/Library/Fonts/Helvetica.ttc',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            'C:\\Windows\\Fonts\\arial.ttf'
        ]
        title_font = None
        subtitle_font = None
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                title_font = ImageFont.truetype(font_path, 36)
                subtitle_font = ImageFont.truetype(font_path, 18)
                break
        
        if not title_font:
            # Use default font
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Draw dragon emoji/symbol (simplified dragon head)
    # Dragon head circle
    dragon_x = 40
    dragon_y = height // 2
    draw.ellipse([(dragon_x-25, dragon_y-25), (dragon_x+25, dragon_y+25)], 
                 fill=(*dark_purple, 255), outline=(*gold, 255), width=2)
    
    # Dragon eyes (googly for humor)
    draw.ellipse([(dragon_x-15, dragon_y-10), (dragon_x-5, dragon_y)], fill=white)
    draw.ellipse([(dragon_x+5, dragon_y-10), (dragon_x+15, dragon_y)], fill=white)
    draw.ellipse([(dragon_x-12, dragon_y-7), (dragon_x-8, dragon_y-3)], fill=(0, 0, 0))
    draw.ellipse([(dragon_x+8, dragon_y-7), (dragon_x+12, dragon_y-3)], fill=(0, 0, 0))
    
    # Dragon smile
    draw.arc([(dragon_x-15, dragon_y), (dragon_x+15, dragon_y+20)], 
             start=0, end=180, fill=(*gold, 255), width=3)
    
    # Tiny graduation cap on dragon
    cap_points = [
        (dragon_x-20, dragon_y-25),
        (dragon_x+20, dragon_y-25),
        (dragon_x+25, dragon_y-30),
        (dragon_x-25, dragon_y-30)
    ]
    draw.polygon(cap_points, fill=(0, 0, 0))
    
    # Binary code decoration (for AI theme)
    binary = "01001000 01101001"  # "Hi" in binary
    draw.text((85, 20), binary, fill=(*gold, 150), font=subtitle_font)
    
    # Main text
    draw.text((85, 45), "AI University", fill=white, font=title_font)
    
    # Subtitle with humor
    draw.text((85, 85), "Where Dragons Teach Calculus!", fill=(*gold, 255), font=subtitle_font)
    
    # Add small epsilon symbols as decoration
    epsilon_font = title_font
    draw.text((width-50, 20), "ε", fill=(*gold, 200), font=epsilon_font)
    draw.text((width-80, height-40), "δ", fill=(*gold, 200), font=epsilon_font)
    
    # Add integration symbol
    draw.text((width-40, height//2-10), "∫", fill=(*gold, 200), font=title_font)
    
    # Save the logo
    output_path = "/Users/yahavzamari/viralAi/ai_university_logo.png"
    logo.save(output_path, 'PNG')
    print(f"✅ AI University logo created: {output_path}")
    return output_path

if __name__ == "__main__":
    create_ai_university_logo()