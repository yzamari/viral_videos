#!/usr/bin/env python3
"""
Demo: VEO JSON Prompt Integration
Demonstrates how to use JSON-structured prompts with VEO 2 client
"""

import asyncio
import sys
import os
import tempfile
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.veo_json_prompts import VEOJSONPromptConverter
from utils.session_context import SessionContext


class VEOJSONDemo:
    """Demo class for VEO JSON prompt integration"""
    
    def __init__(self):
        self.converter = VEOJSONPromptConverter()
        print("🎬 VEO JSON Integration Demo initialized")
    
    def create_japanese_street_scene_json(self) -> Dict[str, Any]:
        """Create the complex Japanese street scene JSON prompt"""
        return {
            "shot": {
                "composition": "Medium tracking shot, 50mm lens, shot on RED V-Raptor 8K with Netflix-approved HDR setup, shallow depth of field",
                "camera_motion": "smooth Steadicam walk-along, slight handheld bounce for naturalistic rhythm",
                "frame_rate": "24fps",
                "film_grain": "clean digital with film-emulated LUT for warmth and vibrancy"
            },
            "subject": {
                "description": "A young woman with a petite frame and soft porcelain complexion. She has oversized, almond-shaped eyes with long lashes, subtle pink-tinted cheeks, and a heart-shaped face. Her inky-black bob is slightly tousled and clipped to one side with a small red strawberry hairpin. Her style blends playful retro and modern Tokyo streetwear",
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
    
    def demonstrate_json_conversion(self):
        """Demonstrate JSON to VEO prompt conversion"""
        print("\n🎯 Step 1: JSON Structure Validation")
        print("-" * 40)
        
        # Create JSON prompt
        json_prompt = self.create_japanese_street_scene_json()
        
        # Validate structure
        is_valid = self.converter.validate_json_structure(json_prompt)
        print(f"JSON Structure Valid: {'✅' if is_valid else '❌'}")
        
        if not is_valid:
            return None
        
        print(f"JSON Sections: {list(json_prompt.keys())}")
        
        print("\n🎬 Step 2: Convert to VEO Prompt")
        print("-" * 40)
        
        # Convert to VEO prompt
        veo_prompt = self.converter.convert_json_to_veo_prompt(json_prompt)
        
        print(f"VEO Prompt Length: {len(veo_prompt)} characters")
        print(f"Preview: {veo_prompt[:200]}...")
        
        return veo_prompt
    
    def demonstrate_veo_generation_simulation(self, veo_prompt: str):
        """Simulate VEO generation process (without actual API call)"""
        print("\n🚀 Step 3: VEO Generation Simulation")
        print("-" * 40)
        
        # This would be where we call the actual VEO API
        print("📝 VEO Request Parameters:")
        print(f"  - Model: veo-2.0-generate-001")
        print(f"  - Duration: 8.0 seconds")
        print(f"  - Aspect Ratio: 9:16 (vertical)")
        print(f"  - Prompt Length: {len(veo_prompt)} chars")
        
        # Simulate processing time
        import time
        print("⏳ Simulating VEO processing...")
        
        # Extract key elements that should be preserved
        key_elements = self._extract_key_elements(veo_prompt)
        print(f"\n🔍 Key Cinematic Elements Detected:")
        for element in key_elements:
            print(f"  ✅ {element}")
        
        print(f"\n✨ Simulated VEO generation completed!")
        print(f"📹 Output: japanese_street_scene_8s.mp4")
    
    def _extract_key_elements(self, prompt: str) -> list:
        """Extract key cinematic elements from the prompt"""
        elements = []
        
        # Check for professional equipment
        if "RED V-Raptor 8K" in prompt:
            elements.append("Professional 8K camera specified")
        
        # Check for specific lens
        if "50mm lens" in prompt:
            elements.append("50mm lens composition")
        
        # Check for character details
        if "strawberry hairpin" in prompt:
            elements.append("Detailed character styling")
        
        # Check for cinematography
        if "golden-hour lighting" in prompt:
            elements.append("Professional lighting direction")
        
        # Check for audio specification
        if "Japanese" in prompt:
            elements.append("Japanese audio/dialogue specified")
        
        # Check for restrictions
        if "NO on-screen subtitles" in prompt:
            elements.append("Text overlay restrictions")
        
        # Check for environment
        if "early morning sunlight" in prompt:
            elements.append("Specific time and lighting")
        
        return elements
    
    def show_json_vs_standard_comparison(self):
        """Show comparison between JSON and standard prompts"""
        print("\n📊 Step 4: JSON vs Standard Prompt Comparison")
        print("-" * 50)
        
        # Standard prompt approach
        standard_prompt = "A young woman walks down a street in the morning singing in Japanese"
        
        # JSON prompt approach
        json_prompt = self.create_japanese_street_scene_json()
        veo_prompt = self.converter.convert_json_to_veo_prompt(json_prompt)
        
        print("📝 Standard Prompt:")
        print(f"  Length: {len(standard_prompt)} characters")
        print(f"  Content: {standard_prompt}")
        
        print(f"\n🎬 JSON-Enhanced Prompt:")
        print(f"  Length: {len(veo_prompt)} characters")
        print(f"  Sections: {len(json_prompt)} major cinematic elements")
        print(f"  Detail Level: Professional cinematography specification")
        
        print(f"\n💡 Benefits of JSON Approach:")
        print(f"  ✅ Precise camera and lens specification")
        print(f"  ✅ Detailed character and wardrobe description")
        print(f"  ✅ Professional lighting and color direction")
        print(f"  ✅ Specific audio and dialogue requirements")
        print(f"  ✅ Clear visual restrictions and rules")
        print(f"  ✅ Structured, reproducible prompt engineering")


def main():
    """Run the VEO JSON integration demo"""
    print("🎬 VEO JSON Prompt Integration Demo")
    print("=" * 50)
    print("Based on: https://dev.to/therealmrmumba/how-to-create-any-google-veo-3-video-styles-with-json-format-hack-1ond")
    print("")
    
    demo = VEOJSONDemo()
    
    # Step 1: Demonstrate JSON conversion
    veo_prompt = demo.demonstrate_json_conversion()
    
    if veo_prompt:
        # Step 2: Simulate VEO generation
        demo.demonstrate_veo_generation_simulation(veo_prompt)
        
        # Step 3: Show comparison
        demo.show_json_vs_standard_comparison()
        
        print(f"\n🎯 Integration Summary:")
        print(f"✅ JSON structure validated and converted")
        print(f"✅ VEO-compatible prompt generated ({len(veo_prompt)} chars)")
        print(f"✅ Professional cinematography elements preserved")
        print(f"✅ Ready for VEO 2 API integration")
        
        print(f"\n💻 Next Steps for Implementation:")
        print(f"1. Integrate VEOJSONPromptConverter with VertexAIVeo2Client")
        print(f"2. Add JSON prompt support to video generation pipeline")
        print(f"3. Create JSON prompt templates for common video styles")
        print(f"4. Test with actual VEO API calls")
    
    print(f"\n✨ Demo completed!")


if __name__ == '__main__':
    main()