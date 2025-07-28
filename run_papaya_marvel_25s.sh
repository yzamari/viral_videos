#!/bin/bash

# Papaya Bar 25-second Marvel Comics Style Advertisement
# Business address MUST be in overlays as per requirement

echo "🎬 Generating 25-second Papaya Bar Marvel Comics Advertisement..."
echo "📍 Business: Papaya Bar, שבזי 47, ראש העין"
echo "📱 Contact: 054-222-2617"

# Mission description for 25-second ad
MISSION="Create a 25-second Marvel Comics style advertisement for Papaya Bar, the famous juice and shake bar in Rosh HaAyin. Show a superhero-style entrance to the vibrant juice bar, with explosive colors and comic book effects. Feature their signature papaya smoothies with dynamic action shots, comic book speech bubbles, and POW/BAM style effects. Emphasize the fresh fruits, healthy energy, and the transformation into a nighttime alcohol-shake destination. Include Marvel-style character reactions to the amazing taste. The business is located at Shabazi 47, Rosh HaAyin, phone 054-222-2617, email thepapayabar@gmail.com. They are always open with outdoor seating. Visual style: Marvel Comics with bright colors, action lines, and comic book panels."

# Run the generation with proper parameters
python3 main.py generate \
  --mission "$MISSION" \
  --session-id "papaya_marvel_25s_$(date +%Y%m%d_%H%M%S)" \
  --theme marvel-comics \
  --business-name "Papaya Bar פפאיה בר" \
  --business-address "שבזי 47, ראש העין" \
  --business-phone "054-222-2617" \
  --business-website "thepapayabar@gmail.com" \
  --show-business-info \
  --languages he \
  --veo-model-order veo3-fast,veo2 \
  --category Entertainment \
  --platform instagram \
  --duration 25 \
  --character "marvel_hero" \
  --no-cheap

echo "✅ Generation command submitted!"
echo "📂 Check outputs folder for results"