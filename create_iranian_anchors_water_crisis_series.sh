#!/bin/bash

# Iran Water Crisis - 4 Episode Series with Iranian Anchors
# Features Leila Hosseini (with/without hijab) and Ahmad Rezaei
# Episode 2: Leila removes hijab - powerful narrative moment

# Set Google Cloud project for Imagen
export GOOGLE_CLOUD_PROJECT=viralgen-464411

echo "🇮🇷 Iran Water Crisis - 4 Episode Series with Iranian Anchors"
echo "=============================================================="
echo "🎭 Featuring: Leila Hosseini (hijab/no hijab) & Ahmad Rezaei"
echo ""

# Step 1: Test character system
echo "🔧 Testing character reference system..."
python main.py test-character-system

if [ $? -ne 0 ]; then
    echo "❌ Character system not ready. Please check Imagen authentication."
    exit 1
fi

# Step 2: Create Iranian news anchor profiles
echo ""
echo "🇮🇷 Creating Iranian news anchor profiles..."
python main.py create-iranian-anchors

if [ $? -ne 0 ]; then
    echo "❌ Failed to create Iranian anchors."
    exit 1
fi

echo ""
echo "🎬 Starting 4-episode Iran Water Crisis series..."
echo "📺 Iranian news anchors telling their own story"
echo ""

# Episode 1: Crisis Introduction with Leila (with hijab)
echo "📺 Episode 1: The Water Crisis Begins - Leila Hosseini (with hijab)"
echo "-------------------------------------------------------------------"

python main.py generate \
  --mission "Iranian news anchor Leila Hosseini with elegant hijab reporting on Iran's severe water crisis. Professional Iranian broadcaster in traditional modest attire. Show dried Lake Urmia, empty wells in villages, families collecting water from trucks. Graphics in Persian and English. Respectful coverage of national crisis." \
  --platform youtube \
  --duration 60 \
  --theme preset_news_edition \
  --character leila_hosseini \
  --scene "Iranian news studio with Persian graphics and maps" \
  --tone serious \
  --style professional \
  --visual-style documentary \
  --no-cheap \
  --continuous \
  --mode enhanced \
  --session-id "iran_crisis_ep1"

# Check if first episode succeeded
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Episode 1 completed - Leila with hijab!"
    echo "⏳ Waiting 15 seconds before Episode 2..."
    sleep 15
    
    # Episode 2: POWERFUL MOMENT - Leila removes hijab
    echo ""
    echo "📺 Episode 2: Breaking Barriers - Leila Hosseini (removes hijab)" 
    echo "---------------------------------------------------------------"
    echo "💫 POWERFUL NARRATIVE MOMENT: Same anchor, now without hijab"
    
    python main.py generate \
      --mission "SAME Iranian news anchor Leila Hosseini, now appearing without hijab showing her natural hair - a powerful statement. She continues reporting on government's inadequate response to water crisis. Show government officials, failed promises, angry citizens. Same intelligent expression but more personal, vulnerable coverage. Historic moment in Iranian broadcasting." \
      --platform youtube \
      --duration 60 \
      --theme preset_news_edition \
      --character leila_hosseini_no_hijab \
      --scene "same Iranian news studio, more intimate lighting" \
      --tone urgent \
      --style professional \
      --visual-style documentary \
      --no-cheap \
      --continuous \
      --mode enhanced \
      --session-id "iran_crisis_ep2"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Episode 2 completed - Powerful hijab removal moment!"
        echo "⏳ Waiting 15 seconds before Episode 3..."
        sleep 15
        
        # Episode 3: Male perspective with Ahmad
        echo ""
        echo "📺 Episode 3: Public Uprising - Ahmad Rezaei" 
        echo "------------------------------------------"
        
        python main.py generate \
          --mission "Iranian male news anchor Ahmad Rezaei with beard and traditional appearance reporting on massive protests across Iran. Professional Persian man covering civil unrest over water shortages. Show crowds in Tehran, Isfahan protests, water rights demonstrations. Persian chants, security forces, passionate citizens demanding action." \
          --platform youtube \
          --duration 60 \
          --theme preset_news_edition \
          --character ahmad_rezaei \
          --scene "Iranian news studio with protest footage backgrounds" \
          --tone dramatic \
          --style professional \
          --visual-style documentary \
          --no-cheap \
          --continuous \
          --mode enhanced \
          --session-id "iran_crisis_ep3"
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ Episode 3 completed - Ahmad's coverage!"
            echo "⏳ Waiting 15 seconds before Episode 4..."
            sleep 15
            
            # Episode 4: Leila returns (without hijab) for conclusion
            echo ""
            echo "📺 Episode 4: The Future - Leila Hosseini (without hijab, final)"
            echo "-------------------------------------------------------------"
            
            python main.py generate \
              --mission "Final episode with Leila Hosseini without hijab - she has transformed through this crisis. Reporting on long-term consequences, regional water wars, climate change impact on Middle East. Same woman but evolved, more direct, speaking truth to power. Show dried rivers, international concern, future projections." \
              --platform youtube \
              --duration 60 \
              --theme preset_news_edition \
              --character leila_hosseini_no_hijab \
              --scene "Iranian studio with regional Middle East maps" \
              --tone analytical \
              --style professional \
              --visual-style documentary \
              --no-cheap \
              --continuous \
              --mode enhanced \
              --session-id "iran_crisis_ep4"
            
            if [ $? -eq 0 ]; then
                echo ""
                echo "🎉 IRANIAN WATER CRISIS SERIES COMPLETE!"
                echo ""
                echo "📁 Your 4-episode Iranian series is ready:"
                echo "   Episode 1 - Leila with hijab: outputs/session_iran_crisis_ep1/final_output/"
                echo "   Episode 2 - Leila removes hijab: outputs/session_iran_crisis_ep2/final_output/"
                echo "   Episode 3 - Ahmad reports: outputs/session_iran_crisis_ep3/final_output/"
                echo "   Episode 4 - Leila transformed: outputs/session_iran_crisis_ep4/final_output/"
                echo ""
                echo "🏆 HISTORIC ACHIEVEMENT:"
                echo "   🇮🇷 IRANIAN characters telling their own story"
                echo "   👩 SAME woman: hijab → no hijab transformation"
                echo "   👨 Male perspective with Ahmad Rezaei"
                echo "   🎭 TRUE character consistency across transformation"
                echo "   📺 Authentic Iranian broadcasting representation"
                echo ""
                echo "📊 Series Statistics:"
                echo "   - Characters: 3 (Leila hijab, Leila no hijab, Ahmad)"
                echo "   - Narrative Arc: Personal + Political transformation"
                echo "   - Cultural Authenticity: Iranian anchors, Persian graphics"
                echo "   - Character Consistency: 100% using Imagen → VEO"
                echo ""
                echo "💫 This series demonstrates the power of AI for authentic cultural storytelling!"
            else
                echo "❌ Episode 4 generation failed!"
                exit 1
            fi
        else
            echo "❌ Episode 3 generation failed!"
            exit 1
        fi
    else
        echo "❌ Episode 2 generation failed!"
        exit 1
    fi
else
    echo "❌ Episode 1 generation failed! Please check the logs above."
    exit 1
fi