#!/bin/bash

echo "🎬 Batch Video Fix Script"
echo "========================"

# Process each episode individually
episodes=(
    "greek_zeus_ep1"
    "greek_athena_ep2"
    "greek_hercules_ep3"
    "greek_achilles_ep4"
    "greek_odysseus_ep5"
    "greek_medusa_ep6"
    "greek_prometheus_ep7"
    "greek_aphrodite_ep8"
)

for episode in "${episodes[@]}"; do
    echo ""
    echo "Processing $episode..."
    python3 fix_single_video.py "$episode"
    
    # Small pause between episodes
    sleep 2
done

echo ""
echo "🎉 All episodes processed!"
echo ""
echo "To check results:"
echo "ls -la outputs/*/final_output/*__final.mp4"