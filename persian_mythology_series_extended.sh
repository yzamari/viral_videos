#!/bin/bash

# Extended Persian Mythology Series Generator
# 8 episodes total, 48 seconds each, hyper-realistic, educational and inspiring

echo "🏛️ Creating EXTENDED Persian Mythology Series: Legends of Ancient Persia"
echo "📺 8 episodes × 48 seconds each (Episodes 5-8 added)"
echo "🎯 Goal: Inspire viewers with Persian legendary characters"
echo ""

# Base parameters
DURATION="48"
PLATFORM="youtube"
VOICE="en-US-Neural2-D"  # Consistent male narrator voice
STYLE="hyper_realistic"
THEME="persian_mythology"
MODE="professional"  # Enable all 22 AI agents with professional discussions

# Episodes 1-4 (Already created - displaying for reference)
echo "✅ Episodes 1-4 Previously Created:"
echo "    🗡️  Episode 1: Rostam - The Invincible Hero"
echo "    💧 Episode 2: Anahita - Goddess of Waters and Wisdom"
echo "    👑 Episode 3: Fereydun - The Just King"
echo "    ⚔️  Episode 4: Gordafarid - The Warrior Princess"
echo ""
echo "🚀 Creating NEW Episodes 5-8:"
echo ""

# Episode 5: Cyrus the Great - The Noble Conqueror
echo "👑 EPISODE 5: Cyrus the Great - The Noble Conqueror"
python3 main.py generate \
  --mission "Create an inspiring educational video about Cyrus the Great, the noble founder of the Persian Empire who revolutionized leadership through tolerance and respect. Show his wisdom in freeing enslaved peoples, respecting different cultures, and building an empire through unity rather than oppression. Highlight how he represents enlightened leadership, human rights, and the Persian ideal of ruling with justice and compassion. Make viewers feel inspired by his progressive vision and humanitarian approach to power." \
  --duration "$DURATION" \
  --platform "$PLATFORM" \
  --voice "$VOICE" \
  --style-template "$STYLE" \
  --mode "$MODE" \
  --no-cheap \
  --session-id "persian_cyrus_ep5" \
  --character "Cyrus the Great, Persian emperor, royal robes and crown, wise and compassionate expression, holding scroll of human rights, majestic and benevolent appearance" \

echo ""
echo "⏳ Waiting 5 seconds before next episode..."
sleep 5

# Episode 6: Scheherazade - The Master Storyteller
echo "📚 EPISODE 6: Scheherazade - The Master Storyteller"
python3 main.py generate \
  --mission "Create an inspiring educational video about Scheherazade, the brilliant Persian storyteller who saved her life and countless others through the power of narrative. Show her incredible intelligence, creativity, and courage in using stories to change hearts and minds. Highlight how she represents the power of wisdom, creativity, and the transformative nature of storytelling in Persian culture. Make viewers feel inspired by her intelligence and the idea that words and stories can literally save lives." \
  --duration "$DURATION" \
  --platform "$PLATFORM" \
  --voice "$VOICE" \
  --style-template "$STYLE" \
  --mode "$MODE" \
  --no-cheap \
  --session-id "persian_scheherazade_ep6" \
  --character "Scheherazade, Persian storyteller, elegant Persian dress, intelligent and captivating expression, surrounded by magical story elements, enchanting and wise appearance" \

echo ""
echo "⏳ Waiting 5 seconds before next episode..."
sleep 5

# Episode 7: Kaveh the Blacksmith - The Revolutionary Hero
echo "🔨 EPISODE 7: Kaveh the Blacksmith - The Revolutionary Hero"
python3 main.py generate \
  --mission "Create an inspiring educational video about Kaveh the Blacksmith, the common man who became a revolutionary hero by standing up against the tyrant Zahhak. Show his courage in leading the people's rebellion despite being a simple craftsman, and how he raised his leather apron as a banner of freedom. Highlight how he represents the power of ordinary people to create extraordinary change, standing up for justice regardless of social status. Make viewers feel inspired that anyone can be a hero and fight against oppression." \
  --duration "$DURATION" \
  --platform "$PLATFORM" \
  --voice "$VOICE" \
  --style-template "$STYLE" \
  --mode "$MODE" \
  --no-cheap \
  --session-id "persian_kaveh_ep7" \
  --character "Kaveh the Blacksmith, Persian craftsman, work clothes and leather apron, determined and defiant expression, holding hammer and banner, strong and revolutionary appearance" \

echo ""
echo "⏳ Waiting 5 seconds before final episode..."
sleep 5

# Episode 8: Arash the Archer - The Ultimate Sacrifice
echo "🏹 EPISODE 8: Arash the Archer - The Ultimate Sacrifice"
python3 main.py generate \
  --mission "Create an inspiring educational video about Arash the Archer, the legendary Persian hero who made the ultimate sacrifice to save his homeland. Show his incredible skill with the bow, his selfless decision to give his life to determine Persia's borders, and how his arrow flew for days to mark the boundary. Highlight how he represents the highest form of patriotism, selfless sacrifice, and putting one's people before personal survival. Make viewers feel inspired by his ultimate devotion and the idea that true heroes give everything for their people." \
  --duration "$DURATION" \
  --platform "$PLATFORM" \
  --voice "$VOICE" \
  --style-template "$STYLE" \
  --mode "$MODE" \
  --no-cheap \
  --session-id "persian_arash_ep8" \
  --character "Arash the Archer, Persian warrior, traditional archer attire, noble and determined expression, drawing a magnificent bow, heroic and sacrificial appearance" \

echo ""
echo "🎬 EXTENDED SERIES COMPLETE!"
echo "📁 All 8 episodes created in outputs/ directory"
echo "🏛️ Persian Mythology Series: Legends of Ancient Persia (Complete Edition)"
echo "✨ 8 inspiring episodes showcasing Persian heroes and values:"
echo "    1. 🗡️  Rostam - The Invincible Hero"
echo "    2. 💧 Anahita - Goddess of Waters and Wisdom"  
echo "    3. 👑 Fereydun - The Just King"
echo "    4. ⚔️  Gordafarid - The Warrior Princess"
echo "    5. 👑 Cyrus the Great - The Noble Conqueror"
echo "    6. 📚 Scheherazade - The Master Storyteller"
echo "    7. 🔨 Kaveh the Blacksmith - The Revolutionary Hero"
echo "    8. 🏹 Arash the Archer - The Ultimate Sacrifice"
echo ""
echo "🚀 Ready for YouTube series launch!"