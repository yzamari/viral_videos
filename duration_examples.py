#!/usr/bin/env python3
"""
Duration Examples - Shows different ways to control clip durations
"""

from src.news_aggregator.duration_manager import DurationManager
import json


def show_duration_examples():
    """Demonstrate all duration control methods"""
    
    print("""
🕐 NEWS AGGREGATOR DURATION CONTROL
===================================

The system offers several ways to control how long each clip appears:
""")
    
    # Initialize duration manager
    dm = DurationManager()
    
    # Example content
    content_examples = [
        {
            'title': 'Quick Update',
            'type': 'image',
            'description': ''
        },
        {
            'title': 'Breaking: Major earthquake hits California, thousands evacuated',
            'description': 'A 7.2 magnitude earthquake has struck Southern California, causing widespread damage and forcing thousands to evacuate. Emergency services are responding.',
            'type': 'image',
            'category': 'breaking_news'
        },
        {
            'title': 'Lakers 110 - Celtics 95',
            'type': 'image',
            'category': 'sports'
        },
        {
            'title': 'Stock Market Report',
            'description': 'Dow Jones: +2.5% ($35,241), S&P 500: +1.8% ($4,523), NASDAQ: +3.1% ($14,239)',
            'type': 'image',
            'category': 'finance'
        },
        {
            'title': 'Weather Forecast',
            'description': 'Today: Sunny 75°F, Tomorrow: Cloudy 68°F, Weekend: Rain expected',
            'type': 'image',
            'category': 'weather'
        },
        {
            'title': 'Video Report from Scene',
            'type': 'video',
            'duration': 15  # Original video is 15 seconds
        }
    ]
    
    print("\n1️⃣ AUTOMATIC DURATION CALCULATION")
    print("=" * 50)
    print("The system automatically calculates duration based on:")
    print("  • Content type (breaking news, sports, finance, etc.)")
    print("  • Text length and reading speed")
    print("  • Media type (image vs video)")
    print("  • Language (Hebrew is slightly slower than English)")
    
    print("\n📊 Examples:")
    for content in content_examples:
        duration = dm.get_duration(content)
        content_type = dm.analyze_content_complexity(content)
        print(f"\n  • {content['title'][:50]}...")
        print(f"    Type: {content_type}")
        print(f"    Auto Duration: {duration} seconds")
    
    print("\n\n2️⃣ MANUAL DURATION CONTROL")
    print("=" * 50)
    print("You can manually set durations in several ways:")
    
    print("\n  A) Force specific duration:")
    print("     duration = dm.get_duration(content, force_duration=7)")
    forced = dm.get_duration(content_examples[0], force_duration=7)
    print(f"     Result: {forced} seconds (forced)")
    
    print("\n  B) Set min/max constraints:")
    print("     duration = dm.get_duration(content, min_duration=5, max_duration=10)")
    constrained = dm.get_duration(content_examples[0], min_duration=5, max_duration=10)
    print(f"     Result: {constrained} seconds (constrained to 5-10)")
    
    print("\n  C) In your CSV file:")
    print("     title,source,media_url,duration")
    print("     'Breaking News','CNN','http://...jpg',8")
    print("     'Sports Update','ESPN','http://...mp4',5")
    
    print("\n\n3️⃣ DURATION DISTRIBUTION")
    print("=" * 50)
    print("When creating a compilation, durations are distributed intelligently:")
    
    # Show distribution example
    total_duration = 60
    items = content_examples[:5]  # Take first 5 items
    
    distributed = dm.distribute_durations(items.copy(), total_duration=total_duration)
    
    print(f"\nDistributing {total_duration} seconds across {len(items)} clips:")
    total = 0
    for i, item in enumerate(distributed):
        print(f"  Clip {i+1}: {item['duration']}s - {item['title'][:40]}...")
        total += item['duration']
    print(f"  Total: {total} seconds")
    
    print("\n\n4️⃣ DURATION PRESETS")
    print("=" * 50)
    print("Use presets for different pacing styles:")
    
    presets = {
        'fast': 'Quick social media style (2-5 seconds per clip)',
        'default': 'Standard news pacing (3-8 seconds per clip)',
        'slow': 'Documentary style (5-12 seconds per clip)',
        'breaking_news': 'Extended for important news (5-15 seconds)',
        'social_media': 'TikTok/Instagram style (2-4 seconds)'
    }
    
    for preset, description in presets.items():
        print(f"\n  • {preset}: {description}")
    
    print("\n\n5️⃣ VIDEO HANDLING")
    print("=" * 50)
    print("For video clips, the system can:")
    print("  • Use original video duration (if shorter than calculated)")
    print("  • Trim longer videos to fit optimal duration")
    print("  • Speed up/slow down playback (optional)")
    
    video_example = {
        'title': 'News Report',
        'type': 'video',
        'duration': 25  # 25-second video
    }
    
    print(f"\n  Example: 25-second video")
    print(f"  • Default max duration: 10 seconds")
    print(f"  • Result: Video trimmed to 10 seconds")
    print(f"  • To use full video: set max_duration=30")
    
    print("\n\n6️⃣ PRACTICAL EXAMPLES")
    print("=" * 50)
    
    print("\n📺 Example 1: 60-second news compilation")
    print("python main.py news aggregate --duration 60")
    
    print("\n⚽ Example 2: 30-second sports highlights (fast pace)")
    print("python main.py news sports --duration 30 --pace fast")
    
    print("\n📰 Example 3: Custom durations from CSV")
    print("Create a CSV file with duration column:")
    print("title,source,media_url,duration,category")
    print("'Big Goal!','ESPN','video1.mp4',5,sports")
    print("'Market Update','Bloomberg','chart.jpg',7,finance")
    print("'Weather Alert','Weather.com','map.jpg',4,weather")
    
    print("\n\n💡 TIPS")
    print("=" * 50)
    print("• Let automatic calculation handle most cases")
    print("• Override only when needed (important news, specific pacing)")
    print("• Test different presets to find your style")
    print("• Consider your audience (social media = faster, TV = slower)")
    print("• Mix short and long clips for variety")
    
    # Save example configuration
    config_example = {
        "duration_settings": {
            "total_duration": 60,
            "min_clip_duration": 3,
            "max_clip_duration": 10,
            "preset": "default"
        },
        "content_items": [
            {
                "title": "Breaking News Story",
                "duration": "auto",
                "category": "breaking_news"
            },
            {
                "title": "Sports Highlight",
                "duration": 5,
                "category": "sports"
            },
            {
                "title": "Weather Update",
                "duration": "auto",
                "category": "weather"
            }
        ]
    }
    
    with open("duration_config_example.json", "w") as f:
        json.dump(config_example, f, indent=2)
    
    print("\n\n📄 Created: duration_config_example.json")
    print("Use this as a template for your duration configurations!")


if __name__ == "__main__":
    show_duration_examples()