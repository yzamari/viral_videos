#!/bin/bash

# Run Iranian news episode 4 with premium mode - FULL 30 SECONDS
# With all improvements: better rephrasing, thicker borders, AI styling

echo "🎬 Generating Iranian news episode 4 - PREMIUM MODE FULL VERSION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ Features:"
echo "   - 30 second duration (full episode)"
echo "   - Improved AI rephrasing (preserves satire)"
echo "   - Thicker text borders (3-5px)"
echo "   - AI-controlled overlay styling"
echo "   - Better audio/video/subtitle sync"
echo ""

python3 main.py generate \
    --mission "SATIRICAL NEWS PARODY: Family Guy style animated news. Maryam announces: 'Breaking news! Citizens discovering amazing offline activities!' Shows teenager: 'Talking to parents is surprisingly interesting!' Tech minister declares: 'Traditional communication works great!' Pigeons carry USB drives. News ticker shows updates." \
    --character "Maryam - Family Guy style news anchor with colorful hijab, animated expressions, sitting at news desk" \
    --platform youtube \
    --duration 30 \
    --visual-style "family guy cartoon animation" \
    --tone "comedic satirical lighthearted" \
    --style "animated news parody" \
    --theme preset_news_edition \
    --no-cheap \
    --voice "en-US-Neural2-F" \
    --session-id "iran_news_premium_ep4_full" \
    --languages en-US \
    --visual-continuity \
    --content-continuity \
    --mode enhanced \
    --scene "Family Guy style animated news studio"

echo ""
echo "✅ Episode 4 premium mode (full) generation complete!"
echo "📁 Output folder: outputs/iran_news_premium_ep4_full/"