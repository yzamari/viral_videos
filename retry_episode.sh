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

# Episode definitions - Short missions giving AI agents creative freedom
declare -A EPISODES=(
    [1]="Dragon teaches kids what a mathematical limit is using fun everyday examples"
    [2]="Dragon explains derivatives - how to measure how fast things change"
    [3]="Dragon shows what integration means - adding things up to get totals"
    [4]="Dragon discovers the chain rule - how connected things affect each other"
    [5]="Dragon learns about finding maximum values - the biggest or best amount"
    [6]="Dragon explores related rates - when changing one thing changes another"
    [7]="Dragon reveals that derivatives and integrals are opposites"
    [8]="Dragon demonstrates infinite series - how adding forever can equal a finite number"
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