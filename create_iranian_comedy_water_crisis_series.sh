#!/bin/bash

# Iran Water Crisis - DARK COMEDY SERIES for Iranian Audience
# Satirical take with Iranian humor, cultural references, and dark comedy
# Features Leila & Ahmad in satirical news format

# Set Google Cloud project for Imagen
export GOOGLE_CLOUD_PROJECT=viralgen-464411

echo "😂 Iran Water Crisis - DARK COMEDY SERIES"
echo "========================================"
echo "🎭 For Iranian Audience - Dark Humor & Satire"
echo "🇮🇷 Persian Comedy Style with Cultural References"
echo ""

# Step 1: Test character system
echo "🔧 Testing character reference system..."
python main.py test-character-system

if [ $? -ne 0 ]; then
    echo "❌ Character system not ready. Please check Imagen authentication."
    exit 1
fi

# Ensure Iranian anchors exist
echo ""
echo "🇮🇷 Ensuring Iranian news anchor profiles exist..."
python main.py create-iranian-anchors

echo ""
echo "😂 Starting SATIRICAL Iran Water Crisis series..."
echo "📺 Dark Comedy for Persian-speaking audience"
echo ""

# Episode 1: Absurdist Introduction - Leila with hijab
echo "📺 Episode 1: 'Breaking: Water is Wet!' - Leila Hosseini (Satirical)"
echo "----------------------------------------------------------------"

python main.py generate \
  --mission "SATIRICAL Iranian news segment with anchor Leila Hosseini wearing hijab. Dark comedy. Mock serious tone: 'Breaking news: Scientists confirm water is indeed wet, Iranian government surprised.' Officials looking confused at empty swimming pools, ministers drinking tea while announcing water shortage. Persian cultural humor: reference to tarof, bureaucracy jokes. Subtitle in Persian: 'آب خشک شده!' (Water has dried up!)" \
  --platform tiktok \
  --duration 40 \
  --theme preset_iran_international_news \
  --character leila_hosseini \
  --scene "Professional Iranian news studio, modern setting" \
  --tone humorous \
  --style comedy \
  --visual-style "family guy animation style" \
  --target-audience "Iranian comedy fans" \
  --no-cheap \
  --continuous \
  --mode enhanced \
  --session-id "iran_comedy_ep1"

if [ $? -eq 0 ]; then
    echo ""
    echo "😂 Episode 1 completed - Satirical hijab intro!"
    echo "⏳ Waiting 15 seconds before Episode 2..."
    sleep 15
    
    # Episode 2: THE LIBERATION COMEDY - Leila removes hijab
    echo ""
    echo "📺 Episode 2: 'Freedom & Water Shortage' - Leila's Liberation (DARK COMEDY)" 
    echo "------------------------------------------------------------------------"
    echo "💫 COMEDIC MOMENT: Hijab removal as comedy bit"
    
    python main.py generate \
      --mission "DARK COMEDY: Same anchor Leila removes hijab mid-broadcast! 'Since we have no water for hijab washing, I'm taking it off!' Dramatic slow-motion with epic music. Her hair flows dramatically as she continues serious water report. Persian humor: 'حداقل یه چیز آزاد شد!' (At least one thing got liberated!). Mix liberation joy with water crisis absurdity. For Persian-speaking comedy fans." \
      --platform tiktok \
      --duration 40 \
      --theme preset_iran_international_news \
      --character leila_hosseini_no_hijab \
      --scene "Same news studio with celebration, confetti and Iranian flag colors" \
      --tone humorous \
      --style comedy \
      --visual-style "family guy animation style" \
      --target-audience "Iranian comedy fans" \
      --no-cheap \
      --continuous \
      --mode enhanced \
      --session-id "iran_comedy_ep2"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🤣 Episode 2 completed - HILARIOUS hijab removal comedy!"
        echo "⏳ Waiting 15 seconds before Episode 3..."
        sleep 15
        
        # Episode 3: Male comedian perspective - Ahmad
        echo ""
        echo "📺 Episode 3: 'Men Don't Understand Water Either' - Ahmad's Comedy" 
        echo "---------------------------------------------------------------"
        
        python main.py generate \
          --mission "Iranian male anchor Ahmad Rezaei doing DARK COMEDY about protests. Political rant: 'People are protesting for water while government officials are swimming in pools of corruption!' Show angry crowds, officials at luxury resorts. Iranian comedy with sarcasm: stupid bureaucrats, useless meetings, endless committees about water committees. Persian subtitle: 'کمیته آب کمیته تشکیل داد' (Water committee formed a committee committee). For Iranian audience who loves political satire." \
          --platform tiktok \
          --duration 40 \
          --theme preset_iran_international_news \
          --character ahmad_rezaei \
          --scene "News studio with cutaway segments showing Iranian protests" \
          --tone humorous \
          --style comedy \
          --visual-style "family guy animation style" \
          --target-audience "Iranian comedy fans" \
          --no-cheap \
          --continuous \
          --mode enhanced \
          --session-id "iran_comedy_ep3"
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "😂 Episode 3 completed - Ahmad's political satire!"
            echo "⏳ Waiting 15 seconds before Episode 4..."
            sleep 15
            
            # Episode 4: Dark Comedy Finale - Leila's absurdist conclusion
            echo ""
            echo "📺 Episode 4: 'The Solution: Import Persian Gulf!' - Comedy Finale"
            echo "--------------------------------------------------------------"
            
            python main.py generate \
              --mission "FINAL SATIRICAL EPISODE: Leila (no hijab) presents absurd government solutions with deadpan Persian humor. 'Government announces plan to import the entire Persian Gulf to Tehran via pipeline.' Show ridiculous graphics of impossible engineering. Iranian comedy gold: bureaucrats measuring clouds, rain committee meetings, hiring water fortune tellers. Persian punchline: 'در آخر همه تشنه ماندیم!' (In the end, we all stayed thirsty!). Perfect Persian dark comedy for Iranian audience who understands the cultural context." \
              --platform tiktok \
              --duration 40 \
              --theme preset_iran_international_news \
              --character leila_hosseini_no_hijab \
              --scene "Studio with impossible engineering blueprints and diagrams" \
              --tone humorous \
              --style comedy \
              --visual-style "family guy animation style" \
              --target-audience "Iranian comedy fans" \
              --no-cheap \
              --continuous \
              --mode enhanced \
              --session-id "iran_comedy_ep4"
            
            if [ $? -eq 0 ]; then
                echo ""
                echo "🎉 Episode 4 completed - Absurdist solutions!"
                echo "⏳ Waiting 15 seconds before Episode 5..."
                sleep 15
                
                # Episode 5: Weather Report - "Hot and Nuclear"
                echo ""
                echo "📺 Episode 5: 'Weather Report: Hot and Nuclear' - Leila's Forecast"
                echo "----------------------------------------------------------------"
                
                python main.py generate \
                  --mission "DARKEST COMEDY WEATHER REPORT: Leila (no hijab) as weather anchor with Iran International graphics. 'Today's forecast: Hot and nuclear with a chance of uranium enrichment!' Show weather map of Iran with absurd symbols: mushroom clouds for Tehran, boiling kettles for Isfahan, empty water bottles everywhere. Persian dark humor: 'دمای تهران: رادیواکتیو!' (Tehran temperature: Radioactive!). Make jokes about nuclear program heating the country. Use professional weather graphics but with satirical elements. Perfect for Iranian audience who loves political dark comedy." \
                  --platform tiktok \
                  --duration 40 \
                  --theme preset_iran_international_news \
                  --character leila_hosseini_no_hijab \
                  --scene "Weather studio with dramatic weather report graphics" \
                  --tone humorous \
                  --style comedy \
                  --visual-style "family guy animation style" \
                  --target-audience "Iranian comedy fans" \
                  --no-cheap \
                  --continuous \
                  --mode enhanced \
                  --session-id "iran_comedy_ep5"
                
                if [ $? -eq 0 ]; then
                    echo ""
                    echo "🎉 IRANIAN DARK COMEDY SERIES COMPLETE!"
                echo ""
                echo "📁 Your satirical 5-episode series is ready:"
                echo "   Episode 1 - Absurd Crisis (Leila hijab): outputs/session_iran_comedy_ep1/final_output/"
                echo "   Episode 2 - Liberation Comedy (no hijab): outputs/session_iran_comedy_ep2/final_output/"
                echo "   Episode 3 - Male Political Satire: outputs/session_iran_comedy_ep3/final_output/"
                echo "   Episode 4 - Absurdist Solutions: outputs/session_iran_comedy_ep4/final_output/"
                echo "   Episode 5 - Hot & Nuclear Weather: outputs/session_iran_comedy_ep5/final_output/"
                echo ""
                echo "🏆 COMEDY BREAKTHROUGH:"
                echo "   😂 PERSIAN DARK HUMOR for Iranian audience"
                echo "   🎭 Cultural references Iranians will understand"
                echo "   💫 Hijab removal as COMEDIC liberation moment"
                echo "   🇮🇷 Political satire in Persian comedy style"
                echo "   📺 Professional Iran International news branding"
                echo "   ☢️ Hot & Nuclear weather forecast added!"
                echo ""
                echo "📊 Comedy Series Features:"
                echo "   - Audience: Iranian/Persian speakers"
                echo "   - Style: Dark humor + political satire"
                echo "   - Cultural: Tarof jokes, bureaucracy comedy"
                echo "   - Language: Persian subtitles & cultural references"
                echo "   - Character Arc: Leila's comedic transformation"
                echo ""
                echo "🎬 Persian Comedy Elements:"
                echo "   - Government incompetence jokes"
                echo "   - Bureaucracy absurdity"
                echo "   - Cultural liberation humor"
                echo "   - Political situation comedy"
                echo "   - Iranian audience inside jokes"
                echo ""
                echo "💫 This series will be HILARIOUS for Iranian viewers!"
                echo "😂 Perfect blend of serious topic + Persian dark humor!"
                else
                    echo "❌ Episode 5 generation failed!"
                    exit 1
                fi
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