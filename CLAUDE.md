# ViralAI System Instructions

## Core Principles

### 1. Centralized Decision Framework
- ALL decisions must be made upfront via `DecisionFramework` before any generation
- No component should make its own decisions during generation
- Use `CoreDecisions` object to pass decisions to all components
- Always trace decision sources and reasoning

### 2. Session Management
- Every operation must be tracked in a session
- Use `SessionContext` for all file operations
- Maintain complete audit trail of all operations
- Save decisions, discussions, and artifacts to session directories

### 3. AI Agent System
- Use the 22-agent system for comprehensive discussions
- Professional mode: All 22 agents with 7 discussion topics
- Enhanced mode: 7 core agents with focused discussions
- Simple mode: Minimal AI for fast generation

### 4. Code Quality
- Always find the root cause for issues and make sure there are no linter errors
- Follow the centralized architecture patterns
- Use proper error handling and logging
- Maintain clean separation of concerns
- Always write the root cause of the issues and how the fix fixing it

### 5. Configuration System
- ALL hardcoded values must be moved to `src/config/video_config.py`
- Use configuration methods instead of hardcoding values
- Access configuration through the global `video_config` instance
- Platform-aware configuration is automatically applied
- Never hardcode: FPS, dimensions, font sizes, colors, text, durations

### 6. AI Provider System
- Use `AIServiceManager` to access AI services
- Never directly instantiate AI clients
- Always use the unified interface methods
- Handle provider-specific errors gracefully
- Support automatic fallback to alternative providers

### 7. News Aggregator System (NEW!)
- Use `EnhancedNewsAggregator` for news video creation
- Configure scrapers via JSON files in `scraper_configs/`
- Support multiple sources: web, Telegram, CSV
- Use `UniversalScraper` for configurable web scraping
- Always use real media when available (no AI generation)

### 8. Scraper Configuration
- Place scraper configs in `scraper_configs/` directory
- Use CSS selectors for content extraction
- Support fallback test content for development
- Handle multiple languages including RTL (Hebrew, Arabic)
- Cache downloaded media for efficiency

## Development Notes
- Never run no-cheap mode if you didnt run cheap mode first for verification
- When adding new scrapers, create JSON config instead of hardcoding
- Test with fallback content before using real sources
- Use the universal scraper for new sources

## News Aggregator Workflow
1. Configure sources in `scraper_configs/`
2. Run with `python main.py news aggregate-enhanced`
3. Specify sources: config names, URLs, or Telegram channels
4. System will scrape, analyze, and create video
5. Output includes professional overlays and transitions

[Rest of the existing content remains unchanged]