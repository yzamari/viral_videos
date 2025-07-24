#!/bin/bash

# Racheli's Goodbye Video from NeuReality
# AI-generated creative farewell videos for multiple platforms

echo "🎬 Generating Racheli's Goodbye Videos for All Platforms"
echo "========================================================"
echo ""

# YouTube Version (40 seconds)
echo "📺 YOUTUBE VERSION - Horizontal 16:9"
echo "------------------------------------"
python main.py generate \
  --mission "Create engaging, funny, humorous first-person goodbye video from Racheli who's leaving NeuReality, AI chips company" \
  --platform youtube \
  --duration 40 \
  --style viral \
  --tone humorous \
  --visual-style disney \
  --character "Racheli - tech worker leaving company" \
  --scene "modern tech office environment" \
  --no-cheap \
  --mode enhanced \
  --session-id "racheli_goodbye_youtube"

if [ $? -eq 0 ]; then
    echo "✅ YouTube version complete!"
    sleep 5
    
    # Instagram Version (30 seconds)
    echo ""
    echo "📷 INSTAGRAM VERSION - Square 1:1"
    echo "---------------------------------"
    python main.py generate \
      --mission "Create engaging, funny, humorous first-person goodbye video from Racheli who's leaving NeuReality, AI chips company" \
      --platform instagram \
      --duration 30 \
      --style viral \
      --tone humorous \
      --visual-style disney \
      --character "Racheli - tech worker leaving company" \
      --scene "modern tech office environment" \
          --continuous \
      --no-cheap \
      --mode enhanced \
      --session-id "racheli_goodbye_instagram"
    
    if [ $? -eq 0 ]; then
        echo "✅ Instagram version complete!"
        sleep 5
        
        # TikTok Version (15 seconds)
        echo ""
        echo "🎵 TIKTOK VERSION - Vertical 9:16"
        echo "---------------------------------"
        python main.py generate \
          --mission "Create engaging, funny, humorous first-person goodbye video from Racheli who's leaving NeuReality, AI chips company" \
          --platform tiktok \
          --duration 15 \
          --style viral \
          --tone humorous \
          --visual-style disney \
          --character "Racheli - tech worker leaving company" \
          --scene "modern tech office environment" \
                  --continuous \
          --no-cheap \
          --mode enhanced \
          --session-id "racheli_goodbye_tiktok"
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "🎉 ALL PLATFORMS COMPLETE!"
            echo ""
            echo "📁 Your videos are ready:"
            echo "   YouTube (40s, 16:9): outputs/racheli_goodbye_youtube/"
            echo "   Instagram (30s, 1:1): outputs/racheli_goodbye_instagram/"
            echo "   TikTok (15s, 9:16): outputs/racheli_goodbye_tiktok/"
            echo ""
            echo "🎯 AI CREATIVE DECISIONS:"
            echo "   ✨ Simple mission → AI agents created detailed narrative"
            echo "   🎤 Single voice consistency across all platforms"
            echo "   🎨 Disney visual style adapted for each platform"
            echo "   😂 Humorous tone maintained with platform-specific pacing"
            echo ""
        else
            echo "❌ TikTok version failed!"
            exit 1
        fi
    else
        echo "❌ Instagram version failed!"
        exit 1
    fi
else
    echo "❌ YouTube version failed!"
    exit 1
fi

echo "🚀 Ready for multi-platform distribution!"