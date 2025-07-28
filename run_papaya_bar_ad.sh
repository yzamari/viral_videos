#!/bin/bash

# Papaya Bar Advertisement - Dual Language (English & Hebrew)
# Healthy shakes by day, cocktails by night!

echo "🥤 Starting Papaya Bar Advertisement Generation"
echo "📍 Location: Shabazi 47, Rosh Ha'Ayin"
echo "🌐 Languages: English and Hebrew"
echo "📱 Platforms: Instagram & TikTok"
echo "⏱️  Duration: 30 seconds"
echo ""

# Set session ID with timestamp
SESSION_ID="papaya_bar_ad_$(date +%Y%m%d_%H%M%S)"

# Mission - Keep it short and let AI agents decide the creative approach
MISSION="Papaya Bar: Grandma's healing smoothies by day, shake-based cocktails by night. Fresh, colorful, healthy transformation."

# Character description for consistent visuals
CHARACTER="Young, energetic bartender mixing colorful drinks, vibrant tropical setting with fresh fruits"

# Run the generation with professional mode for best quality
python3 main.py generate \
  --mission "$MISSION" \
  --languages en-US --languages he \
  --duration 30 \
  --platform instagram \
  --character "$CHARACTER" \
  --session-id "$SESSION_ID" \
  --category Entertainment \
  --style viral \
  --tone "funny refreshing engaging" \
  --visual-style "colorful vibrant tropical" \
  --mode professional \
  --no-cheap \
  2>&1 | tee "papaya_bar_generation.log"

# Check if generation was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Generation completed successfully!"
    echo "📁 Output location: outputs/$SESSION_ID"
    echo ""
    echo "📹 Videos generated:"
    echo "  - Main video: outputs/$SESSION_ID/final_output/"
    echo "  - Hebrew version: outputs/$SESSION_ID/languages/he/"
    echo "  - English version: outputs/$SESSION_ID/languages/en_US/"
    echo ""
    echo "🎨 Ready for upload to:"
    echo "  - Instagram Reels"
    echo "  - TikTok"
    echo ""
    echo "💡 Business details included:"
    echo "  - Location: Shabazi 47, Rosh Ha'Ayin"
    echo "  - Phone: 054-222-2617"
    echo "  - Email: thepapayabar@gmail.com"
else
    echo ""
    echo "❌ Generation failed. Check logs for details."
    echo "📋 Log file: papaya_bar_generation.log"
fi