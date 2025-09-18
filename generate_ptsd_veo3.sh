#!/bin/bash

# PTSD Awareness Video Generator - VEO3 Version
# Generates a first-person soldier narrative with Waltz with Bashir animation style
# Uses premium VEO3 video generation (no-cheap mode)

echo "🎬 Starting PTSD Awareness Video Generation with VEO3..."
echo "📝 First-person soldier narrative with PTSD theme"
echo "🎨 Style: Waltz with Bashir animation style"
echo "⏱️  Duration: 20 seconds"
echo "💎 Premium Mode: VEO3 video generation enabled"
echo "⚡ Fast Mode: Discussions OFF for quicker generation"
echo ""

# Activate virtual environment
source .venv/bin/activate

# Run the generation with optimized parameters
python main.py generate \
  --mission "First-person POV: Israeli soldier with PTSD walks through war-torn Gaza streets. Hands shake searching rooms. Explosions echo. Flashbacks blur reality. Healing journey. Animated in Waltz with Bashir style." \
  --duration 20 \
  --no-cheap \
  --platform youtube \
  --category Educational \
  --style "dramatic documentary" \
  --tone "serious introspective" \
  --visual-style "Waltz with Bashir animation style" \
  --session-id ptsd_veo3_waltz_20s \
  --discussions off \
  --mode simple

echo ""
echo "✅ Video generation completed!"
echo "📁 Check outputs/ptsd_veo3_waltz_20s/final_output/ for your video"