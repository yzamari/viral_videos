#!/bin/bash

# Netanyahu Marvel Episode 17 - Current Term with Dark Humor
# Generates both Hebrew and English versions

# Parse command line arguments
GENERATE_HEBREW=true
GENERATE_ENGLISH=true

while [[ $# -gt 0 ]]; do
    case $1 in
        -l|--language)
            shift
            case $1 in
                en|english)
                    GENERATE_HEBREW=false
                    GENERATE_ENGLISH=true
                    ;;
                he|hebrew)
                    GENERATE_HEBREW=true
                    GENERATE_ENGLISH=false
                    ;;
                all|both)
                    GENERATE_HEBREW=true
                    GENERATE_ENGLISH=true
                    ;;
                *)
                    echo "Unknown language: $1"
                    echo "Valid options: en, he, all"
                    exit 1
                    ;;
            esac
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -l, --language <lang>  Generate specific language version"
            echo "                         Options: en (English), he (Hebrew), all (both)"
            echo "                         Default: all"
            echo "  -h, --help             Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                  # Generate both languages"
            echo "  $0 -l en            # Generate English only"
            echo "  $0 -l he            # Generate Hebrew only"
            echo "  $0 --language all   # Generate both languages"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

echo "🎬 Starting Netanyahu Marvel Episode 17 Generation"
if $GENERATE_HEBREW && $GENERATE_ENGLISH; then
    echo "📊 Languages: Hebrew and English"
elif $GENERATE_ENGLISH; then
    echo "📊 Language: English only"
elif $GENERATE_HEBREW; then
    echo "📊 Language: Hebrew only"
fi
echo "⏱️  Duration: 55 seconds"
echo "📱 Platform: Instagram"
echo "🎨 Style: Marvel Comics with dark humor"
echo ""

# Set session ID with timestamp
SESSION_ID="netanyahu_marvel_ep17_$(date +%Y%m%d_%H%M%S)"

# Mission texts
MISSION_EN="Marvel Comics explosion! Benjamin Netanyahu with lightning effects crashes through Knesset walls. CRASH! 'I am eternal!' Opposition parties vanish in comic smoke. WHOOSH! Coalition deals with exploding panels. BOOM! Juggling multiple corruption trials while texting. ZAP! Building settlements with energy beams. THWACK! Judicial reform controversy splits the nation. CRACK! 'Bibi will return... again!' WHAM! Israeli flag with lightning bolts."
MISSION_HE="פיצוץ קומיקס מארוול! בנימין נתניהו עם אפקטי ברקים מתרסק דרך קירות הכנסת. קראש! 'אני נצחי!' מפלגות האופוזיציה נעלמות בעשן קומיקס. וואוש! עסקאות קואליציה עם פאנלים מתפוצצים. בום! מלהטט במשפטי שחיתות מרובים תוך כדי סמסים. זאפ! בונה התנחלויות עם קרני אנרגיה. ת'וואק! מחלוקת הרפורמה המשפטית מפצלת את האומה. קראק! 'ביבי יחזור... שוב!' וואם! דגל ישראל עם ברקים."

# Character descriptions
CHARACTER_EN="Benjamin Netanyahu with gray hair, determined expression, dark suit with lightning aura, Marvel superhero style"
CHARACTER_HE="בנימין נתניהו עם שיער אפור, הבעה נחושה, חליפה כהה עם הילת ברקים, בסגנון גיבור על של מארוול"

# Build language list based on flags
LANGUAGES=""
if $GENERATE_HEBREW; then
    LANGUAGES="--languages he"
fi
if $GENERATE_ENGLISH; then
    if [ -n "$LANGUAGES" ]; then
        LANGUAGES="$LANGUAGES --languages en"
    else
        LANGUAGES="--languages en"
    fi
fi

# Set appropriate mission and character based on languages
if $GENERATE_HEBREW && $GENERATE_ENGLISH; then
    # For both languages, use English (system will handle both)
    MISSION="$MISSION_EN"
    CHARACTER="$CHARACTER_EN"
elif $GENERATE_ENGLISH; then
    MISSION="$MISSION_EN"
    CHARACTER="$CHARACTER_EN"
elif $GENERATE_HEBREW; then
    MISSION="$MISSION_HE"
    CHARACTER="$CHARACTER_HE"
fi

# Run the generation
python3 main.py generate \
  --mission "$MISSION" \
  $LANGUAGES \
  --duration 55 \
  --platform instagram \
  --character "$CHARACTER" \
  --session-id "$SESSION_ID" \
  --category Comedy \
  --style marvel \
  --tone satirical \
  --no-cheap

# Check if generation was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Generation completed successfully!"
    echo "📁 Output location: outputs/$SESSION_ID"
    echo ""
    echo "📹 Videos generated:"
    if $GENERATE_HEBREW; then
        echo "  - Hebrew: outputs/$SESSION_ID/languages/he/final_video.mp4"
    fi
    if $GENERATE_ENGLISH; then
        echo "  - English: outputs/$SESSION_ID/languages/en/final_video.mp4"
    fi
else
    echo ""
    echo "❌ Generation failed. Check logs for details."
    echo "📋 Log file: outputs/$SESSION_ID/logs/generation.log"
fi