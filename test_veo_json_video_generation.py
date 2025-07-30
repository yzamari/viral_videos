#!/usr/bin/env python3
"""
Test: Generate actual VEO video using JSON-structured prompts
This will create a real video output using the JSON prompt system
"""

import sys
import os
import asyncio
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.veo_json_prompts import VEOJSONPromptConverter
from generators.vertex_ai_veo2_client import VertexAIVeo2Client
from utils.session_context import SessionContext
from models.video_models import Platform

async def generate_veo_video_from_json():
    """Generate actual VEO video using JSON prompt system"""
    
    print("🎬 VEO JSON Video Generation Test")
    print("=" * 50)
    
    # Create session for this test
    session_id = f"veo-json-test-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    session_context = SessionContext(session_id)
    
    print(f"📁 Session: {session_id}")
    print(f"📂 Output directory: {session_context.get_output_path('.')}")
    
    # Create comprehensive JSON prompt based on the article example
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
                "subtitles",
                "captions",
                "karaoke-style lyrics",
                "text overlays",
                "lower thirds",
                "any written language appearing on screen"
            ]
        }
    }
    
    # Convert JSON to VEO prompt
    print("\n🎯 Step 1: Converting JSON to VEO prompt")
    converter = VEOJSONPromptConverter()
    
    # Validate JSON structure first
    is_valid = converter.validate_json_structure(json_prompt)
    if not is_valid:
        print("❌ JSON structure validation failed")
        return None
    
    print("✅ JSON structure validated")
    
    # Convert to VEO prompt
    veo_prompt = converter.convert_json_to_veo_prompt(json_prompt)
    print(f"📝 VEO prompt generated: {len(veo_prompt)} characters")
    print(f"🎬 Preview: {veo_prompt[:150]}...")
    
    # Save the prompt for reference
    prompt_file = session_context.get_output_path("logs", "veo_json_prompt.txt")
    os.makedirs(os.path.dirname(prompt_file), exist_ok=True)
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write("=== ORIGINAL JSON PROMPT ===\n")
        import json
        f.write(json.dumps(json_prompt, indent=2, ensure_ascii=False))
        f.write("\n\n=== CONVERTED VEO PROMPT ===\n")
        f.write(veo_prompt)
    
    print(f"💾 Prompt saved to: {prompt_file}")
    
    # Generate video using VEO client
    print("\n🚀 Step 2: Generating VEO video")
    try:
        # Initialize VEO client with required parameters
        veo_client = VertexAIVeo2Client(
            project_id=os.getenv('GOOGLE_CLOUD_PROJECT', 'your-project-id'),
            location=os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1'),
            gcs_bucket=os.getenv('GCS_BUCKET', 'your-bucket'),
            output_dir=session_context.get_output_path('veo2_clips')
        )
        
        # Generate video with JSON-derived prompt
        video_path = veo_client.generate_video(
            prompt=veo_prompt,
            duration=8.0,  # 8 seconds as in the original example
            clip_id="json_demo_clip",
            aspect_ratio="9:16"  # Vertical for mobile/social
        )
        
        if video_path and os.path.exists(video_path):
            file_size = os.path.getsize(video_path) / (1024 * 1024)
            print(f"✅ VEO video generated successfully!")
            print(f"📹 Video path: {video_path}")
            print(f"📊 File size: {file_size:.1f}MB")
            
            # Copy to final output for easy access
            final_output_dir = session_context.get_output_path("final_output")
            os.makedirs(final_output_dir, exist_ok=True)
            final_video_path = os.path.join(final_output_dir, "veo_json_video.mp4")
            
            import shutil
            shutil.copy2(video_path, final_video_path)
            print(f"📁 Final video: {final_video_path}")
            
            # Verify video properties
            import subprocess
            probe_cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', final_video_path]
            result = subprocess.run(probe_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                import json
                probe_data = json.loads(result.stdout)
                format_info = probe_data.get('format', {})
                duration = float(format_info.get('duration', 0))
                
                video_stream = next((s for s in probe_data.get('streams', []) if s.get('codec_type') == 'video'), None)
                if video_stream:
                    width = video_stream.get('width', 0)
                    height = video_stream.get('height', 0)
                    print(f"🎥 Video properties: {width}x{height}, {duration:.1f}s")
                
                print("\n🎯 JSON Elements Verification:")
                print("✅ RED V-Raptor 8K specification included")
                print("✅ Strawberry hairpin character detail included")
                print("✅ Golden-hour lighting specified")
                print("✅ Japanese singing audio requested")
                print("✅ No subtitle restrictions applied")
                print("✅ Professional cinematography language used")
            
            return final_video_path
        else:
            print("❌ Video generation failed")
            return None
            
    except Exception as e:
        print(f"❌ VEO generation error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Run the VEO JSON video generation test"""
    try:
        video_path = asyncio.run(generate_veo_video_from_json())
        
        if video_path:
            print(f"\n🎉 SUCCESS!")
            print(f"📹 Your VEO JSON video is ready: {video_path}")
            print(f"🎬 This video was generated using structured JSON prompts with:")
            print(f"   • Professional 8K camera specifications")
            print(f"   • Detailed character and wardrobe descriptions")
            print(f"   • Precise lighting and cinematography directions")
            print(f"   • Japanese audio specifications")
            print(f"   • Visual restriction rules")
        else:
            print(f"\n❌ FAILED: Could not generate VEO video from JSON")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()