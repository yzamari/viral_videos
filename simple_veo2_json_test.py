#!/usr/bin/env python3
"""
Simple unit test for VEO2 with raw JSON prompt.
Direct call to VEO2 API without full generation pipeline.
"""

import json
import os
import sys
import asyncio
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from generators.veo_client_factory import VeoClientFactory, VeoModel
from utils.session_context import SessionContext
from models.video_models import Platform

class SimpleVEO2JSONTest:
    """Simple test for VEO2 with JSON prompts"""
    
    def __init__(self):
        self.session_id = "veo2-ikea-json-test"
        self.session_context = SessionContext(self.session_id)
        self.veo_factory = VeoClientFactory()
    
    def create_veo_prompt_from_json(self, json_data: Dict[str, Any]) -> str:
        """Convert JSON data to VEO prompt string"""
        try:
            # Check if this is the new simpler format
            if "description" in json_data and isinstance(json_data.get("description"), str):
                # New format with direct description
                prompt_parts = []
                
                # Main description
                prompt_parts.append(json_data["description"])
                
                # Add style info
                if json_data.get("style"):
                    prompt_parts.append(f"{json_data['style']} style")
                
                # Camera details
                if json_data.get("camera"):
                    prompt_parts.append(f"shot with {json_data['camera']}")
                
                # Lighting
                if json_data.get("lighting"):
                    prompt_parts.append(f"lighting: {json_data['lighting']}")
                
                # Motion details
                if json_data.get("motion"):
                    prompt_parts.append(f"motion: {json_data['motion']}")
                
                # Elements (convert list to description)
                if json_data.get("elements") and isinstance(json_data["elements"], list):
                    elements_str = ", ".join(json_data["elements"])
                    prompt_parts.append(f"featuring: {elements_str}")
                
                # Keywords
                if json_data.get("keywords") and isinstance(json_data["keywords"], list):
                    keywords_str = ", ".join(json_data["keywords"])
                    prompt_parts.append(f"keywords: {keywords_str}")
                
                return ". ".join(prompt_parts)
            
            else:
                # Original format handling
                shot = json_data.get("shot", {})
                subject = json_data.get("subject", {})
                scene = json_data.get("scene", {})
                cinematography = json_data.get("cinematography", {})
                
                prompt_parts = []
                
                if subject.get("description"):
                    prompt_parts.append(subject["description"])
                
                if subject.get("wardrobe"):
                    prompt_parts.append(f"wearing {subject['wardrobe']}")
                
                if scene.get("location"):
                    prompt_parts.append(f"in {scene['location']}")
                
                if scene.get("environment"):
                    prompt_parts.append(f"with {scene['environment']}")
                
                if shot.get("composition"):
                    prompt_parts.append(f"captured in {shot['composition']}")
                
                if shot.get("camera_motion"):
                    prompt_parts.append(f"using {shot['camera_motion']}")
                
                if cinematography.get("lighting"):
                    prompt_parts.append(f"with {cinematography['lighting']}")
                
                if cinematography.get("tone"):
                    prompt_parts.append(f"conveying a {cinematography['tone']} tone")
                
                if shot.get("frame_rate"):
                    prompt_parts.append(f"at {shot['frame_rate']}")
                
                if shot.get("film_grain"):
                    prompt_parts.append(f"with {shot['film_grain']}")
                
                if cinematography.get("notes"):
                    prompt_parts.append(cinematography["notes"])
                
                return ", ".join(prompt_parts)
            
        except Exception as e:
            print(f"❌ Error converting JSON to prompt: {e}")
            # Fallback: return JSON as string
            return json.dumps(json_data, indent=2)
    
    def test_veo2_with_json(self, json_prompt: Dict[str, Any]) -> str:
        """Test VEO2 with JSON prompt"""
        print("🎬 Starting Simple VEO2 JSON Test")
        print(f"📁 Session: {self.session_id}")
        
        try:
            # Convert JSON to VEO prompt
            veo_prompt = self.create_veo_prompt_from_json(json_prompt)
            print(f"🎯 VEO Prompt: {veo_prompt[:200]}...")
            
            # Get VEO2 client
            output_dir = self.session_context.session_dir + "/video_clips"
            veo_client = self.veo_factory.create_client(
                model=VeoModel.VEO2,
                output_dir=output_dir
            )
            
            print("🚀 Sending to VEO2...")
            
            # Generate video (synchronous)
            video_path = veo_client.generate_video(
                prompt=veo_prompt,
                duration=8.0,
                clip_id="json-test-clip"
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
    """Run the simple VEO2 JSON test"""
    
    # Your exact JSON
    json_prompt = {
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
    
    # Run test
    test = SimpleVEO2JSONTest()
    
    # Run test
    result = test.test_veo2_with_json(json_prompt)
    
    if result:
        print(f"🎉 SUCCESS! Video generated: {result}")
    else:
        print("❌ FAILED! No video generated")

if __name__ == "__main__":
    main()