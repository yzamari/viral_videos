#!/bin/bash

# Fixed News Series Generator
# Creates two episodes without style reference issues

echo "🎬 Iran Water Crisis News Series (Fixed Version)"
echo "=============================================="
echo ""

# Episode 1: The Crisis
echo "📺 Episode 1: Iran Water Crisis Report"
echo "-----------------------------------"

python main.py generate \
  --mission "GNN News Network. Professional female narrator voice-over throughout. 
VISUALS: Aerial shots of Lake Urmia before/after, dried riverbeds, empty reservoirs, Isfahan water trucks.
GRAPHICS: Network logo 'GNN', lower thirds, statistical overlays showing 90% shrinkage.
NO ANCHOR FACES - documentary style footage only.
Content: Iran faces 50-year worst water crisis. Major cities experiencing severe shortages." \
  --platform youtube \
  --duration 50 \
  --theme preset_news_edition \
  --tone serious \
  --style professional \
  --visual-style documentary \
  --no-cheap \
  --mode enhanced \
  --session-id "gnn_water_ep1"

# Check if first episode succeeded
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Episode 1 generated successfully!"
    echo "⏳ Waiting 10 seconds before Episode 2..."
    sleep 10
    
    # Episode 2: The Response (without style reference)
    echo ""
    echo "📺 Episode 2: Protests Over Water Crisis" 
    echo "------------------------------------"
    
    python main.py generate \
      --mission "GNN News Network. SAME professional female narrator as previous episode.
VISUALS: Wide shots of peaceful protests in Tehran/Isfahan, crowds with signs, security presence.
GRAPHICS: Same GNN branding, lower thirds, maps showing protest locations.
NO ANCHOR FACES - documentary protest footage only.
Content: Massive protests erupt across Iran over water crisis. Citizens demand government action.
TONE: More urgent than previous episode." \
      --platform youtube \
      --duration 50 \
      --theme preset_news_edition \
      --tone urgent \
      --style professional \
      --visual-style documentary \
      --no-cheap \
      --continuous \
      --mode enhanced \
      --session-id "gnn_water_ep2"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 NEWS SERIES COMPLETE!"
        echo ""
        echo "📁 Your videos are ready:"
        echo "   Episode 1: outputs/session_gnn_water_ep1/final_output/"
        echo "   Episode 2: outputs/session_gnn_water_ep2/final_output/"
        echo ""
        echo "✅ Consistency achieved through:"
        echo "   - Same GNN network branding"
        echo "   - Same female narrator voice"
        echo "   - Same documentary style"
        echo "   - Same theme (preset_news_edition)"
        echo "   - Connected storyline (crisis → protests)"
    else
        echo "❌ Episode 2 generation failed!"
    fi
else
    echo "❌ Episode 1 generation failed! Please check the logs above."
fi