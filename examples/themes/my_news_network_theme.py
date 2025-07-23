"""
Custom News Network Theme with Consistent Anchors
"""

from src.themes.models.theme import (
    Theme, ThemeCategory, BrandKit, ColorScheme,
    Typography, TypographyStyle, TransitionStyle,
    AudioTheme, ContentTone, PlatformSettings,
    VideoTemplate, LowerThirdsStyle, CaptionStyle,
    EffectPreset, LogoConfiguration, VisualEffect
)

# Define your news network theme
MY_NEWS_NETWORK_THEME = Theme(
    id="my_news_network",
    name="My News Network",
    category=ThemeCategory.NEWS,
    description="Consistent news network with recurring anchors Sarah Chen and Michael Roberts",
    
    # Brand identity
    brand_kit=BrandKit(
        primary_logo=None,  # Add your network logo path here
        secondary_logo=None,
        color_primary="#003366",      # Deep navy blue
        color_secondary="#CC0000",    # Breaking news red
        color_accent="#FFFFFF",       # Clean white
        color_background="#F0F0F0",   # Light gray
        fonts={
            "heading": "Helvetica Neue Bold",
            "body": "Arial",
            "caption": "Helvetica Neue"
        }
    ),
    
    # Visual style
    color_scheme=ColorScheme(
        primary_colors=["#003366", "#CC0000", "#FFFFFF"],
        secondary_colors=["#666666", "#E0E0E0"],
        background_colors=["#FFFFFF", "#F0F0F0"],
        text_colors=["#000000", "#333333"],
        mood="professional"
    ),
    
    # Typography
    typography=Typography(
        heading_style=TypographyStyle(
            font_family="Helvetica Neue Bold",
            font_size=48,
            font_weight="bold",
            text_transform="uppercase",
            letter_spacing=1.2
        ),
        body_style=TypographyStyle(
            font_family="Arial",
            font_size=18,
            font_weight="normal",
            line_height=1.6
        ),
        caption_style=TypographyStyle(
            font_family="Helvetica Neue",
            font_size=14,
            font_weight="medium",
            text_transform="none"
        )
    ),
    
    # Content settings - THIS IS KEY FOR CONSISTENT ANCHORS
    content_tone=ContentTone(
        voice="professional",
        formality_level=0.9,
        energy_level=0.7,
        humor_level=0.0,
        # Custom metadata for anchor consistency
        custom_metadata={
            "primary_anchor": {
                "name": "Sarah Chen",
                "description": "Professional female news anchor, mid-30s, wearing navy blue suit, brown hair in professional style, confident demeanor",
                "voice": "en-US-News-F",  # Female news voice
                "position": "left"
            },
            "secondary_anchor": {
                "name": "Michael Roberts", 
                "description": "Professional male news anchor, early 40s, wearing dark gray suit with red tie, short dark hair, authoritative presence",
                "voice": "en-US-News-M",  # Male news voice
                "position": "right"
            },
            "studio_setting": "Modern news studio with large video wall showing world map, glass desk, professional lighting",
            "camera_angles": ["two-shot wide", "single medium shot", "over-shoulder"],
            "anchor_interaction": "Professional co-anchor dynamic with occasional brief exchanges"
        }
    ),
    
    # Visual effects
    visual_effects=[
        VisualEffect(
            effect_type="lower-third",
            intensity=1.0,
            apply_to="text",
            parameters={
                "style": "news-breaking",
                "animation": "slide-in",
                "duration": 0.5
            }
        ),
        VisualEffect(
            effect_type="background-blur",
            intensity=0.3,
            apply_to="background",
            parameters={
                "blur_amount": 5,
                "focus_area": "center"
            }
        )
    ],
    
    # Lower thirds for consistency
    lower_thirds_style=LowerThirdsStyle(
        background_color="#003366",
        text_color="#FFFFFF",
        font_family="Helvetica Neue Bold",
        animation_type="slide",
        position="bottom",
        height_percentage=15,
        opacity=0.95
    ),
    
    # Platform settings
    platform_settings={
        "youtube": PlatformSettings(
            optimal_duration=120,
            aspect_ratio="16:9",
            thumbnail_style="news-breaking",
            hashtag_style="news"
        ),
        "instagram": PlatformSettings(
            optimal_duration=60,
            aspect_ratio="9:16",
            thumbnail_style="news-alert",
            hashtag_style="breaking"
        )
    }
)

# Function to get the theme
def get_theme() -> Theme:
    return MY_NEWS_NETWORK_THEME

if __name__ == "__main__":
    theme = get_theme()
    print(f"Theme: {theme.name}")
    print(f"Anchors: {theme.content_tone.custom_metadata['primary_anchor']['name']} & {theme.content_tone.custom_metadata['secondary_anchor']['name']}")