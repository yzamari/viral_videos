"""Israeli Content Processor - Uses existing ViralAI infrastructure"""

from typing import List, Dict, Any, Optional
import random

from ...utils.logging_config import get_logger
from ...core.decision_framework import DecisionFramework, CoreDecisions
from ...models.video_models import Language, VideoCategory, Platform
from ..models.content_models import ContentItem

logger = get_logger(__name__)


class IsraeliContentProcessor:
    """Process Israeli news content using existing style/tone infrastructure"""
    
    def __init__(self, decision_framework: DecisionFramework):
        self.decision_framework = decision_framework
        
        # Map content types to existing style/tone options
        self.content_style_mapping = {
            "political_scandal": {
                "style": "satirical",
                "tone": "sarcastic",
                "visual_style": "dramatic"
            },
            "bizarre_news": {
                "style": "humorous", 
                "tone": "playful",
                "visual_style": "dynamic"
            },
            "serious_news": {
                "style": "professional",
                "tone": "informative", 
                "visual_style": "minimalist"
            },
            "tech_news": {
                "style": "educational",
                "tone": "engaging",
                "visual_style": "modern"
            },
            "sports": {
                "style": "energetic",
                "tone": "exciting",
                "visual_style": "fast-paced"
            }
        }
        
        # Dark humor templates that work with any style
        self.humor_enhancers = {
            "opening": [
                "אז מה קרה היום בארץ הקודש? ספוילר: לא משהו קדוש במיוחד",
                "עוד יום רגיל בישראל, כלומר - משהו בין קומדיה לטרגדיה",
                "ברוכים הבאים לסיכום החדשות, או כמו שאנחנו קוראים לזה - 'למה אנחנו כאלה?'"
            ],
            "transition": [
                "ואם חשבתם שזה מוזר, חכו לסיפור הבא",
                "עוברים לחדשות הבאות, כי למה לא?",
                "ובינתיים, במקום אחר לגמרי אבל באותה מדינה משוגעת..."
            ],
            "commentary": {
                "political": [
                    "כי פוליטיקה ישראלית זה כמו ריאליטי, רק פחות אמין",
                    "זוכרים כשחשבנו שיש גבול? גם אנחנו לא"
                ],
                "bizarre": [
                    "רק בישראל דבר כזה יכול לקרות... ולהיחשב נורמלי",
                    "ולא, זה לא מ'ארץ נהדרת'. זה החיים האמיתיים"
                ],
                "economy": [
                    "הכלכלה הישראלית: איפה הכל עולה חוץ מהמורל",
                    "מומחים אומרים שזה זמני. מ-1948."
                ]
            }
        }
    
    def process_for_news_video(
        self, 
        articles: List[ContentItem],
        target_style: str = "dark_humor",
        language: Language = Language.HEBREW
    ) -> Dict[str, Any]:
        """Process articles for news video generation"""
        
        # Select top 5 most interesting articles
        selected_articles = self._select_top_articles(articles, count=5)
        
        # Create segments for each article
        segments = []
        for i, article in enumerate(selected_articles):
            segment = self._create_segment(
                article, 
                position=i,
                total=len(selected_articles),
                style_override=target_style
            )
            segments.append(segment)
        
        # Create overall structure
        video_structure = {
            "intro": self._create_intro(target_style, language),
            "segments": segments,
            "outro": self._create_outro(target_style, language),
            "theme": "israeli_news",
            "presenter": {
                "type": "alien",
                "position": "bottom_right",
                "commentary_style": target_style
            }
        }
        
        return video_structure
    
    def _select_top_articles(self, articles: List[ContentItem], count: int = 5) -> List[ContentItem]:
        """Select most interesting articles based on scores"""
        # Sort by combined interest and humor scores
        scored_articles = []
        for article in articles:
            score = (
                article.metadata.get("interest_score", 0) * 0.6 +
                article.metadata.get("humor_score", 0) * 0.4
            )
            # Boost bizarre news
            if article.metadata.get("is_bizarre", False):
                score += 0.2
            
            scored_articles.append((score, article))
        
        # Sort and return top articles
        scored_articles.sort(key=lambda x: x[0], reverse=True)
        return [article for _, article in scored_articles[:count]]
    
    def _create_segment(
        self, 
        article: ContentItem,
        position: int,
        total: int,
        style_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create video segment from article"""
        
        # Determine content type
        content_type = self._determine_content_type(article)
        
        # Get style configuration
        if style_override == "dark_humor":
            # Apply dark humor to any content type
            style_config = self.content_style_mapping.get(content_type, {}).copy()
            style_config["tone"] = "sarcastic" if content_type == "political_scandal" else "humorous"
            commentary = self._generate_dark_commentary(article, content_type)
        else:
            style_config = self.content_style_mapping.get(content_type, {})
            commentary = None
        
        # Create segment
        segment = {
            "article_id": article.id,
            "title": article.title,
            "summary": article.summary or article.content[:200],
            "duration": 30 + (10 if article.has_video() else 0),  # Longer if has video
            "style": style_config.get("style", "professional"),
            "tone": style_config.get("tone", "informative"),
            "visual_style": style_config.get("visual_style", "dynamic"),
            "media": {
                "primary": article.get_primary_media(),
                "all": article.media_assets
            },
            "alien_commentary": commentary,
            "position": position,
            "transition": self._get_transition(position, total)
        }
        
        return segment
    
    def _determine_content_type(self, article: ContentItem) -> str:
        """Determine article content type"""
        title_lower = article.title.lower()
        content_lower = article.content.lower()
        
        # Check categories first
        if "פוליטיקה" in article.categories or any(
            word in title_lower for word in ["שחיתות", "חקירה", "ביבי", "כנסת"]
        ):
            return "political_scandal"
        
        if article.metadata.get("is_bizarre", False):
            return "bizarre_news"
        
        if any(word in article.categories for word in ["טכנולוגיה", "מדע", "סטארטאפ"]):
            return "tech_news"
        
        if "ספורט" in article.categories:
            return "sports"
        
        return "serious_news"
    
    def _generate_dark_commentary(self, article: ContentItem, content_type: str) -> str:
        """Generate dark humor commentary for article"""
        templates = self.humor_enhancers["commentary"].get(
            content_type.split("_")[0],  # Get base type
            ["עוד סיפור ישראלי טיפוסי"]
        )
        
        base_commentary = random.choice(templates)
        
        # Add specific observations
        if "מיליון" in article.content or "מיליארד" in article.content:
            base_commentary += ". כסף? תמיד יש. רק לא לדברים החשובים"
        
        if article.metadata.get("is_bizarre", False):
            base_commentary += ". ברצינות, אי אפשר להמציא דבר כזה"
        
        return base_commentary
    
    def _create_intro(self, style: str, language: Language) -> Dict[str, Any]:
        """Create intro segment"""
        if style == "dark_humor":
            text = random.choice(self.humor_enhancers["opening"])
        else:
            text = "ברוכים הבאים לסיכום החדשות היומי" if language == Language.HEBREW else "Welcome to today's news summary"
        
        return {
            "text": text,
            "duration": 5,
            "style": "dramatic",
            "alien_appears": True,
            "alien_animation": "entrance"
        }
    
    def _create_outro(self, style: str, language: Language) -> Dict[str, Any]:
        """Create outro segment"""
        if style == "dark_humor":
            text = "זהו להיום. תזכרו - מחר יהיה אותו דבר, רק עם שמות אחרים"
        else:
            text = "תודה שצפיתם. נתראה מחר" if language == Language.HEBREW else "Thanks for watching. See you tomorrow"
        
        return {
            "text": text,
            "duration": 5,
            "style": "casual",
            "alien_animation": "wave_goodbye"
        }
    
    def _get_transition(self, position: int, total: int) -> str:
        """Get transition text between segments"""
        if position == 0:
            return ""
        elif position == total - 1:
            return "ולסיום..."
        else:
            return random.choice(self.humor_enhancers["transition"])