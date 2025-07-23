"""
Entertainment Theme Preset
Vibrant entertainment and lifestyle theme
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


class EntertainmentTheme(Theme):
    """Vibrant entertainment theme"""
    
    def __init__(self):
        # Create entertainment-style color palette
        entertainment_colors = ColorPalette(
            primary_color="#FF1493",  # Deep pink
            secondary_color="#FFD700",  # Gold
            accent_color="#9400D3",  # Violet
            background_colors=["#1E0033", "#3D0066"],
            text_colors=["#FFFFFF", "#FFD700"],
            saturation_level=0.95,
            brightness_level=0.75,
            contrast_ratio=0.8,
            mood="vibrant"
        )
        
        # Entertainment typography
        entertainment_typography = Typography(
            primary_font_family="Bebas Neue",
            secondary_font_family="Montserrat",
            title_size_ratio=0.09,
            body_size_ratio=0.05,
            font_weight="bold",
            letter_spacing=1.3,
            line_height=1.3,
            has_shadow=True,
            has_outline=False,
            text_animation_style="pop"
        )
        
        # Entertainment composition
        entertainment_composition = Composition(
            rule_of_thirds_adherence=0.6,
            symmetry_score=0.5,
            primary_layout="center-focused",
            text_placement_zones=["center", "lower-third", "top-banner"],
            margin_ratio=0.04,
            padding_ratio=0.02,
            focal_point_strategy="celebrity-focus",
            depth_layers=7
        )
        
        # Entertainment motion style
        entertainment_motion = MotionStyle(
            camera_movement="smooth-pan",
            transition_style="zoom",
            average_shot_duration=2.0,
            movement_intensity=0.7,
            text_animation_type="pop",
            element_animation_style="sparkle",
            pacing="upbeat",
            rhythm_pattern="music-sync"
        )
        
        # Create style reference
        entertainment_style = StyleReference(
            reference_id="style_entertainment_preset",
            name="Entertainment Style",
            reference_type=ReferenceType.TEMPLATE,
            source_path=None,
            template_id="preset_entertainment",
            color_palette=entertainment_colors,
            typography=entertainment_typography,
            composition=entertainment_composition,
            motion_style=entertainment_motion,
            visual_effects=[
                VisualEffect(
                    effect_type="sparkles",
                    intensity=0.7,
                    apply_to="full-frame",
                    parameters={"density": 0.5, "color": "#FFD700"}
                ),
                VisualEffect(
                    effect_type="lens-flare",
                    intensity=0.5,
                    apply_to="background",
                    parameters={"position": "dynamic", "color": "#FF1493"}
                ),
                VisualEffect(
                    effect_type="glow",
                    intensity=0.6,
                    apply_to="text",
                    parameters={"glow_color": "#FFD700", "radius": 10}
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
            tags=["entertainment", "vibrant", "lifestyle", "celebrity"],
            description="Vibrant entertainment visual style",
            confidence_scores={"preset": 1.0}
        )
        
        # Create brand kit
        entertainment_brand = BrandKit(
            primary_logo="assets/logos/entertainment_logo.png",
            primary_logo_dark="assets/logos/entertainment_logo_dark.png",
            primary_logo_light="assets/logos/entertainment_logo_light.png",
            color_primary="#FF1493",
            color_secondary="#FFD700",
            color_accent="#9400D3",
            color_background="#1E0033",
            color_text_primary="#FFFFFF",
            color_text_secondary="#FFD700",
            fonts={
                "heading": "Bebas Neue",
                "body": "Montserrat",
                "accent": "Pacifico"
            },
            minimum_logo_size_percentage=10.0,
            clear_space_ratio=1.8,
            allow_logo_effects=True
        )
        
        # Create intro template
        intro_template = VideoTemplate(
            template_id="entertainment_intro",
            duration=4.0,
            background_type="video",
            background_content="assets/templates/entertainment_intro_bg.mp4",
            title_text="ENTERTAINMENT TONIGHT",
            subtitle_text="{SHOW_TOPIC}",
            title_animation="sparkle-pop",
            music_path="assets/audio/entertainment_intro.mp3",
            sound_effects=["applause", "sparkle", "whoosh"],
            fade_in_duration=0.3,
            fade_out_duration=0.5
        )
        
        # Create outro template
        outro_template = VideoTemplate(
            template_id="entertainment_outro",
            duration=3.5,
            background_type="video",
            background_content="assets/templates/entertainment_outro_bg.mp4",
            title_text="THANKS FOR WATCHING!",
            subtitle_text="SUBSCRIBE & STAY TUNED",
            title_animation="zoom-sparkle",
            music_path="assets/audio/entertainment_outro.mp3",
            sound_effects=["applause", "chime"],
            fade_in_duration=0.4,
            fade_out_duration=0.7
        )
        
        # Logo configuration
        logo_config = LogoConfiguration(
            logo_path="assets/logos/entertainment_logo.png",
            position="top-center",
            size_percentage=11.0,
            opacity=0.9,
            always_visible=True,
            margin_percentage=2.0,
            entrance_animation="sparkle-fade",
            exit_animation="sparkle-fade"
        )
        
        # Lower thirds style (celebrity style)
        lower_thirds = LowerThirdsStyle(
            enabled=True,
            background_type="gradient",
            background_color_primary="#FF1493",
            background_color_secondary="#9400D3",
            background_opacity=0.85,
            title_font_size_ratio=0.07,
            subtitle_font_size_ratio=0.045,
            title_color="#FFFFFF",
            subtitle_color="#FFD700",
            entrance_animation="pop-slide",
            exit_animation="pop-slide",
            animation_duration=0.35,
            position_y_percentage=77.0,
            height_percentage=14.0,
            margin_x_percentage=3.5
        )
        
        # Caption style
        captions = CaptionStyle(
            font_family="Montserrat",
            font_size_ratio=0.045,
            font_color="#FFFFFF",
            font_weight="semi-bold",
            background_enabled=True,
            background_color="#FF1493",
            background_opacity=0.8,
            background_padding=14.0,
            shadow_enabled=True,
            shadow_color="#9400D3",
            shadow_offset=2.5,
            position_y_percentage=83.0,
            max_width_percentage=88.0
        )
        
        # Initialize theme
        super().__init__(
            theme_id="preset_entertainment",
            name="Entertainment Tonight",
            category=ThemeCategory.ENTERTAINMENT,
            version="1.0.0",
            style_reference=entertainment_style,
            brand_kit=entertainment_brand,
            intro_template=intro_template,
            outro_template=outro_template,
            transition_style=TransitionStyle.ZOOM,
            transition_duration=0.35,
            logo_config=logo_config,
            lower_thirds_style=lower_thirds,
            caption_style=captions,
            intro_music="assets/audio/entertainment_intro.mp3",
            outro_music="assets/audio/entertainment_outro.mp3",
            background_music_style="upbeat-pop",
            sound_effects_pack="entertainment-sparkle",
            content_tone="exciting",
            content_style="entertaining",
            target_audience="general-entertainment",
            default_duration=90,
            default_aspect_ratio="16:9",
            default_resolution="1920x1080",
            default_frame_rate=30,
            description="Vibrant entertainment theme with sparkles and celebrity-style presentation",
            tags=["entertainment", "celebrity", "lifestyle", "vibrant", "pop-culture"],
            created_by="system"
        )