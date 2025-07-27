# Release Notes - v0.5.1-rc1

## 🎬 Release Candidate 1 for Version 0.5.1

### VEO Mode Enforcement & Cheap Mode Fixes

This release candidate addresses critical issues with cheap mode generation and ensures all scripts use high-quality VEO video generation.

## 🐛 Bug Fixes

### Cheap Mode Subtitle Error
- **Fixed**: "name 'width' is not defined" error in `_create_cheap_mode_subtitles`
- **Solution**: Added `video_width` calculation based on `video_height` parameter
- **Impact**: Cheap mode subtitles now render correctly when fallback is needed

### VEO Mode Enforcement
- **Issue**: Some shell scripts were generating cheap mode videos instead of VEO
- **Fixed**: Added `--no-cheap` flag to all generation scripts
- **Result**: All automated scripts now produce high-quality VEO videos

## 🔧 Technical Changes

### Video Generator Updates
```python
# Added in _create_cheap_mode_subtitles
video_width = 1080 if video_height == 1920 else 1920
fontsize=video_config.get_font_size('subtitle', video_width)
```

### Shell Scripts Updated
1. **run_netanyahu_marvel_ep17.sh**
   - Added `--no-cheap` flag
   - Now generates Marvel-style VEO videos

2. **examples/create_bbc_style_news_series.sh**
   - Added `--no-cheap` flag to all 3 episode generations
   - Ensures BBC-style news series uses VEO quality

3. **run_video_generator.sh**
   - Added `--no-cheap` flag to CLI mode
   - Default behavior now uses VEO generation

## ✅ Scripts Already Using VEO Mode
- run_israeli_pm_50s_final.sh
- run_iran_news_family_guy_final.sh
- run_episode_2.sh
- manage_characters.sh

## 📋 Testing

To verify VEO generation:
```bash
# Run Netanyahu Marvel Episode 17 (should generate VEO video)
./run_netanyahu_marvel_ep17.sh

# Check output folder for VEO clips
ls outputs/netanyahu_marvel_ep17_*/video_clips/veo_clips/
```

## 🚀 Impact

- **Consistent Quality**: All scripts now generate high-quality VEO videos
- **No Surprises**: Users won't accidentally get cheap mode output
- **Better UX**: Clear expectation of video quality across all scripts

## 📝 Notes

- Cheap mode is still available via explicit `--cheap` flag when needed
- VEO generation requires proper API credentials and may take longer
- Monitor VEO API usage to manage costs

## 🏷️ Version

- **Version**: 0.5.1-rc1
- **Type**: Release Candidate
- **Branch**: feature/datasources-integration
- **Tag**: v0.5.1-rc1
- **Previous**: v0.5.0-rc1

## 🤝 Contributors

- Human: Bug report and testing
- Claude: Implementation and fixes