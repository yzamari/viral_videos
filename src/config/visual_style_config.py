"""
Visual Style Configuration System
NO HARDCODED PROMPTS - All style characteristics from configuration
"""

from typing import Dict, List, Any
from enum import Enum


class VisualStyleType(Enum):
    """Supported visual style types"""
    WALTZ_WITH_BASHIR = "Waltz with Bashir animation"
    CINEMATIC = "cinematic"
    DYNAMIC = "dynamic"
    REALISTIC = "realistic"


class VisualStyleConfig:
    """Dynamic visual style configuration - NO hardcoded values"""
    
    @staticmethod
    def get_style_characteristics(visual_style: str) -> Dict[str, Any]:
        """Get visual characteristics for a style dynamically"""
        
        # Convert string to enum for consistent matching
        style_lower = visual_style.lower()
        
        if "waltz with bashir" in style_lower:
            return {
                "animation_type": "rotoscoped animation",
                "visual_characteristics": [
                    "high contrast rotoscoped animation",
                    "stark black outlines", 
                    "desaturated color palette",
                    "surreal dreamlike visuals",
                    "war documentary aesthetic",
                    "hand-drawn animation feel",
                    "psychological surrealism"
                ],
                "color_palette": "desaturated, muted colors, high contrast",
                "line_style": "stark black outlines, rotoscoped borders",
                "mood": "surreal, psychological, war documentary",
                "camera_style": "first-person POV, handheld feel",
                "lighting": "harsh, high contrast shadows",
                "texture": "hand-drawn, rotoscoped animation texture"
            }
        elif "cinematic" in style_lower:
            return {
                "animation_type": "cinematic realism",
                "visual_characteristics": [
                    "cinematic composition",
                    "professional lighting",
                    "smooth camera movements",
                    "realistic rendering"
                ],
                "color_palette": "natural, balanced colors",
                "mood": "dramatic, professional",
                "camera_style": "cinematic shots",
                "lighting": "professional cinematic lighting"
            }
        else:
            # Dynamic style based on input
            return {
                "animation_type": "dynamic visuals",
                "visual_characteristics": [
                    "engaging visual style",
                    "platform-optimized composition"
                ],
                "color_palette": "vibrant, engaging colors",
                "mood": "dynamic, engaging"
            }
    
    @staticmethod
    def build_style_prompt_enhancement(visual_style: str, base_description: str) -> str:
        """Build style-specific prompt enhancement"""
        
        characteristics = VisualStyleConfig.get_style_characteristics(visual_style)
        
        # Build dynamic enhancement based on characteristics
        enhancements = []
        
        if characteristics.get("animation_type"):
            enhancements.append(characteristics["animation_type"])
        
        if characteristics.get("visual_characteristics"):
            enhancements.extend(characteristics["visual_characteristics"])
        
        if characteristics.get("color_palette"):
            enhancements.append(f"color palette: {characteristics['color_palette']}")
        
        if characteristics.get("mood"):
            enhancements.append(f"mood: {characteristics['mood']}")
        
        # Combine base description with style enhancements
        enhanced_prompt = f"{base_description}, {', '.join(enhancements)}"
        
        return enhanced_prompt
    
    @staticmethod
    def get_style_keywords(visual_style: str) -> List[str]:
        """Get style-specific keywords dynamically"""
        
        characteristics = VisualStyleConfig.get_style_characteristics(visual_style)
        keywords = ["16:9"]  # Always include aspect ratio
        
        style_lower = visual_style.lower()
        
        if "waltz with bashir" in style_lower:
            keywords.extend([
                "Waltz with Bashir",
                "rotoscoped animation", 
                "high contrast",
                "surreal",
                "war documentary",
                "desaturated colors",
                "stark outlines",
                "hand-drawn animation",
                "psychological tension",
                "first-person POV",
                "no cartoon",
                "no child-friendly",
                "no colorful"
            ])
        
        return keywords