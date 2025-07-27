"""
University Theme Preset
Academic theme with university branding and educational focus
"""
from datetime import datetime
import os

from ..models.theme import (
    Theme, ThemeCategory, TransitionStyle, VideoTemplate,
    LogoConfiguration, LowerThirdsStyle, CaptionStyle, BrandKit
)
from ...style_reference.models.style_attributes import (
    ColorPalette, Typography, Composition, MotionStyle, VisualEffect
)
from ...style_reference.models.style_reference import StyleReference, ReferenceType


class UniversityTheme(Theme):
    """Academic university theme with educational focus"""
    
    def __init__(self):
        # Create university-style color palette
        university_colors = ColorPalette(
            primary_color="#1E3A8A",  # Deep blue (academic)
            secondary_color="#F59E0B",  # Gold/amber (achievement)
            accent_color="#10B981",  # Green (growth/learning)
            background_colors=["#F3F4F6", "#E5E7EB"],  # Light gray backgrounds
            text_colors=["#1F2937", "#374151"],  # Dark gray text
            saturation_level=0.7,
            brightness_level=0.8,
            contrast_ratio=0.85,
            mood="academic"
        )
        
        # Academic typography
        university_typography = Typography(
            primary_font_family="Georgia",
            secondary_font_family="Arial",
            title_size_ratio=0.07,
            body_size_ratio=0.04,
            font_weight="normal",
            letter_spacing=1.0,
            line_height=1.6,
            has_shadow=True,
            has_outline=False,
            text_animation_style="fade"
        )
        
        # Academic composition
        university_composition = Composition(
            rule_of_thirds_adherence=0.85,
            visual_balance="centered",
            depth_layer_count=3,
            focal_point_strength=0.8,
            negative_space_ratio=0.3,
            symmetry_level=0.7,
            grid_system="golden_ratio"
        )
        
        # Smooth academic transitions
        university_motion = MotionStyle(
            pace="moderate",
            transition_type="smooth",
            camera_movement="steady",
            cut_frequency=0.3,
            motion_blur_intensity=0.1,
            animation_easing="ease-in-out",
            energy_level=0.5
        )
        
        # Professional effects
        university_effects = VisualEffect(
            filter_type="clean",
            color_grading="warm",
            vignette_intensity=0.2,
            grain_amount=0.0,
            glow_intensity=0.3,
            blur_amount=0.0,
            stylization_level=0.3
        )
        
        # Create university style reference
        university_style = StyleReference(
            template_id="preset_university",
            name="University Academic Style",
            description="Professional academic theme for educational content",
            style_family="educational",
            reference_type=ReferenceType.TEMPLATE,
            style_attributes={
                "colors": university_colors,
                "typography": university_typography,
                "composition": university_composition,
                "motion": university_motion,
                "effects": university_effects
            }
        )
        
        # Logo configuration for university branding
        logo_config = LogoConfiguration(
            primary_logo_path="/Users/yahavzamari/viralAi/ai_university_logo.png",
            secondary_logo_path=None,
            position="top-right",
            size_percentage=12,  # 12% of screen width
            opacity=0.9,
            animation_type="fade_in",
            display_duration="constant",  # Always visible
            padding_percentage=2.5
        )
        
        # Lower thirds for educational content
        lower_thirds = LowerThirdsStyle(
            background_color="#1E3A8A",
            background_opacity=0.85,
            text_color="#FFFFFF",
            font_family="Arial",
            font_size_percentage=4.5,
            position="bottom",
            animation_in="slide_up",
            animation_out="fade",
            display_duration=5.0,
            height_percentage=12
        )
        
        # Caption style for educational clarity
        captions = CaptionStyle(
            font_family="Arial",
            font_size_percentage=3.5,
            text_color="#FFFFFF",
            background_color="#000000",
            background_opacity=0.7,
            position="bottom-center",
            max_width_percentage=80,
            padding_percentage=1.5,
            animation_style="fade"
        )
        
        # Brand kit for consistency
        brand_kit = BrandKit(
            brand_name="AI University",
            primary_colors=["#1E3A8A", "#F59E0B"],
            secondary_colors=["#10B981", "#6366F1"],
            fonts=["Georgia", "Arial"],
            logo_urls=["/Users/yahavzamari/viralAi/ai_university_logo.png"],
            tagline="Learn. Create. Innovate.",
            tone_of_voice="educational, inspiring, accessible"
        )
        
        # Create video template
        template = VideoTemplate(
            template_id="university_educational",
            name="University Educational Template",
            description="Professional template for educational content",
            category=ThemeCategory.EDUCATION,
            duration_range=(30, 300),
            aspect_ratios=["16:9", "9:16", "1:1"],
            platform_optimizations=["youtube", "instagram", "tiktok"],
            includes_intro=True,
            includes_outro=True,
            includes_lower_thirds=True,
            includes_captions=True,
            music_style="uplifting_instrumental",
            transition_style=TransitionStyle.SMOOTH_FADE
        )
        
        # Initialize the theme
        super().__init__(
            theme_id="preset_university",
            name="University Academic Theme",
            description="Professional academic theme for educational content with university branding",
            category=ThemeCategory.EDUCATION,
            style_references=[university_style],
            color_palettes=[university_colors],
            typography_sets=[university_typography],
            templates=[template],
            logo_config=logo_config,
            lower_thirds_style=lower_thirds,
            caption_style=captions,
            brand_kit=brand_kit,
            is_premium=False,
            created_by="system",
            version="1.0.0",
            tags=["education", "university", "academic", "professional", "learning"],
            preview_url="/themes/university/preview.mp4",
            thumbnail_url="/themes/university/thumbnail.png"
        )
        
        # Add educational-specific metadata
        self.metadata = {
            "subject_areas": ["mathematics", "science", "engineering", "technology"],
            "target_audience": ["students", "educators", "lifelong learners"],
            "content_types": ["lectures", "tutorials", "demonstrations", "explanations"],
            "branding_elements": {
                "logo_overlay": True,
                "watermark": False,
                "intro_animation": True,
                "outro_animation": True
            }
        }