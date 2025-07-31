#!/bin/bash
# Test script to generate a 10-second video and verify 2-second fadeout

echo "🎬 Generating 10-second test video with fadeout..."

# Generate a 10-second video
python main.py \
  --mission "Quick test: A reporter discovers water has turned into chocolate milk in Tehran" \
  --duration 10 \
  --platform youtube \
  --cheap full \
  --style "news report" \
  --voice "neutral female" \
  --no-post \
  --session-id "fadeout_test_10s" \
  --overlay-video "/Users/yahavzamari/viralAi/assets/overlays/iran_thirstional_overlay.mp4"

echo "✅ Video generation complete"

# Check the fadeout
python3 test_fadeout_simple.py