# Release Notes - v3.8.1-rc1

**Release Date**: August 7, 2025  
**Type**: Bug Fix Release Candidate

## 🐛 Bug Fixes

### Fixed: Language Mixing in News Titles
- **Issue**: Hebrew news titles were showing English words mixed in (e.g., "Another R..." instead of pure Hebrew)
- **Root Cause**: The news orchestrator's rephrasing prompt had conflicting language instructions and provided examples in multiple languages regardless of target language
- **Solution**: 
  - Added strict language separation rules in the prompt
  - Implemented language-specific examples only for the target language
  - Added support for 14+ languages with proper examples
  - Enforced "ONLY [language], no English" rules for non-English content

## ✨ Improvements

### Enhanced Multi-Language Support
- **Universal Language Support**: Now properly handles any language without mixing
- **Supported Languages with Examples**:
  - Hebrew (עברית)
  - Arabic (العربية)
  - Russian (Русский)
  - Spanish (Español)
  - French (Français)
  - German (Deutsch)
  - Chinese (中文)
  - Japanese (日本語)
  - Korean (한국어)
  - Persian/Farsi (فارسی)
  - And more...

- **Language Purity**: Strict enforcement of single-language output
- **Cultural Context**: Humor and expressions adapted to target language culture
- **Flexible Input**: Supports both ISO codes (he, ar, ru) and full names (hebrew, arabic, russian)

## 📝 Documentation Updates

### New Documentation
- **TIKTOK_COMMERCIAL_GUIDE.md**: Complete guide for creating business commercials on TikTok
  - Step-by-step instructions for different commercial types
  - 5 commercial templates (product showcase, testimonials, educational, etc.)
  - Visual style recommendations
  - Best practices for TikTok commercial creation
  - Industry-specific templates
  - A/B testing strategies

### Updated Documentation
- **README.md**: Added "Business & Commercial Features" section
- **docs/FEATURES.md**: Updated with v3.8.1-rc1 features and commercial creation capabilities

## 🔧 Technical Changes

### Files Modified
- `src/news_aggregator/agents/news_orchestrator.py`:
  - Updated `rephrase_content_with_tone()` method with strict language rules
  - Added `_get_language_examples()` helper method for language-specific examples
  - Improved prompt to prevent language mixing

## 🚀 How to Use

### Generate Pure Language Content
```bash
# Hebrew news (pure Hebrew, no English)
python main.py news aggregate-enhanced --languages he

# Arabic news (pure Arabic)
python main.py news aggregate-enhanced --languages ar

# Multi-language versions (each pure)
python main.py news aggregate-enhanced --languages he --languages ar --languages en
```

### Create Business Commercials
```bash
# TikTok commercial for business
python main.py generate \
  --mission "Launch eco-friendly water bottle" \
  --platform tiktok \
  --duration 30 \
  --category business \
  --mode professional
```

## 🧪 Testing
- Tested with Hebrew news generation
- Verified no English words appear in Hebrew titles
- Confirmed language purity for multiple languages

## 📦 Installation
```bash
# Update to latest version
git fetch
git checkout v3.8.1-rc1

# Install dependencies
pip install -r requirements.txt
```

## 🔄 Upgrade Notes
- No breaking changes
- Backward compatible with existing news aggregator configurations
- Existing language configurations will work with improved purity

## 🙏 Credits
- Bug reported and fixed for Hebrew language mixing issue
- Documentation expanded for business use cases

---

**Note**: This is a Release Candidate. Please test thoroughly before using in production.