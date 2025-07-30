#!/usr/bin/env python3
"""
VEO2 Unit Test with IKEA Room Assembly JSON
Tests VEO2 with the specific JSON format provided by user
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

class VEO2PapayaJSONTest:
    """VEO2 test with Papaya Shake Bar JSON"""
    
    def __init__(self):
        self.session_id = "veo2-papaya-shakebar-test"
        self.session_context = SessionContext(self.session_id)
        self.veo_factory = VeoClientFactory()
    
    def convert_papaya_json_to_veo_prompt(self, json_data: Dict[str, Any]) -> str:
        """Convert the Papaya shake bar JSON to VEO prompt string"""
        try:
            prompt_parts = []
            
            # Extract metadata
            metadata = json_data.get("metadata", {})
            
            # Base style and setup
            if metadata.get("base_style"):
                prompt_parts.append(f"Style: {metadata['base_style']}")
            
            if metadata.get("aspect_ratio"):
                prompt_parts.append(f"Aspect ratio: {metadata['aspect_ratio']}")
            
            if metadata.get("room_description"):
                prompt_parts.append(f"Setting: {metadata['room_description']}")
            
            if metadata.get("camera_setup"):
                prompt_parts.append(f"Camera: {metadata['camera_setup']}")
            
            # Key elements
            if metadata.get("key_elements"):
                elements = ", ".join(metadata["key_elements"])
                prompt_parts.append(f"Key elements: {elements}")
            
            # Assembled elements 
            if metadata.get("assembled_elements"):
                assembled = ", ".join(metadata["assembled_elements"])
                prompt_parts.append(f"Final assembled items: {assembled}")
            
            # Negative prompts
            if metadata.get("negative_prompts"):
                negatives = ", ".join(metadata["negative_prompts"])
                prompt_parts.append(f"Avoid: {negatives}")
            
            # Timeline conversion to narrative
            timeline = json_data.get("timeline", [])
            if timeline:
                prompt_parts.append("Sequence:")
                
                for seq in timeline:
                    timestamp = seq.get("timestamp", "")
                    action = seq.get("action", "")
                    audio = seq.get("audio", "")
                    
                    sequence_desc = f"{timestamp}: {action}"
                    if audio:
                        sequence_desc += f" (Audio: {audio})"
                    
                    prompt_parts.append(sequence_desc)
            
            return ". ".join(prompt_parts)
            
        except Exception as e:
            print(f"❌ Error converting Papaya JSON to VEO prompt: {e}")
            # Fallback: return JSON as string
            return json.dumps(json_data, indent=2)
    
    def test_veo2_with_papaya_json_direct(self, json_prompt: Dict[str, Any]) -> str:
        """Test VEO2 with Papaya shake bar JSON sent directly (no conversion)"""
        print("🎬 Starting VEO2 Papaya Shake Bar JSON Test (DIRECT JSON)")
        print(f"📁 Session: {self.session_id}")
        
        try:
            # Send JSON directly to VEO2 without conversion
            print("📋 Sending raw JSON structure directly to VEO2...")
            print(f"🔍 JSON Keys: {list(json_prompt.keys())}")
            print(f"🔍 Metadata Keys: {list(json_prompt['metadata'].keys())}")
            print(f"🔍 Timeline Sequences: {len(json_prompt['timeline'])}")
            
            # Get VEO2 client
            output_dir = self.session_context.session_dir + "/video_clips"
            veo_client = self.veo_factory.create_client(
                model=VeoModel.VEO2,
                output_dir=output_dir
            )
            
            print("🚀 Sending Papaya Shake Bar JSON directly to VEO2...")
            
            # Generate video using JSON directly as prompt
            # VEO2 should be able to handle structured JSON input
            video_path = veo_client.generate_video(
                prompt=json.dumps(json_prompt, indent=2),  # Send JSON as formatted string
                duration=8.0,  # 8 seconds as specified in timeline
                clip_id="papaya-shakebar-ad-direct"
            )
            
            print(f"✅ VEO2 Response: {video_path}")
            
            if video_path:
                print(f"🎥 Papaya Shake Bar ad (direct JSON) saved to: {video_path}")
                return video_path
            else:
                print("❌ No video path returned")
                return None
                
        except Exception as e:
            print(f"❌ Error in VEO2 Papaya direct JSON test: {e}")
            import traceback
            traceback.print_exc()
            return None

def main():
    """Run the VEO2 Papaya Shake Bar JSON test"""
    
    # Papaya Shake Bar Advertisement JSON - Detailed Version
    papaya_json_prompt = {
        "metadata": {
            "prompt_name": "Papaya Shake Bar - Morning Energy to Night Sophistication",
            "base_style": "ultra-detailed, cinematic commercial, vibrant colors, high-energy transitions, 4K HDR",
            "aspect_ratio": "16:9",
            "room_description": "Luxurious tropical shake bar with floor-to-ceiling windows, living papaya tree centerpiece, hand-painted papaya murals, Edison bulb chandeliers, marble countertops with gold veining, tropical wood accents, Instagram-worthy neon signs, professional juice bar setup with chrome equipment, leather bar stools, hanging plants, and adaptive lighting system.",
            "camera_setup": "Professional multi-angle cinematography: sweeping crane shots, macro close-ups of drinks, tracking shots following bartenders, 360-degree bar reveals, slow-motion pour shots, dynamic lighting changes, seamless day-to-night transitions.",
            "key_elements": [
                "Illuminated 'Papaya Shake Bar' logo with tropical font",
                "Fresh whole papayas, mangoes, pineapples, coconuts, dragon fruit",
                "High-end Vitamix blenders, espresso machines, cocktail shakers",
                "Custom papaya-shaped glasses and cocktail vessels",
                "Tropical plants: monstera, bird of paradise, palm fronds",
                "Artisanal ingredient displays in glass containers"
            ],
            "morning_elements": [
                "Golden sunlight streaming through large windows",
                "Fresh fruit prep stations with colorful displays",
                "Yoga mats and gym bags from health-conscious customers",
                "Laptops and newspapers of morning workers",
                "Barista in bright tropical uniform making smoothies",
                "Acai bowls, granola toppings, chia seeds visible",
                "Natural wood and white marble surfaces",
                "Energetic customers in workout clothes and business attire",
                "Fresh mint, spinach, protein powders, coconut water",
                "Motivational health quotes on chalkboard menus"
            ],
            "night_elements": [
                "Dramatic purple and pink LED underglow lighting",
                "Professional bartender in sleek black uniform with gold accents",
                "Premium spirits: aged rum, top-shelf tequila, craft vodka",
                "Crystal cocktail glasses with gold rims",
                "Sophisticated adults in evening attire",
                "Ambient candles and hanging Edison bulbs",
                "Leather seating areas with velvet cushions",
                "Professional cocktail tools: muddlers, jiggers, strainers",
                "Smoke effects from dry ice in specialty cocktails",
                "Live tropical plants illuminated with accent lighting",
                "Luxury bar accessories and premium garnish station",
                "Elegant papaya-infused cocktails with artistic presentation"
            ],
            "transition_elements": [
                "Automated lighting system changing color temperature",
                "Staff changing uniforms and bar setup",
                "Menu boards flipping from smoothies to cocktails",
                "Seating arrangements transforming from casual to intimate",
                "Background music shifting from upbeat to sophisticated",
                "Glassware changing from mason jars to crystal cocktail glasses"
            ],
            "negative_prompts": ["no alcohol visible during morning", "no children in nighttime scenes", "no dark lighting in morning", "no casual dress in evening cocktail scene"]
        },
        "timeline": [
            {
                "sequence": 1,
                "timestamp": "00:00-00:02",
                "action": "MORNING ENERGY: Golden hour sunlight floods the space. Close-up of fresh papayas being expertly diced, revealing vibrant orange flesh. Professional barista operates chrome Vitamix blender creating colorful layered smoothies. Health-conscious customers in activewear and business casual enjoy acai bowls and protein shakes. Detailed shots of tropical fruit displays, chia seed toppings, fresh mint garnishes, coconut shavings. Wide shot reveals the full morning atmosphere with natural lighting and energetic ambiance.",
                "audio": "Uplifting tropical music, rhythmic blender sounds, satisfied customer 'mmm' reactions, gentle morning bird sounds, coffee machine steam, cheerful conversations about fitness goals."
            },
            {
                "sequence": 2,
                "timestamp": "00:02-00:04",
                "action": "SIGNATURE MORNING DRINKS: Slow-motion macro shots of signature morning creations: Papaya-Mango Paradise (orange gradient with coconut cream), Green Goddess Detox (spinach, papaya, pineapple with spirulina swirl), Protein Power Bowl (papaya base with granola, nuts, berries). Each drink showcased with artistic garnishes, edible flowers, and custom papaya-shaped glasses. Text appears: 'FUEL YOUR DAY - NATURAL ENERGY'",
                "audio": "Dynamic commercial jingle with tropical beats, blending sounds in rhythm, satisfied customer testimonials, energetic voiceover highlighting fresh ingredients."
            },
            {
                "sequence": 3,
                "timestamp": "00:04-00:06",
                "action": "DRAMATIC DAY-TO-NIGHT TRANSFORMATION: Time-lapse sequence showing the complete bar metamorphosis. Lighting system automatically shifts from bright natural white to warm amber, then to sophisticated purple-pink LED. Staff members change from bright tropical uniforms to sleek black evening attire. Menu boards flip revealing cocktail selections. Seating transforms from casual high-top tables to intimate lounge areas. The living papaya tree centerpiece becomes dramatically lit. Chrome equipment remains but is now accompanied by premium bar tools.",
                "audio": "Building orchestral music with electronic elements, mechanical sounds of lighting changes, subtle clock ticking, ambient evening city sounds beginning to emerge."
            },
            {
                "sequence": 4,
                "timestamp": "00:06-00:08",
                "action": "SOPHISTICATED NIGHTTIME COCKTAIL EXPERIENCE: Dimly lit luxurious atmosphere with professional bartender in black uniform creating artisanal papaya cocktails. Close-ups of premium ingredients: aged Caribbean rum, fresh papaya puree, artisanal bitters, dry ice creating smoke effects. Elegantly dressed adults (25-45 years) in evening attire enjoying sophisticated drinks: Papaya Caipirinha with gold leaf, Smoky Papaya Margarita with chili rim, Papaya Champagne Cocktail with edible flowers. Detailed shots of crystal glasses, professional muddling techniques, garnish artistry, intimate conversations, candle-lit ambiance.",
                "audio": "Smooth jazz with tropical undertones, rhythmic cocktail shaker sounds, ice clinking against crystal, sophisticated adult laughter, intimate conversations, ambient lounge atmosphere, bartender explaining cocktail craftsmanship."
            }
        ]
    }
    
    # Run test
    test = VEO2PapayaJSONTest()
    
    print("📋 Input JSON Structure:")
    print(f"  - Metadata keys: {list(papaya_json_prompt['metadata'].keys())}")
    print(f"  - Timeline sequences: {len(papaya_json_prompt['timeline'])}")
    print(f"  - Duration: 8 seconds (00:00-00:08)")
    print("=" * 60)
    
    # Run test with direct JSON (no conversion)
    result = test.test_veo2_with_papaya_json_direct(papaya_json_prompt)
    
    if result:
        print(f"🎉 SUCCESS! Papaya Shake Bar ad generated: {result}")
    else:
        print("❌ FAILED! No video generated")

if __name__ == "__main__":
    main()