# News Aggregator Module

Automated news video creation system that scrapes content from news websites and generates professional news-style videos using existing ViralAI infrastructure.

## Features

### 🇮🇱 Israeli News Generator
- Scrapes content from Ynet and Rotter
- Selects top 5 most interesting/bizarre stories
- Adds dark humor commentary
- Features alien presenter "Zorg" in bottom-right
- Ynet-style graphics and overlays
- Hebrew/English bilingual support

### 🎨 Styles Available
- **dark_humor**: Sarcastic and cynical commentary (default)
- **professional**: Standard news presentation
- **satirical**: Political satire style
- **casual**: Relaxed, conversational tone

## Usage

### CLI Commands

```bash
# Generate Israeli news with dark humor and alien
python main.py news israeli --style dark_humor

# Professional style without alien
python main.py news israeli --style professional --no-alien

# Custom output filename
python main.py news israeli --output my_news_video.mp4

# Help
python main.py news israeli --help
```

### Python API

```python
from src.news_aggregator.israeli_news_generator import generate_israeli_news

# Generate with default settings
video_path = await generate_israeli_news()

# Custom settings
video_path = await generate_israeli_news(
    style="satirical",
    include_alien=True,
    output_filename="news_today.mp4"
)
```

## Architecture

The news aggregator integrates with existing ViralAI components:

1. **Scrapers** - Extract articles and media from news sites
2. **Content Processor** - Score and select interesting content
3. **Style Mapping** - Maps news styles to existing ViralAI styles/tones
4. **Alien Presenter** - Generates commentary using character system
5. **Theme System** - JSON-based visual customization
6. **Video Generation** - Uses existing VEO-3, TTS, and composition

## Content Selection Algorithm

Articles are scored based on:
- **Interest Score** (0-1): Media presence, recency, comments
- **Humor Score** (0-1): Keywords, bizarre factor, categories
- **Combined Score**: 60% interest + 40% humor

Top 5 articles are selected for the video.

## Alien Presenter: Zorg

- Name: זורג מכוכב קסם (Zorg from Planet Qesem)
- Position: Bottom-right corner (1720, 880)
- Size: 200x200 pixels
- Personality: Cynical observer of human behavior
- Special traits: Loves hummus, confused by Israeli bureaucracy

## Theme Configuration

Ynet-style theme includes:
- Primary color: #D40000 (Ynet red)
- Hebrew fonts with RTL support
- Logo positioning
- News ticker
- Lower third graphics

## Adding New Sources

1. Create scraper in `scrapers/` extending `WebNewsScraper`
2. Add site-specific selectors
3. Implement scoring logic
4. Register in main generator

## Testing

```bash
# Run tests
pytest tests/news_aggregator/

# Test specific component
pytest tests/news_aggregator/unit/test_web_scraper.py
```

## Assets Required

Place in `src/news_aggregator/assets/`:
- `overlays/ynet_logo.png`
- `overlays/ynet_lower_third.png`
- `audio/israeli_news_theme.mp3`

## Examples

See `example_israeli_news.py` for complete examples.

## Future Enhancements

- [ ] More news sources (Haaretz, Mako, etc.)
- [ ] Real-time ticker updates
- [ ] Weather integration
- [ ] Sports highlights
- [ ] Custom alien personalities
- [ ] Multiple presenter support