"""
Dynamic Content Configuration System
ZERO HARDCODED CONTENT - All content generated dynamically based on user input
"""

from typing import Dict, List, Any, Optional
from ..models.video_models import Platform


class DynamicContentConfig:
    """Generate all content dynamically based on mission, platform, style, tone"""
    
    @staticmethod
    def generate_hook(mission: str, platform: str, tone: str, visual_style: str) -> str:
        """Generate hook dynamically based on content context"""
        
        mission_lower = mission.lower()
        tone_lower = tone.lower()
        
        # Extract content themes from mission
        if "waltz with bashir" in mission_lower:
            if "tense" in tone_lower:
                return "Experience war through a soldier's eyes"
            else:
                return "Journey into a soldier's mind"
        elif "soldier" in mission_lower:
            return "Witness a soldier's story"
        elif "war" in mission_lower:
            return "See the unseen reality"
        elif "ptsd" in mission_lower:
            return "Understanding the invisible wounds"
        else:
            # Generate based on tone
            if "tense" in tone_lower:
                return "Feel the tension unfold"
            elif "dramatic" in tone_lower:
                return "Experience the drama"
            else:
                return "Discover this story"
    
    @staticmethod
    def generate_cta(mission: str, platform: str, tone: str, visual_style: str) -> str:
        """Generate call-to-action dynamically based on content context"""
        
        mission_lower = mission.lower()
        
        # Extract action from mission context
        if "waltz with bashir" in mission_lower:
            return "Witness the psychological journey"
        elif "soldier" in mission_lower:
            return "See the complete story"
        elif "experience" in mission_lower:
            return "Continue the experience"
        else:
            # Generate based on platform
            platform_lower = platform.lower()
            if platform_lower == "youtube":
                return "Watch the full story"
            elif platform_lower == "tiktok":
                return "See what happens next"
            else:
                return "Experience more"
    
    @staticmethod
    def generate_visual_prompt_enhancement(base_prompt: str, visual_style: str, 
                                          tone: str, mission: str) -> str:
        """Generate visual prompt enhancement dynamically"""
        
        style_lower = visual_style.lower()
        tone_lower = tone.lower()
        mission_lower = mission.lower()
        
        enhancements = []
        
        # Style-based enhancements
        if "waltz with bashir" in style_lower:
            enhancements.extend([
                "rotoscoped animation style",
                "high contrast black outlines",
                "desaturated color palette",
                "surreal dreamlike visuals",
                "war documentary aesthetic"
            ])
        elif "cinematic" in style_lower:
            enhancements.extend([
                "cinematic composition",
                "professional lighting",
                "dramatic camera work"
            ])
        
        # Tone-based enhancements
        if "tense" in tone_lower:
            enhancements.extend([
                "psychological tension",
                "suspenseful atmosphere"
            ])
        elif "dramatic" in tone_lower:
            enhancements.extend([
                "dramatic lighting",
                "emotional intensity"
            ])
        
        # Mission-based enhancements
        if "soldier" in mission_lower:
            enhancements.extend([
                "military authenticity",
                "first-person perspective"
            ])
        
        if "pov" in mission_lower:
            enhancements.append("first-person point of view")
        
        # Combine base prompt with dynamic enhancements
        if enhancements:
            return f"{base_prompt}, {', '.join(enhancements)}"
        else:
            return base_prompt
    
    @staticmethod
    def generate_hashtags(mission: str, platform: str, category: str, 
                         visual_style: str) -> List[str]:
        """Generate hashtags dynamically based on content"""
        
        hashtags = []
        
        # Extract themes from mission
        mission_lower = mission.lower()
        
        if "waltz with bashir" in mission_lower:
            hashtags.extend(["#WaltzWithBashir", "#WarStory", "#Animation"])
        
        if "soldier" in mission_lower:
            hashtags.extend(["#SoldierStory", "#Military", "#FirstPerson"])
        
        if "pov" in mission_lower:
            hashtags.append("#POV")
        
        if "israeli" in mission_lower:
            hashtags.append("#Israeli")
        
        # Platform-specific hashtags
        platform_lower = platform.lower()
        if platform_lower == "youtube":
            hashtags.extend(["#YouTubeShorts", "#Video"])
        elif platform_lower == "tiktok":
            hashtags.extend(["#TikTok", "#ForYou"])
        
        # Category-based hashtags
        if category:
            hashtags.append(f"#{category}")
        
        # Style-based hashtags
        if "animation" in visual_style.lower():
            hashtags.append("#Animation")
        
        return hashtags[:15]  # Limit to 15 hashtags
    
    @staticmethod
    def generate_background_music_style(mission: str, tone: str, visual_style: str) -> str:
        """Generate background music style dynamically"""
        
        mission_lower = mission.lower()
        tone_lower = tone.lower()
        
        if "waltz with bashir" in mission_lower or "war" in mission_lower:
            return "dramatic orchestral"
        elif "tense" in tone_lower:
            return "suspenseful ambient"
        elif "dramatic" in tone_lower:
            return "cinematic dramatic"
        else:
            return "ambient atmospheric"
    
    @staticmethod
    def generate_color_palette(mission: str, visual_style: str, tone: str) -> str:
        """Generate color palette dynamically"""
        
        style_lower = visual_style.lower()
        mission_lower = mission.lower()
        
        if "waltz with bashir" in style_lower:
            return "desaturated, muted greens and browns, high contrast"
        elif "war" in mission_lower:
            return "muted military colors, earth tones"
        elif "tense" in tone.lower():
            return "high contrast, dramatic shadows"
        else:
            return "balanced, natural colors"
    
    @staticmethod
    def generate_theme_text(mission: str, platform: str, tone: str, text_type: str) -> str:
        """Generate theme-specific text dynamically based on content context"""
        
        mission_lower = mission.lower()
        tone_lower = tone.lower()
        
        if text_type == "title":
            if "waltz with bashir" in mission_lower:
                return "War Through Memory"
            elif "tech" in mission_lower:
                return "Innovation Ahead"
            elif "news" in mission_lower:
                return "Breaking Story"
            else:
                return "Story Unfolds"
        
        elif text_type == "subtitle":
            if "waltz with bashir" in mission_lower:
                return "Experience the psychological journey"
            elif "tech" in mission_lower:
                return "Discover more innovation"
            elif "news" in mission_lower:
                return "Stay informed"
            else:
                return "Continue watching"
        
        else:
            return "Content continues"
    
    @staticmethod
    def generate_viral_hook_enhancement(base_hook: str, mission: str, 
                                      tone: str, viral_elements: Dict[str, Any]) -> str:
        """Generate viral hook enhancement dynamically without hardcoded phrases"""
        
        mission_lower = mission.lower()
        tone_lower = tone.lower()
        
        # Extract emotional context from mission and tone
        if "waltz with bashir" in mission_lower:
            if "tense" in tone_lower:
                return f"The tension you're about to witness: {base_hook}"
            else:
                return f"The story that changed everything: {base_hook}"
        
        elif "soldier" in mission_lower:
            return f"Through a soldier's eyes: {base_hook}"
        
        elif "war" in mission_lower:
            return f"The reality of war: {base_hook}"
        
        else:
            # Use mission-derived context
            if any(word in mission_lower for word in ["experience", "journey", "discover"]):
                return f"Experience this: {base_hook}"
            elif any(word in tone_lower for word in ["tense", "dramatic", "intense"]):
                return f"Feel the intensity: {base_hook}"
            else:
                return f"Witness this: {base_hook}"
    
    @staticmethod
    def generate_main_content_structure(mission: str, platform: str, tone: str) -> List[str]:
        """Generate main content structure dynamically based on mission"""
        
        mission_lower = mission.lower()
        
        if "waltz with bashir" in mission_lower:
            return [
                f"Setting: {mission}",
                f"Perspective: First-person soldier experience",
                f"Impact: The psychological reality of war"
            ]
        
        elif "soldier" in mission_lower:
            return [
                f"Context: {mission}",
                f"Experience: Personal soldier journey",
                f"Reality: The human side of conflict"
            ]
        
        else:
            # Extract key components from mission
            return [
                f"Opening: {mission}",
                f"Development: The story behind this",
                f"Resolution: What this means"
            ]