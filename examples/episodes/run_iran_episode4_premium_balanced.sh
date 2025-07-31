#!/bin/bash

# Run Iranian news episode 4 with premium mode - BALANCED VERSION
# Keeps the comedy but uses safer language

echo "🎬 Generating Iranian news episode 4 with PREMIUM MODE (BALANCED)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 main.py generate \
    --mission "Family Guy style animated news. Anchor Maryam announces: 'Breaking news! Citizens discovering life without social media. Young people report surprising activities.' Show teenager: 'I discovered talking to my parents. It's actually interesting!' Tech minister: 'Traditional communication is trendy again.' Show carrier pigeons with USB drives. News ticker: 'Youth Discover Books'. Studio lights flicker. Maryam sips water." \
    --character "Maryam the anchor - Family Guy style news presenter with colorful hijab, animated expressions, holding water bottle, sitting at news desk" \
    --platform youtube \
    --duration 30 \
    --visual-style "family guy cartoon animation" \
    --tone "comedic satirical lighthearted" \
    --style "animated news comedy" \
    --theme preset_news_edition \
    --no-cheap \
    --voice "en-US-Neural2-F" \
    --session-id "iran_news_premium_ep4_balanced" \
    --languages en-US \
    --visual-continuity \
    --content-continuity \
    --mode enhanced \
    --scene "Family Guy style news studio with desk and graphics"

echo ""
echo "✅ Episode 4 premium mode (balanced) generation complete!"
echo "📁 Output folder: outputs/iran_news_premium_ep4_balanced/"