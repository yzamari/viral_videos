#!/usr/bin/env python3
"""
Test: Generate VEO video using JSON prompts through the main video generation system
This uses the existing authentication and infrastructure
"""

import sys
import os
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.veo_json_prompts import VEOJSONPromptConverter

def create_json_mission_and_run():
    """Create a video generation command using JSON-structured prompts"""
    
    print("🎬 VEO JSON Integration with Main System")
    print("=" * 50)
    
    # Create the comprehensive JSON prompt
    json_prompt = {
        "shot": {
            "composition": "Medium tracking shot, 50mm lens, shot on RED V-Raptor 8K with Netflix-approved HDR setup, shallow depth of field",
            "camera_motion": "smooth Steadicam walk-along, slight handheld bounce for naturalistic rhythm",
            "frame_rate": "24fps",
            "film_grain": "clean digital with film-emulated LUT for warmth and vibrancy"
        },
        "subject": {
            "description": "A young woman with a petite frame and soft porcelain complexion. She has oversized, almond-shaped eyes with long lashes, subtle pink-tinted cheeks, and a heart-shaped face. Her inky-black bob is slightly tousled and clipped to one side with a small red strawberry hairpin.",
            "wardrobe": "Crocheted ivory halter with scalloped trim, fitted high-waisted denim shorts, wide tan belt with red enamel star buckle, oversized red gingham blouse slipped off one shoulder"
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
                "subtitles", "captions", "karaoke-style lyrics", 
                "text overlays", "lower thirds", "any written language appearing on screen"
            ]
        }
    }
    
    # Convert JSON to VEO prompt
    print("🎯 Step 1: Converting JSON to VEO prompt")
    converter = VEOJSONPromptConverter()
    
    # Validate JSON structure
    is_valid = converter.validate_json_structure(json_prompt)
    if not is_valid:
        print("❌ JSON structure validation failed")
        return
    
    print("✅ JSON structure validated")
    
    # Convert to VEO prompt
    veo_prompt = converter.convert_json_to_veo_prompt(json_prompt)
    print(f"📝 VEO prompt generated: {len(veo_prompt)} characters")
    print(f"🎬 Preview: {veo_prompt[:150]}...")
    
    # Save JSON and prompt for reference
    session_id = f"json-demo-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Create the command to run the main system
    print(f"\n🚀 Step 2: Command to generate VEO video using main system")
    print("=" * 60)
    
    # Create a mission that incorporates the JSON-derived content
    mission = f"Create a cinematic Japanese street scene video: {veo_prompt[:200]}..."
    
    command = f"""python main.py generate \\
    --mission "{mission}" \\
    --duration 8 \\
    --platform instagram \\
    --session-id {session_id} \\
    --no-cheap \\
    --visual-style "cinematic professional RED camera 8K"
"""
    
    print("📋 Command to run:")
    print(command)
    
    print(f"\n💡 This command will:")
    print(f"✅ Use the JSON-derived prompt content in the mission")
    print(f"✅ Generate an 8-second Instagram video")
    print(f"✅ Use VEO (not cheap mode) for high quality")
    print(f"✅ Apply cinematic visual style")
    print(f"✅ Save output to session: {session_id}")
    
    print(f"\n📁 Expected output location:")
    print(f"outputs/{session_id}/final_output/final_video_{session_id}__final.mp4")
    
    # Save the full JSON and prompt for reference
    with open(f"json_prompt_reference_{session_id}.json", 'w', encoding='utf-8') as f:
        json.dump({
            "original_json": json_prompt,
            "converted_veo_prompt": veo_prompt,
            "session_id": session_id,
            "command": command.strip()
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 JSON reference saved to: json_prompt_reference_{session_id}.json")
    
    print(f"\n🎬 Key JSON Elements in this video:")
    print(f"📹 RED V-Raptor 8K camera specification")
    print(f"👤 Detailed character: young woman with strawberry hairpin")
    print(f"🌅 Golden-hour lighting in early morning urban setting")
    print(f"🎵 Japanese lyrics: 'ラーメンはもういらない、キャビアだけでいいの'") 
    print(f"🚫 No subtitles or text overlays restriction")
    print(f"🎨 Professional cinematography with precise color palette")
    
    return command.strip()

if __name__ == "__main__":
    command = create_json_mission_and_run()
    
    print(f"\n" + "=" * 60)
    print(f"🎯 To generate the actual VEO video, run:")
    print(f"💻 {command}")
    print(f"=" * 60)