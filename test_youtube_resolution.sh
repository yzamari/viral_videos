#!/bin/bash

# Test YouTube video resolution fix

echo "Testing YouTube video resolution fix..."

python main.py generate \
    --topic "Tech tutorial: How to optimize your code for performance" \
    --platform youtube \
    --duration 20 \
    --cheap full \
    --session-id "test_youtube_resolution" \
    --verbose

# Check the resolution of the generated video
echo -e "\nChecking generated video resolution..."
if [ -f "outputs/test_youtube_resolution/final_output/final_video_test_youtube_resolution__final.mp4" ]; then
    ffprobe -v quiet -print_format json -show_streams "outputs/test_youtube_resolution/final_output/final_video_test_youtube_resolution__final.mp4" | jq '.streams[] | select(.codec_type=="video") | {width: .width, height: .height}'
else
    echo "Video file not found!"
fi