#!/usr/bin/env python3
"""
Test VEO2 with raw JSON using working authentication from main system
"""

import sys
import os
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def create_veo2_json_test_command():
    """Create command to test VEO2 with JSON using working system"""
    
    print("🎬 VEO2 Raw JSON Test via Main System")
    print("=" * 50)
    
    # Your exact JSON structure
    json_prompt = {
        "shot": {
            "composition": "Medium tracking shot, 50mm lens, shot on RED V-Raptor 8K with Netflix-approved HDR setup, shallow depth of field",
            "camera_motion": "smooth Steadicam walk-along, slight handheld bounce for naturalistic rhythm",
            "frame_rate": "24fps",
            "film_grain": "clean digital with film-emulated LUT for warmth and vibrancy"
        },
        "subject": {
            "description": "A young woman with a petite frame and soft porcelain complexion. She has oversized, almond-shaped eyes with long lashes, subtle pink-tinted cheeks, and a heart-shaped face. Her inky-black bob is slightly tousled and clipped to one side with a small red strawberry hairpin. Her style blends playful retro and modern Tokyo streetwear: she wears a crocheted ivory halter top with scalloped edges, high-waisted denim shorts with a wide brown belt and a red enamel star buckle, and a loose red gingham blouse draped off one shoulder. Her accessories include glossy cherry lip tint, a beaded bracelet stack, and soft shimmer eyeshadow.",
            "wardrobe": "Crocheted ivory halter with scalloped trim, fitted high-waisted denim shorts, wide tan belt with red enamel star buckle, oversized red gingham blouse slipped off one shoulder, strawberry hairpin in side-parted bob, and translucent plastic bead bracelets in pink and cream tones."
        },
        "scene": {
            "location": "a quiet urban street bathed in early morning sunlight",
            "time_of_day": "early morning",
            "environment": "empty sidewalks, golden sunlight reflecting off puddles and windows, occasional birds fluttering by, street slightly wet from overnight rain"
        },
        "visual_details": {
            "action": "she walks rhythmically down the sidewalk, swinging her hips slightly with the beat, one hand gesturing playfully, the other adjusting her shirt sleeve as she sings",
            "props": "morning mist, traffic light turning green in the distance, reflective puddles, subtle sun flare"
        },
        "cinematography": {
            "lighting": "natural golden-hour lighting with soft HDR bounce, gentle lens flare through morning haze",
            "tone": "playful, stylish, vibrant",
            "notes": "STRICTLY NO on-screen subtitles, lyrics, captions, or text overlays. Final render must be clean visual-only."
        },
        "audio": {
            "ambient": "city birds chirping, distant traffic hum, her boots tapping pavement",
            "voice": {
                "tone": "light, teasing, and melodic",
                "style": "pop-rap delivery in Japanese with flirtatious rhythm, confident breath control, playful pacing and bounce"
            },
            "lyrics": "ラーメンはもういらない、キャビアだけでいいの。 ファイナンスのおかげで、私、星みたいに輝いてる。"
        },
        "color_palette": "sun-warmed pastels with vibrant reds and denim blues, soft contrast with warm film LUT",
        "dialogue": {
            "character": "Woman (singing in Japanese)",
            "line": "ラーメンはもういらない、キャビアだけでいいの。 ファイナンスのおかげで、私、星みたいに輝いてる。",
            "subtitles": False
        },
        "visual_rules": {
            "prohibited_elements": [
                "subtitles",
                "captions",
                "karaoke-style lyrics",
                "text overlays",
                "lower thirds",
                "any written language appearing on screen"
            ]
        }
    }
    
    session_id = f"veo2-json-raw-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"🎯 Testing 3 JSON formats with VEO2:")
    print(f"1. JSON as string (compact)")
    print(f"2. JSON as formatted string (pretty)")
    print(f"3. JSON with interpretation instruction")
    
    # Test 1: JSON as compact string
    json_string = json.dumps(json_prompt, ensure_ascii=False, separators=(',', ':'))
    command1 = f'''python main.py generate \\
    --mission "{json_string}" \\
    --duration 8 \\
    --platform instagram \\
    --session-id {session_id}-compact \\
    --no-cheap \\
    --visual-style "JSON-compact-test"'''
    
    # Test 2: JSON as formatted string (truncated for command line)
    json_formatted = json.dumps(json_prompt, indent=2, ensure_ascii=False)
    # For command line, we'll use a shorter version
    short_json = {
        "shot": json_prompt["shot"],
        "subject": {"description": json_prompt["subject"]["description"][:100] + "..."},
        "scene": json_prompt["scene"],
        "cinematography": json_prompt["cinematography"]
    }
    json_formatted_short = json.dumps(short_json, indent=2, ensure_ascii=False)
    
    command2 = f'''python main.py generate \\
    --mission "{json_formatted_short}" \\
    --duration 8 \\
    --platform instagram \\
    --session-id {session_id}-formatted \\
    --no-cheap \\
    --visual-style "JSON-formatted-test"'''
    
    # Test 3: JSON with instruction
    instruction = f"Interpret this JSON as video parameters: {json_string[:200]}..."
    command3 = f'''python main.py generate \\
    --mission "{instruction}" \\
    --duration 8 \\
    --platform instagram \\
    --session-id {session_id}-instructed \\
    --no-cheap \\
    --visual-style "JSON-instructed-test"'''
    
    # Save all formats for reference
    with open(f"veo2_json_test_formats_{session_id}.json", 'w', encoding='utf-8') as f:
        json.dump({
            "original_json": json_prompt,
            "compact_string": json_string,
            "formatted_string": json_formatted,
            "instruction_prompt": instruction,
            "commands": {
                "compact": command1,
                "formatted": command2,
                "instructed": command3
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📝 JSON formats saved to: veo2_json_test_formats_{session_id}.json")
    
    print(f"\n🚀 Commands to test VEO2 with different JSON formats:")
    print(f"\n1️⃣  JSON COMPACT STRING:")
    print(f"📋 Length: {len(json_string)} characters")
    print(f"💻 {command1}")
    
    print(f"\n2️⃣  JSON FORMATTED STRING:")
    print(f"📋 Length: {len(json_formatted_short)} characters")  
    print(f"💻 {command2}")
    
    print(f"\n3️⃣  JSON WITH INSTRUCTION:")
    print(f"📋 Length: {len(instruction)} characters")
    print(f"💻 {command3}")
    
    print(f"\n🎬 Expected outputs:")
    print(f"📁 outputs/{session_id}-compact/final_output/")
    print(f"📁 outputs/{session_id}-formatted/final_output/")
    print(f"📁 outputs/{session_id}-instructed/final_output/")
    
    print(f"\n🔍 What we're testing:")
    print(f"✅ Can VEO2 interpret raw JSON structure?")
    print(f"✅ Does formatting (pretty print) help VEO2?")
    print(f"✅ Do explicit instructions improve JSON parsing?")
    print(f"✅ Which format produces the most accurate video?")
    
    return [command1, command2, command3]

if __name__ == "__main__":
    commands = create_veo2_json_test_command()
    
    print(f"\n" + "=" * 60)
    print(f"🎯 To test VEO2 with raw JSON, run each command above")
    print(f"💡 Compare the outputs to see which JSON format works best")
    print(f"=" * 60)