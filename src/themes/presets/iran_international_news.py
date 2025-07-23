"""
Iran International News Theme Preset
Professional Persian news broadcast theme with Iran International branding
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


class IranInternationalNewsTheme(Theme):
    """Iran International news broadcast theme"""
    
    def __init__(self):
        # Create Iran International color palette
        iran_intl_colors = ColorPalette(
            primary_color="#C8102E",  # Iran International red
            secondary_color="#FFFFFF",  # White
            accent_color="#FFD700",  # Gold/yellow for breaking news
            background_colors=["#1A1A1A", "#2B2B2B"],  # Dark backgrounds
            text_colors=["#FFFFFF", "#C8102E"],
            saturation_level=0.9,
            brightness_level=0.3,  # Darker for professional look
            contrast_ratio=0.95,
            mood="professional-serious"
        )
        
        # Persian-friendly typography
        iran_intl_typography = Typography(
            primary_font_family="Arial",  # Works well with Persian text
            secondary_font_family="Tahoma",  # Good Persian support
            title_size_ratio=0.08,
            body_size_ratio=0.05,
            font_weight="bold",
            letter_spacing=1.0,
            line_height=1.4,  # Better for Persian text
            has_shadow=True,
            has_outline=False,
            text_animation_style="slide"
        )
        
        # News composition
        iran_intl_composition = Composition(
            rule_of_thirds_adherence=0.9,
            symmetry_score=0.85,
            primary_layout="lower-third-heavy",
            text_placement_zones=["lower-third", "top-banner", "ticker"],
            margin_ratio=0.04,
            padding_ratio=0.02,
            focal_point_strategy="center-news-anchor",
            depth_layers=5  # More layers for ticker
        )
        
        # News motion style
        iran_intl_motion = MotionStyle(
            camera_movement="static",
            transition_style="cut",
            average_shot_duration=5.0,
            movement_intensity=0.1,
            text_animation_type="slide",
            element_animation_style="wipe",
            pacing="steady",
            rhythm_pattern="continuous"
        )
        
        # Create style reference
        iran_intl_style = StyleReference(
            reference_id="style_iran_intl_preset",
            name="Iran International News Style",
            reference_type=ReferenceType.TEMPLATE,
            source_path=None,
            template_id="preset_iran_international",
            color_palette=iran_intl_colors,
            typography=iran_intl_typography,
            composition=iran_intl_composition,
            motion_style=iran_intl_motion,
            visual_effects=["lower-thirds", "ticker", "breaking-news-banner"],
            logo_placement="top-right",
            watermark=None,
            lower_thirds="professional-news",
            aspect_ratio="16:9",
            resolution="1920x1080",
            frame_rate=30,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags=["news", "persian", "iran-international", "professional"],
            description="Iran International professional news broadcast style",
            confidence_scores={"preset": 1.0}
        )
        
        # Create brand kit
        iran_intl_brand = BrandKit(
            primary_logo="assets/logos/iran_international_logo.png",
            primary_logo_dark="assets/logos/iran_international_logo_dark.png",
            primary_logo_light="assets/logos/iran_international_logo_light.png",
            color_primary="#C8102E",
            color_secondary="#FFFFFF",
            color_accent="#FFD700",
            color_background="#1A1A1A",
            color_text_primary="#FFFFFF",
            color_text_secondary="#C8102E",
            fonts={
                "heading": "Arial Black",
                "body": "Arial",
                "ticker": "Tahoma",
                "persian": "B Nazanin"  # Persian font
            },
            minimum_logo_size_percentage=10.0,
            clear_space_ratio=2.0
        )
        
        # Create intro template
        intro_template = VideoTemplate(
            template_id="iran_intl_intro",
            duration=3.0,
            background_type="video",
            background_content="assets/templates/iran_intl_intro_bg.mp4",
            title_text="IRAN INTERNATIONAL",
            subtitle_text="اخبار | NEWS",
            title_animation="zoom-in",
            music_path="assets/audio/iran_intl_intro.mp3",
            sound_effects=["news-swoosh", "impact"],
            fade_in_duration=0.3,
            fade_out_duration=0.5
        )
        
        # Create outro template
        outro_template = VideoTemplate(
            template_id="iran_intl_outro",
            duration=2.5,
            background_type="gradient",
            background_content="#C8102E,#1A1A1A",
            title_text="IRAN INTERNATIONAL",
            subtitle_text="Stay Informed | با ما همراه باشید",
            title_animation="fade",
            music_path="assets/audio/iran_intl_outro.mp3",
            fade_in_duration=0.5,
            fade_out_duration=0.8
        )
        
        # Logo configuration
        logo_config = LogoConfiguration(
            logo_path="assets/logos/iran_international_logo.png",
            position="top-right",
            size_percentage=12.0,  # Slightly larger
            opacity=0.95,
            always_visible=True,
            margin_percentage=2.0
        )
        
        # Lower thirds style
        lower_thirds = LowerThirdsStyle(
            enabled=True,
            background_type="gradient",
            background_color_primary="#C8102E",
            background_color_secondary="#8B0000",
            background_opacity=0.95,
            title_font_size_ratio=0.06,
            subtitle_font_size_ratio=0.04,
            title_color="#FFFFFF",
            subtitle_color="#FFD700",
            entrance_animation="slide-right",  # RTL friendly
            exit_animation="slide-right",
            animation_duration=0.4,
            position_y_percentage=75.0,
            height_percentage=13.0,
            margin_x_percentage=3.0
        )
        
        # Caption style
        captions = CaptionStyle(
            font_family="Arial",
            font_size_ratio=0.045,
            font_color="#FFFFFF",
            font_weight="bold",
            background_enabled=True,
            background_color="#000000",
            background_opacity=0.85,
            background_padding=15.0,
            shadow_enabled=True,
            shadow_color="#000000",
            shadow_offset=2.0,
            position_y_percentage=80.0,  # Higher to avoid ticker
            max_width_percentage=85.0
        )
        
        # Additional news elements configuration
        self.ticker_config = {
            "enabled": True,
            "position": "bottom",
            "height_percentage": 6.0,
            "background_color": "#000000",
            "text_color": "#FFFFFF",
            "speed": "moderate",
            "font_size_ratio": 0.035,
            "content": [
                "آخرین اخبار ایران و جهان",
                "BREAKING NEWS • اخبار فوری",
                "تحلیل‌های کارشناسان • EXPERT ANALYSIS"
            ]
        }
        
        self.breaking_news_banner = {
            "enabled": True,
            "position": "top",
            "height_percentage": 8.0,
            "background_color": "#FFD700",
            "text_color": "#000000",
            "text": "خبر فوری • BREAKING NEWS",
            "animation": "pulse"
        }
        
        # Initialize theme
        super().__init__(
            theme_id="preset_iran_international_news",
            name="Iran International News",
            category=ThemeCategory.NEWS,
            version="1.0.0",
            style_reference=iran_intl_style,
            brand_kit=iran_intl_brand,
            intro_template=intro_template,
            outro_template=outro_template,
            transition_style=TransitionStyle.CUT,
            transition_duration=0.2,
            logo_config=logo_config,
            lower_thirds_style=lower_thirds,
            caption_style=captions,
            intro_music="assets/audio/iran_intl_intro.mp3",
            outro_music="assets/audio/iran_intl_outro.mp3",
            background_music_style="subtle-news",
            sound_effects_pack="news-broadcast",
            content_tone="professional-serious",
            content_style="informative",
            target_audience="persian-speaking",
            default_duration=60,
            default_aspect_ratio="16:9",
            default_resolution="1920x1080",
            default_frame_rate=30,
            description="Iran International professional Persian news broadcast theme",
            tags=["news", "persian", "iran-international", "broadcast", "professional"],
            created_by="system"
        )