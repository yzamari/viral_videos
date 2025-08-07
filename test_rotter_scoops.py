#!/usr/bin/env python3
"""
Test Rotter.net scoops with fallback content
"""

import asyncio
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_rotter_scoops():
    """Test with Rotter scoops using fallback content"""
    
    print("🔍 Testing Rotter.net Scoops Aggregation")
    print("=" * 70)
    
    # Import the aggregator
    from src.news_aggregator.enhanced_aggregator import EnhancedNewsAggregator
    from src.utils.session_manager import SessionManager
    from src.ai.manager import AIServiceManager
    
    # Initialize components
    session_manager = SessionManager()
    ai_manager = AIServiceManager()
    
    # Create aggregator
    aggregator = EnhancedNewsAggregator(
        session_manager=session_manager,
        ai_manager=ai_manager
    )
    
    # Create fallback content for Rotter scoops
    fallback_scoops = [
        {
            "title": "דיווח: פיצוץ בצפון תל אביב - כוחות חילוץ במקום",
            "content": "התקבל דיווח על פיצוץ חזק שנשמע באזור צפון תל אביב. כוחות חילוץ והצלה הוזעקו למקום. משטרת ישראל סגרה את האזור ומבקשת מהציבור להימנע מהגעה.",
            "url": "https://rotter.net/forum/scoops1/852741.shtml",
            "category": "חדשות",
            "embedded_links": [
                "https://www.ynet.co.il/news/article/B1234567",
                "https://www.mako.co.il/news-military/security/Article-abc123.htm"
            ]
        },
        {
            "title": "בלעדי: שר האוצר שוקל להתפטר - דיונים סוערים בממשלה",
            "content": "על פי מקורות בכירים, שר האוצר שוקל להגיש את התפטרותו על רקע חילוקי דעות עמוקים בנושא התקציב. ישיבת הממשלה הסתיימה ללא הסכמות.",
            "url": "https://rotter.net/forum/scoops1/852742.shtml",
            "category": "פוליטיקה",
            "embedded_links": [
                "https://www.calcalist.co.il/local_news/article/H1234567",
                "https://www.globes.co.il/news/article.aspx?did=1001234567"
            ]
        },
        {
            "title": "מכבי תל אביב מנצחת את ריאל מדריד בהארכה דרמטית",
            "content": "במשחק מטורף בבלגרד, מכבי תל אביב ניצחה את ריאל מדריד 92-91 לאחר הארכה. ווילביקין קלע את הסל המנצח 2 שניות לפני הסיום.",
            "url": "https://rotter.net/forum/scoops1/852743.shtml",
            "category": "ספורט",
            "embedded_links": [
                "https://www.sport5.co.il/articles.aspx?FolderID=403&docID=123456",
                "https://www.one.co.il/Article/123456.html"
            ]
        },
        {
            "title": "גילוי ארכיאולוגי מרעיש: מקדש בן 3000 שנה נחשף בירושלים",
            "content": "ארכיאולוגים מרשות העתיקות חשפו מקדש עתיק מתקופת בית ראשון בעיר דוד. בין הממצאים: כלי פולחן נדירים וכתובת עברית קדומה.",
            "url": "https://rotter.net/forum/scoops1/852744.shtml",
            "category": "תרבות",
            "embedded_links": [
                "https://www.haaretz.co.il/archaeology/.premium-1.123456",
                "https://www.timesofisrael.com/ancient-temple-found-jerusalem/"
            ]
        },
        {
            "title": "התרסקות מזל\"ט איראני בשטח ישראל - צה״ל חוקר",
            "content": "מזל״ט איראני מתקדם התרסק הלילה בשטח פתוח בנגב. צה״ל אסף את השברים לבדיקה. לא היו נפגעים.",
            "url": "https://rotter.net/forum/scoops1/852745.shtml",
            "category": "ביטחון",
            "embedded_links": [
                "https://www.inn.co.il/news/123456",
                "https://www.jpost.com/breaking-news/article-123456"
            ]
        }
    ]
    
    print(f"📰 Processing {len(fallback_scoops)} Rotter scoops")
    print()
    
    # Display scoops with embedded links info
    for i, scoop in enumerate(fallback_scoops, 1):
        print(f"{'='*70}")
        print(f"📌 Scoop #{i}: {scoop['title']}")
        print(f"📝 {scoop['content'][:100]}...")
        print(f"🏷️ Category: {scoop['category']}")
        print(f"🔗 Embedded links: {len(scoop.get('embedded_links', []))}")
        if scoop.get('embedded_links'):
            for link in scoop['embedded_links']:
                from urllib.parse import urlparse
                domain = urlparse(link).netloc
                print(f"   • {domain}")
    
    print()
    print("=" * 70)
    print("📊 Summary:")
    print(f"   Total scoops: {len(fallback_scoops)}")
    print(f"   Categories: {', '.join(set(s['category'] for s in fallback_scoops))}")
    total_links = sum(len(s.get('embedded_links', [])) for s in fallback_scoops)
    print(f"   Total embedded links to follow: {total_links}")
    print()
    print("💡 With link-following enabled, the scraper would:")
    print("   1. Extract these scoops from Rotter")
    print("   2. Follow the embedded links to news sites")
    print("   3. Extract media (images/videos) from those linked articles")
    print("   4. Create a news video with rich media content")
    
    # Now try to create actual video
    try:
        print("\n🎬 Creating news video from scoops...")
        
        # Convert to format expected by aggregator
        sources = ["rotter"]  # Use the configured Rotter scraper
        
        # Call the aggregator
        result = await aggregator.create_enhanced_news_edition(
            sources=sources,
            platform="tiktok",
            duration_seconds=60,
            languages=["he"],
            style="breaking news",
            tone="urgent",
            max_stories=5,
            overlay_style="modern",
            enable_discussions=False
        )
        
        if result:
            print(f"\n✅ Video created successfully!")
            print(f"📹 Output: {result}")
        else:
            print("\n⚠️ No video was created (may be due to scraping issues)")
            
    except Exception as e:
        print(f"\n❌ Error creating video: {e}")

def main():
    """Run the test"""
    print("🚀 Rotter.net Scoops Test with Link Following")
    print("This demonstrates how Rotter scoops with embedded links would be processed\n")
    
    asyncio.run(test_rotter_scoops())

if __name__ == "__main__":
    main()