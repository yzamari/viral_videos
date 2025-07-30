#!/bin/bash

# Quick test to verify audio-subtitle sync fix
# Using simple 8-second cheap mode for fast results

echo "🎬 Testing Audio-Subtitle Sync Fix - VERIFICATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Fix Applied: Removed padding gaps in SRT timing"
echo ""

python3 main.py generate \
    --mission "Hello everyone! This is Emma with breaking tech news. Artificial intelligence continues advancing rapidly. Stay tuned for more updates." \
    --character "Emma - news reporter" \
    --platform youtube \
    --duration 8 \
    --visual-style "simple" \
    --tone "professional" \
    --style "news" \
    --cheap \
    --voice "en-US-Neural2-F" \
    --session-id "sync_verification" \
    --languages en-US \
    --mode simple

echo ""
echo "✅ Test complete!"
echo "📁 Output: outputs/sync_verification/"
echo ""
echo "🔍 Checking results..."
echo ""

# Check if final video was created
if [ -f "outputs/sync_verification/final_output/final_video_sync_verification__final.mp4" ]; then
    echo "✅ Final video created successfully!"
    echo "📹 Video: outputs/sync_verification/final_output/final_video_sync_verification__final.mp4"
    
    # Check audio files
    echo ""
    echo "🎵 Audio files generated:"
    ls -la outputs/sync_verification/audio/*.mp3 2>/dev/null | wc -l | xargs echo "   Audio segments:"
    
    # Check subtitle file
    if [ -f "outputs/sync_verification/subtitles/subtitles.srt" ]; then
        echo ""
        echo "📝 Subtitle file created:"
        echo "   outputs/sync_verification/subtitles/subtitles.srt"
        echo ""
        echo "📊 Subtitle timing (first 5 entries):"
        head -20 outputs/sync_verification/subtitles/subtitles.srt
    fi
else
    echo "❌ No final video found - checking for errors..."
    ls -la outputs/sync_verification/final_output/
fi