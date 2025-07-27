#!/bin/bash

# Iran International News - Family Guy Style with News Overlay
# English and Hebrew versions - 50 seconds each

echo "🎬 Iran International News - Family Guy Style"
echo "============================================="
echo "🎨 Family Guy animation style"
echo "📺 Professional news overlay"
echo "🌐 Languages: English & Hebrew"
echo "⏱️  50 seconds duration (~8 clips of 5-8s each)"
echo ""
echo "✨ IMPROVEMENTS APPLIED:"
echo "   - Video clips now 5-8 seconds (not 0.5-2s)"
echo "   - Hebrew script/audio/subtitles (not English)"
echo "   - RTL text rendering for Hebrew overlays"
echo "   - Frame continuity between clips"
echo ""

# Function to generate news episode
generate_news_episode() {
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
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    python3 main.py generate \
        --mission "$mission_en" \
        --character "$character_en" \
        --platform youtube \
        --duration 50 \
        --visual-style "family guy animation" \
        --tone darkly_humorous \
        --style news \
        --no-cheap \
        --voice "en-US-Neural2-F" \
        --session-id "${session_base}_ep${ep_num}_en" \
        --languages en-US \
        --visual-continuity \
        --content-continuity \
        --scene "Family Guy style animated news studio, Iran International logo, professional news desk with overlay graphics"
    
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
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    python3 main.py generate \
        --mission "$mission_he" \
        --character "$character_he" \
        --platform youtube \
        --duration 50 \
        --visual-style "family guy animation" \
        --tone darkly_humorous \
        --style news \
        --no-cheap \
        --voice "he-IL-Wavenet-C" \
        --session-id "${session_base}_ep${ep_num}_he" \
        --languages he \
        --visual-continuity \
        --content-continuity \
        --scene "Family Guy style animated news studio, Iran International logo in Hebrew, professional news desk with RTL overlay graphics"
    
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

# Episode 1: Water Crisis Breaking News
EPISODE_TITLES[1]="Water Crisis - Breaking News"
EPISODE_MISSIONS_EN[1]="Family Guy style animated news. Professional news overlay graphics. Iran International logo top-right. News anchor Maryam (Persian Lois Griffin with hijab, huge eyes) reports: 'BREAKING NEWS: Scientists confirm water has officially ghosted Iran. It left no forwarding address.' Show cartoon map of Iran with water droplets running away with suitcases. News ticker: 'WATER CRISIS DAY 1,847'. Peter Griffin-style official: 'Water? Never heard of her.' Citizens licking morning dew. Lower third: 'EXCLUSIVE: Dew Licking Tutorial at 11'"
EPISODE_MISSIONS_HE[1]="חדשות בסגנון פמילי גאי. גרפיקת חדשות מקצועית. לוגו איראן אינטרנשיונל מימין למעלה. קריינית החדשות מרים (לויס גריפין פרסית עם חיג'אב, עיניים ענקיות) מדווחת: 'מבזק: מדענים מאשרים שהמים נטשו את איראן. לא השאירו כתובת להעברת דואר.' מפת איראן מצוירת עם טיפות מים בורחות עם מזוודות. טיקר חדשות: 'יום 1,847 למשבר המים'. פקיד בסגנון פיטר גריפין: 'מים? לא מכיר אותה.' אזרחים מלקקים טל. כותרת תחתונה: 'בלעדי: מדריך ללקק טל ב-11'"
EPISODE_CHARACTERS_EN[1]="Animated news anchor Maryam - Family Guy style Persian woman with oversized hijab, huge expressive eyes, Lois Griffin body type but Persian features, professional blazer"
EPISODE_CHARACTERS_HE[1]="קריינית חדשות מצוירת מרים - אישה פרסית בסגנון פמילי גאי עם חיג'אב גדול מדי, עיניים ענקיות ומבעיות, מבנה גוף של לויס גריפין אך עם תווי פנים פרסיים, בלייזר מקצועי"

# Episode 2: Committee Committee Committee
EPISODE_TITLES[2]="Committee Committee Committee"
EPISODE_MISSIONS_EN[2]="Family Guy news continues. Same anchor Maryam announces: 'BREAKING: Government unveils master plan - Committee to form committee about committees.' Professional news graphics show organizational chart exploding. Cutaway: Stewie-style minister: 'I propose we form a sub-committee!' Room of identical officials nodding. News ticker: 'COMMITTEE COUNT: ∞'. Lower third: 'EXCLUSIVE INTERVIEW: Chairman of Nothing Committee'. Maryam's eye twitches. Map shows committee buildings multiplying like cancer cells. 'This is fine' meme in corner."
EPISODE_MISSIONS_HE[2]="חדשות פמילי גאי ממשיכות. אותה קריינית מרים מכריזה: 'מבזק: הממשלה חושפת תוכנית - ועדה להקמת ועדה על ועדות.' גרפיקת חדשות מציגה תרשים ארגוני מתפוצץ. קטאוויי: שר בסגנון סטואי: 'אני מציע שנקים תת-ועדה!' חדר מלא פקידים זהים מהנהנים. טיקר: 'ספירת ועדות: ∞'. כותרת: 'ראיון בלעדי: יו״ר ועדת הכלום'. העין של מרים מתעוותת. מפה מראה בנייני ועדות מתרבים כמו סרטן."
EPISODE_CHARACTERS_EN[2]="Same Maryam - consistent Family Guy Persian anchor, hijab slightly disheveled from stress, eye twitching, professional but losing patience"
EPISODE_CHARACTERS_HE[2]="אותה מרים - קריינית פרסית עקבית בסגנון פמילי גאי, חיג'אב מעט פרוע מלחץ, עין מתעוותת, מקצועית אך מאבדת סבלנות"

# Add more episodes here as needed...

# Generate selected episodes
for ep in "${EPISODES_TO_GENERATE[@]}"; do
    if [ -n "${EPISODE_TITLES[$ep]}" ]; then
        generate_news_episode "$ep" \
            "${EPISODE_TITLES[$ep]}" \
            "${EPISODE_MISSIONS_EN[$ep]}" \
            "${EPISODE_MISSIONS_HE[$ep]}" \
            "${EPISODE_CHARACTERS_EN[$ep]}" \
            "${EPISODE_CHARACTERS_HE[$ep]}" \
            "iran_news_family_guy"
    else
        echo "⚠️  Episode $ep not defined yet. Available episodes: 1, 2"
    fi
done

echo ""
echo "🎬 News Generation Complete!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📌 Features:"
echo "   - Family Guy animation style"
echo "   - Professional news overlay graphics"
echo "   - Iran International branding"
echo "   - News ticker and lower thirds"
echo "   - Consistent character (Maryam)"
echo ""
echo "💡 To run in background:"
echo "   nohup ./run_iran_news_family_guy_final.sh > iran_news_log.txt 2>&1 &"
echo "   tail -f iran_news_log.txt"
echo ""
echo "📺 'And now, back to your regularly scheduled water crisis!' - Iran International"