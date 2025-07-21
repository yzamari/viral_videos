#!/bin/bash
echo "🍕 Starting PizzaIDF commercial generation..."
echo "📅 Started at: $(date)"

# Run the command with proper formatting
python main.py generate \
  --mission "Create an inspiring 60-second Instagram commercial for PizzaIDF - the veteran family-operated organization that has delivered 800,000+ pizzas and fed 2,000,000+ IDF soldiers since 2022. Show their mission of 'Serving Those Serving Israel' through Operation Swords of Iron, delivering kosher meals to soldiers on the front lines in Gaza and across Israel. Highlight their 100% volunteer-powered operation, support for small businesses, and the heartwarming impact of bringing comfort food to heroes in combat zones. Feature their dedication certificates, donor community of 60,000+ supporters, and the emotional connection between pizza delivery and soldier morale. Emphasize how 'Every Slice Counts' in supporting IDF soldiers defending Israel. Kosher food only! No ham, no peperoni etc! NOTICE! Only kosher food should be shown in the video" \
  --platform instagram \
  --duration 60 \
  --no-cheap \
  --mode simple \
  --style "inspirational" \
  --tone "heartwarming" \
  --target-audience "Israeli community, IDF supporters, Jewish diaspora, humanitarian donors" \
  --visual-style "realistic" \
  --category "Entertainment" \
  > pizzaidf_output.log 2>&1

echo "✅ Completed at: $(date)"
echo "📄 Check pizzaidf_output.log for details"