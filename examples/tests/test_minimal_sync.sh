#!/bin/bash

# Minimal test to verify audio-subtitle sync fix
# Extremely simple 5-second test that should complete quickly

echo "🧪 MINIMAL SYNC TEST: Audio-Subtitle Fix"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Testing sync fix with minimal 5-second video"
echo ""

python3 main.py generate \
    --mission "Hello world. This is a test." \
    --character "Simple test" \
    --platform youtube \
    --duration 5 \
    --visual-style "simple" \
    --tone "neutral" \
    --style "test" \
    --cheap \
    --voice "en-US-Neural2-F" \
    --session-id "minimal_sync_test" \
    --languages en-US \
    --mode simple

echo ""
echo "✅ Test complete!"
echo ""

# Check results
if [ -f "outputs/minimal_sync_test/final_output/final_video_minimal_sync_test__final.mp4" ]; then
    echo "✅ Final video created successfully!"
    echo "📹 Video: outputs/minimal_sync_test/final_output/final_video_minimal_sync_test__final.mp4"
    
    # Show subtitle timing
    if [ -f "outputs/minimal_sync_test/subtitles/subtitles.srt" ]; then
        echo ""
        echo "📝 Subtitle timing:"
        cat outputs/minimal_sync_test/subtitles/subtitles.srt
    fi
else
    echo "❌ No final video found"
    ls -la outputs/minimal_sync_test/final_output/ 2>/dev/null
fi