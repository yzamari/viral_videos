#!/bin/bash

# Papaya Bar Ad - Studio Ghibli Style (Hebrew Version)
# 40 seconds duration
# Hebrew audio and subtitles

# Set environment
cd "$(dirname "$0")"

# Configuration
DURATION=40
STYLE="studio ghibli"
THEME="whimsical"
PLATFORM="instagram"
LANGUAGE="he"  # Hebrew

# Create mission for Papaya Bar ad in Hebrew
MISSION="Create a dreamy Studio Ghibli-style advertisement for The Papaya Bar in Rosh HaAyin, Israel. 
The ad should showcase their natural shakes, fresh juices, and healthy menu options during the day, 
and their unique alcohol-shake bar concept at night. Use whimsical Ghibli-style animation with 
soft colors, magical elements, and charming characters enjoying the drinks. Include the business 
details: Shabazi 47, Rosh HaAyin, Israel, Phone: 054-222-2617, Always Open. 
Make it feel like a magical oasis where healthy meets delicious. 
Target audience: health-conscious young adults and families in Israel."

# Run the video generation with Hebrew language
echo "🎬 Generating Papaya Bar ad in Studio Ghibli style (Hebrew)..."
python3 main.py generate \
    --mission "$MISSION" \
    --style "$STYLE" \
    --theme "$THEME" \
    --duration $DURATION \
    --platform "$PLATFORM" \
    --languages "$LANGUAGE" \
    --character "papaya_fruit_character" \
    --tone "whimsical" \
    --visual-style "soft pastel ghibli magical" \
    --target-audience "health-conscious israeli families" \
    --business-name "The Papaya Bar" \
    --business-address "שבזי 47, ראש העין" \
    --business-phone "054-222-2617" \
    --business-website "thepapayabar.com" \
    --business-facebook "thepapayabar" \
    --business-instagram "@thepapayabar" \
    --show-business-info \
    --session-id "papaya_ghibli_hebrew_$(date +%Y%m%d_%H%M%S)" \
    --no-cheap \
    --mode enhanced

echo "✅ Papaya Bar Ghibli-style Hebrew ad generation complete!"