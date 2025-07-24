# Release Notes: v3.1.0-rc1

## 🎉 Major Improvements

### 1. **AI Model Configuration System**
- Centralized AI model configuration in `src/config/ai_model_config.py`
- Default model changed to `gemini-2.5-flash-lite` for super fast performance
- Easy model switching across all components
- Consistent model usage throughout the system

### 2. **Mission-Based Terminology**
- Complete refactoring: replaced all "topic" references with "mission"
- Improved clarity and consistency across the codebase
- Updated all CLI flags, documentation, and internal APIs
- Better alignment with video generation objectives

### 3. **Enhanced Continuity Flags**
- Renamed flags for better clarity:
  - `--continuous` → `--content-continuity` (narrative flow)
  - `--frame-continuity` → `--visual-continuity` (visual consistency)
- Both flags now default to `True` for better out-of-box experience
- Improved scene transitions and storytelling coherence

### 4. **Character Description Extraction**
- Automatic extraction of character descriptions from mission text
- Support for inline character descriptions like "(with white hair, round face)"
- Character descriptions properly integrated into VEO prompts
- Ensures visual consistency for named characters

### 5. **Script Processing Improvements**
- Fixed script duplication issue in enhanced script processor
- Improved content expansion without repetition
- Better handling of target duration and segment count
- More natural script flow for long-form content

## 🐛 Bug Fixes

### Critical Fixes
- **Script Duplication**: Fixed issue where scripts were duplicated to reach target word count
- **Character Description Error**: Fixed `character_desc_section` undefined variable error
- **Mission Context**: Fixed "Unknown" mission appearing in AI agent discussions
- **Parameter Mismatches**: Fixed multiple parameter naming inconsistencies

### Minor Fixes
- Fixed `GeneratedVideoConfig` parameter ordering
- Updated method signatures to use 'mission' instead of 'topic'
- Improved error handling in character scene generation
- Fixed visual style agent parameter issues

## 🔧 Technical Improvements

### Code Quality
- Consistent parameter naming throughout codebase
- Improved error messages and logging
- Better type safety and validation
- Enhanced code documentation

### Performance
- Faster AI model responses with `gemini-2.5-flash-lite`
- Reduced token usage in agent discussions
- Optimized script processing pipeline
- Better caching of AI responses

## 📚 Documentation Updates

### Updated Documents
- **README.md**: Updated with v3.1.0 features and examples
- **CLAUDE.md**: Added new implemented features and guidelines
- **CLI_FLAGS_REFERENCE.md**: Comprehensive flag documentation
- All shell scripts updated with new flag names

### New Examples
- Israeli Prime Ministers Marvel series example
- Iranian Family Guy water crisis series
- Character-based series creation workflows

## 🚀 Migration Guide

### For Existing Users
1. Update flag names in your scripts:
   ```bash
   # Old
   --continuous --frame-continuity
   
   # New
   --content-continuity --visual-continuity
   ```

2. AI model will automatically use `gemini-2.5-flash-lite`
   - To use a different model, modify `src/config/ai_model_config.py`

3. Character descriptions in missions now work automatically:
   ```bash
   --mission "David Ben-Gurion (with white Einstein hair) rises from desert"
   ```

### Breaking Changes
- `--continuous` flag renamed to `--content-continuity`
- `--frame-continuity` flag renamed to `--visual-continuity`
- All internal APIs changed from `topic` to `mission` parameter

## 🎯 What's Next

### Coming in v3.2.0
- Media scraping and integration
- Advanced subtitle positioning
- Multi-language voice cloning
- Enhanced social media scheduling

### Known Issues
- VEO-2 availability depends on Google Cloud authentication
- Some visual styles may not work perfectly with all content types
- Character consistency requires clear descriptions

## 💡 Tips for Best Results

1. **Use Character Descriptions**: Include character details in parentheses within your mission
2. **Enable Continuity**: Keep both continuity flags enabled for coherent videos
3. **Choose Right Mode**: Use `enhanced` mode for balanced quality/speed
4. **Leverage Cheap Mode**: Use `--cheap` for rapid prototyping

## 🙏 Acknowledgments

Thanks to all contributors and users who provided feedback for this release. Special thanks for identifying the script duplication and character description issues.

---

**Release Date**: July 24, 2025
**Release Type**: Release Candidate 1
**Version**: 3.1.0-rc1