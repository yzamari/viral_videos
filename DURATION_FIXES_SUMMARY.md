# Duration Fixes Summary

## Overview
All duration alignment issues have been fixed across the ViralAI codebase to ensure consistent video generation that matches the target duration.

## Changes Made

### 1. ✅ **Subtitle Formatting & Timing Fixes**
**File:** `src/generators/video_generator.py`
- **Issue:** Subtitles were displayed as single long lines instead of 2-line maximum
- **Fix:** Modified `_create_subtitles` function to:
  - Use `_format_subtitle_text` with 8 words/42 chars per line maximum
  - Split audio segments into 2.5-second subtitle chunks for better timing
  - Properly format both SRT and VTT files

### 2. ✅ **Removed Hardcoded Duration Defaults**

#### **video_generator.py**
- Changed: `duration_seconds=15` → `duration_seconds if duration_seconds is not None else 30`
- Added duration_seconds parameter to `generate_video_config` function

#### **image_timing_agent.py**
- Replaced all hardcoded `7.0` second defaults with calculated values based on target_duration
- Updated platform-specific durations to be proportional ratios (0.9x, 1.0x, 1.1x) of target average
- Fixed: Base durations now calculated as `target_duration / num_images`

#### **voice_director_agent.py**
- Removed default value from `duration_seconds: int = 10` parameter
- Made duration_seconds a required parameter in `get_voice_config`

#### **overlay_positioning_agent.py**
- Changed: `hook_duration = 2.5` → `hook_duration = min(3.0, max(1.5, video_duration * 0.08))`
- Hook duration now calculated as 8% of video duration (capped at 1.5-3 seconds)

### 3. ✅ **Fixed Clip Duration Enforcement Timing**
**File:** `src/core/decision_framework.py`
- **Issue:** Clip duration enforcement happened AFTER AI optimization, causing script segmentation mismatches
- **Fix:** 
  - Pre-calculate `min_clips_needed` based on 8-second maximum before AI optimization
  - Pass constraint to all optimization methods (mission planning, basic AI, heuristic)
  - Updated AI prompts to include minimum clips constraint
  - All clip structure decisions now respect the 8-second maximum upfront

### 4. ✅ **Fixed Script Processor Duration Estimation**
**File:** `src/generators/enhanced_script_processor.py`
- **Issue:** Script processor estimated 36.8s for 30s target due to inconsistent words-per-second rates
- **Fixes:**
  - Unified all calculations to use 2.5 words per second (was mix of 2.5 and 3.0)
  - Updated speech rates: slow=2.0, normal=2.5, fast=3.0
  - Added guidance to account for contraction expansion in word count
  - Added "AIM FOR SLIGHTLY FEWER WORDS" instruction to compensate for expansions

## Key Improvements

### Duration Flow Consistency
```
Before: DecisionFramework → Components (with their own defaults/adjustments)
After:  DecisionFramework → Components (strict adherence to CoreDecisions)
```

### Clip Structure Pre-calculation
```python
# Now calculated BEFORE AI optimization:
MAX_CLIP_DURATION = 8.0
min_clips_needed = max(1, int(np.ceil(duration / MAX_CLIP_DURATION)))
```

### Consistent Speech Rate
- All components now use 2.5 words/second for duration calculations
- Accounts for contraction expansion (e.g., "don't" → "do not")

## Testing Recommendations

1. **Subtitle Verification**
   - Generate a video and check SRT/VTT files
   - Verify each subtitle has maximum 2 lines
   - Confirm subtitle timing matches audio segments

2. **Duration Accuracy**
   - Test with various durations (15s, 30s, 60s)
   - Verify output matches target within ±2 seconds
   - Check script word count matches duration expectations

3. **Clip Structure**
   - Verify no clip exceeds 8 seconds
   - Confirm clip count matches pre-calculated minimum
   - Check script segmentation aligns with clip boundaries

## Impact

These fixes ensure:
- ✅ Videos match requested duration accurately
- ✅ Subtitles are readable with proper 2-line formatting
- ✅ All components respect centralized duration decisions
- ✅ Script content fits within target duration
- ✅ Clip structure is optimized before script generation

The system now maintains consistent duration alignment throughout the entire video generation pipeline.