#!/bin/bash

# Test subtitle size fix
echo "🧪 SUBTITLE SIZE FIX TEST"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Fixed Issues:"
echo "   - Reduced subtitle font size from 3.5% to 2.0% of video width"
echo "   - Minimum subtitle size reduced from 32px to 24px"
echo ""

# Quick 8-second test
echo "🎬 Testing with 8-second video"
python3 main.py generate \
    --mission "Hello everyone. Technology brings us together. Let's enjoy both digital and real experiences." \
    --character "Emma - news reporter" \
    --platform youtube \
    --duration 8 \
    --visual-style "simple" \
    --tone "cheerful" \
    --style "news" \
    --no-cheap \
    --voice "en-US-Neural2-F" \
    --session-id "subtitle_size_test" \
    --languages en-US \
    --mode simple \
    --veo-model-order "veo3-fast,veo3,veo2"

echo ""
echo "✅ Test complete!"
echo "📹 Final video: outputs/subtitle_size_test/final_output/final_video_subtitle_size_test__final.mp4"
echo ""
echo "🔍 Subtitles should now be:"
echo "   - Normal readable size (not huge)"
echo "   - Clean without pink background"
echo "   - Properly synced with audio"