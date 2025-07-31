#!/bin/bash

# Run Iranian news episode 4 with premium mode (no cheap)

echo "🎬 Generating Iranian news episode 4 with PREMIUM MODE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 main.py generate \
    --mission "Family Guy news breakdown. Maryam (makeup smeared) announces: 'Celebrating 1000 days without Instagram! Citizens report strange symptoms: actual conversations.' Show Meg-style teenager: 'I had to... talk to my parents. THE HORROR!' Cleveland-style IT minister: 'Internet is overrated. Try smoke signals!' Cutaway: Pigeons carrying USB drives. News ticker: 'BREAKING: Youth Discover Books Exist'. Lower third: 'COMING UP: How to Like Things Without a Button'. Studio lights flicker. Maryam drinks from flask." \
    --character "Desert Maryam - THIRSTIONAL anchor with hijab now tumble-weed style, raccoon eyes from dehydration, clutching flask of sand, smile like cracked desert floor, papers turning to dust, THIRSTIONAL logo barely visible through haze" \
    --platform youtube \
    --duration 30 \
    --visual-style "family guy animation extreme satire" \
    --tone "darkly humorous absurdist hilarious" \
    --style "satirical news parody" \
    --theme preset_news_edition \
    --no-cheap \
    --voice "en-US-Neural2-F" \
    --session-id "iran_news_premium_ep4" \
    --languages en-US \
    --visual-continuity \
    --content-continuity \
    --mode enhanced \
    --scene "Family Guy style animated news studio, IRAN THIRSTIONAL logo with water drops, professional news desk with empty water cooler, overlay graphics showing hydration alerts"

echo ""
echo "✅ Episode 4 premium mode generation complete!"
echo "📁 Output folder: outputs/iran_news_premium_ep4/"