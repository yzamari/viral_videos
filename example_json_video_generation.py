#!/usr/bin/env python3
"""
Example: How to use JSON prompts for actual VEO video generation
This shows how the JSON system would integrate with real video generation
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.veo_json_prompts import VEOJSONPromptConverter
from generators.vertex_ai_veo2_client import VertexAIVeo2Client
from utils.session_context import SessionContext

def generate_video_with_json_prompt():
    """Example of generating a video using JSON-structured prompts"""
    
    # Create JSON prompt with precise control
    json_prompt = {
        "shot": {
            "composition": "Medium tracking shot, 50mm lens, shot on RED V-Raptor 8K",
            "camera_motion": "smooth Steadicam walk-along, slight handheld bounce",
            "frame_rate": "24fps"
        },
        "subject": {
            "description": "A young woman with inky-black bob and red strawberry hairpin",
            "wardrobe": "Crocheted ivory halter, high-waisted denim shorts"
        },
        "scene": {
            "location": "quiet urban street bathed in early morning sunlight",
            "time_of_day": "early morning",
            "environment": "golden sunlight reflecting off puddles"
        },
        "cinematography": {
            "lighting": "natural golden-hour lighting with soft HDR bounce",
            "tone": "playful, stylish, vibrant",
            "notes": "STRICTLY NO on-screen subtitles or text overlays"
        },
        "audio": {
            "voice": {
                "style": "pop-rap delivery in Japanese with flirtatious rhythm"
            },
            "lyrics": "ラーメンはもういらない、キャビアだけでいいの。"
        }
    }
    
    # Convert JSON to VEO prompt
    converter = VEOJSONPromptConverter()
    veo_prompt = converter.convert_json_to_veo_prompt(json_prompt)
    
    print("🎬 JSON Prompt converted to VEO format")
    print(f"📝 Prompt length: {len(veo_prompt)} characters")
    print(f"🎯 Preview: {veo_prompt[:100]}...")
    
    # THIS IS WHERE ACTUAL VIDEO GENERATION WOULD HAPPEN:
    # 
    # session_context = SessionContext("json-demo")
    # veo_client = VertexAIVeo2Client(session_context=session_context)
    # 
    # video_path = await veo_client.generate_video(
    #     prompt=veo_prompt,
    #     duration=8.0,
    #     aspect_ratio="9:16"
    # )
    # 
    # print(f"✅ Video generated: {video_path}")
    
    print("\n💡 To generate actual video:")
    print("1. Uncomment the VEO client code above")
    print("2. Ensure proper authentication is set up")
    print("3. Run this script with VEO API access")
    
    return veo_prompt

if __name__ == "__main__":
    generate_video_with_json_prompt()