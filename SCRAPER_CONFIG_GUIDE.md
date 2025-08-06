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
  }
}
```

## Configuration Fields

- **name**: Display name for the source
- **base_url**: Main URL to scrape from  
- **language**: Content language code (en, he, ar, etc.)
- **selectors**: CSS selectors to find content elements
- **headers**: Optional HTTP headers for requests

## CSS Selectors

The scraper uses CSS selectors to find content:

- **article_container**: Main container holding each article/post
- **title**: Article headline selector
- **description**: Article summary/content selector  
- **url**: Link to full article
- **image**: Article images
- **video**: Article videos

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
python main.py news aggregate-enhanced source1 source2 https://example.com --platform tiktok
```

## Supported Source Types

- **News websites**: Any HTML website with article content
- **Telegram channels**: Public Telegram channel URLs  
- **Instagram profiles**: Public Instagram profile URLs
- **Social media**: Twitter, Reddit, etc. (with appropriate selectors)

## Examples

See `example_scraper_configs/` directory for sample configurations.