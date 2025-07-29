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

# Episode definitions - Each focuses on ONE concept with complete narrative
declare -A EPISODES=(
    [1]="Dragon Episode 1: What is a Limit? Dragon discovers the concept of limits using his shrinking gold coins. He starts with a pile of gold and keeps dividing it in half, getting closer and closer to zero but never quite reaching it. Through this simple demonstration, Dragon explains how limits work - approaching a value without necessarily reaching it. Include Dragon's amazement as he realizes the gold never completely disappears!"
    [2]="Dragon Episode 2: Understanding Derivatives - Speed of Change. Dragon learns about derivatives by tracking his flying speed. He starts flying slowly, then faster, measuring how his speed changes each second. Using his flight path, Dragon discovers that derivatives measure rate of change. He realizes his acceleration (change in speed) is the derivative of his velocity. Make it visual with Dragon's speed meter!"
    [3]="Dragon Episode 3: The Power of Integration - Adding Things Up. Dragon discovers integration by counting his daily treasure collection. Each day he collects different amounts, and integration helps him find the total. He learns that integration is the reverse of derivatives - instead of finding rate of change, we find the total accumulation. Dragon uses colorful treasure piles to show how areas under curves work!"
    [4]="Dragon Episode 4: The Chain Rule Made Simple. Dragon learns the chain rule through nested treasure boxes. Each box contains a smaller box with gold multipliers. To find total gold, Dragon must multiply the rates from each box - this is the chain rule! He discovers how composite functions work by opening box after box, each affecting the final result."
    [5]="Dragon Episode 5: Finding Maximum Treasure - Optimization. Dragon uses calculus to find the perfect cave size for maximum treasure storage. Too small and he can't fit treasure, too big and thieves can enter. Using derivatives to find where the slope is zero, Dragon discovers the optimal size. This episode teaches finding maxima and minima in a practical, visual way!"
    [6]="Dragon Episode 6: Related Rates - Everything Connected. Dragon learns related rates by filling his circular pool with water. As water level rises, the radius increases. Dragon discovers how these rates are related using calculus. He calculates how fast the radius grows based on water flow rate. Make it fun with Dragon splashing and measuring!"
    [7]="Dragon Episode 7: The Fundamental Theorem - Connecting Two Worlds. Dragon discovers the magical connection between derivatives and integrals. Using his flying height (position) and speed (velocity), he shows how integrating velocity gives position, and deriving position gives velocity. This revelation amazes Dragon as he realizes these operations are opposites!"
    [8]="Dragon Episode 8: Series and Sequences - Infinite Patterns. Dragon learns about series by stacking smaller and smaller gold coins infinitely high. He discovers that infinite series can have finite sums! Using geometric series, Dragon calculates the total height of his infinite stack. The episode ends with Dragon's mind blown by infinity having limits!"
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