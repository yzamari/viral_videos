"""
YouTube Educational Theme Example
Educational content theme with clear structure and professional presentation
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


def create_youtube_educational_theme():
    """Create a YouTube educational content theme"""
    
    # Educational color palette
    edu_colors = ColorPalette(
        primary_color="#2E7D32",  # Educational green
        secondary_color="#FFFFFF",  # White
        accent_color="#FF9800",  # Orange accent for highlights
        background_colors=["#FAFAFA", "#F5F5F5"],
        text_colors=["#212121", "#424242"],
        saturation_level=0.7,
        brightness_level=0.85,
        contrast_ratio=0.9,
        mood="professional"
    )
    
    # Educational typography
    edu_typography = Typography(
        primary_font_family="Poppins",
        secondary_font_family="Open Sans",
        title_size_ratio=0.08,
        body_size_ratio=0.045,
        font_weight="semi-bold",
        letter_spacing=1.1,
        line_height=1.6,
        has_shadow=True,
        has_outline=False,
        text_animation_style="slide"
    )
    
    # Educational composition
    edu_composition = Composition(
        rule_of_thirds_adherence=0.85,
        symmetry_score=0.8,
        primary_layout="presenter-focused",
        text_placement_zones=["lower-third", "side-panel", "top-banner"],
        margin_ratio=0.06,
        padding_ratio=0.03,
        focal_point_strategy="instructor-centered",
        depth_layers=4
    )
    
    # Educational motion style
    edu_motion = MotionStyle(
        camera_movement="stable",
        transition_style="slide",
        average_shot_duration=5.0,  # Longer shots for explanation
        movement_intensity=0.3,
        text_animation_type="slide",
        element_animation_style="fade-in",
        pacing="moderate",
        rhythm_pattern="educational"
    )
    
    # Create style reference
    edu_style = StyleReference(
        reference_id="style_youtube_educational",
        name="YouTube Educational Style",
        reference_type=ReferenceType.TEMPLATE,
        source_path=None,
        template_id="youtube_edu_template",
        color_palette=edu_colors,
        typography=edu_typography,
        composition=edu_composition,
        motion_style=edu_motion,
        visual_effects=[
            VisualEffect(
                effect_type="whiteboard",
                intensity=0.4,
                apply_to="background",
                parameters={"style": "clean"}
            ),
            VisualEffect(
                effect_type="highlight",
                intensity=0.6,
                apply_to="text",
                parameters={"color": "#FF9800", "animation": "pulse"}
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
        tags=["educational", "youtube", "learning", "tutorial"],
        description="Clean educational style for YouTube content",
        confidence_scores={"preset": 1.0}
    )
    
    # Create brand kit
    edu_brand = BrandKit(
        primary_logo="assets/logos/edu_channel_logo.png",
        primary_logo_dark="assets/logos/edu_channel_logo_dark.png",
        primary_logo_light="assets/logos/edu_channel_logo_light.png",
        color_primary="#2E7D32",
        color_secondary="#FFFFFF",
        color_accent="#FF9800",
        color_background="#FAFAFA",
        color_text_primary="#212121",
        color_text_secondary="#424242",
        fonts={
            "heading": "Poppins",
            "body": "Open Sans",
            "caption": "Roboto"
        },
        minimum_logo_size_percentage=5.0,
        clear_space_ratio=2.0
    )
    
    # Create intro template
    intro_template = VideoTemplate(
        template_id="edu_intro",
        duration=4.0,
        background_type="video",
        background_content="assets/templates/edu_intro_bg.mp4",
        title_text="LEARN WITH {CHANNEL_NAME}",
        subtitle_text="{TOPIC}",
        title_animation="zoom-slide",
        music_path="assets/audio/edu_intro.mp3",
        sound_effects=["chime", "swoosh"],
        fade_in_duration=0.3,
        fade_out_duration=0.4
    )
    
    # Create outro template
    outro_template = VideoTemplate(
        template_id="edu_outro",
        duration=5.0,
        background_type="gradient",
        background_content="#2E7D32,#1B5E20",
        title_text="THANKS FOR LEARNING!",
        subtitle_text="SUBSCRIBE FOR MORE TUTORIALS",
        title_animation="fade-zoom",
        music_path="assets/audio/edu_outro.mp3",
        sound_effects=["success-chime"],
        fade_in_duration=0.4,
        fade_out_duration=0.8
    )
    
    # Logo configuration
    logo_config = LogoConfiguration(
        logo_path="assets/logos/edu_channel_logo.png",
        position="top-right",
        size_percentage=7.0,
        opacity=0.85,
        always_visible=True,
        margin_percentage=2.0,
        entrance_animation="fade",
        exit_animation="fade"
    )
    
    # Lower thirds style (for presenter name/credentials)
    lower_thirds = LowerThirdsStyle(
        enabled=True,
        background_type="gradient",
        background_color_primary="#2E7D32",
        background_color_secondary="#1B5E20",
        background_opacity=0.9,
        title_font_size_ratio=0.055,
        subtitle_font_size_ratio=0.04,
        title_color="#FFFFFF",
        subtitle_color="#B2DFDB",
        entrance_animation="slide-up",
        exit_animation="slide-down",
        animation_duration=0.5,
        position_y_percentage=75.0,
        height_percentage=12.0,
        margin_x_percentage=4.0
    )
    
    # Caption style
    captions = CaptionStyle(
        font_family="Open Sans",
        font_size_ratio=0.042,
        font_color="#FFFFFF",
        font_weight="semi-bold",
        background_enabled=True,
        background_color="#000000",
        background_opacity=0.8,
        background_padding=14.0,
        shadow_enabled=True,
        shadow_color="#000000",
        shadow_offset=2.0,
        position_y_percentage=82.0,
        max_width_percentage=85.0
    )
    
    # Create theme
    theme = Theme(
        theme_id="youtube_educational",
        name="YouTube Educational",
        category=ThemeCategory.EDUCATION,
        version="1.0.0",
        style_reference=edu_style,
        brand_kit=edu_brand,
        intro_template=intro_template,
        outro_template=outro_template,
        transition_style=TransitionStyle.SLIDE,
        transition_duration=0.4,
        logo_config=logo_config,
        lower_thirds_style=lower_thirds,
        caption_style=captions,
        intro_music="assets/audio/edu_intro.mp3",
        outro_music="assets/audio/edu_outro.mp3",
        background_music_style="soft-educational",
        sound_effects_pack="educational-cues",
        content_tone="instructional",
        content_style="educational",
        target_audience="learners",
        default_duration=300,  # 5 minutes default for educational content
        default_aspect_ratio="16:9",
        default_resolution="1920x1080",
        default_frame_rate=30,
        description="Professional educational theme for YouTube tutorials and courses",
        tags=["educational", "youtube", "tutorial", "learning", "professional"],
        created_by="example"
    )
    
    return theme


if __name__ == "__main__":
    # Create and save the theme
    from src.themes.managers.theme_manager import ThemeManager
    
    theme_manager = ThemeManager()
    theme = create_youtube_educational_theme()
    theme_id = theme_manager.save_theme(theme)
    print(f"✅ Created YouTube educational theme: {theme_id}")