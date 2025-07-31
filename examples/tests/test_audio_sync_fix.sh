#!/bin/bash

# Test the audio-subtitle sync fix with refactored video generator
# Short 8-second test to verify timing accuracy

echo "🧪 Testing Audio-Subtitle Sync Fix"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ Testing:"
echo "   - RefactoredVideoGenerator (with AudioFirstSubtitleGenerator)"
echo "   - 8 second duration (1 clip)"
echo "   - Simple content to verify sync timing"
echo ""

python3 main.py generate \
    --mission "Quick test. Emma says hello and talks about technology being great for everyone." \
    --character "Emma - friendly cartoon character" \
    --platform youtube \
    --duration 8 \
    --visual-style "simple cartoon" \
    --tone "cheerful" \
    --style "simple test" \
    --theme preset_news_edition \
    --no-cheap \
    --voice "en-US-Neural2-F" \
    --session-id "audio_sync_test" \
    --languages en-US \
    --mode enhanced \
    --scene "simple background" \
    --veo-model-order "veo3-fast,veo3,veo2"

echo ""
echo "✅ Audio sync test complete!"
echo "📁 Output folder: outputs/audio_sync_test/"
echo "🔍 Check: audio duration vs subtitle timing vs video duration"