#!/usr/bin/env python3
"""
Sports Video Demo - Creates sports video from scraped media
"""

import asyncio
import csv
import os
from datetime import datetime

# Create sample CSV with sports content
csv_content = """title,url,media_url,type,tags,duration
"Amazing Soccer Goal Fail","https://reddit.com/r/sportsfails/1","https://v.redd.it/soccer_fail.mp4","video","funny,fails,soccer",15
"Basketball Blooper Compilation","https://reddit.com/r/funny/2","https://v.redd.it/basketball_fail.mp4","video","funny,fails,basketball",20
"Hilarious Golf Swing","https://reddit.com/r/sports/3","https://i.redd.it/golf_fail.jpg","image","funny,golf",5
"Football Fumble Comedy","https://reddit.com/r/nfl/4","https://v.redd.it/football_fail.mp4","video","funny,fails,football",18
"Tennis Racket Mishap","https://reddit.com/r/tennis/5","https://i.imgur.com/tennis_fail.gif","video","funny,tennis",8
"""

# Write sample CSV
csv_file = "sports_content.csv"
with open(csv_file, "w") as f:
    f.write(csv_content)

print(f"✅ Created sample CSV: {csv_file}")
print("\n📋 Sample content:")
print("=" * 60)

# Read and display CSV
with open(csv_file, "r") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader, 1):
        print(f"{i}. {row['title']}")
        print(f"   Media: {row['media_url']} ({row['type']})")
        print(f"   Tags: {row['tags']}")
        print()

print("=" * 60)
print("\n🎬 To create sports video from this CSV:")
print(f"   python main.py news csv {csv_file} --type sports --duration 30")
print("\n📸 This will:")
print("   1. Parse the CSV file")
print("   2. Download actual media files from URLs")
print("   3. Create video using FFmpeg (NO VEO)")
print("   4. Output: sports_video_[timestamp].mp4")