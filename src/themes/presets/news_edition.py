"""
News Edition Theme Preset
Professional news broadcast theme with lower thirds, breaking news style
"""
from datetime import datetime

from ..models.theme import (
    Theme, ThemeCategory, TransitionStyle, VideoTemplate,
    LogoConfiguration, LowerThirdsStyle, CaptionStyle, BrandKit
)
from ...style_reference.models.style_attributes import (
    ColorPalette, Typography, Composition, MotionStyle
)
from ...style_reference.models.style_reference import StyleReference, ReferenceType


class NewsEditionTheme(Theme):
    """Professional news broadcast theme"""
    
    def __init__(self):
        # Create news-style color palette
        news_colors = ColorPalette(
            primary_color="#CC0000",  # News red
            secondary_color="#FFFFFF",  # White
            accent_color="#000000",  # Black
            background_colors=["#F5F5F5", "#E0E0E0"],
            text_colors=["#FFFFFF", "#000000"],
            saturation_level=0.8,
            brightness_level=0.5,
            contrast_ratio=0.9,
            mood="professional"
        )
        
        # News typography
        news_typography = Typography(
            primary_font_family="Arial",
            secondary_font_family="Helvetica",
            title_size_ratio=0.08,
            body_size_ratio=0.05,
            font_weight="bold",
            letter_spacing=1.1,
            line_height=1.3,
            has_shadow=True,
            has_outline=False,
            text_animation_style="slide"
        )
        
        # News composition
        news_composition = Composition(
            rule_of_thirds_adherence=0.9,
            symmetry_score=0.8,
            primary_layout="lower-third-heavy",
            text_placement_zones=["lower-third", "top-banner"],
            margin_ratio=0.05,
            padding_ratio=0.02,
            focal_point_strategy="center-news-anchor",
            depth_layers=4
        )
        
        # News motion style
        news_motion = MotionStyle(
            camera_movement="static",
            transition_style="cut",
            average_shot_duration=4.0,
            movement_intensity=0.2,
            text_animation_type="slide",
            element_animation_style="wipe",
            pacing="moderate",
            rhythm_pattern="steady"
        )
        
        # Create style reference
        news_style = StyleReference(
            reference_id="style_news_preset",
            name="News Broadcast Style",
            reference_type=ReferenceType.TEMPLATE,
            source_path=None,
            template_id="preset_news",
            color_palette=news_colors,
            typography=news_typography,
            composition=news_composition,
            motion_style=news_motion,
            visual_effects=[],
            logo_placement=None,
            watermark=None,
            lower_thirds=None,
            aspect_ratio="16:9",
            resolution="1920x1080",
            frame_rate=30,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags=["news", "broadcast", "professional"],
            description="Professional news broadcast visual style",
            confidence_scores={"preset": 1.0}
        )
        
        # Create brand kit
        news_brand = BrandKit(
            primary_logo="assets/logos/news_logo.png",
            primary_logo_dark="assets/logos/news_logo_dark.png",
            primary_logo_light="assets/logos/news_logo_light.png",
            color_primary="#CC0000",
            color_secondary="#FFFFFF",
            color_accent="#FFD700",  # Breaking news yellow
            color_background="#F5F5F5",
            color_text_primary="#000000",
            color_text_secondary="#333333",
            fonts={
                "heading": "Arial Black",
                "body": "Arial",
                "ticker": "Helvetica"
            },
            minimum_logo_size_percentage=8.0,
            clear_space_ratio=2.0
        )
        
        # Create intro template
        intro_template = VideoTemplate(
            template_id="news_intro",
            duration=3.0,
            background_type="video",
            background_content="assets/templates/news_intro_bg.mp4",
            title_text="{CHANNEL_NAME} NEWS",
            subtitle_text="{DATE} | {TIME}",
            title_animation="zoom-in",
            music_path="assets/audio/news_intro.mp3",
            sound_effects=["swoosh", "impact"],
            fade_in_duration=0.3,
            fade_out_duration=0.5
        )
        
        # Create outro template
        outro_template = VideoTemplate(
            template_id="news_outro",
            duration=2.5,
            background_type="gradient",
            background_content="#CC0000,#000000",
            title_text="THANK YOU FOR WATCHING",
            subtitle_text="{CHANNEL_NAME} NEWS",
            title_animation="fade",
            music_path="assets/audio/news_outro.mp3",
            fade_in_duration=0.5,
            fade_out_duration=0.8
        )
        
        # Logo configuration
        logo_config = LogoConfiguration(
            logo_path="assets/logos/news_logo.png",
            position="top-right",
            size_percentage=10.0,
            opacity=0.9,
            always_visible=True,
            margin_percentage=2.0
        )
        
        # Lower thirds style
        lower_thirds = LowerThirdsStyle(
            enabled=True,
            background_type="gradient",
            background_color_primary="#CC0000",
            background_color_secondary="#990000",
            background_opacity=0.95,
            title_font_size_ratio=0.06,
            subtitle_font_size_ratio=0.04,
            title_color="#FFFFFF",
            subtitle_color="#FFD700",
            entrance_animation="slide-left",
            exit_animation="slide-left",
            animation_duration=0.4,
            position_y_percentage=75.0,
            height_percentage=12.0,
            margin_x_percentage=3.0
        )
        
        # Caption style
        captions = CaptionStyle(
            font_family="Arial",
            font_size_ratio=0.04,
            font_color="#FFFFFF",
            font_weight="bold",
            background_enabled=True,
            background_color="#000000",
            background_opacity=0.8,
            background_padding=12.0,
            shadow_enabled=True,
            shadow_color="#000000",
            shadow_offset=2.0,
            position_y_percentage=85.0,
            max_width_percentage=90.0
        )
        
        # Initialize theme
        super().__init__(
            theme_id="preset_news_edition",
            name="News Edition",
            category=ThemeCategory.NEWS,
            version="1.0.0",
            style_reference=news_style,
            brand_kit=news_brand,
            intro_template=intro_template,
            outro_template=outro_template,
            transition_style=TransitionStyle.CUT,
            transition_duration=0.2,
            logo_config=logo_config,
            lower_thirds_style=lower_thirds,
            caption_style=captions,
            intro_music="assets/audio/news_intro.mp3",
            outro_music="assets/audio/news_outro.mp3",
            background_music_style="subtle-news",
            sound_effects_pack="news-broadcast",
            content_tone="professional",
            content_style="informative",
            target_audience="general-public",
            default_duration=60,
            default_aspect_ratio="16:9",
            default_resolution="1920x1080",
            default_frame_rate=30,
            description="Professional news broadcast theme with lower thirds and breaking news styling",
            tags=["news", "broadcast", "professional", "breaking-news", "lower-thirds"],
            created_by="system"
        )