#!/bin/bash
# Force use of modern bash for associative arrays
if [[ ${BASH_VERSION%%.*} -lt 4 ]]; then
    echo "⚠️  This script requires bash 4.0+. macOS default is bash 3.x"
    echo "Installing modern bash via homebrew..."
    if command -v brew >/dev/null 2>&1; then
        brew install bash
        exec /usr/local/bin/bash "$0" "$@"
    else
        echo "❌ Please install bash 4+ or run: brew install bash"
        exit 1
    fi
fi
# Generate Israeli Prime Ministers Educational Series
# Each episode teaches about one PM with historically accurate representation

echo "🇮🇱 Israeli Prime Ministers Educational Series Production"
echo "========================================================"

# Configuration
export GEMINI_API_KEY="${GEMINI_API_KEY}"
export GOOGLE_CLOUD_PROJECT="${GOOGLE_CLOUD_PROJECT}"

# Activate virtual environment if exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Series configuration
SERIES_NAME="israeli_pm_marvel"
PLATFORM="instagram"
STYLE="marvel cinematic epic"  # Marvel superhero style
VOICE="en-US-Journey-D"        # Epic cinematic voice
LANGUAGE="en-US"               # American English
THEME="preset_marvel"          # Marvel theme with overlays

# Create series directory
SERIES_DIR="outputs/${SERIES_NAME}_series_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$SERIES_DIR"

# Log file
LOG_FILE="$SERIES_DIR/series_production.log"

# Episode definitions - Marvel-style inspiring and funny missions
declare -A EPISODES=(
    [1]="Create an EPIC Marvel-style adventure about David Ben-Gurion, the FOUNDING AVENGER who assembled Israel's first superhero team in 1948! Show him declaring independence with THUNDEROUS power, making the desert bloom with his KIBBUTZ POWERS, and his wild Einstein-like hair giving him wisdom abilities! Make it HILARIOUS with his short stature but GIANT personality, inspiring viewers with his unstoppable determination!"
    [2]="Create a MARVEL blockbuster about Golda Meir, the IRON GRANDMOTHER with the power to destroy enemies with her sharp wit and Milwaukee accent! Show her as the ONLY female superhero PM who could make world leaders tremble with her grandma stare, chain-smoking her way through crises, and serving tea while planning military operations! Make it FUNNY and INSPIRING showing her rise from Milwaukee teacher to Israel's most badass leader!"
    [3]="Create an ACTION-PACKED Marvel story about Menachem Begin, the UNDERGROUND FIGHTER turned PEACE WARRIOR! Show his transformation from rebel leader with STEALTH powers to the peacemaker who could FLY to Camp David! Include HILARIOUS scenes of his Polish formality meeting Egyptian culture, his thick glasses giving him VISION powers, and his emotional Nobel Prize moment! INSPIRE viewers with his journey from fighter to peacemaker!"
    [4]="Create a MARVEL EPIC about Yitzhak Rabin, the SHY WARRIOR with the power of military strategy and peace vision! Show him as the reluctant hero who led the Six-Day War with TACTICAL GENIUS, then transformed into the PEACE AVENGER shaking hands with former enemies! Include FUNNY moments of his awkward public speaking but BRILLIANT military mind! INSPIRE with his courage to change from warrior to peacemaker!"
    [5]="Create a CINEMATIC Marvel adventure about Benjamin Netanyahu, the MEDIA MASTER with communication superpowers and political immortality! Show him speaking at the UN with THUNDEROUS eloquence, surviving political battles like a phoenix, and his EPIC hair that defies aging! Make it ENTERTAINING with his American swagger meets Israeli chutzpah! Show his record-breaking leadership inspiring persistence!"
    [6]="Create an EXPLOSIVE Marvel tale about Ariel Sharon, the BULLDOZER with unstoppable force powers! Show him as the military TITAN who could reshape maps, the farmer who made deserts bloom, and the pragmatic leader who SHOCKED everyone with the Gaza withdrawal! Include FUNNY scenes of him eating while making crucial decisions! INSPIRE with his transformation from hawk to surprising peacemaker!"
    [7]="Create a HEARTWARMING Marvel story about Shimon Peres, the ETERNAL OPTIMIST with future-vision powers and technological genius! Show him serving Israel for 70 YEARS, never giving up despite losses, inventing Israel's nuclear program, and becoming the startup nation visionary! Make it FUNNY with his endless optimism even at 90+! INSPIRE viewers to never stop dreaming and innovating!"
    [8]="Create a SOPHISTICATED Marvel adventure about Moshe Sharett, the DIPLOMATIC MASTERMIND with multilingual powers and negotiation skills! Show him as Israel's FIRST Foreign Minister building relationships with his scholarly charm, speaking 8 languages, and laying diplomatic foundations! Include HUMOROUS contrasts with Ben-Gurion's rough style! INSPIRE with his belief in diplomacy and education!"
)

# Character descriptions - Marvel superhero versions
declare -A CHARACTERS=(
    [1]="David Ben-Gurion as FOUNDING AVENGER: Short but MIGHTY superhero with wild Einstein-like white hair that GLOWS with wisdom power, wearing high-tech kibbutz armor, energy glasses that shoot determination beams, cape made from Declaration of Independence, standing heroically despite height"
    [2]="Golda Meir as IRON GRANDMOTHER: Badass elderly superhero with steel-grey hair in power bun, eyes that shoot truth lasers, armor-plated dress with Star of David arc reactor, wielding a teacup of justice and cigarette of destruction, grandma sneakers that can kick butt"
    [3]="Menachem Begin as TRANSFORMATION WARRIOR: Sleek hero with morphing abilities, thick power glasses that see through deception, suit that transforms from underground fighter gear to peace negotiator armor, Polish accent that charms enemies, Nobel Peace Prize as power source"
    [4]="Yitzhak Rabin as TACTICAL GENIUS: Tall muscular warrior in military super-suit, grey hair styled for aerodynamics, jaw of steel, hands that can build peace or destroy enemies, shy smile that disarms opponents, Six-Day War medals as power amplifiers"
    [5]="Benjamin Netanyahu as MEDIA MASTER: Charismatic hero with perfectly styled silver hair that never moves, communication suit with built-in teleprompter, voice that thunders across dimensions, phoenix wings for political resurrection, American-Israeli fusion powers"
    [6]="Ariel Sharon as THE BULLDOZER: Massive tank-like hero, white hair like snow avalanche, farm-warrior hybrid armor, hands that reshape reality, strategic eating powers, transformation ability from hawk to dove, ground-shaking presence"
    [7]="Shimon Peres as ETERNAL OPTIMIST: Ageless hero with future-vision goggles, white hair of wisdom, high-tech suit powered by dreams and innovation, startup nation energy field, Nobel Prize shield, levitation through pure optimism"
    [8]="Moshe Sharett as DIPLOMATIC MASTERMIND: Sophisticated hero in multi-cultural armor, translation visor for 8 languages, negotiation gauntlets, scholarly force field, mustache of distinction, books that transform into weapons of wisdom"
)

# Function to generate single episode
generate_episode() {
    local episode_num=$1
    local mission="${EPISODES[$episode_num]}"
    local character="${CHARACTERS[$episode_num]}"
    local session_id="${SERIES_NAME}_ep${episode_num}"
    
    echo ""
    echo "🎬 Generating Episode $episode_num..."
    echo "Character: $character"
    echo "Session: $session_id"
    
    # Run generation with Marvel superhero character
    python3 main.py generate \
        --mission "$mission" \
        --duration 40 \
        --style "$STYLE" \
        --character "$character" \
        --platform "$PLATFORM" \
        --voice "$VOICE" \
        --languages "$LANGUAGE" \
        --session-id "$session_id" \
        --theme "$THEME" \
        --visual-style "marvel superhero epic" \
        --tone "inspiring funny engaging" \
        --mode "professional" \
        --discussions "enhanced" \
        --visual-continuity \
        --content-continuity \
        --no-cheap \
        2>&1 | tee -a "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        echo "✅ Episode $episode_num completed successfully!" | tee -a "$LOG_FILE"
        
        # Copy to series directory
        LATEST_OUTPUT=$(ls -td outputs/${session_id}_* 2>/dev/null | head -1)
        if [ -n "$LATEST_OUTPUT" ]; then
            FINAL_VIDEO=$(find "$LATEST_OUTPUT/final_output" -name "*.mp4" 2>/dev/null | head -1)
            if [ -n "$FINAL_VIDEO" ]; then
                cp "$FINAL_VIDEO" "$SERIES_DIR/episode_${episode_num}.mp4"
                echo "📦 Saved Episode $episode_num to series directory" | tee -a "$LOG_FILE"
            fi
        fi
        
        # Delay between episodes
        if [ $episode_num -lt 8 ]; then
            echo "⏰ Waiting 30 seconds before next episode..." | tee -a "$LOG_FILE"
            sleep 30
        fi
        
        return 0
    else
        echo "❌ Episode $episode_num failed!" | tee -a "$LOG_FILE"
        return 1
    fi
}

# Start production
echo "🦸 Starting Israeli PM MARVEL SUPERHERO Series production!" | tee "$LOG_FILE"
echo "💥 EPIC, FUNNY, and INSPIRING adventures await!" | tee -a "$LOG_FILE"
echo "Series directory: $SERIES_DIR" | tee -a "$LOG_FILE"
echo "Style: Marvel Cinematic Epic with Overlays" | tee -a "$LOG_FILE"
echo "Voice: Epic Cinematic ($VOICE)" | tee -a "$LOG_FILE"
echo "Theme: Marvel with dynamic overlays" | tee -a "$LOG_FILE"
echo "Mode: Professional (22 AI agents)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Track success/failure
SUCCESS_COUNT=0
FAILED_EPISODES=""

# Generate all episodes
for i in {1..8}; do
    if generate_episode $i; then
        ((SUCCESS_COUNT++))
    else
        FAILED_EPISODES="$FAILED_EPISODES $i"
    fi
done

# Summary
echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "PRODUCTION SUMMARY" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "Total episodes: 8" | tee -a "$LOG_FILE"
echo "Successful: $SUCCESS_COUNT" | tee -a "$LOG_FILE"
echo "Failed: $((8 - SUCCESS_COUNT))" | tee -a "$LOG_FILE"

if [ -n "$FAILED_EPISODES" ]; then
    echo "Failed episodes:$FAILED_EPISODES" | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"
echo "Series directory: $SERIES_DIR" | tee -a "$LOG_FILE"
echo "🦸✨ Israeli PM MARVEL SUPERHERO Series production complete!" | tee -a "$LOG_FILE"
echo "💥 8 EPIC episodes of inspiring, funny superhero adventures!" | tee -a "$LOG_FILE"
echo "🎬 Ready to go VIRAL with Marvel-style overlays!" | tee -a "$LOG_FILE"