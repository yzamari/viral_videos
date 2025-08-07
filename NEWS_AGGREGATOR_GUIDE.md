# News Aggregator Complete Guide

## Overview
The Enhanced News Aggregator is a powerful system that scrapes news from multiple sources, processes them with AI, and creates professional news videos with overlays, transitions, and multi-language support.

## Key Features
- 🌐 **Multi-source scraping** with Playwright for JavaScript-heavy sites
- 📊 **CSV import/export** for batch processing
- 🎭 **AI-powered content selection** with 22-agent discussion system
- 🎬 **Professional video creation** with news overlays
- 🌍 **Multi-language support** including RTL languages
- 📱 **Platform optimization** (YouTube, TikTok, Instagram)
- 🔗 **Link-following** to extract media from embedded links
- 📸 **Real media usage** - no AI generation, only scraped content

## Quick Start

### Basic Command
```bash
python3 main.py news aggregate-enhanced [sources] [options]
```

### Example Commands

#### 1. Scrape from websites with Playwright
```bash
python3 main.py news aggregate-enhanced rotter timesofisrael cnn \
  --duration 60 \
  --platform youtube \
  --max-stories 10
```

#### 2. Import from CSV
```bash
python3 main.py news aggregate-enhanced test_demo \
  --csv sample_news.csv \
  --duration 40 \
  --platform instagram \
  --max-stories 100
```

#### 3. Multi-language output
```bash
python3 main.py news aggregate-enhanced ynet \
  --languages he --languages en --languages ru \
  --duration 90 \
  --platform tiktok
```

#### 4. Custom style and tone
```bash
python3 main.py news aggregate-enhanced https://www.bbc.com \
  --style "viral breaking news" \
  --tone "sarcastic dark humor" \
  --channel-name "BREAKING NEWS 24/7"
```

## CSV Format

### Input CSV Structure
```csv
title,content,source,url,category,media_links,priority,ai_reasoning
"Breaking News Title","Full article content","SourceName","https://example.com","technology","https://image1.jpg,https://image2.jpg",0.9,"High impact story"
```

### Fields Explanation
- **title**: Article headline
- **content**: Full article text
- **source**: Source name/website
- **url**: Article URL
- **category**: Content category (technology, sports, etc.)
- **media_links**: Comma-separated list of image/video URLs
- **priority**: 0-1 score for importance
- **ai_reasoning**: Why this story matters

### Output CSV
Every run automatically generates `outputs/session_[timestamp]/scraped_articles.csv` containing all processed articles.

## Scraper Configuration

### Adding New Sources
Create a JSON file in `scraper_configs/` directory:

```json
{
  "name": "Site Name",
  "base_url": "https://example.com",
  "language": "en",
  "selectors": {
    "article_container": "article, div.news-item",
    "title": "h1, h2",
    "url": "a[href]",
    "description": "p",
    "image": "img",
    "video": "video"
  },
  "force_playwright": true,
  "follow_embedded_links": true,
  "max_link_depth": 1
}
```

### Pre-configured Sources
- **Hebrew**: ynet, rotter, timesofisrael, i24news
- **English**: cnn, bbc, guardian, reuters, nytimes
- **Demo**: test_demo (with fallback content)

## Advanced Features

### Playwright Support
Sites requiring JavaScript rendering are automatically detected and processed with Playwright:
- Rotter.net
- Times of Israel
- Ynet
- CNN
- BBC

### Link Following
Extracts media from linked articles:
```json
{
  "follow_embedded_links": true,
  "max_link_depth": 1,
  "max_links_to_follow": 3
}
```

### AI Discussion System
Enable comprehensive AI agent discussions:
```bash
--discussion-log  # Saves AI discussion to file
--max-stories 10  # AI selects top stories
```

## Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `--csv FILE` | Import articles from CSV | None |
| `--languages LANG` | Output languages (can repeat) | en |
| `--duration SECONDS` | Video duration | 60 |
| `--platform PLATFORM` | youtube/tiktok/instagram | youtube |
| `--max-stories NUM` | Maximum stories to include | 10 |
| `--style TEXT` | Visual style description | professional |
| `--tone TEXT` | Content tone | informative |
| `--channel-name TEXT` | Channel name overlay | NEWS |
| `--overlay-style STYLE` | Overlay style (modern/minimal) | minimal |
| `--discussion-log` | Save AI discussion | False |
| `--output-dir PATH` | Output directory | outputs/[session] |

## Platform Specifications

### YouTube
- Aspect ratio: 16:9
- Duration: 60-90 seconds recommended
- Overlays: Full news graphics

### Instagram
- Aspect ratio: 9:16 (vertical)
- Duration: 30-60 seconds
- Optimized for mobile viewing

### TikTok
- Aspect ratio: 9:16 (vertical)
- Duration: 15-60 seconds
- Fast-paced transitions

## Troubleshooting

### Site Not Accessible
- Check if Playwright browsers are installed: `python3 -m playwright install chromium`
- Use fallback content in scraper config
- Try with direct URL instead of config name

### No Media in Video
- Verify media URLs are accessible
- Check `outputs/news_media_cache/` for downloaded files
- Ensure SSL certificates are valid

### CSV Import Issues
- Verify CSV encoding is UTF-8
- Check media_links are comma-separated
- Ensure required fields are present

## Examples

### News Broadcast Style
```bash
python3 main.py news aggregate-enhanced cnn bbc reuters \
  --style "professional news broadcast" \
  --tone "authoritative" \
  --duration 90 \
  --channel-name "WORLD NEWS NETWORK"
```

### Viral Social Media
```bash
python3 main.py news aggregate-enhanced test_demo \
  --csv trending_news.csv \
  --style "viral breaking news" \
  --tone "exciting and urgent" \
  --platform tiktok \
  --duration 30
```

### Multi-Language News
```bash
python3 main.py news aggregate-enhanced ynet bbc \
  --languages he --languages en --languages ar \
  --duration 60 \
  --max-stories 5
```

## Output Files

Each session creates:
- `news_[language]_[platform]_[timestamp].mp4` - Final video
- `scraped_articles.csv` - All articles with media links
- `news_aggregation_report.json` - Session summary
- `ai_discussion_log.json` - AI agent discussions (if enabled)

## Best Practices

1. **Use CSV for batch processing** - Prepare multiple articles offline
2. **Enable Playwright for modern sites** - Better scraping success
3. **Provide media URLs** - Ensures visual content in videos
4. **Test with fallback content** - Verify pipeline before live scraping
5. **Export CSV for reuse** - Build article database over time

## API Integration

The system can be integrated programmatically:

```python
from src.news_aggregator.enhanced_aggregator import create_enhanced_news_edition

await create_enhanced_news_edition(
    sources=['cnn', 'bbc'],
    csv_file='articles.csv',
    languages=['en'],
    platform='youtube',
    duration_seconds=60,
    max_stories=10
)
```