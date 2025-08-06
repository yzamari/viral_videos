"""Mock News Aggregator - Works without external dependencies"""

import asyncio
from datetime import datetime
from typing import List

from ..utils.logging_config import get_logger
from ..workflows.generate_viral_video import async_main as generate_viral_video
from .models.content_models import ContentItem, NewsSource, MediaAsset, AssetType, SourceType, ContentStatus

logger = get_logger(__name__)


class MockNewsAggregator:
    """Mock news aggregator that generates videos using scraped content"""
    
    def __init__(self):
        self.mock_articles = self._create_mock_articles()
    
    def _create_mock_articles(self) -> List[ContentItem]:
        """Create mock articles for testing"""
        
        # Ynet mock articles
        ynet_source = NewsSource(
            id="ynet",
            name="Ynet",
            source_type=SourceType.WEB,
            url="https://www.ynet.co.il"
        )
        
        ynet_articles = [
            ContentItem(
                id="ynet_1",
                source=ynet_source,
                title="חדשות מרעישות: גילוי ארכיאולוגי חשוב בירושלים",
                content="ארכיאולוגים גילו היום ממצא נדיר מתקופת בית שני בחפירות בעיר העתיקה...",
                summary="גילוי ארכיאולוגי משמעותי בירושלים",
                published_date=datetime.now(),
                language="he",
                categories=["culture", "history"],
                relevance_score=0.9,
                status=ContentStatus.SCRAPED,
                media_assets=[
                    MediaAsset(
                        id="ynet_1_img",
                        asset_type=AssetType.IMAGE,
                        source_url="https://ynet.co.il/archaeology.jpg"
                    )
                ]
            ),
            ContentItem(
                id="ynet_2",
                source=ynet_source,
                title="הייטק ישראלי: חברת סטארט-אפ גייסה 100 מיליון דולר",
                content="חברת הסטארט-אפ הישראלית השלימה סבב גיוס ענק...",
                summary="גיוס ענק לסטארט-אפ ישראלי",
                published_date=datetime.now(),
                language="he",
                categories=["tech", "business"],
                relevance_score=0.85,
                status=ContentStatus.SCRAPED,
                media_assets=[
                    MediaAsset(
                        id="ynet_2_img",
                        asset_type=AssetType.IMAGE,
                        source_url="https://ynet.co.il/startup.jpg"
                    )
                ]
            )
        ]
        
        # CNN mock articles
        cnn_source = NewsSource(
            id="cnn",
            name="CNN",
            source_type=SourceType.WEB,
            url="https://www.cnn.com"
        )
        
        cnn_articles = [
            ContentItem(
                id="cnn_1",
                source=cnn_source,
                title="Breaking: Major Climate Agreement Reached at UN Summit",
                content="World leaders have agreed on unprecedented measures to combat climate change...",
                summary="Historic climate agreement at UN",
                published_date=datetime.now(),
                language="en",
                categories=["politics", "environment"],
                relevance_score=0.95,
                status=ContentStatus.SCRAPED,
                media_assets=[
                    MediaAsset(
                        id="cnn_1_img",
                        asset_type=AssetType.IMAGE,
                        source_url="https://cnn.com/climate.jpg"
                    ),
                    MediaAsset(
                        id="cnn_1_vid",
                        asset_type=AssetType.VIDEO,
                        source_url="https://cnn.com/climate_video.mp4",
                        duration=30.0
                    )
                ]
            ),
            ContentItem(
                id="cnn_2",
                source=cnn_source,
                title="Tech Giant Unveils Revolutionary AI System",
                content="A major technology company announced a breakthrough in artificial intelligence...",
                summary="AI breakthrough announced",
                published_date=datetime.now(),
                language="en",
                categories=["tech", "ai"],
                relevance_score=0.88,
                status=ContentStatus.SCRAPED,
                media_assets=[
                    MediaAsset(
                        id="cnn_2_img",
                        asset_type=AssetType.IMAGE,
                        source_url="https://cnn.com/ai_tech.jpg"
                    )
                ]
            )
        ]
        
        return ynet_articles + cnn_articles
    
    def _create_mission(self, articles: List[ContentItem], edition_type: str) -> str:
        """Create mission string for video generation"""
        
        # Count by language
        hebrew_count = sum(1 for a in articles if a.language == "he")
        english_count = sum(1 for a in articles if a.language == "en")
        
        mission = f"Create a {edition_type} news edition video featuring {len(articles)} stories. "
        mission += f"Mix of Hebrew ({hebrew_count}) and English ({english_count}) content. "
        
        # Add headlines
        mission += "Headlines include: "
        for i, article in enumerate(articles[:3]):
            mission += f"{i+1}. {article.title[:50]}... "
        
        mission += "Use professional news broadcast style with dynamic visuals. "
        mission += "Note: This demo uses mock scraped media from news sources."
        
        return mission
    
    async def create_news_edition(
        self,
        sources: List[str],
        edition_type: str = "general",
        style: str = "professional",
        tone: str = "informative",
        duration_minutes: int = 5
    ) -> str:
        """Create news edition using mock data and existing video generation"""
        
        logger.info(f"🎬 Creating mock news edition from {len(sources)} sources")
        
        # Filter articles based on sources
        selected_articles = []
        for article in self.mock_articles:
            if any(source in article.source.url for source in sources):
                selected_articles.append(article)
        
        logger.info(f"📰 Selected {len(selected_articles)} articles")
        
        # Create mission for video generation
        mission = self._create_mission(selected_articles, edition_type)
        
        # Prepare media URLs for the video
        media_urls = []
        for article in selected_articles:
            for asset in article.media_assets:
                media_urls.append(asset.source_url)
        
        logger.info(f"📸 Found {len(media_urls)} media assets")
        
        # Generate video using existing infrastructure
        # Note: This will use VEO for generation, but we're providing context about scraped media
        video_params = {
            "mission": mission,
            "category": "News",
            "platform": "youtube",
            "duration": duration_minutes * 60,
            "style": style,
            "tone": tone,
            "visual_style": "dynamic",
            "languages": ["en", "he"],
            "theme": "news_edition",
            "discussions": "simple",
            "mode": "simple",
            "voice": "en-US-Standard-D",
            "veo_model_order": "veo3-fast",
            "business_name": "AI News Network",
            "show_business_info": True,
            "media_context": {
                "scraped_media": media_urls,
                "articles": len(selected_articles),
                "sources": sources
            }
        }
        
        try:
            # Note: In a real implementation, this would:
            # 1. Download the actual media from media_urls
            # 2. Use the downloaded media in video composition
            # 3. Create news segments with the scraped content
            
            # For now, we'll use the existing video generation
            # which will generate content, but we've provided context about scraped media
            output_path = await generate_viral_video(**video_params)
            logger.info(f"✅ News edition created: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to generate video: {str(e)}")
            raise


async def create_mock_news_edition(sources: List[str], **kwargs) -> str:
    """Convenience function to create mock news edition"""
    aggregator = MockNewsAggregator()
    return await aggregator.create_news_edition(sources, **kwargs)