#!/bin/bash

# Israeli PM Marvel Series - 50 second episodes with English and Hebrew
# Ready for background execution in separate thread

# Parse command line arguments
EPISODES_TO_GENERATE=()
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--episodes)
            shift
            # Read episode numbers until we hit another flag or end of args
            while [[ $# -gt 0 && ! "$1" =~ ^- ]]; do
                EPISODES_TO_GENERATE+=("$1")
                shift
            done
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -e, --episodes <num1> <num2> ...  Generate specific episodes"
            echo "  -h, --help                        Show this help message"
            echo ""
            echo "Available episodes:"
            echo "  1: Ben-Gurion - The Founding Titan"
            echo "  2: Moshe Sharett - The Forgotten Avenger"
            echo "  3: Levi Eshkol - The Peacekeeper"
            echo "  4: Golda Meir - The Iron Lady"
            echo "  5: Yitzhak Rabin - The Soldier's Peace"
            echo "  6: Menachem Begin - The Revolutionary"
            echo "  7: Yitzhak Shamir - The Underground Fighter"
            echo "  8: Shimon Peres - The Eternal Optimist"
            echo "  9: Benjamin Netanyahu - The Eternal Return"
            echo "  10: Ehud Barak - The Commander"
            echo "  11: Ariel Sharon - The Bulldozer"
            echo "  12: Ehud Olmert - The Rise and Fall"
            echo "  13: Naftali Bennett - The Disruptor"
            echo "  14: Yair Lapid - The Media Star"
            echo "  15: Netanyahu's Return - The Phoenix"
            echo "  16: Netanyahu's Trials - The Legal Battles"
            echo "  17: Netanyahu's Current Term - The Controversy"
            echo ""
            echo "Examples:"
            echo "  $0                    # Generate all available episodes"
            echo "  $0 -e 1              # Generate only episode 1"
            echo "  $0 -e 1 5 9          # Generate episodes 1, 5, and 9"
            echo "  $0 --episodes 15 16  # Generate episodes 15 and 16"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# If no episodes specified, generate default episode 1
if [ ${#EPISODES_TO_GENERATE[@]} -eq 0 ]; then
    EPISODES_TO_GENERATE=(1)
    echo "ℹ️  No episodes specified, generating episode 1 by default"
    echo "   Use -e flag to specify episodes, or -h for help"
fi

echo "🦸 Israeli PM Marvel Series - Production Script"
echo "=============================================="
echo "⏱️  50 seconds duration (~8 clips of 5-8s each)"
echo "🌐 Languages: English & Hebrew"
echo "🇮🇱 Israeli flag overlay in top-left"
echo "💥 Marvel Comics style"
echo "🎭 Consistent character appearance"
echo ""
echo "✨ IMPROVEMENTS APPLIED:"
echo "   - Video clips now 5-8 seconds (not 0.5-2s)"
echo "   - Hebrew script/audio/subtitles (not English)"
echo "   - RTL text rendering for Hebrew overlays"
echo "   - Frame continuity between clips"
echo ""
echo "📺 Episodes to generate: ${EPISODES_TO_GENERATE[*]}"
echo ""

# Function to generate episode
generate_episode() {
    local ep_num=$1
    local title=$2
    local mission_en=$3
    local mission_he=$4
    local character_en=$5
    local character_he=$6
    local session_base=$7
    
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "📺 Episode $ep_num: $title"
    echo "═══════════════════════════════════════════════════════════════"
    
    # English Version
    echo ""
    echo "🇬🇧 Generating ENGLISH version..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    python3 main.py generate \
        --mission "$mission_en" \
        --character "$character_en" \
        --platform instagram \
        --duration 50 \
        --visual-style "marvel comics" \
        --tone darkly_humorous \
        --style cinematic \
        --no-cheap \
        --voice "en-US-Neural2-J" \
        --session-id "${session_base}_ep${ep_num}_en" \
        --languages en-US \
        --visual-continuity \
        --content-continuity
    
    EN_RESULT=$?
    
    if [ $EN_RESULT -eq 0 ]; then
        echo "✅ English version completed successfully!"
    else
        echo "❌ English version failed with exit code: $EN_RESULT"
    fi
    
    # Brief pause between languages
    sleep 10
    
    # Hebrew Version
    echo ""
    echo "🇮🇱 Generating HEBREW version..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    python3 main.py generate \
        --mission "$mission_he" \
        --character "$character_he" \
        --platform instagram \
        --duration 50 \
        --visual-style "marvel comics" \
        --tone darkly_humorous \
        --style cinematic \
        --no-cheap \
        --voice "he-IL-Wavenet-D" \
        --session-id "${session_base}_ep${ep_num}_he" \
        --languages he \
        --visual-continuity \
        --content-continuity
    
    HE_RESULT=$?
    
    if [ $HE_RESULT -eq 0 ]; then
        echo "✅ Hebrew version completed successfully!"
    else
        echo "❌ Hebrew version failed with exit code: $HE_RESULT"
    fi
    
    # Summary
    echo ""
    echo "📊 Episode $ep_num Generation Summary:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "English: $([ $EN_RESULT -eq 0 ] && echo "✅ SUCCESS" || echo "❌ FAILED")"
    echo "Hebrew:  $([ $HE_RESULT -eq 0 ] && echo "✅ SUCCESS" || echo "❌ FAILED")"
    echo ""
    echo "Output folders:"
    echo "- English: outputs/${session_base}_ep${ep_num}_en/"
    echo "- Hebrew:  outputs/${session_base}_ep${ep_num}_he/"
    echo ""
    
    return 0
}

# Define all episode data
declare -a EPISODE_TITLES
declare -a EPISODE_MISSIONS_EN
declare -a EPISODE_MISSIONS_HE
declare -a EPISODE_CHARACTERS_EN
declare -a EPISODE_CHARACTERS_HE

# Episode 1: David Ben-Gurion
EPISODE_TITLES[1]="Ben-Gurion - The Founding Titan"
EPISODE_MISSIONS_EN[1]="Marvel Comics explosion! David Ben-Gurion with iconic white Einstein hair bursts from desert sands. 'I am INEVITABLE!' SNAP! British Mandate vanishes in comic smoke. Declaration of Independence with exploding panels. KA-POW! Yoga headstands during cabinet meetings. Building kibbutzim with energy effects. Desert retirement. 'Ben-Gurion will return!' Israeli flag in top-left corner."
EPISODE_MISSIONS_HE[1]="פיצוץ קומיקס מארוול! דוד בן-גוריון עם שיער איינשטיין לבן איקוני פורץ מחולות המדבר. 'אני בלתי נמנע!' המנדט הבריטי נעלם בעשן קומיקס. הכרזת העצמאות עם פאנלים מתפוצצים. קא-פאו! עמידות ראש ביוגה בישיבות הממשלה. בניית קיבוצים עם אפקטי אנרגיה. פרישה למדבר. 'בן-גוריון יחזור!' דגל ישראל בפינה השמאלית העליונה."
EPISODE_CHARACTERS_EN[1]="David Ben-Gurion with iconic white Einstein-like wild hair flowing dramatically, round face, determined expression, wearing simple khaki shirt like the real founder of Israel"
EPISODE_CHARACTERS_HE[1]="דוד בן-גוריון עם שיער לבן פרוע איקוני בסגנון איינשטיין זורם בדרמטיות, פנים עגולות, הבעה נחושה, לובש חולצת חאקי פשוטה כמו מייסד ישראל האמיתי"

# Episode 2: Moshe Sharett
EPISODE_TITLES[2]="Sharett - The Forgotten Avenger"
EPISODE_MISSIONS_EN[2]="Marvel intro: Moshe Sharett materializes between Ben-Gurion appearances. 'Did anyone notice I was here?' Being overshadowed montage. Spider-Man inner monologue: 'With great responsibility comes... being ignored.' Diplomatic skills like Doctor Strange. Ben-Gurion's shadow literally consuming screen. 'Is it 1955 yet?' Stan Lee cameo confusion. Israeli flag top-left."
EPISODE_MISSIONS_HE[2]="מבוא מארוול: משה שרת מתממש בין הופעות בן-גוריון. 'מישהו שם לב שהייתי פה?' מונטאז' של להיות בצל. מונולוג פנימי בסגנון ספיידרמן: 'עם כוח גדול באה... התעלמות.' כישורים דיפלומטיים כמו דוקטור סטריינג'. הצל של בן-גוריון בולע את המסך. 'זה כבר 1955?' בלבול עם קמיאו של סטן לי. דגל ישראל משמאל למעלה."
EPISODE_CHARACTERS_EN[2]="Moshe Sharett with distinctive completely bald head, round wire-frame glasses, diplomatic suit, thoughtful expression like the real second Prime Minister of Israel"
EPISODE_CHARACTERS_HE[2]="משה שרת עם ראש קירח לחלוטין מיוחד, משקפיים עגולים עם מסגרת תיל, חליפה דיפלומטית, הבעה מהורהרת כמו ראש הממשלה השני האמיתי של ישראל"

# Episode 17: Netanyahu's Current Term (from the other script)
EPISODE_TITLES[17]="Netanyahu's Current Term - The Controversy"
EPISODE_MISSIONS_EN[17]="Marvel Comics explosion! Benjamin Netanyahu with lightning effects crashes through Knesset walls. CRASH! 'I am eternal!' Opposition parties vanish in comic smoke. WHOOSH! Coalition deals with exploding panels. BOOM! Juggling multiple corruption trials while texting. ZAP! Building settlements with energy beams. THWACK! Judicial reform controversy splits the nation. CRACK! 'Bibi will return... again!' WHAM! Israeli flag with lightning bolts."
EPISODE_MISSIONS_HE[17]="פיצוץ קומיקס מארוול! בנימין נתניהו עם אפקטי ברקים מתרסק דרך קירות הכנסת. קראש! 'אני נצחי!' מפלגות האופוזיציה נעלמות בעשן קומיקס. וואוש! עסקאות קואליציה עם פאנלים מתפוצצים. בום! מלהטט במשפטי שחיתות מרובים תוך כדי סמסים. זאפ! בונה התנחלויות עם קרני אנרגיה. ת'וואק! מחלוקת הרפורמה המשפטית מפצלת את האומה. קראק! 'ביבי יחזור... שוב!' וואם! דגל ישראל עם ברקים."
EPISODE_CHARACTERS_EN[17]="Benjamin Netanyahu with gray hair, determined expression, dark suit with lightning aura, Marvel superhero style"
EPISODE_CHARACTERS_HE[17]="בנימין נתניהו עם שיער אפור, הבעה נחושה, חליפה כהה עם הילת ברקים, בסגנון גיבור על של מארוול"

# Add more episodes here as needed...

# Generate selected episodes
for ep in "${EPISODES_TO_GENERATE[@]}"; do
    if [ -n "${EPISODE_TITLES[$ep]}" ]; then
        generate_episode "$ep" \
            "${EPISODE_TITLES[$ep]}" \
            "${EPISODE_MISSIONS_EN[$ep]}" \
            "${EPISODE_MISSIONS_HE[$ep]}" \
            "${EPISODE_CHARACTERS_EN[$ep]}" \
            "${EPISODE_CHARACTERS_HE[$ep]}" \
            "israeli_pm_marvel"
    else
        echo "⚠️  Episode $ep not defined yet. Available episodes: 1, 2, 17"
    fi
done

echo ""
echo "🎬 Episode Generation Complete!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📺 Generated ${#EPISODES_TO_GENERATE[@]} episodes: ${EPISODES_TO_GENERATE[*]}"
echo ""
echo "📌 Notes for background execution:"
echo "   - Each episode takes approximately 30-50 minutes"
echo "   - Monitor progress in output folders"
echo "   - Check for .mp4 files in video_clips/veo_clips/"
echo "   - Final video will be in final_output/"
echo ""
echo "💡 To run in background:"
echo "   nohup ./run_israeli_pm_50s_final.sh > israeli_pm_log.txt 2>&1 &"
echo "   tail -f israeli_pm_log.txt"
echo ""
echo "🦸 'With great power comes great Marvel videos!' - Every Israeli PM, probably"