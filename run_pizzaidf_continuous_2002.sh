#!/bin/bash
echo "🎬 Starting PizzaIDF CONTINUOUS cinematic movie generation (Since 2002)..."
echo "📅 Started at: $(date)"

# Run with continuous mode and correct date (2002)
python main.py generate \
  --mission "Create a CINEMATIC, HYPER-REALISTIC 70-second continuous action movie for Instagram about PizzaIDF - the veteran family-operated organization that has delivered 800,000+ pizzas and fed 2,000,000+ IDF soldiers since 2002. CRITICAL REQUIREMENTS: 1) KOSHER FOOD ONLY - absolutely NO ham, NO pepperoni, NO non-kosher ingredients! 2) CONTINUOUS CINEMATIC FLOW - one seamless 70-second movie where each scene flows perfectly into the next. Create a continuous ACTION MOVIE showing their 23-year mission 'Serving Those Serving Israel' through Operation Swords of Iron. Film one continuous sequence following volunteers racing to deliver kosher meals to soldiers on the front lines. Show the continuous journey from pizza preparation to delivery, maintaining visual continuity throughout. Feature their 100% volunteer operation, support for small businesses, and the emotional impact. Show dedication certificates and their 60,000+ donor community in a continuous narrative. Make it one unbroken cinematic experience where 'Every Slice Counts'. REMEMBER: KOSHER ONLY + ONE CONTINUOUS FLOW!" \
  --platform instagram \
  --duration 70 \
  --no-cheap \
  --mode professional \
  --style "cinematic" \
  --tone "dramatic" \
  --target-audience "Israeli community, IDF supporters, Jewish diaspora, humanitarian donors" \
  --visual-style "realistic" \
  --category "Entertainment" \
  --frame-continuity on \
  --continuous \
  > pizzaidf_continuous_output.log 2>&1

echo "✅ Completed at: $(date)"
echo "📄 Check pizzaidf_continuous_output.log for details"