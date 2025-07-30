#!/bin/bash

# Test Iran Thirstional overlay
echo "💧 Testing Iran THIRSTIONAL Overlay 💧"
echo "====================================="

# Quick test with short duration
python3 main.py generate \
    --mission "Iran THIRSTIONAL breaking news: Water has been missing for 2000 days! Our reporter Maryam brings you the latest updates from the desert formerly known as Tehran." \
    --platform youtube \
    --duration 15 \
    --style "satirical news" \
    --tone "darkly humorous" \
    --visual-style "family guy animation" \
    --theme preset_news_edition \
    --no-cheap \
    --session-id "test_thirstional_overlay" \
    --voice "en-US-Neural2-F"

echo ""
echo "✅ Test complete! Check outputs/test_thirstional_overlay/"
echo "🔍 Look for the THIRSTIONAL logo in the top-right corner!"