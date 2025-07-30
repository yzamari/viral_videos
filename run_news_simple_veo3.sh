#!/bin/bash

# Run simple news-style cartoon with VEO3-fast - using successful pattern
# Based on the working simple test, but with news theme

echo "🎬 Generating Simple News Cartoon - VEO3-FAST"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ Features:"
echo "   - 16 second duration (2 clips)"
echo "   - VEO3-fast generation"
echo "   - Simple news format"
echo "   - Generic cartoon style"
echo ""

python3 main.py generate \
    --mission "Simple animated news show. Emma happily reports good news about technology. Shows people enjoying digital and offline activities together. Everyone finds balance between online and real-world fun." \
    --character "Emma - friendly cartoon news reporter with simple design" \
    --platform youtube \
    --duration 16 \
    --visual-style "simple cartoon animation" \
    --tone "cheerful positive upbeat" \
    --style "simple cartoon news" \
    --theme preset_news_edition \
    --no-cheap \
    --voice "en-US-Neural2-F" \
    --session-id "news_simple_veo3" \
    --languages en-US \
    --mode enhanced \
    --scene "simple colorful news studio background" \
    --veo-model-order "veo3-fast,veo3,veo2"

echo ""
echo "✅ Simple news cartoon (VEO3-fast) generation complete!"
echo "📁 Output folder: outputs/news_simple_veo3/"