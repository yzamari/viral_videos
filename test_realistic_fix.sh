#!/bin/bash
echo "🎬 Testing realistic video generation fix..."
echo "📅 Started at: $(date)"

# Run a simple test with realistic style
python main.py generate \
  --mission "Create a 30-second realistic documentary about volunteers delivering food to communities in need. Show real people helping others with compassion." \
  --platform instagram \
  --duration 30 \
  --cheap simple \
  --visual-style "realistic" \
  --style "documentary" \
  > test_realistic_output.log 2>&1

echo "✅ Completed at: $(date)"
echo "📄 Checking results..."

# Check if cartoon was used
if grep -q "animated cartoon style" test_realistic_output.log; then
    echo "❌ ERROR: Still using cartoon style!"
    grep -C2 "cartoon" test_realistic_output.log
else
    echo "✅ SUCCESS: No cartoon style detected"
fi

# Check for the session
SESSION=$(grep -o "session_[0-9_]*" test_realistic_output.log | head -1)
if [ -n "$SESSION" ]; then
    echo "📁 Session: $SESSION"
    # Check final video
    if ls outputs/$SESSION/final_output/*_final.mp4 2>/dev/null; then
        echo "✅ Final video created successfully"
    else
        echo "❌ No final video found"
    fi
fi