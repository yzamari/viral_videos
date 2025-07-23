# 📺 Complete Guide to Creating Consistent Series with ViralAI

## Table of Contents
1. [Overview](#overview)
2. [Character Consistency](#character-consistency)
3. [Voice Consistency](#voice-consistency)
4. [Style Consistency](#style-consistency)
5. [Theme Consistency](#theme-consistency)
6. [Complete Series Examples](#complete-series-examples)
7. [Troubleshooting](#troubleshooting)

## Overview

Creating a consistent series with ViralAI involves maintaining consistency across four key areas:
- **Character Appearance**: Same face/person across all episodes
- **Voice**: Same narrator or character voice
- **Visual Style**: Consistent colors, typography, and aesthetics
- **Theme**: Consistent branding, intros, and overlays

## Character Consistency

### 🎭 Method 1: True Character Persistence (NEW!)

This revolutionary feature uses Google's Imagen to generate consistent character images, then feeds them to VEO for video generation.

#### Setup Character System
```bash
# One-time setup
./setup_character_system.sh

# Verify it's working
python main.py test-character-system
```

#### Create Characters

**Option A: Pre-built News Anchors**
```bash
# American news anchors
python main.py create-news-anchors
# Creates: Sarah Chen, Michael Rodriguez

# Iranian news anchors  
python main.py create-iranian-anchors
# Creates: Leila Hosseini (hijab), Leila Hosseini (no hijab), Ahmad Rezaei
```

**Option B: Custom Character from Photo**
```bash
# Store your own character
python main.py store-character /path/to/photo.jpg \
  --name "John Smith" \
  --description "Professional male news anchor, 40s, gray suit"
```

#### Generate Episodes with Same Character
```bash
# Episode 1
python main.py generate \
  --mission "Breaking news: Water crisis begins" \
  --character sarah_chen \
  --scene "professional news studio with blue backdrop" \
  --platform tiktok \
  --duration 60 \
  --theme preset_news_edition

# Episode 2 - SAME character
python main.py generate \
  --mission "Update: Water crisis worsens" \
  --character sarah_chen \
  --scene "same news studio setup" \
  --platform tiktok \
  --duration 60 \
  --theme preset_news_edition

# Episode 3 - Character in different setting
python main.py generate \
  --mission "Field report from drought area" \
  --character sarah_chen \
  --scene "outdoor desert location, reporter outfit" \
  --platform tiktok \
  --duration 60 \
  --theme preset_news_edition
```

### 🎬 Method 2: Voice-Over Consistency

For 100% reliability, use voice-over with branded visuals instead of on-screen characters.

```bash
# Professional voice-over series
python main.py generate \
  --mission "Documentary style report. Show relevant footage. Network branding throughout. NO visible anchors." \
  --platform tiktok \
  --duration 60 \
  --theme preset_news_edition \
  --voice "alloy"  # Consistent voice
```

## Voice Consistency

### Using Specific Voices

```bash
# Premium voices (when not in cheap mode)
--voice "alloy"     # Professional female
--voice "echo"      # Male narrator
--voice "fable"     # British accent
--voice "onyx"      # Deep male
--voice "nova"      # Energetic female
--voice "shimmer"   # Warm female

# Language-specific
--language "es-ES" --voice "alloy"  # Spanish
--language "fr-FR" --voice "nova"   # French
--language "ar-SA" --voice "echo"   # Arabic
```

### Maintaining Voice Across Episodes
```bash
# Create voice profile for series
SERIES_VOICE="alloy"
SERIES_LANG="en-US"

# Use in all episodes
python main.py generate \
  --mission "Episode 1 content" \
  --voice $SERIES_VOICE \
  --language $SERIES_LANG \
  ...

python main.py generate \
  --mission "Episode 2 content" \
  --voice $SERIES_VOICE \
  --language $SERIES_LANG \
  ...
```

## Style Consistency

### Method 1: Extract Style from Reference
```bash
# Analyze existing video style
python main.py analyze-style /path/to/reference/video.mp4 \
  --name "My Series Style" \
  --save

# Use in all episodes
python main.py generate \
  --mission "Episode content" \
  --style-template "My Series Style" \
  ...
```

### Method 2: Define Style Parameters
```bash
# Create consistent style variables
SERIES_STYLE="cinematic"
SERIES_TONE="professional"
SERIES_COLORS="blue,silver,white"

# Apply to all episodes
python main.py generate \
  --mission "Episode content" \
  --visual-style $SERIES_STYLE \
  --tone $SERIES_TONE \
  --color-scheme $SERIES_COLORS \
  ...
```

## Theme Consistency

### Using Pre-built Themes
```bash
# Available themes
python main.py list-themes

# News series
--theme preset_news_edition

# Sports series  
--theme preset_sports

# Tech series
--theme preset_tech

# Entertainment series
--theme preset_entertainment
```

### Creating Custom Themes
```bash
# Export existing theme as template
python main.py export-theme preset_news_edition my_news_template.json

# Modify the JSON file with your branding

# Import as custom theme
python main.py import-theme my_news_template.json --name "My Network News"

# Use in series
python main.py generate \
  --mission "Episode content" \
  --theme "My Network News" \
  ...
```

## Complete Series Examples

### Example 1: Professional News Series
```bash
#!/bin/bash
# save as: create_my_news_series.sh

# Series configuration
CHARACTER="sarah_chen"
VOICE="alloy"
THEME="preset_news_edition"
PLATFORM="youtube"
DURATION=60

# Episode 1
python main.py generate \
  --mission "Breaking news: Major discovery in renewable energy" \
  --character $CHARACTER \
  --scene "professional news studio" \
  --voice $VOICE \
  --theme $THEME \
  --platform $PLATFORM \
  --duration $DURATION \
  --session-id "news_series_ep1"

# Episode 2
python main.py generate \
  --mission "Follow-up: Scientists explain the breakthrough" \
  --character $CHARACTER \
  --scene "professional news studio" \
  --voice $VOICE \
  --theme $THEME \
  --platform $PLATFORM \
  --duration $DURATION \
  --session-id "news_series_ep2"

# Episode 3
python main.py generate \
  --mission "Impact: How this changes our future" \
  --character $CHARACTER \
  --scene "professional news studio" \
  --voice $VOICE \
  --theme $THEME \
  --platform $PLATFORM \
  --duration $DURATION \
  --session-id "news_series_ep3"
```

### Example 2: Comedy Series with Character Evolution
```bash
# Episode 1: Traditional
python main.py generate \
  --mission "Satirical news: Water is wet discovery" \
  --character leila_hosseini \
  --scene "traditional news desk" \
  --platform tiktok \
  --duration 60 \
  --style comedy \
  --session-id "comedy_ep1"

# Episode 2: Modern transformation  
python main.py generate \
  --mission "Breaking: Water still wet, officials baffled" \
  --character leila_hosseini_no_hijab \
  --scene "modern news studio" \
  --platform tiktok \
  --duration 60 \
  --style comedy \
  --session-id "comedy_ep2"
```

### Example 3: Tech Review Series
```bash
# Setup
REVIEWER="tech_reviewer_alex"  # Your custom character
STYLE_TEMPLATE="TechChannel2024"
THEME="preset_tech"

# Store character photo first
python main.py store-character alex_photo.jpg \
  --name "Alex Chen" \
  --description "Young tech reviewer, casual attire, enthusiastic"

# Episode series
for episode in 1 2 3 4; do
  python main.py generate \
    --mission "Tech Review Episode $episode: Latest AI gadgets" \
    --character $REVIEWER \
    --scene "modern tech studio with gadgets" \
    --style-template $STYLE_TEMPLATE \
    --theme $THEME \
    --platform tiktok \
    --duration 120 \
    --session-id "tech_series_ep$episode"
done
```

## Troubleshooting

### Character Inconsistency Issues
```bash
# Problem: Character looks different
# Solution: Use exact same character ID and similar scene descriptions

# Good:
--character sarah_chen --scene "news studio with blue background"
--character sarah_chen --scene "news studio with blue background"

# Bad:
--character sarah_chen --scene "news desk"
--character sarah_chen --scene "outdoor location"  # Too different
```

### Voice Consistency Issues
```bash
# Problem: Voice changes between episodes
# Solution: Always specify --voice parameter

# Check available voices
python main.py list-voices

# Use specific voice
--voice "alloy" --language "en-US"
```

### Style Drift Issues
```bash
# Problem: Visual style changes
# Solution: Use saved style templates

# Save reference style
python main.py analyze-style episode1.mp4 --name "SeriesStyle" --save

# Apply to all episodes
--style-template "SeriesStyle"
```

### Session Management
```bash
# Problem: Can't find previous episodes
# Solution: Use meaningful session IDs

# Good:
--session-id "tech_review_s01e01"
--session-id "tech_review_s01e02"

# List all sessions
python main.py list-sessions

# Get session details
python main.py session-info tech_review_s01e01
```

## Best Practices

1. **Plan Your Series**
   - Define character profiles
   - Choose consistent voice
   - Create style guide
   - Select appropriate theme

2. **Test First Episode**
   ```bash
   # Test with cheap mode
   python main.py generate \
     --mission "Test episode" \
     --character your_character \
     --cheap \
     --duration 30
   ```

3. **Create Series Script**
   - Use bash script for consistency
   - Define all parameters as variables
   - Include error handling

4. **Maintain Series Bible**
   ```bash
   # Create series documentation
   mkdir my_series
   echo "Character: sarah_chen" > my_series/series_bible.txt
   echo "Voice: alloy" >> my_series/series_bible.txt
   echo "Theme: preset_news_edition" >> my_series/series_bible.txt
   ```

5. **Batch Generation**
   ```bash
   # Generate multiple episodes efficiently
   ./create_my_series_batch.sh --episodes 10 --cheap
   ```

## Advanced Features

### Cross-Episode References
```bash
# Episode 2 referencing Episode 1
--mission "As we reported yesterday about the water crisis..."
```

### Character Development
```bash
# Gradual scene changes
Episode 1: --scene "formal news studio, serious atmosphere"
Episode 2: --scene "news studio, slightly relaxed"
Episode 3: --scene "casual news setting, modern design"
```

### Multi-Character Series
```bash
# Alternating hosts
Episode 1: --character sarah_chen
Episode 2: --character michael_rodriguez  
Episode 3: --character sarah_chen  # Returns
```

## Need Help?

- Check logs: `outputs/session_*/logs/`
- Test components: `python main.py test-character-system`
- Join Discord: [Link to community]
- Report issues: [GitHub Issues]

Remember: Consistency is key to building audience loyalty and professional content series!