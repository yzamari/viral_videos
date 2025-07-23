# ViralAI Configuration Guide

## Overview

ViralAI v3.0 introduces a comprehensive configuration system that eliminates ALL hardcoded values throughout the codebase. Every aspect of video generation is now fully configurable through a centralized system located at `src/config/video_config.py`.

## Quick Start

```python
from src.config.video_config import video_config

# Access the global configuration instance
fps = video_config.get_fps('youtube')  # Get platform-specific FPS
font_size = video_config.get_font_size('title', 1920)  # Calculate font size
```

## Configuration Structure

The configuration system is organized into five main categories:

### 1. Video Encoding Configuration (`VideoEncodingConfig`)

Controls all video encoding parameters:

```python
@dataclass
class VideoEncodingConfig:
    # Frame rates by platform
    fps_by_platform: Dict[str, int] = {
        'youtube': 30,
        'tiktok': 30,
        'instagram': 30,
        'facebook': 30,
        'twitter': 30,
        'linkedin': 30,
        'default': 30
    }
    
    # Video codec settings
    video_codec: str = 'libx264'
    audio_codec: str = 'aac'
    pixel_format: str = 'yuv420p'
    
    # Quality presets by platform
    encoding_presets: Dict[str, str] = {
        'youtube': 'medium',      # Better quality for YouTube
        'tiktok': 'fast',        # Faster encoding for short videos
        'instagram': 'fast',     
        'default': 'medium'
    }
    
    # CRF (Constant Rate Factor) - lower = better quality
    crf_by_platform: Dict[str, int] = {
        'youtube': 23,          # Good quality
        'tiktok': 25,          # Slightly lower quality
        'instagram': 25,
        'default': 23
    }
```

**Customization Examples:**

```python
# Increase quality for YouTube
video_config.encoding.crf_by_platform['youtube'] = 20  # Better quality

# Change to 60fps for smoother videos
video_config.encoding.fps_by_platform['tiktok'] = 60

# Use faster encoding for all platforms
for platform in video_config.encoding.encoding_presets:
    video_config.encoding.encoding_presets[platform] = 'veryfast'
```

### 2. Text Overlay Configuration (`TextOverlayConfig`)

Controls all text styling parameters:

```python
@dataclass
class TextOverlayConfig:
    # Font settings
    default_font: str = 'Arial-Bold'
    
    # Font sizes (relative to video width)
    font_sizes: Dict[str, float] = {
        'title': 0.06,          # 6% of video width
        'subtitle': 0.044,      # 4.4% of video width
        'header': 0.05,         # 5% of video width
        'body': 0.04,           # 4% of video width
        'caption': 0.035,       # 3.5% of video width
        'badge': 0.03,          # 3% of video width
        'news_ticker': 0.025,   # 2.5% of video width
    }
    
    # Minimum font sizes (absolute pixels)
    min_font_sizes: Dict[str, int] = {
        'title': 48,
        'subtitle': 44,
        'header': 40,
        'body': 32,
        'caption': 28,
        'badge': 24,
        'news_ticker': 20,
    }
    
    # Colors and opacity
    default_text_color: str = 'white'
    default_stroke_color: str = 'black'
    default_opacity: float = 1.0
    background_opacity: float = 0.8
```

**Customization Examples:**

```python
# Change to your brand colors
video_config.text_overlay.default_text_color = '#FF6B6B'
video_config.text_overlay.default_stroke_color = '#2D3436'

# Increase title size for better visibility
video_config.text_overlay.font_sizes['title'] = 0.08  # 8% of width

# Make backgrounds more transparent
video_config.text_overlay.background_opacity = 0.6

# Use a custom font
video_config.text_overlay.default_font = 'Montserrat-Bold'
```

### 3. Animation Timing Configuration (`AnimationTimingConfig`)

Controls all animation and timing parameters:

```python
@dataclass
class AnimationTimingConfig:
    # Fade settings
    fade_in_duration: float = 0.5
    fade_out_duration: float = 0.5
    
    # Display durations
    hook_display_duration: float = 3.0
    cta_display_duration: float = 3.0
    
    # Animation timing
    subtitle_fade_duration: float = 0.2
    overlay_fade_duration: float = 0.3
    
    # Transition settings
    default_transition_duration: float = 0.5
    crossfade_duration: float = 1.0
    
    # Continuity settings
    frame_continuity_trim_frames: int = 1
    frame_continuity_blend_frames: int = 2
```

**Customization Examples:**

```python
# Faster animations for TikTok-style content
video_config.animation.fade_in_duration = 0.2
video_config.animation.fade_out_duration = 0.2

# Longer hook display for complex messages
video_config.animation.hook_display_duration = 5.0

# Smoother transitions
video_config.animation.crossfade_duration = 2.0
```

### 4. Default Text Configuration (`DefaultTextConfig`)

Controls platform-specific default texts:

```python
@dataclass
class DefaultTextConfig:
    # Platform-specific hooks
    hooks_by_platform: Dict[str, str] = {
        'youtube': "Discover something amazing!",
        'tiktok': "Wait for it...",
        'instagram': "You won't believe this!",
        'facebook': "Check this out!",
        'twitter': "Thread below 👇",
        'linkedin': "Key insights ahead",
    }
    
    # Platform-specific CTAs
    ctas_by_platform: Dict[str, str] = {
        'youtube': "Subscribe for more!",
        'tiktok': "Follow for more!",
        'instagram': "Follow for daily content!",
        'facebook': "Like and share!",
        'twitter': "Retweet if you agree!",
        'linkedin': "Connect for insights!",
    }
    
    # Badge texts
    badge_texts: Dict[str, str] = {
        'cheap': "💰 CHEAP",
        'premium': "✨ PREMIUM",
        'veo2': "🎬 VEO-2",
        'veo3': "🎬 VEO-3",
        'ai': "🤖 AI",
        'news': "📰 NEWS",
        'breaking': "🚨 BREAKING"
    }
```

**Customization Examples:**

```python
# Customize for your brand
video_config.default_text.hooks_by_platform['youtube'] = "🚀 Get ready to learn!"
video_config.default_text.ctas_by_platform['instagram'] = "Tap follow for daily tips! 💡"

# Add custom badges
video_config.default_text.badge_texts['exclusive'] = "🔥 EXCLUSIVE"
video_config.default_text.badge_texts['sponsored'] = "💼 SPONSORED"

# Localize for different languages
video_config.default_text.hooks_by_platform['youtube'] = "¡Descubre algo increíble!"
```

### 5. Layout Configuration (`LayoutConfig`)

Controls positioning and layout:

```python
@dataclass
class LayoutConfig:
    # Subtitle positioning (from bottom)
    subtitle_bottom_offset: Dict[str, int] = {
        'default': 150,
        'news': 250,           # Higher to avoid news ticker
        'minimal': 100,
        'centered': 200
    }
    
    # Overlay positioning
    overlay_positions: Dict[str, Dict[str, Any]] = {
        'hook': {
            'x': 'center',
            'y': 60,
            'animation': 'slide_in'
        },
        'cta': {
            'x': 'right-30',
            'y': 120,
            'animation': 'slide_in'
        },
        'badge': {
            'x': 50,
            'y': 150,
            'animation': 'fade'
        }
    }
    
    # Spacing
    overlay_vertical_spacing: int = 80
    overlay_horizontal_padding: int = 30
    
    # Safe zones (percentage of video dimensions)
    safe_zone_percentage: float = 0.05  # 5% margin
```

**Customization Examples:**

```python
# Move subtitles higher for mobile viewing
video_config.layout.subtitle_bottom_offset['default'] = 200

# Center the CTA
video_config.layout.overlay_positions['cta']['x'] = 'center'
video_config.layout.overlay_positions['cta']['y'] = 100

# Increase safe zones for TV display
video_config.layout.safe_zone_percentage = 0.10  # 10% margins
```

## Advanced Configuration

### Creating Custom Configurations

You can create custom configuration instances for different use cases:

```python
from src.config.video_config import VideoGenerationConfig, VideoEncodingConfig

# Create a high-quality configuration
hq_config = VideoGenerationConfig()
hq_config.encoding.crf_by_platform = {platform: 18 for platform in hq_config.encoding.crf_by_platform}
hq_config.encoding.encoding_presets = {platform: 'slow' for platform in hq_config.encoding.encoding_presets}

# Create a fast configuration for testing
fast_config = VideoGenerationConfig()
fast_config.encoding.encoding_presets = {platform: 'ultrafast' for platform in fast_config.encoding.encoding_presets}
fast_config.animation.fade_in_duration = 0.1
fast_config.animation.fade_out_duration = 0.1
```

### Platform-Specific Configurations

The configuration system is platform-aware and automatically applies optimal settings:

```python
# Get platform-specific values
fps = video_config.get_fps('youtube')  # Returns 30
crf = video_config.get_crf('tiktok')   # Returns 25
preset = video_config.get_encoding_preset('instagram')  # Returns 'fast'

# Get dynamic font size based on video dimensions
title_size = video_config.get_font_size('title', 1920)  # Returns 115px for 1920 width
body_size = video_config.get_font_size('body', 1080)   # Returns 43px for 1080 width
```

### Theme-Aware Configuration

The system supports theme-specific configurations:

```python
# Get subtitle offset based on theme
news_offset = video_config.get_subtitle_offset('news')  # Returns 250 (higher for ticker)
default_offset = video_config.get_subtitle_offset()     # Returns 150

# Configure for specific themes
if theme == 'preset_news_edition':
    video_config.layout.subtitle_bottom_offset['current'] = 300
    video_config.text_overlay.font_sizes['news_ticker'] = 0.03
```

## Best Practices

### 1. Don't Hardcode Values

Instead of:
```python
# BAD - Hardcoded values
font_size = 48
fps = 30
```

Use:
```python
# GOOD - Configuration-based
font_size = video_config.get_font_size('title', video_width)
fps = video_config.get_fps(platform)
```

### 2. Use Platform-Aware Methods

```python
# Get platform-specific settings automatically
def setup_encoding(platform: str):
    fps = video_config.get_fps(platform)
    crf = video_config.get_crf(platform)
    preset = video_config.get_encoding_preset(platform)
    return fps, crf, preset
```

### 3. Create Configuration Profiles

```python
# Save common configurations
BRAND_CONFIG = {
    'text_color': '#FF6B6B',
    'stroke_color': '#2D3436',
    'font': 'Montserrat-Bold',
    'hook': 'Discover our amazing content!',
    'cta': 'Follow us for more!'
}

def apply_brand_config():
    video_config.text_overlay.default_text_color = BRAND_CONFIG['text_color']
    video_config.text_overlay.default_stroke_color = BRAND_CONFIG['stroke_color']
    video_config.text_overlay.default_font = BRAND_CONFIG['font']
    # ... apply other settings
```

### 4. Validate Configuration Changes

```python
def validate_config():
    # Ensure minimum values
    for platform, fps in video_config.encoding.fps_by_platform.items():
        assert fps >= 24, f"FPS too low for {platform}: {fps}"
    
    # Ensure font sizes are reasonable
    for text_type, size in video_config.text_overlay.font_sizes.items():
        assert 0.01 <= size <= 0.2, f"Font size out of range for {text_type}: {size}"
```

## Configuration Loading

The system uses a global configuration instance that can be modified at runtime:

```python
from src.config.video_config import video_config

# Modify global configuration
video_config.encoding.fps_by_platform['youtube'] = 60

# Or import specific configs
from src.config.video_config import VideoEncodingConfig, TextOverlayConfig

# Create custom instances
custom_encoding = VideoEncodingConfig()
custom_encoding.video_codec = 'libx265'  # Use H.265
```

## Migration Guide

If you're updating from a previous version with hardcoded values:

1. **Replace hardcoded FPS:**
   ```python
   # Old
   fps = 30
   
   # New
   fps = video_config.get_fps(platform)
   ```

2. **Replace hardcoded dimensions:**
   ```python
   # Old
   width, height = 1920, 1080
   
   # New (handled by PlatformDimensions class)
   dimensions = PlatformDimensions.get_dimensions(platform)
   ```

3. **Replace hardcoded font sizes:**
   ```python
   # Old
   font_size = 48
   
   # New
   font_size = video_config.get_font_size('title', video_width)
   ```

4. **Replace hardcoded text:**
   ```python
   # Old
   hook = "Check this out!"
   
   # New
   hook = video_config.get_default_hook(platform)
   ```

## Troubleshooting

### Common Issues

1. **Font not found:**
   - Ensure the font specified in `default_font` is installed on your system
   - Use fallback fonts: 'Arial-Bold', 'Helvetica-Bold'

2. **Configuration not applying:**
   - Make sure you're modifying the global `video_config` instance
   - Import from the correct location: `from src.config.video_config import video_config`

3. **Platform-specific settings not working:**
   - Verify the platform name matches exactly (lowercase)
   - Check that the platform exists in the configuration dictionaries

### Debugging Configuration

```python
# Print current configuration
def debug_config():
    print(f"FPS Settings: {video_config.encoding.fps_by_platform}")
    print(f"Font Sizes: {video_config.text_overlay.font_sizes}")
    print(f"Default Hooks: {video_config.default_text.hooks_by_platform}")
    
# Test configuration methods
def test_config():
    platforms = ['youtube', 'tiktok', 'instagram']
    for platform in platforms:
        fps = video_config.get_fps(platform)
        crf = video_config.get_crf(platform)
        hook = video_config.get_default_hook(platform)
        print(f"{platform}: FPS={fps}, CRF={crf}, Hook='{hook}'")
```

## Summary

The ViralAI configuration system provides complete control over every aspect of video generation without requiring code changes. By centralizing all parameters in `src/config/video_config.py`, the system ensures consistency, maintainability, and easy customization for different use cases and brands.

Remember: If you find yourself hardcoding any value related to video generation, it should probably be added to the configuration system instead!