#!/usr/bin/env python3
"""
Test sending RAW JSON directly to VEO2 without any translation.
"""

import json
import os
import sys
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from generators.veo_client_factory import VeoClientFactory, VeoModel
from utils.session_context import SessionContext
from models.video_models import Platform

class RawVEO2JSONTest:
    """Test VEO2 with raw JSON as prompt"""
    
    def __init__(self):
        self.session_id = "veo2-raw-json-test"
        self.session_context = SessionContext(self.session_id)
        self.veo_factory = VeoClientFactory()
    
    def test_veo2_with_raw_json(self, json_data: Dict[str, Any]) -> str:
        """Test VEO2 with RAW JSON as prompt - no translation"""
        print("🎬 Starting RAW JSON VEO2 Test")
        print(f"📁 Session: {self.session_id}")
        
        try:
            # Convert JSON to string - this is what we'll send directly
            raw_json_prompt = json.dumps(json_data, indent=2)
            
            print("📝 Sending RAW JSON to VEO2:")
            print("="*50)
            print(raw_json_prompt)
            print("="*50)
            
            # Get VEO2 client
            output_dir = self.session_context.session_dir + "/video_clips"
            veo_client = self.veo_factory.create_client(
                model=VeoModel.VEO2,
                output_dir=output_dir
            )
            
            print("🚀 Sending RAW JSON directly to VEO2...")
            
            # Generate video with RAW JSON as prompt
            video_path = veo_client.generate_video(
                prompt=raw_json_prompt,  # RAW JSON string
                duration=8.0,
                clip_id="raw-json-test"
            )
            
            print(f"✅ VEO2 Response: {video_path}")
            
            if video_path:
                print(f"🎥 Video saved to: {video_path}")
                return video_path
            else:
                print("❌ No video path returned")
                return None
                
        except Exception as e:
            print(f"❌ Error in VEO2 test: {e}")
            import traceback
            traceback.print_exc()
            return None

def main():
    """Run the RAW JSON VEO2 test"""
    
    # Test with IKEA JSON
    ikea_json = {
        "description": "Cinematic shot of a sunlit Scandinavian bedroom. A sealed IKEA box trembles, opens, and flat pack furniture assembles rapidly into a serene, styled room highlighted by a yellow IKEA throw on the bed. No text.",
        "style": "cinematic",
        "camera": "fixed wide angle",
        "lighting": "natural warm with cool accents",
        "room": "Scandinavian bedroom",
        "elements": [
            "IKEA box (logo visible)",
            "bed with yellow throw",
            "bedside tables",
            "lamps",
            "wardrobe",
            "shelves",
            "mirror",
            "art",
            "rug",
            "curtains",
            "reading chair",
            "plants"
        ],
        "motion": "box opens, furniture assembles precisely and rapidly",
        "ending": "calm, modern space with yellow IKEA accent",
        "text": "none",
        "keywords": [
            "16:9",
            "IKEA",
            "Scandinavian",
            "fast assembly",
            "no text",
            "warm & cool tones"
        ]
    }
    
    print("🧪 TEST 1: IKEA JSON (Complex Structure)")
    test = RawVEO2JSONTest()
    result = test.test_veo2_with_raw_json(ikea_json)
    
    if result:
        print(f"🎉 SUCCESS! Video generated: {result}")
    else:
        print("❌ FAILED! No video generated")
    
    # Also test with the original format
    print("\n" + "="*70 + "\n")
    print("🧪 TEST 2: Original JSON Format")
    
    original_json = {
        "shot": {
            "composition": "Medium tracking shot, 50mm lens, shot on RED V-Raptor 8K with Netflix-approved HDR setup, shallow depth of field",
            "camera_motion": "smooth Steadicam walk-along, slight handheld bounce for naturalistic rhythm",
            "frame_rate": "24fps",
            "film_grain": "clean digital with film-emulated LUT for warmth and vibrancy"
        },
        "subject": {
            "description": "A young woman with a petite frame and soft porcelain complexion. She has oversized, almond-shaped eyes with long lashes, subtle pink-tinted cheeks, and a heart-shaped face. Her inky-black bob is slightly tousled and clipped to one side with a small red strawberry hairpin.",
            "wardrobe": "Crocheted ivory halter with scalloped trim, fitted high-waisted denim shorts, wide tan belt with red enamel star buckle, oversized red gingham blouse slipped off one shoulder, strawberry hairpin in side-parted bob"
        },
        "scene": {
            "location": "a quiet urban street bathed in early morning sunlight",
            "time_of_day": "early morning",
            "environment": "empty sidewalks, golden sunlight reflecting off puddles and windows, occasional birds fluttering by, street slightly wet from overnight rain"
        },
        "cinematography": {
            "lighting": "natural golden-hour lighting with soft HDR bounce, gentle lens flare through morning haze",
            "tone": "playful, stylish, vibrant",
            "notes": "STRICTLY NO on-screen subtitles, lyrics, captions, or text overlays. Final render must be clean visual-only."
        }
    }
    
    test2 = RawVEO2JSONTest()
    test2.session_id = "veo2-raw-json-test-2"
    test2.session_context = SessionContext(test2.session_id)
    
    result2 = test2.test_veo2_with_raw_json(original_json)
    
    if result2:
        print(f"🎉 SUCCESS! Video generated: {result2}")
    else:
        print("❌ FAILED! No video generated")

if __name__ == "__main__":
    main()