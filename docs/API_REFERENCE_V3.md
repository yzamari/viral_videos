# ViralAI v3.0 API Reference

## CLI Commands

### Creating Consistent Series

#### Character-Based Series (TRUE Consistency!)

##### **🔥 Complete Series Scripts**

```bash
# Iranian Dark Comedy Series (4 episodes) - Persian humor
./create_iranian_comedy_water_crisis_series.sh

# Professional Iran Water Crisis (4 episodes) - Serious tone  
./create_iran_water_crisis_series.sh

# Character-based news series (2 episodes) - General approach
./create_character_news_series.sh
```

##### **🎯 Step-by-Step Character Series Creation**

```bash
# PHASE 1: System Setup (one time)
./setup_character_system.sh

# PHASE 2: Create Characters
# Option A: Iranian characters (recommended)
python main.py create-iranian-anchors
# Creates: Leila Hosseini (hijab), Leila Hosseini (no hijab), Ahmad Rezaei

# Option B: American characters
python main.py create-news-anchors  
# Creates: Sarah Chen, Michael Rodriguez

# Option C: Custom character
python main.py store-character photo.jpg --name "Custom Anchor"

# PHASE 3: Generate Series with SAME Character
# Episode 1
python main.py generate \
  --mission "Breaking news about Iran water crisis with Iranian anchor" \
  --character leila_hosseini \
  --scene "professional Iranian news studio" \
  --platform youtube \
  --duration 60 \
  --theme preset_news_edition \
  --no-cheap \
  --continuous \
  --session-id "series_ep1"

# Episode 2 (SAME CHARACTER - 100% consistency!)
python main.py generate \
  --mission "Follow-up report by SAME anchor on government response" \
  --character leila_hosseini \
  --scene "same Iranian news studio" \
  --platform youtube \
  --duration 60 \
  --theme preset_news_edition \
  --no-cheap \
  --continuous \
  --session-id "series_ep2"

# Episode 3 (Character Transformation!)
python main.py generate \
  --mission "Powerful moment - same anchor now appears without hijab" \
  --character leila_hosseini_no_hijab \
  --scene "same studio, more intimate lighting" \
  --platform youtube \
  --duration 60 \
  --theme preset_news_edition \
  --no-cheap \
  --continuous \
  --session-id "series_ep3"
```

##### **💫 Advanced Character Features**

```bash
# Character Transformation Series
python main.py generate \
  --mission "Traditional coverage" \
  --character leila_hosseini \
  --duration 60

python main.py generate \
  --mission "Same person, evolved perspective" \
  --character leila_hosseini_no_hijab \
  --duration 60

# Multiple Character Episode
python main.py generate \
  --mission "Male anchor covers protests" \
  --character ahmad_rezaei \
  --scene "studio with protest footage backgrounds" \
  --duration 60

# Comedy Series with Characters
python main.py generate \
  --mission "Satirical news with Persian humor for Iranian audience" \
  --character leila_hosseini \
  --tone humorous \
  --style comedy \
  --target-audience "Iranian comedy fans" \
  --duration 60
```

#### Voice-Over Series (Reliable Alternative)

```bash
# Professional News Series (Voice-Over Approach)
./create_news_series_fixed.sh  # Working script

# Manual Voice-Over Approach
python main.py generate \
  --mission "Professional news broadcast. Female narrator voice-over. Show maps, footage, graphics. No faces. Topic: [YOUR STORY]" \
  --platform youtube \
  --duration 50 \
  --theme preset_news_edition \
  --visual-style documentary \
  --no-cheap \
  --continuous
```

### Video Generation with Themes and Styles

```bash
# Generate with theme
python main.py generate \
  --mission "Your content mission" \
  --platform instagram \
  --duration 30 \
  --theme preset_news_edition

# Generate with style template
python main.py generate \
  --mission "Your content mission" \
  --platform youtube \
  --duration 60 \
  --style-template "Corporate Style"

# Generate with reference video style
python main.py generate \
  --mission "Your content mission" \
  --platform tiktok \
  --duration 15 \
  --reference-style /path/to/reference.mp4
```

### Style Management Commands

```bash
# Analyze and save style from video
python main.py analyze-style <video_path> \
  --name "Style Name" \
  --save \
  --tags "tag1,tag2" \
  --description "Style description"

# List available styles
python main.py list-styles [--query "search term"] [--tags "tag1,tag2"]

# Delete a style template
python main.py delete-style <template_id>

# List preset styles
python main.py list-presets
```

### Character Management Commands

```bash
# Store character reference image
python main.py store-character <image_path> --name "Character Name" [--description "Description"]

# List all stored characters
python main.py list-characters

# Generate character in new scene
python main.py generate-character-scene <character_id> <scene_description> [--output <path>]

# Delete character reference
python main.py delete-character <character_id>

# Create professional news anchors automatically
python main.py create-news-anchors

# Test character reference system
python main.py test-character-system
```

### Theme Management Commands

```bash
# List all themes
python main.py list-themes [--category news|sports|tech|entertainment|custom]

# Get theme details
python main.py theme-info <theme_id>

# Export theme
python main.py export-theme <theme_id> <output_path>

# Import theme
python main.py import-theme <theme_file> [--name "New Name"]

# Delete custom theme
python main.py delete-theme <theme_id>
```

## Style Reference System

### VideoStyleAnalyzer

Analyzes videos to extract visual style attributes.

```python
from src.style_reference.analyzers.video_style_analyzer import VideoStyleAnalyzer

analyzer = VideoStyleAnalyzer()
style_ref = await analyzer.analyze_video("/path/to/video.mp4", "My Style")
```

#### Methods

**analyze_video(video_path: str, name: str) -> StyleReference**
- Extracts comprehensive style from video
- Returns StyleReference object with color, typography, motion attributes

**analyze_image(image_path: str, name: str) -> StyleReference**
- Extracts style from static image
- Returns partial StyleReference (no motion data)

### StyleLibrary

Manages saved style references.

```python
from src.style_reference.managers.style_library import StyleLibrary

library = StyleLibrary()
template_id = library.save_style(style_ref, "Brand Style", tags=["corporate"])
```

#### Methods

**save_style(style: StyleReference, name: str, tags: List[str], description: str) -> str**
- Saves style as reusable template
- Returns template ID

**load_style(template_id: str) -> StyleReference**
- Loads style by ID

**search_styles(query: str, tags: List[str]) -> List[Dict]**
- Search styles by name, description, or tags

**get_preset_styles() -> List[Dict]**
- Returns built-in style presets

### StylePromptBuilder

Converts style references to generation prompts.

```python
from src.style_reference.builders.style_prompt_builder import StylePromptBuilder

builder = StylePromptBuilder()
prompts = builder.build_prompts(style_ref, content_type="product_showcase")
```

## Theme System

### Theme Model

Represents a complete visual theme with branding.

```python
from src.themes.models.theme import Theme, ThemeCategory, BrandKit

theme = Theme(
    name="My Brand Theme",
    category=ThemeCategory.BUSINESS,
    brand_kit=BrandKit(
        primary_logo="logo.png",
        color_primary="#FF0000"
    )
)
```

### ThemeManager

Manages theme storage and retrieval.

```python
from src.themes.managers.theme_manager import ThemeManager

manager = ThemeManager()
theme_id = manager.save_theme(theme)
```

#### Methods

**save_theme(theme: Theme, overwrite: bool) -> str**
- Saves custom theme
- Returns theme ID

**load_theme(theme_id: str) -> Theme**
- Loads theme by ID

**list_themes(category: ThemeCategory) -> List[Dict]**
- Lists available themes

**duplicate_theme(theme_id: str, new_name: str) -> str**
- Creates copy of existing theme

**export_theme(theme_id: str, output_path: str) -> bool**
- Exports theme for sharing

**import_theme(import_path: str, new_name: str) -> str**
- Imports theme from file

### ThemedSessionManager

Creates video sessions with consistent themes.

```python
from src.themes.managers.themed_session_manager import ThemedSessionManager

themed_manager = ThemedSessionManager(theme_manager, session_manager)
session = themed_manager.create_themed_session("preset_news_edition")
```

#### Methods

**create_themed_session(theme_id: str, session_name: str, override_settings: Dict) -> SessionContext**
- Creates new session with theme

**generate_with_theme(theme_id: str, mission: str, params: Dict) -> SessionContext**
- Generates video with theme

**create_series_session(theme_id: str, series_name: str, episode_count: int) -> List[SessionContext]**
- Creates multiple episodes with same theme

## Content Scraping Framework (Coming Soon)

### ContentScraper

Base class for content scrapers.

```python
from src.scraping.scrapers.base_scraper import ContentScraper

class NewsPortalScraper(ContentScraper):
    def scrape(self, url: str) -> ScrapedContent:
        # Implementation
        pass
```

### ScraperFactory

Creates appropriate scraper for content source.

```python
from src.scraping.factory import ScraperFactory

factory = ScraperFactory()
scraper = factory.get_scraper("https://news.example.com/feed")
content = scraper.scrape()
```

## Media Integration Pipeline (Coming Soon)

### MediaProcessor

Processes external media for video integration.

```python
from src.media_integration.processors.media_processor import MediaProcessor

processor = MediaProcessor()
processed = processor.process_image(image_path, target_size=(1920, 1080))
```

### MediaComposer

Integrates external media into video generation.

```python
from src.media_integration.composers.media_composer import MediaComposer

composer = MediaComposer()
video = composer.compose_with_media(script_segments, media_assets)
```

## Integration Examples

### Using Style Reference in Generation

```python
# Extract style from reference video
analyzer = VideoStyleAnalyzer()
style = await analyzer.analyze_video("reference.mp4", "Brand Style")

# Save for reuse
library = StyleLibrary()
style_id = library.save_style(style, "Corporate 2024")

# Use in generation
decisions = DecisionFramework()
decisions.set_style_reference(style_id)
```

### Creating Themed Series

```python
# Initialize managers
theme_mgr = ThemeManager()
session_mgr = SessionManager()
themed_mgr = ThemedSessionManager(theme_mgr, session_mgr)

# Create news series
sessions = themed_mgr.create_series_session(
    "preset_news_edition",
    "Tech News Weekly",
    episode_count=10
)

# Generate each episode
for i, session in enumerate(sessions):
    themed_mgr.generate_with_theme(
        "preset_news_edition",
        f"This week in tech: Episode {i+1}",
        {"duration": 60}
    )
```

### Custom Theme Creation

```python
from src.themes.models.theme import (
    Theme, BrandKit, LogoConfiguration,
    LowerThirdsStyle, VideoTemplate
)

# Create brand kit
brand = BrandKit(
    primary_logo="assets/logo.png",
    color_primary="#1E88E5",
    fonts={"heading": "Roboto", "body": "Open Sans"}
)

# Create intro template
intro = VideoTemplate(
    template_id="custom_intro",
    duration=3.0,
    title_text="ACME CORP",
    music_path="assets/intro.mp3"
)

# Build theme
theme = Theme(
    name="ACME Corporate",
    brand_kit=brand,
    intro_template=intro,
    content_tone="professional"
)

# Save theme
manager = ThemeManager()
theme_id = manager.save_theme(theme)
```

## Error Handling

All v3.0 components follow consistent error handling:

```python
try:
    style = analyzer.analyze_video("video.mp4", "Style")
except VideoAnalysisError as e:
    logger.error(f"Failed to analyze video: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
```

## Example Themes and Styles

### Custom Theme Examples

Located in `examples/themes/`:

1. **Corporate Professional** (`corporate_theme.py`)
   - Clean business communication theme
   - Professional blue color scheme
   - Minimal transitions and effects
   - Suitable for: Company updates, presentations, announcements

2. **YouTube Educational** (`youtube_educational_theme.py`)
   - Educational content with clear structure
   - Green accent colors for learning
   - Whiteboard effects and highlights
   - Suitable for: Tutorials, courses, how-to videos

3. **Lifestyle Vlog** (`lifestyle_vlog_theme.py`)
   - Warm, personal aesthetic
   - Vertical format for social media
   - Soft filters and light leaks
   - Suitable for: Personal vlogs, lifestyle content, Instagram stories

### Style Template Examples

Located in `examples/styles/`:

1. **Cinematic Style** (`cinematic_style.json`)
   - Dramatic color grading (teal & orange)
   - Widescreen letterbox (2.35:1)
   - Film grain and slow camera movements
   - 24fps for cinematic feel

2. **Minimalist Clean** (`minimalist_clean_style.json`)
   - High contrast black & white
   - Simple typography (Helvetica Neue)
   - Static camera, minimal effects
   - Maximum clarity and readability

3. **Retro 80s Synthwave** (`retro_80s_style.json`)
   - Neon colors and glow effects
   - VHS-inspired distortions
   - Chromatic aberration and scan lines
   - 4:3 aspect ratio for authenticity

4. **Documentary Style** (`documentary_style.json`)
   - Serious, professional tone
   - Typewriter text animations
   - Film-look color grading
   - Interview-style composition

### Using Examples

```bash
# Run a custom theme example
cd examples/themes
python corporate_theme.py

# Import a style template
python main.py import-style examples/styles/cinematic_style.json

# Use in generation
python main.py generate \
  --mission "Product launch" \
  --theme corporate_professional \
  --style-template "Cinematic Style"
```

## Character Consistency API

### CharacterConsistencyManager

Manages character profiles for consistent series.

```python
from src.utils.character_consistency import CharacterConsistencyManager

# Initialize manager
manager = CharacterConsistencyManager()

# Create news anchor profiles
sarah, michael = manager.create_news_anchors()

# Generate consistent prompt
prompt = manager.get_episode_prompt(
    episode_num=1, 
    content="Breaking news coverage"
)
```

### Character Profile Structure

```python
@dataclass
class CharacterProfile:
    name: str
    description: str
    detailed_appearance: Dict[str, str]  # ethnicity, age, hair, etc.
    reference_images: List[str]
    voice_profile: str
    personality_traits: List[str]
```

### Consistency Strategies

```python
# Voice-Over Approach (Most Consistent)
mission = "Professional narrator voice. Show footage, no faces."

# Branded Graphics Approach
mission = "Network logo 'ABC News'. Blue/white colors. Same graphics."

# Style Reference Approach
reference_style = "outputs/session_ep1/final_output/video.mp4"
```

## Best Practices

1. **Style References**
   - Analyze high-quality reference videos
   - Save frequently used styles to library
   - Combine multiple styles for unique looks

2. **Themes**
   - Use presets as starting points
   - Create organization-specific themes
   - Export/import themes for team sharing

3. **Character Consistency**
   - Use voice-over for perfect consistency
   - Focus on branding elements over faces
   - Leverage style references between episodes
   - See [Character Consistency Guide](CHARACTER_CONSISTENCY_GUIDE.md)

4. **Performance**
   - Cache analyzed styles
   - Reuse theme objects
   - Batch process when possible

4. **Testing**
   - Use cheap mode with themes
   - Test style extraction on various videos
   - Validate theme consistency