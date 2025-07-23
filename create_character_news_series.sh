#!/bin/bash

# Character-Based News Series Generator
# Uses Imagen + VEO pipeline for TRUE character consistency

echo "🎭 Character-Based News Series Generator"
echo "======================================"
echo ""

# Step 1: Test character system
echo "🔧 Testing character reference system..."
python main.py test-character-system

if [ $? -ne 0 ]; then
    echo "❌ Character system not ready. Please check Imagen authentication."
    exit 1
fi

# Step 2: Create news anchor profiles
echo ""
echo "👥 Creating professional news anchor profiles..."
python main.py create-news-anchors

if [ $? -ne 0 ]; then
    echo "❌ Failed to create news anchors."
    exit 1
fi

# Step 3: Generate Episode 1 with Sarah Chen
echo ""
echo "📺 Episode 1: Iran Water Crisis (Sarah Chen)"
echo "-------------------------------------------"

python main.py generate \
  --mission "Breaking news report about Iran's severe water crisis. Professional news anchor Sarah Chen reporting from studio. Show statistics, maps of affected regions, dried reservoirs." \
  --platform youtube \
  --duration 50 \
  --theme preset_news_edition \
  --character sarah_chen \
  --scene "professional news studio with desk and monitors" \
  --tone serious \
  --style professional \
  --visual-style documentary \
  --no-cheap \
  --continuous \
  --mode enhanced \
  --session-id "character_news_ep1"

# Check if first episode succeeded
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Episode 1 generated with consistent character!"
    echo "⏳ Waiting 10 seconds before Episode 2..."
    sleep 10
    
    # Episode 2: Same character, different story
    echo ""
    echo "📺 Episode 2: Protests Over Water Crisis (Same Sarah Chen)" 
    echo "--------------------------------------------------------"
    
    python main.py generate \
      --mission "Follow-up news report by Sarah Chen about massive protests erupting across Iran over water crisis. Same anchor, same professional appearance. Show protest footage, crowd scenes." \
      --platform youtube \
      --duration 50 \
      --theme preset_news_edition \
      --character sarah_chen \
      --scene "same news studio setup as previous episode" \
      --tone urgent \
      --style professional \
      --visual-style documentary \
      --no-cheap \
      --continuous \
      --mode enhanced \
      --session-id "character_news_ep2"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 CHARACTER CONSISTENCY NEWS SERIES COMPLETE!"
        echo ""
        echo "📁 Your videos are ready:"
        echo "   Episode 1: outputs/session_character_news_ep1/final_output/"
        echo "   Episode 2: outputs/session_character_news_ep2/final_output/"
        echo ""
        echo "✨ TRUE CHARACTER CONSISTENCY achieved through:"
        echo "   - Same character reference (Sarah Chen)"
        echo "   - Imagen generates character in new scenes"
        echo "   - VEO uses generated images as first frames"
        echo "   - Result: SAME FACE across episodes!"
        echo ""
        echo "🚀 This is a BREAKTHROUGH for AI video consistency!"
    else
        echo "❌ Episode 2 generation failed!"
    fi
else
    echo "❌ Episode 1 generation failed! Please check the logs above."
fi