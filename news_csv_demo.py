#!/usr/bin/env python3
"""
News Aggregator CSV Demo
Shows how the CSV input works for news aggregation
"""

import csv
import os

print("""
📄 NEWS AGGREGATOR CSV INPUT SYSTEM
===================================

The news aggregator supports multiple CSV formats:
""")

# 1. Articles CSV
print("\n1️⃣ ARTICLES CSV FORMAT:")
print("-" * 50)
articles_csv = """title,url,summary,content,image_url,video_url,author,date,category,language
"Breaking: Major Climate Agreement Reached","https://cnn.com/climate-deal","World leaders agree on climate action","Full article content here...","https://cnn.com/climate.jpg","https://cnn.com/climate.mp4","John Smith","2024-01-15","environment","en"
"חדשות: גילוי ארכיאולוגי בירושלים","https://ynet.co.il/archaeology","ממצא נדיר מתקופת בית שני","תוכן הכתבה המלא...","https://ynet.co.il/arch.jpg","","יוסי כהן","2024-01-15","culture","he"
"Tech Giant Unveils New AI System","https://techcrunch.com/ai-news","Revolutionary AI breakthrough","Article content...","https://tech.jpg","https://tech.mp4","Jane Doe","2024-01-15","tech","en"
"""

with open("sample_articles.csv", "w") as f:
    f.write(articles_csv)
print("✅ Created: sample_articles.csv")
print("Fields: title, url, summary, content, image_url, video_url, author, date, category, language")

# 2. Media CSV
print("\n\n2️⃣ MEDIA CSV FORMAT:")
print("-" * 50)
media_csv = """media_url,type,title,description,duration,tags,source
"https://cnn.com/climate_speech.mp4","video","UN Climate Summit Speech","World leader addresses climate crisis",120,"climate,politics,un","CNN"
"https://ynet.co.il/jerusalem_dig.jpg","image","Jerusalem Archaeological Site","Ancient artifacts discovered",,"archaeology,history,israel","Ynet"
"https://reddit.com/sportsfail.mp4","video","Epic Sports Fail Compilation","Funny sports moments",30,"sports,funny,fails","Reddit"
"https://bbc.com/tech_demo.mp4","video","AI Technology Demo","New AI system demonstration",90,"tech,ai,innovation","BBC"
"""

with open("sample_media.csv", "w") as f:
    f.write(media_csv)
print("✅ Created: sample_media.csv")
print("Fields: media_url, type, title, description, duration, tags, source")

# 3. Sources CSV
print("\n\n3️⃣ SOURCES CSV FORMAT:")
print("-" * 50)
sources_csv = """source_url,source_name,category,language,scrape_config
"https://www.cnn.com","CNN","general","en","full"
"https://www.ynet.co.il","Ynet","general","he","full"
"https://www.bbc.com/sport","BBC Sport","sports","en","headlines"
"https://reddit.com/r/worldnews","Reddit World News","general","en","top_posts"
"https://t.me/breaking_news","Telegram News","general","multi","recent"
"""

with open("sample_sources.csv", "w") as f:
    f.write(sources_csv)
print("✅ Created: sample_sources.csv")
print("Fields: source_url, source_name, category, language, scrape_config")

# 4. Events CSV
print("\n\n4️⃣ EVENTS CSV FORMAT (for sports/conferences):")
print("-" * 50)
events_csv = """event_name,date,location,description,media_urls,highlights,category
"World Cup Final 2024","2024-07-15","Paris Stadium","Epic final match","goal1.mp4,goal2.mp4,celebration.jpg","Amazing goals and dramatic finish","sports"
"Tech Conference 2024","2024-06-20","Silicon Valley","Major tech announcements","keynote.mp4,demo1.mp4,demo2.mp4","New AI and robotics demos","tech"
"Climate Summit","2024-05-10","New York","Global climate agreement","speech1.mp4,signing.jpg,protests.mp4","Historic agreement signed","environment"
"""

with open("sample_events.csv", "w") as f:
    f.write(events_csv)
print("✅ Created: sample_events.csv")
print("Fields: event_name, date, location, description, media_urls, highlights, category")

print("\n" + "=" * 60)
print("\n🎬 HOW TO USE THESE CSV FILES:")
print("=" * 60)

print("""
1. Edit the CSV files with your actual content/URLs
2. Run the news aggregator with CSV input:

   # Create news from articles CSV:
   python main.py news csv sample_articles.csv --type general --duration 5
   
   # Create sports video from media CSV:
   python main.py news csv sample_media.csv --type sports --duration 3
   
   # Create news from multiple sources:
   python main.py news csv sample_sources.csv --type general
   
   # Create event summary video:
   python main.py news csv sample_events.csv --type sports --style dramatic

3. The system will:
   ✓ Parse the CSV file
   ✓ Download media from URLs
   ✓ Use AI agents for editorial decisions
   ✓ Create video using SCRAPED MEDIA ONLY (no VEO)
   ✓ Output professional news edition video

📸 IMPORTANT: All media URLs in CSV should be actual media files
             The system uses these real files, NOT AI generation!
""")

print("\n✅ All sample CSV files created in current directory!")
print("📝 Edit them with your content and run the commands above.")