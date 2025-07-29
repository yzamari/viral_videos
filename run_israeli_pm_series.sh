#!/bin/bash
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
SERIES_NAME="israeli_pm_education"
PLATFORM="instagram"
STYLE="realistic documentary"  # Realistic style for historical accuracy
VOICE="en-IN-Wavenet-A"       # Indian English narrator
LANGUAGE="en-IN"               # Indian English

# Create series directory
SERIES_DIR="outputs/${SERIES_NAME}_series_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$SERIES_DIR"

# Log file
LOG_FILE="$SERIES_DIR/series_production.log"

# Episode definitions - Concise missions for AI creativity
declare -A EPISODES=(
    [1]="Teach about David Ben-Gurion, Israel's founding father who declared independence in 1948"
    [2]="Explore Golda Meir, Israel's Iron Lady and only female Prime Minister"
    [3]="Show how Menachem Begin transformed from fighter to peacemaker with Egypt"
    [4]="Tell the story of Yitzhak Rabin, from military hero to peace architect"
    [5]="Explain Benjamin Netanyahu's impact as Israel's longest-serving Prime Minister"
    [6]="Discover Ariel Sharon, the warrior general who became a pragmatic leader"
    [7]="Learn about Shimon Peres, the eternal optimist who served Israel for seven decades"
    [8]="Introduce Moshe Sharett, Israel's diplomatic founding father"
)

# Character descriptions for accurate representation
declare -A CHARACTERS=(
    [1]="David Ben-Gurion: Short man, distinctive white hair in halo shape, round face, glasses, khaki kibbutz shirt"
    [2]="Golda Meir: Elderly woman, grey hair in bun, strong features, dark dress with brooch, grandmotherly appearance"
    [3]="Menachem Begin: Thin man, thick glasses, receding grey hair, formal dark suit, Polish mannerisms"
    [4]="Yitzhak Rabin: Tall robust man, thick grey hair, strong jaw, military casual shirts, shy smile"
    [5]="Benjamin Netanyahu: Silver-grey hair, sharp features, dark suits, commanding presence, media-savvy look"
    [6]="Ariel Sharon: Heavy-set, white hair, round face, farm clothes or uniform, bulldozer presence"
    [7]="Shimon Peres: Tall elderly man, white hair, gentle eyes, formal attire, visionary expression"
    [8]="Moshe Sharett: Refined, neat mustache, round glasses, diplomatic attire, scholarly appearance"
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
    
    # Run generation with historically accurate character
    python main.py \
        --mission "$mission" \
        --duration 40 \
        --style "$STYLE" \
        --character "$character" \
        --platform "$PLATFORM" \
        --voice "$VOICE" \
        --language "$LANGUAGE" \
        --session-id "$session_id" \
        --hashtags "israelipm israelhistory education history israel primeminister jewish learning episode${episode_num}" \
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
echo "Starting Israeli PM Educational Series production..." | tee "$LOG_FILE"
echo "Series directory: $SERIES_DIR" | tee -a "$LOG_FILE"
echo "Style: Realistic documentary" | tee -a "$LOG_FILE"
echo "Voice: Indian English ($VOICE)" | tee -a "$LOG_FILE"
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
echo "✨ Israeli PM Educational Series production complete!" | tee -a "$LOG_FILE"