# Release Notes - v0.5.0-rc1

## 🎉 Release Candidate 1 for Version 0.5.0

### 🌐 Major Hebrew Support Fixes

This release candidate addresses critical issues with Hebrew language support in video overlays and introduces a new Netanyahu Marvel Episode 17 generation script.

## 🐛 Bug Fixes

### Hebrew Overlay Support
- **Fixed**: Hebrew CTAs in overlays were showing English "Follow for more!" - now properly displays Hebrew CTAs
- **Fixed**: Hebrew hooks in overlays were showing English "Amazing content ahead!" - now shows Hebrew hooks
- **Fixed**: DecisionFramework was not language-aware - now properly detects and uses Hebrew defaults
- **Fixed**: Director CTA generation ignored target language - now respects language settings

## ✨ New Features

### Netanyahu Marvel Episode 17 Script
- Added `run_netanyahu_marvel_ep17.sh` for generating Marvel-style political comedy
- Supports dual language generation (Hebrew + English)
- Marvel comic style with multiple sound effects:
  - CRASH! - Netanyahu breaks through Knesset walls
  - BOOM! - Coalition deals with exploding panels
  - ZAP! - Texting while juggling trials
  - THWACK! - Building settlements with energy beams
  - CRACK! - Judicial reform splits the nation
  - WHAM! - "Bibi will return... again!"
- Dark humor and satirical tone for political comedy
- 55-second Instagram format

## 🔧 Technical Improvements

### Language System Enhancements
- Modified `director.py` to pass `target_language` to `_create_cta` method
- Added comprehensive Hebrew CTA templates for all platforms
- Updated `decision_framework.py` to check language and use Hebrew defaults
- Added `_get_hebrew_cta_for_platform` helper method
- Fixed AttributeError by adding `hasattr` check before accessing `all_languages`

### Hebrew Templates Added
- YouTube: "הירשמו לעוד תוכן!" (Subscribe for more content!)
- TikTok: "עקבו לחלק 2! 👀" (Follow for part 2!)
- Instagram: "לייק ועקבו! ❤️" (Like and follow!)

## 📋 Testing

- Verified Hebrew script generation works correctly
- Confirmed audio and subtitles are properly generated in Hebrew
- Validated overlays now show Hebrew CTAs and hooks
- Tested with both simple and full generation modes
- Tested RTL text handling in all overlay positions

## 🚀 Usage

### Generate Netanyahu Marvel Episode 17:
```bash
./run_netanyahu_marvel_ep17.sh
```

This will generate both Hebrew and English versions with Marvel comic effects and dark humor.

## 📝 Notes

- Missions remain in English as designed
- Scripts, audio, subtitles, and overlays are now properly localized
- RTL languages are fully supported in overlays
- This RC is ready for production testing

## 🏷️ Version

- **Version**: 0.5.0-rc1
- **Type**: Release Candidate
- **Branch**: feature/datasources-integration
- **Tag**: v0.5.0-rc1

## 🤝 Contributors

- Human: Requirements and testing
- Claude: Implementation and fixes