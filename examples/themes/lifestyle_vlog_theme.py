"""
Lifestyle Vlog Theme Example
Trendy lifestyle and vlog theme with warm, personal aesthetics
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


def create_lifestyle_vlog_theme():
    """Create a trendy lifestyle vlog theme"""
    
    # Lifestyle color palette - warm and inviting
    lifestyle_colors = ColorPalette(
        primary_color="#F4A460",  # Sandy brown
        secondary_color="#FFF8DC",  # Cornsilk
        accent_color="#FF6B9D",  # Pink accent
        background_colors=["#FFF5EE", "#FAF0E6"],  # Seashell, Linen
        text_colors=["#8B4513", "#A0522D"],  # Saddle brown, Sienna
        saturation_level=0.65,
        brightness_level=0.9,
        contrast_ratio=0.7,
        mood="warm"
    )
    
    # Lifestyle typography - modern and friendly
    lifestyle_typography = Typography(
        primary_font_family="Playfair Display",
        secondary_font_family="Lato",
        title_size_ratio=0.085,
        body_size_ratio=0.048,
        font_weight="regular",
        letter_spacing=1.2,
        line_height=1.4,
        has_shadow=False,
        has_outline=False,
        text_animation_style="fade-slide"
    )
    
    # Lifestyle composition - natural and personal
    lifestyle_composition = Composition(
        rule_of_thirds_adherence=0.7,
        symmetry_score=0.5,
        primary_layout="natural-flow",
        text_placement_zones=["lower-third", "corner-overlay"],
        margin_ratio=0.05,
        padding_ratio=0.025,
        focal_point_strategy="personal-focus",
        depth_layers=5
    )
    
    # Lifestyle motion style - smooth and trendy
    lifestyle_motion = MotionStyle(
        camera_movement="handheld-smooth",
        transition_style="crossfade",
        average_shot_duration=3.0,
        movement_intensity=0.5,
        text_animation_type="fade-slide",
        element_animation_style="float",
        pacing="relaxed",
        rhythm_pattern="lifestyle-flow"
    )
    
    # Create style reference
    lifestyle_style = StyleReference(
        reference_id="style_lifestyle_vlog",
        name="Lifestyle Vlog Style",
        reference_type=ReferenceType.TEMPLATE,
        source_path=None,
        template_id="lifestyle_vlog_template",
        color_palette=lifestyle_colors,
        typography=lifestyle_typography,
        composition=lifestyle_composition,
        motion_style=lifestyle_motion,
        visual_effects=[
            VisualEffect(
                effect_type="warm-filter",
                intensity=0.4,
                apply_to="full-frame",
                parameters={"temperature": "warm", "tint": "golden"}
            ),
            VisualEffect(
                effect_type="bokeh",
                intensity=0.3,
                apply_to="background",
                parameters={"shape": "circular", "softness": 0.8}
            ),
            VisualEffect(
                effect_type="light-leak",
                intensity=0.2,
                apply_to="edges",
                parameters={"color": "#FFB6C1", "position": "corners"}
            )
        ],
        logo_placement=None,
        watermark=None,
        lower_thirds=None,
        aspect_ratio="9:16",  # Vertical for Instagram/TikTok
        resolution="1080x1920",
        frame_rate=30,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        tags=["lifestyle", "vlog", "personal", "warm", "trendy"],
        description="Warm and personal lifestyle vlog style",
        confidence_scores={"preset": 1.0}
    )
    
    # Create brand kit
    lifestyle_brand = BrandKit(
        primary_logo="assets/logos/lifestyle_logo.png",
        primary_logo_dark=None,  # Lifestyle often uses single logo variant
        primary_logo_light="assets/logos/lifestyle_logo_light.png",
        color_primary="#F4A460",
        color_secondary="#FFF8DC",
        color_accent="#FF6B9D",
        color_background="#FFF5EE",
        color_text_primary="#8B4513",
        color_text_secondary="#A0522D",
        fonts={
            "heading": "Playfair Display",
            "body": "Lato",
            "script": "Dancing Script"  # For special accents
        },
        minimum_logo_size_percentage=8.0,
        clear_space_ratio=1.5,
        allow_logo_effects=True  # Allow creative effects on logo
    )
    
    # Create intro template
    intro_template = VideoTemplate(
        template_id="lifestyle_intro",
        duration=3.0,
        background_type="video",
        background_content="assets/templates/lifestyle_intro_bg.mp4",
        title_text="HEY BEAUTIFUL!",
        subtitle_text="{TODAY'S_TOPIC}",
        title_animation="handwritten",
        music_path="assets/audio/lifestyle_intro.mp3",
        sound_effects=["camera-shutter", "gentle-whoosh"],
        fade_in_duration=0.5,
        fade_out_duration=0.3
    )
    
    # Create outro template
    outro_template = VideoTemplate(
        template_id="lifestyle_outro",
        duration=4.0,
        background_type="image",
        background_content="assets/templates/lifestyle_outro_bg.jpg",
        title_text="THANKS FOR WATCHING!",
        subtitle_text="@{SOCIAL_HANDLE}",
        title_animation="bounce-fade",
        music_path="assets/audio/lifestyle_outro.mp3",
        sound_effects=["kiss-sound", "sparkle"],
        fade_in_duration=0.4,
        fade_out_duration=0.7
    )
    
    # Logo configuration - minimalist
    logo_config = LogoConfiguration(
        logo_path="assets/logos/lifestyle_logo.png",
        position="bottom-right",
        size_percentage=6.0,
        opacity=0.7,
        always_visible=False,  # Show intermittently for cleaner look
        appear_at=2.0,
        disappear_at=None,
        margin_percentage=3.0,
        entrance_animation="fade-bounce",
        exit_animation="fade"
    )
    
    # Lower thirds style - minimal and elegant
    lower_thirds = LowerThirdsStyle(
        enabled=True,
        background_type="blur",
        background_color_primary="#FFFFFF",
        background_opacity=0.7,
        title_font_size_ratio=0.05,
        subtitle_font_size_ratio=0.035,
        title_color="#8B4513",
        subtitle_color="#A0522D",
        entrance_animation="fade-up",
        exit_animation="fade-down",
        animation_duration=0.6,
        position_y_percentage=78.0,
        height_percentage=10.0,
        margin_x_percentage=6.0
    )
    
    # Caption style - clean and readable
    captions = CaptionStyle(
        font_family="Lato",
        font_size_ratio=0.04,
        font_color="#8B4513",
        font_weight="regular",
        background_enabled=True,
        background_color="#FFFFFF",
        background_opacity=0.85,
        background_padding=10.0,
        shadow_enabled=False,  # Clean look without shadow
        position_y_percentage=80.0,
        max_width_percentage=90.0
    )
    
    # Create theme
    theme = Theme(
        theme_id="lifestyle_vlog",
        name="Lifestyle Vlog",
        category=ThemeCategory.LIFESTYLE,
        version="1.0.0",
        style_reference=lifestyle_style,
        brand_kit=lifestyle_brand,
        intro_template=intro_template,
        outro_template=outro_template,
        transition_style=TransitionStyle.DISSOLVE,
        transition_duration=0.6,
        logo_config=logo_config,
        lower_thirds_style=lower_thirds,
        caption_style=captions,
        intro_music="assets/audio/lifestyle_intro.mp3",
        outro_music="assets/audio/lifestyle_outro.mp3",
        background_music_style="acoustic-upbeat",
        sound_effects_pack="lifestyle-sounds",
        content_tone="friendly",
        content_style="personal",
        target_audience="lifestyle-enthusiasts",
        default_duration=60,
        default_aspect_ratio="9:16",  # Vertical for social media
        default_resolution="1080x1920",
        default_frame_rate=30,
        description="Warm and trendy lifestyle vlog theme for personal content creators",
        tags=["lifestyle", "vlog", "personal", "warm", "instagram", "tiktok"],
        created_by="example"
    )
    
    return theme


if __name__ == "__main__":
    # Create and save the theme
    from src.themes.managers.theme_manager import ThemeManager
    
    theme_manager = ThemeManager()
    theme = create_lifestyle_vlog_theme()
    theme_id = theme_manager.save_theme(theme)
    print(f"✅ Created lifestyle vlog theme: {theme_id}")