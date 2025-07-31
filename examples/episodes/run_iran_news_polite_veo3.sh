#!/bin/bash

# Run Iranian news with polite, VEO-friendly mission using VEO3-fast
# Family Guy style but with positive, non-satirical content

echo "🎬 Generating Iranian news - POLITE VERSION with VEO3-FAST"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ Features:"
echo "   - 30 second duration (full episode)"
echo "   - VEO3-fast generation"
echo "   - Polite, positive content"
echo "   - Family Guy animation style"
echo "   - No satirical elements"
echo ""

python3 main.py generate \
    --mission "ANIMATED NEWS SHOW: Family Guy style cartoon news. Maryam cheerfully announces: 'Great news! People are rediscovering wonderful offline activities!' Shows happy teenager: 'Spending time with family has been really rewarding!' Technology expert shares: 'Both digital and traditional communication have their benefits!' Colorful pigeons deliver messages in a whimsical world. Positive updates scroll below." \
    --character "Maryam - Family Guy style news anchor with colorful hijab, friendly smile, animated expressions, sitting at modern news desk" \
    --platform youtube \
    --duration 30 \
    --visual-style "family guy cartoon animation" \
    --tone "cheerful positive upbeat" \
    --style "animated cartoon news" \
    --theme preset_news_edition \
    --no-cheap \
    --voice "en-US-Neural2-F" \
    --session-id "iran_news_polite_veo3" \
    --languages en-US \
    --visual-continuity \
    --content-continuity \
    --mode enhanced \
    --scene "Family Guy style animated news studio" \
    --veo-model-order "veo3-fast,veo3,veo2"

echo ""
echo "✅ Polite Iranian news (VEO3-fast) generation complete!"
echo "📁 Output folder: outputs/iran_news_polite_veo3/"