#!/usr/bin/env python3
"""
Demo script showcasing all features of the Viral Video Generator
"""

import os
import sys

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"🎬 {title}")
    print("=" * 60)

def demo_features():
    """Demonstrate all features of the system"""
    
    print_header("VIRAL VIDEO GENERATOR - FEATURE DEMO")
    
    print("\n📋 Available Features:")
    print("1. Fallback-Only Mode (no VEO quota usage)")
    print("2. Image-Only Mode (AI-generated images)")
    print("3. Frame Continuity Mode (seamless videos)")
    print("4. Real Google Quota Checking")
    print("5. Enhanced Script Generation")
    
    # Check if API key is set
    if not os.getenv("GEMINI_API_KEY"):
        print("\n❌ Please set GEMINI_API_KEY environment variable")
        print("   export GEMINI_API_KEY='your-api-key'")
        return
    
    print("\n✅ API Key detected")
    
    # Demo commands
    demos = [
        {
            "title": "Check VEO Quota",
            "command": "python3 main.py veo-quota",
            "description": "Check your current VEO generation quota"
        },
        {
            "title": "Fallback-Only Video",
            "command": "python3 main.py generate --topic 'How AI is changing education' --platform youtube --category education --fallback-only",
            "description": "Generate video without using VEO quota"
        },
        {
            "title": "Image-Based Video",
            "command": "python3 main.py generate --topic 'The future of space travel' --platform youtube --category technology --image-only",
            "description": "Generate video using AI images (2-3 per second)"
        },
        {
            "title": "Frame Continuity Video",
            "command": "python3 main.py generate --topic 'A journey through Tokyo' --platform youtube --category lifestyle --frame-continuity",
            "description": "Generate seamless video with continuous flow"
        },
        {
            "title": "AI Auto-Decision",
            "command": "python3 main.py generate --topic 'Top 10 tech gadgets of 2024' --platform tiktok --category technology",
            "description": "Let AI decide all parameters (continuity, style, etc.)"
        },
        {
            "title": "News-Based Video",
            "command": "python3 main.py news 'artificial intelligence' --platform youtube --angle pro_technology --duration 60",
            "description": "Generate video based on current news"
        },
        {
            "title": "Combined Features",
            "command": "python3 main.py generate --topic 'Building a startup' --platform youtube --category education --fallback-only --frame-continuity",
            "description": "Use multiple features together"
        }
    ]
    
    print_header("DEMO COMMANDS")
    
    for i, demo in enumerate(demos, 1):
        print(f"\n{i}. {demo['title']}")
        print(f"   📝 {demo['description']}")
        print(f"   💻 Command:")
        print(f"      {demo['command']}")
    
    print_header("FRAME CONTINUITY EXAMPLES")
    
    print("\n✅ Videos that WILL use continuity:")
    continuity_examples = [
        "- Documentary: 'A day in the life of a CEO'",
        "- Tutorial: 'How to build a mobile app'",
        "- Journey: 'Exploring the Amazon rainforest'",
        "- Process: 'From seed to harvest: organic farming'"
    ]
    for example in continuity_examples:
        print(example)
    
    print("\n❌ Videos that WON'T use continuity:")
    no_continuity_examples = [
        "- Compilation: 'Funniest fails of 2024'",
        "- List: 'Top 10 viral moments'",
        "- Memes: 'Best TikTok trends'",
        "- Highlights: 'Sports moments that shocked the world'"
    ]
    for example in no_continuity_examples:
        print(example)
    
    print_header("QUICK START")
    
    print("\n1. Set your API key:")
    print("   export GEMINI_API_KEY='your-api-key'")
    
    print("\n2. Check your quota:")
    print("   python3 main.py veo-quota")
    
    print("\n3. Generate a video (AI decides everything):")
    print("   python3 main.py generate --topic 'Your amazing topic'")
    
    print("\n4. Use fallback mode if quota is low:")
    print("   python3 main.py generate --topic 'Your topic' --fallback-only")
    
    print_header("OUTPUT LOCATION")
    
    print("\nAll videos are saved to: outputs/session_[timestamp]_[id]/")
    print("- viral_video_[id].mp4 - Final video")
    print("- script_[id].txt - Full script")
    print("- veo2_prompts_[id].txt - Scene prompts")
    print("- clips/ - Individual video clips")
    print("- scene_images/ - AI-generated images (if used)")
    
    print("\n🎉 Happy video generating!\n")

if __name__ == "__main__":
    demo_features() 