#!/bin/bash

# Israeli PM Marvel Series - 50 second episodes with English and Hebrew
# Ready for background execution in separate thread

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

# Episode 1: David Ben-Gurion
generate_episode 1 \
    "Ben-Gurion - The Founding Titan" \
    "Marvel Comics explosion! David Ben-Gurion with iconic white Einstein hair bursts from desert sands. 'I am INEVITABLE!' SNAP! British Mandate vanishes in comic smoke. Declaration of Independence with exploding panels. KA-POW! Yoga headstands during cabinet meetings. Building kibbutzim with energy effects. Desert retirement. 'Ben-Gurion will return!' Israeli flag in top-left corner." \
    "פיצוץ קומיקס מארוול! דוד בן-גוריון עם שיער איינשטיין לבן איקוני פורץ מחולות המדבר. 'אני בלתי נמנע!' המנדט הבריטי נעלם בעשן קומיקס. הכרזת העצמאות עם פאנלים מתפוצצים. קא-פאו! עמידות ראש ביוגה בישיבות הממשלה. בניית קיבוצים עם אפקטי אנרגיה. פרישה למדבר. 'בן-גוריון יחזור!' דגל ישראל בפינה השמאלית העליונה." \
    "David Ben-Gurion with iconic white Einstein-like wild hair flowing dramatically, round face, determined expression, wearing simple khaki shirt like the real founder of Israel" \
    "דוד בן-גוריון עם שיער לבן פרוע איקוני בסגנון איינשטיין זורם בדרמטיות, פנים עגולות, הבעה נחושה, לובש חולצת חאקי פשוטה כמו מייסד ישראל האמיתי" \
    "israeli_pm_marvel"

# Episode 2: Moshe Sharett (uncomment to run)
# generate_episode 2 \
#     "Sharett - The Forgotten Avenger" \
#     "Marvel intro: Moshe Sharett materializes between Ben-Gurion appearances. 'Did anyone notice I was here?' Being overshadowed montage. Spider-Man inner monologue: 'With great responsibility comes... being ignored.' Diplomatic skills like Doctor Strange. Ben-Gurion's shadow literally consuming screen. 'Is it 1955 yet?' Stan Lee cameo confusion. Israeli flag top-left." \
#     "מבוא מארוול: משה שרת מתממש בין הופעות בן-גוריון. 'מישהו שם לב שהייתי פה?' מונטאז' של להיות בצל. מונולוג פנימי בסגנון ספיידרמן: 'עם כוח גדול באה... התעלמות.' כישורים דיפלומטיים כמו דוקטור סטריינג'. הצל של בן-גוריון בולע את המסך. 'זה כבר 1955?' בלבול עם קמיאו של סטן לי. דגל ישראל משמאל למעלה." \
#     "Moshe Sharett with distinctive completely bald head, round wire-frame glasses, diplomatic suit, thoughtful expression like the real second Prime Minister of Israel" \
#     "משה שרת עם ראש קירח לחלוטין מיוחד, משקפיים עגולים עם מסגרת תיל, חליפה דיפלומטית, הבעה מהורהרת כמו ראש הממשלה השני האמיתי של ישראל" \
#     "israeli_pm_marvel"

echo ""
echo "🎬 Episode Generation Complete!"
echo "═══════════════════════════════════════════════════════════════"
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