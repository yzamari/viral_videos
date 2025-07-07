# Viral Video Generator - Features Summary

## 🎬 Video Generation Modes

### 1. **Fallback-Only Mode**
- **Flag**: `--fallback-only`
- **Purpose**: Generate videos without using VEO2/VEO3 quota
- **Features**:
  - Black screen with descriptive text overlays
  - Full script and audio generation
  - Scene descriptions of what would be shown
  - No API quota consumption

### 2. **Image-Only Mode**
- **Flag**: `--image-only`
- **Purpose**: Generate videos using AI-generated images instead of VEO
- **Features**:
  - 2-3 images per second of video
  - Coherent visual storytelling
  - Scene progression (establishing → medium → close-up)
  - Dynamic color schemes based on content
  - High-resolution 1920x1080 images

### 3. **Frame Continuity Mode**
- **Flag**: `--frame-continuity` (or AI auto-decides)
- **Purpose**: Create seamless long-form videos
- **Features**:
  - AI director decides when to use continuity
  - Last frame of clip N-1 flows into first frame of clip N
  - Multiple transition strategies
  - Platform and content-aware decisions

## 🤖 AI Director Capabilities

### Automatic Frame Continuity Decision
The director analyzes:
- **Content Style**: Documentary, journey, tutorial → continuity
- **Platform**: YouTube (0.7) vs TikTok (0.3) preference
- **Category**: Education (0.8) vs Comedy (0.3) preference
- **Duration**: Longer videos benefit more from continuity

### Transition Strategies
1. **Smooth Motion**: Camera movement continues across clips
2. **Object Tracking**: Follow same subject across clips
3. **Environment Flow**: Natural space/time progression
4. **Narrative Continuity**: Story flows seamlessly

## 📊 Quota Management

### Real Google Quota Integration
- **Command**: `python3 main.py veo-quota`
- **Features**:
  - Real-time quota checking via Google AI SDK
  - Model availability verification
  - No local quota tracking (removed)
  - Direct API testing for usage estimation

### Fallback Chain
1. Try VEO-2 generation
2. If quota exhausted → Try VEO-3
3. If both fail → Use AI image generation
4. Final fallback → Descriptive text overlays

## 🎨 Content Generation

### Script Variety System
- Multiple hook templates
- Varied content structures
- Dynamic prompt generation
- Prevents repetitive phrases

### Enhanced TTS
- Cleaned scripts without literal "LIKE" or "POV"
- Natural speech patterns
- Emotional context support
- Duration-optimized content

### Text Overlays
- AI-generated overlays matching script
- Proper positioning (no cutoffs)
- Dynamic timing based on content
- Scene-appropriate text

## 🎯 Video Duration Control
- Respects `VIDEO_DURATION` environment variable
- Proper clip count calculation
- Audio-video synchronization
- Frame-accurate timing

## 🔧 CLI Commands

### Generate Videos
```bash
# Basic generation (AI decides everything)
python3 main.py generate --topic "Your topic" --platform youtube --category tech

# Fallback only (no VEO quota)
python3 main.py generate --topic "Your topic" --fallback-only

# Image-based generation
python3 main.py generate --topic "Your topic" --image-only

# Force frame continuity
python3 main.py generate --topic "Your topic" --frame-continuity

# Combine flags
python3 main.py generate --topic "Your topic" --fallback-only --frame-continuity
```

### Check Quota
```bash
# Check VEO-specific quota
python3 main.py veo-quota

# Check before generation
python3 main.py generate --topic "Your topic" --check-veo-quota
```

### News Videos
```bash
# Generate news-based video
python3 main.py news "tech innovation" --platform youtube --angle pro_technology
```

## 📁 Output Structure
```
outputs/
├── session_[timestamp]_[id]/
│   ├── script_[id].txt           # Full script
│   ├── tts_script_[id].txt       # Clean TTS script
│   ├── veo2_prompts_[id].txt     # VEO2 prompts
│   ├── clips/                    # Individual clips
│   ├── scene_images/             # AI-generated images
│   └── viral_video_[id].mp4      # Final video
```

## 🚀 Performance Features

### Parallel Processing
- Multiple tool calls executed simultaneously
- Efficient information gathering
- Reduced generation time

### Smart Fallbacks
- Graceful degradation when APIs fail
- Multiple fallback levels
- Always produces output

### Memory Efficiency
- Proper resource cleanup
- Optimized video processing
- Minimal disk usage

## 🎭 Content Quality

### Viral Optimization
- Pattern analysis from trending videos
- Platform-specific adaptations
- Engagement-focused hooks
- Optimized pacing

### Multi-Language Support
- Primary and additional languages
- Translated scripts and overlays
- Culture-aware adaptations

## 🔒 Error Handling

### Robust Recovery
- API failure handling
- Quota exhaustion management
- Network error recovery
- Syntax error prevention

### Validation
- Content policy compliance
- Script format verification
- Duration validation
- File integrity checks

---

*This system represents a complete viral video generation platform with intelligent fallbacks, quota management, and professional video creation capabilities.* 