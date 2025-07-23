#!/bin/bash

# Simple Iran Water Crisis News Series Generator
# Creates two consistent news episodes

echo "🎬 Iran Water Crisis News Series (Simple Version)"
echo "=============================================="
echo ""

# Configuration
ANCHORS="Professional news anchors Sarah Chen (Asian woman, 35, navy suit, black hair) and Michael Roberts (Caucasian man, 40, gray suit) at news desk"

# Episode 1
echo "📺 Generating Episode 1: Water Crisis Report..."
python main.py generate \
  --mission "${ANCHORS}. Breaking news: Iran faces worst water crisis in 50 years. Cities experiencing severe shortages. Lake Urmia shrunk 90%. Professional news studio." \
  --platform youtube \
  --duration 50 \
  --theme preset_news_edition \
  --tone serious \
  --style professional \
  --visual-style realistic \
  --no-cheap \
  --continuous \
  --mode enhanced

echo ""
echo "⏳ Waiting 3 seconds..."
sleep 3

# Episode 2
echo "📺 Generating Episode 2: Protests Coverage..."
python main.py generate \
  --mission "${ANCHORS}. Continuing coverage: Massive protests erupt across Iran over water crisis. Thousands march demanding action. Same studio, urgent tone." \
  --platform youtube \
  --duration 50 \
  --theme preset_news_edition \
  --tone urgent \
  --style professional \
  --visual-style realistic \
  --no-cheap \
  --continuous \
  --mode enhanced

echo ""
echo "✅ Generation complete! Check outputs/ folder for your videos."