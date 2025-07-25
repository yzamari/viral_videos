#!/bin/bash

# Racheli's Goodbye Video - Celebrating an Amazing Journey
# A heartfelt tribute to an exceptional colleague

echo "👋 Creating Racheli's Goodbye Video"
echo "===================================="
echo "🌟 Celebrating an Agile Champion"
echo "🏠 Full House Career Mom"
echo "🚀 Culture Transformation Leader"
echo ""

python main.py generate \
  --mission "Marvel Comics style professional farewell video from Racheli to NeuReality team. Opening: Racheli (green eyes, elegant business suit, stylish headscarf) stands heroically in NeuReality AI chip headquarters. 'Dear NeuReality team, as my mission here completes...' Office transforms with dramatic comic panels. 'Serving as your Agile Coach has been an honor.' Sticky notes swirl like energy particles. Action montage: Racheli leading Scrum ceremonies with superhero efficiency, comic book style. 'We conquered impossible deadlines in chip development.' Dynamic PMO orchestration scene with dramatic angles. '2 in a box partnerships - unstoppable force meets immovable object.' Split panel: 'Mastering work-life balance like a true hero.' Office evolution shown in epic comic panels: 'Together we transformed NeuReality's culture.' Energy effects subtly appear. 'Your dedication and professionalism made us invincible.' Racheli maintains heroic stance. 'The frameworks we built will endure.' Final panel: 'May NeuReality continue its legendary journey in AI innovation.' Professional salute, NeuReality logo glowing behind. 'Excelsior! -Racheli'" \
  --platform instagram \
  --duration 40 \
  --character "Racheli: Marvel Comics style professional woman with expressive green eyes, elegant business attire, stylish headscarf, confident posture, consistent comic book appearance throughout" \
  --scene "Marvel Comics style office with dramatic panels and transitions, maintaining Racheli's consistent character design in every frame" \
  --visual-style "marvel cinematic universe" \
  --tone "emotional" \
  --style "animated" \
  --no-cheap \
  --session-id "racheli_goodbye_tribute" \
  --content-continuity \
  --visual-continuity \
  --voice "en-US-Journey-F"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Racheli's goodbye video created successfully!"
    echo "📝 Key themes included:"
    echo "   - Agile Coach & Scrum Master excellence"
    echo "   - PMO & Release Management achievements"  
    echo "   - Full House career mom inspiration"
    echo "   - Organizational culture transformation"
    echo "   - 2 in a box partnership success"
    echo "   - Lasting legacy of positive change"
    echo ""
    echo "💝 Thank you, Racheli, for making our workplace better!"
else
    echo "❌ Failed to create goodbye video"
fi