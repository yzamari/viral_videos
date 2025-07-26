# Release v0.4.0-rc1 - Major Fixes and Improvements

## 🎉 Highlights
This release candidate includes critical fixes for video generation, multilingual support, and content filter handling.

## 🐛 Bug Fixes

### Video Generation
- **Fixed video clip durations**: Video clips now properly use 5-8 second durations instead of incorrectly using audio segment durations (0.5-2s)
- **Fixed clip count calculation**: 50-second videos now generate ~8 clips as expected, not 10-13 clips
- **Fixed frame continuity**: Last frame extraction and continuity between clips working correctly

### Multilingual Support  
- **Fixed Hebrew language generation**: Script processor and voice selection now correctly use target language from `--languages` parameter
- **Fixed language parameter bug**: Changed from incorrect `config.get('language')` to proper `config.get('languages')[0]`
- **Hebrew RTL text rendering**: Already implemented, will work once Hebrew content is generated

### Content Filter Handling
- **Implemented hierarchical fallback system**:
  1. VEO generation (first attempt)
  2. VEO with rephrased prompt (if content filter violation)
  3. Image generation (2 attempts) 
  4. Color fallback (final resort)
- **Fixed immediate fallback issue**: VEO client now propagates errors to upper layer instead of creating fallback immediately

### Script Processing
- **Fixed text validator warnings**: Changed from WARNING to DEBUG level when no issues found
- **Fixed aggressive text validation**: Text validator was removing valid content thinking it was metadata

## ✨ Improvements

### Error Handling
- Better error propagation between VEO client and video generator
- Clearer logging for content filter violations
- Improved fallback generation with proper error context

### Code Quality
- Removed hardcoded duration logic
- Centralized language detection
- Better separation of concerns between layers

## 📝 Updated Scripts
- `run_israeli_pm_50s_final.sh` - Ready with all fixes noted
- `run_iran_news_family_guy_final.sh` - Ready with all fixes noted

## 🔧 Technical Details

### Files Modified
- `src/generators/video_generator.py` - Fixed clip duration logic, added hierarchical fallback
- `src/generators/vertex_ai_veo2_client.py` - Fixed error handling, removed immediate fallback
- `src/agents/working_orchestrator.py` - Fixed language parameter usage
- `src/generators/enhanced_script_processor.py` - Fixed logging levels

### Known Issues
- Image generation fallback is currently a placeholder (needs implementation)
- Text validator may still need tuning for edge cases

## 📦 Installation
```bash
git checkout v0.4.0-rc1
pip install -r requirements.txt
```

## 🧪 Testing
Test the fixes with:
```bash
./run_israeli_pm_50s_final.sh  # Tests Hebrew generation and clip durations
./run_iran_news_family_guy_final.sh  # Tests Family Guy style with news overlay
```

## 🤝 Contributors
- Fixed by Claude with human guidance
- Tested on Israeli PM Marvel series generation

---

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>