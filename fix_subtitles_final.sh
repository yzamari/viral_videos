#!/bin/bash

echo "🎬 Final Subtitle Fix - Smaller Font & Bottom Position"
echo "====================================================="

# Episodes to fix
episodes=(
    "greek_zeus_ep1:1080:1920"         # YouTube landscape
    "greek_athena_ep2:1080:1920"       # YouTube landscape
    "greek_hercules_ep3:1080:1920"     # YouTube landscape
    "greek_achilles_ep4:1080:1920"     # YouTube landscape
    "greek_odysseus_ep5:1080:1920"     # YouTube landscape
    "greek_medusa_ep6:1920:1080"       # Instagram portrait
    "greek_prometheus_ep7:1920:1080"   # Instagram portrait
    "greek_aphrodite_ep8:1920:1080"    # Instagram portrait
)

for episode_info in "${episodes[@]}"; do
    IFS=':' read -r episode height width <<< "$episode_info"
    
    echo ""
    echo "🔧 Processing $episode (${width}x${height})..."
    
    # Paths
    BASE_DIR="/Users/yahavzamari/viralAi/outputs/$episode"
    AUDIO_ONLY="$BASE_DIR/final_output/final_video_${episode}__audio_only.mp4"
    SUBTITLE_FILE="$BASE_DIR/subtitles/subtitles.srt"
    OUTPUT="$BASE_DIR/final_output/final_video_${episode}__final.mp4"
    TEMP="$BASE_DIR/final_output/final_video_${episode}__temp.mp4"
    
    # Check if files exist
    if [ ! -f "$AUDIO_ONLY" ]; then
        echo "  ⚠️  No audio_only file found"
        continue
    fi
    
    if [ ! -f "$SUBTITLE_FILE" ]; then
        echo "  ⚠️  No subtitle file found"
        continue
    fi
    
    # Calculate font size - SMALLER!
    if [ "$height" -gt "$width" ]; then
        # Portrait: 2% of height (was 2.8%)
        FONT_SIZE=$((height * 20 / 1000))
        MARGIN_V=200  # More margin from bottom for portrait
        echo "  📐 Portrait mode: ${FONT_SIZE}px font"
    else
        # Landscape: 1.8% of height (was 2.5%)
        FONT_SIZE=$((height * 18 / 1000))
        MARGIN_V=80   # Standard margin for landscape
        echo "  📐 Landscape mode: ${FONT_SIZE}px font"
    fi
    
    # Apply subtitles with correct positioning
    echo "  🎬 Applying subtitles at BOTTOM..."
    
    # Use Alignment=2 for bottom center
    # MarginV controls distance from bottom
    ffmpeg -y -i "$AUDIO_ONLY" \
        -vf "subtitles='${SUBTITLE_FILE}':force_style='Alignment=2,MarginV=${MARGIN_V},Fontsize=${FONT_SIZE},PrimaryColour=&HFFFFFF,OutlineColour=&H000000,BorderStyle=3,Outline=2,Bold=1,Spacing=0.3,FontName=Arial'" \
        -c:a copy \
        -c:v libx264 -preset medium -crf 23 -pix_fmt yuv420p \
        "$TEMP" 2>/dev/null
    
    if [ $? -eq 0 ] && [ -f "$TEMP" ]; then
        mv "$TEMP" "$OUTPUT"
        echo "  ✅ Fixed successfully!"
        echo "  📝 Font: ${FONT_SIZE}px at bottom (margin: ${MARGIN_V}px)"
    else
        echo "  ❌ Fix failed"
        rm -f "$TEMP"
    fi
done

echo ""
echo "🎉 All videos processed!"
echo ""
echo "Summary of fixes:"
echo "• Subtitle font: 1.8% (landscape) or 2% (portrait) of video height"
echo "• Position: Bottom center with proper margins"
echo "• Style: White text with black outline for readability"