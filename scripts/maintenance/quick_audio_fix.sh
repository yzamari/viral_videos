#!/bin/bash

echo "🎬 Quick Audio Fix for Greek Mythology Episodes"
echo "=============================================="

# Main Greek episodes only
EPISODES=(
    "greek_zeus_ep1"
    "greek_athena_ep2"
    "greek_hercules_ep3"
    "greek_achilles_ep4"
    "greek_odysseus_ep5"
    "greek_medusa_ep6"
    "greek_prometheus_ep7"
    "greek_aphrodite_ep8"
)

for episode in "${EPISODES[@]}"; do
    echo ""
    echo "🔧 Processing $episode..."
    
    AUDIO_ONLY="/Users/yahavzamari/viralAi/outputs/${episode}/final_output/final_video_${episode}__audio_only.mp4"
    FINAL="/Users/yahavzamari/viralAi/outputs/${episode}/final_output/final_video_${episode}__final.mp4"
    SRT="/Users/yahavzamari/viralAi/outputs/${episode}/subtitles/subtitles.srt"
    
    if [ ! -f "$AUDIO_ONLY" ]; then
        echo "  ⚠️  No audio_only file found"
        continue
    fi
    
    if [ ! -f "$FINAL" ]; then
        echo "  ⚠️  No final file found"
        continue
    fi
    
    # Check if already fixed
    if [ -f "${FINAL}.backup" ]; then
        echo "  ✅ Already fixed (backup exists)"
        continue
    fi
    
    # Backup original
    cp "$FINAL" "${FINAL}.backup"
    echo "  💾 Created backup"
    
    if [ -f "$SRT" ]; then
        echo "  📝 Adding subtitles from SRT file..."
        # Use ffmpeg to burn subtitles
        ffmpeg -y -i "$AUDIO_ONLY" \
            -vf "subtitles='$SRT':force_style='Alignment=2,MarginV=120,Fontsize=24,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,BorderStyle=3,Outline=3,Bold=1'" \
            -c:a copy \
            -c:v libx264 -preset medium -crf 23 \
            "$FINAL" 2>/dev/null
    else
        echo "  🎵 Copying audio from audio_only version..."
        # Just copy audio from audio_only
        ffmpeg -y -i "$FINAL" -i "$AUDIO_ONLY" \
            -map 0:v -map 1:a \
            -c:v copy -c:a copy \
            "${FINAL}.temp" 2>/dev/null
        mv "${FINAL}.temp" "$FINAL"
    fi
    
    if [ $? -eq 0 ]; then
        echo "  ✅ Fixed successfully!"
    else
        echo "  ❌ Fix failed"
    fi
done

echo ""
echo "🎉 Audio fix complete!"
echo "Original files backed up as .backup"