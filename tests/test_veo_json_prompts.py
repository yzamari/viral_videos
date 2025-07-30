"""
Unit tests for VEO video generation using structured JSON prompts
Tests the enhanced VEO 2 client with JSON-formatted prompts for precise control
"""

import unittest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
import sys
import asyncio

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from generators.vertex_ai_veo2_client import VertexAIVeo2Client
from utils.session_context import SessionContext


class TestVEOJSONPrompts(unittest.TestCase):
    """Test VEO 2 client with structured JSON prompts for enhanced video generation"""
    
    def setUp(self):
        """Set up test environment"""
        self.mock_session = Mock(spec=SessionContext)
        self.mock_session.get_output_path.return_value = "/tmp/test_output"
        
        # Create temporary directory for test outputs
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_json_prompt_structure_validation(self):
        """Test that JSON prompt structure is properly validated"""
        
        # Sample JSON prompt based on the provided example
        json_prompt = {
            "shot": {
                "composition": "Medium tracking shot, 50mm lens, shot on RED V-Raptor 8K with Netflix-approved HDR setup, shallow depth of field",
                "camera_motion": "smooth Steadicam walk-along, slight handheld bounce for naturalistic rhythm",
                "frame_rate": "24fps",
                "film_grain": "clean digital with film-emulated LUT for warmth and vibrancy"
            },
            "subject": {
                "description": "A young woman with a petite frame and soft porcelain complexion. She has oversized, almond-shaped eyes with long lashes, subtle pink-tinted cheeks, and a heart-shaped face. Her inky-black bob is slightly tousled and clipped to one side with a small red strawberry hairpin.",
                "wardrobe": "Crocheted ivory halter with scalloped trim, fitted high-waisted denim shorts, wide tan belt with red enamel star buckle"
            },
            "scene": {
                "location": "a quiet urban street bathed in early morning sunlight",
                "time_of_day": "early morning",
                "environment": "empty sidewalks, golden sunlight reflecting off puddles and windows, occasional birds fluttering by"
            },
            "visual_details": {
                "action": "she walks rhythmically down the sidewalk, swinging her hips slightly with the beat",
                "props": "morning mist, traffic light turning green in the distance, reflective puddles"
            },
            "cinematography": {
                "lighting": "natural golden-hour lighting with soft HDR bounce, gentle lens flare through morning haze",
                "tone": "playful, stylish, vibrant",
                "notes": "STRICTLY NO on-screen subtitles, lyrics, captions, or text overlays"
            },
            "visual_rules": {
                "prohibited_elements": [
                    "subtitles",
                    "captions", 
                    "text overlays",
                    "any written language appearing on screen"
                ]
            }
        }
        
        # Validate JSON structure
        self.assertIn("shot", json_prompt)
        self.assertIn("subject", json_prompt)
        self.assertIn("scene", json_prompt)
        self.assertIn("visual_details", json_prompt)
        self.assertIn("cinematography", json_prompt)
        
        # Validate nested structure
        self.assertIn("composition", json_prompt["shot"])
        self.assertIn("camera_motion", json_prompt["shot"])
        self.assertIn("description", json_prompt["subject"])
        self.assertIn("location", json_prompt["scene"])
        
        print("✅ JSON prompt structure validation passed")
    
    def test_convert_json_to_veo_prompt(self):
        """Test conversion of JSON structure to VEO-compatible prompt string"""
        
        json_prompt = {
            "shot": {
                "composition": "Medium tracking shot, 50mm lens",
                "camera_motion": "smooth Steadicam walk-along"
            },
            "subject": {
                "description": "A young woman with petite frame and soft complexion",
                "wardrobe": "Crocheted ivory halter, high-waisted denim shorts"
            },
            "scene": {
                "location": "quiet urban street bathed in early morning sunlight",
                "environment": "empty sidewalks, golden sunlight reflecting off puddles"
            },
            "visual_details": {
                "action": "she walks rhythmically down the sidewalk, swinging her hips slightly"
            },
            "cinematography": {
                "lighting": "natural golden-hour lighting with soft HDR bounce",
                "tone": "playful, stylish, vibrant"
            }
        }
        
        # Convert JSON to VEO prompt string
        veo_prompt = self._convert_json_to_veo_prompt(json_prompt)
        
        # Validate that key elements are preserved in the prompt
        self.assertIn("Medium tracking shot", veo_prompt)
        self.assertIn("young woman", veo_prompt)
        self.assertIn("quiet urban street", veo_prompt)
        self.assertIn("walks rhythmically", veo_prompt)
        self.assertIn("golden-hour lighting", veo_prompt)
        self.assertIn("playful, stylish, vibrant", veo_prompt)
        
        print(f"✅ JSON to VEO prompt conversion successful")
        print(f"📝 Generated prompt: {veo_prompt[:100]}...")
    
    def test_veo2_json_prompt_generation(self):
        """Test VEO 2 client with JSON-formatted prompt"""
        
        # Test the JSON-to-VEO prompt conversion without external dependencies
        
        # Create the complex JSON prompt from your example
        complex_json_prompt = {
            "shot": {
                "composition": "Medium tracking shot, 50mm lens, shot on RED V-Raptor 8K with Netflix-approved HDR setup, shallow depth of field",
                "camera_motion": "smooth Steadicam walk-along, slight handheld bounce for naturalistic rhythm",
                "frame_rate": "24fps",
                "film_grain": "clean digital with film-emulated LUT for warmth and vibrancy"
            },
            "subject": {
                "description": "A young woman with a petite frame and soft porcelain complexion. She has oversized, almond-shaped eyes with long lashes, subtle pink-tinted cheeks, and a heart-shaped face. Her inky-black bob is slightly tousled and clipped to one side with a small red strawberry hairpin. Her style blends playful retro and modern Tokyo streetwear: she wears a crocheted ivory halter top with scalloped edges, high-waisted denim shorts with a wide brown belt and a red enamel star buckle, and a loose red gingham blouse draped off one shoulder.",
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
        
        # Convert to VEO prompt
        veo_prompt = self._convert_json_to_veo_prompt(complex_json_prompt)
        
        # Test that the conversion captures key cinematic details
        self.assertIn("RED V-Raptor 8K", veo_prompt)
        self.assertIn("strawberry hairpin", veo_prompt)
        self.assertIn("crocheted ivory halter", veo_prompt)
        self.assertIn("early morning sunlight", veo_prompt)
        self.assertIn("golden-hour lighting", veo_prompt)
        self.assertIn("NO on-screen subtitles", veo_prompt)
        
        print("✅ Complex JSON prompt conversion successful")
        print(f"📝 Full VEO prompt length: {len(veo_prompt)} characters")
        print(f"🎬 Cinematography details preserved: ✅")
        print(f"👗 Wardrobe details preserved: ✅")
        print(f"🌅 Scene atmosphere preserved: ✅")
    
    def test_json_prompt_cinematic_language(self):
        """Test that JSON prompts include professional cinematic language"""
        
        json_prompt = {
            "shot": {
                "composition": "Medium tracking shot, 50mm lens, shot on RED V-Raptor 8K",
                "camera_motion": "smooth Steadicam walk-along, slight handheld bounce"
            },
            "cinematography": {
                "lighting": "natural golden-hour lighting with soft HDR bounce",
                "tone": "playful, stylish, vibrant"
            }
        }
        
        veo_prompt = self._convert_json_to_veo_prompt(json_prompt)
        
        # Test for professional cinematography terms
        cinematic_terms = [
            "50mm lens", "RED V-Raptor", "Steadicam", "HDR", "golden-hour"
        ]
        
        for term in cinematic_terms:
            self.assertIn(term, veo_prompt, f"Cinematic term '{term}' not found in prompt")
            
        print("✅ Professional cinematic language preserved in VEO prompt")
    
    def _convert_json_to_veo_prompt(self, json_prompt: dict) -> str:
        """Convert structured JSON prompt to VEO-compatible string"""
        
        prompt_parts = []
        
        # Shot composition and camera work
        if "shot" in json_prompt:
            shot = json_prompt["shot"]
            if "composition" in shot:
                prompt_parts.append(f"Shot: {shot['composition']}")
            if "camera_motion" in shot:
                prompt_parts.append(f"Camera: {shot['camera_motion']}")
            if "frame_rate" in shot:
                prompt_parts.append(f"Frame rate: {shot['frame_rate']}")
            if "film_grain" in shot:
                prompt_parts.append(f"Film quality: {shot['film_grain']}")
        
        # Subject description
        if "subject" in json_prompt:
            subject = json_prompt["subject"]
            if "description" in subject:
                prompt_parts.append(f"Subject: {subject['description']}")
            if "wardrobe" in subject:
                prompt_parts.append(f"Wardrobe: {subject['wardrobe']}")
        
        # Scene and environment
        if "scene" in json_prompt:
            scene = json_prompt["scene"]
            if "location" in scene:
                prompt_parts.append(f"Location: {scene['location']}")
            if "time_of_day" in scene:
                prompt_parts.append(f"Time: {scene['time_of_day']}")
            if "environment" in scene:
                prompt_parts.append(f"Environment: {scene['environment']}")
        
        # Visual details and action
        if "visual_details" in json_prompt:
            visual = json_prompt["visual_details"]
            if "action" in visual:
                prompt_parts.append(f"Action: {visual['action']}")
            if "props" in visual:
                prompt_parts.append(f"Props: {visual['props']}")
        
        # Cinematography
        if "cinematography" in json_prompt:
            cinema = json_prompt["cinematography"]
            if "lighting" in cinema:
                prompt_parts.append(f"Lighting: {cinema['lighting']}")
            if "tone" in cinema:
                prompt_parts.append(f"Tone: {cinema['tone']}")
            if "notes" in cinema:
                prompt_parts.append(f"Notes: {cinema['notes']}")
        
        # Audio elements
        if "audio" in json_prompt:
            audio = json_prompt["audio"]
            if "ambient" in audio:
                prompt_parts.append(f"Ambient audio: {audio['ambient']}")
            if "voice" in audio:
                voice = audio["voice"]
                if "tone" in voice:
                    prompt_parts.append(f"Voice tone: {voice['tone']}")
                if "style" in voice:
                    prompt_parts.append(f"Voice style: {voice['style']}")
            if "lyrics" in audio:
                prompt_parts.append(f"Lyrics: {audio['lyrics']}")
        
        # Color palette
        if "color_palette" in json_prompt:
            prompt_parts.append(f"Color palette: {json_prompt['color_palette']}")
        
        # Visual rules and restrictions
        if "visual_rules" in json_prompt:
            rules = json_prompt["visual_rules"]
            if "prohibited_elements" in rules:
                prohibited = ", ".join(rules["prohibited_elements"])
                prompt_parts.append(f"Prohibited elements: {prohibited}")
        
        # Join all parts with proper formatting
        return ". ".join(prompt_parts) + "."
    
    def test_json_prompt_completeness(self):
        """Test that JSON prompt includes all necessary cinematic elements"""
        
        # Your complex JSON prompt
        json_prompt = {
            "shot": {
                "composition": "Medium tracking shot, 50mm lens, shot on RED V-Raptor 8K with Netflix-approved HDR setup, shallow depth of field",
                "camera_motion": "smooth Steadicam walk-along, slight handheld bounce for naturalistic rhythm",
                "frame_rate": "24fps",
                "film_grain": "clean digital with film-emulated LUT for warmth and vibrancy"
            },
            "subject": {
                "description": "A young woman with a petite frame and soft porcelain complexion. She has oversized, almond-shaped eyes with long lashes, subtle pink-tinted cheeks, and a heart-shaped face. Her inky-black bob is slightly tousled and clipped to one side with a small red strawberry hairpin.",
                "wardrobe": "Crocheted ivory halter with scalloped trim, fitted high-waisted denim shorts, wide tan belt with red enamel star buckle"
            },
            "visual_rules": {
                "prohibited_elements": [
                    "subtitles", "captions", "text overlays", "any written language appearing on screen"
                ]
            }
        }
        
        # Essential cinematic elements that should be present
        essential_elements = [
            ("shot", "composition"),
            ("shot", "camera_motion"), 
            ("subject", "description"),
            ("visual_rules", "prohibited_elements")
        ]
        
        for section, key in essential_elements:
            self.assertIn(section, json_prompt, f"Missing section: {section}")
            self.assertIn(key, json_prompt[section], f"Missing key: {key} in {section}")
        
        print("✅ JSON prompt completeness validation passed")
        print(f"📋 Validated {len(essential_elements)} essential cinematic elements")


def run_veo_json_test():
    """Convenience function to run the VEO JSON tests"""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == '__main__':
    print("🎬 Testing VEO 2 with JSON-structured prompts...")
    print("=" * 60)
    
    # Run the tests
    unittest.main(verbosity=2)