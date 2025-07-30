#!/bin/bash
# Test script to verify single voice consistency

echo "🎤 Testing Single Voice Consistency..."
echo "====================================="

# Generate a test video with multiple segments
python main.py \
  --mission "Breaking news: Scientists discover that homework actually makes students smarter, shocking parents worldwide" \
  --duration 16 \
  --platform youtube \
  --cheap full \
  --style "news report" \
  --voice "en-US-Journey-O" \
  --no-post \
  --session-id "single_voice_test" \
  --overlay-video "/Users/yahavzamari/viralAi/assets/overlays/iran_thirstional_overlay.mp4"

echo "✅ Test complete - check logs for voice consistency"