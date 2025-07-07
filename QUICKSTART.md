# 🚀 Viral Video Generator v2.0 - Quick Start Guide
## Frame Continuity & Seamless Video Generation

Get up and running with AI-powered video generation and revolutionary frame continuity in under 5 minutes!

## ⚡ Setup (5 minutes)

```bash
# 1. Clone and install
git clone <repo-url>
cd viralAi
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Get API keys
# - Google AI Studio: https://aistudio.google.com/app/apikey
# - YouTube API (optional): https://console.cloud.google.com

# 3. Configure
cp env.example .env
# Edit .env with your Google API key:
# GOOGLE_API_KEY=your_key_here
```

## 🎬 Frame Continuity (NEW in v2.0!)

### What is Frame Continuity?
Revolutionary technology that creates seamless transitions between video clips - the last frame of one clip becomes the first frame of the next clip!

### Benefits:
- ✅ **No jarring cuts** between clips
- ✅ **Professional cinematic flow**
- ✅ **Enhanced viewer engagement**
- ✅ **Film-quality production value**

## 🎯 First Run Examples

```bash
# Check system status
python3 main.py quota

# Basic video generation
python3 main.py generate --category Entertainment --topic "cute cats playing"

# 🌟 NEW: Video with Frame Continuity (Recommended!)
python3 main.py generate \
    --category Entertainment \
    --topic "magical unicorns celebrating victory" \
    --frame-continuity \
    --platform youtube

# News-based video with frame continuity
python3 main.py news "AI breakthrough" \
    --angle explainer \
    --feeling inspirational \
    --frame-continuity

# Test frame continuity feature
python3 test_frame_continuity.py
```

## 📊 Advanced Usage

### Analyze Trending Content:
```bash
# Check trends
python3 main.py trends

# Analyze videos for insights
python3 main.py analyze --platform youtube --category Gaming
```

### Multi-Platform Generation:
```bash
# YouTube (16:9)
python3 main.py generate --platform youtube --topic "your idea" --frame-continuity

# TikTok (9:16) 
python3 main.py generate --platform tiktok --topic "your idea" --frame-continuity

# Instagram
python3 main.py generate --platform instagram --topic "your idea" --frame-continuity
```

## 📁 Output Structure

```
outputs/
├── session_20250102_143022_abc123def/    # Session folder
│   ├── viral_video_abc123def.mp4         # 🎬 Final seamless video
│   ├── clips/                            # Individual VEO2 clips
│   │   ├── veo2_clip_scene_0.mp4        # First clip
│   │   ├── veo2_clip_scene_1.mp4        # Second clip (continues from first)
│   │   └── last_frame_scene_0.jpg       # 🖼️ Frame continuity assets
│   ├── natural_voiceover.mp3            # Audio narration
│   ├── script.txt                       # Generated script
│   └── video_analysis.json              # Generation metadata
```

## 🎬 Frame Continuity Examples

### Perfect Use Cases:
- **Storytelling Videos**: "Journey through magical forest" (30-40s)
- **Product Demos**: "Unboxing and review" (seamless flow)
- **Educational Content**: "Step-by-step tutorial" (visual continuity)
- **Entertainment**: "Epic fantasy adventure" (cinematic quality)

### Command Examples:
```bash
# Fantasy/Adventure (Your Request!)
python3 main.py generate \
    --category Entertainment \
    --topic "unicorns loving Israel and celebrating war victory" \
    --frame-continuity \
    --platform youtube

# Educational Content
python3 main.py generate \
    --category Education \
    --topic "how quantum computers work" \
    --frame-continuity \
    --platform youtube

# Product Showcase
python3 main.py generate \
    --category Technology \
    --topic "revolutionary new smartphone features" \
    --frame-continuity \
    --platform instagram
```

## 🔧 Troubleshooting

### Common Issues:
```bash
# "python not found" on macOS
python3 main.py generate --help

# Check API key
echo $GOOGLE_API_KEY

# Test system health
python3 -c "import src.utils.quota_verification; print('✅ System OK')"

# Verify frame continuity
python3 test_frame_continuity.py
```

## 🚀 Ready to Create?

**Start with frame continuity for the best results:**

```bash
python3 main.py generate \
    --category Entertainment \
    --topic "your creative idea here" \
    --frame-continuity \
    --platform youtube
```

**🎬 Experience seamless AI video generation with v2.0!** 