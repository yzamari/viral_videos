# Weather Graphics Generator Example

This is an **example** of how to create custom graphics for your videos. These tools are not part of the core ViralAI system.

## What's Included

- `weather_graphics_generator.py` - Example class for creating weather maps and overlays
- `create_weather_graphics.py` - Script to generate sample weather graphics

## Usage

1. **Generate Graphics** (optional):
   ```bash
   cd examples/weather_graphics
   python create_weather_graphics.py
   ```

2. **Reference in Video Generation**:
   ```bash
   python main.py generate \
     --mission "Show weather map from assets/iran_comedy_graphics/weather/nuclear_heat_map.png..."
   ```

## Important Notes

- This is an **example** only - not integrated into the main video pipeline
- Graphics must be created **before** video generation
- The AI may or may not use referenced PNG files
- For production use, consider professional graphics tools

## Creating Your Own Graphics

You can:
1. Use this example as a template
2. Create graphics with any image editing software
3. Generate graphics programmatically
4. Use online tools or APIs

The main requirement is that graphics should be PNG format with transparency for overlays.