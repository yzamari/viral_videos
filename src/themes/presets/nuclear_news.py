"""
Nuclear News Theme Preset - Family Guy Style
Satirical animated news broadcast theme with Family Guy aesthetic
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


class NuclearNewsTheme(Theme):
    """Nuclear News - Family Guy style news broadcast theme"""
    
    def __init__(self):
        # Create Family Guy news color palette
        nuclear_colors = ColorPalette(
            primary_color="#FF0000",  # Bright red for drama
            secondary_color="#000080",  # Navy blue
            accent_color="#FFFF00",  # Yellow for alerts
            background_colors=["#000080", "#0000CD"],  # Blue news desk style
            text_colors=["#FFFFFF", "#FFFF00"],
            saturation_level=1.0,  # Maximum saturation for cartoon style
            brightness_level=0.7,  # Bright cartoon colors
            contrast_ratio=0.9,
            mood="satirical-dramatic"
        )
        
        # Family Guy style typography
        nuclear_typography = Typography(
            primary_font_family="Impact",  # Bold cartoon font
            secondary_font_family="Arial Black",  # Thick readable font
            title_size_ratio=0.09,  # Larger for cartoon style
            body_size_ratio=0.06,
            font_weight="black",
            letter_spacing=1.2,
            line_height=1.2,
            has_shadow=True,
            has_outline=True,  # Cartoon outline
            text_animation_style="slam"
        )
        
        # News desk composition
        nuclear_composition = Composition(
            rule_of_thirds_adherence=0.7,  # Less strict for cartoon
            symmetry_score=0.8,
            primary_layout="lower-third-heavy",
            text_placement_zones=["lower-third", "top-banner", "ticker"],
            margin_ratio=0.03,
            padding_ratio=0.02,
            focal_point_strategy="center-news-anchor",
            depth_layers=8  # Extra layers for cartoon effects and overlays
        )
        
        # Cartoon motion style
        nuclear_motion = MotionStyle(
            camera_movement="shake",  # Dramatic shakes
            transition_style="swoosh",
            average_shot_duration=3.0,  # Faster cuts
            movement_intensity=0.4,  # More animated
            text_animation_type="slam",
            element_animation_style="bounce",
            pacing="frenetic",
            rhythm_pattern="chaotic"
        )
        
        # Create style reference
        nuclear_style = StyleReference(
            reference_id="style_nuclear_news_preset",
            name="Nuclear News Family Guy Style",
            reference_type=ReferenceType.TEMPLATE,
            source_path=None,
            template_id="preset_nuclear_news",
            color_palette=nuclear_colors,
            typography=nuclear_typography,
            composition=nuclear_composition,
            motion_style=nuclear_motion,
            visual_effects=["lower-thirds", "ticker", "breaking-news-banner", "cartoon-outline", "shake"],
            logo_placement="top-left",
            watermark=None,
            lower_thirds="cartoon-news",
            aspect_ratio="16:9",
            resolution="1920x1080",
            frame_rate=30,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags=["news", "family-guy", "animated", "satirical", "comedy"],
            description="Family Guy style satirical news broadcast",
            confidence_scores={"preset": 1.0}
        )
        
        # Create brand kit
        nuclear_brand = BrandKit(
            primary_logo="assets/logos/nuclear_news_logo.png",
            primary_logo_dark="assets/logos/nuclear_news_logo_dark.png",
            primary_logo_light="assets/logos/nuclear_news_logo_light.png",
            color_primary="#FF0000",
            color_secondary="#000080",
            color_accent="#FFFF00",
            color_background="#000080",
            color_text_primary="#FFFFFF",
            color_text_secondary="#FFFF00",
            fonts={
                "heading": "Impact",
                "body": "Arial Black",
                "ticker": "Comic Sans MS",  # Extra cartoony for ticker
                "persian": "B Nazanin"
            },
            minimum_logo_size_percentage=15.0,  # Bigger for cartoon style
            clear_space_ratio=1.5
        )
        
        # Create intro template
        intro_template = VideoTemplate(
            template_id="nuclear_news_intro",
            duration=2.0,  # Shorter, punchier
            background_type="gradient",
            background_content="#FF0000,#000080",
            title_text="NUCLEAR NEWS",
            subtitle_text="WE REPORT, YOU PANIC!",
            title_animation="explosion",
            music_path="assets/audio/nuclear_news_intro.mp3",
            sound_effects=["explosion", "siren", "dramatic-sting"],
            fade_in_duration=0.1,
            fade_out_duration=0.2
        )
        
        # Create outro template
        outro_template = VideoTemplate(
            template_id="nuclear_news_outro",
            duration=2.0,
            background_type="solid",
            background_content="#000080",
            title_text="NUCLEAR NEWS",
            subtitle_text="Tomorrow's Disasters Today!",
            title_animation="shake",
            music_path="assets/audio/nuclear_news_outro.mp3",
            fade_in_duration=0.2,
            fade_out_duration=0.5
        )
        
        # Logo configuration
        logo_config = LogoConfiguration(
            logo_path="assets/logos/nuclear_news_logo.png",
            position="top-left",  # Family Guy style position
            size_percentage=18.0,  # Large cartoon logo
            opacity=1.0,  # Full opacity for cartoon
            always_visible=True,
            margin_percentage=1.5,
            z_index=999  # Ensure logo is always on top
        )
        
        # Lower thirds style - Family Guy news desk
        lower_thirds = LowerThirdsStyle(
            enabled=True,
            background_type="gradient",
            background_color_primary="#FF0000",
            background_color_secondary="#8B0000",
            background_opacity=0.95,
            title_font_size_ratio=0.08,  # Bigger for cartoon
            subtitle_font_size_ratio=0.05,
            title_color="#FFFFFF",
            subtitle_color="#FFFF00",
            entrance_animation="bounce",  # Cartoon bounce
            exit_animation="explode",
            animation_duration=0.3,
            position_y_percentage=72.0,
            height_percentage=15.0,  # Taller for cartoon style
            margin_x_percentage=2.0,
            z_index=998  # Ensure lower thirds are on top
        )
        
        # Caption style
        captions = CaptionStyle(
            font_family="Arial Black",
            font_size_ratio=0.055,  # Bigger for cartoon
            font_color="#FFFFFF",
            font_weight="black",
            background_enabled=True,
            background_color="#000000",
            background_opacity=0.9,
            background_padding=20.0,
            shadow_enabled=True,
            shadow_color="#FF0000",  # Red shadow for drama
            shadow_offset=3.0,
            position_y_percentage=78.0,
            max_width_percentage=80.0
        )
        
        # Additional cartoon news elements
        self.ticker_config = {
            "enabled": True,
            "position": "bottom",
            "height_percentage": 8.0,  # Taller ticker
            "background_color": "#FFFF00",  # Yellow ticker
            "text_color": "#000000",
            "speed": "fast",  # Faster for comedy
            "font_size_ratio": 0.04,
            "font_family": "Comic Sans MS",
            "content": [
                "BREAKING: Water still missing! Scientists baffled!",
                "THIS JUST IN: Government forms committee to form committees",
                "ALERT: Citizens resort to drinking their own tears",
                "NUCLEAR NEWS - Fair & Balanced & Totally Not Panicking"
            ],
            "z_index": 997  # Ensure ticker is on top
        }
        
        self.breaking_news_banner = {
            "enabled": True,
            "position": "top",
            "height_percentage": 10.0,  # Bigger banner
            "background_color": "#FF0000",
            "text_color": "#FFFFFF",
            "text": "BREAKING NEWS!!!",
            "animation": "flash",
            "font_family": "Impact",
            "z_index": 996  # Ensure banner is on top
        }
        
        # Family Guy style news desk overlay
        self.news_desk_overlay = {
            "enabled": True,
            "style": "family_guy_desk",
            "desk_color": "#000080",
            "desk_height_percentage": 25.0,
            "has_globe": True,  # Spinning globe behind anchor
            "has_papers": True,  # Scattered papers for chaos
            "animation_style": "cartoon",
            "z_index": 995,  # Desk below other overlays
            "render_order": "foreground"  # Ensure desk is in foreground
        }
        
        # Initialize theme
        super().__init__(
            theme_id="preset_nuclear_news",
            name="Nuclear News",
            category=ThemeCategory.NEWS,
            version="1.0.0",
            style_reference=nuclear_style,
            brand_kit=nuclear_brand,
            intro_template=intro_template,
            outro_template=outro_template,
            transition_style=TransitionStyle.SWOOSH,
            transition_duration=0.3,
            logo_config=logo_config,
            lower_thirds_style=lower_thirds,
            caption_style=captions,
            intro_music="assets/audio/nuclear_news_intro.mp3",
            outro_music="assets/audio/nuclear_news_outro.mp3",
            background_music_style="dramatic-cartoon",
            sound_effects_pack="cartoon-news",
            content_tone="satirical-panicked",
            content_style="comedic",
            target_audience="comedy-fans",
            default_duration=60,
            default_aspect_ratio="16:9",
            default_resolution="1920x1080",
            default_frame_rate=30,
            description="Family Guy style satirical news broadcast with dramatic flair",
            tags=["news", "family-guy", "cartoon", "satirical", "comedy", "animated"],
            created_by="system",
            overlay_settings={
                "render_order": "top",  # Ensure all overlays render on top
                "composite_mode": "over",  # Overlay mode
                "layer_priority": [
                    "logo",  # Logo on top
                    "lower_thirds",  # Then lower thirds
                    "ticker",  # Then ticker
                    "breaking_news",  # Then breaking news
                    "news_desk"  # Desk at bottom of overlays
                ]
            }
        )