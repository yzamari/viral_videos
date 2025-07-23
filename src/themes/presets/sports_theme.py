"""
Sports Theme Preset
Dynamic sports broadcast theme with scoreboard style
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


class SportsTheme(Theme):
    """Dynamic sports broadcast theme"""
    
    def __init__(self):
        # Create sports-style color palette
        sports_colors = ColorPalette(
            primary_color="#FF6B00",  # Sports orange
            secondary_color="#FFFFFF",  # White
            accent_color="#000000",  # Black
            background_colors=["#2C3E50", "#34495E"],
            text_colors=["#FFFFFF", "#FFD700"],
            saturation_level=0.9,
            brightness_level=0.7,
            contrast_ratio=0.85,
            mood="energetic"
        )
        
        # Sports typography
        sports_typography = Typography(
            primary_font_family="Impact",
            secondary_font_family="Arial Black",
            title_size_ratio=0.09,
            body_size_ratio=0.05,
            font_weight="bold",
            letter_spacing=1.2,
            line_height=1.2,
            has_shadow=True,
            has_outline=True,
            text_animation_style="slam"
        )
        
        # Sports composition
        sports_composition = Composition(
            rule_of_thirds_adherence=0.7,
            symmetry_score=0.6,
            primary_layout="dynamic-action",
            text_placement_zones=["top-banner", "lower-third", "scoreboard"],
            margin_ratio=0.03,
            padding_ratio=0.02,
            focal_point_strategy="action-tracking",
            depth_layers=5
        )
        
        # Sports motion style
        sports_motion = MotionStyle(
            camera_movement="dynamic",
            transition_style="swipe",
            average_shot_duration=2.5,
            movement_intensity=0.8,
            text_animation_type="slam",
            element_animation_style="bounce",
            pacing="fast",
            rhythm_pattern="action-sync"
        )
        
        # Create style reference
        sports_style = StyleReference(
            reference_id="style_sports_preset",
            name="Sports Broadcast Style",
            reference_type=ReferenceType.TEMPLATE,
            source_path=None,
            template_id="preset_sports",
            color_palette=sports_colors,
            typography=sports_typography,
            composition=sports_composition,
            motion_style=sports_motion,
            visual_effects=[
                VisualEffect(
                    effect_type="motion-blur",
                    intensity=0.6,
                    apply_to="background",
                    parameters={"blur_amount": 5}
                ),
                VisualEffect(
                    effect_type="speed-lines",
                    intensity=0.4,
                    apply_to="full-frame",
                    parameters={"direction": "horizontal"}
                )
            ],
            logo_placement=None,
            watermark=None,
            lower_thirds=None,
            aspect_ratio="16:9",
            resolution="1920x1080",
            frame_rate=60,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags=["sports", "dynamic", "energetic", "broadcast"],
            description="Dynamic sports broadcast visual style",
            confidence_scores={"preset": 1.0}
        )
        
        # Create brand kit
        sports_brand = BrandKit(
            primary_logo="assets/logos/sports_logo.png",
            primary_logo_dark="assets/logos/sports_logo_dark.png",
            primary_logo_light="assets/logos/sports_logo_light.png",
            color_primary="#FF6B00",
            color_secondary="#FFFFFF",
            color_accent="#FFD700",  # Gold for highlights
            color_background="#2C3E50",
            color_text_primary="#FFFFFF",
            color_text_secondary="#FFD700",
            fonts={
                "heading": "Impact",
                "body": "Arial Black",
                "score": "Digital-7"  # Digital font for scores
            },
            minimum_logo_size_percentage=10.0,
            clear_space_ratio=1.5
        )
        
        # Create intro template
        intro_template = VideoTemplate(
            template_id="sports_intro",
            duration=4.0,
            background_type="video",
            background_content="assets/templates/sports_intro_bg.mp4",
            title_text="{SPORT_TYPE} CHAMPIONSHIP",
            subtitle_text="{TEAM1} vs {TEAM2}",
            title_animation="slam",
            music_path="assets/audio/sports_intro.mp3",
            sound_effects=["crowd-cheer", "whistle", "impact"],
            fade_in_duration=0.2,
            fade_out_duration=0.3
        )
        
        # Create outro template
        outro_template = VideoTemplate(
            template_id="sports_outro",
            duration=3.0,
            background_type="video",
            background_content="assets/templates/sports_outro_bg.mp4",
            title_text="FINAL SCORE",
            subtitle_text="{SCORE}",
            title_animation="zoom-bounce",
            music_path="assets/audio/sports_outro.mp3",
            sound_effects=["crowd-applause"],
            fade_in_duration=0.3,
            fade_out_duration=0.5
        )
        
        # Logo configuration
        logo_config = LogoConfiguration(
            logo_path="assets/logos/sports_logo.png",
            position="top-left",
            size_percentage=12.0,
            opacity=0.95,
            always_visible=True,
            margin_percentage=2.5,
            entrance_animation="bounce",
            exit_animation="zoom-out"
        )
        
        # Lower thirds style (scoreboard style)
        lower_thirds = LowerThirdsStyle(
            enabled=True,
            background_type="gradient",
            background_color_primary="#FF6B00",
            background_color_secondary="#CC5500",
            background_opacity=0.9,
            title_font_size_ratio=0.07,
            subtitle_font_size_ratio=0.05,
            title_color="#FFFFFF",
            subtitle_color="#FFD700",
            entrance_animation="slide-bounce",
            exit_animation="slide-bounce",
            animation_duration=0.3,
            position_y_percentage=80.0,
            height_percentage=15.0,
            margin_x_percentage=2.0
        )
        
        # Caption style
        captions = CaptionStyle(
            font_family="Arial Black",
            font_size_ratio=0.045,
            font_color="#FFFFFF",
            font_weight="bold",
            background_enabled=True,
            background_color="#000000",
            background_opacity=0.85,
            background_padding=15.0,
            shadow_enabled=True,
            shadow_color="#FF6B00",
            shadow_offset=3.0,
            position_y_percentage=82.0,
            max_width_percentage=85.0
        )
        
        # Initialize theme
        super().__init__(
            theme_id="preset_sports",
            name="Sports Edition",
            category=ThemeCategory.SPORTS,
            version="1.0.0",
            style_reference=sports_style,
            brand_kit=sports_brand,
            intro_template=intro_template,
            outro_template=outro_template,
            transition_style=TransitionStyle.WIPE,
            transition_duration=0.3,
            logo_config=logo_config,
            lower_thirds_style=lower_thirds,
            caption_style=captions,
            intro_music="assets/audio/sports_intro.mp3",
            outro_music="assets/audio/sports_outro.mp3",
            background_music_style="energetic-sports",
            sound_effects_pack="sports-broadcast",
            content_tone="energetic",
            content_style="action-packed",
            target_audience="sports-fans",
            default_duration=90,
            default_aspect_ratio="16:9",
            default_resolution="1920x1080",
            default_frame_rate=60,
            description="Dynamic sports broadcast theme with scoreboard styling and energetic transitions",
            tags=["sports", "broadcast", "dynamic", "scoreboard", "championship"],
            created_by="system"
        )