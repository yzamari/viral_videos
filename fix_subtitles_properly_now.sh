#!/bin/bash

echo "🎬 PROPER Subtitle Fix - Bottom Position & Correct Size"
echo "======================================================"

# Test on Aphrodite first
EPISODE="greek_aphrodite_ep8"
BASE_DIR="/Users/yahavzamari/viralAi/outputs/$EPISODE"
AUDIO_ONLY="$BASE_DIR/final_output/final_video_${EPISODE}__audio_only.mp4"
SUBTITLE_FILE="$BASE_DIR/subtitles/subtitles.srt"
OUTPUT="$BASE_DIR/final_output/final_video_${EPISODE}__final.mp4"
BACKUP="$BASE_DIR/final_output/final_video_${EPISODE}__final.mp4.aphrodite_backup"

# Backup current file
cp "$OUTPUT" "$BACKUP"

echo "🔍 Testing different subtitle approaches on Aphrodite..."

# First, let's check the overlay_only file size
OVERLAY_SIZE=$(ls -lh "$BASE_DIR/final_output/final_video_${EPISODE}__overlays_only.mp4" | awk '{print $5}')
echo "📊 Overlay file size: $OVERLAY_SIZE"

# Try different subtitle positioning methods
echo ""
echo "Method 1: Using proper ASS alignment codes..."

# Create temporary ASS file with explicit positioning
cat > /tmp/temp_subtitles.ass << 'EOF'
[Script Info]
Title: Subtitles
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,38,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,3,2,0,2,10,10,200,1

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

with open('/tmp/temp_subtitles.ass', 'a') as f:
    for match in matches:
        num, start, end, text = match
        # Convert time format
        start = start.replace(',', '.')
        end = end.replace(',', '.')
        # Clean text
        text = text.replace('\n', '\\\\N').strip()
        f.write(f'Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n')
"

echo "  🎬 Applying ASS subtitles..."
ffmpeg -y -i "$AUDIO_ONLY" \
    -vf "ass='/tmp/temp_subtitles.ass'" \
    -c:a copy \
    -c:v libx264 -preset fast -crf 18 \
    "${OUTPUT}.method1.mp4" 2>/dev/null

echo ""
echo "Method 2: Using drawtext filter directly..."
# This gives us more control over positioning

# For portrait video 1080x1920
FONT_SIZE=38
Y_POS=$((1920 - 250))  # 250px from bottom

# Extract first subtitle for testing
FIRST_SUB=$(head -n 4 "$SUBTITLE_FILE" | tail -n 1)
echo "  Test subtitle: $FIRST_SUB"

ffmpeg -y -i "$AUDIO_ONLY" \
    -vf "drawtext=text='Test Subtitle':fontfile=/System/Library/Fonts/Helvetica.ttc:fontsize=$FONT_SIZE:fontcolor=white:borderw=2:bordercolor=black:x=(w-text_w)/2:y=$Y_POS" \
    -t 10 \
    -c:a copy \
    -c:v libx264 -preset fast -crf 18 \
    "${OUTPUT}.method2_test.mp4" 2>/dev/null

echo ""
echo "Method 3: Using overlay_only as base..."
# Since overlay_only is 96MB and has better quality

OVERLAY_ONLY="$BASE_DIR/final_output/final_video_${EPISODE}__overlays_only.mp4"

if [ -f "$OVERLAY_ONLY" ]; then
    echo "  🎬 Adding subtitles to overlay version..."
    ffmpeg -y -i "$OVERLAY_ONLY" \
        -vf "subtitles='${SUBTITLE_FILE}':force_style='Alignment=2,MarginV=250,Fontsize=36,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,BorderStyle=3,Outline=2,Bold=1'" \
        -c:a copy \
        -c:v libx264 -preset medium -crf 20 \
        "${OUTPUT}.method3.mp4" 2>/dev/null
fi

echo ""
echo "📊 Results:"
ls -lh "${OUTPUT}"*.mp4 | grep -E "method|aphrodite_ep8__final\.mp4"

echo ""
echo "Please check which method works best, then we'll apply to all videos."