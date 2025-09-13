#!/bin/bash

# Test script for creating a 60-second funny pro-Israeli Rosh Hashana video in Hebrew
# This tests the fix for the script truncation bug

echo "🍯🍎 Creating Hebrew Rosh Hashana Comedy Video (60 seconds)"
echo "=================================================="

# Set environment variables for GCP
export GOOGLE_CLOUD_PROJECT="viralgen-464411"
export VERTEX_AI_PROJECT_ID="viralgen-464411"
export VERTEX_AI_LOCATION="us-central1"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Create the video with specific parameters for Rosh Hashana (60 seconds)
python3 main.py generate \
    --mission "ראש השנה: סרטון קומי קצר על החג עם דבש ותפוחים ושופר. בדיחות על המסורות והארוחות המשפחתיות הארוכות" \
    --duration 60 \
    --platform youtube \
    --category Comedy \
    --style "קומדיה ישראלית" \
    --visual-style "חגיגי וצבעוני" \
    --languages he \
    --session-id rosh_hashana_60s_test \
    --discussions enhanced \
    --cheap-mode full \
    --theme "jewish_holiday" \
    --veo-model-order "veo3-fast"

echo ""
echo "✅ Video generation completed!"
echo "📁 Output location: outputs/rosh_hashana_60s_test/"
echo ""
echo "🎬 The video should include:"
echo "   - Hebrew narration and text"
echo "   - Rosh Hashana symbols"
echo "   - 60 seconds duration"
echo "   - VEO 3 video generation"
echo "   - FIXED script word count (should be ~168 words, not truncated to 90)"