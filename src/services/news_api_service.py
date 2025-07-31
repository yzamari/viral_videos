"""
News API Service
Provides real news data from multiple sources for fact checking
"""

import os
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
from ..utils.logging_config import get_logger

logger = get_logger(__name__)

class NewsAPIService:
    """
    Unified news API service supporting multiple providers
    """
    
    def __init__(self):
        # Try to get API keys from environment
        self.newsapi_key = os.getenv('NEWSAPI_KEY')
        self.gnews_key = os.getenv('GNEWS_API_KEY')
        self.bing_key = os.getenv('BING_NEWS_API_KEY')
        
        # NewsAPI.org endpoints
        self.newsapi_base = "https://newsapi.org/v2"
        
        # GNews.io endpoints
        self.gnews_base = "https://gnews.io/api/v4"
        
        # Bing News Search API
        self.bing_base = "https://api.bing.microsoft.com/v7.0/news"
        
        # Determine which APIs are available
        self.available_apis = []
        if self.newsapi_key:
            self.available_apis.append('newsapi')
            logger.info("✅ NewsAPI.org configured")
        if self.gnews_key:
            self.available_apis.append('gnews')
            logger.info("✅ GNews.io configured")
        if self.bing_key:
            self.available_apis.append('bing')
            logger.info("✅ Bing News API configured")
            
        if not self.available_apis:
            logger.warning("⚠️ No news API keys found. News features will be limited.")
    
    def search_news(self, 
                   query: str,
                   language: str = 'en',
                   max_results: int = 10,
                   days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Search for news articles across multiple sources
        
        Args:
            query: Search query
            language: Language code (en, es, fr, etc.)
            max_results: Maximum number of results
            days_back: How many days back to search
            
        Returns:
            List of news articles with unified format
        """
        articles = []
        
        # Try each available API
        for api in self.available_apis:
            try:
                if api == 'newsapi':
                    articles.extend(self._search_newsapi(query, language, max_results, days_back))
                elif api == 'gnews':
                    articles.extend(self._search_gnews(query, language, max_results, days_back))
                elif api == 'bing':
                    articles.extend(self._search_bing(query, language, max_results, days_back))
                    
                if len(articles) >= max_results:
                    break
                    
            except Exception as e:
                logger.error(f"Error searching {api}: {e}")
                continue
        
        # Sort by relevance and recency
        articles.sort(key=lambda x: (x.get('relevance_score', 0), x.get('published_at', '')), reverse=True)
        
        return articles[:max_results]
    
    def get_trending_topics(self, 
                          country: str = 'us',
                          category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get trending news topics
        
        Args:
            country: Country code (us, gb, fr, etc.)
            category: News category (business, technology, health, etc.)
            
        Returns:
            List of trending topics with article counts
        """
        topics = []
        
        # Get top headlines from available APIs
        headlines = []
        
        if 'newsapi' in self.available_apis:
            try:
                headlines.extend(self._get_newsapi_headlines(country, category))
            except Exception as e:
                logger.error(f"Error getting NewsAPI headlines: {e}")
        
        if 'gnews' in self.available_apis:
            try:
                headlines.extend(self._get_gnews_headlines(country, category))
            except Exception as e:
                logger.error(f"Error getting GNews headlines: {e}")
        
        # Extract trending topics from headlines
        topic_counts = {}
        for article in headlines:
            # Simple topic extraction from title
            title_words = article.get('title', '').lower().split()
            for word in title_words:
                if len(word) > 4:  # Skip short words
                    topic_counts[word] = topic_counts.get(word, 0) + 1
        
        # Convert to list of topics
        for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:20]:
            topics.append({
                'topic': topic,
                'article_count': count,
                'trending_score': count / len(headlines) if headlines else 0
            })
        
        return topics
    
    def fact_check_claim(self, claim: str) -> Dict[str, Any]:
        """
        Search for articles related to a specific claim for fact checking
        
        Args:
            claim: The claim to fact check
            
        Returns:
            Fact checking result with supporting articles
        """
        # Search for articles about the claim
        articles = self.search_news(claim, max_results=20, days_back=30)
        
        # Analyze article sentiment and credibility
        supporting = []
        contradicting = []
        neutral = []
        
        for article in articles:
            # Simple keyword analysis (in production, use NLP)
            title_lower = article.get('title', '').lower()
            content_lower = article.get('description', '').lower()
            
            if any(word in title_lower + content_lower for word in ['false', 'fake', 'debunked', 'myth', 'not true']):
                contradicting.append(article)
            elif any(word in title_lower + content_lower for word in ['confirmed', 'true', 'verified', 'proven']):
                supporting.append(article)
            else:
                neutral.append(article)
        
        # Calculate verdict
        total_articles = len(articles)
        if total_articles == 0:
            verdict = "No information found"
            confidence = 0.0
        else:
            support_ratio = len(supporting) / total_articles
            contradict_ratio = len(contradicting) / total_articles
            
            if contradict_ratio > 0.6:
                verdict = "Likely false"
                confidence = contradict_ratio
            elif support_ratio > 0.6:
                verdict = "Likely true"
                confidence = support_ratio
            else:
                verdict = "Uncertain"
                confidence = 0.5
        
        return {
            'claim': claim,
            'verdict': verdict,
            'confidence': confidence,
            'total_articles': total_articles,
            'supporting_articles': supporting[:5],
            'contradicting_articles': contradicting[:5],
            'neutral_articles': neutral[:5],
            'search_date': datetime.now().isoformat()
        }
    
    # Private methods for each API
    
    def _search_newsapi(self, query: str, language: str, max_results: int, days_back: int) -> List[Dict[str, Any]]:
        """Search using NewsAPI.org"""
        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        params = {
            'q': query,
            'language': language,
            'from': from_date,
            'sortBy': 'relevancy',
            'pageSize': max_results,
            'apiKey': self.newsapi_key
        }
        
        response = requests.get(f"{self.newsapi_base}/everything", params=params)
        response.raise_for_status()
        
        data = response.json()
        articles = []
        
        for article in data.get('articles', []):
            articles.append({
                'title': article.get('title'),
                'description': article.get('description'),
                'url': article.get('url'),
                'source': article.get('source', {}).get('name'),
                'author': article.get('author'),
                'published_at': article.get('publishedAt'),
                'relevance_score': 0.9,  # NewsAPI sorts by relevance
                'provider': 'newsapi'
            })
        
        return articles
    
    def _search_gnews(self, query: str, language: str, max_results: int, days_back: int) -> List[Dict[str, Any]]:
        """Search using GNews.io"""
        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        params = {
            'q': query,
            'lang': language,
            'from': from_date,
            'max': max_results,
            'apikey': self.gnews_key
        }
        
        response = requests.get(f"{self.gnews_base}/search", params=params)
        response.raise_for_status()
        
        data = response.json()
        articles = []
        
        for article in data.get('articles', []):
            articles.append({
                'title': article.get('title'),
                'description': article.get('description'),
                'url': article.get('url'),
                'source': article.get('source', {}).get('name'),
                'author': None,  # GNews doesn't provide author
                'published_at': article.get('publishedAt'),
                'relevance_score': 0.8,
                'provider': 'gnews'
            })
        
        return articles
    
    def _search_bing(self, query: str, language: str, max_results: int, days_back: int) -> List[Dict[str, Any]]:
        """Search using Bing News API"""
        headers = {
            'Ocp-Apim-Subscription-Key': self.bing_key
        }
        
        params = {
            'q': query,
            'mkt': f'{language}-US',
            'count': max_results,
            'freshness': 'Week' if days_back <= 7 else 'Month'
        }
        
        response = requests.get(f"{self.bing_base}/search", headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        articles = []
        
        for article in data.get('value', []):
            articles.append({
                'title': article.get('name'),
                'description': article.get('description'),
                'url': article.get('url'),
                'source': article.get('provider', [{}])[0].get('name') if article.get('provider') else None,
                'author': None,
                'published_at': article.get('datePublished'),
                'relevance_score': 0.7,
                'provider': 'bing'
            })
        
        return articles
    
    def _get_newsapi_headlines(self, country: str, category: Optional[str]) -> List[Dict[str, Any]]:
        """Get top headlines from NewsAPI"""
        params = {
            'country': country,
            'apiKey': self.newsapi_key
        }
        
        if category:
            params['category'] = category
        
        response = requests.get(f"{self.newsapi_base}/top-headlines", params=params)
        response.raise_for_status()
        
        data = response.json()
        return data.get('articles', [])
    
    def _get_gnews_headlines(self, country: str, category: Optional[str]) -> List[Dict[str, Any]]:
        """Get top headlines from GNews"""
        params = {
            'country': country,
            'max': 20,
            'apikey': self.gnews_key
        }
        
        if category:
            params['topic'] = category
        
        response = requests.get(f"{self.gnews_base}/top-headlines", params=params)
        response.raise_for_status()
        
        data = response.json()
        return data.get('articles', [])

# Singleton instance
news_service = NewsAPIService()