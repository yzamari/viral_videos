#!/bin/bash
# Test Dragon Episode 7 with --cheap flag to ensure no errors

echo "🐉 Testing Dragon Episode 7 with --cheap flag..."
echo "================================================"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Set up environment variables
export GEMINI_API_KEY="${GEMINI_API_KEY:-your-api-key}"
export GOOGLE_CLOUD_PROJECT="${GOOGLE_CLOUD_PROJECT:-your-project}"

# Run the command with cheap flag
echo "Running: python3 main.py --cheap --duration 40 --mission 'Dragon episode 7: nested intervals are time portals...'"
python3 main.py \
    --cheap \
    --duration 40 \
    --mission "Dragon episode 7: nested intervals are time portals. Dragon hilariously explains each concept while time-traveling. Include funny historical encounters, dragon's time-travel jokes, and visual demonstrations of recursive concepts!" \
    --character "Dragon with graduation cap and time-travel goggles" \
    --style "studio ghibli" \
    --platform youtube \
    --session-id "dragon_ep7_test" \
    2>&1 | tee dragon_ep7_test.log

# Check if the command succeeded
if [ $? -eq 0 ]; then
    echo "✅ Test completed successfully!"
    echo "Check outputs/dragon_ep7_test_* for results"
    
    # Check for timeline visualization
    if ls outputs/dragon_ep7_test_*/analysis/timeline/timeline_visual.txt 2>/dev/null; then
        echo ""
        echo "📊 Timeline visualization available:"
        ls -la outputs/dragon_ep7_test_*/analysis/timeline/
    fi
else
    echo "❌ Test failed! Check dragon_ep7_test.log for errors"
    exit 1
fi