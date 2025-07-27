#!/bin/bash

# Example: Create a BBC-style news series with consistent branding

echo "🎬 Creating BBC-Style News Series"
echo "================================"

# Step 1: Create the series with news theme
echo "1️⃣ Creating series..."
python main.py series create \
  --name "Global News Tonight" \
  --theme "news-edition" \
  --description "Your trusted source for global news and analysis" \
  --template "news-daily" \
  --character "news-anchor-american-female" \
  --voice "professional-narrator" \
  --duration 180 \
  --quality professional

# Get the series ID (you'd capture this from the output in real usage)
SERIES_ID="<series-id-from-output>"

# Step 2: Generate Episode 1
echo -e "\n2️⃣ Generating Episode 1..."
python main.py generate \
  --series "$SERIES_ID" \
  --topic "Breaking: Major breakthrough in renewable energy technology promises to revolutionize global power generation" \
  --episode-title "Renewable Energy Revolution" \
  --style news \
  --model veo-3 \
  --no-cheap \
  --post

# Step 3: Generate Episode 2 (same series, different topic)
echo -e "\n3️⃣ Generating Episode 2..."
python main.py generate \
  --series "$SERIES_ID" \
  --topic "Exclusive: Scientists discover potential cure for rare genetic disorder affecting millions worldwide" \
  --episode-title "Medical Breakthrough" \
  --style news \
  --model veo-3 \
  --no-cheap \
  --post

# Step 4: Generate Episode 3
echo -e "\n4️⃣ Generating Episode 3..."
python main.py generate \
  --series "$SERIES_ID" \
  --topic "Investigation: How artificial intelligence is transforming education in developing countries" \
  --episode-title "AI in Education" \
  --style news \
  --model veo-3 \
  --no-cheap \
  --post

# View series info
echo -e "\n📊 Series Information:"
python main.py series info "$SERIES_ID"

# List all episodes
echo -e "\n📺 All Episodes:"
python main.py series episodes "$SERIES_ID"

echo -e "\n✅ BBC-style news series created successfully!"
echo "All episodes will have:"
echo "- Consistent news anchor (same face)"
echo "- Consistent voice narration"
echo "- News Edition theme (red accents, lower thirds)"
echo "- Professional news graphics"
echo "- Series branding throughout"