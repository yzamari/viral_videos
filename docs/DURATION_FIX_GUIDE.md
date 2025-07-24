# Duration Synchronization Fix Guide

## Problem Summary

The Israeli PM series generation revealed several critical issues:

1. **Audio Duration Mismatch**: Audio generated was only 48.3s instead of target 65s
2. **Video Clip Count Mismatch**: 17 video clips generated instead of expected 13 
3. **Total Duration Mismatch**: 136s of video clips vs 48.3s of audio

## Root Causes

### 1. TTS Speed Mismatch
- Script processor assumed 2.5 words/second
- Actual TTS speaks at ~2.8 words/second
- Result: Scripts generate less audio than expected

### 2. Segment Count Mismatch
- Script has 13 sentences
- Audio generates 14 segments 
- Video generates 17 clips
- No synchronization between components

### 3. Duration Coordinator Issues
- Reports 136s video duration (17 clips × 8s each)
- Correctly identifies mismatch but can't prevent it
- Warning appears after generation, not before

## Solutions Implemented

### 1. Centralized TTS Configuration
Created `src/config/tts_config.py`:
```python
WORDS_PER_SECOND = 2.8  # Empirically tested
MIN_WORDS_PER_SECOND = 2.7
MAX_WORDS_PER_SECOND = 2.9
```

### 2. Enhanced Script Processor Updates
- Uses centralized TTS config
- Calculates word count based on 2.8 wps
- Better duration estimation

### 3. Video Generator Synchronization
- Uses same TTS config for consistency
- Better segment counting logic

## Remaining Issues to Fix

### 1. Enforce Segment Synchronization
The video generator should:
- Count audio segments first
- Generate exactly that many video clips
- Never exceed audio segment count

### 2. Pre-Generation Validation
Before generating:
- Calculate expected segments
- Validate duration feasibility
- Warn if mismatches likely

### 3. Script Content Generation
For 65s videos:
- Need ~182 words (at 2.8 wps)
- Current scripts only ~132 words
- Need to expand content generation

## Quick Fix for Users

Until comprehensive fix is deployed:

1. **Use shorter durations**: Try 45-50s instead of 65s
2. **Check word count**: Ensure script has ~2.8 words per second
3. **Monitor generation**: Watch for audio/video count mismatches
4. **Use cheap mode for testing**: Faster iteration to validate

## Testing Commands

```bash
# Test with shorter duration
python main.py generate \
  --mission "Your mission here" \
  --duration 45 \
  --cheap \
  --session-id test_duration

# Check results
ls outputs/test_duration/audio/*.mp3 | wc -l
ls outputs/test_duration/video_clips/*.mp4 | wc -l
```

## Long-term Solution

The system needs:
1. Pre-generation planning phase
2. Strict segment count enforcement
3. Dynamic duration adjustment
4. Better script expansion logic