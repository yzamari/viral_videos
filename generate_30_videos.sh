#!/bin/bash

# Script to generate 30 diverse videos for testing and demonstration
# Uses cheap mode for efficiency

echo "🎬 Starting batch generation of 30 diverse videos..."
echo "Using cheap mode for all videos to complete quickly"

# Array of diverse missions across different categories
declare -a MISSIONS=(
    # Educational (6 videos)
    "Learn Python programming basics in 5 minutes"
    "Understanding climate change and its impact"
    "The history of artificial intelligence"
    "How to start investing in stocks"
    "Basic cooking techniques for beginners"
    "Understanding cryptocurrency and blockchain"
    
    # Comedy (6 videos)
    "Why cats are secretly plotting world domination"
    "The struggles of working from home"
    "Things only 90s kids will understand"
    "Awkward elevator moments we all experience"
    "Why adulting is harder than expected"
    "The evolution of dad jokes through history"
    
    # Entertainment (6 videos)
    "Top 10 movies you must watch this year"
    "The rise of K-pop culture worldwide"
    "Behind the scenes of viral TikTok trends"
    "Best video games of all time"
    "The evolution of social media platforms"
    "Celebrity fashion fails and wins"
    
    # News (6 videos)
    "Breaking: AI revolutionizes healthcare industry"
    "Tech giants announce new privacy features"
    "Climate summit reaches historic agreement"
    "Space exploration breakthrough announced"
    "New discovery in renewable energy"
    "Global education initiative launched"
    
    # Tech (6 videos)
    "The future of quantum computing"
    "How 5G will change everything"
    "Best productivity apps for 2025"
    "Understanding the metaverse"
    "Cybersecurity tips for everyone"
    "The rise of AI assistants"
)

declare -a CATEGORIES=("Educational" "Educational" "Educational" "Educational" "Educational" "Educational"
                       "Comedy" "Comedy" "Comedy" "Comedy" "Comedy" "Comedy"
                       "Entertainment" "Entertainment" "Entertainment" "Entertainment" "Entertainment" "Entertainment"
                       "News" "News" "News" "News" "News" "News"
                       "Tech" "Tech" "Tech" "Tech" "Tech" "Tech")

declare -a PLATFORMS=("youtube" "tiktok" "instagram" "youtube" "tiktok" "instagram")
declare -a DURATIONS=(15 20 30 10 25 15)

# Generate videos
for i in {0..29}; do
    MISSION="${MISSIONS[$i]}"
    CATEGORY="${CATEGORIES[$i]}"
    PLATFORM="${PLATFORMS[$((i % 6))]}"
    DURATION="${DURATIONS[$((i % 6))]}"
    SESSION_ID="batch_video_$(printf "%02d" $((i+1)))"
    
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "📹 Video $((i+1))/30: $SESSION_ID"
    echo "Mission: $MISSION"
    echo "Category: $CATEGORY | Platform: $PLATFORM | Duration: ${DURATION}s"
    echo "═══════════════════════════════════════════════════════════════"
    
    # Run generation in background to allow parallel processing
    python3 main.py generate \
        --mission "$MISSION" \
        --category "$CATEGORY" \
        --platform "$PLATFORM" \
        --duration "$DURATION" \
        --cheap \
        --cheap-mode full \
        --discussions off \
        --session-id "$SESSION_ID" 2>&1 | tee "logs/${SESSION_ID}.log" &
    
    # Limit parallel jobs to 3 to avoid overwhelming the system
    if [ $((($i + 1) % 3)) -eq 0 ]; then
        echo "⏳ Waiting for current batch to complete..."
        wait
    fi
done

# Wait for all remaining jobs
echo ""
echo "⏳ Waiting for all remaining videos to complete..."
wait

# Count successful outputs
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ Batch generation complete!"
echo ""
echo "📊 Results:"
SUCCESSFUL=$(ls outputs/batch_video_*/final_output/*.mp4 2>/dev/null | wc -l)
echo "Successfully generated: $SUCCESSFUL/30 videos"
echo ""
echo "📁 Videos saved in: outputs/batch_video_*/"
echo "📋 Logs saved in: logs/batch_video_*.log"
echo "═══════════════════════════════════════════════════════════════"