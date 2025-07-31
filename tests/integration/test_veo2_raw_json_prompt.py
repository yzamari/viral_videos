#!/usr/bin/env python3
"""
Test: Send raw JSON directly to VEO2 API as prompt
This tests if VEO2 can interpret JSON structure natively without conversion
"""

import sys
import os
import json
import asyncio
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from generators.vertex_ai_veo2_client import VertexAIVeo2Client
from utils.session_context import SessionContext

async def test_veo2_raw_json_prompt():
    """Test VEO2 with raw JSON prompt (no conversion to string)"""
    
    print("🎬 VEO2 Raw JSON Prompt Test")
    print("=" * 50)
    print("Testing if VEO2 can interpret JSON structure natively")
    
    # Create session for this test
    session_id = f"veo2-raw-json-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    session_context = SessionContext(session_id)
    
    print(f"📁 Session: {session_id}")
    
    # Your exact JSON prompt
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
    
    print(f"🎯 Step 1: JSON Prompt Structure")
    print(f"📋 JSON sections: {list(json_prompt.keys())}")
    print(f"📝 JSON size: {len(json.dumps(json_prompt))} characters")
    
    # Save the JSON for reference
    json_file = session_context.get_output_path("logs", "raw_json_prompt.json")
    os.makedirs(os.path.dirname(json_file), exist_ok=True)
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_prompt, f, indent=2, ensure_ascii=False)
    
    print(f"💾 JSON saved to: {json_file}")
    
    # Test 1: Send JSON as string (JSON.stringify equivalent)
    print(f"\n🚀 Step 2: Test 1 - JSON as String")
    try:
        veo_client = VertexAIVeo2Client(
            project_id=os.getenv('GOOGLE_CLOUD_PROJECT', 'viral-ai-project'),
            location=os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1'),
            gcs_bucket=os.getenv('GCS_BUCKET', 'viral-ai-bucket'),
            output_dir=session_context.get_output_path('veo2_clips')
        )
        
        # Convert JSON to string (like JSON.stringify)
        json_string = json.dumps(json_prompt, ensure_ascii=False)
        
        print(f"📝 Sending JSON as string prompt to VEO2...")
        print(f"🎬 Preview: {json_string[:100]}...")
        
        video_path_1 = veo_client.generate_video(
            prompt=json_string,
            duration=8.0,
            clip_id="json_string_test",
            aspect_ratio="9:16"
        )
        
        if video_path_1 and os.path.exists(video_path_1):
            file_size = os.path.getsize(video_path_1) / (1024 * 1024)
            print(f"✅ Test 1 SUCCESS: JSON string accepted by VEO2")
            print(f"📹 Video: {video_path_1}")
            print(f"📊 Size: {file_size:.1f}MB")
            
            # Move to final output
            final_path_1 = session_context.get_output_path("final_output", "veo2_json_string.mp4")
            os.makedirs(os.path.dirname(final_path_1), exist_ok=True)
            import shutil
            shutil.copy2(video_path_1, final_path_1)
            print(f"📁 Final: {final_path_1}")
        else:
            print(f"❌ Test 1 FAILED: JSON string rejected by VEO2")
            
    except Exception as e:
        print(f"❌ Test 1 ERROR: {e}")
    
    # Test 2: Send formatted JSON (pretty printed)
    print(f"\n🚀 Step 3: Test 2 - Formatted JSON")
    try:
        # Convert JSON to formatted string (like JSON.stringify with indent)
        formatted_json = json.dumps(json_prompt, indent=2, ensure_ascii=False)
        
        print(f"📝 Sending formatted JSON to VEO2...")
        print(f"🎬 Preview: {formatted_json[:100]}...")
        
        video_path_2 = veo_client.generate_video(
            prompt=formatted_json,
            duration=8.0,
            clip_id="json_formatted_test",
            aspect_ratio="9:16"
        )
        
        if video_path_2 and os.path.exists(video_path_2):
            file_size = os.path.getsize(video_path_2) / (1024 * 1024)
            print(f"✅ Test 2 SUCCESS: Formatted JSON accepted by VEO2")
            print(f"📹 Video: {video_path_2}")
            print(f"📊 Size: {file_size:.1f}MB")
            
            # Move to final output
            final_path_2 = session_context.get_output_path("final_output", "veo2_json_formatted.mp4")
            os.makedirs(os.path.dirname(final_path_2), exist_ok=True)
            import shutil
            shutil.copy2(video_path_2, final_path_2)
            print(f"📁 Final: {final_path_2}")
        else:
            print(f"❌ Test 2 FAILED: Formatted JSON rejected by VEO2")
            
    except Exception as e:
        print(f"❌ Test 2 ERROR: {e}")
    
    # Test 3: Send JSON with explicit instruction
    print(f"\n🚀 Step 4: Test 3 - JSON with Instructions")
    try:
        # Add instruction for VEO to interpret JSON
        json_with_instruction = f"Please interpret the following JSON structure as video generation parameters:\n\n{json.dumps(json_prompt, indent=2, ensure_ascii=False)}"
        
        print(f"📝 Sending instructed JSON to VEO2...")
        print(f"🎬 Preview: {json_with_instruction[:100]}...")
        
        video_path_3 = veo_client.generate_video(
            prompt=json_with_instruction,
            duration=8.0,
            clip_id="json_instructed_test",
            aspect_ratio="9:16"
        )
        
        if video_path_3 and os.path.exists(video_path_3):
            file_size = os.path.getsize(video_path_3) / (1024 * 1024)
            print(f"✅ Test 3 SUCCESS: Instructed JSON accepted by VEO2")
            print(f"📹 Video: {video_path_3}")
            print(f"📊 Size: {file_size:.1f}MB")
            
            # Move to final output
            final_path_3 = session_context.get_output_path("final_output", "veo2_json_instructed.mp4")
            os.makedirs(os.path.dirname(final_path_3), exist_ok=True)
            import shutil
            shutil.copy2(video_path_3, final_path_3)
            print(f"📁 Final: {final_path_3}")
        else:
            print(f"❌ Test 3 FAILED: Instructed JSON rejected by VEO2")
            
    except Exception as e:
        print(f"❌ Test 3 ERROR: {e}")
    
    print(f"\n" + "=" * 60)
    print(f"🎯 VEO2 Raw JSON Test Summary")
    print(f"=" * 60)
    print(f"📁 Session outputs: {session_context.get_output_path('final_output')}")
    print(f"🎬 Test Results:")
    print(f"   1. JSON String: {'✅' if 'video_path_1' in locals() and video_path_1 else '❌'}")
    print(f"   2. Formatted JSON: {'✅' if 'video_path_2' in locals() and video_path_2 else '❌'}")
    print(f"   3. Instructed JSON: {'✅' if 'video_path_3' in locals() and video_path_3 else '❌'}")
    
    print(f"\n💡 Key Findings:")
    print(f"📝 JSON structure contains {len(json_prompt)} major sections")
    print(f"🎨 Detailed cinematography: RED V-Raptor 8K, 50mm lens, Steadicam")
    print(f"👤 Character details: Young woman with strawberry hairpin")
    print(f"🌅 Scene: Early morning urban street with golden light")
    print(f"🎵 Audio: Japanese lyrics with specific vocal style")
    print(f"🚫 Restrictions: No text overlays or subtitles")
    
    return session_context.get_output_path('final_output')

def main():
    """Run the VEO2 raw JSON test"""
    try:
        output_dir = asyncio.run(test_veo2_raw_json_prompt())
        print(f"\n🎉 Test completed! Check outputs in: {output_dir}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()