#!/bin/bash

# Netanyahu Marvel Episode 17 - Current Term with Dark Humor
# Generates both Hebrew and English versions

echo "🎬 Starting Netanyahu Marvel Episode 17 Generation"
echo "📊 Languages: Hebrew and English"
echo "⏱️  Duration: 55 seconds"
echo "📱 Platform: Instagram"
echo "🎨 Style: Marvel Comics with dark humor"
echo ""

# Set session ID with timestamp
SESSION_ID="netanyahu_marvel_ep17_$(date +%Y%m%d_%H%M%S)"

# Run the generation
python3 -m src.workflows.generate_viral_video \
  --mission "Marvel Comics explosion! Benjamin Netanyahu with lightning effects crashes through Knesset walls. CRASH! 'I am eternal!' Opposition parties vanish in comic smoke. WHOOSH! Coalition deals with exploding panels. BOOM! Juggling multiple corruption trials while texting. ZAP! Building settlements with energy beams. THWACK! Judicial reform controversy splits the nation. CRACK! 'Bibi will return... again!' WHAM! Israeli flag with lightning bolts." \
  --languages he,en \
  --duration 55 \
  --platform instagram \
  --character "Benjamin Netanyahu with gray hair, determined expression, dark suit with lightning aura, Marvel superhero style" \
  --session-id "$SESSION_ID" \
  --category comedy \
  --style marvel \
  --tone satirical

# Check if generation was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Generation completed successfully!"
    echo "📁 Output location: outputs/$SESSION_ID"
    echo ""
    echo "📹 Videos generated:"
    echo "  - Hebrew: outputs/$SESSION_ID/languages/he/final_video.mp4"
    echo "  - English: outputs/$SESSION_ID/languages/en/final_video.mp4"
else
    echo ""
    echo "❌ Generation failed. Check logs for details."
    echo "📋 Log file: outputs/$SESSION_ID/logs/generation.log"
fi