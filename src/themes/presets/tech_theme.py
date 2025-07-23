"""
Tech Theme Preset
Modern technology theme with futuristic elements
"""
from datetime import datetime

from ..models.theme import (
    Theme, ThemeCategory, TransitionStyle, VideoTemplate,
    LogoConfiguration, LowerThirdsStyle, CaptionStyle, BrandKit
)
from ...style_reference.models.style_attributes import (
    ColorPalette, Typography, Composition, MotionStyle, VisualEffect
)
from ...style_reference.models.style_reference import StyleReference, ReferenceType


class TechTheme(Theme):
    """Modern technology theme"""
    
    def __init__(self):
        # Create tech-style color palette
        tech_colors = ColorPalette(
            primary_color="#00D4FF",  # Cyan
            secondary_color="#1A1A2E",  # Dark blue
            accent_color="#FF006E",  # Magenta accent
            background_colors=["#0F0F1E", "#16213E"],
            text_colors=["#FFFFFF", "#00D4FF"],
            saturation_level=0.85,
            brightness_level=0.6,
            contrast_ratio=0.9,
            mood="futuristic"
        )
        
        # Tech typography
        tech_typography = Typography(
            primary_font_family="Roboto",
            secondary_font_family="Source Code Pro",
            title_size_ratio=0.08,
            body_size_ratio=0.045,
            font_weight="light",
            letter_spacing=1.5,
            line_height=1.4,
            has_shadow=False,
            has_outline=False,
            text_animation_style="glitch"
        )
        
        # Tech composition
        tech_composition = Composition(
            rule_of_thirds_adherence=0.9,
            symmetry_score=0.85,
            primary_layout="grid-based",
            text_placement_zones=["lower-third", "side-panel"],
            margin_ratio=0.06,
            padding_ratio=0.03,
            focal_point_strategy="geometric-center",
            depth_layers=6
        )
        
        # Tech motion style
        tech_motion = MotionStyle(
            camera_movement="smooth-tracking",
            transition_style="digital-glitch",
            average_shot_duration=3.0,
            movement_intensity=0.6,
            text_animation_type="typewriter",
            element_animation_style="fade-slide",
            pacing="moderate",
            rhythm_pattern="electronic"
        )
        
        # Create style reference
        tech_style = StyleReference(
            reference_id="style_tech_preset",
            name="Tech Innovation Style",
            reference_type=ReferenceType.TEMPLATE,
            source_path=None,
            template_id="preset_tech",
            color_palette=tech_colors,
            typography=tech_typography,
            composition=tech_composition,
            motion_style=tech_motion,
            visual_effects=[
                VisualEffect(
                    effect_type="digital-glitch",
                    intensity=0.3,
                    apply_to="full-frame",
                    parameters={"frequency": "intermittent", "color_shift": True}
                ),
                VisualEffect(
                    effect_type="hologram",
                    intensity=0.5,
                    apply_to="text",
                    parameters={"color": "#00D4FF", "scan_lines": True}
                ),
                VisualEffect(
                    effect_type="particle-effects",
                    intensity=0.4,
                    apply_to="background",
                    parameters={"particle_type": "digital_dust", "density": 0.3}
                )
            ],
            logo_placement=None,
            watermark=None,
            lower_thirds=None,
            aspect_ratio="16:9",
            resolution="1920x1080",
            frame_rate=30,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags=["tech", "futuristic", "modern", "digital"],
            description="Modern technology visual style with futuristic elements",
            confidence_scores={"preset": 1.0}
        )
        
        # Create brand kit
        tech_brand = BrandKit(
            primary_logo="assets/logos/tech_logo.png",
            primary_logo_dark="assets/logos/tech_logo_dark.png",
            primary_logo_light="assets/logos/tech_logo_light.png",
            color_primary="#00D4FF",
            color_secondary="#1A1A2E",
            color_accent="#FF006E",
            color_background="#0F0F1E",
            color_text_primary="#FFFFFF",
            color_text_secondary="#00D4FF",
            fonts={
                "heading": "Roboto",
                "body": "Source Code Pro",
                "code": "Fira Code"
            },
            minimum_logo_size_percentage=8.0,
            clear_space_ratio=2.0,
            allow_logo_effects=True  # Allow digital effects on logo
        )
        
        # Create intro template
        intro_template = VideoTemplate(
            template_id="tech_intro",
            duration=3.5,
            background_type="video",
            background_content="assets/templates/tech_intro_bg.mp4",
            title_text="INNOVATION UNLEASHED",
            subtitle_text="{TECH_TOPIC}",
            title_animation="digital-reveal",
            music_path="assets/audio/tech_intro.mp3",
            sound_effects=["digital-whoosh", "tech-beep", "glitch"],
            fade_in_duration=0.2,
            fade_out_duration=0.4
        )
        
        # Create outro template
        outro_template = VideoTemplate(
            template_id="tech_outro",
            duration=3.0,
            background_type="gradient",
            background_content="#0F0F1E,#00D4FF",
            title_text="THE FUTURE IS NOW",
            subtitle_text="SUBSCRIBE FOR MORE TECH",
            title_animation="glitch-fade",
            music_path="assets/audio/tech_outro.mp3",
            sound_effects=["power-down", "digital-chime"],
            fade_in_duration=0.3,
            fade_out_duration=0.6
        )
        
        # Logo configuration
        logo_config = LogoConfiguration(
            logo_path="assets/logos/tech_logo.png",
            position="bottom-right",
            size_percentage=9.0,
            opacity=0.85,
            always_visible=True,
            margin_percentage=3.0,
            entrance_animation="digital-materialize",
            exit_animation="digital-dissolve"
        )
        
        # Lower thirds style (tech interface)
        lower_thirds = LowerThirdsStyle(
            enabled=True,
            background_type="blur",
            background_color_primary="#00D4FF",
            background_color_secondary="#1A1A2E",
            background_opacity=0.75,
            title_font_size_ratio=0.06,
            subtitle_font_size_ratio=0.04,
            title_color="#FFFFFF",
            subtitle_color="#00D4FF",
            entrance_animation="digital-slide",
            exit_animation="digital-slide",
            animation_duration=0.4,
            position_y_percentage=78.0,
            height_percentage=12.0,
            margin_x_percentage=4.0
        )
        
        # Caption style
        captions = CaptionStyle(
            font_family="Source Code Pro",
            font_size_ratio=0.04,
            font_color="#00D4FF",
            font_weight="regular",
            background_enabled=True,
            background_color="#0F0F1E",
            background_opacity=0.9,
            background_padding=12.0,
            shadow_enabled=False,  # Clean tech look
            position_y_percentage=85.0,
            max_width_percentage=80.0
        )
        
        # Initialize theme
        super().__init__(
            theme_id="preset_tech",
            name="Tech Innovation",
            category=ThemeCategory.TECH,
            version="1.0.0",
            style_reference=tech_style,
            brand_kit=tech_brand,
            intro_template=intro_template,
            outro_template=outro_template,
            transition_style=TransitionStyle.DISSOLVE,
            transition_duration=0.4,
            logo_config=logo_config,
            lower_thirds_style=lower_thirds,
            caption_style=captions,
            intro_music="assets/audio/tech_intro.mp3",
            outro_music="assets/audio/tech_outro.mp3",
            background_music_style="electronic-ambient",
            sound_effects_pack="tech-digital",
            content_tone="innovative",
            content_style="educational",
            target_audience="tech-enthusiasts",
            default_duration=120,
            default_aspect_ratio="16:9",
            default_resolution="1920x1080",
            default_frame_rate=30,
            description="Modern technology theme with futuristic elements and digital effects",
            tags=["tech", "futuristic", "innovation", "digital", "modern"],
            created_by="system"
        )