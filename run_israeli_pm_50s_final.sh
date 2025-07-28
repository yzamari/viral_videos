#!/bin/bash

# Israeli PM Educational Series - 40 second episodes in English
# Non-political, educational content about Israeli history and leadership

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

echo "🦸 Israeli PM Educational Series - Production Script"
echo "=============================================="
echo "⏱️  40 seconds duration (educational format)"
echo "🌐 Language: English"
echo "📚 Educational focus on history and leadership"
echo "💥 Marvel Comics style (non-political)"
echo "🎭 Consistent character appearance"
echo ""
echo "✨ EDUCATIONAL GOALS:"
echo "   - Teach about Israeli history and governance"
echo "   - Focus on leadership qualities and challenges"
echo "   - Non-political, balanced historical perspective"
echo "   - Engaging and educational content"
echo ""
echo "📺 Episodes to generate: ${EPISODES_TO_GENERATE[*]}"
echo ""

# Function to generate episode
generate_episode() {
    local ep_num=$1
    local title=$2
    local mission_en=$3
    local character_en=$4
    local session_base=$5
    
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "📺 Episode $ep_num: $title"
    echo "═══════════════════════════════════════════════════════════════"
    
    # Generate educational episode
    echo ""
    echo "📚 Generating educational episode..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    python3 main.py generate \
        --mission "$mission_en" \
        --character "$character_en" \
        --platform instagram \
        --duration 40 \
        --visual-style "marvel comics" \
        --tone educational \
        --style cinematic \
        --no-cheap \
        --voice "en-US-Neural2-J" \
        --session-id "${session_base}_ep${ep_num}" \
        --languages en-US \
        --visual-continuity \
        --content-continuity
    
    RESULT=$?
    
    if [ $RESULT -eq 0 ]; then
        echo "✅ Episode completed successfully!"
    else
        echo "❌ Episode failed with exit code: $RESULT"
    fi
    
    # Summary
    echo ""
    echo "📊 Episode $ep_num Generation Summary:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Status: $([ $RESULT -eq 0 ] && echo "✅ SUCCESS" || echo "❌ FAILED")"
    echo ""
    echo "Output folder: outputs/${session_base}_ep${ep_num}/"
    echo ""
    
    return 0
}

# Define all episode data
# Using regular arrays for episode data</# Episode data arrays

# Episode 1: David Ben-Gurion
EPISODE_TITLES[1]="Ben-Gurion - The Founding Titan"
EPISODE_MISSIONS_EN[1]="Educational Marvel style! Meet David Ben-Gurion, Israel's founding Prime Minister. Learn how this visionary leader declared independence in 1948, transforming desert into a nation. Discover his unique leadership style: doing yoga headstands to think clearly, building kibbutzim communities, and retiring to the Negev desert. Fun facts: He changed his name from David Grün, loved Greek philosophy, and believed in making the desert bloom. Historical timeline with comic panels showing key moments!"
EPISODE_MISSIONS_HE[1]="פיצוץ קומיקס מארוול! דוד בן-גוריון עם שיער איינשטיין לבן איקוני פורץ מחולות המדבר. 'אני בלתי נמנע!' המנדט הבריטי נעלם בעשן קומיקס. הכרזת העצמאות עם פאנלים מתפוצצים. קא-פאו! עמידות ראש ביוגה בישיבות הממשלה. בניית קיבוצים עם אפקטי אנרגיה. פרישה למדבר. 'בן-גוריון יחזור!' דגל ישראל בפינה השמאלית העליונה."
EPISODE_CHARACTERS_EN[1]="David Ben-Gurion with iconic white Einstein-like wild hair flowing dramatically, round face, determined expression, wearing simple khaki shirt like the real founder of Israel"
EPISODE_CHARACTERS_HE[1]="דוד בן-גוריון עם שיער לבן פרוע איקוני בסגנון איינשטיין זורם בדרמטיות, פנים עגולות, הבעה נחושה, לובש חולצת חאקי פשוטה כמו מייסד ישראל האמיתי"

# Episode 2: Moshe Sharett
EPISODE_TITLES[2]="Sharett - The Forgotten Avenger"
EPISODE_MISSIONS_EN[2]="Educational Marvel style! Meet Moshe Sharett, Israel's second Prime Minister and master diplomat. Learn how he spoke 8 languages, served as Foreign Minister, and led during challenging times (1954-1955). Discover his diplomatic approach versus Ben-Gurion's military focus, showing different leadership styles. Fun facts: He kept detailed diaries, was a talented linguist, and believed in negotiation over confrontation. Comic panels showing his UN speeches and diplomatic achievements!"
EPISODE_MISSIONS_HE[2]="מבוא מארוול: משה שרת מתממש בין הופעות בן-גוריון. 'מישהו שם לב שהייתי פה?' מונטאז' של להיות בצל. מונולוג פנימי בסגנון ספיידרמן: 'עם כוח גדול באה... התעלמות.' כישורים דיפלומטיים כמו דוקטור סטריינג'. הצל של בן-גוריון בולע את המסך. 'זה כבר 1955?' בלבול עם קמיאו של סטן לי. דגל ישראל משמאל למעלה."
EPISODE_CHARACTERS_EN[2]="Moshe Sharett with distinctive completely bald head, round wire-frame glasses, diplomatic suit, thoughtful expression like the real second Prime Minister of Israel"
EPISODE_CHARACTERS_HE[2]="משה שרת עם ראש קירח לחלוטין מיוחד, משקפיים עגולים עם מסגרת תיל, חליפה דיפלומטית, הבעה מהורהרת כמו ראש הממשלה השני האמיתי של ישראל"

# Episode 17: Netanyahu's Current Term (from the other script)
EPISODE_TITLES[17]="Netanyahu's Current Term - The Controversy"
EPISODE_MISSIONS_EN[17]="Educational Marvel style! Learn about Israel's longest-serving Prime Minister, Benjamin Netanyahu. Explore how he served multiple terms (1996-1999, 2009-2021, 2022-present), making him a unique figure in Israeli history. Discover his background: MIT graduate, special forces veteran, and UN ambassador. Learn about Israel's parliamentary system and how coalition governments work. Fun facts about Israeli democracy and the role of Prime Minister. Educational focus on governance structure!"
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
            "${EPISODE_CHARACTERS_EN[$ep]}" \
            "israeli_pm_educational"
    else
        echo "⚠️  Episode $ep not defined yet. Available episodes: 1, 2, 17"
    fi
done

echo ""
echo "🎬 Educational Series Generation Complete!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📺 Generated ${#EPISODES_TO_GENERATE[@]} episodes: ${EPISODES_TO_GENERATE[*]}"
echo ""
echo "📚 Educational Content:"
echo "   - Historical facts about Israeli leadership"
echo "   - Non-political focus on governance and history"
echo "   - Fun facts and leadership lessons"
echo "   - 40 seconds of engaging educational content"
echo ""
echo "📌 Notes for monitoring:"
echo "   - Each episode takes approximately 20-30 minutes"
echo "   - Check output folders for progress"
echo "   - Final videos in final_output/"
echo ""
echo "🎓 'Learning history through engaging stories!' - Educational Series"