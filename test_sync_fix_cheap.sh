#!/bin/bash

# Test audio-subtitle sync fix with CHEAP MODE first
# Short 16-second test to verify timing accuracy

echo "🧪 Testing Audio-Subtitle Sync Fix - CHEAP MODE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ Testing:"
echo "   - RefactoredVideoGenerator with AudioFirstSubtitleGenerator"
echo "   - 16 second duration (2 clips)"
echo "   - CHEAP MODE (no VEO - faster, reliable)"
echo "   - Simple content to verify sync timing"
echo ""

python3 main.py generate \
    --mission "Audio sync test. Emma explains technology benefits. Shows happy people using devices. Everyone enjoys balanced digital life." \
    --character "Emma - friendly news reporter" \
    --platform youtube \
    --duration 16 \
    --visual-style "simple animation" \
    --tone "cheerful positive" \
    --style "news test" \
    --theme preset_news_edition \
    --cheap \
    --voice "en-US-Neural2-F" \
    --session-id "sync_test_cheap" \
    --languages en-US \
    --mode enhanced \
    --scene "simple studio background"

echo ""
echo "✅ Cheap mode sync test complete!"
echo "📁 Output folder: outputs/sync_test_cheap/"
echo "🔍 Check: Audio duration = Subtitle timing = Video duration"