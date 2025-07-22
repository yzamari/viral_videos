# ViralAI v3.0 Feature Plan: Themed Sessions & Content Scraping

## Executive Summary

This document outlines the comprehensive plan for ViralAI v3.0, introducing two major feature sets:
1. **Referenced Style & Themed Sessions**: Enable consistent branding across multiple videos
2. **Content Scraping & Integration**: Leverage real-world content for enhanced video generation

All features will follow OOP principles, maintain backward compatibility, and include comprehensive testing.

## Table of Contents

1. [Referenced Style System](#1-referenced-style-system)
2. [Themed Session Management](#2-themed-session-management)
3. [Content Scraping Framework](#3-content-scraping-framework)
4. [Media Integration Pipeline](#4-media-integration-pipeline)
5. [Architecture Overview](#5-architecture-overview)
6. [Implementation Plan](#6-implementation-plan)
7. [Testing Strategy](#7-testing-strategy)
8. [Additional Feature Suggestions](#8-additional-feature-suggestions)

---

## 1. Referenced Style System

### Overview
Allow users to reference existing videos or define style templates for consistent visual appearance.

### Features

#### 1.1 Style Reference Engine
```python
# src/style_reference/
├── __init__.py
├── models/
│   ├── style_reference.py      # StyleReference dataclass
│   ├── style_template.py       # StyleTemplate model
│   └── style_attributes.py     # Detailed style attributes
├── analyzers/
│   ├── video_style_analyzer.py # Extract style from videos
│   ├── image_style_analyzer.py # Extract style from images
│   └── style_comparator.py     # Compare styles
├── managers/
│   ├── style_library.py        # Manage style templates
│   └── style_matcher.py        # Match styles to content
└── generators/
    ├── style_prompt_builder.py  # Build prompts with style
    └── style_transfer.py        # Apply style to content
```

#### 1.2 CLI Integration
```bash
# Reference a video style
python main.py generate --mission "..." --reference-style "path/to/video.mp4"

# Use a saved style template
python main.py generate --mission "..." --style-template "news-edition-v1"

# Save current style as template
python main.py save-style --session-id "..." --template-name "my-brand-style"
```

#### 1.3 Core Classes

```python
@dataclass
class StyleReference:
    """Represents a referenced style from video/image"""
    reference_type: ReferenceType  # VIDEO, IMAGE, TEMPLATE
    source_path: Optional[str]
    template_id: Optional[str]
    
    # Visual attributes
    color_palette: ColorPalette
    typography: Typography
    composition: Composition
    motion_style: MotionStyle
    visual_effects: List[VisualEffect]
    
    # Brand elements
    logo_placement: Optional[LogoPlacement]
    watermark: Optional[Watermark]
    lower_thirds: Optional[LowerThirds]
    
    # Technical details
    aspect_ratio: str
    resolution: str
    frame_rate: int
    
class VideoStyleAnalyzer:
    """Analyzes videos to extract style attributes"""
    
    async def analyze_video(self, video_path: str) -> StyleReference:
        """Extract comprehensive style from video"""
        # Use CV2/MoviePy for frame analysis
        # Use AI for style description
        # Extract color schemes, motion patterns
        
    async def analyze_frames(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Analyze sample frames for style elements"""
        
    def extract_color_palette(self, frames: List[np.ndarray]) -> ColorPalette:
        """Extract dominant colors and schemes"""
        
    def detect_typography(self, frames: List[np.ndarray]) -> Typography:
        """Detect text styles and fonts"""
```

---

## 2. Themed Session Management

### Overview
Create consistent video series with shared branding, style, and visual elements.

### Features

#### 2.1 Theme System Architecture
```python
# src/themes/
├── __init__.py
├── models/
│   ├── theme.py               # Theme dataclass
│   ├── theme_preset.py        # Pre-built themes
│   └── brand_kit.py           # Brand assets
├── managers/
│   ├── theme_manager.py       # Manage themes
│   ├── session_theme.py       # Apply themes to sessions
│   └── theme_validator.py     # Validate theme consistency
├── presets/
│   ├── news_edition.py        # News broadcast theme
│   ├── sports_highlights.py   # Sports theme
│   ├── tech_review.py         # Tech channel theme
│   └── gossip_show.py         # Entertainment theme
└── assets/
    ├── logos/
    ├── overlays/
    └── transitions/
```

#### 2.2 Theme Models

```python
@dataclass
class Theme:
    """Represents a complete theme configuration"""
    theme_id: str
    name: str
    category: ThemeCategory
    
    # Visual identity
    style_reference: StyleReference
    brand_kit: BrandKit
    
    # Content structure
    intro_template: VideoTemplate
    outro_template: VideoTemplate
    transition_style: TransitionStyle
    
    # Overlay configuration
    logo_config: LogoConfiguration
    lower_thirds_style: LowerThirdsStyle
    caption_style: CaptionStyle
    
    # Audio identity
    intro_music: Optional[str]
    background_music_style: str
    sound_effects_pack: str
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    version: str

@dataclass
class BrandKit:
    """Brand assets and guidelines"""
    primary_logo: str
    secondary_logo: Optional[str]
    color_primary: str
    color_secondary: str
    color_accent: str
    
    fonts: Dict[str, FontConfig]
    
    # Brand guidelines
    logo_safe_zones: List[Rectangle]
    minimum_logo_size: Size
    clear_space_ratio: float
    
class NewsEditionTheme(Theme):
    """Pre-configured news broadcast theme"""
    
    def __init__(self):
        super().__init__(
            theme_id="news-edition-v1",
            name="Professional News Edition",
            category=ThemeCategory.NEWS,
            # ... comprehensive news theme config
        )
```

#### 2.3 Session Theme Integration

```python
class ThemedSessionManager:
    """Manages themed video sessions"""
    
    def create_themed_session(
        self,
        theme: Theme,
        episode_number: int,
        episode_title: str
    ) -> ThemedSession:
        """Create a new themed session"""
        
    def apply_theme_to_config(
        self,
        config: GeneratedVideoConfig,
        theme: Theme
    ) -> GeneratedVideoConfig:
        """Apply theme settings to video config"""
        
    def ensure_brand_consistency(
        self,
        video_path: str,
        theme: Theme
    ) -> ValidationResult:
        """Validate brand guideline compliance"""
```

---

## 3. Content Scraping Framework

### Overview
Scrape and integrate real-world content from news, sports, and entertainment sources.

### Features

#### 3.1 Scraping Architecture
```python
# src/content_scraping/
├── __init__.py
├── scrapers/
│   ├── base_scraper.py        # Abstract scraper
│   ├── news_scraper.py        # News content
│   ├── sports_scraper.py      # Sports events
│   ├── gossip_scraper.py      # Entertainment news
│   ├── social_media_scraper.py # Social media trends
│   └── rss_scraper.py         # RSS feeds
├── extractors/
│   ├── text_extractor.py      # Extract article text
│   ├── image_extractor.py     # Extract images
│   ├── video_extractor.py     # Extract video clips
│   └── metadata_extractor.py  # Extract metadata
├── processors/
│   ├── content_filter.py      # Filter relevant content
│   ├── content_ranker.py      # Rank by relevance
│   └── content_summarizer.py  # Summarize content
└── storage/
    ├── content_cache.py        # Cache scraped content
    └── content_database.py     # Store processed content
```

#### 3.2 Core Scraping Classes

```python
class BaseScraper(ABC):
    """Abstract base class for all scrapers"""
    
    def __init__(self, config: ScraperConfig):
        self.config = config
        self.session = aiohttp.ClientSession()
        self.rate_limiter = RateLimiter(config.rate_limit)
        
    @abstractmethod
    async def scrape(self, query: str) -> List[ScrapedContent]:
        """Scrape content based on query"""
        
    @abstractmethod
    async def validate_source(self, url: str) -> bool:
        """Validate if source is reliable"""
        
    async def extract_content(self, url: str) -> ScrapedContent:
        """Extract content from URL"""
        
@dataclass
class ScrapedContent:
    """Represents scraped content"""
    source_url: str
    source_name: str
    content_type: ContentType
    
    # Content
    title: str
    text: str
    summary: Optional[str]
    
    # Media
    images: List[ScrapedImage]
    videos: List[ScrapedVideo]
    
    # Metadata
    author: Optional[str]
    publish_date: datetime
    tags: List[str]
    credibility_score: float
    
    # Legal
    license: Optional[str]
    attribution_required: bool

class NewsAggregator:
    """Aggregates news from multiple sources"""
    
    def __init__(self):
        self.scrapers = [
            ReutersScraper(),
            APNewsScraper(),
            BBCScraper(),
            CNNScraper(),
            CustomRSSScraper()
        ]
        
    async def get_trending_news(
        self,
        category: str,
        limit: int = 10
    ) -> List[ScrapedContent]:
        """Get trending news from all sources"""
        
    async def search_news(
        self,
        query: str,
        date_range: DateRange
    ) -> List[ScrapedContent]:
        """Search news across sources"""
```

#### 3.3 Content Processors

```python
class ContentSummarizer:
    """Summarizes scraped content for video scripts"""
    
    async def summarize_for_video(
        self,
        content: ScrapedContent,
        duration: int,
        style: str
    ) -> VideoContentSummary:
        """Create video-ready summary"""
        
class FactChecker:
    """Verifies content accuracy"""
    
    async def verify_facts(
        self,
        content: ScrapedContent
    ) -> FactCheckResult:
        """Cross-reference facts"""
        
class ContentFilter:
    """Filters content for relevance and safety"""
    
    def filter_inappropriate(
        self,
        content: List[ScrapedContent]
    ) -> List[ScrapedContent]:
        """Remove inappropriate content"""
        
    def filter_by_relevance(
        self,
        content: List[ScrapedContent],
        topic: str
    ) -> List[ScrapedContent]:
        """Filter by topic relevance"""
```

---

## 4. Media Integration Pipeline

### Overview
Integrate scraped media (images, videos) into video generation as backgrounds, overlays, and visual elements.

### Features

#### 4.1 Media Integration Architecture
```python
# src/media_integration/
├── __init__.py
├── processors/
│   ├── image_processor.py     # Process scraped images
│   ├── video_processor.py     # Process video clips
│   └── media_optimizer.py     # Optimize for generation
├── composers/
│   ├── background_composer.py # Use media as backgrounds
│   ├── overlay_composer.py    # Create overlays
│   └── pip_composer.py        # Picture-in-picture
├── validators/
│   ├── copyright_validator.py # Check usage rights
│   ├── quality_validator.py   # Ensure quality
│   └── content_validator.py   # Check appropriateness
└── effects/
    ├── blur_background.py      # Blur for focus
    ├── ken_burns.py           # Pan/zoom effects
    └── transitions.py         # Media transitions
```

#### 4.2 Media Integration Classes

```python
class MediaIntegrator:
    """Integrates external media into video generation"""
    
    async def integrate_background(
        self,
        video_config: GeneratedVideoConfig,
        media_source: ScrapedContent
    ) -> GeneratedVideoConfig:
        """Use scraped media as video background"""
        
    async def create_pip_overlay(
        self,
        main_video: str,
        pip_content: ScrapedVideo,
        position: PIPPosition
    ) -> str:
        """Add picture-in-picture overlay"""
        
    async def generate_with_real_footage(
        self,
        script_segments: List[Dict],
        media_library: List[ScrapedContent]
    ) -> List[str]:
        """Generate video using real footage"""

class SmartMediaSelector:
    """Intelligently selects media for video segments"""
    
    async def select_media_for_segment(
        self,
        segment: Dict[str, Any],
        available_media: List[ScrapedContent]
    ) -> SelectedMedia:
        """AI-powered media selection"""
        
    def match_media_to_script(
        self,
        script: str,
        media: ScrapedContent
    ) -> float:
        """Calculate relevance score"""
```

#### 4.3 Background Integration

```python
class BackgroundComposer:
    """Composes videos with scraped backgrounds"""
    
    async def compose_with_background(
        self,
        foreground_elements: List[VideoElement],
        background_media: Union[ScrapedImage, ScrapedVideo],
        effects: List[BackgroundEffect]
    ) -> str:
        """Compose video with background"""
        
    def apply_blur_effect(
        self,
        background: str,
        blur_amount: float
    ) -> str:
        """Apply blur for depth"""
        
    def apply_color_overlay(
        self,
        background: str,
        color: str,
        opacity: float
    ) -> str:
        """Apply color overlay"""
```

---

## 5. Architecture Overview

### 5.1 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        ViralAI v3.0                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────┐ │
│  │  Style System   │  │  Theme System   │  │  Scraping  │ │
│  │                 │  │                 │  │   System   │ │
│  │ • Style Ref     │  │ • Theme Manager │  │ • Scrapers │ │
│  │ • Style Library │  │ • Brand Kits    │  │ • Extract  │ │
│  │ • Style Match   │  │ • Presets       │  │ • Process  │ │
│  └────────┬────────┘  └────────┬────────┘  └─────┬──────┘ │
│           │                    │                   │        │
│  ┌────────▼─────────────────────▼─────────────────▼──────┐ │
│  │              Integration Layer                         │ │
│  │  • Media Pipeline  • Content Processor  • AI Agents   │ │
│  └────────────────────────┬──────────────────────────────┘ │
│                           │                                 │
│  ┌────────────────────────▼──────────────────────────────┐ │
│  │              Core Video Generation                     │ │
│  │  • Decision Framework  • Video Generator  • Composers  │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Data Flow

```
User Input → Style/Theme Selection → Content Scraping
    ↓              ↓                      ↓
CLI Parser → Style Analyzer → Content Aggregator
    ↓              ↓                      ↓
Config Builder ← Style Config ← Media Library
    ↓
Core Decisions (with style/theme/media)
    ↓
Video Generation Pipeline
    ↓
Final Video (with consistent style/theme)
```

### 5.3 Database Schema

```sql
-- Style templates table
CREATE TABLE style_templates (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50),
    style_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Themes table
CREATE TABLE themes (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    style_template_id UUID REFERENCES style_templates(id),
    brand_kit JSONB NOT NULL,
    config JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Scraped content table
CREATE TABLE scraped_content (
    id UUID PRIMARY KEY,
    source_url TEXT NOT NULL,
    content_type VARCHAR(50),
    title TEXT,
    content TEXT,
    media_urls JSONB,
    metadata JSONB,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

-- Theme sessions table
CREATE TABLE theme_sessions (
    id UUID PRIMARY KEY,
    theme_id UUID REFERENCES themes(id),
    session_id VARCHAR(255),
    episode_number INTEGER,
    episode_title TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 6. Implementation Plan

### Phase 1: Foundation (Weeks 1-2)
1. **Create base architecture**
   - Set up new package structure
   - Create abstract base classes
   - Define interfaces and protocols

2. **Implement Style Reference System**
   - Video style analyzer
   - Style template storage
   - Basic style matching

### Phase 2: Theme System (Weeks 3-4)
1. **Build Theme Framework**
   - Theme models and presets
   - Brand kit management
   - Theme application logic

2. **Create Initial Presets**
   - News Edition theme
   - Sports Highlights theme
   - Tech Review theme

### Phase 3: Content Scraping (Weeks 5-6)
1. **Implement Scrapers**
   - News scraper (RSS + web)
   - Sports event scraper
   - Social media trend scraper

2. **Content Processing**
   - Summarization pipeline
   - Fact checking integration
   - Content filtering

### Phase 4: Media Integration (Weeks 7-8)
1. **Media Pipeline**
   - Image/video processors
   - Background composers
   - Overlay system

2. **Smart Selection**
   - AI media matching
   - Copyright validation
   - Quality assurance

### Phase 5: Integration & Testing (Weeks 9-10)
1. **System Integration**
   - Connect all components
   - Update CLI interface
   - Backward compatibility

2. **Comprehensive Testing**
   - Unit tests
   - Integration tests
   - Performance testing

---

## 7. Testing Strategy

### 7.1 Unit Tests

```python
# tests/unit/style_reference/test_video_analyzer.py
class TestVideoStyleAnalyzer:
    def test_extract_color_palette(self):
        """Test color extraction from video"""
        
    def test_detect_typography(self):
        """Test font detection"""
        
    def test_analyze_composition(self):
        """Test composition analysis"""

# tests/unit/scrapers/test_news_scraper.py
class TestNewsScraper:
    def test_scrape_article(self):
        """Test article scraping"""
        
    def test_extract_images(self):
        """Test image extraction"""
        
    def test_rate_limiting(self):
        """Test rate limit compliance"""
```

### 7.2 Integration Tests

```python
# tests/integration/test_themed_generation.py
class TestThemedVideoGeneration:
    async def test_news_theme_generation(self):
        """Test complete news-themed video"""
        
    async def test_style_consistency(self):
        """Test style consistency across clips"""
        
    async def test_brand_compliance(self):
        """Test brand guideline compliance"""

# tests/integration/test_scraped_content.py
class TestScrapedContentIntegration:
    async def test_news_to_video_pipeline(self):
        """Test news scraping to video"""
        
    async def test_media_background_integration(self):
        """Test using scraped media as background"""
```

### 7.3 Performance Tests

```python
# tests/performance/test_scraping_performance.py
class TestScrapingPerformance:
    def test_concurrent_scraping(self):
        """Test multiple scrapers concurrently"""
        
    def test_large_media_processing(self):
        """Test processing large media files"""
        
    def test_cache_effectiveness(self):
        """Test content cache performance"""
```

---

## 8. Additional Feature Suggestions

### 8.1 AI-Powered Features

#### Auto-Documentary Generator
```python
class DocumentaryGenerator:
    """Generates documentaries from scraped content"""
    
    async def generate_documentary(
        self,
        topic: str,
        duration: int,
        style: DocumentaryStyle
    ) -> str:
        """Auto-generate documentary from research"""
```

#### Trend Predictor
```python
class TrendPredictor:
    """Predicts viral content trends"""
    
    async def predict_viral_potential(
        self,
        content: GeneratedVideoConfig
    ) -> ViralScore:
        """Predict viral potential"""
```

### 8.2 Advanced Integrations

#### Live Stream Integration
```python
class LiveStreamIntegrator:
    """Integrate with live streaming platforms"""
    
    async def stream_to_platform(
        self,
        video_path: str,
        platform: StreamPlatform
    ) -> StreamResult:
        """Stream video live"""
```

#### Multi-Platform Optimizer
```python
class MultiPlatformOptimizer:
    """Optimize same content for multiple platforms"""
    
    async def optimize_for_platforms(
        self,
        base_video: str,
        platforms: List[Platform]
    ) -> Dict[Platform, str]:
        """Create platform-specific versions"""
```

### 8.3 Analytics & Insights

#### Performance Analytics
```python
class VideoAnalytics:
    """Track video performance across platforms"""
    
    async def track_performance(
        self,
        video_id: str,
        platform: Platform
    ) -> PerformanceMetrics:
        """Track views, engagement, etc."""
```

#### A/B Testing Framework
```python
class ABTestingFramework:
    """A/B test different video variations"""
    
    async def create_test_variants(
        self,
        base_config: GeneratedVideoConfig,
        variables: List[TestVariable]
    ) -> List[str]:
        """Create test variants"""
```

### 8.4 Collaboration Features

#### Team Workspace
```python
class TeamWorkspace:
    """Collaborative video creation"""
    
    async def create_shared_project(
        self,
        team_id: str,
        project_config: ProjectConfig
    ) -> SharedProject:
        """Create collaborative project"""
```

#### Version Control
```python
class VideoVersionControl:
    """Git-like version control for videos"""
    
    async def commit_version(
        self,
        video_path: str,
        message: str
    ) -> CommitHash:
        """Commit video version"""
```

---

## Conclusion

This comprehensive plan introduces powerful new features while maintaining the system's core strengths:

1. **Referenced Styles** enable consistent branding
2. **Themed Sessions** create professional video series
3. **Content Scraping** provides real-world relevance
4. **Media Integration** enhances visual quality

All features follow OOP principles, maintain backward compatibility, and include thorough testing. The modular architecture ensures easy maintenance and future expansion.

The implementation timeline of 10 weeks allows for careful development and testing of each component, ensuring a robust and professional v3.0 release.