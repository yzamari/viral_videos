#!/bin/bash

# Unified Papaya Bar Commercial - Hebrew 30-second TikTok Ad
# Combines the best elements from all Papaya scripts
# Funny, engaging, and targeted for Israeli audience

cd "$(dirname "$0")"

# Configuration
DURATION=32  # 32 = 4 clips × 8 seconds (rounded up from 30s for TikTok)
PLATFORM="tiktok"
LANGUAGE="he"  # Hebrew output

# Mission in English (system will generate Hebrew output)
MISSION="Create a hilarious 30-second TikTok ad for Papaya Bar in Rosh HaAyin! 
Start with dramatic Marvel-style hero entrance - superhero crashes through wall, exhausted and dehydrated. 
Suddenly, magical Ghibli-style transformation! The bar becomes an enchanted forest with floating papaya fruits. 
Grandma appears with glowing healing smoothie, hero drinks and transforms into muscular god. 
Cut to reality - it's just a regular person feeling amazing after a papaya shake. 
Night scene: same bar transforms into cocktail paradise with shake-based alcohol drinks. 
Young crowd partying with glowing drinks. Funny twist: drunk guy tries to order 'healthy' shake at 2am. 
End with catchy Hebrew slogan about being healthy heroes by day, party legends by night! 
Business: Shabazi 47, Rosh HaAyin, 054-222-2617, Always Open."

echo "🥤 Papaya Bar - Ultimate Hebrew TikTok Commercial"
echo "=============================================="
echo "🎯 Target: Israeli TikTok audience"  
echo "😂 Style: Funny & engaging mix of Marvel action + Ghibli magic"
echo "🌐 Language: Hebrew (עברית)"
echo "⏱️  Duration: 30 seconds"
echo "📱 Platform: TikTok"
echo ""

# Session ID
SESSION_ID="papaya_unified_hebrew_30s_$(date +%Y%m%d_%H%M%S)"

# Generate the commercial with best settings from all scripts
python3 main.py generate \
    --mission "$MISSION" \
    --session-id "$SESSION_ID" \
    --duration $DURATION \
    --platform "$PLATFORM" \
    --languages "$LANGUAGE" \
    --style viral \
    --visual-style "marvel comics meets studio ghibli hybrid colorful vibrant" \
    --tone "funny refreshing energetic" \
    --character "פפאיה הגיבורה - דמות סופר-פפאיה עם שרירים וכנפיים קסומות" \
    --voice "he-IL-AvriNeural" \
    --target-audience "israeli youth tiktok users health-conscious party-goers" \
    --business-name "Papaya Bar פפאיה בר" \
    --business-address "שבזי 47, ראש העין" \
    --business-phone "054-222-2617" \
    --business-instagram "@thepapayabar" \
    --show-business-info \
    --visual-continuity \
    --content-continuity \
    --no-cheap \
    --mode enhanced \
    2>&1 | tee "papaya_unified_generation.log"

EXIT_CODE=${PIPESTATUS[0]}

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ Papaya Bar unified commercial completed successfully!"
    echo ""
    
    # Find output video
    OUTPUT_DIR="outputs/$SESSION_ID"
    if [ -d "$OUTPUT_DIR" ]; then
        echo "📁 Output location: $OUTPUT_DIR"
        echo ""
        
        # Find final video
        FINAL_VIDEO=$(find "$OUTPUT_DIR/final_output" -name "*.mp4" 2>/dev/null | head -1)
        if [ -n "$FINAL_VIDEO" ]; then
            echo "🎬 Final video: $FINAL_VIDEO"
            echo ""
        fi
        
        # Check for Hebrew audio
        HEBREW_AUDIO=$(find "$OUTPUT_DIR/audio" -name "*he*.mp3" -o -name "*hebrew*.mp3" 2>/dev/null | head -1)
        if [ -n "$HEBREW_AUDIO" ]; then
            echo "🔊 Hebrew audio: $HEBREW_AUDIO"
        fi
        
        echo ""
        echo "📱 Ready for TikTok upload!"
        echo ""
        echo "💡 Commercial highlights:"
        echo "   - Marvel superhero entrance"
        echo "   - Ghibli magical transformation"
        echo "   - Grandma's healing smoothie"
        echo "   - Day/night transformation"
        echo "   - Funny drunk scene"
        echo "   - Hebrew slogan"
        echo ""
        echo "🏪 Business info included:"
        echo "   📍 שבזי 47, ראש העין"
        echo "   📞 054-222-2617"
        echo "   🌐 @thepapayabar"
        echo "   ⏰ Always Open"
    fi
else
    echo ""
    echo "❌ Generation failed with exit code: $EXIT_CODE"
    echo "📋 Check papaya_unified_generation.log for details"
    echo ""
    echo "🔧 Common issues:"
    echo "   - Ensure venv is activated"
    echo "   - Check API keys are configured"
    echo "   - Verify Hebrew language support is enabled"
fi

echo ""
echo "💡 To generate more variations:"
echo "   ./run_papaya_unified_hebrew_30s.sh"
echo ""
echo "💡 To run in background:"
echo "   nohup ./run_papaya_unified_hebrew_30s.sh > papaya_log.txt 2>&1 &"
echo "   tail -f papaya_log.txt"