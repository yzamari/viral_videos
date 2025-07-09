# 🎤 Subtitle Overlay Feature

## Overview

The subtitle overlay feature allows you to use audio-based subtitles instead of generic text overlays. This creates more accessible and informative videos by displaying the actual spoken content as subtitles.

## Features

- **Audio-Based Subtitles**: Uses the actual audio script content as subtitle text
- **Smart Timing**: Automatically segments and times subtitles based on audio duration
- **Intelligent Positioning**: Positions subtitles in the bottom third for readability
- **Accessibility**: Improves video accessibility for hearing-impaired viewers
- **Clean Styling**: Uses readable fonts with proper shadows and contrast

## Usage

### Basic Usage

```python
from models.video_models import GeneratedVideoConfig, Platform, VideoCategory

# Enable subtitle overlays
config = GeneratedVideoConfig(
    topic="Your video topic",
    duration_seconds=30,
    target_platform=Platform.INSTAGRAM,
    category=VideoCategory.EDUCATION,
    use_subtitle_overlays=True  # Enable subtitle overlays
)
```

### Comparison

| Feature | Regular Overlays | Subtitle Overlays |
|---------|------------------|-------------------|
| **Content** | Generic trendy text | Audio script content |
| **Positioning** | Various positions | Bottom third (subtitle style) |
| **Accessibility** | Limited | High (shows spoken content) |
| **Informativeness** | Entertainment focused | Educational/informative |
| **Timing** | Fixed intervals | Synced with audio segments |

## How It Works

1. **Script Analysis**: The system analyzes the audio script content
2. **Segmentation**: Breaks the script into subtitle-sized segments
3. **Timing Calculation**: Distributes segments across video duration
4. **Smart Positioning**: Places subtitles in readable positions
5. **Styling**: Applies clean, readable subtitle styling

## Configuration Options

```python
# Default behavior (generic overlays)
config = GeneratedVideoConfig(
    topic="Your topic",
    duration_seconds=30,
    target_platform=Platform.INSTAGRAM,
    category=VideoCategory.EDUCATION,
    use_subtitle_overlays=False  # Default
)

# Enable subtitle overlays
config = GeneratedVideoConfig(
    topic="Your topic",
    duration_seconds=30,
    target_platform=Platform.INSTAGRAM,
    category=VideoCategory.EDUCATION,
    use_subtitle_overlays=True  # Enable subtitles
)
```

## Examples

### Educational Content
Perfect for educational videos where viewers need to understand the exact content being discussed.

### Accessibility
Helps hearing-impaired viewers follow along with the video content.

### Multi-language Support
Works with all supported languages and automatically handles text direction (RTL for Arabic, Hebrew, etc.).

## Technical Details

- **Subtitle Segmentation**: Splits script by sentences, then by phrases if needed
- **Timing**: Ensures minimum 1.5s and maximum 4s display time per subtitle
- **Positioning**: Uses bottom third (75% of video height) for optimal readability
- **Styling**: White text with black stroke and subtle shadow for maximum contrast
- **Fallback**: If script is unavailable, falls back to regular overlays

## Benefits

1. **Improved Accessibility**: Makes videos accessible to hearing-impaired viewers
2. **Better Comprehension**: Viewers can read along with the audio
3. **Educational Value**: Perfect for instructional or informational content
4. **Professional Look**: Clean subtitle styling looks more professional
5. **Content Retention**: Helps viewers remember key points

## Best Practices

1. **Use for Educational Content**: Most effective for informational videos
2. **Clear Audio Scripts**: Ensure your audio script is well-written and clear
3. **Appropriate Duration**: Works best with 15-60 second videos
4. **Consider Platform**: Particularly effective on Instagram and TikTok
5. **Test Both Modes**: Compare regular vs subtitle overlays for your content

## Getting Started

1. Set `use_subtitle_overlays=True` in your `GeneratedVideoConfig`
2. Generate your video as usual
3. The system will automatically use audio-based subtitles instead of generic overlays
4. Review the generated video to see the subtitle styling and timing

The subtitle overlay feature enhances your videos with professional, accessible, and informative text overlays that actually match your audio content! 