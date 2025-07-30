#!/bin/bash

# Run Iranian news episode 4 with premium mode - FIXED VERSION
# Using safer language to avoid VEO content restrictions

echo "🎬 Generating Iranian news episode 4 with PREMIUM MODE (FIXED)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 main.py generate \
    --mission "Animated news report in comedic style. News anchor Maryam announces: 'Breaking news: Citizens adapting to life without social media platforms. Young people report surprising new activities like reading books and having conversations.' Show teenager saying: 'I discovered something called talking to family members. It's actually interesting!' Technology minister suggests: 'Traditional communication methods are making a comeback.' Show carrier pigeons with digital devices. News ticker displays updates about offline discoveries. Studio has professional news desk with modern equipment." \
    --character "Maryam the news anchor - Professional journalist with colorful hijab, animated expressions, holding notepad and pen, cheerful personality, sitting at modern news desk with graphics display behind her" \
    --platform youtube \
    --duration 30 \
    --visual-style "colorful animated news show" \
    --tone "lighthearted comedic informative" \
    --style "animated news broadcast" \
    --theme preset_news_edition \
    --no-cheap \
    --voice "en-US-Neural2-F" \
    --session-id "iran_news_premium_ep4_fixed" \
    --languages en-US \
    --visual-continuity \
    --content-continuity \
    --mode enhanced \
    --scene "Animated news studio with professional desk, colorful graphics displays, news ticker at bottom, bright lighting"

echo ""
echo "✅ Episode 4 premium mode (fixed) generation complete!"
echo "📁 Output folder: outputs/iran_news_premium_ep4_fixed/"