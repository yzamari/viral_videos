#!/bin/bash

# Iran International Style News Satire Series
# Professional news broadcast with dark humor and cultural sensitivity
# Features consistent branding, overlays, and cultural guidelines

# Set Google Cloud project for Imagen
export GOOGLE_CLOUD_PROJECT=viralgen-464411

echo "🎬 Creating Professional Iranian News Satire Series"
echo "=================================================="
echo "📺 Iran International / BBC Persian Style"
echo "🎭 Dark Comedy with Cultural Respect"
echo ""

# Step 1: Create the series with professional news theme
echo "1️⃣ Setting up professional news series..."

# First, ensure we have the Persian News theme
echo "📋 Creating Persian News Theme..."
python -c "
import sys
sys.path.append('.')
from src.themes.managers.theme_manager import ThemeManager
from src.themes.models.theme import Theme, BrandKit, VideoTemplate, LogoConfiguration, LowerThirdsStyle, CaptionStyle, TransitionStyle

manager = ThemeManager()

# Create Persian News Theme (Iran International style)
theme = Theme(
    id='persian-news-pro',
    name='Persian News Professional',
    description='Professional Persian news broadcast theme (Iran International/BBC Persian style)',
    category='news',
    brand_kit=BrandKit(
        brand_name='Persian News Network',
        primary_color='#003366',  # Deep blue
        secondary_color='#CC0000',  # Red accent
        accent_color='#FFFFFF',
        font_family='Arial',
        logo_path='themes/persian-news-pro/logo.png',
        logo_config=LogoConfiguration(
            enabled=True,
            position='top-right',
            size=0.12,
            opacity=0.9,
            margin=20,
            fade_in_duration=0.5,
            fade_out_duration=0.5
        )
    ),
    video_template=VideoTemplate(
        intro_template_path='themes/persian-news-pro/intro.mp4',
        outro_template_path='themes/persian-news-pro/outro.mp4',
        intro_duration=3.0,
        outro_duration=2.0
    ),
    lower_thirds_style=LowerThirdsStyle(
        enabled=True,
        background_color='#003366',
        text_color='#FFFFFF',
        font_family='Arial',
        font_size=24,
        background_opacity=0.95,
        animation_type='slide',
        position='lower_third'
    ),
    caption_style=CaptionStyle(
        style_name='persian_news',
        font_family='Arial',
        font_size=32,
        text_color='#FFFFFF',
        background_enabled=True,
        background_color='#000000',
        background_opacity=0.7,
        outline_enabled=True,
        outline_color='#003366',
        outline_width=2,
        position='bottom'
    ),
    transition_style=TransitionStyle(
        transition_type='cut',
        duration=0.3
    )
)

# Save the theme
manager.save_theme(theme)
print('✅ Persian News Theme created successfully')
"

# Step 2: Create logo and assets
echo ""
echo "2️⃣ Creating news broadcast assets..."
mkdir -p themes/persian-news-pro

# Create a simple logo using ImageMagick (if available)
if command -v convert &> /dev/null; then
    echo "🎨 Creating Persian News logo..."
    convert -size 400x100 xc:transparent \
        -fill '#003366' -draw "rectangle 0,0 400,100" \
        -fill white -font Arial-Bold -pointsize 32 \
        -gravity center -annotate +0+0 'PERSIAN NEWS' \
        -bordercolor '#CC0000' -border 3x3 \
        themes/persian-news-pro/logo.png
    
    # Create intro card
    convert -size 1280x720 xc:'#003366' \
        -fill white -font Arial-Bold -pointsize 48 \
        -gravity center -annotate +0-50 'PERSIAN NEWS NETWORK' \
        -fill '#CC0000' -pointsize 36 \
        -gravity center -annotate +0+50 'خبرگزاری طنز' \
        themes/persian-news-pro/intro_card.png
else
    echo "⚠️ ImageMagick not found. Please create logo manually."
fi

# Step 3: Create Cultural Guidelines Agent
echo ""
echo "3️⃣ Setting up Cultural Sensitivity Guidelines..."
cat > cultural_guidelines_iranian.txt << 'EOF'
IRANIAN CULTURAL SENSITIVITY GUIDELINES FOR VIDEO GENERATION

MANDATORY RULES:
1. DRESS CODE:
   - Women MUST wear appropriate hijab/headscarf in all scenes
   - No revealing clothing (no shorts, tank tops, bikinis)
   - Men should wear modest clothing (no bare chest)
   - Professional attire preferred for news anchors

2. CONTENT RESTRICTIONS:
   - NO alcohol or drinking scenes
   - NO romantic physical contact between non-married individuals
   - NO dancing between mixed genders
   - NO gambling or casino imagery
   - NO pork or non-halal food references

3. RESPECTFUL SATIRE:
   - Political satire is OK but avoid insulting religious figures
   - Mock government inefficiency, not Islamic values
   - Use intelligent humor, not crude jokes
   - Reference Persian poetry and cultural wisdom

4. VISUAL GUIDELINES:
   - Use Persian/Farsi text overlays where appropriate
   - Include traditional Persian design elements
   - Avoid Western-centric imagery
   - Show respect for elders and authority figures (even in satire)

5. APPROPRIATE HUMOR TOPICS:
   - Bureaucratic inefficiency
   - Water crisis management
   - Traffic and pollution
   - Economic challenges
   - Technology adoption struggles
   - Generational differences

POSITIVE ELEMENTS TO INCLUDE:
- Persian hospitality (tarof)
- Family values and respect
- Educational achievements
- Persian cuisine references
- Poetry and literature
- Historical pride
- Scientific contributions
EOF

# Step 4: Create the series
echo ""
echo "4️⃣ Creating the news satire series..."
SERIES_ID=$(python main.py series create \
  --name "Persian News Network Satire" \
  --theme "persian-news-pro" \
  --description "Professional Persian news satire with dark humor and cultural sensitivity" \
  --template "news-daily" \
  --character "leila_hosseini" \
  --voice "professional-narrator" \
  --duration 45 \
  --quality professional 2>&1 | grep "ID:" | awk '{print $2}')

echo "Series created with ID: $SERIES_ID"

# Step 5: Generate Episodes with Cultural Awareness
echo ""
echo "🎬 Generating culturally sensitive episodes..."
echo ""

# Episode 1: Water Crisis Introduction (Professional)
echo "📺 Episode 1: 'Breaking News: National Water Crisis'"
echo "---------------------------------------------------"

python main.py generate \
  --series "$SERIES_ID" \
  --mission "CULTURAL GUIDELINES: Women wear hijab, modest clothing, respectful satire. Professional Persian news broadcast about water crisis. Anchor Leila Hosseini in hijab reports: 'In tonight's news, Iran faces unprecedented water shortage. Government officials assure citizens that forming committees to discuss committee formation is top priority.' Show professional graphics: water level charts, drought maps. Include Persian text overlays. Lower third: 'لیلا حسینی - گزارشگر ارشد' (Leila Hosseini - Senior Reporter). Serious tone with subtle irony." \
  --episode-title "Water Crisis Special Report" \
  --platform tiktok \
  --style news \
  --visual-style professional \
  --tone serious \
  --overlay-style news_lower_thirds \
  --subtitle-position bottom_third \
  --include-logo true \
  --cultural-guidelines iranian \
  --no-cheap \
  --mode professional \
  --session-id "persian_news_ep1"

sleep 15

# Episode 2: Bureaucracy Satire
echo ""
echo "📺 Episode 2: 'Government Forms Water Committee Committee'"
echo "--------------------------------------------------------"

python main.py generate \
  --series "$SERIES_ID" \
  --mission "RESPECT CULTURE: Hijab required, no alcohol, professional satire only. Leila continues: 'Breaking: Government announces formation of Supreme Water Committee, which will oversee the Water Strategy Committee, reporting to the Water Crisis Committee.' Show footage of empty reservoirs while officials drink tea in meetings. Persian subtitle: 'کمیته آب کمیته تشکیل داد' (Water committee formed a committee). Professional graphics showing bureaucratic flowchart. Deadpan delivery with ironic undertone." \
  --episode-title "Bureaucratic Solutions" \
  --platform tiktok \
  --style news \
  --visual-style professional \
  --tone satirical \
  --overlay-style news_lower_thirds \
  --cultural-guidelines iranian \
  --no-cheap \
  --mode professional \
  --session-id "persian_news_ep2"

sleep 15

# Episode 3: Weather Report - "Hot and Nuclear"
echo ""
echo "📺 Episode 3: 'Weather Forecast: Hot and Nuclear'"
echo "------------------------------------------------"

python main.py generate \
  --series "$SERIES_ID" \
  --mission "CULTURAL RESPECT: Appropriate dress, no Western imagery, intelligent humor. Weather segment with Ahmad Rezaei. 'Now for weather: Tehran tomorrow will be hot with a chance of nuclear.' Show weather map with uranium symbols instead of sun icons. Temperature: '45°C and enriching.' Ahmad deadpan: 'Citizens advised to carry both sunscreen and Geiger counters.' Persian text: 'آب و هوای هسته‌ای' (Nuclear Weather). Dark humor about sanctions affecting even weather reports. Professional broadcast quality." \
  --episode-title "Nuclear Weather Forecast" \
  --character ahmad_rezaei \
  --platform tiktok \
  --style news \
  --visual-style professional \
  --tone darkly_humorous \
  --overlay-style weather_forecast \
  --cultural-guidelines iranian \
  --no-cheap \
  --mode professional \
  --session-id "persian_news_ep3"

sleep 15

# Episode 4: Solutions Segment
echo ""
echo "📺 Episode 4: 'Innovative Solutions: Prayer for Rain Committee'"
echo "-------------------------------------------------------------"

python main.py generate \
  --series "$SERIES_ID" \
  --mission "MAINTAIN RESPECT: Religious sensitivity, hijab, no mockery of faith. Leila reports on government solutions: 'Ministry announces new initiative: National Prayer for Rain Day, followed by Cloud Import Feasibility Study.' Show officials looking at sky with binoculars, measuring clouds. Include Persian proverb: 'آسمان که ابر ندارد، دعا هم باران نمی‌آورد' (When sky has no clouds, even prayer won't bring rain). Subtle satire on mixing practical solutions with wishful thinking. Professional news graphics throughout." \
  --episode-title "Divine Intervention Plans" \
  --platform tiktok \
  --style news \
  --visual-style professional \
  --tone satirical \
  --overlay-style news_breaking \
  --cultural-guidelines iranian \
  --no-cheap \
  --mode professional \
  --session-id "persian_news_ep4"

sleep 15

# Episode 5: Economic Impact
echo ""
echo "📺 Episode 5: 'Water Black Market: Bottled Water Now Costs More Than Oil'"
echo "------------------------------------------------------------------------"

python main.py generate \
  --series "$SERIES_ID" \
  --mission "CULTURAL AWARENESS: Modest dress, economic satire OK, respect traditions. Ahmad reports: 'In economic news, bottled water reaches record prices on Tehran black market. One liter now costs more than barrel of oil. Citizens joke: At least we're still world leader in something!' Show water bottles with security tags, water ATMs. Persian text shows prices. Include tarof joke: 'No, you drink first... No, I insist, you're the guest... Actually, nobody drinks, we save water!' Professional broadcast with economic charts." \
  --episode-title "Water Economy Crisis" \
  --character ahmad_rezaei \
  --platform tiktok \
  --style news \
  --visual-style professional \
  --tone darkly_humorous \
  --overlay-style news_financial \
  --cultural-guidelines iranian \
  --no-cheap \
  --mode professional \
  --session-id "persian_news_ep5"

echo ""
echo "🎉 PERSIAN NEWS SATIRE SERIES COMPLETE!"
echo ""
echo "📁 Professional news series ready:"
echo "   Episode 1 - Water Crisis Report: outputs/session_persian_news_ep1/"
echo "   Episode 2 - Bureaucracy Satire: outputs/session_persian_news_ep2/"
echo "   Episode 3 - Nuclear Weather: outputs/session_persian_news_ep3/"
echo "   Episode 4 - Prayer Solutions: outputs/session_persian_news_ep4/"
echo "   Episode 5 - Water Economy: outputs/session_persian_news_ep5/"
echo ""
echo "🏆 SERIES FEATURES:"
echo "   📺 Professional news broadcast quality"
echo "   🎨 Consistent Iran International/BBC Persian styling"
echo "   👳 Cultural sensitivity maintained throughout"
echo "   😂 Dark humor without crossing cultural lines"
echo "   📊 Professional graphics and overlays"
echo "   🇮🇷 Persian text integration"
echo ""
echo "💡 Cultural Guidelines Respected:"
echo "   ✅ Appropriate hijab and modest dress"
echo "   ✅ No alcohol or inappropriate content"
echo "   ✅ Respectful political satire"
echo "   ✅ Persian cultural references"
echo "   ✅ Intelligent humor approach"
echo ""
echo "📺 Ready for Persian-speaking audience!"