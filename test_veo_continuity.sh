#!/bin/bash

# Test VEO generation with visual and content continuity

echo "Testing VEO generation with visual and content continuity (enabled by default)..."

python main.py generate \
    --topic "Beautiful sunrise timelapse over mountain peaks with clouds" \
    --platform youtube \
    --duration 30 \
    --style-template "cinematic landscape" \
    --session-id "test_veo_continuity" \
    --verbose

echo "Test complete. Check outputs/test_veo_continuity for results."