#!/bin/bash

# Greek Mythology Series Generator
# 8 episodes, 48 seconds each, hyper-realistic, educational and inspiring

echo "🏛️ Creating Greek Mythology Series: Heroes of Mount Olympus"
echo "📺 8 episodes × 48 seconds each"
echo "🎯 Goal: Inspire viewers with Greek legendary characters"
echo ""

# Base parameters
DURATION="48"
PLATFORM="youtube"
VOICE="en-US-Neural2-D"  # Consistent male narrator voice
STYLE="hyper_realistic"
THEME="greek_mythology"
MODE="professional"  # Enable all 22 AI agents with professional discussions

# Force disable cheap mode environment variable
export CHEAP_MODE="false"
export NO_CHEAP="true"

# Episode 1: Zeus - King of the Gods
echo "⚡ EPISODE 1: Zeus - King of the Gods"
python3 main.py generate \
  --mission "Create an inspiring educational video about Zeus, the mighty king of the Greek gods and ruler of Mount Olympus. Show his power over thunder and lightning, his role as protector of justice and hospitality, and his complex relationships with gods and mortals. Highlight how he represents leadership, divine authority, and the balance between power and responsibility. Make viewers feel inspired by his commanding presence and the lessons of Greek mythology." \
  --duration "$DURATION" \
  --platform "$PLATFORM" \
  --voice "$VOICE" \
  --style-template "$STYLE" \
  --mode "$MODE" \
  --no-cheap \
  --session-id "greek_zeus_ep1" \
  --character "Zeus, king of Greek gods, majestic bearded figure with flowing white hair, muscular physique, holding lightning bolt, wearing royal toga, divine and powerful appearance"

echo ""
echo "⏳ Waiting 5 seconds before next episode..."
sleep 5

# Episode 2: Athena - Goddess of Wisdom
echo "🦉 EPISODE 2: Athena - Goddess of Wisdom"
python3 main.py generate \
  --mission "Create an inspiring educational video about Athena, the Greek goddess of wisdom, warfare strategy, and crafts. Show her birth from Zeus's head, her role as patron of Athens, and her guidance of heroes like Odysseus. Highlight how she represents intelligence over brute force, strategic thinking, and the power of knowledge. Make viewers feel inspired by her wisdom and the importance of using intellect to solve problems." \
  --duration "$DURATION" \
  --platform "$PLATFORM" \
  --voice "$VOICE" \
  --style-template "$STYLE" \
  --mode "$MODE" \
  --no-cheap \
  --session-id "greek_athena_ep2" \
  --character "Athena, Greek goddess of wisdom, wearing gleaming armor and helmet, holding spear and shield with owl symbol, grey eyes full of intelligence, dignified and strategic appearance" \

echo ""
echo "⏳ Waiting 5 seconds before next episode..."
sleep 5

# Episode 3: Hercules - The Greatest Hero
echo "💪 EPISODE 3: Hercules - The Greatest Hero"
python3 main.py generate \
  --mission "Create an inspiring educational video about Hercules (Heracles), the greatest of all Greek heroes known for his incredible strength and twelve labors. Show his journey from tragedy to redemption, his battles against monsters, and his eventual ascension to godhood. Highlight how he represents perseverance through adversity, redemption through hard work, and the human capacity to overcome any challenge. Make viewers feel inspired by his determination and triumph over impossible odds." \
  --duration "$DURATION" \
  --platform "$PLATFORM" \
  --voice "$VOICE" \
  --style-template "$STYLE" \
  --mode "$MODE" \
  --no-cheap \
  --session-id "greek_hercules_ep3" \
  --character "Hercules, Greek demigod hero, incredibly muscular with lion skin cape, wielding massive club, determined expression, battle-scarred but triumphant appearance" \

echo ""
echo "⏳ Waiting 5 seconds before next episode..."
sleep 5

# Episode 4: Achilles - The Invincible Warrior
echo "⚔️ EPISODE 4: Achilles - The Invincible Warrior"
python3 main.py generate \
  --mission "Create an inspiring educational video about Achilles, the greatest warrior of the Trojan War known for his near-invincibility and tragic fate. Show his choice between a long quiet life and eternal glory, his rage and grief over Patroclus, and his ultimate destiny. Highlight how he represents the warrior's code, the cost of pride, and the eternal struggle between mortality and immortality. Make viewers feel inspired by his courage while learning from his tragic flaws." \
  --duration "$DURATION" \
  --platform "$PLATFORM" \
  --voice "$VOICE" \
  --style-template "$STYLE" \
  --mode "$MODE" \
  --no-cheap \
  --session-id "greek_achilles_ep4" \
  --character "Achilles, Greek warrior, young and handsome with flowing golden hair, wearing bronze armor, holding spear and shield, fierce yet noble expression, legendary appearance" \

echo ""
echo "⏳ Waiting 5 seconds before next episode..."
sleep 5

# Episode 5: Odysseus - The Clever King
echo "🌊 EPISODE 5: Odysseus - The Clever King"
python3 main.py generate \
  --mission "Create an inspiring educational video about Odysseus, the clever king of Ithaca famous for his intelligence and epic journey home. Show his role in the Trojan War with the wooden horse, his ten-year odyssey facing monsters and gods, and his ultimate reunion with Penelope. Highlight how he represents cunning over strength, perseverance through trials, and the power of wit and determination. Make viewers feel inspired by his resourcefulness and unwavering desire to return home." \
  --duration "$DURATION" \
  --platform "$PLATFORM" \
  --voice "$VOICE" \
  --style-template "$STYLE" \
  --mode "$MODE" \
  --no-cheap \
  --session-id "greek_odysseus_ep5" \
  --character "Odysseus, Greek king and hero, weathered but intelligent face with beard, wearing traveler's cloak and armor, holding bow, wise and cunning expression" \

echo ""
echo "⏳ Waiting 5 seconds before next episode..."
sleep 5

# Episode 6: Medusa - The Tragic Monster
echo "🐍 EPISODE 6: Medusa - The Tragic Monster"
python3 main.py generate \
  --mission "Create an inspiring educational video about Medusa, the most famous of the Gorgons, whose tragic transformation from beautiful priestess to monster captures the complexity of Greek mythology. Show her curse by Athena, her isolation, and her eventual defeat by Perseus. Highlight how she represents the victim who becomes victimizer, the power of transformation, and the tragic consequences of divine politics. Make viewers feel both sympathy for her plight and understanding of her role in heroic myths." \
  --duration "$DURATION" \
  --platform "$PLATFORM" \
  --voice "$VOICE" \
  --style-template "$STYLE" \
  --mode "$MODE" \
  --no-cheap \
  --session-id "greek_medusa_ep6" \
  --character "Medusa, Greek gorgon, beautiful yet terrifying face with living snakes for hair, bronze scales, piercing eyes that turn viewers to stone, tragic and fearsome appearance" \

echo ""
echo "⏳ Waiting 5 seconds before next episode..."
sleep 5

# Episode 7: Prometheus - The Fire Bringer
echo "🔥 EPISODE 7: Prometheus - The Fire Bringer"
python3 main.py generate \
  --mission "Create an inspiring educational video about Prometheus, the Titan who defied Zeus to bring fire and knowledge to humanity. Show his creation of humans, his theft of fire from Olympus, and his eternal punishment of having an eagle eat his liver daily. Highlight how he represents sacrifice for the greater good, rebellion against tyranny, and the price of enlightenment. Make viewers feel inspired by his selfless dedication to human progress despite the personal cost." \
  --duration "$DURATION" \
  --platform "$PLATFORM" \
  --voice "$VOICE" \
  --style-template "$STYLE" \
  --mode "$MODE" \
  --no-cheap \
  --session-id "greek_prometheus_ep7" \
  --character "Prometheus, Greek Titan, noble and suffering figure bound to rock, strong but weathered, holding torch of knowledge, defiant yet compassionate expression" \

echo ""
echo "⏳ Waiting 5 seconds before final episode..."
sleep 5

# Episode 8: Aphrodite - Goddess of Love
echo "💕 EPISODE 8: Aphrodite - Goddess of Love"
python3 main.py generate \
  --mission "Create an inspiring educational video about Aphrodite, the Greek goddess of love, beauty, and passion who emerged from sea foam. Show her power over gods and mortals alike, her role in the Trojan War through Paris's choice, and her complex relationships. Highlight how she represents the irresistible force of love, the power of beauty, and the dual nature of passion that can create or destroy. Make viewers feel inspired by love's transformative power while understanding its profound impact on human destiny." \
  --duration "$DURATION" \
  --platform "$PLATFORM" \
  --voice "$VOICE" \
  --style-template "$STYLE" \
  --mode "$MODE" \
  --no-cheap \
  --session-id "greek_aphrodite_ep8" \
  --character "Aphrodite, Greek goddess of love, impossibly beautiful with flowing golden hair, wearing elegant robes, surrounded by roses and doves, radiant and enchanting appearance" \

echo ""
echo "🎬 SERIES COMPLETE!"
echo "📁 All 8 episodes created in outputs/ directory"
echo "🏛️ Greek Mythology Series: Heroes of Mount Olympus"
echo "✨ 8 inspiring episodes showcasing Greek gods and heroes:"
echo "    1. ⚡ Zeus - King of the Gods"
echo "    2. 🦉 Athena - Goddess of Wisdom"
echo "    3. 💪 Hercules - The Greatest Hero"
echo "    4. ⚔️  Achilles - The Invincible Warrior"
echo "    5. 🌊 Odysseus - The Clever King"
echo "    6. 🐍 Medusa - The Tragic Monster"
echo "    7. 🔥 Prometheus - The Fire Bringer"
echo "    8. 💕 Aphrodite - Goddess of Love"
echo ""
echo "🚀 Ready for YouTube series launch!"