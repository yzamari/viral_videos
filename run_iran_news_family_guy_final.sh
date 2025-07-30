#!/bin/bash

# Iran Thirstional News - Family Guy Style with News Overlay
# English version - 35 seconds each
# 6 episodes covering various Iranian crises with dark humor
# NOW WITH ENHANCED HUMOR AND "THIRSTIONAL" BRANDING!

# Parse command line arguments
EPISODES_TO_GENERATE=()
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--episodes)
            shift
            IFS=',' read -ra EPISODES_TO_GENERATE <<< "$1"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [-e episodes]"
            echo "  -e, --episodes   Comma-separated list of episode numbers (1-6)"
            echo "                   Example: -e 1,3,5 or -e 2"
            echo ""
            echo "Available episodes:"
            echo "  1: Water Crisis - Breaking News"
            echo "  2: Committee Committee Committee"
            echo "  3: Economic Meltdown Special Report"
            echo "  4: Internet Shutdown - Day 1000"
            echo "  5: Tehran Air Quality - Chewable Edition"
            echo "  6: Election Special - Same But Different"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Default to generating all episodes if none specified
if [ ${#EPISODES_TO_GENERATE[@]} -eq 0 ]; then
    EPISODES_TO_GENERATE=(1 2 3 4 5 6)
fi

echo "💧 Iran THIRSTIONAL News - Family Guy Style 💧"
echo "============================================="
echo "🎨 Family Guy animation style with EXTRA THIRST"
echo "📺 Professional news overlay (NOW EXTRA DRY!)"
echo "🌐 Language: English (PARCHED EDITION)"
echo "⏱️  35 seconds duration (~5-6 clips of 5-8s each)"
echo ""
echo "✨ Enhanced Features:"
echo "   - 6 HILARIOUSLY satirical news episodes"
echo "   - Consistent anchor character (Maryam the Thirsty)"
echo "   - Progressive DEHYDRATION storyline"
echo "   - Professional news graphics (WITH WATER DROPS!)"
echo "   - Iran THIRSTIONAL branding (SO THIRSTY!)"
echo "   - MAXIMUM COMEDY about water crisis"
echo ""
echo "📺 Episodes to generate: ${EPISODES_TO_GENERATE[@]}"
echo ""

# Function to generate news episode
generate_news_episode() {
    local ep_num=$1
    local title=$2
    local mission=$3
    local character=$4
    local session_base=$5
    
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "📺 Episode $ep_num: $title"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "🌐 Generating episode..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    python3 main.py generate \
        --mission "$mission" \
        --character "$character" \
        --platform youtube \
        --duration 35 \
        --visual-style "family guy animation extreme satire" \
        --tone "darkly humorous absurdist hilarious" \
        --style "satirical news parody" \
        --theme preset_news_edition \
        --no-cheap \
        --voice "en-US-Neural2-F" \
        --session-id "${session_base}_ep${ep_num}" \
        --languages en-US \
        --visual-continuity \
        --content-continuity \
        --mode professional \
        --discussions enhanced \
        --scene "Family Guy style animated news studio, IRAN THIRSTIONAL logo with water drops, professional news desk with empty water cooler, overlay graphics showing hydration alerts"
    
    RESULT=$?
    
    if [ $RESULT -eq 0 ]; then
        echo "✅ Episode completed successfully!"
    else
        echo "❌ Episode failed with exit code: $RESULT"
    fi
    
    # Summary
    echo ""
    echo "📊 Episode $ep_num Generation Summary:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Status: $([ $RESULT -eq 0 ] && echo "✅ SUCCESS" || echo "❌ FAILED")"
    echo ""
    echo "Output folder: outputs/${session_base}_ep${ep_num}/"
    echo ""
    
    return 0
}

# Define all episode data
declare -a EPISODE_TITLES
declare -a EPISODE_MISSIONS
declare -a EPISODE_CHARACTERS

# Episode 1: Water Crisis Breaking News
EPISODE_TITLES[1]="Water Crisis - Breaking News"
EPISODE_MISSIONS[1]="Family Guy style animated news. Professional news overlay graphics. IRAN THIRSTIONAL logo (dripping letters) top-right. News anchor Maryam (Persian Lois Griffin with hijab, huge eyes, holding empty water bottle) reports: 'BREAKING NEWS from THIRSTIONAL NETWORK: Scientists confirm water has officially UNFRIENDED Iran on all platforms. It blocked us everywhere!' Show cartoon map of Iran as dried sponge with water droplets fleeing with passports. News ticker: 'THIRST LEVEL: SAHARA PLUS++'. Peter Griffin-style official drinking sand: 'Water is just a Western conspiracy!' Citizens doing rain dances. Lower third: 'COMING UP: Is Saliva the New Water?'"
EPISODE_CHARACTERS[1]="Animated THIRSTIONAL anchor Maryam - Family Guy style Persian woman with oversized hijab, huge thirsty eyes, Lois Griffin body type but Persian features, professional blazer with water bottle pins, visibly parched, Iran THIRSTIONAL logo on desk"

# Episode 2: Committee Committee Committee
EPISODE_TITLES[2]="Committee Committee Committee"
EPISODE_MISSIONS[2]="Family Guy news continues on THIRSTIONAL. Dehydrated Maryam (sipping air from empty glass) announces: 'BREAKING on Iran THIRSTIONAL: Government's drought solution - Committee to study why previous committee's committee failed!' Professional news graphics show organizational chart turning to dust. Cutaway: Stewie-style minister: 'I motion to form a HYDRATION committee!' Room of officials fainting from thirst. News ticker: 'COMMITTEE BUDGET: 1 TRILLION RIALS (worth: 1 water bottle)'. Lower third: 'EXCLUSIVE: Committee on Committees Now Accepting Bribes in H2O'. THIRSTIONAL logo sweating."
EPISODE_CHARACTERS[2]="Dehydrating Maryam - THIRSTIONAL anchor with hijab wilting, eye twitching from thirst, lips starting to crack, clutching empty water bottle, Iran THIRSTIONAL logo dripping behind her"

# Episode 3: Economic Crisis Report
EPISODE_TITLES[3]="Economic Meltdown Special Report"
EPISODE_MISSIONS[3]="THIRSTIONAL news chaos. Parched Maryam (hijab now a dishrag, lips cracked) croaks: 'BREAKING THIRST NEWS: Rial crashes harder than dehydrated marathon runner! Water now costs more than gold-plated lamborghini!' Show graph melting from heat. Peter Griffin economist drinking his tears: 'I'd explain inflation but my mouth is too dry!' Cutaway: Citizens trading organs for Dasani. Quagmire-style trader: 'Giggity! That's not sweat, it's LIQUID GOLD!' News ticker: 'WATER BOTTLE: 50 BILLION RIALS'. Lower third: 'IRAN THIRSTIONAL TIP: Cry Into Cups for Emergency Hydration!'"
EPISODE_CHARACTERS[3]="Parched Maryam - THIRSTIONAL anchor with hijab like dried dishrag, mascara running in dust streams, holding worthless bills and empty canteen, smile cracking like drought-stricken earth, THIRSTIONAL logo melting"

# Episode 4: Internet Shutdown Anniversary
EPISODE_TITLES[4]="Internet Shutdown - Day 1000"
EPISODE_MISSIONS[4]="Family Guy news breakdown. Maryam (makeup smeared) announces: 'Celebrating 1000 days without Instagram! Citizens report strange symptoms: actual conversations.' Show Meg-style teenager: 'I had to... talk to my parents. THE HORROR!' Cleveland-style IT minister: 'Internet is overrated. Try smoke signals!' Cutaway: Pigeons carrying USB drives. News ticker: 'BREAKING: Youth Discover Books Exist'. Lower third: 'COMING UP: How to Like Things Without a Button'. Studio lights flicker. Maryam drinks from flask."
EPISODE_CHARACTERS[4]="Desert Maryam - THIRSTIONAL anchor with hijab now tumble-weed style, raccoon eyes from dehydration, clutching flask of sand, smile like cracked desert floor, papers turning to dust, THIRSTIONAL logo barely visible through haze"

# Episode 5: Pollution Special Report
EPISODE_TITLES[5]="Tehran Air Quality - Chewable Edition"
EPISODE_MISSIONS[5]="Family Guy news apocalypse. Maryam (wearing gas mask over hijab) reports through filter: 'Today's air quality: Chunky!' Show Brian-style scientist: 'Air shouldn't have texture, but here we are.' Tehran skyline completely invisible. Herbert-style elder: 'Back in my day, we could SEE the buildings we crashed into!' Cutaway: Kids playing 'Guess That Smell'. News ticker: 'AIR QUALITY INDEX: YES'. Lower third: 'HEALTH TIP: Breathing is Optional'. Maryam coughs, pulls out second mask."
EPISODE_CHARACTERS[5]="Apocalypse Maryam - THIRSTIONAL anchor in dust storm survival gear, hijab integrated into breathing apparatus, air quality meter showing 'JUST GIVE UP', skin like leather, THIRSTIONAL logo now just outline in dust"

# Episode 6: Election Coverage
EPISODE_TITLES[6]="Election Special - Same But Different"
EPISODE_MISSIONS[6]="Family Guy news finale. Maryam (completely disheveled) slurs: 'ELECTION RESULTS: Guy with beard wins!' Show identical candidates. Joe-style voter: 'I voted for the one with policies!' Everyone laughs. Cutaway: Ballot box labeled 'Suggestions'. Chris-style official: 'We counted all vote. Both of them!' News ticker: 'BREAKING: Democracy Postponed Due to Weather'. Lower third: 'EXCLUSIVE: Winner Promises More Committees'. Maryam removes hijab, reveals second Maryam. Both drink."
EPISODE_CHARACTERS[6]="Dust Cloud Maryam - THIRSTIONAL anchor literally disintegrating, hijab floating like ghost, face like ancient mummy, holding bottle of mirages, eyes just hollow sockets, laughing sand, THIRSTIONAL logo crumbling"

# Add more episodes here as needed...

# Generate selected episodes
for ep in "${EPISODES_TO_GENERATE[@]}"; do
    if [ -n "${EPISODE_TITLES[$ep]}" ]; then
        generate_news_episode "$ep" \
            "${EPISODE_TITLES[$ep]}" \
            "${EPISODE_MISSIONS[$ep]}" \
            "${EPISODE_CHARACTERS[$ep]}" \
            "iran_news_family_guy"
    else
        echo "⚠️  Episode $ep not defined yet. Available episodes: 1, 2, 3, 4, 5, 6"
    fi
done

echo ""
echo "💧 IRAN THIRSTIONAL News Generation Complete! 💧"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "🏜️ THIRST LEVEL: MAXIMUM"
echo ""
echo "📌 Episode Summary (NOW WITH 200% MORE THIRST!):"
echo "   Episode 1: Water Crisis - Water UNFRIENDED Iran on all platforms!"
echo "   Episode 2: Committee Madness - Committees to study why we're THIRSTY"
echo "   Episode 3: Economic Meltdown - Water costs more than GOLD LAMBORGHINI"
echo "   Episode 4: Internet Shutdown - Too DEHYDRATED to post thirst traps"
echo "   Episode 5: Tehran Air Quality - Air is CRUNCHY, water is MYTHICAL"  
echo "   Episode 6: Election Special - Democracy status: DEHYDRATED"
echo ""
echo "🎭 Character Arc:"
echo "   Maryam progressively DEHYDRATES from professional anchor"
echo "   to literal DUST CLOUD by episode 6"
echo "   (It's a metaphor... or is it? 🏜️)"
echo ""
echo "💡 To run specific episodes:"
echo "   ./run_iran_news_family_guy_final.sh -e 1,3,5"
echo ""
echo "💡 To run in background:"
echo "   nohup ./run_iran_news_family_guy_final.sh -e 1,2,3,4,5,6 > iran_news_log.txt 2>&1 &"
echo "   tail -f iran_news_log.txt"
echo ""
echo "💧 'Stay THIRSTY, my friends!' - Iran THIRSTIONAL News Network 🏜️"