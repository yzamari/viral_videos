#!/bin/bash

# Create professional news assets for Persian News theme

echo "🎨 Creating Persian News Professional Assets"
echo "==========================================="

# Create directories
mkdir -p persian-news-pro/overlays
mkdir -p persian-news-pro/lower_thirds
mkdir -p persian-news-pro/graphics

# Check if ImageMagick is available
if ! command -v convert &> /dev/null; then
    echo "❌ ImageMagick not found. Please install it:"
    echo "   macOS: brew install imagemagick"
    echo "   Linux: sudo apt-get install imagemagick"
    exit 1
fi

# Create main logo (Iran International style)
echo "Creating main logo..."
convert -size 400x120 xc:transparent \
    -fill '#003366' -draw "roundrectangle 10,10 390,110 15,15" \
    -fill white -font Arial-Bold -pointsize 36 \
    -gravity center -annotate +0-10 'PERSIAN NEWS' \
    -fill '#CC0000' -font Arial -pointsize 20 \
    -gravity center -annotate +0+25 'شبکه خبری فارسی' \
    logo.png

# Create small corner logo
echo "Creating corner logo..."
convert logo.png -resize 200x60 logo_small.png

# Create breaking news banner
echo "Creating breaking news banner..."
convert -size 1280x100 xc:transparent \
    -fill '#CC0000' -draw "rectangle 0,0 1280,100" \
    -fill white -font Arial-Bold -pointsize 48 \
    -gravity west -annotate +50+0 'BREAKING NEWS' \
    -fill white -font Arial-Bold -pointsize 36 \
    -gravity east -annotate +400+0 'خبر فوری' \
    overlays/breaking_news.png

# Create lower thirds background
echo "Creating lower thirds template..."
convert -size 800x120 xc:transparent \
    -fill '#003366' -draw "polygon 0,30 800,30 800,120 0,120" \
    -fill '#CC0000' -draw "rectangle 0,0 800,30" \
    lower_thirds/lower_third_bg.png

# Create weather graphics background
echo "Creating weather template..."
convert -size 400x300 xc:'rgba(0,51,102,0.9)' \
    -fill white -font Arial-Bold -pointsize 24 \
    -gravity north -annotate +0+20 'WEATHER / آب و هوا' \
    graphics/weather_bg.png

# Create news ticker background
echo "Creating news ticker..."
convert -size 1280x60 xc:'#003366' \
    -fill '#CC0000' -draw "rectangle 0,0 200,60" \
    -fill white -font Arial-Bold -pointsize 28 \
    -gravity west -annotate +20+0 'NEWS' \
    overlays/ticker_bg.png

# Create intro background
echo "Creating intro sequence..."
convert -size 1280x720 \
    -define gradient:vector="0,0 1280,720" \
    gradient:'#003366'-'#001133' \
    -fill white -font Arial-Bold -pointsize 72 \
    -gravity center -annotate +0-50 'PERSIAN NEWS' \
    -fill '#CC0000' -pointsize 48 \
    -gravity center -annotate +0+50 'شبکه خبری فارسی' \
    intro_bg.png

# Create outro background
echo "Creating outro sequence..."
convert -size 1280x720 xc:'#003366' \
    -fill white -font Arial -pointsize 36 \
    -gravity center -annotate +0+0 'Thank you for watching\nبا تشکر از شما' \
    outro_bg.png

# Create sample lower third with name
echo "Creating sample lower thirds..."
convert -size 800x120 xc:transparent \
    lower_thirds/lower_third_bg.png -composite \
    -fill white -font Arial-Bold -pointsize 32 \
    -gravity west -annotate +50+10 'Leila Hosseini' \
    -fill white -font Arial -pointsize 24 \
    -gravity west -annotate +50+50 'Senior Correspondent / گزارشگر ارشد' \
    lower_thirds/sample_anchor.png

# Create transparent overlays for effects
echo "Creating effect overlays..."
convert -size 1280x720 xc:transparent \
    -fill 'rgba(0,51,102,0.1)' -draw "rectangle 0,0 1280,720" \
    overlays/blue_tint.png

# Create side panel for information
echo "Creating information panel..."
convert -size 400x500 xc:'rgba(0,51,102,0.95)' \
    -fill white -font Arial-Bold -pointsize 28 \
    -gravity north -annotate +0+30 'KEY POINTS' \
    -fill '#CC0000' -draw "rectangle 50,80 350,85" \
    graphics/info_panel.png

echo ""
echo "✅ Assets created successfully!"
echo ""
echo "📁 Created files:"
echo "   - logo.png (main logo)"
echo "   - logo_small.png (corner logo)"
echo "   - overlays/breaking_news.png"
echo "   - lower_thirds/lower_third_bg.png"
echo "   - lower_thirds/sample_anchor.png"
echo "   - graphics/weather_bg.png"
echo "   - graphics/info_panel.png"
echo "   - overlays/ticker_bg.png"
echo "   - overlays/blue_tint.png"
echo "   - intro_bg.png"
echo "   - outro_bg.png"
echo ""
echo "🎨 Ready for professional Persian news broadcasts!"