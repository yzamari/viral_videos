"""
Corporate Theme Example
Professional corporate branding theme with clean design
"""
from datetime import datetime

from src.themes.models.theme import (
    Theme, ThemeCategory, TransitionStyle, VideoTemplate,
    LogoConfiguration, LowerThirdsStyle, CaptionStyle, BrandKit
)
from src.style_reference.models.style_attributes import (
    ColorPalette, Typography, Composition, MotionStyle, VisualEffect
)
from src.style_reference.models.style_reference import StyleReference, ReferenceType


def create_corporate_theme():
    """Create a professional corporate theme"""
    
    # Corporate color palette
    corporate_colors = ColorPalette(
        primary_color="#1E3A8A",  # Corporate blue
        secondary_color="#FFFFFF",  # White
        accent_color="#10B981",  # Success green
        background_colors=["#F9FAFB", "#E5E7EB"],
        text_colors=["#111827", "#6B7280"],
        saturation_level=0.6,
        brightness_level=0.8,
        contrast_ratio=0.85,
        mood="professional"
    )
    
    # Corporate typography
    corporate_typography = Typography(
        primary_font_family="Inter",
        secondary_font_family="Roboto",
        title_size_ratio=0.07,
        body_size_ratio=0.04,
        font_weight="medium",
        letter_spacing=1.0,
        line_height=1.5,
        has_shadow=False,
        has_outline=False,
        text_animation_style="fade"
    )
    
    # Corporate composition
    corporate_composition = Composition(
        rule_of_thirds_adherence=0.9,
        symmetry_score=0.95,
        primary_layout="grid-based",
        text_placement_zones=["lower-third", "center"],
        margin_ratio=0.08,
        padding_ratio=0.04,
        focal_point_strategy="center-balanced",
        depth_layers=3
    )
    
    # Corporate motion style
    corporate_motion = MotionStyle(
        camera_movement="minimal",
        transition_style="fade",
        average_shot_duration=4.0,
        movement_intensity=0.2,
        text_animation_type="fade",
        element_animation_style="slide",
        pacing="steady",
        rhythm_pattern="consistent"
    )
    
    # Create style reference
    corporate_style = StyleReference(
        reference_id="style_corporate_example",
        name="Corporate Professional Style",
        reference_type=ReferenceType.TEMPLATE,
        source_path=None,
        template_id="corporate_template",
        color_palette=corporate_colors,
        typography=corporate_typography,
        composition=corporate_composition,
        motion_style=corporate_motion,
        visual_effects=[
            VisualEffect(
                effect_type="subtle-blur",
                intensity=0.2,
                apply_to="background",
                parameters={"blur_radius": 3}
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
        tags=["corporate", "professional", "business"],
        description="Clean corporate visual style",
        confidence_scores={"preset": 1.0}
    )
    
    # Create brand kit
    corporate_brand = BrandKit(
        primary_logo="assets/logos/corporate_logo.png",
        primary_logo_dark="assets/logos/corporate_logo_dark.png",
        primary_logo_light="assets/logos/corporate_logo_light.png",
        color_primary="#1E3A8A",
        color_secondary="#FFFFFF",
        color_accent="#10B981",
        color_background="#F9FAFB",
        color_text_primary="#111827",
        color_text_secondary="#6B7280",
        fonts={
            "heading": "Inter",
            "body": "Roboto",
            "caption": "Inter"
        },
        minimum_logo_size_percentage=6.0,
        clear_space_ratio=3.0,
        allow_logo_on_dark=True,
        allow_logo_on_light=True
    )
    
    # Create intro template
    intro_template = VideoTemplate(
        template_id="corporate_intro",
        duration=2.5,
        background_type="gradient",
        background_content="#1E3A8A,#2563EB",
        title_text="{COMPANY_NAME}",
        subtitle_text="{TAGLINE}",
        title_animation="fade-up",
        music_path="assets/audio/corporate_intro.mp3",
        sound_effects=["subtle-whoosh"],
        fade_in_duration=0.3,
        fade_out_duration=0.5
    )
    
    # Create outro template
    outro_template = VideoTemplate(
        template_id="corporate_outro",
        duration=2.0,
        background_type="solid",
        background_content="#F9FAFB",
        title_text="Thank You",
        subtitle_text="{WEBSITE_URL}",
        title_animation="fade",
        music_path="assets/audio/corporate_outro.mp3",
        fade_in_duration=0.4,
        fade_out_duration=0.6
    )
    
    # Logo configuration
    logo_config = LogoConfiguration(
        logo_path="assets/logos/corporate_logo.png",
        position="top-left",
        size_percentage=8.0,
        opacity=0.9,
        always_visible=True,
        margin_percentage=3.0,
        entrance_animation="fade",
        exit_animation="fade"
    )
    
    # Lower thirds style
    lower_thirds = LowerThirdsStyle(
        enabled=True,
        background_type="solid",
        background_color_primary="#1E3A8A",
        background_opacity=0.9,
        title_font_size_ratio=0.05,
        subtitle_font_size_ratio=0.035,
        title_color="#FFFFFF",
        subtitle_color="#E5E7EB",
        entrance_animation="slide-left",
        exit_animation="slide-left",
        animation_duration=0.4,
        position_y_percentage=80.0,
        height_percentage=10.0,
        margin_x_percentage=5.0
    )
    
    # Caption style
    captions = CaptionStyle(
        font_family="Inter",
        font_size_ratio=0.038,
        font_color="#111827",
        font_weight="medium",
        background_enabled=True,
        background_color="#FFFFFF",
        background_opacity=0.95,
        background_padding=12.0,
        shadow_enabled=False,
        position_y_percentage=85.0,
        max_width_percentage=75.0
    )
    
    # Create theme
    theme = Theme(
        theme_id="corporate_professional",
        name="Corporate Professional",
        category=ThemeCategory.BUSINESS,
        version="1.0.0",
        style_reference=corporate_style,
        brand_kit=corporate_brand,
        intro_template=intro_template,
        outro_template=outro_template,
        transition_style=TransitionStyle.FADE,
        transition_duration=0.5,
        logo_config=logo_config,
        lower_thirds_style=lower_thirds,
        caption_style=captions,
        intro_music="assets/audio/corporate_intro.mp3",
        outro_music="assets/audio/corporate_outro.mp3",
        background_music_style="ambient-corporate",
        sound_effects_pack="minimal-professional",
        content_tone="professional",
        content_style="informative",
        target_audience="business-professionals",
        default_duration=90,
        default_aspect_ratio="16:9",
        default_resolution="1920x1080",
        default_frame_rate=30,
        description="Clean and professional corporate theme for business communications",
        tags=["corporate", "business", "professional", "clean", "minimal"],
        created_by="example"
    )
    
    return theme


if __name__ == "__main__":
    # Create and save the theme
    from src.themes.managers.theme_manager import ThemeManager
    
    theme_manager = ThemeManager()
    theme = create_corporate_theme()
    theme_id = theme_manager.save_theme(theme)
    print(f"✅ Created corporate theme: {theme_id}")