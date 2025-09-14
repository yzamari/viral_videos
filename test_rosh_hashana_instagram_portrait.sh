#!/bin/bash

# Test script for creating a 30-second funny Instagram Rosh Hashana video in Hebrew
# Uses VEO3 portrait mode (9:16) with best practices for prompting

echo "📱🍯 Creating Instagram Portrait Rosh Hashana Comedy Video (30 seconds)"
echo "========================================================="

# Set environment variables for GCP
export GOOGLE_CLOUD_PROJECT="viralgen-464411"
export VERTEX_AI_PROJECT_ID="viralgen-464411"
export VERTEX_AI_LOCATION="us-central1"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Create the video with specific parameters for Instagram portrait format
# Note: Portrait mode 9:16 will be set through visual-style
python3 main.py generate \
    --mission "סרטון ראש השנה קומי לאינסטגרם בפורמט פורטרט 9:16: משפחה ישראלית מנסה להחליט מי מביא מה לסעודה. סבתא רוצה גפילטע פיש, הילדים רוצים פיצה, והכלב כבר אכל את כל התפוחים בדבש. חובה: בדיחות על שופר שלא עובד וסליחות בוואטסאפ. צילום אנכי לריילס, תקריבים על פנים, מצלמה דינמית" \
    --duration 30 \
    --platform instagram \
    --category Comedy \
    --style "קומדיה ישראלית ויראלית לאינסטגרם" \
    --visual-style "פורמט פורטרט אנכי 9:16 צבעוני ומודרני, צילום סלולרי אנכי, תקריבים דרמטיים" \
    --languages he \
    --session-id rosh_hashana_instagram_portrait \
    --discussions enhanced \
    --theme "jewish_holiday" \
    --veo-model-order "veo3,veo3-fast"

echo ""
echo "✅ Instagram portrait video generation completed!"
echo "📁 Output location: outputs/rosh_hashana_instagram_portrait/"
echo ""
echo "🎬 The video should include:"
echo "   - 9:16 portrait format for Instagram Reels"
echo "   - Hebrew narration with native audio"
echo "   - 30 seconds duration"
echo "   - VEO3 with best practice prompting"
echo "   - LangGraph AI agents for quality"
echo "   - Native audio generation with dialogue"
echo "   - Cinematic camera movements"
echo "   - High-quality 1080p resolution"
echo ""
echo "📱 Ready for Instagram Reels upload!"