#!/bin/bash

# Israeli Prime Ministers Ghibli Style - Hebrew Series for Israeli/Zionist Audience
# TikTok format with realistic characters and magical Studio Ghibli aesthetics

# Parse command line arguments
EPISODES_TO_GENERATE=()
LANGUAGE="he"  # Default to Hebrew

while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--episodes)
            shift
            while [[ $# -gt 0 && ! "$1" =~ ^- ]]; do
                EPISODES_TO_GENERATE+=("$1")
                shift
            done
            ;;
        -l|--language)
            LANGUAGE="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -e, --episodes <num1> <num2> ...  Generate specific episodes"
            echo "  -l, --language <he|en>            Language (he=Hebrew, en=English)"
            echo "  -h, --help                        Show this help message"
            echo ""
            echo "Available episodes:"
            echo "  1: Ben-Gurion - הנשר הגדול (The Great Eagle)"
            echo "  2: Sharett - השגריר הקסום (The Magical Ambassador)"
            echo "  3: Eshkol - הרועה הטוב (The Good Shepherd)"
            echo "  4: Golda - האישה הברזל (The Iron Lady)"
            echo "  5: Rabin - לוחם השלום (The Peace Warrior)"
            echo "  6: Begin - המלך התחתון (The Underground King)"
            echo "  7: Shamir - הרוח הקשה (The Tough Spirit)"
            echo "  8: Peres - חולם השלום (The Peace Dreamer)"
            echo "  9: Netanyahu - הקוסם הנצחי (The Eternal Magician)"
            echo ""
            echo "Examples:"
            echo "  $0 -e 4              # Generate Golda episode in Hebrew"
            echo "  $0 -e 4 -l en        # Generate Golda episode in English"
            echo "  $0 -e 1 4 9          # Generate episodes 1, 4, and 9 in Hebrew"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# If no episodes specified, show help
if [ ${#EPISODES_TO_GENERATE[@]} -eq 0 ]; then
    echo "ℹ️  No episodes specified. Use -h for help."
    exit 1
fi

echo "🌸 Israeli Prime Ministers - Studio Ghibli Series"
echo "=============================================="
echo "🎌 Style: Studio Ghibli magical realism"
echo "📱 Platform: TikTok"
echo "⏱️  Duration: 64 seconds"
echo "🎭 Characters: Realistic appearance with magical elements"
echo "🎯 Audience: Israeli and Zionist people worldwide"
echo "🌐 Language: $([ "$LANGUAGE" = "he" ] && echo "עברית (Hebrew)" || echo "English")"
echo ""
echo "✨ SERIES GOALS:"
echo "   - Inspire Israeli and Zionist pride"
echo "   - Magical storytelling with historical accuracy"
echo "   - Beautiful Ghibli-style visuals"
echo "   - Connect diaspora Jews to Israeli leadership"
echo ""
echo "📺 Episodes to generate: ${EPISODES_TO_GENERATE[*]}"
echo ""

# Function to generate episode
generate_episode() {
    local ep_num=$1
    local title=$2
    local mission=$3
    local character=$4
    local session_base=$5
    local lang=$6
    
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "📺 Episode $ep_num: $title"
    echo "═══════════════════════════════════════════════════════════════"
    
    # Generate Ghibli episode
    echo ""
    echo "🌸 Generating magical Ghibli episode..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    python3 main.py generate \
        --mission "$mission" \
        --character "$character" \
        --platform tiktok \
        --duration 64 \
        --visual-style "studio ghibli magical realism realistic characters" \
        --tone inspiring \
        --style cinematic \
        --theme whimsical \
        --no-cheap \
        --voice "$([ "$lang" = "he" ] && echo "he-IL-AvriNeural" || echo "en-US-Neural2-A")" \
        --session-id "${session_base}_ep${ep_num}_${lang}" \
        --languages "$lang" \
        --visual-continuity \
        --content-continuity \
        --target-audience "israeli zionist diaspora jews" \
        --mode enhanced
    
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
    echo "Output folder: outputs/${session_base}_ep${ep_num}_${lang}/"
    echo ""
    
    return 0
}

# Episode data is defined inline in the case statement below

# Generate selected episodes
for ep in "${EPISODES_TO_GENERATE[@]}"; do
    # Get episode data based on episode number
    case $ep in
        1)
            if [ "$LANGUAGE" = "he" ]; then
                title="בן-גוריון - הנשר הגדול"
                mission="בסגנון סטודיו גיבלי קסום! פגשו את דוד בן-גוריון, ראש הממשלה הראשון של ישראל. ביער קסום של הגליל, נשר זקן בעיניים כחולות זוהרות מכריז על עצמאות ישראל מתוך עץ זית עתיק. רוחות קדושות של אבות האומה מרחפות סביבו כשהוא הופך מדבר לגן עדן עם כוחות קסם. נוכחותו מלאת הרוח היהודית העתיקה משעמת עמו הפזור ברחבי העולם. עם שיער לבן זורם ובגדים פשוטים, הוא אבא של האומה שהחזיר את עמו הביתה. לבביים גיבלי עם מוזיקה רגשית."
                character="דוד בן-גוריון עם מראה אמיתי מדויק - שיער לבן פרוע איקוני, פנים עגולות, הבעה נחושה וחמה, לובש חולצת חאקי פשוטה, אבל מוקף בהילה קסומה של אורות זהובים ונוצות נשר זוהרות בסגנון גיבלי"
            else
                title="Ben-Gurion - The Great Eagle"
                mission="Studio Ghibli magic! Meet David Ben-Gurion, Israel's founding Prime Minister. In a magical Galilee forest, an old eagle with glowing blue eyes declares Israel's independence from atop an ancient olive tree. Holy spirits of the nation's forefathers hover around him as he transforms desert into paradise with magical powers. His presence filled with ancient Jewish spirit inspires his scattered people worldwide. With flowing white hair and simple clothes, he's the father of the nation who brought his people home. Heartwarming Ghibli with emotional music."
                character="David Ben-Gurion with accurate realistic appearance - iconic wild white hair, round face, determined warm expression, wearing simple khaki shirt, but surrounded by magical aura of golden lights and glowing eagle feathers in Ghibli style"
            fi
            ;;
        2)
            if [ "$LANGUAGE" = "he" ]; then
                title="שרת - השגריר הקסום"
                mission="בסגנון סטודיו גיבלי קסום! משה שרת, ראש הממשלה השני, מרחף בין עננים כשהוא מדבר 8 שפות עם רוחות של אומות העולם. כל מילה שהוא אומר הופכת לפרפר צבעוני שעף לכיוון השלום. עם משקפיים זוהרים וחליפה דיפלומטית, הוא אמן המילים שבונה גשרים בין עמים. בספרייה קסומה מלאה בספרים מרחפים, הוא כותב את יומניו כשדיו זהוב זורם מהעט. יונים לבנות מקיפות אותו, סמל לחתירתו לשלום. רגשות חמים של אהבת המולדת וחכמה יהודית עתיקה."
                character="משה שרת עם מראה אמיתי מדויק - ראש קירח לחלוטין, משקפיים עגולים עם מסגרת תיל, חליפה דיפלומטית אלגנטית, הבעה מהורהרת וחכמה, מוקף בפרפרים זוהרים ויונים לבנות בסגנון גיבלי"
            else
                title="Sharett - The Magical Ambassador"
                mission="Studio Ghibli magic! Moshe Sharett, Israel's second Prime Minister, floats among clouds speaking 8 languages with spirits of world nations. Every word he speaks transforms into colorful butterflies flying toward peace. With glowing glasses and diplomatic suit, he's a word artist building bridges between peoples. In a magical library full of floating books, he writes his diaries as golden ink flows from his pen. White doves surround him, symbol of his quest for peace. Warm feelings of homeland love and ancient Jewish wisdom."
                character="Moshe Sharett with accurate realistic appearance - completely bald head, round wire-frame glasses, elegant diplomatic suit, thoughtful wise expression, surrounded by glowing butterflies and white doves in Ghibli style"
            fi
            ;;
        4)
            if [ "$LANGUAGE" = "he" ]; then
                title="גולדה - האישה הברזל"
                mission="Studio Ghibli magic! Golda Meir, the nation's mother, sits at an ancient wooden table in Jerusalem's magical synagogue. Her smoking transforms into spiritual figures of strong pioneer women as she magically prepares tea for world leaders. With her old leather handbag and warm maternal smile, she radiates strength and compassion. During the difficult Yom Kippur period, she becomes a protective goddess with golden eagle wings, defending her children. Long nights of difficult decisions as holy candles burn. She proved that a Jewish mother can lead a nation."
                character="גולדה מאיר עם מראה אמיתי מדויק - שיער אפור מסורק לאחור, פנים מלבניות וחזקות, עיניים חדות וחמות, לובשת שמלה פשוטה וכהה עם תיק עור ישן, מוקפת בזוהר אמהותי זהוב וכנפי נשר בסגנון גיבלי"
            else
                title="Golda - The Iron Lady"
                mission="Studio Ghibli magic! Golda Meir, the nation's mother, sits at an ancient wooden table in Jerusalem's magical synagogue. Her smoking transforms into spiritual figures of strong pioneer women as she magically prepares tea for world leaders. With her old leather handbag and warm maternal smile, she radiates strength and compassion. During the difficult Yom Kippur period, she becomes a protective goddess with golden eagle wings, defending her children. Long nights of difficult decisions as holy candles burn. She proved that a Jewish mother can lead a nation."
                character="Golda Meir with accurate realistic appearance - gray hair combed back, strong rectangular face, sharp warm eyes, wearing simple dark dress with old leather handbag, surrounded by golden maternal glow and eagle wings in Ghibli style"
            fi
            ;;
        5)
            # CRITICAL: Mission should ALWAYS be in English (only output in target language)
            title=$([ "$LANGUAGE" = "he" ] && echo "רבין - לוחם השלום" || echo "Rabin - The Peace Warrior")
            mission="Studio Ghibli magic! Yitzhak Rabin, the soldier turned peacemaker, stands in a magical battlefield as swords transform into olive trees. With military uniform changing to white peace garments, he extends his hand toward yesterday's enemies. Peace angels hover around him as he signs the Oslo Accords under the ancient olive tree. Blue eyes full of pain and compassion, he knows peace requires sacrifice. The handshake with Arafat becomes a rainbow bridge of light over Jerusalem. Heart-touching music of a peace hero who fell holy."
            character="Yitzhak Rabin with accurate realistic appearance - long serious face, deep blue eyes, gray hair, military uniform transforming to white clothes, surrounded by glowing peace wings and floating olive leaves in Ghibli style"
            ;;
        7)
            # Yitzhak Shamir
            title=$([ "$LANGUAGE" = "he" ] && echo "שמיר - הסלע שאינו נכנע" || echo "Shamir - The Unyielding Rock")
            mission="Studio Ghibli magic! Yitzhak Shamir, the underground fighter turned Prime Minister, emerges from Jerusalem's ancient stone walls like a guardian spirit. Small in stature but mighty in spirit, he stands firm as mystical winds of change blow around him. Underground tunnels glow with memories of his Lehi days as he transforms from shadow warrior to nation leader. His piercing eyes see through diplomatic illusions. Stone tablets of Jewish history float around him as he declares 'The sea is the same sea, the Arabs are the same Arabs.' Dramatic music of unwavering determination."
            character="Yitzhak Shamir with accurate realistic appearance - small stature, thin sharp face, intense eyes, gray hair, simple dark suit, surrounded by glowing ancient stones and mystical shadows of his underground past in Ghibli style"
            ;;
        8)
            # Ehud Barak
            title=$([ "$LANGUAGE" = "he" ] && echo "ברק - הלוחם החכם" || echo "Barak - The Wise Warrior")
            mission="Studio Ghibli magic! Ehud Barak, Israel's most decorated soldier, transforms from special forces commander to peace seeker. Lightning bolts form his tactical genius as he dismantles watches and reassembles them into time machines showing alternate futures. In his IDF uniform covered with magical medals, each medal tells a story of bravery. At Camp David, he tries to solve the peace puzzle as mystical pieces float in the air. His analytical mind projects holographic battle plans that morph into peace doves. Music of a brilliant strategist seeking the impossible dream."
            character="Ehud Barak with accurate realistic appearance - sharp intelligent face, piercing eyes, gray hair, military bearing even in civilian clothes, surrounded by floating tactical maps transforming into peace symbols in Ghibli style"
            ;;
        10)
            # Shimon Peres
            title=$([ "$LANGUAGE" = "he" ] && echo "פרס - החולם הנצחי" || echo "Peres - The Eternal Dreamer")
            mission="Studio Ghibli magic! Shimon Peres, the visionary dreamer, stands in a field of high-tech flowers blooming from ancient desert sand. His dreams manifest as colorful birds carrying startup ideas across the sky. With gentle smile and wise eyes, he builds bridges of light between old and new Israel. The Dimona reactor glows with peaceful atomic energy as he whispers secrets to the wind. In his magical workshop, peace agreements transform into origami cranes. At 90, he still dreams of tomorrow, teaching robots to dance the hora. Inspiring music of eternal optimism."
            character="Shimon Peres with accurate realistic appearance - distinguished elder statesman look, white hair, kind wise eyes behind glasses, gentle smile, elegant suit, surrounded by futuristic holograms and peace doves in Ghibli style"
            ;;
        11)
            # Ariel Sharon
            title=$([ "$LANGUAGE" = "he" ] && echo "שרון - האריה של החולות" || echo "Sharon - The Lion of the Sands")
            mission="Studio Ghibli magic! Ariel Sharon, the warrior farmer, rides a magical bulldozer that transforms desert into blooming settlements. His military maps become living landscapes where toy soldiers dance the dance of war and peace. With his iconic paratrooper wings glowing, he commands both armies and orange groves. The controversial Gaza disengagement shows him cutting magical threads with golden scissors, tears in his eyes. His large frame contains the spirit of a lion protecting his cubs. From Sabra warrior to surprising peacemaker. Epic music of a complex leader."
            character="Ariel Sharon with accurate realistic appearance - large robust build, round face, white hair, determined expression, military or farmer attire, surrounded by magical orange groves and glowing paratrooper wings in Ghibli style"
            ;;
        9)
            if [ "$LANGUAGE" = "he" ]; then
                title="נתניהו - הקוסם הנצחי"
                mission="Studio Ghibli magic! Benjamin Netanyahu, the political magician, sits in a crystal tower above Jerusalem as spellbooks full of political tactics float around him. With a dark suit shining like magical armor and eagle-sharp eyes, he controls political forces like a king. His voice echoes with his powerful staff as he makes statements that move nations. But beneath the magic, his heart still beats with love for Israel. A typhoon of controversies surrounds him, but he stands firm as a rock against the storm. Epic music of an eternal leader."
                character="בנימין נתניהו עם מראה אמיתי מדויק - שיער אפור מסורק, פנים חדות וחזקות, עיניים כחולות חודרות, חליפה כהה אלגנטית, מוקף בהילה קסומה של ברקים זהובים ומגן דוד מרחף בסגנון גיבלי"
            else
                title="Netanyahu - The Eternal Magician"
                mission="Studio Ghibli magic! Benjamin Netanyahu, the political magician, sits in a crystal tower above Jerusalem as spellbooks full of political tactics float around him. With a dark suit shining like magical armor and eagle-sharp eyes, he controls political forces like a king. His voice echoes with his powerful staff as he makes statements that move nations. But beneath the magic, his heart still beats with love for Israel. A typhoon of controversies surrounds him, but he stands firm as a rock against the storm. Epic music of an eternal leader."
                character="Benjamin Netanyahu with accurate realistic appearance - gray combed hair, sharp strong face, piercing blue eyes, elegant dark suit, surrounded by magical aura of golden lightning and floating Star of David in Ghibli style"
            fi
            ;;
        *)
            echo "⚠️  Episode $ep not defined yet. Available episodes: 1, 2, 4, 5, 9"
            continue
            ;;
    esac
    
    if [ -n "$title" ]; then
        generate_episode "$ep" \
            "$title" \
            "$mission" \
            "$character" \
            "israeli_pm_ghibli" \
            "$LANGUAGE"
    fi
done

echo ""
echo "🌸 Studio Ghibli Israeli PM Series Complete!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📺 Generated ${#EPISODES_TO_GENERATE[@]} episodes: ${EPISODES_TO_GENERATE[*]}"
echo "🌐 Language: $([ "$LANGUAGE" = "he" ] && echo "עברית (Hebrew)" || echo "English")"
echo ""
echo "✨ Series Features:"
echo "   - Studio Ghibli magical realism style"
echo "   - Realistic character appearances with magical elements"
echo "   - TikTok format (64 seconds)"
echo "   - Inspiring content for Israeli and Zionist audiences"
echo "   - Beautiful cinematography and emotional storytelling"
echo ""
echo "🎌 'מחברים את העם שלנו לתולדותיו הקסומים' - Israeli PM Ghibli Series"