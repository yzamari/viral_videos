#!/bin/bash

# Therapeutic PTSD Video Generator
# Creates safe, therapeutic visualizations for trauma processing

echo "🌱 Therapeutic PTSD Visualization Generator"
echo "================================================"
echo "This creates therapeutic, healing-focused content"
echo "for safe trauma processing and integration."
echo ""

# Check if client story is provided
if [ -z "$1" ]; then
    echo "Usage: ./generate_therapeutic_ptsd_video.sh \"<client_story>\""
    echo ""
    echo "Example:"
    echo "./generate_therapeutic_ptsd_video.sh \"Walking through Gaza as a soldier, the fear and explosions\""
    exit 1
fi

CLIENT_STORY="$1"
SESSION_TYPE="${2:-processing}"  # Default to processing
SESSION_ID="${3:-therapeutic_ptsd_$(date +%Y%m%d_%H%M%S)}"

echo "📝 Client Experience: $CLIENT_STORY"
echo "🎯 Session Type: $SESSION_TYPE"
echo "📁 Session ID: $SESSION_ID"
echo ""

# Activate virtual environment
source .venv/bin/activate

# Run with therapeutic transformation
python main.py generate \
  --mission "$CLIENT_STORY" \
  --therapeutic-mode \
  --duration 15 \
  --platform youtube \
  --category "Health & Wellness" \
  --style "therapeutic healing visualization" \
  --visual-style "soft watercolor, gentle transitions, calming nature scenes, therapeutic imagery" \
  --tone "calming supportive" \
  --session-id "$SESSION_ID" \
  --no-cheap \
  --mode simple \
  --discussions off

echo ""
echo "✅ Therapeutic visualization complete!"
echo "📁 Output: outputs/$SESSION_ID/"
echo ""
echo "⚠️ IMPORTANT: This content is for therapeutic use only."
echo "   Always use with professional supervision."
echo "   Not a substitute for professional mental health treatment."