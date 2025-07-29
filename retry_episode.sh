#!/bin/bash
# Retry a specific Dragon Calculus episode

if [ $# -eq 0 ]; then
    echo "Usage: $0 <episode_number>"
    echo "Example: $0 3"
    exit 1
fi

EPISODE_NUM=$1

# Configuration (same as main script)
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

# Check if episode exists
if [ -z "${EPISODES[$EPISODE_NUM]}" ]; then
    echo "❌ Episode $EPISODE_NUM not found!"
    echo "Available episodes: 1-8"
    exit 1
fi

MISSION="${EPISODES[$EPISODE_NUM]}"
SESSION_ID="${SERIES_NAME}_ep${EPISODE_NUM}_retry"

echo "🔄 Retrying Dragon Calculus Episode $EPISODE_NUM"
echo "Mission: $MISSION"
echo "Voice: Indian English"
echo ""

# Run the generation command
python main.py \
    --mission "$MISSION" \
    --duration 40 \
    --style "$STYLE" \
    --character "$CHARACTER" \
    --platform "$PLATFORM" \
    --voice "$VOICE" \
    --language "$LANGUAGE" \
    --session-id "$SESSION_ID" \
    --hashtags "dragoncalculus calculus mathematics education animation studioghibli dragon math learning episode${EPISODE_NUM}" \
    --auto-post-instagram

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Episode $EPISODE_NUM retry completed successfully!"
    echo "Check Instagram @yalla.chaos.ai for the uploaded video"
else
    echo ""
    echo "❌ Episode $EPISODE_NUM retry failed!"
fi