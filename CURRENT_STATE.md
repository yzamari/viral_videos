# ViralAI Current State - v3.7.0-rc1

## System Overview
ViralAI is a production-ready AI video generation system with two main capabilities:
1. **Generate Command**: Create AI-powered videos with generated visuals
2. **News Command**: Aggregate real media from web/Telegram sources

## ✅ Working Features

### Core Systems
- **22+ AI Agents**: Professional collaborative video creation
- **VEO-2/3 Integration**: Google's advanced video generation
- **Universal Scraper**: Configure any website with JSON
- **Telegram Integration**: Direct channel scraping with media
- **Multi-Language**: 40+ languages including RTL (Hebrew, Arabic)
- **Character Consistency**: Persistent characters across episodes
- **Real Trending Data**: YouTube, TikTok, Instagram APIs
- **Social Media Posting**: Auto-post to all major platforms

### Video Generation
- AI-generated videos with VEO-2/3
- Real media aggregation (no AI generation)
- Professional overlays and transitions
- Multiple output versions (final, clean, overlays)
- 100+ visual styles
- Platform-specific optimization

### Configuration
- Zero hardcoding - all values configurable
- JSON-based scraper configuration
- Theme system with presets
- Style templates and references
- Universal AI provider interface

## 📁 Project Structure

### Main Commands
- `python main.py generate` - Create AI videos
- `python main.py news` - Aggregate news content

### Key Directories
- `src/` - Core source code
- `scraper_configs/` - Website scraper configurations
- `outputs/` - Generated videos and sessions
- `docs/` - User documentation
- `tests/` - Test suite

### Configuration Files
- `scraper_configs/*.json` - Website configurations
- `src/config/video_config.py` - Video generation settings
- `.env` - API keys and credentials
- `CLAUDE.md` - System instructions

## 🔧 Current Configuration

### Available Scrapers
- ynet.json - Israeli news
- rotter.json - Forums
- bbc_hebrew.json - BBC Hebrew
- i24news.json - International news
- test_media.json - Development testing

### Supported Platforms
- Instagram (9:16)
- TikTok (9:16)
- YouTube (16:9)
- Twitter (16:9)
- LinkedIn (16:9)

## 📚 Documentation

### Essential Guides
- [README.md](README.md) - Main documentation
- [TELEGRAM_QUICK_START.md](TELEGRAM_QUICK_START.md) - Telegram setup
- [SCRAPER_CONFIG_GUIDE.md](SCRAPER_CONFIG_GUIDE.md) - Add new sources
- [docs/SERIES_CREATION_GUIDE.md](docs/SERIES_CREATION_GUIDE.md) - Create series
- [docs/CHARACTER_CONSISTENCY_GUIDE.md](docs/CHARACTER_CONSISTENCY_GUIDE.md) - Character system

## 🚀 Quick Start

### Generate AI Video
```bash
python main.py generate \
  --mission "Your creative brief" \
  --platform instagram \
  --duration 30
```

### Aggregate News
```bash
python main.py news aggregate-enhanced \
  ynet rotter \
  --telegram-channels @breaking_news \
  --platform tiktok \
  --duration 60
```

### Add New Source
1. Create `scraper_configs/your_site.json`
2. Run: `python main.py news aggregate-enhanced your_site`

## 🔑 Key Principles
1. **Centralized Decisions**: All decisions made upfront
2. **Session Management**: Complete tracking and audit
3. **No Hardcoding**: Everything configurable
4. **Real Media Priority**: Use actual content when available
5. **Multi-Source Support**: Web, Telegram, CSV, APIs

## 📊 Status
- **Version**: 3.7.0-rc1
- **Status**: Production Ready
- **Last Updated**: August 2025
- **Python**: 3.8+
- **Main Dependencies**: Google Cloud AI, Telethon, BeautifulSoup4