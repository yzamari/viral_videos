"""
VEO JSON Prompt Utility - Convert structured JSON prompts to VEO-compatible strings
Based on https://dev.to/therealmrmumba/how-to-create-any-google-veo-3-video-styles-with-json-format-hack-1ond
"""

import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class VEOJSONPromptConverter:
    """Convert structured JSON prompts to VEO-compatible prompt strings"""
    
    def __init__(self):
        """Initialize the JSON to VEO prompt converter"""
        logger.info("🎬 VEO JSON Prompt Converter initialized")
    
    def convert_json_to_veo_prompt(self, json_prompt: Dict[str, Any]) -> str:
        """
        Convert structured JSON prompt to VEO-compatible string
        
        Args:
            json_prompt: Structured JSON prompt with cinematic details
            
        Returns:
            VEO-compatible prompt string
        """
        prompt_parts = []
        
        # Shot composition and camera work
        if "shot" in json_prompt:
            prompt_parts.extend(self._process_shot_section(json_prompt["shot"]))
        
        # Subject description  
        if "subject" in json_prompt:
            prompt_parts.extend(self._process_subject_section(json_prompt["subject"]))
        
        # Scene and environment
        if "scene" in json_prompt:
            prompt_parts.extend(self._process_scene_section(json_prompt["scene"]))
        
        # Visual details and action
        if "visual_details" in json_prompt:
            prompt_parts.extend(self._process_visual_details_section(json_prompt["visual_details"]))
        
        # Cinematography
        if "cinematography" in json_prompt:
            prompt_parts.extend(self._process_cinematography_section(json_prompt["cinematography"]))
        
        # Audio elements
        if "audio" in json_prompt:
            prompt_parts.extend(self._process_audio_section(json_prompt["audio"]))
        
        # Color palette
        if "color_palette" in json_prompt:
            prompt_parts.append(f"Color palette: {json_prompt['color_palette']}")
        
        # Dialogue
        if "dialogue" in json_prompt:
            prompt_parts.extend(self._process_dialogue_section(json_prompt["dialogue"]))
        
        # Visual rules and restrictions
        if "visual_rules" in json_prompt:
            prompt_parts.extend(self._process_visual_rules_section(json_prompt["visual_rules"]))
        
        # Join all parts with proper formatting
        final_prompt = ". ".join(prompt_parts) + "."
        
        logger.info(f"✅ Converted JSON to VEO prompt ({len(final_prompt)} characters)")
        return final_prompt
    
    def _process_shot_section(self, shot: Dict[str, Any]) -> list:
        """Process shot composition and camera work"""
        parts = []
        
        if "composition" in shot:
            parts.append(f"Shot composition: {shot['composition']}")
        
        if "camera_motion" in shot:
            parts.append(f"Camera movement: {shot['camera_motion']}")
        
        if "frame_rate" in shot:
            parts.append(f"Frame rate: {shot['frame_rate']}")
        
        if "film_grain" in shot:
            parts.append(f"Film quality: {shot['film_grain']}")
        
        return parts
    
    def _process_subject_section(self, subject: Dict[str, Any]) -> list:
        """Process subject description and wardrobe"""
        parts = []
        
        if "description" in subject:
            parts.append(f"Subject: {subject['description']}")
        
        if "wardrobe" in subject:
            parts.append(f"Wardrobe: {subject['wardrobe']}")
        
        return parts
    
    def _process_scene_section(self, scene: Dict[str, Any]) -> list:
        """Process scene location and environment"""
        parts = []
        
        if "location" in scene:
            parts.append(f"Location: {scene['location']}")
        
        if "time_of_day" in scene:
            parts.append(f"Time of day: {scene['time_of_day']}")
        
        if "environment" in scene:
            parts.append(f"Environment: {scene['environment']}")
        
        return parts
    
    def _process_visual_details_section(self, visual_details: Dict[str, Any]) -> list:
        """Process visual details and action"""
        parts = []
        
        if "action" in visual_details:
            parts.append(f"Action: {visual_details['action']}")
        
        if "props" in visual_details:
            parts.append(f"Props: {visual_details['props']}")
        
        return parts
    
    def _process_cinematography_section(self, cinematography: Dict[str, Any]) -> list:
        """Process cinematography and lighting"""
        parts = []
        
        if "lighting" in cinematography:
            parts.append(f"Lighting: {cinematography['lighting']}")
        
        if "tone" in cinematography:
            parts.append(f"Visual tone: {cinematography['tone']}")
        
        if "notes" in cinematography:
            parts.append(f"Production notes: {cinematography['notes']}")
        
        return parts
    
    def _process_audio_section(self, audio: Dict[str, Any]) -> list:
        """Process audio elements"""
        parts = []
        
        if "ambient" in audio:
            parts.append(f"Ambient audio: {audio['ambient']}")
        
        if "voice" in audio and isinstance(audio["voice"], dict):
            voice = audio["voice"]
            if "tone" in voice:
                parts.append(f"Voice tone: {voice['tone']}")
            if "style" in voice:
                parts.append(f"Voice style: {voice['style']}")
        
        if "lyrics" in audio:
            parts.append(f"Lyrics: {audio['lyrics']}")
        
        return parts
    
    def _process_dialogue_section(self, dialogue: Dict[str, Any]) -> list:
        """Process dialogue and speech"""
        parts = []
        
        if "character" in dialogue and "line" in dialogue:
            parts.append(f"Dialogue - {dialogue['character']}: {dialogue['line']}")
        
        if "subtitles" in dialogue and not dialogue["subtitles"]:
            parts.append("No subtitles or text overlays")
        
        return parts
    
    def _process_visual_rules_section(self, visual_rules: Dict[str, Any]) -> list:
        """Process visual rules and restrictions"""
        parts = []
        
        if "prohibited_elements" in visual_rules:
            prohibited = ", ".join(visual_rules["prohibited_elements"])
            parts.append(f"Prohibited visual elements: {prohibited}")
        
        return parts
    
    def validate_json_structure(self, json_prompt: Dict[str, Any]) -> bool:
        """
        Validate that JSON prompt has required structure
        
        Args:
            json_prompt: JSON prompt to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_sections = ["shot", "subject", "scene"]
        
        for section in required_sections:
            if section not in json_prompt:
                logger.error(f"❌ Missing required section: {section}")
                return False
        
        # Validate shot section
        if "shot" in json_prompt:
            shot = json_prompt["shot"]
            if "composition" not in shot:
                logger.error("❌ Shot section missing 'composition'")
                return False
        
        # Validate subject section
        if "subject" in json_prompt:
            subject = json_prompt["subject"]
            if "description" not in subject:
                logger.error("❌ Subject section missing 'description'")
                return False
        
        logger.info("✅ JSON prompt structure validation passed")
        return True
    
    def create_example_json_prompt(self) -> Dict[str, Any]:
        """Create an example JSON prompt for testing"""
        return {
            "shot": {
                "composition": "Medium tracking shot, 50mm lens, shot on RED V-Raptor 8K with Netflix-approved HDR setup, shallow depth of field",
                "camera_motion": "smooth Steadicam walk-along, slight handheld bounce for naturalistic rhythm",
                "frame_rate": "24fps",
                "film_grain": "clean digital with film-emulated LUT for warmth and vibrancy"
            },
            "subject": {
                "description": "A young woman with a petite frame and soft porcelain complexion. She has oversized, almond-shaped eyes with long lashes, subtle pink-tinted cheeks, and a heart-shaped face. Her inky-black bob is slightly tousled and clipped to one side with a small red strawberry hairpin.",
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


def demo_json_to_veo_conversion():
    """Demonstrate JSON to VEO prompt conversion"""
    print("🎬 VEO JSON Prompt Conversion Demo")
    print("=" * 50)
    
    converter = VEOJSONPromptConverter()
    
    # Create example JSON prompt
    json_prompt = converter.create_example_json_prompt()
    
    # Validate structure
    is_valid = converter.validate_json_structure(json_prompt)
    print(f"📋 JSON Structure Valid: {'✅' if is_valid else '❌'}")
    
    if is_valid:
        # Convert to VEO prompt
        veo_prompt = converter.convert_json_to_veo_prompt(json_prompt)
        
        print(f"\n📝 Generated VEO Prompt ({len(veo_prompt)} characters):")
        print("-" * 50)
        print(veo_prompt)
        print("-" * 50)
        
        # Show key elements preserved
        key_elements = [
            "RED V-Raptor 8K",
            "strawberry hairpin", 
            "early morning sunlight",
            "NO on-screen subtitles",
            "Japanese"
        ]
        
        print(f"\n🔍 Key Elements Preserved:")
        for element in key_elements:
            found = element in veo_prompt
            print(f"  {element}: {'✅' if found else '❌'}")
    
    print(f"\n✨ Demo completed!")


if __name__ == '__main__':
    demo_json_to_veo_conversion()