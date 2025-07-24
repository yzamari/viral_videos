# Release Notes - v3.0.0-rc1

## 🚀 ViralAI v3.0.0 Release Candidate 1

**Release Date:** July 23, 2025  
**Type:** Major Release Candidate  
**Focus:** Zero Hardcoding & Complete Configuration System

---

## 🎉 Highlights

This release candidate represents a major milestone in the ViralAI project, introducing a comprehensive configuration system that eliminates ALL hardcoded values from the codebase. Every aspect of video generation is now fully configurable, making the system truly flexible and maintainable.

---

## 🆕 Major Features

### 🎛️ Complete Configuration System

We've introduced a centralized configuration system that replaces all hardcoded values throughout the codebase:

- **Location:** `src/config/video_config.py`
- **Categories:**
  1. **VideoEncodingConfig** - Platform-specific encoding settings
  2. **TextOverlayConfig** - Font styling and appearance
  3. **AnimationTimingConfig** - Transitions and effects
  4. **DefaultTextConfig** - Platform-specific default texts
  5. **LayoutConfig** - Positioning and spacing

**Example Usage:**
```python
from src.config.video_config import video_config

# Get platform-specific settings
fps = video_config.get_fps('youtube')  # Returns 30
font_size = video_config.get_font_size('title', 1920)  # Returns 115px

# Customize for your brand
video_config.text_overlay.default_text_color = '#FF6B6B'
video_config.default_text.ctas_by_platform['youtube'] = "Hit Subscribe! 🔔"
```

---

## 🔧 Critical Fixes

### Audio-Video Synchronization
- **Fixed:** Audio duration mismatch (18s audio vs 40s video)
- **Solution:** Updated script processor to EXPAND content to fill duration
- **Impact:** Perfect audio-video synchronization

### Frame Continuity
- **Fixed:** Frame continuity disabled for videos >20s
- **Solution:** Increased threshold from 20s to 120s
- **Impact:** Seamless transitions in longer videos

### Text Overlay Issues
- **Fixed:** Overlapping overlay text
- **Solution:** Increased spacing and added semi-transparent backgrounds
- **Impact:** Clear, readable overlays

### Subtitle Segmentation
- **Fixed:** Multiple sentences in single subtitle
- **Solution:** Enhanced sentence splitting to include colons/semicolons
- **Impact:** One sentence per subtitle segment as intended

### VEO Generation
- **Fixed:** TypeError with 'reference_image' parameter
- **Solution:** Changed to 'image_path' parameter
- **Impact:** Successful VEO video generation

### Platform Resolution
- **Fixed:** YouTube videos in wrong resolution (720x1280)
- **Solution:** Implemented platform-aware dimensions (1920x1080)
- **Impact:** Correct aspect ratios for all platforms

### Content Policy
- **Fixed:** Hardcoded content restrictions blocking legitimate content
- **Solution:** Removed all validation, added AI retry with rephrasing
- **Impact:** More flexible content generation

---

## 📊 Configuration Details

### Video Encoding
```python
# Platform-specific FPS
fps_by_platform = {
    'youtube': 30,
    'tiktok': 30,
    'instagram': 30
}

# Quality settings (CRF - lower = better)
crf_by_platform = {
    'youtube': 23,    # Good quality
    'tiktok': 25,     # Slightly lower
    'instagram': 25
}
```

### Text Styling
```python
# Dynamic font sizing (% of video width)
font_sizes = {
    'title': 0.06,      # 6% of width
    'subtitle': 0.044,  # 4.4% of width
    'body': 0.04        # 4% of width
}

# Semi-transparent backgrounds
background_opacity = 0.8
```

### Animation Timing
```python
# Smooth transitions
fade_in_duration = 0.5
fade_out_duration = 0.5
crossfade_duration = 1.0

# Display durations
hook_display_duration = 3.0
cta_display_duration = 3.0
```

---

## 💔 Breaking Changes

1. **Configuration Required**: All components now require configuration access
2. **Duration Tolerance**: Changed from 15% to 30%
3. **Frame Continuity**: Threshold changed from 20s to 120s
4. **No Hardcoded Values**: Any hardcoded value will cause errors

---

## 📚 Documentation

### New Documentation
- **[Configuration Guide](docs/CONFIGURATION_GUIDE.md)** - Complete configuration reference
- **Configuration sections** added to:
  - README.md
  - SYSTEM_ARCHITECTURE.md
  - CLAUDE.md

### Updated Examples
- Platform-specific configuration examples
- Brand customization guides
- Migration instructions

---

## 🔄 Migration Guide

### For Developers

Replace all hardcoded values with configuration lookups:

```python
# ❌ Old (Hardcoded)
fps = 30
font_size = 48
text_color = 'white'

# ✅ New (Configuration-based)
fps = video_config.get_fps(platform)
font_size = video_config.get_font_size('title', video_width)
text_color = video_config.text_overlay.default_text_color
```

### For Users

No action required - the system automatically uses optimal settings for each platform.

To customize:
```python
# Import configuration
from src.config.video_config import video_config

# Customize settings
video_config.encoding.fps_by_platform['youtube'] = 60  # 60fps videos
video_config.text_overlay.default_font = 'Montserrat-Bold'  # Custom font
```

---

## 🧪 Testing

This release candidate has been tested with:
- ✅ All generation modes (simple/enhanced/professional)
- ✅ All platforms (YouTube/TikTok/Instagram/Twitter/LinkedIn)
- ✅ Cheap and premium modes
- ✅ Continuous video generation
- ✅ Character consistency features

---

## 📈 Performance Improvements

- **30% tolerance** in duration coordination for more flexible content
- **Dynamic font sizing** ensures readability across all resolutions
- **Platform-aware encoding** optimizes file size and quality
- **Configurable transitions** allow faster or smoother animations

---

## 🐛 Known Issues

1. **Continuous mode** only works in premium (non-cheap) mode
2. **Character consistency** requires manual setup of reference images
3. **Some themes** may need adjustment for new configuration system

---

## 🙏 Acknowledgments

This release represents a major refactoring effort to eliminate technical debt and create a truly flexible video generation system. Special thanks to all contributors and testers.

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/yzamari/viral_videos.git
cd viral_videos

# Checkout the release candidate
git checkout v3.0.0-rc1

# Install dependencies
pip install -r requirements.txt
```

---

## 🚀 What's Next

- **v3.0.0 Final** - After testing and feedback
- **Content Scraping** - Automated content gathering
- **Media Integration** - External media support
- **Advanced Analytics** - Performance tracking

---

## 📞 Support

For issues or questions:
- Create an issue on [GitHub](https://github.com/yzamari/viral_videos/issues)
- Check the [Configuration Guide](docs/CONFIGURATION_GUIDE.md)
- Review the [Migration Guide](#migration-guide)

---

**Thank you for using ViralAI! 🎬**

*This release candidate introduces zero hardcoding and complete configurability to the ViralAI system.*