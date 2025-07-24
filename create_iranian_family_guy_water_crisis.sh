#!/bin/bash

# Iran International News - Family Guy Style Water Crisis Series
# Dark comedy with consistent animated characters
# 5 episodes x 60 seconds each

echo "🎬 Iran International News - Family Guy Style Water Crisis Series"
echo "================================================================="
echo "📺 Dark Comedy News Broadcast"
echo "🎨 Seth MacFarlane Animation Style"
echo "💧 Water Crisis Theme"
echo ""

# Episode 1: Breaking News - Water is Missing
echo "📺 Episode 1: Breaking News - Water Mysteriously Disappears"
echo "-----------------------------------------------------------"

python main.py generate \
  --mission "Family Guy style animated news. Iran International logo. News anchor Maryam (big eyes, hijab, exaggerated Persian features like Lois Griffin) reports: 'Breaking news: Scientists confirm water has officially ghosted Iran. It left no forwarding address.' Show cartoon map of Iran with water droplets running away with suitcases. Cut to Peter Griffin-style government official drinking tea: 'Water? Never heard of her.' Dark humor: Citizens licking morning dew off cars. Persian subtitle: 'آب رفت پی کارش' (Water went its own way)" \
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
  --session-id "iran_fg_water_ep1"

if [ $? -eq 0 ]; then
    echo "✅ Episode 1 complete!"
    sleep 10

    # Episode 2: Government Response - Form More Committees
    echo ""
    echo "📺 Episode 2: Government's Brilliant Solution - Infinite Committees"
    echo "------------------------------------------------------------------"
    
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
      --continuous \
      --frame-continuity \
      --mode enhanced \
      --session-id "iran_fg_water_ep2"
    
    if [ $? -eq 0 ]; then
        echo "✅ Episode 2 complete!"
        sleep 10
        
        # Episode 3: Citizens React - Creative Water Solutions
        echo ""
        echo "📺 Episode 3: Citizens Get Creative - Tears as Water Source"
        echo "----------------------------------------------------------"
        
        python main.py generate \
          --mission "Family Guy style chaos. Maryam reports: 'Citizens pioneer innovative water collection methods.' Cutaway: Peter Griffin-style Iranian dad collecting family tears in buckets while watching water bills. Wife (Lois voice): 'Mahmoud, this is ridiculous!' Mahmoud: 'Shh, cry harder, we need to shower!' Cut to Quagmire-style neighbor: 'Giggity, I'm selling my sweat!' Maryam deadpan: 'Government declares tears tax-deductible.' Show tear collection centers. Persian: 'اشک‌های ملی' (National tears)" \
          --platform youtube \
          --duration 60 \
          --visual-style "family guy animation" \
          --theme iran_international_news \
          --character "animated news anchor: Maryam - Family Guy style Persian woman, oversized hijab, huge eyes, Lois Griffin body type but Persian features" \
          --tone darkly_humorous \
          --style animated_comedy \
          --continuous \
          --frame-continuity \
          --mode enhanced \
          --session-id "iran_fg_water_ep3"
        
        if [ $? -eq 0 ]; then
            echo "✅ Episode 3 complete!"
            sleep 10
            
            # Episode 4: International Response - Nobody Cares
            echo ""
            echo "📺 Episode 4: World Reacts - With Devastating Indifference"
            echo "---------------------------------------------------------"
            
            python main.py generate \
              --mission "Family Guy UN parody. Maryam: 'UN holds emergency meeting about Iran water crisis.' Cut to UN assembly: Stewie as UN secretary: 'We've decided to send thoughts and prayers. Meeting adjourned!' Cleveland-style diplomat: 'That's nasty... anyway, lunch?' Cut back: Maryam's hijab slowly sliding off from frustration: 'In other news, fish in dried Urmia Lake have started evolution speedrun to grow legs.' Show cartoon fish with tiny legs. Persian: 'ماهی‌های دونده' (Running fish)" \
              --platform youtube \
              --duration 60 \
              --visual-style "family guy animation" \
              --theme iran_international_news \
              --character "animated news anchor: Maryam - Family Guy style Persian woman, oversized hijab, huge eyes, Lois Griffin body type but Persian features" \
              --tone darkly_humorous \
              --style animated_comedy \
              --continuous \
              --frame-continuity \
              --mode enhanced \
              --session-id "iran_fg_water_ep4"
            
            if [ $? -eq 0 ]; then
                echo "✅ Episode 4 complete!"
                sleep 10
                
                # Episode 5: The Apocalyptic Finale
                echo ""
                echo "📺 Episode 5: Series Finale - Mad Max: Fury Road Tehran"
                echo "-------------------------------------------------------"
                
                python main.py generate \
                  --mission "Family Guy apocalypse finale. Maryam (hijab completely disheveled, makeup running): 'This just in: Tehran has gone full Mad Max.' Cutaway: Peter Griffin-style warriors fighting over last water bottle: 'WITNESS ME!' *drinks entire bottle* Cut to Brian-style intellectual dog: 'You know, this reminds me of my novel about—' *gets hit by water truck* Maryam removes hijab completely: 'F*** it, there's no water to wash it anyway!' Chicken fight with dehydration. End card: 'Iran International: We're as thirsty as you are!' Persian: 'آخرالزمان آبی' (Water apocalypse)" \
                  --platform youtube \
                  --duration 60 \
                  --visual-style "family guy animation" \
                  --theme iran_international_news \
                  --character "animated news anchor: Maryam - Family Guy style Persian woman, hijab falling off, huge eyes, Lois Griffin body type but Persian features, disheveled" \
                  --scene "Family Guy style animated news studio in chaos, Iran International branding damaged, news desk with papers scattered, apocalyptic background" \
                  --tone darkly_humorous \
                  --style animated_comedy \
                  --continuous \
                  --frame-continuity on \
                  --no-cheap \
                  --mode enhanced \
                  --session-id "iran_fg_water_ep5"
                
                if [ $? -eq 0 ]; then
                    echo ""
                    echo "🎉 FAMILY GUY IRAN WATER CRISIS SERIES COMPLETE!"
                    echo ""
                    echo "📁 Your 5-episode series is ready:"
                    echo "   Episode 1 - Water Ghosts Iran: outputs/session_iran_fg_water_ep1/"
                    echo "   Episode 2 - Infinite Committees: outputs/session_iran_fg_water_ep2/"
                    echo "   Episode 3 - Tears Economy: outputs/session_iran_fg_water_ep3/"
                    echo "   Episode 4 - UN Doesn't Care: outputs/session_iran_fg_water_ep4/"
                    echo "   Episode 5 - Mad Max Tehran: outputs/session_iran_fg_water_ep5/"
                    echo ""
                    echo "🏆 SERIES FEATURES:"
                    echo "   🎨 Family Guy animation style throughout"
                    echo "   📺 Iran International News branding"
                    echo "   😂 Dark humor and cutaway gags"
                    echo "   👩 Consistent character (Maryam's transformation)"
                    echo "   💧 Water crisis escalation arc"
                    echo "   🇮🇷 Persian cultural references"
                    echo ""
                    echo "💀 Dark Comedy Highlights:"
                    echo "   - Water literally ghosting Iran"
                    echo "   - Infinite committee recursion"
                    echo "   - Tears as currency"
                    echo "   - Fish evolution speedrun"
                    echo "   - Mad Max Tehran finale"
                    echo ""
                else
                    echo "❌ Episode 5 failed!"
                    exit 1
                fi
            else
                echo "❌ Episode 4 failed!"
                exit 1
            fi
        else
            echo "❌ Episode 3 failed!"
            exit 1
        fi
    else
        echo "❌ Episode 2 failed!"
        exit 1
    fi
else
    echo "❌ Episode 1 failed!"
    exit 1
fi

echo "🎬 Ready for broadcast on Iran International's comedy hour!"