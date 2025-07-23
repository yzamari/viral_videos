#!/usr/bin/env python3
"""Create custom weather graphics for Iranian comedy series."""

from weather_graphics_generator import WeatherGraphicsGenerator
import os

def create_iranian_comedy_weather_graphics():
    """Create all weather graphics for the Iranian comedy series."""
    
    print("🎨 Creating custom weather graphics for Iranian comedy series...")
    
    # Create generator
    generator = WeatherGraphicsGenerator(output_dir="assets/iran_comedy_graphics/weather")
    
    # 1. Nuclear heat map
    print("☢️  Creating nuclear heat map...")
    nuclear_temps = {
        "Tehran": 55,  # "Radioactive" hot
        "Isfahan": 52,
        "Shiraz": 50,
        "Tabriz": 48,
        "Mashhad": 51,
        "Ahvaz": 58,  # Hottest!
        "Kerman": 53
    }
    nuclear_map = generator.create_heat_map(
        nuclear_temps,
        title="پیش‌بینی هوا: داغ و هسته‌ای | Weather: Hot & Nuclear",
        output_name="nuclear_heat_map.png",
        style="nuclear"
    )
    print(f"   ✅ Created: {nuclear_map}")
    
    # 2. Water crisis map
    print("💧 Creating water crisis map...")
    water_status = {
        "Tehran": "critical",
        "Isfahan": "dry",
        "Shiraz": "critical",
        "Tabriz": "low",
        "Mashhad": "dry",
        "Ahvaz": "dry",
        "Kerman": "critical"
    }
    water_map = generator.create_water_crisis_map(
        water_status,
        output_name="water_crisis_status.png"
    )
    print(f"   ✅ Created: {water_map}")
    
    # 3. Comedy weather overlay
    print("😂 Creating comedy weather overlay...")
    comedy_jokes = {
        "Tehran": "گرما اونقدر زیاده که یخچال‌ها دارن عرق می‌کنن!",
        "Isfahan": "زاینده‌رود: من رفتم، خداحافظ!",
        "Shiraz": "حافظ: 'ساقی آب کو؟' ساقی: 'آب نداریم!'",
        "Ahvaz": "دمای هوا: غیرقابل اندازه‌گیری!"
    }
    comedy_overlay = generator.create_comedy_weather_overlay(
        comedy_jokes,
        output_name="comedy_weather_bubbles.png"
    )
    print(f"   ✅ Created: {comedy_overlay}")
    
    # 4. Animated nuclear warning
    print("⚠️  Creating nuclear warning animation frames...")
    frames = generator.create_nuclear_weather_animation_frames(
        num_frames=30,
        output_prefix="nuclear_pulse"
    )
    print(f"   ✅ Created {len(frames)} animation frames")
    
    print("\n✨ All weather graphics created successfully!")
    print(f"📁 Graphics saved to: assets/iran_comedy_graphics/weather/")
    print("\n🎬 To use in your video generation:")
    print("   Add to your --mission prompt:")
    print("   'Use custom weather graphics from assets/iran_comedy_graphics/weather/nuclear_heat_map.png'")
    
    return {
        "nuclear_map": nuclear_map,
        "water_map": water_map,
        "comedy_overlay": comedy_overlay,
        "animation_frames": frames
    }

if __name__ == "__main__":
    # Check if matplotlib and PIL are installed
    try:
        import matplotlib
        import PIL
    except ImportError:
        print("❌ Please install required packages:")
        print("   pip install matplotlib pillow")
        exit(1)
    
    # Create graphics
    graphics = create_iranian_comedy_weather_graphics()
    
    print("\n📋 Generated graphics:")
    for name, path in graphics.items():
        if isinstance(path, list):
            print(f"   {name}: {len(path)} files")
        else:
            print(f"   {name}: {path}")