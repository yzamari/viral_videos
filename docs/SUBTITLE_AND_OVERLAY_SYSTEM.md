# Subtitle and Overlay System Documentation

## Overview

The ViralAI platform features an advanced subtitle timing and dynamic overlay system optimized for viral video content, particularly TikTok.

## Intelligent Subtitle Timing

### Key Features
- **Multiple Segments**: Scripts are automatically split into optimally-timed segments
- **Audio Synchronization**: Perfect timing alignment with generated audio
- **Content-Aware Timing**: Adjusts duration based on content type (hooks, questions, CTAs)
- **Platform Optimization**: Timing optimized for each social media platform

### Technical Implementation

#### Script Segmentation
```python
def _parse_script_into_segments(self, script: str, video_duration: float):
    """Parse script into natural segments based on sentences and timing"""
    # Split on sentence boundaries
    sentences = re.split(r'[.!?]+', script)
    
    # Calculate timing based on complexity
    words_per_second = max(2.0, min(3.0, total_words / video_duration))
    
    # Adjust for content type
    if sentence.startswith(('discover', 'meet', 'what')):
        duration *= 1.3  # Hooks need more time
    elif sentence.endswith(('!', '?')):
        duration *= 1.1  # Questions need emphasis
```

#### Audio-Based Timing
```python
def _intelligent_subtitle_timing(self, segments, video_duration, audio_file):
    """Use script structure for optimal subtitle timing"""
    # Get actual audio duration
    audio_clip = AudioFileClip(audio_file)
    actual_audio_duration = audio_clip.duration
    
    # Calculate timing based on content complexity
    total_words = sum(len(segment.get('text', '').split()) for segment in segments)
    words_per_second = total_words / actual_audio_duration
    
    # Apply content-specific adjustments
    for segment in segments:
        if text.startswith(('discover', 'meet')):
            base_duration *= 1.3  # Hooks
        elif 'follow' in text.lower():
            base_duration *= 0.9  # CTAs
```

### Output Formats
- **SRT**: Standard subtitle format with proper timing
- **VTT**: WebVTT format for web compatibility
- **Metadata**: JSON with timing analysis and statistics

#### Example SRT Output
```srt
1
00:00:00,000 --> 00:00:03,200
Discover: Think subtitles are easy?

2
00:00:03,200 --> 00:00:07,800
We stress-test every pixel and timing.

3
00:00:07,800 --> 00:00:10,000
Follow for more!
```

## Dynamic Overlay System

### Key Features
- **Platform-Aware Animation**: Different strategies for TikTok vs YouTube
- **Mathematical Animations**: Sine wave movements, sliding effects
- **Content-Specific Positioning**: Hooks, CTAs, and main content optimized separately
- **Mobile Optimization**: Designed for vertical video formats

### Technical Implementation

#### Dynamic Positioning Logic
```python
def _get_positioning_decision(self, config, style_info):
    """Determine overlay positioning strategy"""
    platform = config.target_platform.value.lower()
    duration = config.duration_seconds
    
    # Use dynamic positioning for TikTok videos ≤30 seconds
    strategy = "dynamic" if platform == "tiktok" and duration <= 30 else "static"
    
    return {
        "positioning_strategy": strategy,
        "animation_enabled": strategy == "dynamic"
    }
```

#### FFmpeg Animation Implementation
```python
# Hook overlay with sine wave movement
if is_dynamic:
    hook_animation = (
        f"x='if(lt(t,1.5),(w-text_w)/2,"
        f"if(lt(t,3),(w-text_w)/2-20*sin(2*PI*t),w-text_w-20))'"
        f":y='60+10*sin(4*PI*t)'"
    )

# CTA with sliding and bounce effect
cta_animation = (
    f"x='if(lt(t,{video_duration-3}),w+text_w,"
    f"w-text_w-30-15*sin(8*PI*(t-{video_duration-3})))'"
    f":y='120+5*cos(6*PI*t)'"
)
```

### Animation Types

#### 1. Hook Overlays
- **Movement**: Horizontal sine wave with vertical oscillation
- **Timing**: First 3 seconds of video
- **Purpose**: Grab attention immediately

#### 2. CTA Overlays  
- **Movement**: Slide in from right with bounce effect
- **Timing**: Last 3 seconds of video
- **Purpose**: Encourage engagement

#### 3. Subtitle Positioning
- **Strategy**: Bottom-third positioning to avoid UI conflicts
- **Adaptation**: Adjusts for platform-specific UI elements

### Platform-Specific Optimizations

#### TikTok
- **Dynamic overlays** for videos ≤30 seconds
- **Bottom positioning** to avoid interaction buttons
- **High-energy animations** for engagement

#### YouTube Shorts
- **Moderate animation** for broader audience
- **Flexible positioning** based on content type

#### Instagram Reels
- **Subtle animations** aligned with platform aesthetics
- **Story-safe areas** consideration

## Performance Considerations

### Optimization Strategies
- **Efficient FFmpeg filters**: Mathematical expressions over complex operations
- **Minimal file I/O**: Direct filter chaining
- **Smart caching**: Reuse calculated timing data

### Resource Usage
- **Memory**: Moderate increase for timing calculations
- **CPU**: FFmpeg filter processing
- **Disk**: Temporary files for overlay generation

## Testing and Validation

### Automated Tests
```python
def test_subtitle_segmentation():
    """Test multiple subtitle segments are created"""
    segments = generator._parse_script_into_segments(test_script, 15.0)
    assert len(segments) > 1
    assert all(seg['start'] < seg['end'] for seg in segments)

def test_dynamic_overlay_positioning():
    """Test dynamic positioning for TikTok"""
    decision = agent.analyze_positioning("tiktok", "cartoon", 20.0)
    assert decision['positioning_strategy'] == 'dynamic'
    assert decision['animation_enabled'] == True
```

### Quality Metrics
- **Timing Accuracy**: ±0.1 seconds from optimal
- **Readability**: Minimum 1 second per segment
- **Platform Compliance**: UI-safe positioning zones

## Configuration Options

### Subtitle Timing
```json
{
  "subtitle_config": {
    "min_segment_duration": 1.0,
    "max_segment_duration": 6.0,
    "words_per_second_range": [2.0, 3.5],
    "content_multipliers": {
      "hooks": 1.3,
      "questions": 1.1,
      "ctas": 0.9
    }
  }
}
```

### Overlay Animation
```json
{
  "overlay_config": {
    "animation_enabled": true,
    "hook_duration": 3.0,
    "cta_duration": 3.0,
    "movement_intensity": {
      "tiktok": "high",
      "youtube": "medium", 
      "instagram": "low"
    }
  }
}
```

## Future Enhancements

### Planned Features
- **Whisper Integration**: Speech-to-text for precise timing
- **Advanced Animations**: 3D effects, particle systems
- **A/B Testing**: Automatic optimization based on performance
- **Real-time Preview**: Live animation preview during generation

### Research Areas
- **Attention Mapping**: Eye-tracking data for optimal positioning
- **Engagement Analytics**: Performance correlation with animation types
- **Cultural Adaptation**: Region-specific animation preferences