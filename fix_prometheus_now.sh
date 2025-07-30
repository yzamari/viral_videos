#!/bin/bash

echo "🔧 Fixing Prometheus Episode 7..."

cd /Users/yahavzamari/viralAi/outputs/greek_prometheus_ep7

# Use audio_only version (has good AAC audio)
AUDIO_ONLY="final_output/final_video_greek_prometheus_ep7__audio_only.mp4"
SUBTITLE_FILE="subtitles/subtitles.srt"
OUTPUT="final_output/final_video_greek_prometheus_ep7__final.mp4"

# Calculate font size: 2.8% of 1920 (height) = 53px
FONT_SIZE=53

echo "📝 Applying subtitles with ${FONT_SIZE}px font..."

# Apply subtitles directly
ffmpeg -y -i "$AUDIO_ONLY" \
    -vf "subtitles='${SUBTITLE_FILE}':force_style='Alignment=2,MarginV=120,Fontsize=${FONT_SIZE},PrimaryColour=&HFFFFFF,OutlineColour=&H000000,BorderStyle=3,Outline=2,Bold=1,Spacing=0.5'" \
    -c:a copy \
    -c:v libx264 -preset medium -crf 23 \
    "$OUTPUT"

echo "✅ Done!"