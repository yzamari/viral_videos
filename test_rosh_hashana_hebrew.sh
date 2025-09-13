#!/bin/bash

# Test script for creating a 3-minute funny pro-Israeli Rosh Hashana video in Hebrew
# This video will use VEO 3 for video generation

echo "🍯🍎 Creating Hebrew Rosh Hashana Comedy Video (3 minutes)"
echo "=================================================="

# Set environment variables for GCP
export GOOGLE_CLOUD_PROJECT="viralgen-464411"
export VERTEX_AI_PROJECT_ID="viralgen-464411"
export VERTEX_AI_LOCATION="us-central1"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Create the video with specific parameters for Rosh Hashana
python3 main.py generate \
    --mission "ראש השנה: סרטון קומי פרו-ישראלי על החג היהודי החדש עם דבש ותפוחים, שופר, וחגיגות משפחתיות. הסרטון צריך להיות מצחיק וגאה בישראל, עם בדיחות על המסורות של ראש השנה, סליחות, תשליך ותקיעת שופר. כולל הומור ישראלי אותנטי על ארוחות החג המשפחתיות הארוכות, הדודים שמגיעים מחו״ל, והתחרות מי יביא את העוגת הדבש הכי טובה" \
    --duration 180 \
    --platform youtube \
    --category Comedy \
    --style "קומדיה ישראלית חגיגית" \
    --visual-style "חגיגי וצבעוני עם סמלי ראש השנה" \
    --languages he \
    --session-id rosh_hashana_hebrew_comedy \
    --discussions enhanced \
    --cheap-mode full \
    --theme "jewish_holiday" \
    --veo-model-order "veo3-fast"

echo ""
echo "✅ Video generation completed!"
echo "📁 Output location: outputs/rosh_hashana_hebrew_comedy/"
echo ""
echo "🎬 The video should include:"
echo "   - Hebrew narration and text"
echo "   - Rosh Hashana symbols (apples, honey, shofar)"
echo "   - Israeli humor and cultural references"
echo "   - Family celebrations"
echo "   - 3 minutes duration"
echo "   - VEO 3 video generation"