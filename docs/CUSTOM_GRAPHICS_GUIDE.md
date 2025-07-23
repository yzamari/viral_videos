# Custom Graphics Guide for ViralAI

## Overview
This guide explains how to add custom graphics (weather maps, charts, overlays) to your videos.

## Methods for Custom Graphics

### 1. Static Image Overlays
Create PNG images with transparency and reference them in your theme or session.

**Example Weather Map Creation:**
```bash
# Create a weather map directory
mkdir -p assets/weather_maps/

# Place your custom weather map PNGs here:
# - assets/weather_maps/iran_heat_map.png
# - assets/weather_maps/nuclear_symbols.png
# - assets/weather_maps/water_shortage_icons.png
```

### 2. Dynamic Overlay System
Add custom overlays through the theme configuration:

```python
# In your theme configuration
self.weather_overlays = {
    "heat_map": {
        "image": "assets/weather_maps/iran_heat_map.png",
        "position": "center",
        "size_percentage": 80,
        "opacity": 0.9,
        "animation": "fade-in"
    },
    "nuclear_icons": {
        "image": "assets/weather_maps/nuclear_symbols.png",
        "position": "overlay",
        "opacity": 0.7
    }
}
```

### 3. Custom Graphics in Mission Prompt
Reference specific graphics files in your mission:

```bash
--mission "Show weather report with custom graphics from assets/weather_maps/iran_heat_map.png showing temperatures, overlay nuclear symbols from assets/weather_maps/nuclear_icons.png on Tehran..."
```

### 4. Theme-Based Graphics System
Extend the theme system to include custom graphics:

```python
# In src/themes/models/theme.py
@dataclass
class CustomGraphics:
    """Custom graphics configuration"""
    weather_maps: Dict[str, str]  # weather type -> image path
    charts: Dict[str, str]  # chart type -> image path
    icons: Dict[str, str]  # icon type -> image path
    overlays: Dict[str, str]  # overlay type -> image path
```

### 5. Session-Specific Graphics
For one-off graphics, place them in your session directory:

```bash
# Before running generation
mkdir -p outputs/session_weather_special/graphics/
cp my_custom_weather_map.png outputs/session_weather_special/graphics/

# In your command
--mission "Use the custom weather map from session graphics folder..."
```

## Creating Weather Graphics

### Option 1: Manual Creation
1. Use image editing software (Photoshop, GIMP, etc.)
2. Create PNG with transparency
3. Save to appropriate directory
4. Reference in theme or mission

### Option 2: Programmatic Generation
Create a weather graphics generator:

```python
# src/generators/weather_graphics_generator.py
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw

class WeatherGraphicsGenerator:
    def create_heat_map(self, data, output_path):
        """Create heat map for weather"""
        # Implementation here
        
    def create_nuclear_overlay(self, locations, output_path):
        """Create nuclear symbol overlay"""
        # Implementation here
```

### Option 3: Template System
Create reusable weather templates:

```bash
assets/
  weather_templates/
    heat_map_template.svg
    precipitation_template.svg
    nuclear_warning_template.svg
```

## Best Practices

1. **File Formats**
   - Use PNG for overlays (supports transparency)
   - Use SVG for scalable graphics
   - Keep file sizes reasonable

2. **Naming Convention**
   - Use descriptive names: `iran_heat_map_celsius.png`
   - Include date/version: `weather_map_2024_01.png`
   - Group by type: `maps/`, `icons/`, `charts/`

3. **Resolution**
   - Create at 1920x1080 for HD videos
   - Create at higher resolution for 4K
   - Always test at target resolution

4. **Transparency**
   - Use alpha channel for overlays
   - Test opacity levels
   - Consider video background colors

## Implementation Example

To use custom weather graphics in your Iranian comedy series:

```bash
# 1. Create graphics directory
mkdir -p assets/iran_comedy_graphics/weather/

# 2. Add your custom graphics
# - nuclear_heat_map.png
# - water_crisis_icons.png
# - comedy_weather_symbols.png

# 3. Update your generation command
python main.py generate \
  --mission "Show weather map using assets/iran_comedy_graphics/weather/nuclear_heat_map.png with comedy icons from water_crisis_icons.png..." \
  --custom-graphics-dir "assets/iran_comedy_graphics/weather/" \
  ...
```

## Future Enhancements

1. **Graphics API Integration**
   - Weather API for real data
   - Chart generation services
   - Map rendering services

2. **Template Engine**
   - Dynamic text on graphics
   - Data-driven visualizations
   - Animated graphics support

3. **Graphics Library**
   - Pre-made weather icons
   - Map templates
   - Chart styles

This system gives you full control over custom graphics while maintaining flexibility for AI-generated content.