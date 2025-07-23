# Migration Guide: v2.x to v3.0

## Overview

ViralAI v3.0 introduces powerful new features while maintaining backward compatibility. This guide helps you upgrade smoothly and take advantage of new capabilities.

## What's New

### Major Features
- **Style Reference System**: Extract and reuse visual styles
- **Theme System**: Consistent branding across videos
- **Enhanced Architecture**: Modular OOP design
- **Coming Soon**: Content scraping and media integration

### Breaking Changes
- None! v3.0 maintains full backward compatibility

## Installation

### 1. Update Dependencies

```bash
# Update to latest version
git pull origin main
git checkout v3.0.0-dev

# Install new dependencies
pip install -r requirements.txt
```

### 2. Initialize New Systems

```bash
# First run will create necessary directories
python main.py generate --mission "Test" --platform instagram --duration 10
```

## Using New Features

### Style References

#### Extract Style from Video
```bash
# Old way (no style reference)
python main.py generate --mission "Product demo" --visual-style cinematic

# New way (with style reference)
python main.py generate \
  --mission "Product demo" \
  --style-reference "/path/to/reference/video.mp4" \
  --save-style "Product Style 2024"
```

#### Reuse Saved Styles
```bash
# List available styles
python main.py list-styles

# Use saved style
python main.py generate \
  --mission "New product launch" \
  --style "Product Style 2024"
```

### Themes

#### Use Preset Themes
```bash
# Generate with news theme
python main.py generate \
  --mission "Breaking: Tech announcement" \
  --theme news_edition \
  --duration 60

# Available presets: news_edition, sports, tech, entertainment
```

#### Create Custom Themes
```python
# In your script
from src.themes import Theme, ThemeManager, BrandKit

# Create brand kit
brand = BrandKit(
    primary_logo="company_logo.png",
    color_primary="#FF6B00"
)

# Create theme
theme = Theme(
    name="Company Theme",
    brand_kit=brand
)

# Save theme
manager = ThemeManager()
theme_id = manager.save_theme(theme)
```

## API Changes

### Decision Framework

The DecisionFramework now supports style and theme decisions:

```python
# Old way
decisions = framework.make_all_decisions(
    mission="Create video",
    duration=30
)

# New way (with style/theme)
decisions = framework.make_all_decisions(
    mission="Create video",
    duration=30,
    style_reference_id="style_123",
    theme_id="preset_news"
)
```

### Session Management

Sessions now track theme information:

```python
# Old way
session = session_manager.create_session("My Session")

# New way (themed session)
themed_manager = ThemedSessionManager(theme_mgr, session_mgr)
session = themed_manager.create_themed_session("preset_sports")
```

## Configuration

### New Settings

Add to your `.env` or settings:

```bash
# Style Reference Settings
STYLE_LIBRARY_PATH=styles
MAX_STYLE_CACHE_SIZE=100

# Theme Settings  
THEMES_DIRECTORY=themes
ENABLE_THEME_PRESETS=true
```

## Best Practices

### 1. Gradual Adoption

You don't need to use all new features immediately:

```bash
# Phase 1: Continue using existing commands
python main.py generate --mission "Content" --visual-style dynamic

# Phase 2: Try style extraction
python main.py generate --mission "Content" --style-reference "ref.mp4"

# Phase 3: Adopt themes for consistency
python main.py generate --mission "Content" --theme news_edition
```

### 2. Style Library Management

Build your style library gradually:

```python
# Extract and save brand styles
analyzer = VideoStyleAnalyzer()
library = StyleLibrary()

# Analyze existing brand videos
for video in brand_videos:
    style = await analyzer.analyze_video(video, f"Brand Style {i}")
    library.save_style(style, f"Brand Style {i}")
```

### 3. Theme Migration

Convert existing brand guidelines to themes:

```python
# Create theme from brand guidelines
theme = Theme(
    name="2024 Brand Theme",
    brand_kit=BrandKit(
        primary_logo=existing_logo,
        color_primary=brand_colors["primary"]
    ),
    content_tone=brand_voice,
    default_duration=standard_duration
)
```

## Troubleshooting

### Common Issues

**Q: Style extraction fails on my video**
- Ensure video has clear visual elements
- Try with higher quality source
- Check video codec compatibility

**Q: Theme not applying correctly**
- Verify theme ID with `list-themes`
- Check theme category matches content
- Review override settings

**Q: Performance slower with new features**
- Style analysis is one-time (cached)
- Use `--cheap full` for testing
- Disable unused features

### Debug Mode

Enable detailed logging:

```bash
# Set environment variable
export VIRALAI_DEBUG=true

# Or in command
python main.py generate --mission "Test" --debug
```

## Rollback

If needed, v3.0 can be safely rolled back:

```bash
# Rollback to v2.x
git checkout v2.5.0-rc2

# Videos generated with v3.0 remain compatible
```

## Future Features

Prepare for upcoming features:

### Content Scraping (Coming Soon)
```bash
# Future syntax
python main.py generate \
  --mission "Summarize today's tech news" \
  --scrape-source "https://technews.com/rss" \
  --theme news_edition
```

### Media Integration (Coming Soon)
```bash
# Future syntax
python main.py generate \
  --mission "Product showcase" \
  --media-folder "/path/to/product/images" \
  --background-mode "scraped-media"
```

## Support

- **Documentation**: `/docs/API_REFERENCE_V3.md`
- **Examples**: `/examples/v3_features/`
- **Issues**: GitHub Issues with `v3.0` tag

## Summary

v3.0 is designed for seamless adoption:
1. No breaking changes - existing workflows continue working
2. New features are optional - adopt at your pace
3. Enhanced capabilities - better videos with less effort
4. Future-ready - architecture supports upcoming features

Start with style references for immediate visual improvements, then explore themes for brand consistency. The modular design ensures you can adopt features as needed without disrupting existing workflows.