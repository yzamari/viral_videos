#!/usr/bin/env python3
"""
VEO-3 Fast JSON Prompt Examples
Shows how to use structured JSON prompts for better video quality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.generators.json_prompt_system import (
    VEOJsonPrompt, CameraConfig, LightingConfig, SceneConfig, 
    SubjectConfig, EffectsConfig, SegmentConfig, JSONPromptTemplates,
    CameraMovement, ShotType, VisualStyle, LightingStyle, Platform
)

# Example 1: Viral Hook Video
def create_viral_hook_prompt():
    """Create a viral hook video prompt"""
    return VEOJsonPrompt(
        description="Mind-blowing fact about the human brain with neurons firing",
        style=VisualStyle.VIBRANT,
        duration=3.0,
        platform=Platform.TIKTOK,
        aspect_ratio="9:16",
        
        camera=CameraConfig(
            shot_type=ShotType.EXTREME_CLOSE,
            movement=CameraMovement.ZOOM_IN,
            speed="fast",
            lens="100mm macro"
        ),
        
        lighting=LightingConfig(
            style=LightingStyle.NEON,
            mood="energetic and mysterious",
            color_temperature="cool blue with purple accents"
        ),
        
        effects=EffectsConfig(
            color_grading="high contrast neon glow",
            lens_flare=True,
            particles="electric sparks"
        ),
        
        keywords=["viral", "brain", "neurons", "science", "amazing"],
        constraints=["no text overlays", "smooth zoom", "electric feel"]
    )

# Example 2: Educational Content
def create_educational_prompt():
    """Create an educational video prompt"""
    return VEOJsonPrompt(
        description="Explaining photosynthesis process in plants",
        style=VisualStyle.DOCUMENTARY,
        duration=15.0,
        platform=Platform.YOUTUBE,
        aspect_ratio="16:9",
        
        segments=[
            SegmentConfig(
                duration=5.0,
                description="Sunlight hitting green leaves",
                camera=CameraConfig(
                    shot_type=ShotType.WIDE,
                    movement=CameraMovement.DOLLY_IN,
                    lens="35mm"
                ),
                scene=SceneConfig(
                    location="lush garden",
                    time_of_day="morning",
                    weather="sunny"
                )
            ),
            SegmentConfig(
                duration=5.0,
                description="Close-up of leaf cells and chloroplasts",
                camera=CameraConfig(
                    shot_type=ShotType.EXTREME_CLOSE,
                    movement=CameraMovement.STATIC,
                    lens="100mm macro"
                )
            ),
            SegmentConfig(
                duration=5.0,
                description="Animated visualization of chemical process",
                camera=CameraConfig(
                    shot_type=ShotType.MEDIUM,
                    movement=CameraMovement.ORBIT
                )
            )
        ],
        
        lighting=LightingConfig(
            style=LightingStyle.NATURAL,
            mood="bright and clear"
        ),
        
        keywords=["education", "science", "photosynthesis", "plants"],
        constraints=["clear visuals", "no distracting elements", "scientific accuracy"]
    )

# Example 3: Product Showcase
def create_product_showcase_prompt():
    """Create a product showcase video prompt"""
    return JSONPromptTemplates.product_reveal(
        product_name="Premium Headphones",
        brand="TechBrand",
        duration=10.0
    )

# Example 4: Comedy Skit
def create_comedy_prompt():
    """Create a comedy video prompt"""
    return VEOJsonPrompt(
        description="Office worker discovers their plant is secretly a ninja",
        style=VisualStyle.CARTOON,
        duration=15.0,
        platform=Platform.INSTAGRAM,
        aspect_ratio="9:16",
        
        segments=[
            SegmentConfig(
                duration=5.0,
                description="Boring office scene with wilting plant",
                camera=CameraConfig(
                    shot_type=ShotType.MEDIUM,
                    movement=CameraMovement.STATIC
                ),
                subject=SubjectConfig(
                    description="tired office worker",
                    action="typing on computer",
                    expression="bored"
                )
            ),
            SegmentConfig(
                duration=5.0,
                description="Plant suddenly does a backflip",
                camera=CameraConfig(
                    shot_type=ShotType.CLOSE,
                    movement=CameraMovement.HANDHELD,
                    speed="fast"
                )
            ),
            SegmentConfig(
                duration=5.0,
                description="Epic ninja battle between plant and staplers",
                camera=CameraConfig(
                    shot_type=ShotType.WIDE,
                    movement=CameraMovement.TRACKING,
                    speed="very fast"
                ),
                effects=EffectsConfig(
                    particles="paper confetti",
                    film_grain="action movie style"
                )
            )
        ],
        
        keywords=["comedy", "office", "ninja", "plant", "funny"],
        constraints=["family-friendly", "exaggerated movements", "comedic timing"]
    )

# Example 5: Travel/Lifestyle
def create_travel_prompt():
    """Create a travel video prompt"""
    return VEOJsonPrompt(
        description="Breathtaking sunrise hike to mountain summit",
        style=VisualStyle.CINEMATIC,
        duration=20.0,
        platform=Platform.YOUTUBE,
        aspect_ratio="16:9",
        
        camera=CameraConfig(
            shot_type=ShotType.WIDE,
            movement=CameraMovement.DRONE,
            lens="24mm",
            frame_rate="60fps"  # For smooth motion
        ),
        
        lighting=LightingConfig(
            style=LightingStyle.GOLDEN_HOUR,
            mood="inspirational and majestic"
        ),
        
        scene=SceneConfig(
            location="mountain trail",
            time_of_day="dawn to sunrise",
            weather="clear with morning mist",
            environment_details="rocky path, alpine meadows, snow-capped peaks"
        ),
        
        effects=EffectsConfig(
            color_grading="warm sunrise tones",
            lens_flare=True,
            film_grain="subtle cinematic"
        ),
        
        keywords=["travel", "adventure", "mountains", "sunrise", "hiking"],
        constraints=["steady footage", "epic scale", "natural beauty"]
    )

# Example usage in main code
if __name__ == "__main__":
    # Print examples
    prompts = {
        "Viral Hook": create_viral_hook_prompt(),
        "Educational": create_educational_prompt(),
        "Product": create_product_showcase_prompt(),
        "Comedy": create_comedy_prompt(),
        "Travel": create_travel_prompt()
    }
    
    for name, prompt in prompts.items():
        print(f"\n{'='*50}")
        print(f"{name} Prompt:")
        print(f"{'='*50}")
        print(prompt.to_json()[:500] + "...")
    
    print("\n✨ JSON prompts provide precise control over:")
    print("   - Camera angles, movements, and lenses")
    print("   - Lighting styles and moods")
    print("   - Scene composition and environment")
    print("   - Visual effects and color grading")
    print("   - Multi-segment sequences with transitions")
    print("   - Platform-specific optimizations")