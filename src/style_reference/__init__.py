"""
Style Reference System
Extract, save, and apply visual styles from reference videos/images
"""

from .models.style_reference import StyleReference
from .models.style_attributes import (
    ReferenceType, ColorPalette, Typography, Composition,
    MotionStyle, VisualEffect, LogoPlacement, Watermark, LowerThirds
)
from .analyzers.video_style_analyzer import VideoStyleAnalyzer
from .managers.style_library import StyleLibrary
from .generators.style_prompt_builder import StylePromptBuilder

__all__ = [
    'StyleReference',
    'ReferenceType',
    'ColorPalette',
    'Typography',
    'Composition',
    'MotionStyle',
    'VisualEffect',
    'LogoPlacement',
    'Watermark',
    'LowerThirds',
    'VideoStyleAnalyzer',
    'StyleLibrary',
    'StylePromptBuilder'
]