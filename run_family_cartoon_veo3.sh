#!/bin/bash

# Run generic family cartoon about technology - VEO3-fast compatible
# Completely generic content with no political/news references

echo "🎬 Generating Family Technology Cartoon - VEO3-FAST COMPATIBLE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ Features:"
echo "   - 30 second duration"
echo "   - VEO3-fast generation"
echo "   - Generic family content"
echo "   - Family Guy animation style"
echo "   - No political references"
echo ""

python3 main.py generate \
    --mission "ANIMATED FAMILY SHOW: Cheerful cartoon about modern life. Sarah happily announces: 'Amazing! Families are trying new activities together!' Shows smiling teenager: 'Board games with parents are actually fun!' Tech enthusiast shares: 'Both apps and face-to-face chat work great!' Cartoon birds deliver colorful letters. Happy messages appear on screen." \
    --character "Sarah - Family Guy style animated host with bright clothes, warm smile, sitting at colorful desk" \
    --platform youtube \
    --duration 30 \
    --visual-style "family guy cartoon animation" \
    --tone "cheerful positive wholesome" \
    --style "animated family cartoon" \
    --theme preset_news_edition \
    --no-cheap \
    --voice "en-US-Neural2-F" \
    --session-id "family_tech_cartoon_veo3" \
    --languages en-US \
    --visual-continuity \
    --content-continuity \
    --mode enhanced \
    --scene "Family Guy style colorful animated studio" \
    --veo-model-order "veo3-fast,veo3,veo2"

echo ""
echo "✅ Family technology cartoon (VEO3-fast) generation complete!"
echo "📁 Output folder: outputs/family_tech_cartoon_veo3/"