#!/bin/bash

# Run only Episode 2 of Iran International News - Family Guy Style Water Crisis Series

echo "🎬 Iran International News - Family Guy Style Water Crisis Series"
echo "================================================================="
echo "📺 Episode 2: Government's Brilliant Solution - Infinite Committees"
echo ""

python main.py generate \
  --mission "Family Guy cutaway style. Same anchor Maryam (consistent character) announces: 'Government unveils master plan: Committee to form committee about committees.' Cutaway gag: Stewie-style minister in meeting: 'Gentlemen, I propose we form a sub-committee to discuss forming committees.' Room full of identical officials nodding. Cut back to Maryam: 'In related news, the Committee Committee has formed a Committee Committee Committee.' Show organizational chart exploding. Persian text: 'کمیته‌های بی‌نهایت' (Infinite committees)" \
  --platform youtube \
  --duration 60 \
  --visual-style "family guy animation" \
  --theme iran_international_news \
  --character "animated news anchor: Maryam - Family Guy style Persian woman, oversized hijab, huge eyes, Lois Griffin body type but Persian features" \
  --scene "Family Guy style animated news studio, Iran International branding, news desk, map of Iran in background" \
  --tone darkly_humorous \
  --style animated_comedy \
  --no-cheap \
  --mode enhanced \
  --session-id "iran_fg_water_ep2_v3"

if [ $? -eq 0 ]; then
    echo "✅ Episode 2 complete!"
else
    echo "❌ Episode 2 failed!"
fi