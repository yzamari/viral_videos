#!/usr/bin/env python3
"""
Template Selector - Automatically selects appropriate overlay based on content
"""

import re
from typing import Dict, List, Optional
try:
    from .professional_templates import (
        create_general_news_overlay,
        create_sports_overlay,
        create_gossip_overlay,
        create_tv_show_overlay,
        create_finance_overlay,
        create_tech_overlay,
        create_weather_overlay,
        create_entertainment_overlay,
        create_breaking_news_overlay,
        create_documentary_overlay
    )
except ImportError:
    from professional_templates import (
        create_general_news_overlay,
        create_sports_overlay,
        create_gossip_overlay,
        create_tv_show_overlay,
        create_finance_overlay,
        create_tech_overlay,
        create_weather_overlay,
        create_entertainment_overlay,
        create_breaking_news_overlay,
        create_documentary_overlay
    )


# Keywords for each category
CATEGORY_KEYWORDS = {
    'sports': [
        'game', 'match', 'score', 'player', 'team', 'champion', 'league',
        'football', 'basketball', 'soccer', 'tennis', 'golf', 'baseball',
        'athlete', 'olympic', 'tournament', 'victory', 'defeat', 'goal',
        'sport', 'nba', 'nfl', 'fifa', 'espn', 'stadium', 'coach'
    ],
    'gossip': [
        'celebrity', 'scandal', 'dating', 'breakup', 'exclusive', 'spotted',
        'rumor', 'affair', 'divorce', 'engaged', 'pregnant', 'drama',
        'hollywood', 'star', 'actress', 'actor', 'singer', 'rapper',
        'fashion', 'red carpet', 'paparazzi', 'tmz', 'insider'
    ],
    'finance': [
        'stock', 'market', 'dow', 'nasdaq', 'trading', 'investor', 'economy',
        'bitcoin', 'crypto', 'currency', 'dollar', 'euro', 'inflation',
        'earnings', 'revenue', 'profit', 'loss', 'bank', 'federal',
        'gdp', 'recession', 'bull', 'bear', 'ipo', 'merger', 'acquisition'
    ],
    'tech': [
        'technology', 'ai', 'artificial intelligence', 'startup', 'app',
        'software', 'hardware', 'google', 'apple', 'microsoft', 'meta',
        'algorithm', 'data', 'cyber', 'hack', 'security', 'innovation',
        'robot', 'automation', 'digital', 'internet', 'cloud', 'quantum'
    ],
    'weather': [
        'weather', 'temperature', 'forecast', 'storm', 'hurricane', 'tornado',
        'rain', 'snow', 'sunny', 'cloudy', 'wind', 'climate', 'degree',
        'celsius', 'fahrenheit', 'precipitation', 'humidity', 'pressure'
    ],
    'entertainment': [
        'movie', 'film', 'premiere', 'box office', 'award', 'oscar', 'grammy',
        'music', 'concert', 'tour', 'album', 'release', 'netflix', 'disney',
        'show', 'series', 'season', 'episode', 'streaming', 'theater'
    ],
    'breaking_news': [
        'breaking', 'urgent', 'alert', 'emergency', 'developing', 'just in',
        'live', 'update', 'confirmed', 'explosion', 'attack', 'crash',
        'disaster', 'critical', 'immediate', 'warning', 'evacuation'
    ],
    'documentary': [
        'documentary', 'history', 'biography', 'investigation', 'explore',
        'discover', 'uncover', 'reveal', 'journey', 'story', 'archive',
        'footage', 'interview', 'research', 'evidence', 'chronicle'
    ],
    'tv_show': [
        'tonight', 'tonight show', 'late night', 'talk show', 'host',
        'guest', 'interview', 'comedy', 'monologue', 'audience',
        'studio', 'live audience', 'special guest', 'celebrity interview'
    ]
}


# Template mapping
TEMPLATE_FUNCTIONS = {
    'general_news': create_general_news_overlay,
    'sports': create_sports_overlay,
    'gossip': create_gossip_overlay,
    'tv_show': create_tv_show_overlay,
    'finance': create_finance_overlay,
    'tech': create_tech_overlay,
    'weather': create_weather_overlay,
    'entertainment': create_entertainment_overlay,
    'breaking_news': create_breaking_news_overlay,
    'documentary': create_documentary_overlay
}


def analyze_content(text: str, source: Optional[str] = None) -> Dict[str, float]:
    """Analyze content and return category scores"""
    text_lower = text.lower()
    scores = {category: 0.0 for category in CATEGORY_KEYWORDS}
    
    # Calculate scores for each category
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                # Multi-word keywords get higher weight
                weight = len(keyword.split())
                scores[category] += weight
    
    # Source-based adjustments
    if source:
        source_lower = source.lower()
        if 'espn' in source_lower or 'sport' in source_lower:
            scores['sports'] += 10.0
        elif 'tmz' in source_lower or 'gossip' in source_lower:
            scores['gossip'] += 10.0
        elif 'bloomberg' in source_lower or 'finance' in source_lower:
            scores['finance'] += 10.0
        elif 'tech' in source_lower or 'verge' in source_lower:
            scores['tech'] += 10.0
        elif 'weather' in source_lower:
            scores['weather'] += 10.0
        elif 'entertainment' in source_lower or 'variety' in source_lower:
            scores['entertainment'] += 10.0
    
    # Check for breaking news indicators
    if any(word in text_lower for word in ['breaking:', 'urgent:', 'just in:', 'alert:']):
        scores['breaking_news'] = max(scores.get('breaking_news', 0), 10.0)
    
    return scores


def select_template(content_items: List[Dict], default: str = 'general_news') -> str:
    """Select the most appropriate template based on content analysis"""
    
    if not content_items:
        return default
    
    # Aggregate scores across all content
    total_scores = {}
    
    for item in content_items:
        # Combine title and description for analysis
        text = f"{item.get('title', '')} {item.get('description', '')}"
        source = item.get('source', '')
        
        scores = analyze_content(text, source)
        
        for category, score in scores.items():
            total_scores[category] = total_scores.get(category, 0) + score
    
    # Find category with highest score
    if total_scores:
        best_category = max(total_scores.items(), key=lambda x: x[1])[0]
        
        # Only use specialized template if score is significant
        if total_scores[best_category] > 0:
            return best_category
    
    return default


def get_overlay_for_content(content_items: List[Dict], 
                          force_template: Optional[str] = None,
                          language: str = 'en'):
    """Get the appropriate overlay for given content"""
    
    # If template is forced, use it
    if force_template and force_template in TEMPLATE_FUNCTIONS:
        template_name = force_template
    else:
        # Auto-select based on content
        template_name = select_template(content_items)
    
    # Create overlay
    overlay_func = TEMPLATE_FUNCTIONS.get(template_name, create_general_news_overlay)
    overlay = overlay_func()
    
    print(f"📋 Selected template: {template_name}")
    
    return overlay, template_name


def get_template_info():
    """Get information about available templates"""
    return {
        'general_news': {
            'name': 'General News',
            'description': 'CNN-style professional news overlay',
            'best_for': 'General news, politics, world events'
        },
        'sports': {
            'name': 'Sports',
            'description': 'ESPN-style sports overlay with score displays',
            'best_for': 'Sports news, game highlights, athlete stories'
        },
        'gossip': {
            'name': 'Celebrity Gossip',
            'description': 'TMZ-style gossip and entertainment news',
            'best_for': 'Celebrity news, scandals, entertainment gossip'
        },
        'tv_show': {
            'name': 'TV Show',
            'description': 'Late night talk show style overlay',
            'best_for': 'Talk shows, interviews, comedy segments'
        },
        'finance': {
            'name': 'Finance',
            'description': 'Bloomberg-style financial news overlay',
            'best_for': 'Stock market, crypto, economic news'
        },
        'tech': {
            'name': 'Technology',
            'description': 'Futuristic tech news overlay',
            'best_for': 'Tech news, startups, AI, gadgets'
        },
        'weather': {
            'name': 'Weather',
            'description': 'Weather channel style forecast overlay',
            'best_for': 'Weather updates, forecasts, climate news'
        },
        'entertainment': {
            'name': 'Entertainment',
            'description': 'E! style entertainment news overlay',
            'best_for': 'Movies, music, awards, premieres'
        },
        'breaking_news': {
            'name': 'Breaking News',
            'description': 'Urgent breaking news alert overlay',
            'best_for': 'Breaking stories, urgent updates, alerts'
        },
        'documentary': {
            'name': 'Documentary',
            'description': 'Cinematic documentary style overlay',
            'best_for': 'Documentaries, investigations, historical content'
        }
    }


if __name__ == "__main__":
    # Test the template selector
    print("🧪 Testing Template Selector...")
    print("=" * 50)
    
    test_cases = [
        {
            'content': [{'title': 'Lakers defeat Celtics 110-95', 'description': 'LeBron scores 35 points'}],
            'expected': 'sports'
        },
        {
            'content': [{'title': 'Brad Pitt spotted with new girlfriend', 'source': 'TMZ'}],
            'expected': 'gossip'
        },
        {
            'content': [{'title': 'Stock market crashes as inflation fears rise', 'source': 'Bloomberg'}],
            'expected': 'finance'
        },
        {
            'content': [{'title': 'BREAKING: Earthquake hits California', 'description': 'Urgent evacuation ordered'}],
            'expected': 'breaking_news'
        },
        {
            'content': [{'title': 'Apple unveils new AI assistant', 'description': 'Revolutionary technology announced'}],
            'expected': 'tech'
        }
    ]
    
    for i, test in enumerate(test_cases):
        print(f"\nTest {i+1}:")
        print(f"Content: {test['content'][0]['title']}")
        selected = select_template(test['content'])
        print(f"Selected: {selected}")
        print(f"Expected: {test['expected']}")
        print(f"✅ Match!" if selected == test['expected'] else "❌ Mismatch")
    
    print("\n📋 Available Templates:")
    for key, info in get_template_info().items():
        print(f"\n{key}:")
        print(f"  Name: {info['name']}")
        print(f"  Description: {info['description']}")
        print(f"  Best for: {info['best_for']}")