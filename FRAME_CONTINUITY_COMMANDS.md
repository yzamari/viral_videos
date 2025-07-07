# 🎬 Frame Continuity Commands - Quick Reference

## 🦄 Your Unicorn Israel Video (30-40 seconds)

### Main Command (Recommended):
```bash
python3 main.py generate \
    --category Entertainment \
    --topic "magical unicorns celebrating Israel's victory over Iran with rainbow magic" \
    --frame-continuity \
    --platform youtube
```

### Alternative Commands:
```bash
# Dedicated test script
python3 test_frame_continuity.py

# News-based approach
python3 main.py news "Israel Iran war victory" \
    --angle explainer \
    --duration 35 \
    --feeling dramatic \
    --frame-continuity \
    --platform youtube

# Interactive demo
./run_frame_continuity_demo.sh
```

## 🎬 Frame Continuity Features

### What You Get:
- ✅ **Seamless Transitions**: Last frame of clip1 → first frame of clip2
- ✅ **Professional Quality**: Cinematic flow like one continuous shot
- ✅ **Enhanced Engagement**: No jarring cuts to distract viewers
- ✅ **Multiple Clips**: 4-5 clips of 8 seconds each for 30-40s videos

### Technical Process:
1. Generate first VEO2 clip (8 seconds)
2. Extract last frame: `ffmpeg -i video.mp4 -vf select=eof last_frame.jpg`
3. Use frame as reference for next clip generation
4. Repeat for all clips
5. Compose seamless final video

## 🚀 All Available Commands

### Basic Generation:
```bash
# Without frame continuity (old way)
python3 main.py generate --category Entertainment --topic "cats playing"

# With frame continuity (new way - recommended!)
python3 main.py generate --category Entertainment --topic "cats playing" --frame-continuity
```

### Platform-Specific:
```bash
# YouTube (16:9)
python3 main.py generate --topic "your idea" --frame-continuity --platform youtube

# TikTok (9:16)
python3 main.py generate --topic "your idea" --frame-continuity --platform tiktok

# Instagram
python3 main.py generate --topic "your idea" --frame-continuity --platform instagram
```

### Content Types:
```bash
# Entertainment
python3 main.py generate --category Entertainment --topic "magical adventure" --frame-continuity

# Education  
python3 main.py generate --category Education --topic "how things work" --frame-continuity

# Technology
python3 main.py generate --category Technology --topic "future innovations" --frame-continuity
```

### News & Trending:
```bash
# News with frame continuity
python3 main.py news "trending topic" --frame-continuity --feeling dramatic

# Different angles
python3 main.py news "topic" --angle explainer --frame-continuity
python3 main.py news "topic" --angle reaction --frame-continuity
python3 main.py news "topic" --angle analysis --frame-continuity
```

## 🔧 System Commands

### Check Status:
```bash
# Check quota and system status
python3 main.py quota

# Test frame continuity specifically
python3 test_frame_continuity.py

# Run comprehensive demo
./run_frame_continuity_demo.sh
```

### Troubleshooting:
```bash
# Check Python version
python3 --version

# Check API key
echo $GOOGLE_API_KEY

# Test system health
python3 -c "import src.utils.quota_verification; print('✅ System OK')"
```

## 📁 Output Structure

When you run frame continuity generation, you'll get:

```
outputs/session_[timestamp]_[id]/
├── viral_video_[id].mp4              # 🎬 Final seamless video
├── clips/
│   ├── veo2_clip_scene_0.mp4        # First clip
│   ├── veo2_clip_scene_1.mp4        # Second clip (continues from first)
│   ├── veo2_clip_scene_2.mp4        # Third clip (continues from second)
│   ├── last_frame_scene_0.jpg       # 🖼️ Frame continuity assets
│   └── last_frame_scene_1.jpg       # 🖼️ Frame continuity assets
├── natural_voiceover.mp3            # Audio narration
├── script.txt                       # Generated script
└── video_analysis.json              # Generation metadata
```

## 🎯 Best Practices

### For Optimal Results:
1. **Use 30-40 second duration** for best frame continuity
2. **Choose storytelling topics** that benefit from visual flow
3. **YouTube platform** works best for testing (16:9 format)
4. **Enable frame continuity** with `--frame-continuity` flag
5. **Check quota first** with `python3 main.py quota`

### Perfect Topics for Frame Continuity:
- **Fantasy Adventures**: "magical journey through enchanted forest"
- **Educational Content**: "step-by-step tutorial on solar energy"
- **Product Demos**: "unboxing and reviewing latest gadget"
- **Travel Stories**: "exploring hidden gems in ancient city"
- **Your Request**: "unicorns celebrating Israel's victory with magic"

## 🎉 Ready to Create!

**Start with your unicorn video:**
```bash
python3 main.py generate \
    --category Entertainment \
    --topic "magical unicorns celebrating Israel's victory over Iran with rainbow magic" \
    --frame-continuity \
    --platform youtube
```

**🎬 Experience seamless AI video generation with v2.0!** 