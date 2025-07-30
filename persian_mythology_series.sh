#!/bin/bash

# Persian Mythology Series Generator
# 4 episodes, 48 seconds each, hyper-realistic, educational and inspiring

echo "🏛️ Creating Persian Mythology Series: Legends of Ancient Persia"
echo "📺 4 episodes × 48 seconds each"
echo "🎯 Goal: Inspire viewers with Persian legendary characters"
echo ""

# Base parameters
DURATION="48"
PLATFORM="youtube"
VOICE="en-US-Neural2-D"  # Consistent male narrator voice
STYLE="hyper_realistic"
THEME="persian_mythology"
MODE="professional"  # Enable all 22 AI agents with professional discussions

# Episode 1: Rostam - The Invincible Hero
echo "🗡️  EPISODE 1: Rostam - The Invincible Hero"
python3 main.py generate \
  --mission "Create an inspiring educational video about Rostam, the legendary Persian hero from Shahnameh. Show his incredible strength, unwavering loyalty to Iran, and his epic battles against demons and enemies. Highlight how he represents courage, honor, and dedication to protecting one's homeland. Make viewers feel inspired by his heroic qualities and Persian values." \
  --duration "$DURATION" \
  --platform "$PLATFORM" \
  --voice "$VOICE" \
  --style-template "$STYLE" \
  --mode "$MODE" \
  --no-cheap \
  --session-id "persian_rostam_ep1" \
  --character "Rostam, legendary Persian hero, muscular warrior with traditional armor, wielding famous sword, majestic and powerful appearance" \

echo ""
echo "⏳ Waiting 5 seconds before next episode..."
sleep 5

# Episode 2: Anahita - Goddess of Waters and Wisdom
echo "💧 EPISODE 2: Anahita - Goddess of Waters and Wisdom"
python3 main.py generate \
  --mission "Create an inspiring educational video about Anahita, the ancient Persian goddess of waters, wisdom, and fertility. Show her divine beauty, connection to rivers and knowledge, and her role as protector of the Persian people. Highlight how she represents wisdom, nurturing strength, and the sacred feminine in Persian culture. Make viewers feel inspired by her divine wisdom and protective nature." \
  --duration "$DURATION" \
  --platform "$PLATFORM" \
  --voice "$VOICE" \
  --style-template "$STYLE" \
  --mode "$MODE" \
  --no-cheap \
  --session-id "persian_anahita_ep2" \
  --character "Anahita, Persian goddess, flowing robes, surrounded by water and light, serene and wise expression, divine feminine beauty" \

echo ""
echo "⏳ Waiting 5 seconds before next episode..."
sleep 5

# Episode 3: Fereydun - The Just King
echo "👑 EPISODE 3: Fereydun - The Just King"
python3 main.py generate \
  --mission "Create an inspiring educational video about Fereydun, the legendary just king of Persia who defeated the tyrant Zahhak and brought peace to the land. Show his wisdom in ruling, his commitment to justice, and how he divided his kingdom fairly among his sons. Highlight how he represents righteous leadership, fairness, and the Persian ideal of a wise ruler. Make viewers feel inspired by his dedication to justice and good governance." \
  --duration "$DURATION" \
  --platform "$PLATFORM" \
  --voice "$VOICE" \
  --style-template "$STYLE" \
  --mode "$MODE" \
  --no-cheap \
  --session-id "persian_fereydun_ep3" \
  --character "Fereydun, Persian king, royal robes and crown, wise and noble appearance, holding symbols of justice and authority" \

echo ""
echo "⏳ Waiting 5 seconds before final episode..."
sleep 5

# Episode 4: Gordafarid - The Warrior Princess
echo "⚔️  EPISODE 4: Gordafarid - The Warrior Princess"
python3 main.py generate \
  --mission "Create an inspiring educational video about Gordafarid, the brave Persian warrior princess who defended her city through intelligence and courage. Show her strategic brilliance in battle, her fearless determination, and how she used both wit and warfare to protect her people. Highlight how she represents the strength of Persian women, intelligence over brute force, and fearless leadership. Make viewers feel inspired by her courage and tactical genius." \
  --duration "$DURATION" \
  --platform "$PLATFORM" \
  --voice "$VOICE" \
  --style-template "$STYLE" \
  --mode "$MODE" \
  --no-cheap \
  --session-id "persian_gordafarid_ep4" \
  --character "Gordafarid, Persian warrior princess, armor and weapons, determined and intelligent expression, fierce yet elegant" \

echo ""
echo "🎬 SERIES COMPLETE!"
echo "📁 Episodes created in outputs/ directory"
echo "🏛️ Persian Mythology Series: Legends of Ancient Persia"
echo "✨ 4 inspiring episodes showcasing Persian heroes and values"