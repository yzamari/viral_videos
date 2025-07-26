# Fixed Multi-Language Shell Scripts Summary

## Issues Addressed

1. **Separate Videos per Language**: Each language now gets its own complete video generation run with embedded audio and subtitles, not just copies
2. **VEO Generation**: Added `--force-generation-mode force_veo2` to ensure VEO is used instead of colored fallback
3. **News-Style Overlays**: Added `--use-subtitle-overlays` flag for proper overlay rendering
4. **RTL Support**: Added `--rtl` flag for Hebrew versions to ensure proper text alignment
5. **Image Fallback**: Added `--use-image-fallback` for better fallback when VEO fails

## Key Changes in Fixed Scripts

### 1. Separate Generation Runs
- Each language gets its own python command with unique session ID
- Hebrew missions are fully translated (not just subtitles)
- Each video is generated independently with proper language embedding

### 2. Generation Flags
```bash
--no-cheap                    # Disable cheap mode
--mode enhanced               # Use enhanced mode with 7 AI agents
--use-subtitle-overlays       # Enable news-style overlays
--force-generation-mode force_veo2  # Force VEO-2 generation
--use-image-fallback          # Use image generation as fallback
--rtl                         # For Hebrew versions only
```

### 3. Session Organization
- English: `outputs/{series}_ep{N}_english/`
- Hebrew: `outputs/{series}_ep{N}_hebrew/`

## Fixed Scripts Created

1. **run_israeli_pm_multilang_fixed.sh**
   - Israeli PM Marvel series with superpowers
   - Separate English and Hebrew versions
   - Professional mode for full agent discussions

2. **run_nuclear_news_multilang_fixed.sh**
   - Nuclear News series in Family Guy style
   - Animated comedy with news overlays
   - Enhanced mode for faster generation

3. **run_iranian_news_multilang_fixed.sh**
   - Serious documentary-style news about water crisis
   - Professional news broadcast aesthetic
   - 3 episodes covering crisis progression

## Usage

To run the fixed scripts:
```bash
./run_israeli_pm_multilang_fixed.sh
./run_nuclear_news_multilang_fixed.sh
./run_iranian_news_multilang_fixed.sh
```

Each script will:
1. Generate English version first
2. If successful, generate Hebrew version
3. Continue to next episode
4. Show completion status and output locations

## Expected Output

Each language version will have:
- Complete video with embedded audio in the target language
- Subtitles properly positioned and styled
- News-style overlays (where applicable)
- VEO-generated or image-generated clips (not colored fallback)
- Proper RTL text alignment for Hebrew