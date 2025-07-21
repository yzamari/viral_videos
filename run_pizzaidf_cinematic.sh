#!/bin/bash
echo "🎬 Starting PizzaIDF CINEMATIC continuous movie generation..."
echo "📅 Started at: $(date)"

# Run with continuous generation and frame continuity for seamless cinematic experience
python main.py generate \
  --mission "Create a CINEMATIC, HYPER-REALISTIC 70-second continuous action movie for Instagram about PizzaIDF - the veteran family-operated organization that has delivered 800,000+ pizzas and fed 2,000,000+ IDF soldiers since 2022. CRITICAL REQUIREMENTS: 1) KOSHER FOOD ONLY - absolutely NO ham, NO pepperoni, NO non-kosher ingredients! 2) CONTINUOUS CINEMATIC FLOW - each scene must flow seamlessly into the next with perfect continuity. Create an ACTION MOVIE showing their mission 'Serving Those Serving Israel' through Operation Swords of Iron. Film dramatic continuous sequences of volunteers racing to deliver kosher meals to soldiers on the front lines, with each shot flowing cinematically into the next. Show the adrenaline-pumping 100% volunteer operation, the intensity of supporting small businesses, and powerful moments of bringing comfort food to combat zones. Feature cinematic shots of dedication certificates, their 60,000+ donor community, and the emotional bond between pizza delivery and soldier morale. Make it one continuous cinematic experience where 'Every Slice Counts'. REMEMBER: KOSHER ONLY + CONTINUOUS CINEMATIC FLOW!" \
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
  > pizzaidf_cinematic_output.log 2>&1

echo "✅ Completed at: $(date)"
echo "📄 Check pizzaidf_cinematic_output.log for details"