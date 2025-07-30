# Pull Request: RC v3.3.0 - JSON VEO Prompts & Enhanced Subtitles

## Branch Information
- Source Branch: `feature/universal-ai-provider-interface`
- Target Branch: `main`
- Tag: `v3.3.0-rc1`

## PR Title
🚀 RC v3.3.0 - JSON VEO Prompts & Enhanced Subtitles

## PR Description
### Summary
This PR introduces JSON-structured prompts for VEO video generation and fixes critical subtitle positioning issues for mobile platforms.

### ✨ Features Added
- **JSON VEO Prompts System**
  - Structured prompt format for better video generation control
  - Scene descriptions with segment indexing
  - Visual style and camera movement specifications
  - Platform-optimized settings for TikTok/Instagram/YouTube

- **Enhanced Subtitle Positioning**
  - Optimized for TikTok (70% vertical position)
  - Dynamic font sizing based on orientation
  - Better mobile readability

### 🐛 Bugs Fixed
- Fixed KeyError when processing non-string prompts
- Fixed 'dict' has no attribute 'lower' in VEO client
- Fixed subtitles appearing too low on TikTok
- Fixed font sizes for mobile devices

### 📊 Testing
- ✅ Tested with calculus-drama-v8 session
- ✅ VEO generation working with JSON prompts
- ✅ Subtitle positioning verified on TikTok format
- ✅ No regression in existing features

### 🚀 Ready for Production
This RC has been tested and is ready for production deployment.

## GitHub PR URL
https://github.com/yzamari/viral_videos/compare/main...feature/universal-ai-provider-interface
EOF < /dev/null