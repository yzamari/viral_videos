# Veo Video Generation Retry Mechanism

## Overview
The system implements a robust retry mechanism to handle Google AI Studio quota limits and maximize video generation success with **3 attempts and 1-minute waits**.

## Retry Sequence

When generating a video clip, the system follows this exact sequence:

**For each of 3 attempts:**
1. Try Veo-3 (if available)
2. Try Veo-2 as fallback
3. If not the last attempt: Wait 1 minute
4. Repeat for next attempt

**After all attempts fail:**
5. Create fallback video

## Model Priority

### Veo-3 (veo-3.0-generate-preview)
- **Priority**: First choice on each attempt
- **Model**: `veo-3.0-generate-preview` 
- **Status**: Available with allowlist access
- **Quality**: Latest generation, best results

### Veo-2 (veo-2.0-generate-001)
- **Priority**: Second choice on each attempt  
- **Model**: `veo-2.0-generate-001`
- **Status**: Widely available
- **Quality**: High quality, proven reliability

## Quota Management

### Rate Limits
- **2 videos per minute** (Google AI Studio limit)
- **50 videos per day** (Tier 1 limit)
- **30 seconds minimum spacing** between generations

### Smart Spacing
```
Generation 1: 00:00 ✓
Generation 2: 00:30 ✓ (30s later)
Generation 3: 01:00 ✓ (30s later)
Generation 4: 01:30 ✓ (30s later)
```

## Enhanced Retry Logic

### Attempt Loop (3 times)
```python
for attempt in range(1, 4):  # 3 attempts
    # Try Veo-3 first
    if veo3_available:
        result = try_veo3()
        if success: return result
    
    # Try Veo-2 as fallback  
    if veo2_available:
        result = try_veo2()
        if success: return result
    
    # Wait 1 minute before next attempt (except last)
    if attempt < 3:
        wait(60_seconds)
```

### Fallback Creation
```python
# All 3 attempts failed
create_fallback_video()
```

## Example Scenarios

### Scenario 1: Success on First Attempt
```
🔄 Attempt 1/3 for video generation
🎬 Attempting Veo-3 generation (8s)...
🎉 Veo-3 (attempt 1) SUCCESS: clip_0.mp4 (9.2MB)
✅ SUCCESS on attempt 1 with Veo-3!
```

### Scenario 2: Success on Second Attempt
```
🔄 Attempt 1/3 for video generation
🎬 Attempting Veo-3 generation (8s)...
⏰ Veo-3 quota exceeded
🎬 Attempting Veo-2 generation (8s)...
⏰ Veo-2 quota exceeded
⏳ Attempt 1 failed. Waiting 1 minute before attempt 2...

🔄 Attempt 2/3 for video generation
🎬 Attempting Veo-3 generation (8s)...
🎉 Veo-3 (attempt 2) SUCCESS: clip_0.mp4 (9.1MB)
✅ SUCCESS on attempt 2 with Veo-3!
```

### Scenario 3: All Attempts Fail
```
🔄 Attempt 1/3 for video generation
⏰ Both models quota exceeded
⏳ Attempt 1 failed. Waiting 1 minute before attempt 2...

🔄 Attempt 2/3 for video generation  
⏰ Both models quota exceeded
⏳ Attempt 2 failed. Waiting 1 minute before attempt 3...

🔄 Attempt 3/3 for video generation
⏰ Both models quota exceeded
❌ All 3 attempts failed

⚫ All AI generation attempts failed - creating fallback video...
✅ Fallback video created: clip_0.mp4 (0.5MB)
```

## Benefits

1. **Triple Attempts**: 3 chances for successful generation
2. **1-Minute Waits**: Allows quota refresh between attempts
3. **Veo-3 Priority**: Always tries latest model first
4. **Systematic Approach**: Clear attempt numbering and logging
5. **Never Fails**: Always produces a video (with fallback)
6. **Clear Progress**: Detailed logging of each attempt

## Timing

- **Maximum wait time**: ~3 minutes (2 × 1-minute waits)
- **Typical success**: First or second attempt
- **Total attempts per clip**: Up to 6 (3 × Veo-3 + 3 × Veo-2)

## Configuration

The retry mechanism is automatic and requires no configuration. It adapts based on:
- Available models (auto-detected)
- Current quota status  
- Time since last generation

## Summary

This enhanced retry mechanism ensures:
- **3 systematic attempts** with clear progression
- **1-minute waits** for optimal quota refresh
- **Veo-3 priority** on every attempt
- **100% completion** rate (with fallback)
- **Clear logging** of all retry attempts

## 🎨 **AI-Powered Text Overlays**

The system now uses Gemini AI to generate engaging text overlays with:

### **Smart Styling**
- **Font Selection**: AI chooses fonts based on video tone
  - Playful content → Rounded fonts
  - Serious content → Bold, clean fonts
  - Dramatic content → Impact fonts
  
- **Color Psychology**: 
  - Energetic → Bright colors (orange, yellow)
  - Calm → Cool colors (blue, green)
  - Emotional → Warm colors (red, pink)

### **Example AI-Generated Overlays**

```json
{
  "overlay_1": {
    "text": "🔥 This Changes EVERYTHING!",
    "font": "Impact",
    "color": "orange",
    "position": "top",
    "timing": "0-3",
    "size": "large"
  },
  "overlay_2": {
    "text": "😱 Watch What Happens Next",
    "font": "Arial-Bold", 
    "color": "yellow",
    "position": "center",
    "timing": "7-12",
    "size": "medium"
  },
  "overlay_3": {
    "text": "👆 FOLLOW for Daily Amazement!",
    "font": "Helvetica-Bold",
    "color": "white",
    "position": "bottom",
    "timing": "12-15",
    "size": "medium"
  }
}
```

## 🎤 **Natural Audio Generation**

Audio now reflects the actual video content with:

### **Content-Aware Speech**
- **Baby Videos**: Gentle, warm, "aww" reactions
- **Amazing Content**: Excited, energetic reactions
- **Test Videos**: Clear, descriptive narration
- **Dramatic Content**: Suspenseful, engaging tone

### **Natural Speech Patterns**
```
Before: "Look at this video content it is amazing"
After:  "Oh wow! Look at this... this is absolutely incredible!"
```

### **Emotional Reactions by Type**
- **Energetic**: "Oh wow!", "This is insane!", "Look at that!"
- **Funny**: "Haha, okay get this...", "I can't even!"
- **Dramatic**: "Listen carefully...", "This changes everything"
- **Emotional**: "This is so beautiful...", "I'm actually tearing up"

## ⚫ **Black Screen Fallback**

When all AI models fail, the system creates a professional black screen with:

- **Smart Text Detection**: Analyzes prompt to show relevant message
- **Professional Look**: Centered white text with subtle shadow
- **Examples**:
  - Baby content → "Baby Moments Coming Soon!"
  - Test videos → "Test Video Processing..."
  - Amazing content → "Amazing Content Ahead!"
  - Default → "Please Stand By..."

## 🚀 **Usage Example**

```bash
python generate_custom_video.py \
  --narrative neutral \
  --feeling energetic \
  --duration 15 \
  --realistic-audio \
  "Create an amazing video with perfect audio"
```

This will:
1. Try Veo-3 → Veo-2 → Wait → Retry sequence
2. Generate AI-styled text overlays
3. Create natural, content-aware audio
4. Fallback to black screen if needed

## 📊 **Performance Benefits**

- **Higher Success Rate**: Multiple retry attempts
- **Better Engagement**: AI-optimized text styling
- **Natural Feel**: Content-aware audio generation
- **Professional Fallback**: Never fails completely

## 🔧 **Configuration**

No configuration needed! The system automatically:
- Detects available Veo models
- Manages retry timing
- Generates appropriate content
- Handles all fallbacks gracefully 