"""
Character Consistency Manager for recurring video characters
"""

import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
import hashlib

@dataclass
class CharacterProfile:
    """Profile for a consistent character across videos"""
    name: str
    description: str
    detailed_appearance: Dict[str, str]
    reference_images: List[str]
    voice_profile: str
    personality_traits: List[str]
    
    def to_prompt_description(self) -> str:
        """Convert to detailed prompt description"""
        appearance = ", ".join([f"{k}: {v}" for k, v in self.detailed_appearance.items()])
        return f"{self.name} ({appearance})"
    
    def get_consistency_hash(self) -> str:
        """Generate hash for consistency tracking"""
        data = f"{self.name}{self.description}{str(self.detailed_appearance)}"
        return hashlib.md5(data.encode()).hexdigest()[:8]


class CharacterConsistencyManager:
    """Manages consistent characters across multiple video generations"""
    
    def __init__(self, profiles_dir: str = "character_profiles"):
        self.profiles_dir = profiles_dir
        os.makedirs(profiles_dir, exist_ok=True)
        self.profiles: Dict[str, CharacterProfile] = {}
        self._load_profiles()
    
    def _load_profiles(self):
        """Load saved character profiles"""
        for filename in os.listdir(self.profiles_dir):
            if filename.endswith(".json"):
                with open(os.path.join(self.profiles_dir, filename), "r") as f:
                    data = json.load(f)
                    profile = CharacterProfile(**data)
                    self.profiles[profile.name] = profile
    
    def create_news_anchors(self):
        """Create the standard news anchor profiles"""
        
        # Sarah Chen profile
        sarah = CharacterProfile(
            name="Sarah Chen",
            description="Professional female news anchor",
            detailed_appearance={
                "ethnicity": "Asian (Chinese-American)",
                "age": "35 years old",
                "hair": "shoulder-length straight black hair, professional style",
                "face_shape": "oval face with high cheekbones",
                "eyes": "dark brown almond-shaped eyes",
                "complexion": "light tan skin tone",
                "attire": "navy blue blazer over white blouse",
                "makeup": "subtle professional makeup, nude lipstick",
                "accessories": "small pearl earrings",
                "expression": "confident and approachable",
                "posture": "upright, professional"
            },
            reference_images=[],
            voice_profile="en-US-News-F",
            personality_traits=["professional", "articulate", "empathetic", "authoritative"]
        )
        
        # Michael Roberts profile
        michael = CharacterProfile(
            name="Michael Roberts",
            description="Professional male news anchor",
            detailed_appearance={
                "ethnicity": "Caucasian (American)",
                "age": "40 years old",
                "hair": "short brown hair, neatly styled with slight gray at temples",
                "face_shape": "square jaw, strong features",
                "eyes": "blue eyes",
                "complexion": "fair skin with slight tan",
                "attire": "charcoal gray suit with light blue tie",
                "facial_hair": "clean-shaven",
                "accessories": "silver watch, American flag pin",
                "expression": "serious but approachable",
                "posture": "confident, shoulders back"
            },
            reference_images=[],
            voice_profile="en-US-News-M",
            personality_traits=["authoritative", "measured", "trustworthy", "analytical"]
        )
        
        self.save_profile(sarah)
        self.save_profile(michael)
        
        return sarah, michael
    
    def save_profile(self, profile: CharacterProfile):
        """Save a character profile"""
        self.profiles[profile.name] = profile
        
        filepath = os.path.join(self.profiles_dir, f"{profile.name.lower().replace(' ', '_')}.json")
        with open(filepath, "w") as f:
            json.dump(profile.__dict__, f, indent=2)
    
    def get_profile(self, name: str) -> Optional[CharacterProfile]:
        """Get a character profile by name"""
        return self.profiles.get(name)
    
    def generate_consistent_prompt(self, profiles: List[str], scene_description: str) -> str:
        """Generate a prompt that maintains character consistency"""
        
        character_descriptions = []
        for profile_name in profiles:
            profile = self.get_profile(profile_name)
            if profile:
                detailed = profile.to_prompt_description()
                character_descriptions.append(f"- {detailed}")
        
        prompt = f"""
CONSISTENT CHARACTER GENERATION - MUST MATCH EXACTLY:

Characters in scene:
{chr(10).join(character_descriptions)}

CRITICAL: These characters must appear EXACTLY as described above in every frame.
Maintain identical appearance throughout the video.

Scene: {scene_description}
"""
        return prompt
    
    def get_episode_prompt(self, episode_num: int, content: str) -> str:
        """Generate episode-specific prompt with character consistency"""
        
        base_prompt = self.generate_consistent_prompt(
            ["Sarah Chen", "Michael Roberts"],
            "Professional news studio with glass desk and world map video wall"
        )
        
        if episode_num > 1:
            base_prompt += "\nIMPORTANT: These are the SAME anchors from the previous episode. Maintain exact appearance."
        
        return f"{base_prompt}\n\nEpisode {episode_num} Content: {content}"


# Example usage
if __name__ == "__main__":
    manager = CharacterConsistencyManager()
    
    # Create anchor profiles
    sarah, michael = manager.create_news_anchors()
    
    print(f"Created profiles for: {sarah.name} and {michael.name}")
    print(f"\nSarah's consistency hash: {sarah.get_consistency_hash()}")
    print(f"Michael's consistency hash: {michael.get_consistency_hash()}")
    
    # Generate consistent prompt
    ep1_prompt = manager.get_episode_prompt(1, "Breaking news about water crisis")
    print(f"\nEpisode 1 prompt preview:\n{ep1_prompt[:300]}...")
    
    ep2_prompt = manager.get_episode_prompt(2, "Protests coverage")
    print(f"\nEpisode 2 prompt preview:\n{ep2_prompt[:300]}...")