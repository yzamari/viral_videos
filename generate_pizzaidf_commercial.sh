#!/bin/bash

# PizzaIDF Commercial Generation Script
# Improved command with better mission description and 30-second duration for Instagram

echo "🍕 Starting PizzaIDF Commercial Generation..."
echo "================================================"

# Run the improved command
python main.py generate \
  --mission "Create a powerful 30-second Instagram commercial for PizzaIDF, the volunteer organization bringing hope through kosher pizza to IDF combat soldiers. Show volunteers preparing and delivering over 800,000 fresh pizzas to soldiers on the front lines during Operation Swords of Iron. Capture the emotional moments when exhausted soldiers receive hot pizza in combat zones - their smiles, gratitude, and renewed morale. Highlight: 100% volunteer operation, supporting local Israeli pizzerias, 2 million soldiers fed since 2022, donor dedication certificates, and the powerful message that every slice delivers: 'You are not forgotten.' Feature real stories of soldiers saying pizza from home gave them strength to continue. End with clear call-to-action: 'Join 60,000+ donors. Every pizza counts. Visit PizzaIDF.org'" \
  --platform instagram \
  --duration 30 \
  --no-cheap \
  --mode professional \
  --style "inspirational" \
  --tone "heartwarming" \
  --target-audience "Israeli community, IDF supporters, Jewish diaspora, humanitarian donors, social impact investors" \
  --visual-style "documentary-cinematic" \
  --category "Entertainment" \
  2>&1 | tee pizzaidf_generation_$(date +%Y%m%d_%H%M%S).log &

# Get the process ID
PID=$!
echo "📍 Process ID: $PID"
echo "📄 Log file: pizzaidf_generation_$(date +%Y%m%d_%H%M%S).log"
echo ""
echo "✅ Generation started in background!"
echo "================================================"
echo ""
echo "Monitor with:"
echo "  tail -f pizzaidf_generation_*.log"
echo "  ps -p $PID"
echo ""