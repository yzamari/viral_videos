#!/bin/bash

# Test the final quality and subtitle fixes
echo "🧪 FINAL TEST: Quality & Subtitle Fixes"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Fixed Issues:"
echo "   1. Subtitle styling - transparent background, no pink box"
echo "   2. Video quality - CRF 18 (visually lossless)"
echo "   3. Using overlay video as base for subtitles"
echo "   4. Resolution-aware font sizing"
echo ""

# Test with Iranian news content
echo "🎬 Testing with Iranian News (16 seconds)"
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
    --session-id "final_quality_test" \
    --languages en-US \
    --mode simple \
    --veo-model-order "veo3-fast,veo3,veo2"

echo ""
echo "✅ Test complete!"
echo ""
echo "📹 Check videos:"
echo "   - Final: outputs/final_quality_test/final_output/final_video_final_quality_test__final.mp4"
echo "   - Overlays: outputs/final_quality_test/final_output/final_video_final_quality_test__overlays_only.mp4"
echo ""
echo "🔍 Please verify:"
echo "   1. Subtitles have NO pink background (transparent)"
echo "   2. Final video quality matches overlay video (~25MB)"
echo "   3. Subtitles are added to the high-quality overlay video"
echo "   4. Font size scales with video resolution"