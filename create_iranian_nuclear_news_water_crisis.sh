#!/bin/bash

# Nuclear News - Family Guy Style Water Crisis Series
# Dark comedy with consistent animated characters
# 5 episodes x 60 seconds each
# Features bright news desk overlays rendered on top of video

# Set colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
GREEN='\033[0;32m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${YELLOW}${BOLD}☢️  NUCLEAR NEWS - FAMILY GUY STYLE WATER CRISIS SERIES ☢️${NC}"
echo -e "${RED}============================================================${NC}"
echo -e "${BLUE}📺 Dark Comedy News Broadcast${NC}"
echo -e "${PURPLE}🎨 Seth MacFarlane Animation Style${NC}"
echo -e "${CYAN}💧 Water Crisis Theme${NC}"
echo -e "${YELLOW}☢️  Nuclear News Branding${NC}"
echo ""

# Episode 1: Breaking News - Water is Missing
echo -e "\n${RED}${BOLD}🚨 EPISODE 1: BREAKING NEWS - WATER MYSTERIOUSLY DISAPPEARS 🚨${NC}"
echo -e "${YELLOW}-----------------------------------------------------------${NC}"

python3 main.py generate \
  --mission "Family Guy style animated news. NUCLEAR NEWS logo with radiation symbol. News anchor Maryam (big eyes, hijab, exaggerated Persian features like Lois Griffin) at bright blue news desk: 'This is Nuclear News! Breaking: Water has ABANDONED Iran! Our Panic Level is at DEFCON THIRSTY!' Show cartoon map with water droplets fleeing with radiation symbols. Peter Griffin-style official: 'Water? That's classified!' Citizens drinking mirages. Yellow ticker: 'BREAKING: WATER CRISIS REACHES NUCLEAR LEVELS'" \
  --platform youtube \
  --duration 60 \
  --visual-style "family guy animation" \
  --theme nuclear_news \
  --character "animated news anchor: Maryam - Family Guy style Persian woman, oversized hijab, huge eyes, Lois Griffin body type but Persian features" \
  --scene "Family Guy style animated news studio, bright blue desk, NUCLEAR NEWS logos everywhere, spinning globe, dramatic red alerts, yellow ticker at bottom" \
  --tone darkly_humorous \
  --style animated_comedy \
  --no-cheap \
  --mode enhanced \
  --session-id "nuclear_news_water_ep1"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Episode 1 complete!${NC}"
    sleep 10

    # Episode 2: Government Response - Form More Committees
    echo ""
    echo -e "${RED}${BOLD}⚠️  EPISODE 2: GOVERNMENT'S SOLUTION - INFINITE COMMITTEES ⚠️${NC}"
    echo -e "${YELLOW}------------------------------------------------------------------${NC}"
    
    python3 main.py generate \
      --mission "Family Guy cutaway style. Nuclear News anchor Maryam announces with dramatic music: 'NUCLEAR NEWS ALERT! Government's EXPLOSIVE response: Committee to study committees about committees!' Cutaway: Stewie-style minister with radiation badge: 'Gentlemen, I propose we go NUCLEAR... with bureaucracy!' Officials' heads explode cartoon-style. Maryam: 'BREAKING: Committee count reaches CRITICAL MASS!' Show org chart mushroom cloud. Yellow ticker: 'COMMITTEE MELTDOWN IMMINENT!'" \
      --platform youtube \
      --duration 60 \
      --visual-style "family guy animation" \
      --theme nuclear_news \
      --character "animated news anchor: Maryam - Family Guy style Persian woman, oversized hijab, huge eyes, Lois Griffin body type but Persian features" \
      --scene "Family Guy style animated news studio, bright blue desk, NUCLEAR NEWS logos everywhere, spinning globe, dramatic red alerts, yellow ticker at bottom" \
      --tone darkly_humorous \
      --style animated_comedy \
      --content-continuity \
      --visual-continuity \
      --no-cheap \
      --mode enhanced \
      --session-id "nuclear_news_water_ep2"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Episode 2 complete!${NC}"
        sleep 10
        
        # Episode 3: Citizens React - Creative Water Solutions
        echo ""
        echo -e "${RED}${BOLD}💧 EPISODE 3: CITIZENS GET CREATIVE - TEARS AS WATER SOURCE 💧${NC}"
        echo -e "${YELLOW}----------------------------------------------------------${NC}"
        
        python3 main.py generate \
          --mission "Nuclear News EXCLUSIVE! Maryam with flashing alerts: 'Citizens reach RADIOACTIVE levels of desperation!' Cutaway: Peter-style dad with hazmat suit collecting tears: 'These tears are WEAPONS-GRADE!' Wife: 'Mahmoud, you're INSANE!' 'No, I'm NUCLEAR!' Quagmire neighbor: 'Giggity, my sweat's going CRITICAL!' Maryam: 'DEFCON TEARS activated!' Show tear enrichment facilities. Ticker: 'TEAR URANIUM NOW TRADING AT $5000/GALLON'" \
          --platform youtube \
          --duration 60 \
          --visual-style "family guy animation" \
          --theme nuclear_news \
          --character "animated news anchor: Maryam - Family Guy style Persian woman, oversized hijab, huge eyes, Lois Griffin body type but Persian features" \
          --tone darkly_humorous \
          --style animated_comedy \
          --content-continuity \
          --visual-continuity \
          --no-cheap \
          --mode enhanced \
          --session-id "nuclear_news_water_ep3"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Episode 3 complete!${NC}"
            sleep 10
            
            # Episode 4: International Response - Nobody Cares
            echo ""
            echo -e "${RED}${BOLD}🌍 EPISODE 4: WORLD REACTS - WITH DEVASTATING INDIFFERENCE 🌍${NC}"
            echo -e "${YELLOW}---------------------------------------------------------${NC}"
            
            python3 main.py generate \
              --mission "Nuclear News WORLD EXCLUSIVE! Maryam with sirens blaring: 'UN declares Iran water crisis NOT NUCLEAR ENOUGH TO CARE!' Cut to UN: Stewie with radiation detector: 'No plutonium in the water? BORING!' Cleveland diplomat: 'That's not radioactive... NEXT!' Maryam's hijab glowing: 'BREAKING: Urmia Lake fish achieve NUCLEAR EVOLUTION!' Show glowing mutant fish. Ticker: 'FISH DEVELOP URANIUM GILLS - STILL THIRSTY'" \
              --platform youtube \
              --duration 60 \
              --visual-style "family guy animation" \
              --theme nuclear_news \
              --character "animated news anchor: Maryam - Family Guy style Persian woman, oversized hijab, huge eyes, Lois Griffin body type but Persian features" \
              --tone darkly_humorous \
              --style animated_comedy \
              --content-continuity \
              --visual-continuity \
              --no-cheap \
              --mode enhanced \
              --session-id "nuclear_news_water_ep4"
            
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✅ Episode 4 complete!${NC}"
                sleep 10
                
                # Episode 5: The Apocalyptic Finale
                echo ""
                echo -e "${RED}${BOLD}☢️  EPISODE 5: SERIES FINALE - NUCLEAR MELTDOWN TEHRAN ☢️${NC}"
                echo -e "${YELLOW}-------------------------------------------------------${NC}"
                
                python3 main.py generate \
                  --mission "NUCLEAR NEWS FINAL MELTDOWN! Maryam (hijab radioactive green, eyes glowing): 'THIS IS IT! Tehran reaches MAXIMUM NUCLEAR THIRST!' Cutaway: Mad Max warriors with Geiger counters: 'WITNESS MY RADIATION!' *drinks glowing water* Brian-dog: 'Actually, nuclear fission—' *EXPLODES* Maryam goes FULL NUCLEAR: 'WE'RE ALL ATOMS NOW!' Epic chicken vs dehydration NUCLEAR SHOWDOWN. End card: 'NUCLEAR NEWS: WE REPORT, YOU MUTATE!' Mushroom cloud finale" \
                  --platform youtube \
                  --duration 60 \
                  --visual-style "family guy animation" \
                  --theme nuclear_news \
                  --character "animated news anchor: Maryam - Family Guy style Persian woman, hijab falling off, huge eyes, Lois Griffin body type but Persian features, disheveled" \
                  --scene "Family Guy style animated news studio MELTING DOWN, Nuclear News logos GLOWING RADIOACTIVE, news desk ON FIRE, nuclear explosion background, sirens, red alerts everywhere" \
                  --tone darkly_humorous \
                  --style animated_comedy \
                  --content-continuity \
                  --visual-continuity \
                  --no-cheap \
                  --mode enhanced \
                  --session-id "nuclear_news_water_ep5"
                
                if [ $? -eq 0 ]; then
                    echo ""
                    echo -e "${YELLOW}${BOLD}☢️  NUCLEAR NEWS WATER CRISIS SERIES COMPLETE! ☢️${NC}"
                    echo ""
                    echo -e "${CYAN}${BOLD}📁 Your 5-episode series is ready:${NC}"
                    echo -e "   ${RED}🚨${NC} Episode 1 - DEFCON THIRSTY: ${BLUE}outputs/session_nuclear_news_water_ep1/${NC}"
                    echo -e "   ${RED}⚠️${NC}  Episode 2 - COMMITTEE MELTDOWN: ${BLUE}outputs/session_nuclear_news_water_ep2/${NC}"
                    echo -e "   ${RED}💧${NC} Episode 3 - RADIOACTIVE TEARS: ${BLUE}outputs/session_nuclear_news_water_ep3/${NC}"
                    echo -e "   ${RED}🌍${NC} Episode 4 - NUCLEAR EVOLUTION: ${BLUE}outputs/session_nuclear_news_water_ep4/${NC}"
                    echo -e "   ${RED}☢️${NC}  Episode 5 - MAXIMUM MELTDOWN: ${BLUE}outputs/session_nuclear_news_water_ep5/${NC}"
                    echo ""
                    echo -e "${GREEN}${BOLD}🏆 SERIES FEATURES:${NC}"
                    echo -e "   ${PURPLE}🎨${NC} Family Guy animation style throughout"
                    echo -e "   ${YELLOW}☢️${NC}  Nuclear News branding with radiation symbols"
                    echo -e "   ${CYAN}😂${NC} Dark humor and cutaway gags"
                    echo -e "   ${PURPLE}👩${NC} Consistent character (Maryam's transformation)"
                    echo -e "   ${BLUE}💧${NC} Water crisis escalation arc"
                    echo -e "   ${GREEN}🇮🇷${NC} Persian cultural references"
                    echo ""
                    echo -e "${RED}${BOLD}💀 Dark Comedy Highlights:${NC}"
                    echo -e "   ${YELLOW}⚠️${NC}  DEFCON THIRSTY alert system"
                    echo -e "   ${YELLOW}💥${NC} Committee reaching CRITICAL MASS"
                    echo -e "   ${YELLOW}☢️${NC}  WEAPONS-GRADE tears"
                    echo -e "   ${YELLOW}🧬${NC} NUCLEAR fish evolution"
                    echo -e "   ${YELLOW}🎆${NC} ATOMIC apocalypse finale"
                    echo ""
                else
                    echo -e "${RED}❌ Episode 5 failed!${NC}"
                    exit 1
                fi
            else
                echo -e "${RED}❌ Episode 4 failed!${NC}"
                exit 1
            fi
        else
            echo -e "${RED}❌ Episode 3 failed!${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ Episode 2 failed!${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Episode 1 failed!${NC}"
    exit 1
fi

echo -e "\n${YELLOW}${BOLD}☢️  Ready for broadcast on Nuclear News - Tomorrow's Disasters Today! ☢️${NC}"