"""Content Analyzer - Analyzes news content for relevance and interest"""

from typing import List, Dict, Any, Optional
import re
from datetime import datetime, timedelta

from ...utils.logging_config import get_logger
from ...ai.manager import AIServiceManager
from ..models.content_models import ContentItem, AssetType

logger = get_logger(__name__)


class ContentAnalyzer:
    """Analyzes content for relevance, interest, and categorization"""
    
    def __init__(self, ai_manager: AIServiceManager):
        self.ai_manager = ai_manager
        
        # Keywords for different edition types
        self.edition_keywords = {
            "general": {
                "include": ["breaking", "major", "important", "announced", "report"],
                "exclude": ["opinion", "sponsored", "advertisement"]
            },
            "gossip": {
                "include": ["celebrity", "scandal", "dating", "divorce", "drama", 
                           "revealed", "shocking", "exclusive", "spotted"],
                "exclude": ["politics", "finance", "technology"]
            },
            "sports": {
                "include": ["game", "match", "win", "lose", "score", "championship",
                           "player", "team", "coach", "transfer", "injury"],
                "exclude": ["gossip", "entertainment"]
            },
            "finance": {
                "include": ["market", "stock", "economy", "earnings", "trading",
                           "investment", "crypto", "dollar", "inflation", "rates"],
                "exclude": ["sports", "entertainment", "gossip"]
            },
            "tech": {
                "include": ["AI", "startup", "launch", "app", "software", "hardware",
                           "innovation", "tech", "digital", "cyber", "data"],
                "exclude": ["gossip", "sports"]
            }
        }
        
        # Sentiment keywords
        self.sentiment_keywords = {
            "positive": ["success", "win", "achieve", "improve", "growth", "breakthrough"],
            "negative": ["fail", "loss", "crisis", "problem", "scandal", "crash"],
            "neutral": ["report", "announce", "update", "change", "plan"]
        }
    
    async def analyze(
        self,
        content_item: ContentItem,
        edition_type: str,
        target_language: str
    ) -> Dict[str, Any]:
        """Analyze content item for relevance and metadata"""
        
        # Basic analysis
        analysis = {
            "relevance_score": 0.0,
            "sentiment_score": 0.0,
            "interest_score": 0.0,
            "summary": "",
            "tags": [],
            "categories": [],
            "metadata": {}
        }
        
        # Calculate relevance score
        analysis["relevance_score"] = self._calculate_relevance(
            content_item, 
            edition_type
        )
        
        # Calculate sentiment
        analysis["sentiment_score"] = self._calculate_sentiment(content_item)
        
        # Calculate interest score
        analysis["interest_score"] = self._calculate_interest(content_item)
        
        # Generate summary using AI
        if analysis["relevance_score"] > 0.3:
            analysis["summary"] = await self._generate_summary(
                content_item,
                target_language
            )
        
        # Extract tags
        analysis["tags"] = self._extract_tags(content_item)
        
        # Categorize content
        analysis["categories"] = self._categorize_content(content_item)
        
        # Add metadata
        analysis["metadata"] = self._extract_metadata(content_item)
        
        return analysis
    
    def _calculate_relevance(
        self, 
        content_item: ContentItem,
        edition_type: str
    ) -> float:
        """Calculate relevance score based on edition type"""
        score = 0.0
        
        # Get keywords for edition type
        keywords = self.edition_keywords.get(
            edition_type, 
            self.edition_keywords["general"]
        )
        
        # Check title and content
        text = f"{content_item.title} {content_item.content}".lower()
        
        # Count include keywords
        include_count = sum(
            1 for keyword in keywords["include"] 
            if keyword.lower() in text
        )
        
        # Count exclude keywords (negative impact)
        exclude_count = sum(
            1 for keyword in keywords["exclude"] 
            if keyword.lower() in text
        )
        
        # Base score on keyword presence
        if include_count > 0:
            score = min(include_count * 0.2, 0.8)
        
        # Reduce score for excluded content
        score -= exclude_count * 0.3
        
        # Boost for recent content
        age_hours = (datetime.now() - content_item.published_date).total_seconds() / 3600
        if age_hours < 1:
            score += 0.3
        elif age_hours < 6:
            score += 0.2
        elif age_hours < 24:
            score += 0.1
        
        # Boost for media presence
        if content_item.has_video():
            score += 0.2
        elif content_item.has_images():
            score += 0.1
        
        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, score))
    
    def _calculate_sentiment(self, content_item: ContentItem) -> float:
        """Calculate sentiment score (-1 to 1)"""
        text = f"{content_item.title} {content_item.content}".lower()
        
        positive_count = sum(
            1 for word in self.sentiment_keywords["positive"]
            if word in text
        )
        
        negative_count = sum(
            1 for word in self.sentiment_keywords["negative"]
            if word in text
        )
        
        # Calculate sentiment
        if positive_count + negative_count == 0:
            return 0.0
        
        sentiment = (positive_count - negative_count) / (positive_count + negative_count)
        return sentiment
    
    def _calculate_interest(self, content_item: ContentItem) -> float:
        """Calculate interest score based on various factors"""
        score = 0.0
        
        # Media presence
        if content_item.has_video():
            score += 0.3
        if content_item.has_images():
            score += 0.2
        
        # Content length (moderate length is better)
        content_length = len(content_item.content)
        if 200 <= content_length <= 2000:
            score += 0.2
        elif content_length > 2000:
            score += 0.1
        
        # Title characteristics
        title = content_item.title.lower()
        
        # Questions in title
        if '?' in title:
            score += 0.1
        
        # Numbers in title (listicles, stats)
        if any(char.isdigit() for char in title):
            score += 0.1
        
        # Excitement words
        excitement_words = ["breaking", "exclusive", "shocking", "amazing", 
                           "unbelievable", "viral", "trending"]
        if any(word in title for word in excitement_words):
            score += 0.2
        
        # Platform-specific boosts
        if content_item.metadata.get("platform") == "reddit":
            # Reddit score/engagement
            reddit_score = content_item.metadata.get("score", 0)
            if reddit_score > 1000:
                score += 0.2
            elif reddit_score > 100:
                score += 0.1
        
        return min(1.0, score)
    
    async def _generate_summary(
        self,
        content_item: ContentItem,
        target_language: str
    ) -> str:
        """Generate summary using AI"""
        
        # If content is already short, use it as summary
        if len(content_item.content) < 200:
            return content_item.content
        
        # Use AI to generate summary
        prompt = f"""Summarize this news article in 2-3 sentences.
        Language: {target_language}
        
        Title: {content_item.title}
        Content: {content_item.content[:1000]}...
        
        Summary:"""
        
        try:
            response = await self.ai_manager.generate_text(prompt, max_tokens=150)
            return response.strip()
        except Exception as e:
            logger.warning(f"Failed to generate AI summary: {str(e)}")
            # Fallback to simple truncation
            return content_item.content[:200] + "..."
    
    def _extract_tags(self, content_item: ContentItem) -> List[str]:
        """Extract relevant tags from content"""
        tags = []
        text = f"{content_item.title} {content_item.content}".lower()
        
        # Extract hashtags if present
        hashtags = re.findall(r'#(\w+)', text)
        tags.extend(hashtags[:5])
        
        # Extract capitalized phrases (likely important terms)
        cap_phrases = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', 
                                content_item.content)
        
        # Filter and add unique phrases
        for phrase in cap_phrases:
            if len(phrase) > 3 and phrase not in tags:
                tags.append(phrase.lower())
                if len(tags) >= 10:
                    break
        
        return tags
    
    def _categorize_content(self, content_item: ContentItem) -> List[str]:
        """Categorize content based on keywords"""
        categories = []
        text = f"{content_item.title} {content_item.content}".lower()
        
        # Check each edition type's keywords
        for edition_type, keywords in self.edition_keywords.items():
            match_count = sum(
                1 for keyword in keywords["include"]
                if keyword.lower() in text
            )
            
            if match_count >= 2:  # At least 2 keywords match
                categories.append(edition_type)
        
        # Add existing categories from content item
        categories.extend(content_item.categories)
        
        # Remove duplicates and return
        return list(set(categories))
    
    def _extract_metadata(self, content_item: ContentItem) -> Dict[str, Any]:
        """Extract additional metadata from content"""
        metadata = {}
        
        # Content characteristics
        metadata["word_count"] = len(content_item.content.split())
        metadata["has_numbers"] = bool(re.search(r'\d+', content_item.content))
        metadata["has_quotes"] = '"' in content_item.content or "'" in content_item.content
        
        # Media analysis
        if content_item.media_assets:
            metadata["media_count"] = len(content_item.media_assets)
            metadata["media_types"] = list(set(
                asset.asset_type.value for asset in content_item.media_assets
            ))
        
        # Time-based metadata
        age_hours = (datetime.now() - content_item.published_date).total_seconds() / 3600
        metadata["age_hours"] = round(age_hours, 1)
        metadata["is_recent"] = age_hours < 24
        metadata["is_breaking"] = age_hours < 1
        
        # Engagement hints
        if "views" in content_item.metadata:
            views = content_item.metadata["views"]
            metadata["high_engagement"] = views > 10000
        
        return metadata