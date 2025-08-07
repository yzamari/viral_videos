# News Source Configuration Guide

The News Aggregator now supports configurable sources instead of hardcoded scrapers. You can add any website, Telegram channel, or social media source by creating configuration files.

## Configuration Directory

Place your configuration files in: `scraper_configs/`

Each source should have its own `.json` file (e.g., `ynet.json`, `cnn.json`, `my_news_site.json`)

## Configuration Format

```json
{
  "name": "Site Display Name",
  "base_url": "https://example.com",
  "language": "en",
  "selectors": {
    "article_container": "article, .news-item",
    "title": "h1, h2, .title",
    "description": ".summary, .excerpt", 
    "url": "a[href]",
    "image": "img",
    "video": "video, iframe"
  },
  "headers": {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
  },
  "test_articles": [
    {
      "title": "Test Article Title",
      "description": "Test article content for development",
      "url": "https://example.com/article1",
      "image_url": "https://picsum.photos/800/600",
      "source": "Test"
    }
  ]
}
```

## Configuration Fields

- **name**: Display name for the source
- **base_url**: Main URL to scrape from  
- **language**: Content language code (en, he, ar, etc.)
- **selectors**: CSS selectors to find content elements
- **headers**: Optional HTTP headers for requests
- **test_articles**: Optional fallback content for testing/development

## CSS Selectors

The scraper uses CSS selectors to find content:

- **article_container**: Main container holding each article/post
- **title**: Article headline selector
- **description**: Article summary/content selector  
- **url**: Link to full article
- **image**: Article images
- **video**: Article videos

## Available Configurations

Current scraper configs in `scraper_configs/`:
- `ynet.json` - Ynet Israeli news (Hebrew)
- `rotter.json` - Rotter.net forums (Hebrew)
- `bbc_hebrew.json` - BBC Hebrew service
- `i24news.json` - i24 News (Hebrew/English)
- `www_mako_co_il.json` - Mako news (Hebrew)
- `www_sport5_co_il.json` - Sport5 (Hebrew sports)
- `test_media.json` - Test configuration with fallback content

## Usage Examples

### Add a new news website:
1. Create `scraper_configs/mynews.json` with the site configuration
2. Run: `python main.py news aggregate-enhanced mynews --platform tiktok`

### Use direct URL:
```bash
python main.py news aggregate-enhanced https://example.com/news --platform tiktok
```

### Multiple sources:
```bash
python main.py news aggregate-enhanced ynet rotter https://example.com --platform tiktok
```

### With Telegram channels:
```bash
python main.py news aggregate-enhanced \
  ynet \
  --telegram-channels @ynet_news \
  --telegram-channels @breaking_news \
  --platform tiktok
```

## Supported Source Types

- **News websites**: Any HTML website with article content
- **Telegram channels**: Public Telegram channel URLs or @handles
- **Instagram profiles**: Public Instagram profile URLs
- **Social media**: Twitter, Reddit, etc. (with appropriate selectors)
- **CSV files**: Bulk import of articles or media

## Creating a New Configuration

1. **Analyze the target website**: Inspect the HTML structure
2. **Identify selectors**: Find CSS selectors for articles, titles, etc.
3. **Create JSON config**: Save to `scraper_configs/your_site.json`
4. **Test with fallback**: Add `test_articles` for initial testing
5. **Verify scraping**: Run the aggregator with your config

## Debugging Tips

- Use `test_articles` to verify the system works before scraping
- Check logs in `outputs/session_*/logs/` for scraping errors
- Verify CSS selectors using browser developer tools
- Test with `--max-stories 5` to limit initial scraping

## Examples

### Hebrew News Site
```json
{
  "name": "Hebrew News",
  "base_url": "https://news.example.co.il",
  "language": "he",
  "selectors": {
    "article_container": ".news-item",
    "title": ".article-title",
    "description": ".article-summary",
    "url": "a.article-link",
    "image": ".article-image img"
  }
}
```

### English Tech Blog
```json
{
  "name": "Tech Blog",
  "base_url": "https://techblog.example.com",
  "language": "en",
  "selectors": {
    "article_container": "article.post",
    "title": "h2.post-title",
    "description": "div.post-excerpt",
    "url": "a.read-more",
    "image": "img.featured-image"
  }
}
```