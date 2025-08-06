#!/bin/bash

# Dark Humor News Command
# Creates a satirical news video with dark humor styling

echo "🎭 Creating Dark Humor News Video..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 main.py news aggregate-enhanced \
    ynet rotter cnn \
    --platform tiktok \
    --duration 50 \
    --style "dark humor satirical apocalyptic" \
    --tone "funny irreverent sarcastic cynical" \
    --channel-name "DOOM & GLOOM NEWS" \
    --max-stories 5 \
    --overlay-style modern \
    --output-dir outputs/dark_humor_news

echo ""
echo "✅ Dark humor news video created!"
echo "📂 Check outputs/dark_humor_news/ for the video"