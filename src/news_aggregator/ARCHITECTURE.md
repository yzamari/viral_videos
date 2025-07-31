# News Aggregator Architecture - Simplified Approach

## Overview

The News Aggregator is a **separate tool** that leverages existing ViralAI components to create news compilation videos from web sources.

## Core Design Principles

1. **Modular Integration**: Use existing components (VEO-3, audio generation, subtitles) rather than reimplementing
2. **Simple Web Scraping**: Start with direct web links (BBC, Ynet, etc.) 
3. **Local Media Cache**: Store scraped media in organized local folders
4. **JSON Theme Config**: Easy-to-edit theme preferences
5. **Bilingual Support**: Hebrew and English from the start

## Architecture

```
news_aggregator/
├── scrapers/
│   └── web_scraper.py          # Extract articles + media from URLs
├── processors/
│   ├── content_analyzer.py     # Summarize, extract key points
│   └── media_extractor.py      # Download and process media
├── composers/
│   └── news_composer.py        # Create video using existing generators
├── themes/
│   └── theme_manager.py        # JSON-based theme system
├── integration/
│   └── viralai_bridge.py       # Interface with existing ViralAI components
└── storage/
    └── media_cache/            # Local storage for scraped media
```

## Integration Points with Existing ViralAI

### 1. Video Generation
```python
# Use existing VEO-3 fast generator
from src.ai.providers.veo_video_generation import VeoVideoGenerator
from src.infrastructure.services.existing_video_generation_service import ExistingVideoGenerationService
```

### 2. Audio Generation  
```python
# Use existing TTS services
from src.ai.providers.google_tts_service import GoogleTTSService
from src.infrastructure.services.existing_audio_generation_service import ExistingAudioGenerationService
```

### 3. Subtitle Generation
```python
# Use existing subtitle system
from src.generators.subtitle_generator import SubtitleGenerator
```

### 4. Session Management
```python
# Use existing session tracking
from src.utils.session_manager import SessionManager
```

## Workflow

1. **Input**: List of news URLs + theme config
2. **Scrape**: Extract articles and media from websites
3. **Analyze**: Summarize content, select key points
4. **Organize**: Group related stories, order by importance
5. **Generate**: 
   - Create script from summaries
   - Generate narrator audio (Hebrew/English)
   - Use existing media or generate with VEO-3
   - Add theme overlays and subtitles
6. **Output**: Professional news video

## Theme System (JSON)

```json
{
  "name": "Modern News Channel",
  "style": {
    "colors": {
      "primary": "#1E3A8A",
      "secondary": "#3B82F6",
      "text": "#FFFFFF",
      "background": "#000000"
    },
    "fonts": {
      "headline": {"family": "Arial", "size": 56},
      "subtitle": {"family": "Arial", "size": 32}
    },
    "logo": "themes/logos/news_logo.png",
    "overlays": {
      "lower_third": "themes/overlays/lower_third.png",
      "breaking_news": "themes/overlays/breaking.png"
    }
  },
  "layout": {
    "headline_position": {"x": 100, "y": 100},
    "ticker_enabled": true,
    "presenter_position": "bottom-right"
  },
  "audio": {
    "background_music": "themes/audio/news_theme.mp3",
    "volume": 0.3
  }
}
```

## Example Usage

```python
# Configure news channel
channel = NewsChannel(
    name="Daily Tech News",
    sources=[
        "https://www.bbc.com/news/technology",
        "https://www.ynet.co.il/digital"
    ],
    theme="themes/modern_news.json",
    languages=["en", "he"],
    schedule="daily_8am"
)

# Run aggregation
await channel.create_episode()
```

## Key Differences from Original Design

1. **Simpler Scope**: Focus on web scraping instead of multiple sources
2. **Reuse Components**: Leverage existing generators instead of building new ones
3. **Local First**: Simple local storage instead of complex cloud integration
4. **JSON Themes**: Easy configuration instead of complex theme engine
5. **Separate Tool**: Can run independently but uses ViralAI components

## Concerns & Solutions

### Concern 1: Code Duplication
**Solution**: Create thin integration layer that imports and uses existing components

### Concern 2: Media Quality
**Solution**: Prefer original media from articles, fallback to VEO-3 generation

### Concern 3: Hebrew Support
**Solution**: Use existing language detection and Google TTS with Hebrew support

### Concern 4: Scheduling Complexity
**Solution**: Start with simple cron-like scheduling, can enhance later