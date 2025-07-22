"""
Style Prompt Builder
Builds enhanced prompts incorporating style reference attributes
"""
from typing import Dict, List, Optional
import logging

from ..models.style_reference import StyleReference
from ..models.style_attributes import VisualEffect

logger = logging.getLogger(__name__)


class StylePromptBuilder:
    """Builds prompts that incorporate style reference attributes"""
    
    def __init__(self):
        """Initialize prompt builder"""
        self.style_weight = 0.7  # How much to emphasize style (0-1)
    
    def enhance_prompt_with_style(self, base_prompt: str, 
                                 style_ref: StyleReference) -> str:
        """Enhance a base prompt with style attributes
        
        Args:
            base_prompt: Original prompt describing content
            style_ref: Style reference to apply
            
        Returns:
            Enhanced prompt with style attributes
        """
        logger.info(f"🎨 Enhancing prompt with style: {style_ref.name}")
        
        # Build style components
        style_components = []
        
        # Visual style
        visual_style = self._build_visual_style(style_ref)
        if visual_style:
            style_components.append(visual_style)
        
        # Color style
        color_style = self._build_color_style(style_ref)
        if color_style:
            style_components.append(color_style)
        
        # Composition style
        comp_style = self._build_composition_style(style_ref)
        if comp_style:
            style_components.append(comp_style)
        
        # Motion style
        motion_style = self._build_motion_style(style_ref)
        if motion_style:
            style_components.append(motion_style)
        
        # Effects
        effects_style = self._build_effects_style(style_ref)
        if effects_style:
            style_components.append(effects_style)
        
        # Technical specs
        tech_style = self._build_technical_style(style_ref)
        if tech_style:
            style_components.append(tech_style)
        
        # Combine all style elements
        style_description = ", ".join(style_components)
        
        # Build enhanced prompt
        if self.style_weight >= 0.9:
            # Style-first prompt
            enhanced = f"{style_description}. {base_prompt}"
        elif self.style_weight >= 0.5:
            # Balanced prompt
            enhanced = f"{base_prompt}, {style_description}"
        else:
            # Content-first prompt
            enhanced = f"{base_prompt}. Style: {style_description}"
        
        # Add no text overlays if not specified
        if "no text overlays" not in enhanced.lower():
            enhanced += ", no text overlays"
        
        logger.info(f"✅ Enhanced prompt: {enhanced[:100]}...")
        return enhanced
    
    def _build_visual_style(self, style_ref: StyleReference) -> str:
        """Build visual style description"""
        components = []
        
        # Overall mood from color palette
        if style_ref.color_palette.mood:
            components.append(f"{style_ref.color_palette.mood} visual style")
        
        # Brightness/contrast
        if style_ref.color_palette.brightness_level > 0.7:
            components.append("bright and vivid")
        elif style_ref.color_palette.brightness_level < 0.3:
            components.append("dark and moody")
        
        if style_ref.color_palette.contrast_ratio > 0.7:
            components.append("high contrast")
        elif style_ref.color_palette.contrast_ratio < 0.3:
            components.append("low contrast")
        
        return ", ".join(components)
    
    def _build_color_style(self, style_ref: StyleReference) -> str:
        """Build color palette description"""
        components = []
        
        # Primary colors
        palette = style_ref.color_palette
        
        # Color temperature
        if palette.mood in ["warm", "cool"]:
            components.append(f"{palette.mood} color temperature")
        
        # Saturation
        if palette.saturation_level > 0.7:
            components.append("highly saturated colors")
        elif palette.saturation_level < 0.3:
            components.append("desaturated colors")
        
        # Specific color hints (simplified for VEO)
        if self._is_color_dominant(palette.primary_color, "blue"):
            components.append("blue tones")
        elif self._is_color_dominant(palette.primary_color, "orange"):
            components.append("orange/warm tones")
        elif self._is_color_dominant(palette.primary_color, "green"):
            components.append("green/natural tones")
        
        return ", ".join(components)
    
    def _build_composition_style(self, style_ref: StyleReference) -> str:
        """Build composition description"""
        components = []
        
        comp = style_ref.composition
        
        # Layout
        if comp.primary_layout:
            components.append(f"{comp.primary_layout} composition")
        
        # Symmetry
        if comp.symmetry_score > 0.7:
            components.append("symmetrical framing")
        
        # Depth
        if comp.depth_layers > 3:
            components.append("deep layered composition")
        
        return ", ".join(components)
    
    def _build_motion_style(self, style_ref: StyleReference) -> str:
        """Build motion description"""
        components = []
        
        motion = style_ref.motion_style
        
        # Camera movement
        if motion.camera_movement:
            components.append(f"{motion.camera_movement} camera movement")
        
        # Pacing
        if motion.pacing:
            components.append(f"{motion.pacing} paced")
        
        # Shot duration hint
        if motion.average_shot_duration < 2:
            components.append("quick cuts")
        elif motion.average_shot_duration > 5:
            components.append("long takes")
        
        return ", ".join(components)
    
    def _build_effects_style(self, style_ref: StyleReference) -> str:
        """Build effects description"""
        components = []
        
        # Only include prominent effects
        for effect in style_ref.visual_effects:
            if effect.intensity > 0.5:
                if effect.effect_type == "blur":
                    components.append("shallow depth of field")
                elif effect.effect_type == "grain":
                    components.append("film grain texture")
                elif effect.effect_type == "glow":
                    components.append("soft glow lighting")
        
        return ", ".join(components)
    
    def _build_technical_style(self, style_ref: StyleReference) -> str:
        """Build technical specifications"""
        components = []
        
        # Aspect ratio
        if style_ref.aspect_ratio:
            if style_ref.aspect_ratio == "21:9":
                components.append("cinematic widescreen")
            elif style_ref.aspect_ratio == "1:1":
                components.append("square format")
            elif style_ref.aspect_ratio == "9:16":
                components.append("vertical format")
        
        # Frame rate hints
        if style_ref.frame_rate >= 60:
            components.append("smooth high framerate")
        elif style_ref.frame_rate <= 24:
            components.append("cinematic framerate")
        
        return ", ".join(components)
    
    def _is_color_dominant(self, hex_color: str, color_name: str) -> bool:
        """Check if a color is dominant in hex color"""
        # Simple color detection
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        if color_name == "blue":
            return b > r and b > g
        elif color_name == "orange":
            return r > g and r > b and g > b
        elif color_name == "green":
            return g > r and g > b
        
        return False
    
    def create_style_comparison_prompt(self, content: str, 
                                     style_ref: StyleReference) -> str:
        """Create a prompt that explicitly references a style
        
        Args:
            content: Content description
            style_ref: Style to match
            
        Returns:
            Prompt that references the style
        """
        prompt = f"Create a video about {content} "
        prompt += f"in the exact visual style of {style_ref.name}: "
        prompt += f"{style_ref.to_prompt_modifiers()}"
        
        # Add specific style attributes
        if style_ref.color_palette.mood:
            prompt += f", maintaining {style_ref.color_palette.mood} color mood"
        
        if style_ref.motion_style.pacing:
            prompt += f", with {style_ref.motion_style.pacing} pacing"
        
        prompt += ", no text overlays"
        
        return prompt