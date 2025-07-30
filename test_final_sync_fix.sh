#!/bin/bash

# Final test of the audio-subtitle sync fix 
# Test both cheap and premium modes to verify the fix works

echo "🧪 FINAL TEST: Audio-Subtitle Sync Fix"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ Fix Applied:"
echo "   - Removed padding gaps in SRT timing"  
echo "   - Audio plays back-to-back, subtitles match exactly"
echo "   - Single voice consistency maintained" 
echo ""

echo "🏃‍♂️ Test 1: CHEAP MODE (8 seconds)"
python3 main.py generate \
    --mission "Quick sync test. Emma talks about tech news." \
    --character "Emma - news reporter" \
    --platform youtube \
    --duration 8 \
    --visual-style "simple" \
    --tone "cheerful" \
    --style "test" \
    --cheap \
    --voice "en-US-Neural2-F" \
    --session-id "final_sync_test_cheap" \
    --languages en-US \
    --mode simple

echo ""
echo "🚀 Test 2: PREMIUM MODE (8 seconds)"  
python3 main.py generate \
    --mission "Quick sync test. Emma talks about tech news." \
    --character "Emma - news reporter" \
    --platform youtube \
    --duration 8 \
    --visual-style "simple" \
    --tone "cheerful" \
    --style "test" \
    --no-cheap \
    --voice "en-US-Neural2-F" \
    --session-id "final_sync_test_premium" \
    --languages en-US \
    --mode simple \
    --veo-model-order "veo3-fast,veo3,veo2"

echo ""
echo "✅ Final sync tests complete!"
echo "📁 Cheap mode: outputs/final_sync_test_cheap/"
echo "📁 Premium mode: outputs/final_sync_test_premium/"