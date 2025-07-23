# Persian News Satire Series Guide

## Overview

This guide explains how to create a professional Persian news satire series that looks like Iran International or BBC Persian, with dark humor while respecting Iranian cultural sensitivities.

## Features

### 1. **Professional News Broadcast Style**
- Consistent branding with logo overlays
- Lower thirds with Persian/English text
- Professional news graphics and transitions
- Breaking news banners
- Weather forecast overlays

### 2. **Cultural Sensitivity**
- Automatic hijab enforcement for female characters
- Modest dress code for all characters
- No alcohol, gambling, or inappropriate content
- Respectful political satire
- Persian cultural references (tarof, etc.)

### 3. **Dark Humor Topics**
- Government bureaucracy inefficiency
- Water crisis management
- "Nuclear" weather forecasts
- Economic challenges (water more expensive than oil)
- Committee formations for everything

## Quick Start

### Run the Complete Series
```bash
./create_iranian_news_satire_series.sh
```

This creates 5 episodes:
1. Water Crisis Special Report
2. Bureaucratic Solutions
3. Nuclear Weather Forecast
4. Divine Intervention Plans
5. Water Economy Crisis

### Create Individual Episodes
```bash
# Episode with cultural guidelines
python main.py generate \
  --series "persian-news-series-id" \
  --mission "Your satirical news content here" \
  --cultural-guidelines iranian \
  --theme persian-news-pro \
  --character leila_hosseini
```

## Theme Assets

### Create News Graphics
```bash
cd themes/persian-news-pro
./create_assets.sh
```

This creates:
- Logo (main and corner versions)
- Breaking news banners
- Lower thirds templates
- Weather graphics
- News ticker backgrounds

## Cultural Guidelines

### Mandatory Rules

#### Dress Code
- **Women**: Must wear hijab/headscarf, modest clothing
- **Men**: No bare chest, professional attire

#### Content Restrictions
- NO alcohol or drinking
- NO romantic physical contact
- NO mixed-gender dancing
- NO gambling imagery
- NO mockery of religion

#### Appropriate Satire Topics
- Government inefficiency
- Bureaucracy and red tape
- Economic challenges
- Environmental issues
- Technology struggles

### Visual Guidelines
- Include Persian/Farsi text
- Traditional Persian design elements
- Professional broadcast standards
- Modest, appropriate settings

## Series Structure

### Episode Format
Each episode follows professional news format:
1. Opening with logo animation
2. Anchor introduction with lower third
3. Main story with graphics
4. Persian text overlays
5. Professional outro

### Character Consistency
- **Leila Hosseini**: Female anchor (with hijab)
- **Ahmad Rezaei**: Male anchor
- Same studio background
- Consistent voice narration

### Dark Humor Elements
- Deadpan delivery of absurd news
- Ironic government solutions
- Bureaucratic inefficiency jokes
- Cultural references (tarof in water crisis)
- "Nuclear" weather forecasts

## Technical Implementation

### Video Generation
```python
# Culturally sensitive generation
config = GeneratedVideoConfig(
    topic="Your satirical news story",
    cultural_guidelines="iranian",
    theme_id="persian-news-pro",
    character_id="leila_hosseini",
    include_logo=True,
    overlay_style="news_lower_thirds"
)
```

### Theme Integration
- Logo appears in top-right corner
- Lower thirds slide in from left
- Persian text overlays included
- Professional transitions between segments

### Cultural Validation
The system automatically:
- Validates content for cultural sensitivity
- Adjusts prompts to include dress code
- Filters inappropriate content
- Adds cultural context to all AI agents

## Best Practices

### Writing Satirical Content
1. Focus on systemic issues, not individuals
2. Use intelligent humor over crude jokes
3. Include Persian idioms and references
4. Maintain professional news tone
5. Balance criticism with humor

### Visual Consistency
1. Always use the theme overlays
2. Maintain professional studio look
3. Include Persian text for key points
4. Use appropriate news graphics
5. Keep consistent color scheme

### Cultural Respect
1. Never mock religious beliefs
2. Maintain appropriate dress codes
3. Use respectful language
4. Include positive cultural elements
5. Avoid Western-centric perspective

## Example Scripts

### Bureaucracy Satire
```
"Breaking news: Government announces formation of 
Supreme Water Committee, which will oversee the 
Water Strategy Committee, reporting to the Water 
Crisis Committee. Officials assure citizens that 
forming committees about committees is top priority."
```

### Nuclear Weather
```
"Weather forecast: Tehran tomorrow will be hot with 
a chance of nuclear. Temperature: 45°C and enriching. 
Citizens advised to carry both sunscreen and Geiger 
counters. Weekend outlook: Sanctions with scattered 
negotiations."
```

### Economic Satire
```
"In economic news, bottled water reaches record 
prices on Tehran black market. One liter now costs 
more than barrel of oil. Citizens joke: At least 
we're still world leader in something!"
```

## Troubleshooting

### Cultural Violations
If you see warnings about cultural violations:
1. Check dress code requirements
2. Remove prohibited content
3. Adjust humor to be more respectful

### Theme Not Applied
Ensure:
1. Theme assets exist in `themes/persian-news-pro/`
2. Use `--theme persian-news-pro` flag
3. Set `--include-logo true`

### Character Consistency
Always use:
- Same `--character` ID across episodes
- Same `--voice` settings
- Same studio `--scene`

## Advanced Features

### Custom Overlays
Create custom overlays for special segments:
```bash
convert -size 800x100 xc:transparent \
    -fill '#CC0000' -draw "rectangle 0,0 800,100" \
    -fill white -font Arial-Bold -pointsize 36 \
    -gravity center -annotate +0+0 'SPECIAL REPORT' \
    special_report.png
```

### Multi-Language Support
Include both English and Persian:
```
--mission "English narration here. 
Persian subtitle: 'متن فارسی اینجا'"
```

## Conclusion

This system creates professional-looking Persian news satire that:
- Respects cultural sensitivities
- Maintains broadcast quality
- Delivers intelligent dark humor
- Engages Persian-speaking audiences
- Looks like real news channels

Perfect for creating viral content that resonates with Iranian audiences while maintaining cultural respect!