#!/bin/bash

# Nuclear News - Persian Animation Style Water Crisis Series (TikTok Version)
# In the Shadow of the Cypress animation style with authentic Persian cultural elements
# 5 episodes x 40 seconds each for TikTok vertical format
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

echo -e "${YELLOW}${BOLD}☢️  NUCLEAR NEWS - PERSIAN ANIMATION (TIKTOK) ☢️${NC}"
echo -e "${RED}============================================================${NC}"
echo -e "${BLUE}📱 TikTok Vertical Format (9:16)${NC}"
echo -e "${PURPLE}🎨 In the Shadow of the Cypress Animation Style${NC}"
echo -e "${CYAN}⏱️  40-Second Episodes${NC}"
echo -e "${YELLOW}🌸 Authentic Persian Visual Elements${NC}"
echo ""

# Activate virtual environment
source .venv/bin/activate

# Episode 1: Breaking News - Water Departs Like Birds
echo -e "\n${RED}${BOLD}🚨 EPISODE 1: BREAKING NEWS - WATER TAKES FLIGHT 🚨${NC}"
echo -e "${YELLOW}-----------------------------------------------------------${NC}"

python main.py generate \
  --mission "Create Persian animation exactly like 'In the Shadow of the Cypress' movie style - muted earth tones, watercolor textures, flat 2D characters with minimal shading, traditional Persian clothing patterns. NUCLEAR NEWS in Persian calligraphy. News anchor Maryam (flat 2D design, earth-tone hijab with traditional motifs, minimal facial features like the movie) at simple desk: 'بسم الله الرحمن الرحیم (In the name of God). This is Nuclear News. Our water flies away like birds.' Show watercolor-style map with simple bird shapes. Official in traditional clothing (flat design): 'The matter is... complex.' Citizens as simple silhouettes. Use exact visual style from 'In the Shadow of the Cypress' - no modern animation, only traditional Persian art." \
  --platform tiktok \
  --duration 40 \
  --visual-style "In the Shadow of the Cypress movie style - watercolor textures, flat 2D, earth tones" \
  --theme nuclear_news \
  --character "news anchor: Maryam - flat 2D design like In the Shadow of the Cypress movie, minimal facial features, earth-tone hijab, traditional Persian woman" \
  --scene "Simple Persian news desk with watercolor texture background, muted earth tones, flat 2D design exactly like In the Shadow of the Cypress movie, minimal details, traditional patterns" \
  --tone poetic_serious \
  --style artistic_documentary \
  --no-cheap \
  --mode enhanced \
  --session-id "persian_nuclear_tiktok_ep1"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Episode 1 complete!${NC}"
    sleep 10

    # Episode 2: Government Response - The Garden of Committees
    echo ""
    echo -e "${RED}${BOLD}⚠️  EPISODE 2: THE GARDEN OF COMMITTEES ⚠️${NC}"
    echo -e "${YELLOW}------------------------------------------------------------------${NC}"
    
    python main.py generate \
      --mission "In the Shadow of the Cypress exact visual style. Maryam (flat 2D, watercolor texture): 'Government plants committee gardens.' Show minister as flat silhouette watering paper tree with traditional Persian garden in background (muted greens, browns). Papers float like leaves in watercolor style. Everything flat 2D with texture overlays, no gradients, no modern effects. Exact movie style: characters are simple shapes with minimal detail, backgrounds are textured washes, movement is minimal. Persian text overlays in traditional calligraphy." \
      --platform tiktok \
      --duration 40 \
      --visual-style "In the Shadow of the Cypress movie style - watercolor textures, flat 2D, earth tones" \
      --theme nuclear_news \
      --character "news anchor: Maryam - flat 2D design like In the Shadow of the Cypress movie, minimal facial features, earth-tone hijab, traditional Persian woman" \
      --scene "Simple Persian news desk with watercolor texture background, muted earth tones, flat 2D design exactly like In the Shadow of the Cypress movie, minimal details, traditional patterns" \
      --tone poetic_serious \
      --style artistic_documentary \
      --content-continuity \
      --visual-continuity \
      --no-cheap \
      --mode enhanced \
      --session-id "persian_nuclear_tiktok_ep2"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Episode 2 complete!${NC}"
        sleep 10
        
        # Episode 3: Citizens' Ingenuity - Tears of the Desert
        echo ""
        echo -e "${RED}${BOLD}💧 EPISODE 3: TEARS OF THE DESERT 💧${NC}"
        echo -e "${YELLOW}----------------------------------------------------------${NC}"
        
        python main.py generate \
          --mission "Pure In the Shadow of the Cypress style: Citizens as flat paper cutout figures collecting tears in traditional vessels. Maryam (watercolor texture, minimal features): 'People harvest sorrow.' Father figure is simple brown shape with turban, mother in patterned chador (flat colors). Tears are simple blue dots. Background is textured paper with Persian patterns. No shading, no 3D effects, only flat shapes with watercolor textures exactly like the movie. Movement is minimal, like animated paper." \
          --platform tiktok \
          --duration 40 \
          --visual-style "In the Shadow of the Cypress movie style - watercolor textures, flat 2D, earth tones" \
          --theme nuclear_news \
          --character "news anchor: Maryam - flat 2D design like In the Shadow of the Cypress movie, minimal facial features, earth-tone hijab, traditional Persian woman" \
          --scene "Simple Persian news desk with watercolor texture background, muted earth tones, flat 2D design exactly like In the Shadow of the Cypress movie, minimal details, traditional patterns" \
          --tone poetic_serious \
          --style artistic_documentary \
          --content-continuity \
          --visual-continuity \
          --no-cheap \
          --mode enhanced \
          --session-id "persian_nuclear_tiktok_ep3"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Episode 3 complete!${NC}"
            sleep 10
            
            # Episode 4: International Response - The Silent Caravan
            echo ""
            echo -e "${RED}${BOLD}🌍 EPISODE 4: THE SILENT CARAVAN 🌍${NC}"
            echo -e "${YELLOW}---------------------------------------------------------${NC}"
            
            python main.py generate \
              --mission "In the Shadow of the Cypress exact style: UN assembly as flat paper cutouts in muted blues and grays. Diplomats are simple geometric shapes. Maryam (watercolor wash effect): 'World watches like distant stars.' Show Urmia lake as textured paper with simple fish shapes swimming in air. All elements are flat 2D cutouts with watercolor textures, no modern animation techniques. Colors are all muted earth tones: browns, ochres, dusty blues. Exactly replicate the movie's handmade paper animation aesthetic." \
              --platform tiktok \
              --duration 40 \
              --visual-style "In the Shadow of the Cypress movie style - watercolor textures, flat 2D, earth tones" \
              --theme nuclear_news \
              --character "news anchor: Maryam - flat 2D design like In the Shadow of the Cypress movie, minimal facial features, earth-tone hijab, traditional Persian woman" \
              --scene "Simple Persian news desk with watercolor texture background, muted earth tones, flat 2D design exactly like In the Shadow of the Cypress movie, minimal details, traditional patterns" \
              --tone poetic_serious \
              --style artistic_documentary \
              --content-continuity \
              --visual-continuity \
              --no-cheap \
              --mode enhanced \
              --session-id "persian_nuclear_tiktok_ep4"
            
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✅ Episode 4 complete!${NC}"
                sleep 10
                
                # Episode 5: The Desert Blooms - A Mystical Finale
                echo ""
                echo -e "${RED}${BOLD}☢️  EPISODE 5: WHEN THE DESERT BLOOMS ☢️${NC}"
                echo -e "${YELLOW}-------------------------------------------------------${NC}"
                
                python main.py generate \
                  --mission "In the Shadow of the Cypress finale: Maryam dissolves into Persian calligraphy (flat ink strokes on paper). Desert transforms into ancient manuscript pages with gold leaf accents (flat, no shine). Citizens become geometric patterns dancing in circles. Cypress tree is simple black silhouette with blue water drops as flat circles. All elements are paper cutouts with watercolor washes. Final shot: manuscript page closing. Use only traditional Persian manuscript colors: deep blues, gold ochre, burgundy, black ink. Exact movie style - handmade paper animation aesthetic." \
                  --platform tiktok \
                  --duration 40 \
                  --visual-style "In the Shadow of the Cypress movie style - watercolor textures, flat 2D, earth tones" \
                  --theme nuclear_news \
                  --character "news anchor: Maryam transforming into calligraphy - flat 2D design dissolving into Persian script" \
                  --scene "News desk becoming manuscript page, all elements transforming into traditional Persian art, flat 2D paper cutout style like In the Shadow of the Cypress" \
                  --tone mystical_philosophical \
                  --style artistic_poetry \
                  --content-continuity \
                  --visual-continuity \
                  --no-cheap \
                  --mode enhanced \
                  --session-id "persian_nuclear_tiktok_ep5"
                
                if [ $? -eq 0 ]; then
                    echo ""
                    echo -e "${YELLOW}${BOLD}🌸 PERSIAN NUCLEAR NEWS TIKTOK SERIES COMPLETE! 🌸${NC}"
                    echo ""
                    echo -e "${CYAN}${BOLD}📁 Your 5-episode TikTok series is ready:${NC}"
                    echo -e "   ${RED}🕊️${NC} Episode 1 - Water Takes Flight: ${BLUE}outputs/session_persian_nuclear_tiktok_ep1/${NC}"
                    echo -e "   ${RED}🌳${NC} Episode 2 - Garden of Committees: ${BLUE}outputs/session_persian_nuclear_tiktok_ep2/${NC}"
                    echo -e "   ${RED}💧${NC} Episode 3 - Tears of the Desert: ${BLUE}outputs/session_persian_nuclear_tiktok_ep3/${NC}"
                    echo -e "   ${RED}🌍${NC} Episode 4 - The Silent Caravan: ${BLUE}outputs/session_persian_nuclear_tiktok_ep4/${NC}"
                    echo -e "   ${RED}🌸${NC} Episode 5 - When Desert Blooms: ${BLUE}outputs/session_persian_nuclear_tiktok_ep5/${NC}"
                    echo ""
                    echo -e "${GREEN}${BOLD}🏆 SERIES FEATURES:${NC}"
                    echo -e "   ${PURPLE}🎨${NC} Exact 'In the Shadow of the Cypress' visual style"
                    echo -e "   ${YELLOW}📱${NC} TikTok vertical format (9:16)"
                    echo -e "   ${CYAN}⏱️${NC}  40-second episodes"
                    echo -e "   ${PURPLE}🎭${NC} Flat 2D paper cutout animation"
                    echo -e "   ${BLUE}🎨${NC} Watercolor textures and earth tones"
                    echo -e "   ${GREEN}📜${NC} Traditional Persian artistic elements"
                    echo ""
                    echo -e "${RED}${BOLD}🎭 Artistic Elements:${NC}"
                    echo -e "   ${YELLOW}📄${NC} Paper cutout characters"
                    echo -e "   ${YELLOW}🎨${NC} Watercolor wash backgrounds"
                    echo -e "   ${YELLOW}🏛️${NC} Minimal geometric shapes"
                    echo -e "   ${YELLOW}🖌️${NC} Persian calligraphy integration"
                    echo -e "   ${YELLOW}🍂${NC} Muted earth tone palette"
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

echo -e "\n${YELLOW}${BOLD}🌸 Ready for TikTok - Authentic Persian Animation! 🌸${NC}"