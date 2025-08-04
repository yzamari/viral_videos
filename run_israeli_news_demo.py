#!/usr/bin/env python3
"""
Israeli News Demo - Shows how to create news video from CSV
"""

import csv
import os

print("""
🇮🇱 ISRAELI NEWS VIDEO GENERATOR
================================

This demo shows how to create a Hebrew news edition
from Israeli news sources using CSV input.
""")

# Display the CSV content
print("\n📋 Israeli News Articles CSV:")
print("=" * 60)

with open("israeli_news_articles.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader, 1):
        print(f"\n{i}. {row['title']}")
        print(f"   מקור: {row['url']}")
        print(f"   קטגוריה: {row['category']}")
        if row['video_url']:
            print(f"   🎥 וידאו: {row['video_url']}")
        if row['image_url']:
            print(f"   📸 תמונה: {row['image_url']}")

print("\n" + "=" * 60)

print("""
🎬 TO CREATE ISRAELI NEWS VIDEO:
================================

Run one of these commands:

1. General Hebrew news (5 minutes):
   python main.py news csv israeli_news_articles.csv --language he --duration 5

2. Tech news only (3 minutes):
   python main.py news csv israeli_news_articles.csv --type tech --language he --duration 3

3. Professional style news edition:
   python main.py news csv israeli_news_articles.csv --style professional --language he

4. From news sources list:
   python main.py news csv israeli_news_sources.csv --language he

📸 The system will:
   ✓ Parse the Hebrew CSV file
   ✓ Download actual images/videos from Israeli news sites
   ✓ Use AI agents to create editorial flow in Hebrew
   ✓ Create professional Hebrew news video
   ✓ NO VEO generation - only real Israeli media

🎯 OUTPUT:
   The final video will be a professional Hebrew news edition
   similar to Channel 12 or Ynet video style, using actual
   media from the Israeli news sources.
""")

# Show CSV stats
print("\n📊 CSV Statistics:")
print(f"   - Total articles: 8")
print(f"   - With video: 4")
print(f"   - With images: 8")
print(f"   - Categories: tech, health, sports, culture, finance, general")
print(f"   - Language: Hebrew (he)")

print("\n✅ Ready to create Israeli news video!")
print("📝 Edit israeli_news_articles.csv to add more articles")
print("🎬 Run the commands above to generate video")