#!/bin/bash
# Run only Dragon Episode 3 with fixes

# Configuration
CHARACTER="Young clever dragon professor with glasses, purple scales, wearing a lab coat, Family Guy animation style, holding advanced calculus textbook, confident and witty expression"
SCENE="University lecture hall with complex equations on multiple blackboards, Family Guy style, mathematical symbols and formulas floating around, epsilon-delta proofs visualized, engineering diagrams in background"
VOICE="en-US-Wavenet-D"

# Episode 3 details
TITLE="To Infinity and Beyond!"
MISSION="[VISUAL: Show 'EPISODE 3: To Infinity and Beyond!!' as HUGE ANIMATED TITLE CARD for 3 seconds with epic effects] Family Guy space comedy! Dragon astronaut explores INFINITY SPACE STATION where different sequences live! Divergent sequences are friendly rockets zooming to infinity, convergent ones land safely. Dragon demonstrates ratio test as space multiplication game, root test as cosmic plant growth experiment, and comparison test as rocket races. Include funny zero-gravity math demonstrations, dragon's space jokes, and visual explanations of convergence tests. Make infinity concepts approachable and fun!"

# Enhanced mode for better memory management (not professional mode)
MODE="enhanced"

echo "🎬 Generating Dragon Episode 3: $TITLE"
echo "📚 Using enhanced mode to avoid memory issues"

# Generate with enhanced mode
python3 main.py generate \
    --mission "$MISSION" \
    --character "$CHARACTER" \
    --scene "$SCENE" \
    --platform instagram \
    --duration 40 \
    --visual-style "family guy animation" \
    --category Educational \
    --tone funny \
    --style educational \
    --voice "$VOICE" \
    --session-id "dragon_ep3_fixed_$(date +%Y%m%d_%H%M%S)" \
    --languages en-US \
    --no-cheap \
    --auto-post \
    --visual-continuity \
    --content-continuity \
    --theme preset_university \
    --mode "$MODE"

echo "✅ Episode 3 generation complete!"