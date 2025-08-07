#!/bin/bash

# News Aggregator Example Scripts
# Run various news aggregation scenarios

echo "🎬 News Aggregator Examples"
echo "=========================="

# Example 1: Basic scraping with Playwright
echo "1. Basic Web Scraping (Hebrew sources)..."
python3 main.py news aggregate-enhanced rotter ynet \
  --languages he \
  --duration 30 \
  --platform youtube \
  --max-stories 5 \
  --output-dir outputs/example1_hebrew

# Example 2: CSV import with Instagram format
echo "2. CSV Import for Instagram..."
python3 main.py news aggregate-enhanced test_demo \
  --csv sample_news.csv \
  --duration 40 \
  --platform instagram \
  --style "viral breaking news" \
  --tone "exciting and urgent" \
  --max-stories 10 \
  --output-dir outputs/example2_instagram

# Example 3: Multi-language output
echo "3. Multi-language News..."
python3 main.py news aggregate-enhanced cnn bbc \
  --languages en --languages he --languages es \
  --duration 60 \
  --platform youtube \
  --max-stories 8 \
  --output-dir outputs/example3_multilang

# Example 4: Dark humor news style
echo "4. Sarcastic News Style..."
python3 main.py news aggregate-enhanced test_demo \
  --style "modern and dynamic" \
  --tone "sarcastic dark humor" \
  --duration 45 \
  --platform tiktok \
  --channel-name "DARK NEWS" \
  --output-dir outputs/example4_sarcastic

# Example 5: Professional broadcast
echo "5. Professional News Broadcast..."
python3 main.py news aggregate-enhanced reuters guardian nytimes \
  --style "professional news broadcast" \
  --tone "authoritative and informative" \
  --duration 90 \
  --platform youtube \
  --channel-name "WORLD NEWS NETWORK" \
  --overlay-style modern \
  --discussion-log \
  --output-dir outputs/example5_broadcast

echo "✅ All examples completed!"
echo "Check outputs/ directory for generated videos and CSVs"