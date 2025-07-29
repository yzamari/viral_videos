#!/bin/bash

# Iran International News - Family Guy Style with News Overlay
# English version - 35 seconds each
# 6 episodes covering various Iranian crises with dark humor

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

echo "🎬 Iran International News - Family Guy Style"
echo "============================================="
echo "🎨 Family Guy animation style"
echo "📺 Professional news overlay"
echo "🌐 Language: English"
echo "⏱️  35 seconds duration (~5-6 clips of 5-8s each)"
echo ""
echo "✨ Features:"
echo "   - 6 satirical news episodes"
echo "   - Consistent anchor character (Maryam)"
echo "   - Progressive deterioration storyline"
echo "   - Professional news graphics"
echo "   - Iran International branding"
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
        --visual-style "family guy animation" \
        --tone darkly_humorous \
        --style news \
        --theme preset_news_edition \
        --no-cheap \
        --voice "en-US-Neural2-F" \
        --session-id "${session_base}_ep${ep_num}" \
        --languages en-US \
        --visual-continuity \
        --content-continuity \
        --scene "Family Guy style animated news studio, Iran International logo, professional news desk with overlay graphics"
    
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
EPISODE_MISSIONS[1]="Family Guy style animated news. Professional news overlay graphics. Iran International logo top-right. News anchor Maryam (Persian Lois Griffin with hijab, huge eyes) reports: 'BREAKING NEWS: Scientists confirm water has officially ghosted Iran. It left no forwarding address.' Show cartoon map of Iran with water droplets running away with suitcases. News ticker: 'WATER CRISIS DAY 1,847'. Peter Griffin-style official: 'Water? Never heard of her.' Citizens licking morning dew. Lower third: 'EXCLUSIVE: Dew Licking Tutorial at 11'"
EPISODE_CHARACTERS[1]="Animated news anchor Maryam - Family Guy style Persian woman with oversized hijab, huge expressive eyes, Lois Griffin body type but Persian features, professional blazer"

# Episode 2: Committee Committee Committee
EPISODE_TITLES[2]="Committee Committee Committee"
EPISODE_MISSIONS[2]="Family Guy news continues. Same anchor Maryam announces: 'BREAKING: Government unveils master plan - Committee to form committee about committees.' Professional news graphics show organizational chart exploding. Cutaway: Stewie-style minister: 'I propose we form a sub-committee!' Room of identical officials nodding. News ticker: 'COMMITTEE COUNT: ∞'. Lower third: 'EXCLUSIVE INTERVIEW: Chairman of Nothing Committee'. Maryam's eye twitches. Map shows committee buildings multiplying like cancer cells. 'This is fine' meme in corner."
EPISODE_CHARACTERS[2]="Same Maryam - consistent Family Guy Persian anchor, hijab slightly disheveled from stress, eye twitching, professional but losing patience"

# Episode 3: Economic Crisis Report
EPISODE_TITLES[3]="Economic Meltdown Special Report"
EPISODE_MISSIONS[3]="Family Guy news chaos. Maryam (hijab now crooked) reports: 'BREAKING: Rial value drops so low, mathematicians invented new numbers.' Show graph diving through floor into Earth's core. Peter Griffin economist: 'Economy is like my diet - non-existent!' Cutaway: Citizens using wheelbarrows of cash for one tomato. Quagmire-style trader: 'Giggity! I'll trade you my house for that sandwich!' News ticker: 'RIAL TO DOLLAR: 1,000,000:1 (UPDATED: 2,000,000:1)'. Lower third: 'EXPERT ADVICE: Just Print More Money!'"
EPISODE_CHARACTERS[3]="Maryam deteriorating - Family Guy Persian anchor, hijab askew, mascara running, holding stack of worthless bills, forced smile cracking"

# Episode 4: Internet Shutdown Anniversary
EPISODE_TITLES[4]="Internet Shutdown - Day 1000"
EPISODE_MISSIONS[4]="Family Guy news breakdown. Maryam (makeup smeared) announces: 'Celebrating 1000 days without Instagram! Citizens report strange symptoms: actual conversations.' Show Meg-style teenager: 'I had to... talk to my parents. THE HORROR!' Cleveland-style IT minister: 'Internet is overrated. Try smoke signals!' Cutaway: Pigeons carrying USB drives. News ticker: 'BREAKING: Youth Discover Books Exist'. Lower third: 'COMING UP: How to Like Things Without a Button'. Studio lights flicker. Maryam drinks from flask."
EPISODE_CHARACTERS[4]="Maryam unraveling - Family Guy anchor, hijab hanging off, raccoon eyes, clutching emergency flask, twitching smile, papers everywhere"

# Episode 5: Pollution Special Report
EPISODE_TITLES[5]="Tehran Air Quality - Chewable Edition"
EPISODE_MISSIONS[5]="Family Guy news apocalypse. Maryam (wearing gas mask over hijab) reports through filter: 'Today's air quality: Chunky!' Show Brian-style scientist: 'Air shouldn't have texture, but here we are.' Tehran skyline completely invisible. Herbert-style elder: 'Back in my day, we could SEE the buildings we crashed into!' Cutaway: Kids playing 'Guess That Smell'. News ticker: 'AIR QUALITY INDEX: YES'. Lower third: 'HEALTH TIP: Breathing is Optional'. Maryam coughs, pulls out second mask."
EPISODE_CHARACTERS[5]="Maryam in hazmat - Family Guy anchor in full gas mask, hijab barely visible, holding air quality meter showing skull symbol, wheezing"

# Episode 6: Election Coverage
EPISODE_TITLES[6]="Election Special - Same But Different"
EPISODE_MISSIONS[6]="Family Guy news finale. Maryam (completely disheveled) slurs: 'ELECTION RESULTS: Guy with beard wins!' Show identical candidates. Joe-style voter: 'I voted for the one with policies!' Everyone laughs. Cutaway: Ballot box labeled 'Suggestions'. Chris-style official: 'We counted all vote. Both of them!' News ticker: 'BREAKING: Democracy Postponed Due to Weather'. Lower third: 'EXCLUSIVE: Winner Promises More Committees'. Maryam removes hijab, reveals second Maryam. Both drink."
EPISODE_CHARACTERS[6]="Maryam final form - Family Guy anchor completely unhinged, hijab as cape, makeup like Joker, holding wine bottle, crazy eyes, laughing maniacally"

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
echo "🎬 News Generation Complete!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📌 Episode Summary:"
echo "   Episode 1: Water Crisis - Water has ghosted Iran"
echo "   Episode 2: Committee Madness - Committees about committees"
echo "   Episode 3: Economic Meltdown - Rial reaches Earth's core"
echo "   Episode 4: Internet Shutdown - 1000 days of digital darkness"
echo "   Episode 5: Tehran Air Quality - Chewable atmosphere"
echo "   Episode 6: Election Special - Democracy on permanent vacation"
echo ""
echo "🎭 Character Arc:"
echo "   Maryam progressively deteriorates from professional anchor"
echo "   to completely unhinged by episode 6"
echo ""
echo "💡 To run specific episodes:"
echo "   ./run_iran_news_family_guy_final.sh -e 1,3,5"
echo ""
echo "💡 To run in background:"
echo "   nohup ./run_iran_news_family_guy_final.sh -e 1,2,3,4,5,6 > iran_news_log.txt 2>&1 &"
echo "   tail -f iran_news_log.txt"
echo ""
echo "📺 'And now, back to your regularly scheduled water crisis!' - Iran International"