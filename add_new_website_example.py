#!/usr/bin/env python3
"""
Example: How to add ANY website to the news aggregator
No coding required - just configuration!
"""

import asyncio
from src.news_aggregator.scrapers.universal_scraper import UniversalNewsScraper


# Example 1: Add The Guardian
guardian_config = {
    'name': 'The Guardian',
    'base_url': 'https://www.theguardian.com/international',
    'language': 'en',
    'selectors': {
        'article_container': 'div[data-link-name="article"]',
        'title': 'h3, a[data-link-name="article"] span',
        'url': 'a[href]',
        'description': 'div.fc-item__standfirst',
        'author': 'span.fc-item__byline',
        'date': 'time'
    },
    'category_mapping': {
        'politics': ['politics', 'election', 'government', 'parliament'],
        'sports': ['football', 'sport', 'match', 'game'],
        'technology': ['tech', 'digital', 'internet', 'data']
    }
}

# Example 2: Add Times of Israel
times_of_israel_config = {
    'name': 'Times of Israel',
    'base_url': 'https://www.timesofisrael.com',
    'language': 'en',
    'selectors': {
        'article_container': 'article, div.item',
        'title': 'h2.headline, h3.headline',
        'url': 'a[href]',
        'description': 'p.excerpt',
        'author': 'span.byline',
        'date': 'span.date'
    },
    'media_extraction': {
        'image_selector': 'img.featured-image, img[src*="timesofisrael"]'
    },
    'category_mapping': {
        'politics': ['knesset', 'netanyahu', 'government', 'minister'],
        'security': ['idf', 'gaza', 'hamas', 'security'],
        'technology': ['startup', 'tech', 'cyber', 'innovation']
    }
}

# Example 3: Add Haaretz
haaretz_config = {
    'name': 'Haaretz',
    'base_url': 'https://www.haaretz.com',
    'language': 'he',
    'selectors': {
        'article_container': 'article, section.article-item',
        'title': 'h1, h2, h3.article-title',
        'url': 'a[href]',
        'description': 'p.article-brief',
        'author': 'address.author-name',
        'date': 'time'
    },
    'patterns': {
        'category_patterns': {
            '/news/': 'general',
            '/israel-news/': 'politics',
            '/middle-east/': 'world',
            '/business/': 'finance'
        }
    }
}

# Example 4: Add custom Israeli forum/blog
israeli_tech_blog_config = {
    'name': 'GeekTime',
    'base_url': 'https://www.geektime.co.il',
    'language': 'he',
    'selectors': {
        'article_container': 'article.post',
        'title': 'h2.entry-title',
        'url': 'a[href]',
        'description': 'div.entry-summary',
        'author': 'span.author',
        'date': 'time.published'
    },
    'category_mapping': {
        'technology': ['סטארטאפ', 'טכנולוגיה', 'חדשנות', 'אפליקציה'],
        'finance': ['השקעה', 'מימון', 'יוניקורן', 'אקזיט']
    }
}

# Example 5: Add social media (Twitter/X)
twitter_config = {
    'name': 'Twitter Breaking News',
    'base_url': 'https://twitter.com/search?q=breaking%20news%20israel',
    'language': 'multi',
    'selectors': {
        'article_container': 'article[data-testid="tweet"]',
        'title': 'div[data-testid="tweetText"]',
        'url': 'a[href*="/status/"]',
        'author': 'span[data-testid="User-Name"]',
        'date': 'time'
    },
    'media_extraction': {
        'image_selector': 'img[alt="Image"]',
        'video_selector': 'video'
    }
}


async def demonstrate_adding_websites():
    """Show how easy it is to add new websites"""
    
    print("""
🌐 ADDING NEW WEBSITES TO NEWS AGGREGATOR
========================================
No coding required - just configuration!
""")
    
    # Initialize scraper
    scraper = UniversalNewsScraper()
    
    # Add all example websites
    websites = [
        ('guardian', guardian_config),
        ('times_of_israel', times_of_israel_config),
        ('haaretz', haaretz_config),
        ('geektime', israeli_tech_blog_config),
        ('twitter', twitter_config)
    ]
    
    print("\n📝 Adding websites:")
    for site_id, config in websites:
        scraper.add_website_config(site_id, config)
    
    # Now scrape from any of them
    print("\n📰 Scraping news from newly added sites...")
    
    # Example: Scrape Times of Israel
    print("\n🇮🇱 Scraping Times of Israel...")
    articles = await scraper.scrape_website('times_of_israel', max_items=5)
    
    if articles:
        print(f"Found {len(articles)} articles:")
        for article in articles[:3]:
            print(f"  • {article['title'][:60]}...")
    
    # Show configuration structure
    print("""

📋 HOW TO ADD YOUR OWN WEBSITE:
==============================

1. Create a configuration dictionary:
   config = {
       'name': 'Website Name',
       'base_url': 'https://website.com',
       'language': 'en',  # or 'he', 'ar', etc.
       'selectors': {
           'article_container': 'CSS selector for article',
           'title': 'CSS selector for title',
           'url': 'CSS selector for link',
           'description': 'CSS selector for description'
       },
       'category_mapping': {
           'politics': ['keyword1', 'keyword2'],
           'sports': ['sport', 'game', 'match']
       }
   }

2. Add it to the scraper:
   scraper.add_website_config('my_site', config)

3. Scrape articles:
   articles = await scraper.scrape_website('my_site')

That's it! No new code needed! 🎉
""")
    
    # Show all configured sites
    print("\n📚 All configured websites:")
    for site_id, config in scraper.configs.items():
        print(f"  • {site_id}: {config.name} ({config.base_url})")


def show_selector_tips():
    """Show tips for finding CSS selectors"""
    
    print("""
🔍 HOW TO FIND CSS SELECTORS:
============================

1. Open the website in Chrome/Firefox
2. Right-click on an article → "Inspect Element"
3. Look for patterns:

   ARTICLE CONTAINERS:
   • <article> tags
   • <div class="post">
   • <div class="article-item">
   • <section class="news-item">

   TITLES:
   • <h1>, <h2>, <h3> tags
   • <span class="headline">
   • <a class="title">

   COMMON PATTERNS:
   • BBC: article[data-testid="card"]
   • CNN: div[class*="card"]
   • Guardian: div[data-link-name="article"]
   • Reddit: Use JSON API instead

4. Test your selectors:
   • Browser Console: document.querySelectorAll('your-selector')
   • Should return multiple elements

💡 TIPS:
• Use class names that look specific to articles
• Avoid generic classes like "container" or "wrapper"
• Look for data-* attributes - they're often stable
• Check if the site has a JSON API (faster!)
""")


if __name__ == "__main__":
    # Run demonstration
    asyncio.run(demonstrate_adding_websites())
    
    # Show selector tips
    print("\n" + "="*50)
    show_selector_tips()