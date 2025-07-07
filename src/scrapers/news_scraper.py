"""
Enhanced news scraper for hot trending topics
"""
import requests
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
import time

from ..utils.logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class NewsArticle:
    """Represents a trending news article"""
    title: str
    description: str
    content: str
    url: str
    source: str
    published_at: datetime
    image_url: Optional[str] = None
    category: str = "general"
    viral_score: float = 0.0

class HotNewsScaper:
    """Scrape hot trending news from multiple sources"""
    
    def __init__(self):
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ViralVideoGenerator/1.0'
        })
        
    def get_trending_news(self, topic: str, max_articles: int = 10, 
                         hours_back: int = 24) -> List[NewsArticle]:
        """
        Get trending news articles for a specific topic
        
        Args:
            topic: Topic to search for (e.g., "AI technology", "crypto", "politics")
            max_articles: Maximum number of articles to return
            hours_back: How many hours back to search
            
        Returns:
            List of NewsArticle objects sorted by viral potential
        """
        logger.info(f"🔥 Fetching hot news for topic: '{topic}'")
        
        articles = []
        
        # Try multiple news sources for comprehensive coverage
        sources = [
            self._get_newsapi_articles,
            self._get_google_news_articles,
            self._get_reddit_trending,
            self._get_twitter_trending
        ]
        
        for source_func in sources:
            try:
                source_articles = source_func(topic, max_articles//len(sources), hours_back)
                articles.extend(source_articles)
                logger.info(f"✅ Got {len(source_articles)} articles from {source_func.__name__}")
            except Exception as e:
                logger.warning(f"⚠️ {source_func.__name__} failed: {e}")
                continue
        
        # Remove duplicates and rank by viral potential
        unique_articles = self._deduplicate_articles(articles)
        ranked_articles = self._rank_by_viral_potential(unique_articles)
        
        logger.info(f"🎯 Found {len(ranked_articles)} trending articles for '{topic}'")
        return ranked_articles[:max_articles]
    
    def _get_newsapi_articles(self, topic: str, max_articles: int, hours_back: int) -> List[NewsArticle]:
        """Get articles from NewsAPI"""
        if not self.news_api_key:
            logger.warning("NEWS_API_KEY not set, skipping NewsAPI")
            return []
            
        # Calculate date range
        from_date = (datetime.now() - timedelta(hours=hours_back)).isoformat()
        
        url = "https://newsapi.org/v2/everything"
        params = {
            'q': topic,
            'from': from_date,
            'sortBy': 'popularity',
            'pageSize': max_articles,
            'language': 'en',
            'apiKey': self.news_api_key
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        articles = []
        
        for article in data.get('articles', []):
            if article['title'] and article['description']:
                articles.append(NewsArticle(
                    title=article['title'],
                    description=article['description'],
                    content=article.get('content', article['description']),
                    url=article['url'],
                    source=article['source']['name'],
                    published_at=datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00')),
                    image_url=article.get('urlToImage'),
                    category="news"
                ))
        
        return articles
    
    def _get_google_news_articles(self, topic: str, max_articles: int, hours_back: int) -> List[NewsArticle]:
        """Get trending articles from Google News RSS (free alternative)"""
        try:
            import feedparser
            
            # Google News RSS feed
            url = f"https://news.google.com/rss/search?q={topic}&hl=en-US&gl=US&ceid=US:en"
            
            feed = feedparser.parse(url)
            articles = []
            
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            for entry in feed.entries[:max_articles]:
                pub_date = datetime(*entry.published_parsed[:6])
                
                if pub_date >= cutoff_time:
                    articles.append(NewsArticle(
                        title=entry.title,
                        description=entry.get('summary', entry.title),
                        content=entry.get('summary', entry.title),
                        url=entry.link,
                        source="Google News",
                        published_at=pub_date,
                        category="trending"
                    ))
            
            return articles
            
        except ImportError:
            logger.warning("feedparser not installed, install with: pip install feedparser")
            return []
        except Exception as e:
            logger.error(f"Google News scraping failed: {e}")
            return []
    
    def _get_reddit_trending(self, topic: str, max_articles: int, hours_back: int) -> List[NewsArticle]:
        """Get trending discussions from Reddit"""
        try:
            # Reddit search API (no auth needed for public posts)
            url = "https://www.reddit.com/search.json"
            params = {
                'q': topic,
                'sort': 'hot',
                'limit': max_articles,
                't': 'day'  # Past day
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for post in data.get('data', {}).get('children', []):
                post_data = post['data']
                
                if post_data.get('selftext') or post_data.get('title'):
                    content = post_data.get('selftext', post_data['title'])
                    if len(content) > 50:  # Filter out very short posts
                        articles.append(NewsArticle(
                            title=post_data['title'],
                            description=content[:200] + "..." if len(content) > 200 else content,
                            content=content,
                            url=f"https://reddit.com{post_data['permalink']}",
                            source="Reddit",
                            published_at=datetime.fromtimestamp(post_data['created_utc']),
                            category="discussion",
                            viral_score=post_data.get('score', 0) / 1000  # Normalize Reddit score
                        ))
            
            return articles
            
        except Exception as e:
            logger.error(f"Reddit scraping failed: {e}")
            return []
    
    def _get_twitter_trending(self, topic: str, max_articles: int, hours_back: int) -> List[NewsArticle]:
        """Get trending Twitter discussions (placeholder - would need Twitter API)"""
        # This would require Twitter API access
        # For now, return empty but structure is ready
        logger.info("Twitter trending requires API setup")
        return []
    
    def _deduplicate_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Remove duplicate articles based on title similarity"""
        unique_articles = []
        seen_titles = set()
        
        for article in articles:
            # Simple deduplication based on first 50 characters of title
            title_key = article.title.lower()[:50]
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_articles.append(article)
        
        return unique_articles
    
    def _rank_by_viral_potential(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Rank articles by viral potential"""
        
        def calculate_viral_score(article: NewsArticle) -> float:
            score = article.viral_score
            
            # Boost score based on recency (more recent = higher score)
            hours_old = (datetime.now() - article.published_at).total_seconds() / 3600
            recency_boost = max(0, 1 - (hours_old / 24))  # Linear decay over 24 hours
            score += recency_boost * 0.5
            
            # Boost score for viral keywords in title
            viral_keywords = [
                'breaking', 'shocking', 'amazing', 'incredible', 'viral', 'trending',
                'exclusive', 'revealed', 'exposed', 'secret', 'insider', 'leaked',
                'dramatic', 'surprising', 'unexpected', 'crisis', 'scandal'
            ]
            
            title_lower = article.title.lower()
            keyword_boost = sum(0.1 for keyword in viral_keywords if keyword in title_lower)
            score += keyword_boost
            
            # Boost for content length (medium length is often more viral)
            content_len = len(article.content)
            if 100 <= content_len <= 500:
                score += 0.2
            
            return score
        
        # Calculate viral scores and sort
        for article in articles:
            article.viral_score = calculate_viral_score(article)
        
        return sorted(articles, key=lambda x: x.viral_score, reverse=True)
    
    def create_video_prompt_from_news(self, article: NewsArticle, 
                                    angle: str = "breaking") -> str:
        """
        Convert news article into viral video prompt
        
        Args:
            article: NewsArticle to convert
            angle: Video angle ('breaking', 'explainer', 'reaction', 'analysis')
            
        Returns:
            Optimized prompt for viral video generation
        """
        
        angles = {
            "breaking": f"BREAKING: {article.title} - Here's what you need to know",
            "explainer": f"Everyone's talking about {article.title} - Let me explain why this matters", 
            "reaction": f"My honest reaction to {article.title}",
            "analysis": f"The real story behind {article.title} that no one is telling you"
        }
        
        prompt = angles.get(angle, angles["breaking"])
        
        # Add context from article
        context = f"\n\nKey details: {article.description[:200]}"
        if len(article.content) > len(article.description):
            context += f"\n\nAdditional context: {article.content[:300]}"
        
        return prompt + context

# Convenience function for easy use
def get_hot_news_video_prompt(topic: str, angle: str = "breaking") -> str:
    """
    Quick function to get a viral video prompt from trending news
    
    Args:
        topic: News topic to search for
        angle: Video angle style
        
    Returns:
        Ready-to-use video prompt based on hot news
    """
    scraper = HotNewsScaper()
    articles = scraper.get_trending_news(topic, max_articles=1)
    
    if articles:
        return scraper.create_video_prompt_from_news(articles[0], angle)
    else:
        return f"Latest updates on {topic} - Breaking developments you need to know" 