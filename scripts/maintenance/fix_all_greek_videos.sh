#!/bin/bash

echo "🎬 Fixing All Greek Mythology Videos"
echo "===================================="

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
    BACKUP="$BASE_DIR/final_output/final_video_${episode}__final.mp4.backup"
    
    # Check if files exist
    if [ ! -f "$AUDIO_ONLY" ]; then
        echo "  ⚠️  No audio_only file found"
        continue
    fi
    
    if [ ! -f "$SUBTITLE_FILE" ]; then
        echo "  ⚠️  No subtitle file found"
        continue
    fi
    
    # Backup if not already done
    if [ ! -f "$BACKUP" ]; then
        cp "$OUTPUT" "$BACKUP" 2>/dev/null
        echo "  💾 Created backup"
    fi
    
    # Calculate font size based on orientation
    if [ "$height" -gt "$width" ]; then
        # Portrait: 2.8% of height
        FONT_SIZE=$((height * 28 / 1000))
        echo "  📐 Portrait mode: ${FONT_SIZE}px font"
    else
        # Landscape: 2.5% of height  
        FONT_SIZE=$((height * 25 / 1000))
        echo "  📐 Landscape mode: ${FONT_SIZE}px font"
    fi
    
    # Apply subtitles
    echo "  🎬 Applying subtitles..."
    ffmpeg -y -i "$AUDIO_ONLY" \
        -vf "subtitles='${SUBTITLE_FILE}':force_style='Alignment=2,MarginV=120,Fontsize=${FONT_SIZE},PrimaryColour=&HFFFFFF,OutlineColour=&H000000,BorderStyle=3,Outline=2,Bold=1,Spacing=0.5'" \
        -c:a copy \
        -c:v libx264 -preset medium -crf 23 \
        "$OUTPUT" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "  ✅ Fixed successfully!"
    else
        echo "  ❌ Fix failed"
    fi
done

echo ""
echo "🎉 All videos processed!"
echo ""
echo "Summary of fixes:"
echo "• Subtitle font: 2.5% (landscape) or 2.8% (portrait) of video height"
echo "• Audio: Preserved AAC codec from audio_only versions"
echo "• Backups: Created as .backup files"