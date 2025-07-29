# Release Notes

## v3.2.3 (July 29, 2025)

### 🚨 Critical Production Fixes

#### RTL Text Double Reversal Fix
- **ROOT CAUSE FOUND**: MoviePy was applying RTL handling on already-reversed text
- **Fixed**: Removed `get_display()` call - MoviePy expects logical order, not visual order
- **Impact**: Hebrew/Arabic/Persian text now displays correctly in all videos

#### Historical Figure Accuracy
- **Added**: Historical figure database with accurate descriptions
- **Ben-Gurion**: Now shows with distinctive wild white hair and khaki shirt
- **Sharett**: Correctly shows as completely bald with wire-rimmed glasses
- **Enhanced**: Director emphasizes historical accuracy for real people

#### Audio Synchronization Enhancement
- **Added**: 50ms timing buffer for better audio-subtitle sync
- **Fixed**: Processing delays causing misalignment

#### Ghibli Animation Style Fix
- **Enhanced**: Style description now emphasizes "2D hand-drawn animation"
- **Added**: Specific Miyazaki aesthetic keywords
- **Result**: Proper Japanese anime style instead of realistic rendering

#### Failed Video Generation Prevention
- **Added**: Emergency fallback when all generation methods fail
- **Prevents**: "base_video.mp4 not found" errors
- **Ensures**: Pipeline completion even in worst-case scenarios

### 📚 Documentation
- Added comprehensive `ROOT_CAUSE_ANALYSIS.md` documenting all issues and fixes

---

## v3.2.2 (July 28, 2025)

### 🎬 Major Video Generation Fixes

#### RTL Text Rendering
- **Fixed Hebrew/Arabic text reversal**: Text now displays correctly using `arabic-reshaper` and `python-bidi`
- **Proper bidirectional text support**: Hebrew subtitles no longer appear reversed (זקן instead of ןקז)
- **Automatic RTL detection**: System detects RTL languages and applies proper text shaping
- **Fallback support**: Graceful degradation if RTL libraries unavailable

#### Animation Style Recognition 
- **Fixed Ghibli style detection**: Enhanced style matching for complex style strings
- **Proper style enhancement**: "studio ghibli magical realism" now correctly applies Ghibli animation
- **Improved style mapping**: Better partial matching for animation styles

#### Audio-Subtitle Synchronization
- **Perfect timing alignment**: Replaced overlapping audio with proper silence gaps
- **Sequential audio playback**: Audio segments now play at exact subtitle timings
- **Dynamic silence insertion**: Calculates and inserts precise silence between segments
- **End-of-video padding**: Added proper silence at video end to match duration

### 🔧 Technical Implementation
- Added RTL text reshaping in `video_generator.py` for all subtitle rendering
- Enhanced `visual_style_agent.py` style detection algorithm
- Rewrote audio concatenation logic with proper gap calculation
- Added `fix_rtl_rendering.py` utility for RTL package installation

### 📦 New Dependencies
- `arabic-reshaper`: For proper RTL text shaping
- `python-bidi`: For bidirectional text algorithm support

---

## v3.2.1-rc1 (July 27, 2025)

### 🎯 Critical Fix: Audio-Visual Separation

#### Visual/Dialogue Tagging System
- **Revolutionary tagging system**: AI agents now properly tag visual descriptions vs spoken dialogue
- **No more hardcoded filters**: System uses intelligent tagging instead of regex patterns
- **Format**: `[VISUAL: description] DIALOGUE: spoken text`
- **Perfect subtitle sync**: Only dialogue is sent to TTS, visual descriptions enhance video only
- **Backward compatible**: System handles both old and new formats automatically

### 🔧 Technical Improvements
- Updated Director to generate properly tagged content
- Enhanced Multi-Agent Discussion system with tagging awareness
- Improved Script Processor to extract dialogue from tagged content
- Added comprehensive tagging documentation

### 📚 Documentation
- New `docs/TAGGING_SYSTEM.md` explains the visual/dialogue separation
- Updated all prompts to include tagging instructions
- Added examples and best practices for tagged content

### 🐛 Bug Fixes
- Fixed issue where visual descriptions were being spoken in audio
- Resolved subtitle synchronization problems in educational content
- Eliminated hardcoded pattern matching for visual content removal

---

## v3.2.0-rc1 (July 27, 2025)

### 🎉 New Features

#### 🎓 University Theme & Custom Overlays
- **New `preset_university` theme**: Professional academic theme designed for educational content
- **Integrated logo overlays**: Themes now support automatic PNG logo overlays
- **AI University branding**: Complete educational branding kit with logo generation
- **Smart positioning**: Logos automatically positioned with proper padding and animations
- **Theme-based overlay management**: Logo configuration is part of theme definition

#### 📺 Enhanced Episode Selection
- **Selective episode generation**: Use `-e` or `--episodes` flag to generate specific episodes
- **Multiple episode support**: Generate batches like `-e 1 3 5 7`
- **Universal implementation**: Works across all series scripts (Educational, News, Israeli PM)
- **Parallel compatibility**: Episode selection works with parallel generation (`-p` flag)
- **Help documentation**: All scripts now include episode listing with `-h` flag

### 🔧 Improvements

#### Script Enhancements
- **Bash compatibility fixes**: Removed associative arrays for older bash version support
- **Parallel generation optimization**: Fixed concurrent episode generation issues
- **Better error handling**: Improved error messages and recovery mechanisms
- **Progress tracking**: Enhanced logging for multi-episode generation

#### Theme System Updates
- **Logo overlay support**: All themes can now include custom PNG overlays
- **Position control**: Configure logo position, size, opacity, and animation
- **Brand consistency**: Maintain visual identity across all generated videos
- **Educational focus**: New academic styling options for learning content

### 🐛 Bug Fixes
- Fixed bash `declare -A` errors in parallel generation script
- Fixed `--overlay` option to use theme system instead
- Resolved theme registration issues in theme manager
- Fixed episode data validation in series scripts

### 📚 Documentation Updates
- Updated README.md with v3.2.0-rc1 features
- Enhanced SYSTEM_ARCHITECTURE.md with theme system details
- Added university theme documentation
- Updated series generation examples

### 🔄 Migration Notes
- Replace `--overlay` with `--theme preset_university` for logo overlays
- Update bash scripts if using associative arrays
- Logo files should be PNG format with transparent backgrounds
- Themes now handle all overlay management

### 💡 Usage Examples

```bash
# Generate calculus series with university branding
./run_calculus_baby_dragon_series.sh -e 1 2 3

# Use parallel generation with episode selection
./run_calculus_baby_dragon_series_parallel.sh -e 1 5 9 -p 3

# Apply university theme to any generation
python3 main.py generate \
  --mission "Your educational content" \
  --theme preset_university \
  --platform instagram
```

### 🙏 Acknowledgments
- Thanks to all contributors who reported bash compatibility issues
- Special thanks for feedback on educational content needs

---

## Previous Releases

### v3.1.0 (July 2025)
- Universal AI Provider Interface
- Enhanced configuration system with zero hardcoding
- Critical bug fixes for VEO generation
- Character consistency system
- Style reference system implementation

### v3.0.0 (July 2025)
- Initial release of centralized decision framework
- 22-agent AI collaboration system
- Multi-language support
- Professional video generation modes