#!/usr/bin/env python3
"""
Create Iran Thirstional News Overlay PNG
A parody of Iran International with water/thirst theme
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_iran_thirstional_overlay():
    """Create Iran Thirstional news logo overlay"""
    
    # Create directories
    os.makedirs("assets/overlays/iran_thirstional", exist_ok=True)
    
    # Main logo dimensions
    width, height = 600, 180
    logo = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(logo)
    
    # Background shape (dark blue with transparency)
    draw.rounded_rectangle(
        [(10, 10), (width-10, height-10)],
        radius=20,
        fill=(0, 33, 66, 230)  # Dark blue with transparency
    )
    
    # Try to use a good font
    try:
        title_font = ImageFont.truetype("Arial-Bold.ttf", 48)
        subtitle_font = ImageFont.truetype("Arial.ttf", 24)
    except:
        # Fallback to default
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Main text "IRAN THIRSTIONAL"
    main_text = "IRAN THIRSTIONAL"
    text_bbox = draw.textbbox((0, 0), main_text, font=title_font)
    text_width = text_bbox[2] - text_bbox[0]
    x = (width - text_width) // 2
    
    # Draw main text with dripping effect
    draw.text((x, 35), main_text, fill=(255, 255, 255), font=title_font)
    
    # Add water drops coming from letters
    drop_positions = [(x + 80, 85), (x + 200, 85), (x + 350, 85), (x + 480, 85)]
    for drop_x, drop_y in drop_positions:
        # Draw water drop shape
        draw.ellipse([drop_x-5, drop_y, drop_x+5, drop_y+15], fill=(135, 206, 235))
        draw.polygon([(drop_x, drop_y-5), (drop_x-5, drop_y+5), (drop_x+5, drop_y+5)], 
                    fill=(135, 206, 235))
    
    # Subtitle
    subtitle = "YOUR THIRST FOR NEWS"
    sub_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    sub_width = sub_bbox[2] - sub_bbox[0]
    sub_x = (width - sub_width) // 2
    draw.text((sub_x, 110), subtitle, fill=(135, 206, 235), font=subtitle_font)
    
    # Add thirsty emoji symbols
    draw.text((50, 70), "💧", font=subtitle_font)
    draw.text((width-80, 70), "🏜️", font=subtitle_font)
    
    # Save main logo
    logo.save("assets/overlays/iran_thirstional/logo_main.png")
    print("✅ Created main logo: assets/overlays/iran_thirstional/logo_main.png")
    
    # Create corner version (smaller)
    corner_logo = logo.resize((300, 90), Image.Resampling.LANCZOS)
    corner_logo.save("assets/overlays/iran_thirstional/logo_corner.png")
    print("✅ Created corner logo: assets/overlays/iran_thirstional/logo_corner.png")
    
    # Create breaking news banner
    breaking_width, breaking_height = 1920, 150
    breaking = Image.new('RGBA', (breaking_width, breaking_height), (0, 0, 0, 0))
    draw_breaking = ImageDraw.Draw(breaking)
    
    # Red background
    draw_breaking.rectangle([(0, 0), (breaking_width, breaking_height)], 
                           fill=(204, 0, 0, 240))
    
    # White text
    try:
        breaking_font = ImageFont.truetype("Arial-Bold.ttf", 72)
    except:
        breaking_font = ImageFont.load_default()
    
    draw_breaking.text((50, 35), "BREAKING THIRST", fill=(255, 255, 255), font=breaking_font)
    draw_breaking.text((700, 35), "💧", font=breaking_font)
    draw_breaking.text((1200, 35), "WATER CRISIS UPDATE", fill=(255, 255, 255), font=breaking_font)
    
    breaking.save("assets/overlays/iran_thirstional/breaking_news.png")
    print("✅ Created breaking news banner: assets/overlays/iran_thirstional/breaking_news.png")
    
    # Create lower third background
    lower_width, lower_height = 1200, 180
    lower_third = Image.new('RGBA', (lower_width, lower_height), (0, 0, 0, 0))
    draw_lower = ImageDraw.Draw(lower_third)
    
    # Two-tone design
    draw_lower.polygon([(0, 40), (lower_width, 40), (lower_width, lower_height), (0, lower_height)], 
                      fill=(0, 33, 66, 230))
    draw_lower.rectangle([(0, 0), (lower_width, 40)], fill=(204, 0, 0, 240))
    
    # Add text placeholders
    try:
        lower_font = ImageFont.truetype("Arial.ttf", 20)
    except:
        lower_font = ImageFont.load_default()
    
    draw_lower.text((30, 8), "IRAN THIRSTIONAL NEWS", fill=(255, 255, 255), font=lower_font)
    
    lower_third.save("assets/overlays/iran_thirstional/lower_third.png")
    print("✅ Created lower third: assets/overlays/iran_thirstional/lower_third.png")
    
    # Create news ticker
    ticker_width, ticker_height = 1920, 80
    ticker = Image.new('RGBA', (ticker_width, ticker_height), (0, 0, 0, 0))
    draw_ticker = ImageDraw.Draw(ticker)
    
    # Dark blue background
    draw_ticker.rectangle([(0, 0), (ticker_width, ticker_height)], 
                         fill=(0, 33, 66, 230))
    
    # Red accent box
    draw_ticker.rectangle([(0, 0), (300, ticker_height)], fill=(204, 0, 0, 240))
    
    try:
        ticker_font = ImageFont.truetype("Arial-Bold.ttf", 36)
    except:
        ticker_font = ImageFont.load_default()
    
    draw_ticker.text((20, 20), "THIRST NEWS", fill=(255, 255, 255), font=ticker_font)
    draw_ticker.text((350, 20), "💧 WATER UPDATE: Still missing | 🏜️ DROUGHT LEVEL: YES | 💧", 
                    fill=(255, 255, 255), font=ticker_font)
    
    ticker.save("assets/overlays/iran_thirstional/news_ticker.png")
    print("✅ Created news ticker: assets/overlays/iran_thirstional/news_ticker.png")
    
    # Create studio watermark
    watermark = Image.new('RGBA', (200, 60), (0, 0, 0, 0))
    draw_watermark = ImageDraw.Draw(watermark)
    
    # Semi-transparent background
    draw_watermark.rounded_rectangle(
        [(5, 5), (195, 55)],
        radius=10,
        fill=(0, 33, 66, 180)
    )
    
    try:
        watermark_font = ImageFont.truetype("Arial.ttf", 18)
    except:
        watermark_font = ImageFont.load_default()
    
    draw_watermark.text((15, 20), "IRAN THIRSTIONAL", fill=(255, 255, 255, 200), font=watermark_font)
    
    watermark.save("assets/overlays/iran_thirstional/watermark.png")
    print("✅ Created watermark: assets/overlays/iran_thirstional/watermark.png")
    
    print("\n🎉 All Iran Thirstional overlays created successfully!")
    print("📁 Files saved in: assets/overlays/iran_thirstional/")
    print("\nAvailable overlays:")
    print("  - logo_main.png (600x180) - Main logo with dripping effect")
    print("  - logo_corner.png (300x90) - Corner logo for continuous display")
    print("  - breaking_news.png (1920x150) - Breaking thirst banner")
    print("  - lower_third.png (1200x180) - Lower third template")
    print("  - news_ticker.png (1920x80) - News ticker with thirst updates")
    print("  - watermark.png (200x60) - Small watermark")

if __name__ == "__main__":
    create_iran_thirstional_overlay()