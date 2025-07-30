#!/bin/bash

# Test the audio-subtitle sync and font size fixes
echo "🧪 TESTING FIXES: Audio-Subtitle Sync & Font Size"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Fixed Issues:"
echo "   1. Restored padding in subtitle timing (300ms between segments)"
echo "   2. Increased subtitle font size from 22 to 36 pixels"
echo ""

# Test with Iranian news content
echo "🎬 Test 1: Iranian News with VEO3-fast (16 seconds)"
python3 main.py generate \
    --mission "Simple animated news show. Emma happily reports good news about technology. Shows people enjoying digital and offline activities together. Everyone finds balance between online and real-world fun." \
    --character "Emma - cheerful news reporter" \
    --platform youtube \
    --duration 16 \
    --visual-style "simple" \
    --tone "cheerful" \
    --style "news" \
    --no-cheap \
    --voice "en-US-Neural2-F" \
    --session-id "sync_font_fix_test" \
    --languages en-US \
    --mode simple \
    --veo-model-order "veo3-fast,veo3,veo2"

echo ""
echo "✅ Test complete!"
echo "📹 Check video at: outputs/sync_font_fix_test/final_output/final_video_sync_font_fix_test__final.mp4"
echo ""
echo "🔍 Please verify:"
echo "   1. Audio and subtitles are properly synchronized"
echo "   2. Subtitle font is large enough to read comfortably"
echo "   3. There's a natural pause between sentences"