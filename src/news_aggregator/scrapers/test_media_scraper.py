"""Test Media Scraper with Real Downloadable URLs"""

import random
from datetime import datetime, timedelta
from typing import List
from ..models.content_models import ContentItem, MediaAsset, AssetType, NewsSource, SourceType, ContentStatus

class TestMediaScraper:
    """Test scraper with real downloadable media URLs"""
    
    def __init__(self):
        self.test_articles = [
            {
                "title": "טכנולוגיה: פריצת דרך בבינה מלאכותית",
                "content": "חברת הייטק ישראלית פיתחה טכנולוגיה חדשנית לעיבוד שפה טבעית בעברית.",
                "image": "https://picsum.photos/1920/1080",  # Lorem Picsum - always works
                "video": None,
                "categories": ["technology", "ai"]
            },
            {
                "title": "ספורט: ניצחון דרמטי בדקה ה-90",
                "content": "הקבוצה המקומית השיגה ניצחון מרגש בדקות הסיום של המשחק.",
                "image": "https://source.unsplash.com/1920x1080/?soccer,stadium",
                "video": None,
                "categories": ["sports", "football"]
            },
            {
                "title": "כלכלה: שוק ההון בתנודתיות",
                "content": "המדדים המובילים נעים בתנודתיות על רקע אי הוודאות הגלובלית.",
                "image": "https://dummyimage.com/1920x1080/4a90e2/ffffff&text=Stock+Market",
                "video": None,
                "categories": ["economy", "finance"]
            },
            {
                "title": "תרבות: פסטיבל הקולנוע הבינלאומי נפתח",
                "content": "עשרות סרטים מרחבי העולם יוקרנו בפסטיבל השנה.",
                "image": "https://via.placeholder.com/1920x1080/ff6b6b/ffffff?text=Film+Festival",
                "video": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
                "categories": ["culture", "cinema"]
            },
            {
                "title": "מזג אוויר: גשמים כבדים צפויים",
                "content": "התחזית מצביעה על סופת גשמים שתגיע בסוף השבוע.",
                "image": "https://placehold.co/1920x1080/87ceeb/ffffff/png?text=Weather+Report",
                "video": None,
                "categories": ["weather", "news"]
            }
        ]
        
        # Pexels API test data (requires API key for real use)
        self.pexels_test = [
            {
                "title": "טבע: שמורת הטבע החדשה נפתחה",
                "content": "שמורת טבע חדשה בצפון הארץ נפתחה למבקרים.",
                "image": "https://images.pexels.com/photos/417173/pexels-photo-417173.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1080",
                "video": None,
                "categories": ["nature", "environment"]
            }
        ]
    
    async def scrape(self, source: NewsSource, hours_back: int = 24) -> List[ContentItem]:
        """Scrape test articles with real media"""
        
        articles = []
        now = datetime.now()
        
        # Mix different test sources
        all_articles = self.test_articles + self.pexels_test
        
        for idx, data in enumerate(all_articles):
            # Random time in the past hours_back
            published = now - timedelta(minutes=random.randint(5, hours_back * 60))
            
            # Create media assets
            media_assets = []
            
            if data.get("image"):
                # Add random query params to bypass cache
                image_url = data["image"]
                if "?" not in image_url:
                    image_url += f"?rand={random.randint(1000, 9999)}"
                
                media_assets.append(MediaAsset(
                    id=f"img_{idx}_{published.timestamp()}",
                    asset_type=AssetType.IMAGE,
                    source_url=image_url,
                    caption=f"Image for: {data['title']}"
                ))
            
            if data.get("video"):
                media_assets.append(MediaAsset(
                    id=f"vid_{idx}_{published.timestamp()}",
                    asset_type=AssetType.VIDEO,
                    source_url=data["video"],
                    caption=f"Video for: {data['title']}"
                ))
            
            # Create content item
            article = ContentItem(
                id=f"test_{idx}_{published.timestamp()}",
                source=source,
                title=data["title"],
                content=data["content"],
                media_assets=media_assets,
                published_date=published,
                language="he",
                author="Test Reporter",
                url=f"https://test.example.com/article/{idx}",
                status=ContentStatus.SCRAPED,
                categories=data.get("categories", ["general"]),
                relevance_score=random.uniform(0.7, 1.0),
                metadata={
                    "test": True,
                    "media_count": len(media_assets)
                }
            )
            
            articles.append(article)
        
        return articles[:5]  # Return max 5 articles