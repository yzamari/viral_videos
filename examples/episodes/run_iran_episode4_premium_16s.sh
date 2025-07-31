#!/bin/bash

# Run Iranian news episode 4 with premium mode - 16 SECONDS TEST
# With improved rephrasing, better stroke borders, and AI styling

echo "🎬 Generating Iranian news episode 4 - PREMIUM MODE 16 SECONDS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ Features:"
echo "   - 16 second duration (2 clips)"
echo "   - Improved AI rephrasing (keeps comedy)"
echo "   - Thicker text borders for visibility"
echo "   - AI-controlled overlay styling"
echo "   - Better audio/video/subtitle sync"
echo ""

python3 main.py generate \
    --mission "SATIRICAL NEWS PARODY: Family Guy style animated news. Maryam announces: 'Breaking news! Citizens discovering amazing offline activities!' Shows teenager: 'Talking to parents is surprisingly interesting!' Tech minister declares: 'Traditional communication works great!' Pigeons carry USB drives. News ticker shows updates." \
    --character "Maryam - Family Guy style news anchor with colorful hijab, animated expressions, sitting at news desk" \
    --platform youtube \
    --duration 16 \
    --visual-style "family guy cartoon animation" \
    --tone "comedic satirical lighthearted" \
    --style "animated news parody" \
    --theme preset_news_edition \
    --no-cheap \
    --voice "en-US-Neural2-F" \
    --session-id "iran_news_premium_ep4_16s" \
    --languages en-US \
    --visual-continuity \
    --content-continuity \
    --mode enhanced \
    --scene "Family Guy style animated news studio"

echo ""
echo "✅ Episode 4 premium mode (16s) generation complete!"
echo "📁 Output folder: outputs/iran_news_premium_ep4_16s/"