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