# VEO-3 Fast JSON Prompt Guide

## Overview

VEO-3 Fast now supports structured JSON prompts, providing precise control over video generation for improved quality and consistency. JSON prompts allow you to specify camera movements, lighting, scene composition, and visual effects in a structured format.

## Benefits of JSON Prompts

1. **Better Video Quality**: More detailed instructions lead to higher quality outputs
2. **Consistency**: Structured format ensures consistent results across generations
3. **Fine Control**: Specify exact camera angles, movements, and visual styles
4. **Multi-Segment Support**: Create complex sequences with different shots
5. **Platform Optimization**: Automatic adjustments for different social media platforms

## Quick Start

### Basic Example

```python
from src.generators.json_prompt_system import VEOJsonPrompt, CameraConfig, ShotType, VisualStyle

# Create a JSON prompt
json_prompt = VEOJsonPrompt(
    description="A cat playing with a laser pointer",
    style=VisualStyle.VIBRANT,
    duration=5.0,
    camera=CameraConfig(
        shot_type=ShotType.MEDIUM,
        movement=CameraMovement.TRACKING
    )
)

# Use with VEO-3 Fast
video_path = veo_client.generate_video(
    prompt=json_prompt,  # Pass JSON prompt instead of string
    duration=5.0,
    clip_id="cat_video"
)
```

## JSON Prompt Structure

### Core Fields

- `description` (required): Main description of the video content
- `style` (required): Visual style (cinematic, cartoon, vibrant, etc.)
- `duration` (required): Video duration in seconds
- `platform`: Target platform (instagram, tiktok, youtube)
- `aspect_ratio`: Video aspect ratio (9:16, 16:9, 1:1)

### Camera Configuration

```python
camera=CameraConfig(
    shot_type=ShotType.CLOSE,        # wide, medium, close, extreme_close
    movement=CameraMovement.DOLLY_IN, # static, pan, tilt, zoom, tracking
    lens="85mm",                     # 24mm, 35mm, 50mm, 85mm, 100mm
    aperture="f/1.8",               # f/1.4 to f/22
    frame_rate="24fps",             # 24fps, 30fps, 60fps
    speed="normal"                  # slow, normal, fast
)
```

### Lighting Configuration

```python
lighting=LightingConfig(
    style=LightingStyle.GOLDEN_HOUR,  # natural, studio, neon, golden_hour
    mood="warm and inviting",         # descriptive mood
    key_light="soft sunlight",        # main light source
    fill_light="reflector",           # secondary light
    color_temperature="warm"          # cool, neutral, warm
)
```

### Scene Configuration

```python
scene=SceneConfig(
    location="modern kitchen",
    time_of_day="morning",
    weather="sunny",
    environment_details="minimalist design with marble counters",
    props=["coffee maker", "fresh flowers", "laptop"]
)
```

### Effects Configuration

```python
effects=EffectsConfig(
    color_grading="warm and saturated",
    film_grain="subtle",
    lens_flare=True,
    particles="dust motes in sunlight"
)
```

## Multi-Segment Videos

Create complex sequences with multiple shots:

```python
json_prompt = VEOJsonPrompt(
    description="Day in the life of a developer",
    style=VisualStyle.DOCUMENTARY,
    duration=15.0,
    segments=[
        SegmentConfig(
            duration=5.0,
            description="Morning coffee routine",
            camera=CameraConfig(shot_type=ShotType.CLOSE),
            scene=SceneConfig(location="kitchen", time_of_day="morning")
        ),
        SegmentConfig(
            duration=5.0,
            description="Coding at desk",
            camera=CameraConfig(shot_type=ShotType.MEDIUM),
            scene=SceneConfig(location="home office")
        ),
        SegmentConfig(
            duration=5.0,
            description="Evening relaxation",
            camera=CameraConfig(shot_type=ShotType.WIDE),
            scene=SceneConfig(location="living room", time_of_day="evening")
        )
    ]
)
```

## Pre-built Templates

Use templates for common scenarios:

```python
from src.generators.json_prompt_system import JSONPromptTemplates

# Product reveal
prompt = JSONPromptTemplates.product_reveal(
    product_name="Smart Watch",
    brand="TechCo",
    duration=10.0
)

# Educational content
prompt = JSONPromptTemplates.educational(
    topic="Solar System",
    duration=30.0
)

# Viral hook
prompt = JSONPromptTemplates.viral_hook(
    hook_text="You won't believe this!",
    platform=Platform.TIKTOK
)
```

## Best Practices

1. **Be Specific**: More detailed prompts produce better results
2. **Use Appropriate Styles**: Match visual style to content type
3. **Consider Platform**: Use platform-specific aspect ratios and durations
4. **Test Variations**: Try different camera movements and angles
5. **Combine Elements**: Mix camera, lighting, and effects for unique looks

## Integration with Main System

The video generator automatically detects JSON prompts:

```python
# In your video generation code
if isinstance(prompt, VEOJsonPrompt):
    # JSON prompt is automatically handled
    video = veo_client.generate_video(prompt=prompt, ...)
else:
    # String prompt works as before
    video = veo_client.generate_video(prompt="simple text prompt", ...)
```

## Performance Notes

- JSON prompts are converted to optimized text prompts internally
- No performance penalty compared to text prompts
- VEO-3 Fast remains the fastest and most cost-effective option
- Generation time: ~90-120 seconds per video
- Cost: ~$0.05 per second (10x cheaper than VEO-2)

## Examples

See `/examples/veo3_json_prompt_examples.py` for complete examples including:
- Viral hooks
- Educational content
- Product showcases
- Comedy skits
- Travel videos

## Troubleshooting

1. **Validation Errors**: Use `JSONPromptValidator.validate()` to check prompts
2. **Duration Limits**: VEO-3 Fast supports up to 8 seconds per clip
3. **Aspect Ratios**: Stick to standard ratios (16:9, 9:16, 1:1)
4. **Complex Scenes**: Break into multiple segments for better results