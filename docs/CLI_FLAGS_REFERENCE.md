# Complete CLI Flags Reference

This document provides a comprehensive reference for all command-line flags available in ViralAI.

## Table of Contents
- [Core Generation Flags](#core-generation-flags)
- [Content & Style Flags](#content--style-flags)
- [Platform & Format Flags](#platform--format-flags)
- [Development & Debug Flags](#development--debug-flags)
- [Quality & Performance Flags](#quality--performance-flags)
- [Continuity & Consistency Flags](#continuity--consistency-flags)
- [Theme & Branding Flags](#theme--branding-flags)
- [Advanced Features](#advanced-features)
- [Series & Character Flags](#series--character-flags)
- [Social Media Flags](#social-media-flags)
- [Usage Examples](#usage-examples)
- [Additional Commands](#additional-commands)
  - [Authentication & Testing](#authentication--testing)
  - [Character Management Commands](#character-management-commands)
  - [Style Management Commands](#style-management-commands)
  - [Theme Management Commands](#theme-management-commands)
  - [Social Media Commands](#social-media-commands)
- [Notes on Implementation](#notes-on-implementation)

## Core Generation Flags

### `--mission` (Required)
**Type**: String  
**Description**: The main topic or prompt for video generation  
**Example**: `--mission "Create a funny video about cats learning to code"`

### `--duration`
**Type**: Integer  
**Default**: 30  
**Description**: Target video duration in seconds  
**Example**: `--duration 60`

### `--session-id`
**Type**: String  
**Default**: Auto-generated timestamp  
**Description**: Custom session identifier for organizing outputs  
**Example**: `--session-id "my_project_v1"`

### `--category`
**Type**: String  
**Options**: `Comedy`, `Educational`, `Entertainment`, `News`, `Tech`  
**Description**: Content category for better AI agent optimization  
**Example**: `--category Educational`

### `--target-audience`
**Type**: String  
**Description**: Specify target audience for content optimization  
**Example**: `--target-audience "tech professionals aged 25-40"`

## Content & Style Flags

### `--tone`
**Type**: String  
**Options**: `serious`, `humorous`, `inspiring`, `educational`, `dramatic`, `casual`, `professional`, `satirical`, `darkly_humorous`, `urgent`, `analytical`  
**Description**: Sets the emotional tone of the content  
**Example**: `--tone humorous`

### `--style`
**Type**: String  
**Options**: `modern`, `vintage`, `minimalist`, `cinematic`, `documentary`, `artistic`, `professional`, `casual`, `news`, `comedy`, `animated_comedy`  
**Description**: Visual and narrative style  
**Example**: `--style cinematic`

### `--visual-style`
**Type**: String  
**Options**: `realistic`, `animated`, `abstract`, `documentary`, `cinematic`, `cartoon`, `anime`, `3d`, `watercolor`, `oil-painting`, `sketch`, `family guy animation`, `disney`, `professional`  
**Description**: Specific visual rendering style  
**Example**: `--visual-style "family guy animation"`

### `--music-style`
**Type**: String  
**Options**: `upbeat`, `dramatic`, `ambient`, `electronic`, `orchestral`, `pop`, `rock`, `jazz`, `classical`, `hip-hop`, `world`, `none`  
**Description**: Background music style  
**Example**: `--music-style orchestral`

## Platform & Format Flags

### `--platform`
**Type**: String  
**Options**: `youtube`, `tiktok`, `instagram`, `twitter`  
**Default**: `tiktok`  
**Description**: Target social media platform (affects aspect ratio and duration)  
**Example**: `--platform instagram`

### `--voice`
**Type**: String  
**Options**: `professional-narrator`, `casual-young`, `wise-elder`, `energetic-host`, `calm-instructor`, `news-anchor`, `comedic-performer`, `child-friendly`, `dramatic-storyteller`  
**Description**: Voice style for narration  
**Example**: `--voice news-anchor`

## Development & Debug Flags

### `--image-only`
**Type**: Boolean  
**Description**: Force image-only generation using Gemini (no video)  
**Example**: `--image-only`

### `--fallback-only`
**Type**: Boolean  
**Description**: Use fallback text-based video generation only  
**Example**: `--fallback-only`

### `--force`
**Type**: Boolean  
**Description**: Force generation even with quota warnings  
**Example**: `--force`

### `--skip-auth-test`
**Type**: Boolean  
**Description**: Skip authentication test (not recommended)  
**Example**: `--skip-auth-test`

### `--discussion-log`
**Type**: Boolean  
**Description**: Show detailed AI agent discussion logs  
**Example**: `--discussion-log`

### `--discussions`
**Type**: String  
**Options**: `off`, `light`, `standard`, `deep`, `streamlined`, `enhanced`  
**Default**: `enhanced`  
**Description**: AI agent discussion depth and mode  
- `off`: No AI discussions
- `light`: Minimal discussions
- `standard`: Normal discussion depth
- `deep`: In-depth analysis
- `streamlined`: Efficient focused discussions
- `enhanced`: Comprehensive discussions for best viral content

**Example**: `--discussions deep`

## Quality & Performance Flags

### `--mode`
**Type**: String  
**Options**: `simple`, `enhanced`, `advanced`, `professional`  
**Default**: `enhanced`  
**Description**: AI agent complexity and quality level  
- `simple`: Fast generation with basic AI (3 agents)
- `enhanced`: Balanced quality and speed (7 agents)
- `advanced`: High quality with 15 agents
- `professional`: Maximum quality with 19 agents

**Example**: `--mode professional`

### `--veo-model-order`
**Type**: String  
**Default**: `veo3-fast,veo3,veo2`  
**Description**: Specify VEO model preference order for video generation  
**Options**: `veo2`, `veo3`, `veo3-fast`  
**Example**: `--veo-model-order veo3,veo2,veo3-fast`

### `--languages`
**Type**: String  
**Default**: `en-US`  
**Description**: Language(s) for audio and subtitle generation  
**Example**: `--languages "en-US,es-ES,he-IL"`

### `--multiple-voices` / `--single-voice`
**Type**: Boolean  
**Default**: `--single-voice`  
**Description**: Allow multiple voices in video or use single narrator  
**Example**: `--multiple-voices`

### `--cheap` / `--no-cheap`
**Type**: Boolean  
**Default**: `true` (cheap mode enabled)  
**Description**: Enable or disable basic cheap mode  
**Example**: `--no-cheap` (to disable cheap mode)

### `--cheap-mode`
**Type**: String  
**Options**: `full`, `video`, `audio`  
**Default**: `full`  
**Description**: Specify which parts use cheap generation  
- `full`: Use cheap alternatives for both video and audio (text video + gTTS)
- `video`: Only use cheap video generation (fallback graphics + premium audio)
- `audio`: Only use cheap audio generation (premium video + gTTS)

**Example**: `--cheap-mode audio`

## Continuity & Consistency Flags

### `--content-continuity` / `--no-content-continuity`
**Type**: Boolean  
**Default**: `True` (enabled)  
**Description**: Enable content/narrative continuity for seamless storytelling  
**Details**: 
- Creates one long continuous narrative instead of disconnected clips
- Each scene flows naturally into the next
- Best for stories, documentaries, tutorials
- Automatically adds scene transitions in prompts
- Use `--no-content-continuity` to disable

**Example**: `--no-content-continuity` (to disable)

### `--visual-continuity` / `--no-visual-continuity`
**Type**: Boolean  
**Default**: `True` (enabled)  
**Description**: Enable visual continuity between clips  
**Details**:
- Uses last frame of each clip as reference for next clip
- Maintains consistent visual elements (characters, scenes, colors)
- Reduces jarring cuts between scenes
- Ensures smooth visual transitions
- Use `--no-visual-continuity` to disable

**Example**: `--no-visual-continuity` (to disable)

### `--character`
**Type**: String  
**Description**: Character identifier for consistent appearance across videos  
**Details**:
- Can be a stored character ID (e.g., "leila_hosseini")
- Or a detailed character description for one-off use
- Ensures same character appears consistently

**Example**: `--character "animated anchor: Maryam - big eyes, hijab, Persian features"`

### `--scene`
**Type**: String  
**Description**: Scene description for character placement  
**Example**: `--scene "professional news studio with world map background"`

## Theme & Branding Flags

### `--theme`
**Type**: String  
**Options**: Custom theme ID or preset themes  
**Presets**: `preset_news_edition`, `preset_sports`, `preset_tech`, `iran_international_news`, `entertainment`, `educational`  
**Description**: Apply consistent branding and styling  
**Example**: `--theme iran_international_news`

### Business Information Flags

### `--business-name`
**Type**: String  
**Description**: Business or organization name for branding  
**Example**: `--business-name "TechCorp Solutions"`

### `--business-address`
**Type**: String  
**Description**: Business address for contact information  
**Example**: `--business-address "123 Tech Street, Silicon Valley, CA"`

### `--business-phone`
**Type**: String  
**Description**: Business phone number  
**Example**: `--business-phone "+1-555-123-4567"`

### `--business-website`
**Type**: String  
**Description**: Business website URL  
**Example**: `--business-website "https://techcorp.com"`

### `--business-facebook`
**Type**: String  
**Description**: Business Facebook page URL  
**Example**: `--business-facebook "https://facebook.com/techcorp"`

### `--business-instagram`
**Type**: String  
**Description**: Business Instagram handle or URL  
**Example**: `--business-instagram "@techcorp"`

### `--show-business-info` / `--hide-business-info`
**Type**: Boolean  
**Default**: `--hide-business-info`  
**Description**: Show or hide business information in video  
**Example**: `--show-business-info`

### `--series`
**Type**: String  
**Description**: Series ID for episodic content  
**Example**: `--series "my_news_show_s01"`

### `--episode-number`
**Type**: Integer  
**Description**: Episode number within a series  
**Example**: `--episode-number 5`

### `--episode-title`
**Type**: String  
**Description**: Title for the specific episode  
**Example**: `--episode-title "The Water Crisis Deepens"`

## Advanced Features

### `--target-audience`
**Type**: String  
**Description**: Target audience description for content optimization  
**Example**: `--target-audience "young adults interested in tech"`

## Series & Character Flags

### `--reference-style`
**Type**: Path  
**Description**: Path to local video file for style extraction and matching  
**Example**: `--reference-style "/path/to/reference/video.mp4"`

### `--style-template`
**Type**: String  
**Description**: Predefined style template  
**Example**: `--style-template cinematic_drama`

## Social Media Flags

### `--auto-post`
**Type**: Boolean  
**Description**: Automatically post to configured social media  
**Example**: `--auto-post`



## Usage Examples

### Basic Generation
```bash
python main.py generate --mission "Create a funny cat video" --duration 30
```

### Professional News Series
```bash
python main.py generate \
  --mission "Breaking news about technology" \
  --platform youtube \
  --duration 60 \
  --mode professional \
  --theme iran_international_news \
  --character "news_anchor_jane" \
  --style news \
  --tone serious \
  --no-cheap
```

### Comedy Series with Character
```bash
python main.py generate \
  --mission "Family Guy style comedy about water crisis" \
  --visual-style "family guy animation" \
  --character "Maryam the news anchor" \
  --tone darkly_humorous \
  --episode-number 1 \
  --series "water_crisis_comedy"
```

### Cost-Effective Social Media Post
```bash
python main.py generate \
  --mission "Quick tip about productivity" \
  --platform tiktok \
  --duration 15 \
  --cheap-mode full \
  --auto-post
```

## Flag Combinations

### Best Quality
```bash
--mode professional --no-cheap
```

### Fastest Generation
```bash
--mode simple --cheap full --fast
```

### Series Production
```bash
--series "my_series" --character "main_character" --theme "my_theme"
```

### Voice-Specific Content
```bash
--voice news-anchor --tone serious
```

## Additional Commands

### Authentication & Testing

#### `test-auth`
**Description**: Test Google Cloud authentication comprehensively  
**Usage**: `python main.py test-auth`

### Character Management Commands

#### `store-character`
**Description**: Store a character reference image for consistent character generation  
**Usage**: `python main.py store-character [IMAGE_PATH] --name [NAME]`  
**Options**:
- `--name` (Required): Name for the character
- `--description`: Optional character description

#### `list-characters`
**Description**: List all stored character references  
**Usage**: `python main.py list-characters`

#### `generate-character-scene`
**Description**: Generate character in a new scene  
**Usage**: `python main.py generate-character-scene [CHARACTER_ID] [SCENE_DESCRIPTION]`  
**Options**:
- `--output`: Output path for generated image

#### `delete-character`
**Description**: Delete a stored character reference  
**Usage**: `python main.py delete-character [CHARACTER_ID]`

#### `create-news-anchors`
**Description**: Create default news anchor character profiles  
**Usage**: `python main.py create-news-anchors`

#### `create-iranian-anchors`
**Description**: Create Iranian news anchor character profiles  
**Usage**: `python main.py create-iranian-anchors`

#### `test-character-system`
**Description**: Test if character reference system is working  
**Usage**: `python main.py test-character-system`

### Style Management Commands

#### `analyze-style`
**Description**: Analyze visual style from a video  
**Usage**: `python main.py analyze-style [VIDEO_PATH]`  
**Options**:
- `--name`: Name for the style
- `--save`: Save as template
- `--tags`: Comma-separated tags
- `--description`: Style description

#### `list-styles`
**Description**: List available style templates  
**Usage**: `python main.py list-styles`  
**Options**:
- `--query`: Search query
- `--tags`: Filter by tags (comma-separated)

#### `save-style`
**Description**: Save style from a video generation session  
**Usage**: `python main.py save-style [SESSION_ID] --name [NAME]`  
**Options**:
- `--name` (Required): Template name
- `--tags`: Comma-separated tags
- `--description`: Style description

#### `delete-style`
**Description**: Delete a style template  
**Usage**: `python main.py delete-style [TEMPLATE_ID]`

#### `list-presets`
**Description**: List preset style templates  
**Usage**: `python main.py list-presets`

### Theme Management Commands

#### `list-themes`
**Description**: List available themes  
**Usage**: `python main.py list-themes`  
**Options**:
- `--category`: Filter by category (news, sports, tech, entertainment, education, business, lifestyle, custom)

#### `theme-info`
**Description**: Show detailed information about a theme  
**Usage**: `python main.py theme-info [THEME_ID]`

#### `delete-theme`
**Description**: Delete a custom theme  
**Usage**: `python main.py delete-theme [THEME_ID]`

#### `export-theme`
**Description**: Export a theme to file  
**Usage**: `python main.py export-theme [THEME_ID] [OUTPUT_PATH]`

#### `import-theme`
**Description**: Import a theme from file  
**Usage**: `python main.py import-theme [THEME_FILE]`  
**Options**:
- `--name`: New name for imported theme

### Social Media Commands

#### `social status`
**Description**: Show social media platform status  
**Usage**: `python main.py social status`

#### `social configure-whatsapp`
**Description**: Configure WhatsApp integration  
**Usage**: `python main.py social configure-whatsapp`  
**Options**:
- `--access-token`: WhatsApp access token
- `--phone-number-id`: WhatsApp phone number ID
- `--verify-token`: WhatsApp verify token
- `--enabled/--disabled`: Enable/disable WhatsApp

#### `social configure-telegram`
**Description**: Configure Telegram integration  
**Usage**: `python main.py social configure-telegram`  
**Options**:
- `--bot-token`: Telegram bot token
- `--bot-username`: Telegram bot username
- `--enabled/--disabled`: Enable/disable Telegram

#### `social send-video`
**Description**: Send video to social media platforms  
**Usage**: `python main.py social send-video [VIDEO_PATH] [MISSION] [PLATFORM]`  
**Options**:
- `--hashtags/-h`: Hashtags to include (multiple allowed)
- `--caption/-c`: Custom caption

## Notes on Implementation

### Flags Not Yet Implemented
The following flags are documented for future implementation but not currently available:
- Subtitle controls (`--subtitles`, `--subtitle-style`, `--subtitle-position`)
- Overlay controls (`--overlay-style`, `--include-logo`, `--watermark`)
- Series management (`--series`, `--episode-number`, `--episode-title`)
- Advanced posting (`--instagram-caption`, `--hashtags` for generate, `--schedule-time`)
- Cultural controls (`--cultural-guidelines`, `--content-rating`)
- Debug flags (`--verbose`, `--debug`, `--dry-run`, `--save-intermediates`)
- Performance (`--fast`)

### 🚨 **Critical Limitation**: Trending Intelligence Flags Missing

Currently, there are **no CLI flags for trending intelligence control** because the system uses mock trending data instead of real platform APIs. The following trending-related flags should be implemented once real-time trending intelligence is added:

**Proposed Trending Flags** (Future Implementation):
- `--trending-hours <hours>`: Analyze trends from past N hours (default: 24)
- `--trending-region <region>`: Geographic region for trending analysis (e.g., 'US', 'global')
- `--trending-platform <platform>`: Focus trending analysis on specific platform
- `--disable-trending`: Skip trending analysis entirely (use only topic-based insights)
- `--trending-fallback`: Allow fallback to mock data if APIs unavailable
- `--trending-weight <float>`: Weight of trending data in decision making (0.0-1.0)

**Current Status**: These flags don't exist because trending intelligence uses mock data only. Implementation of real-time trending APIs is required before these flags can be added.

### Platform Support
Currently supported platforms: `youtube`, `tiktok`, `instagram`, `twitter`  
Platforms `facebook` and `linkedin` are planned for future releases.