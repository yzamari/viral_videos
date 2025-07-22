"""
Style Reference Model
Main model for representing a complete style reference
"""
from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime

from .style_attributes import (
    ReferenceType, ColorPalette, Typography, Composition,
    MotionStyle, VisualEffect, LogoPlacement, Watermark, LowerThirds
)


@dataclass
class StyleReference:
    """Represents a complete style reference from video/image"""
    # Identification
    reference_id: str
    name: str
    reference_type: ReferenceType
    source_path: Optional[str]
    template_id: Optional[str]
    
    # Visual attributes
    color_palette: ColorPalette
    typography: Typography
    composition: Composition
    motion_style: MotionStyle
    visual_effects: List[VisualEffect]
    
    # Brand elements
    logo_placement: Optional[LogoPlacement]
    watermark: Optional[Watermark]
    lower_thirds: Optional[LowerThirds]
    
    # Technical details
    aspect_ratio: str  # e.g., "16:9", "9:16", "1:1"
    resolution: str  # e.g., "1920x1080", "4K"
    frame_rate: int  # e.g., 30, 60
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    tags: List[str]
    description: Optional[str]
    
    # Analysis confidence
    confidence_scores: Dict[str, float]  # Confidence for each analyzed aspect
    
    def to_prompt_modifiers(self) -> str:
        """Convert style reference to prompt modifiers for video generation"""
        modifiers = []
        
        # Color mood
        if self.color_palette.mood:
            modifiers.append(f"{self.color_palette.mood} color palette")
        
        # Composition style
        if self.composition.primary_layout:
            modifiers.append(f"{self.composition.primary_layout} composition")
        
        # Motion characteristics
        if self.motion_style.camera_movement:
            modifiers.append(f"{self.motion_style.camera_movement} camera movement")
        
        # Pacing
        if self.motion_style.pacing:
            modifiers.append(f"{self.motion_style.pacing} paced")
        
        # Visual effects
        for effect in self.visual_effects[:3]:  # Limit to top 3 effects
            if effect.intensity > 0.5:
                modifiers.append(f"{effect.effect_type} effect")
        
        return ", ".join(modifiers)
    
    def to_technical_specs(self) -> Dict[str, any]:
        """Extract technical specifications for video generation"""
        return {
            "aspect_ratio": self.aspect_ratio,
            "resolution": self.resolution,
            "frame_rate": self.frame_rate,
            "average_shot_duration": self.motion_style.average_shot_duration,
            "transition_style": self.motion_style.transition_style
        }
    
    def similarity_score(self, other: 'StyleReference') -> float:
        """Calculate similarity score with another style reference"""
        scores = []
        
        # Color similarity
        color_score = self._compare_colors(other.color_palette)
        scores.append(color_score * 0.3)  # 30% weight
        
        # Composition similarity
        comp_score = abs(self.composition.rule_of_thirds_adherence - 
                        other.composition.rule_of_thirds_adherence)
        scores.append((1 - comp_score) * 0.2)  # 20% weight
        
        # Motion similarity
        motion_score = 1.0 if self.motion_style.pacing == other.motion_style.pacing else 0.5
        scores.append(motion_score * 0.25)  # 25% weight
        
        # Technical similarity
        tech_score = 1.0 if self.aspect_ratio == other.aspect_ratio else 0.5
        scores.append(tech_score * 0.25)  # 25% weight
        
        return sum(scores)
    
    def _compare_colors(self, other_palette: ColorPalette) -> float:
        """Compare color palettes for similarity"""
        # Simple comparison based on mood and brightness
        mood_match = 1.0 if self.color_palette.mood == other_palette.mood else 0.5
        brightness_diff = abs(self.color_palette.brightness_level - 
                            other_palette.brightness_level)
        brightness_score = 1.0 - brightness_diff
        
        return (mood_match + brightness_score) / 2