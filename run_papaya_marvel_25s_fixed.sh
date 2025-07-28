#!/bin/bash

# Papaya Bar Marvel Comics Style Ad - FIXED VERSION
# 25 seconds duration with proper error handling

cd "$(dirname "$0")"

# Configuration
DURATION=25
STYLE="marvel comics"
THEME="superhero"
PLATFORM="instagram"
LANGUAGE="he"

# Enhanced mission with clear business focus
MISSION="Create an exciting Marvel Comics-style advertisement for The Papaya Bar in Rosh HaAyin, Israel. 
Show heroic characters enjoying healthy smoothies and shakes that give them superpowers during the day, 
and powerful alcohol shakes that fuel their nighttime adventures. Use bold comic book visuals with 
dynamic action scenes and colorful panels. The business offers natural shakes, fresh juices, 
and healthy options during the day, transforming into an alcohol-shake bar at night. 
Business details: The Papaya Bar, Shabazi 47, Rosh HaAyin, Israel, Phone: 054-222-2617, Always Open.
Target: Young Israeli adults who love comics and healthy lifestyle."

echo "🦸 Generating Papaya Bar Marvel Comics ad (FIXED VERSION)..."
echo "📍 Business: The Papaya Bar, Shabazi 47, Rosh HaAyin"
echo "⏱️  Duration: ${DURATION}s | Platform: ${PLATFORM} | Language: Hebrew"

# Run with comprehensive logging and error recovery
python3 main.py generate \
    --mission "$MISSION" \
    --style "$STYLE" \
    --theme "$THEME" \
    --duration $DURATION \
    --platform "$PLATFORM" \
    --languages "$LANGUAGE" \
    --character "superhero_papaya_character" \
    --tone "exciting" \
    --visual-style "bold comic book dynamic" \
    --target-audience "young israeli comic fans" \
    --business-name "The Papaya Bar" \
    --business-address "שבזי 47, ראש העין" \
    --business-phone "054-222-2617" \
    --business-website "thepapayabar.com" \
    --business-facebook "thepapayabar" \
    --business-instagram "@thepapayabar" \
    --show-business-info \
    --session-id "papaya_marvel_25s_fixed_$(date +%Y%m%d_%H%M%S)" \
    --no-cheap \
    --mode enhanced 2>&1 | tee marvel_generation.log

EXIT_CODE=${PIPESTATUS[0]}

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Papaya Bar Marvel Comics ad generation completed successfully!"
    # Find and display the output video
    LATEST_SESSION=$(ls -td outputs/papaya_marvel_25s_fixed_* 2>/dev/null | head -1)
    if [ -n "$LATEST_SESSION" ]; then
        echo "📁 Session: $LATEST_SESSION"
        find "$LATEST_SESSION/final_output" -name "*.mp4" -exec echo "🎬 Video: {}" \;
    fi
else
    echo "❌ Generation failed with exit code: $EXIT_CODE"
    echo "📋 Check marvel_generation.log for details"
fi