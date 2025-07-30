#!/bin/bash

# Test VEO3-fast with extremely simple, safe content
# No Family Guy references, no complex scenarios

echo "🎬 Testing VEO3-FAST with Simple Content"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ Features:"
echo "   - 16 second duration (2 clips)"
echo "   - VEO3-fast generation"
echo "   - Very simple content"
echo "   - Generic cartoon style"
echo ""

python3 main.py generate \
    --mission "Simple animated show about friendship. Emma happily talks about playing games. Shows kids having fun together. Everyone enjoys spending time with family." \
    --character "Emma - friendly cartoon character with simple design" \
    --platform youtube \
    --duration 16 \
    --visual-style "simple cartoon animation" \
    --tone "cheerful positive" \
    --style "simple cartoon" \
    --theme preset_news_edition \
    --no-cheap \
    --voice "en-US-Neural2-F" \
    --session-id "simple_veo3_test" \
    --languages en-US \
    --mode enhanced \
    --scene "simple colorful cartoon background" \
    --veo-model-order "veo3-fast,veo3,veo2"

echo ""
echo "✅ Simple VEO3-fast test complete!"
echo "📁 Output folder: outputs/simple_veo3_test/"