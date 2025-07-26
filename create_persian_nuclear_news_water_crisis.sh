#!/bin/bash

# Nuclear News - Persian Animation Style Water Crisis Series
# In the Shadow of the Cypress animation style with Persian cultural elements
# 5 episodes x 60 seconds each
# Features elegant Persian news desk overlays rendered on top of video

# Set colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
GREEN='\033[0;32m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${YELLOW}${BOLD}☢️  NUCLEAR NEWS - PERSIAN ANIMATION WATER CRISIS SERIES ☢️${NC}"
echo -e "${RED}============================================================${NC}"
echo -e "${BLUE}📺 Serious Yet Poetic News Broadcast${NC}"
echo -e "${PURPLE}🎨 In the Shadow of the Cypress Animation Style${NC}"
echo -e "${CYAN}💧 Water Crisis Theme${NC}"
echo -e "${YELLOW}🌸 Persian Cultural Elements${NC}"
echo ""

# Activate virtual environment
source .venv/bin/activate

# Episode 1: Breaking News - Water Departs Like Birds
echo -e "\n${RED}${BOLD}🚨 EPISODE 1: BREAKING NEWS - WATER TAKES FLIGHT 🚨${NC}"
echo -e "${YELLOW}-----------------------------------------------------------${NC}"

python main.py generate \
  --mission "Persian animated news in 'In the Shadow of the Cypress' style. NUCLEAR NEWS logo with pomegranate and cypress motifs. News anchor Maryam (elegant Persian features, artistic hijab with paisley patterns, expressive almond eyes, graceful hand gestures) at ornate news desk with Persian geometric tiles: 'In the name of the Merciful, this is Nuclear News. Our precious water has taken flight from Iran like migrating birds. We have reached the station of CRITICAL THIRST.' Show artistic map with water droplets transforming into birds flying away. Traditional official: 'The matter of water is... under consideration.' Citizens reaching toward mirages in stylized desert. Persian calligraphy ticker: 'URGENT: HISTORIC WATER CRISIS UNFOLDS'" \
  --platform youtube \
  --duration 60 \
  --visual-style "persian miniature animation" \
  --theme nuclear_news \
  --character "animated news anchor: Maryam - elegant Persian woman with artistic hijab featuring paisley patterns, expressive almond-shaped eyes, graceful hand movements, In the Shadow of the Cypress animation style" \
  --scene "Persian animated news studio with intricate geometric tile work, carved wooden desk with arabesque patterns, NUCLEAR NEWS logos with Persian design elements, illuminated manuscripts in background, warm golden lighting" \
  --tone serious_yet_poetic \
  --style animated_documentary \
  --no-cheap \
  --mode enhanced \
  --session-id "persian_nuclear_news_ep1"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Episode 1 complete!${NC}"
    sleep 10

    # Episode 2: Government Response - The Garden of Committees
    echo ""
    echo -e "${RED}${BOLD}⚠️  EPISODE 2: THE GARDEN OF COMMITTEES ⚠️${NC}"
    echo -e "${YELLOW}------------------------------------------------------------------${NC}"
    
    python main.py generate \
      --mission "Persian animation style. Nuclear News anchor Maryam with pomegranate brooch announces: 'Dear viewers, our government has planted a garden... of committees!' Cutaway: Minister in traditional formal attire waters a tree that grows committee documents instead of leaves: 'We shall cultivate solutions through proper channels!' Officials sit in circle passing papers endlessly like a Sufi dance. Maryam: 'The committee tree bears no fruit, only more committees.' Persian miniature style organizational chart spirals into infinity. Calligraphy ticker: 'COMMITTEE COUNT EXCEEDS STARS IN SKY'" \
      --platform youtube \
      --duration 60 \
      --visual-style "persian miniature animation" \
      --theme nuclear_news \
      --character "animated news anchor: Maryam - elegant Persian woman with artistic hijab featuring paisley patterns, expressive almond-shaped eyes, graceful hand movements, In the Shadow of the Cypress animation style" \
      --scene "Persian animated news studio with intricate geometric tile work, carved wooden desk with arabesque patterns, NUCLEAR NEWS logos with Persian design elements, illuminated manuscripts in background, warm golden lighting" \
      --tone serious_yet_poetic \
      --style animated_documentary \
      --content-continuity \
      --visual-continuity \
      --no-cheap \
      --mode enhanced \
      --session-id "persian_nuclear_news_ep2"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Episode 2 complete!${NC}"
        sleep 10
        
        # Episode 3: Citizens' Ingenuity - Tears of the Desert
        echo ""
        echo -e "${RED}${BOLD}💧 EPISODE 3: TEARS OF THE DESERT 💧${NC}"
        echo -e "${YELLOW}----------------------------------------------------------${NC}"
        
        python main.py generate \
          --mission "Nuclear News presents: Citizens' remarkable adaptations! Maryam with sorrow in her eyes: 'Our people have become alchemists of survival.' Persian miniature style: Father in traditional clothing collects family tears in ornate glass vessels: 'Each tear is a pearl of hope!' Mother: 'Hossein, save your sorrow for tomorrow!' Neighbor with Persian rug shop: 'I'm distilling morning dew from my carpets!' Maryam: 'Poetry is born from hardship.' Show tear collection becoming art installation. Ticker: 'TEAR MERCHANTS OPEN IN BAZAAR'" \
          --platform youtube \
          --duration 60 \
          --visual-style "persian miniature animation" \
          --theme nuclear_news \
          --character "animated news anchor: Maryam - elegant Persian woman with artistic hijab featuring paisley patterns, expressive almond-shaped eyes, graceful hand movements, In the Shadow of the Cypress animation style" \
          --scene "Persian animated news studio with intricate geometric tile work, carved wooden desk with arabesque patterns, NUCLEAR NEWS logos with Persian design elements, illuminated manuscripts in background, warm golden lighting" \
          --tone serious_yet_poetic \
          --style animated_documentary \
          --content-continuity \
          --visual-continuity \
          --no-cheap \
          --mode enhanced \
          --session-id "persian_nuclear_news_ep3"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Episode 3 complete!${NC}"
            sleep 10
            
            # Episode 4: International Response - The Silent Caravan
            echo ""
            echo -e "${RED}${BOLD}🌍 EPISODE 4: THE SILENT CARAVAN 🌍${NC}"
            echo -e "${YELLOW}---------------------------------------------------------${NC}"
            
            python main.py generate \
              --mission "Nuclear News international desk! Maryam with diplomatic scarf: 'The world watches our thirst like a Persian miniature - beautiful but distant.' UN assembly in Persian art style: Representatives admire the 'aesthetic of suffering.' European diplomat: 'Such poetic drought!' American official checking phone: 'No oil in the water? Not interested.' Maryam's voice breaks: 'Lake Urmia's fish now swim in sand, creating new mythology.' Show surreal fish swimming through desert air. Ticker: 'INTERNATIONAL AID: THOUGHTS AND PRAYERS ONLY'" \
              --platform youtube \
              --duration 60 \
              --visual-style "persian miniature animation" \
              --theme nuclear_news \
              --character "animated news anchor: Maryam - elegant Persian woman with artistic hijab featuring paisley patterns, expressive almond-shaped eyes, graceful hand movements, In the Shadow of the Cypress animation style" \
              --scene "Persian animated news studio with intricate geometric tile work, carved wooden desk with arabesque patterns, NUCLEAR NEWS logos with Persian design elements, illuminated manuscripts in background, warm golden lighting" \
              --tone serious_yet_poetic \
              --style animated_documentary \
              --content-continuity \
              --visual-continuity \
              --no-cheap \
              --mode enhanced \
              --session-id "persian_nuclear_news_ep4"
            
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✅ Episode 4 complete!${NC}"
                sleep 10
                
                # Episode 5: The Desert Blooms - A Mystical Finale
                echo ""
                echo -e "${RED}${BOLD}☢️  EPISODE 5: WHEN THE DESERT BLOOMS ☢️${NC}"
                echo -e "${YELLOW}-------------------------------------------------------${NC}"
                
                python main.py generate \
                  --mission "NUCLEAR NEWS FINALE! Maryam (hijab flowing like water, tears of gold): 'From the depth of thirst, a strange garden grows.' Surreal sequence: Tehran transforms into Persepolis of mirages. Citizens dance with dust devils in Sufi circles. Ancient poet appears: 'We asked for water, but found ourselves instead.' Maryam transcends into calligraphy: 'Perhaps this is how civilizations become legends - not with floods, but with thirst.' Final shot: Cypress tree growing from cracked earth, bearing water drops like fruit. End card in Persian script: 'NUCLEAR NEWS: WHERE REALITY MEETS MYTHOLOGY'" \
                  --platform youtube \
                  --duration 60 \
                  --visual-style "persian miniature animation" \
                  --theme nuclear_news \
                  --character "animated news anchor: Maryam - elegant Persian woman, hijab flowing like water with golden threads, tears of liquid gold, transcendent expression, becoming one with calligraphy" \
                  --scene "Persian news studio transforming into mystical landscape, desk becoming ancient stone, tiles morphing into star patterns, manuscripts floating, ethereal golden light, surreal Persian garden emerging" \
                  --tone mystical_philosophical \
                  --style animated_poetry \
                  --content-continuity \
                  --visual-continuity \
                  --no-cheap \
                  --mode enhanced \
                  --session-id "persian_nuclear_news_ep5"
                
                if [ $? -eq 0 ]; then
                    echo ""
                    echo -e "${YELLOW}${BOLD}🌸 PERSIAN NUCLEAR NEWS SERIES COMPLETE! 🌸${NC}"
                    echo ""
                    echo -e "${CYAN}${BOLD}📁 Your 5-episode series is ready:${NC}"
                    echo -e "   ${RED}🕊️${NC} Episode 1 - Water Takes Flight: ${BLUE}outputs/session_persian_nuclear_news_ep1/${NC}"
                    echo -e "   ${RED}🌳${NC} Episode 2 - Garden of Committees: ${BLUE}outputs/session_persian_nuclear_news_ep2/${NC}"
                    echo -e "   ${RED}💧${NC} Episode 3 - Tears of the Desert: ${BLUE}outputs/session_persian_nuclear_news_ep3/${NC}"
                    echo -e "   ${RED}🌍${NC} Episode 4 - The Silent Caravan: ${BLUE}outputs/session_persian_nuclear_news_ep4/${NC}"
                    echo -e "   ${RED}🌸${NC} Episode 5 - When Desert Blooms: ${BLUE}outputs/session_persian_nuclear_news_ep5/${NC}"
                    echo ""
                    echo -e "${GREEN}${BOLD}🏆 SERIES FEATURES:${NC}"
                    echo -e "   ${PURPLE}🎨${NC} In the Shadow of the Cypress animation style"
                    echo -e "   ${YELLOW}🌸${NC} Persian cultural elements and poetry"
                    echo -e "   ${CYAN}📿${NC} Mystical and philosophical themes"
                    echo -e "   ${PURPLE}👩${NC} Maryam's spiritual transformation"
                    echo -e "   ${BLUE}💧${NC} Water crisis as metaphor"
                    echo -e "   ${GREEN}🇮🇷${NC} Authentic Persian aesthetics"
                    echo ""
                    echo -e "${RED}${BOLD}🎭 Poetic Highlights:${NC}"
                    echo -e "   ${YELLOW}🕊️${NC} Water departing like migrating birds"
                    echo -e "   ${YELLOW}🌳${NC} Committee tree bearing paper fruit"
                    echo -e "   ${YELLOW}💧${NC} Tears becoming pearls of hope"
                    echo -e "   ${YELLOW}🐟${NC} Fish swimming through desert air"
                    echo -e "   ${YELLOW}🌸${NC} Desert blooming into mythology"
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

echo -e "\n${YELLOW}${BOLD}🌸 Ready for broadcast on Nuclear News - Where Reality Meets Poetry! 🌸${NC}"