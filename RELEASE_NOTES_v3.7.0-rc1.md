# Release Notes - v3.7.0-rc1

## 🎬 News Aggregator with Scraped Media Support

### Release Date: August 4, 2025

---

## 🚀 Major Features

### 1. **News Aggregator System - Scraped Media Only**
- ✅ Complete news aggregation system that uses ONLY scraped media
- ✅ NO VEO/AI video generation - 100% real content
- ✅ Professional broadcast-quality output

### 2. **Multi-Source News Scraping**
- ✅ **Ynet.co.il** - Israeli news with Hebrew content
- ✅ **BBC.com** - International news
- ✅ **CNN.com** - US news coverage
- ✅ **Reddit** - Sports fails and funny content
- ✅ **Pixabay/Pexels** - Additional media sources

### 3. **CSV Input Support**
- ✅ Articles CSV - Bulk news articles with media URLs
- ✅ Media CSV - Direct media file links
- ✅ Sources CSV - Multiple news sources for scraping
- ✅ Events CSV - Sports/conference summaries

### 4. **RTL Hebrew Support**
- ✅ Right-to-left Hebrew text rendering
- ✅ Proper Hebrew alignment in overlays
- ✅ Mixed Hebrew/English content support
- ✅ Hebrew news from Ynet properly displayed

### 5. **Professional Video Editing**
- ✅ FFmpeg-based video composition
- ✅ Zoom/pan effects on images
- ✅ Professional news overlay with:
  - Breaking news banner
  - Live indicator
  - News ticker
  - Source attribution
  - Location tags

---

## 📦 New Components

### Core Modules
- `src/news_aggregator/scrapers/`
  - `ynet_scraper.py` - Ynet.co.il scraper
  - `cnn_scraper.py` - CNN scraper
  - `bbc_scraper.py` - BBC scraper
  - `sports_scraper.py` - Reddit sports scraper
  - `social_media_scraper.py` - Social media scraper

- `src/news_aggregator/composers/`
  - `scraped_media_composer.py` - Creates videos using ONLY scraped media
  - `news_edition_composer.py` - AI agents for editorial decisions

- `src/news_aggregator/processors/`
  - `media_downloader.py` - Downloads and caches media
  - `content_analyzer.py` - Analyzes news content
  - `news_grouper.py` - Groups related stories

### CLI Commands
```bash
# Create news from scraped sources
python main.py news scraped https://www.ynet.co.il https://www.cnn.com

# Create news from CSV
python main.py news csv israeli_news_articles.csv --language he

# Create sports compilation
python main.py news sports --type funny --duration 20
```

---

## 🔧 Technical Improvements

### Architecture Changes
- Removed VEO dependency from news aggregator
- Implemented FFmpeg-only video composition
- Added media caching system
- Improved error handling for scraping

### Performance
- Parallel media downloads
- Efficient video processing pipeline
- Cached media reuse

### Quality
- Professional broadcast overlays
- HD 1920x1080 output
- Smooth transitions and effects

---

## 🐛 Bug Fixes

- Fixed Hebrew text rendering (RTL support)
- Fixed import errors in aggregation models
- Fixed async event loop issues
- Fixed media download SSL errors
- Fixed overlay transparency issues

---

## 📋 Requirements

### New Dependencies
```
aiohttp
beautifulsoup4
Pillow
certifi
arabic-reshaper (optional for advanced RTL)
python-bidi (optional for advanced RTL)
```

### System Requirements
- FFmpeg (for video processing)
- Python 3.8+
- Internet connection for scraping

---

## 🚨 Breaking Changes

- News aggregator no longer uses VEO generation
- All video content must come from scraped sources
- CSV format has been standardized (see examples)

---

## 📝 Migration Guide

For users upgrading from v3.6.x:

1. Update dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Use new commands for scraped media:
   ```bash
   # Old: python main.py news aggregate
   # New: python main.py news scraped
   ```

3. Prepare CSV files in new format (see `news_csv_demo.py`)

---

## 🎯 Known Issues

- Some news sites may block scraping (use rotating user agents)
- Video downloads from some sources require additional auth
- RTL rendering may vary based on system fonts

---

## 🔮 Future Enhancements

- YouTube video support
- More news sources (Reuters, AP)
- Advanced Hebrew NLP
- Real-time news updates
- Multi-language subtitles

---

## 🙏 Acknowledgments

Thanks to all contributors and testers who helped make this release possible.

---

**Full Changelog**: v3.6.0...v3.7.0-rc1