#!/bin/bash

# Iranian Water Crisis - International News Report
# Professional news style video about Iran's water crisis

echo "💧 Iranian Water Crisis News Report"
echo "=================================="
echo "📺 International News Style"
echo "🌍 Environmental & Political Analysis"
echo ""

# Activate virtual environment
source .venv/bin/activate

python3 main.py generate \
  --mission "BREAKING NEWS: Iran faces worst water crisis in 50 years. Lake Urmia shrinking 90%, Isfahan farmers protest, Tehran rationing water. Expert analysis: decades of mismanagement, dam construction, climate change impact. Satellite images show dramatic environmental collapse. Citizens desperate: 'We have no water for drinking.' Government promises solutions but critics skeptical. Regional tensions rising as rivers dry up. International observers warn of humanitarian crisis. Deep dive investigation into causes, consequences, and potential solutions for Iran's water catastrophe." \
  --platform youtube \
  --duration 90 \
  --visual-style "professional news broadcast" \
  --tone serious \
  --style documentary \
  --no-cheap \
  --voice "en-US-Neural2-D" \
  --session-id "iran_water_crisis_news"

echo ""
echo "✅ Iranian water crisis news report generation complete!"
echo "📁 Output saved in outputs/iran_water_crisis_news/"