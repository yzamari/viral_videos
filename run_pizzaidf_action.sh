#!/bin/bash
echo "🍕 Starting PizzaIDF ACTION commercial generation..."
echo "📅 Started at: $(date)"

# Run the command with action movie style and hyper realistic emphasis
python main.py generate \
  --mission "Create an ACTION-PACKED, HYPER-REALISTIC 60-second Instagram commercial for PizzaIDF - the veteran family-operated organization that has delivered 800,000+ pizzas and fed 2,000,000+ IDF soldiers since 2022. CRITICAL: Show ONLY KOSHER FOOD - absolutely NO ham, NO pepperoni, NO non-kosher ingredients! Create an ACTION MOVIE style video showing their mission of 'Serving Those Serving Israel' through Operation Swords of Iron, with dramatic scenes of delivering kosher meals to soldiers on the front lines in Gaza and across Israel. Feature high-intensity moments of their 100% volunteer-powered operation racing against time, the adrenaline of supporting small businesses, and the powerful emotional impact of bringing comfort food to heroes in combat zones. Show dramatic shots of dedication certificates, their massive donor community of 60,000+ supporters, and the intense emotional connection between pizza delivery and soldier morale. Make it feel like an action movie where 'Every Slice Counts' in supporting IDF soldiers defending Israel. REMEMBER: KOSHER FOOD ONLY - NO NON-KOSHER INGREDIENTS WHATSOEVER!" \
  --platform instagram \
  --duration 60 \
  --no-cheap \
  --mode professional \
  --style "action" \
  --tone "dramatic" \
  --target-audience "Israeli community, IDF supporters, Jewish diaspora, humanitarian donors" \
  --visual-style "realistic" \
  --category "Entertainment" \
  > pizzaidf_action_output.log 2>&1

echo "✅ Completed at: $(date)"
echo "📄 Check pizzaidf_action_output.log for details"