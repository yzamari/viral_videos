#!/bin/bash

echo "🎬 FINAL FIX - Proper Subtitles with Full Quality"
echo "================================================="

# Root cause: We were using audio_only which has low quality video
# Solution: Use overlay_only which has high quality video, then add subtitles

episodes=(
    "greek_zeus_ep1:1920:1080"         # YouTube landscape
    "greek_athena_ep2:1920:1080"       # YouTube landscape
    "greek_hercules_ep3:1920:1080"     # YouTube landscape
    "greek_achilles_ep4:1920:1080"     # YouTube landscape
    "greek_odysseus_ep5:1920:1080"     # YouTube landscape
    "greek_medusa_ep6:1080:1920"       # Instagram portrait
    "greek_prometheus_ep7:1080:1920"   # Instagram portrait
    "greek_aphrodite_ep8:1080:1920"    # Instagram portrait
)

for episode_info in "${episodes[@]}"; do
    IFS=':' read -r episode width height <<< "$episode_info"
    
    echo ""
    echo "🔧 Processing $episode (${width}x${height})..."
    
    # Paths
    BASE_DIR="/Users/yahavzamari/viralAi/outputs/$episode"
    OVERLAY_VIDEO="$BASE_DIR/final_output/final_video_${episode}__overlays_only.mp4"
    AUDIO_ONLY="$BASE_DIR/final_output/final_video_${episode}__audio_only.mp4"
    SUBTITLE_FILE="$BASE_DIR/subtitles/subtitles.srt"
    OUTPUT="$BASE_DIR/final_output/final_video_${episode}__final.mp4"
    TEMP="$BASE_DIR/final_output/final_video_${episode}__temp.mp4"
    
    # Check files
    if [ ! -f "$OVERLAY_VIDEO" ]; then
        echo "  ⚠️  No overlay video found - using audio_only as fallback"
        OVERLAY_VIDEO="$AUDIO_ONLY"
    fi
    
    if [ ! -f "$SUBTITLE_FILE" ]; then
        echo "  ⚠️  No subtitle file found"
        continue
    fi
    
    # Get original sizes for comparison
    OVERLAY_SIZE=$(ls -lh "$OVERLAY_VIDEO" 2>/dev/null | awk '{print $5}')
    echo "  📊 Source video size: $OVERLAY_SIZE"
    
    # Calculate subtitle parameters
    if [ "$height" -gt "$width" ]; then
        # Portrait video
        FONT_SIZE=36  # Good size for portrait
        MARGIN_V=250  # Distance from bottom
        echo "  📐 Portrait: ${FONT_SIZE}px font, ${MARGIN_V}px from bottom"
    else
        # Landscape video  
        FONT_SIZE=20  # Smaller for landscape
        MARGIN_V=100  # Distance from bottom
        echo "  📐 Landscape: ${FONT_SIZE}px font, ${MARGIN_V}px from bottom"
    fi
    
    # Apply subtitles using ASS format for better control
    echo "  🎬 Creating properly positioned subtitles..."
    
    # Create ASS header with correct positioning
    cat > /tmp/${episode}_subtitles.ass << EOF
[Script Info]
Title: Subtitles
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,${FONT_SIZE},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,3,2,0,2,10,10,${MARGIN_V},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
EOF

    # Convert SRT to ASS events
    python3 -c "
import re

with open('$SUBTITLE_FILE', 'r') as f:
    content = f.read()

# Parse SRT
pattern = r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.+?)(?=\n\n|\Z)'
matches = re.findall(pattern, content, re.DOTALL)

with open('/tmp/${episode}_subtitles.ass', 'a') as f:
    for match in matches:
        num, start, end, text = match
        # Convert time format
        start = start.replace(',', '.')
        end = end.replace(',', '.')
        # Clean text and preserve line breaks
        text = text.replace('\n', '\\\\N').strip()
        f.write(f'Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n')
"

    # Apply subtitles with high quality settings
    echo "  🎥 Encoding with subtitles..."
    ffmpeg -y -i "$OVERLAY_VIDEO" \
        -vf "ass='/tmp/${episode}_subtitles.ass'" \
        -c:a aac -b:a 128k \
        -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
        -movflags +faststart \
        "$TEMP" 2>/dev/null
    
    if [ $? -eq 0 ] && [ -f "$TEMP" ]; then
        # Check output size
        OUTPUT_SIZE=$(ls -lh "$TEMP" | awk '{print $5}')
        mv "$TEMP" "$OUTPUT"
        echo "  ✅ Success! Output size: $OUTPUT_SIZE"
        echo "  📝 Subtitles: ${FONT_SIZE}px at bottom (${MARGIN_V}px margin)"
    else
        echo "  ❌ Encoding failed"
        rm -f "$TEMP"
    fi
    
    # Cleanup
    rm -f /tmp/${episode}_subtitles.ass
done

echo ""
echo "🎉 All videos processed!"
echo ""
echo "📊 Final verification:"
ls -lh /Users/yahavzamari/viralAi/outputs/*/final_output/*__final.mp4 | grep -v backup | grep -v original