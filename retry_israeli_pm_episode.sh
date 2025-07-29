#!/bin/bash
# Retry a specific Israeli PM episode

if [ $# -eq 0 ]; then
    echo "Usage: $0 <episode_number>"
    echo "Example: $0 3"
    exit 1
fi

EPISODE_NUM=$1

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
STYLE="realistic documentary"
VOICE="en-IN-Wavenet-A"
LANGUAGE="en-IN"

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

# Character descriptions
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

# Check if episode exists
if [ -z "${EPISODES[$EPISODE_NUM]}" ]; then
    echo "❌ Episode $EPISODE_NUM not found!"
    echo "Available episodes: 1-8"
    exit 1
fi

MISSION="${EPISODES[$EPISODE_NUM]}"
CHARACTER="${CHARACTERS[$EPISODE_NUM]}"
SESSION_ID="${SERIES_NAME}_ep${EPISODE_NUM}_retry"

echo "🔄 Retrying Israeli PM Episode $EPISODE_NUM"
echo "Character: $CHARACTER"
echo "Style: Realistic documentary"
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
    --hashtags "israelipm israelhistory education history israel primeminister jewish learning episode${EPISODE_NUM}"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Episode $EPISODE_NUM retry completed successfully!"
    echo "Video saved to outputs/${SESSION_ID}_*"
else
    echo ""
    echo "❌ Episode $EPISODE_NUM retry failed!"
fi