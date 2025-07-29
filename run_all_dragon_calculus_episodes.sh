#!/bin/bash
# Generate and upload all Dragon Calculus episodes to Instagram
# Uses Indian English accent for all narration

echo "🐉 Dragon Calculus Series - Full Production & Instagram Upload"
echo "============================================================="

# Configuration
export INSTAGRAM_USERNAME="yalla.chaos.ai"
export INSTAGRAM_PASSWORD="Nvnnh@123"
export GEMINI_API_KEY="${GEMINI_API_KEY}"
export GOOGLE_CLOUD_PROJECT="${GOOGLE_CLOUD_PROJECT}"

# Activate virtual environment if exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Series configuration
SERIES_NAME="dragon_calculus"
PLATFORM="instagram"
STYLE="studio ghibli"
CHARACTER="Dragon with graduation cap and time-travel goggles"
VOICE="en-IN-Wavenet-A"  # Indian English male voice
LANGUAGE="en-IN"          # Indian English (matches Language.ENGLISH_IN enum)

# Create series directory
SERIES_DIR="outputs/${SERIES_NAME}_series_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$SERIES_DIR"

# Log file
LOG_FILE="$SERIES_DIR/series_production.log"

# Episode definitions
declare -A EPISODES=(
    [1]="Dragon Episode 1: Meet Professor Dragon who discovered calculus while trying to count his gold. He explains limits using shrinking treasure piles and approaching castle gates. Include dragon puns and visual math jokes!"
    [2]="Dragon Episode 2: Dragon teaches derivatives by flying at different speeds. Shows rate of change using dragon flight paths, treasure accumulation rates, and melting ice cream. Make it hilarious with dragon physics!"
    [3]="Dragon Episode 3: Integration explained through dragon hoarding behavior. Dragon fills treasure vaults to demonstrate area under curves. Include jokes about dragon greed and mathematical accumulation!"
    [4]="Dragon Episode 4: Chain rule through dragon family trees. Each dragon passes traits (functions) to children. Composite functions explained with nested dragon eggs and inherited fire-breathing abilities!"
    [5]="Dragon Episode 5: Dragon demonstrates optimization by finding the perfect cave size. Uses calculus to maximize treasure storage while minimizing entrance size for security. Include burglar jokes!"
    [6]="Dragon Episode 6: Related rates with dragon race scenarios. Multiple dragons flying at different speeds, shadows changing, and treasure piles growing. Make it a comedy race competition!"
    [7]="Dragon Episode 7: Nested intervals are time portals. Dragon hilariously explains each concept while time-traveling. Include funny historical encounters, dragon's time-travel jokes, and visual demonstrations of recursive concepts!"
    [8]="Dragon Episode 8: Series finale - Dragon's Calculus Magic Show! Reviews all concepts through spectacular magic tricks. Grand finale with fireworks spelling calculus formulas!"
)

# Function to generate single episode
generate_episode() {
    local episode_num=$1
    local mission="${EPISODES[$episode_num]}"
    local session_id="${SERIES_NAME}_ep${episode_num}"
    
    echo ""
    echo "🎬 Generating Episode $episode_num..."
    echo "Mission: $mission"
    echo "Session: $session_id"
    
    # Run the generation command with Indian English voice
    python main.py \
        --mission "$mission" \
        --duration 40 \
        --style "$STYLE" \
        --character "$CHARACTER" \
        --platform "$PLATFORM" \
        --voice "$VOICE" \
        --language "$LANGUAGE" \
        --session-id "$session_id" \
        --hashtags "dragoncalculus calculus mathematics education animation studioghibli dragon math learning episode${episode_num}" \
        --auto-post-instagram \
        2>&1 | tee -a "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        echo "✅ Episode $episode_num completed successfully!" | tee -a "$LOG_FILE"
        
        # Copy final video to series directory
        LATEST_OUTPUT=$(ls -td outputs/${session_id}_* 2>/dev/null | head -1)
        if [ -n "$LATEST_OUTPUT" ]; then
            FINAL_VIDEO=$(find "$LATEST_OUTPUT/final_output" -name "*.mp4" 2>/dev/null | head -1)
            if [ -n "$FINAL_VIDEO" ]; then
                cp "$FINAL_VIDEO" "$SERIES_DIR/episode_${episode_num}.mp4"
                echo "📦 Saved Episode $episode_num to series directory" | tee -a "$LOG_FILE"
            fi
        fi
        
        # Add delay between episodes to avoid rate limiting
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
echo "Starting Dragon Calculus series production..." | tee "$LOG_FILE"
echo "Series directory: $SERIES_DIR" | tee -a "$LOG_FILE"
echo "Platform: Instagram" | tee -a "$LOG_FILE"
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
    echo "" | tee -a "$LOG_FILE"
    echo "To retry failed episodes, run:" | tee -a "$LOG_FILE"
    for ep in $FAILED_EPISODES; do
        echo "  ./retry_episode.sh $ep" | tee -a "$LOG_FILE"
    done
fi

echo "" | tee -a "$LOG_FILE"
echo "Series directory: $SERIES_DIR" | tee -a "$LOG_FILE"
echo "Log file: $LOG_FILE" | tee -a "$LOG_FILE"

# Check Instagram uploads
echo "" | tee -a "$LOG_FILE"
echo "📱 Instagram Upload Status:" | tee -a "$LOG_FILE"
echo "Username: @yalla.chaos.ai" | tee -a "$LOG_FILE"
echo "Check https://instagram.com/yalla.chaos.ai for uploaded videos" | tee -a "$LOG_FILE"

# Create a summary file
cat > "$SERIES_DIR/series_info.json" << EOF
{
    "series": "Dragon Calculus",
    "episodes": 8,
    "platform": "instagram",
    "voice": "Indian English",
    "character": "$CHARACTER",
    "style": "$STYLE",
    "instagram_account": "@yalla.chaos.ai",
    "production_date": "$(date)",
    "success_count": $SUCCESS_COUNT,
    "failed_episodes": "$FAILED_EPISODES"
}
EOF

echo "" | tee -a "$LOG_FILE"
echo "✨ Dragon Calculus series production complete!" | tee -a "$LOG_FILE"