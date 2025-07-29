#!/bin/bash
# Test Indian English voice configuration

echo "🎤 Testing Indian English Voice Configuration"
echo "==========================================="

# Activate virtual environment if exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Test with a short episode
python main.py \
    --mission "Dragon teaches quick math tip: 2+2=4. Dragon says 'Hello friends, today we learn basic addition!'" \
    --duration 10 \
    --style "studio ghibli" \
    --character "Dragon with graduation cap" \
    --platform "instagram" \
    --voice "en-IN-Wavenet-A" \
    --language "en-IN" \
    --session-id "indian_voice_test" \
    --cheap \
    2>&1 | tee indian_voice_test.log

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Indian voice test successful!"
    echo "Check the audio file in outputs/indian_voice_test_*"
else
    echo ""
    echo "❌ Indian voice test failed! Check indian_voice_test.log"
fi