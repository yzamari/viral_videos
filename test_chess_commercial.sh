#!/bin/bash

# Test script for Hebrew chess commercial with LangGraph quality monitoring

echo "=================================================="
echo "🎬 CREATING HEBREW CHESS COMMERCIAL"
echo "=================================================="
echo "📝 Mission: Chess community classes"
echo "⏱️ Duration: 30 seconds"
echo "🌍 Language: Hebrew"
echo "🎯 Quality: Professional with LangGraph monitoring"
echo "=================================================="

# Export API key if needed
export GEMINI_API_KEY="${GEMINI_API_KEY:-AIzaSyCtw5XG_XTbxxNRajkbGWj9feoaqwFoptA}"

# Run the video generation using the generate command
python3 main.py generate \
    --mission "חוג שחמט קהילתי - לימוד אסטרטגיה וחשיבה מתקדמת לילדים ומבוגרים. הצטרפו לחוג השחמט המוביל בעיר! פיתוח חשיבה לוגית, שיפור ריכוז, ובניית ביטחון עצמי. מתאים לכל הגילאים - מתחילים עד מתקדמים. מדריכים מוסמכים, אווירה חמה ותומכת. ההרשמה פתוחה עכשיו!" \
    --duration 30 \
    --platform youtube \
    --category Educational \
    --style "professional educational" \
    --visual-style "modern community center" \
    --session-id chess_commercial_hebrew

echo ""
echo "=================================================="
echo "✅ Hebrew chess commercial generation complete!"
echo "📁 Check outputs/session_chess_commercial_hebrew/"
echo "=================================================="