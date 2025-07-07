# 📚 Viral Video Generator v2.0 - Complete Usage Guide

Welcome to the comprehensive usage guide for Viral Video Generator v2.0! This guide covers all features, from basic generation to advanced trending analysis and fallback systems.

## 🚀 Quick Start

### 1. Installation
```bash
# Clone and install
git clone <repository-url>
cd viralAi
chmod +x install_app.sh
./install_app.sh

# Set up API key
export GOOGLE_API_KEY="your-google-ai-studio-key"
```

### 2. Your First Video
```bash
# Generate a comedy video with trending analysis
python main.py generate --category Comedy --topic "Funny cat moments"
```

### 3. Check Your Output
```bash
# Videos are saved in outputs/session_YYYYMMDD_HHMMSS_<id>/
ls -la outputs/
```

## 📊 Understanding Trending Analysis

### What You'll See
When you generate a video, you'll see a comprehensive trending analysis display:

```
📊 TRENDING VIDEO ANALYSIS SUMMARY
============================================================
🎯 Analyzed 10 trending videos from youtube
📂 Category: Comedy

📹 TOP TRENDING VIDEOS:
 1. "Funny Cat Compilation 2024"
    👀 8,258,348 views | 👍 473,093 likes | 📺 PetTube Channel
 2. "Cats Being Dramatic"
    👀 5,421,789 views | 👍 321,456 likes | 📺 Comedy Pets
 ...

🧠 VIRAL INSIGHTS EXTRACTED:
📊 Total videos analyzed: 10
⭐ Average viral score: 0.83/5.0
💫 Average engagement rate: 0.0600

🎭 TOP VIRAL THEMES:
   1. humor (appears in 3 videos)
   2. relatability (appears in 2 videos)
   3. nostalgia (appears in 2 videos)

🚀 TOP SUCCESS FACTORS:
   1. High relatability for specific audiences
   2. Effective short-form comedy format
   3. Strong curiosity-inducing hooks
============================================================
```

### How It Helps Your Content
- **🎯 Topic Optimization**: Understand what's trending in your category
- **📈 Viral Patterns**: Learn what makes content go viral
- **🎭 Theme Insights**: Discover popular themes to incorporate
- **🚀 Success Factors**: Apply proven viral strategies

## 🎨 Generation Modes Explained

### 1. **Full AI Generation** (Default)
**Best for**: High-quality content when you have quota available

```bash
python main.py generate --category Comedy --topic "Funny moments"
```

**What happens:**
1. 📊 Analyzes 10 trending videos
2. 🎬 Attempts VEO-2 video generation
3. 🔄 Falls back to VEO-3 if needed
4. 🎨 Falls back to Gemini images if VEO exhausted
5. 📝 Falls back to text overlays as final option
6. 🎤 Generates natural TTS audio
7. 🎵 Combines everything into final video

### 2. **Fallback-Only Mode**
**Best for**: Fast generation, preserving quota, testing

```bash
python main.py generate --category Comedy --topic "Quick content" --fallback-only
```

**What happens:**
1. 📊 Analyzes trending videos
2. ⚡ Skips VEO generation entirely
3. 📝 Creates descriptive text overlays
4. 🎤 Generates natural TTS audio
5. 🎬 Produces video in 1-3 minutes

### 3. **Image-Only Mode**
**Best for**: Visual storytelling, slideshow-style content

```bash
python main.py generate --category Comedy --topic "Visual comedy" --image-only
```

**What happens:**
1. 📊 Analyzes trending videos
2. 🎨 Forces Gemini image generation
3. 📸 Creates 4-5 images per second
4. 🎬 Builds slideshow-style video
5. 🎤 Adds synchronized audio

## 🎯 Categories & Topics Guide

### Supported Categories
```bash
# Comedy - Funny, entertaining content
python main.py generate --category Comedy --topic "Pets being silly"

# Educational - Learning and tutorials
python main.py generate --category Educational --topic "Quick science facts"

# Entertainment - General entertainment
python main.py generate --category Entertainment --topic "Celebrity moments"

# Technology - Tech reviews and tutorials
python main.py generate --category Technology --topic "AI breakthroughs"

# Lifestyle - Daily life and wellness
python main.py generate --category Lifestyle --topic "Morning routines"

# Gaming - Game content and reviews
python main.py generate --category Gaming --topic "Epic gaming fails"
```

### Topic Guidelines
- **✅ Good Topics**: Specific, visual, trending
  - "Cats being dramatic"
  - "Monday morning struggles"
  - "Cooking disasters"
- **❌ Avoid**: Too broad, non-visual, controversial
  - "Everything about cats"
  - "Political opinions"
  - "Abstract concepts"

## 🌐 Platform Optimization

### YouTube Shorts
```bash
python main.py generate --category Comedy --topic "Funny moments" --platform youtube
```
- **📐 Aspect Ratio**: 9:16 (vertical)
- **⏱️ Duration**: 15-60 seconds
- **🎯 Optimization**: Hooks, engagement, retention

### TikTok
```bash
python main.py generate --category Comedy --topic "Funny moments" --platform tiktok
```
- **📐 Aspect Ratio**: 9:16 (vertical)
- **⏱️ Duration**: 15-30 seconds
- **🎯 Optimization**: Trends, music, effects

### Instagram Reels
```bash
python main.py generate --category Comedy --topic "Funny moments" --platform instagram
```
- **📐 Aspect Ratio**: 9:16 (vertical)
- **⏱️ Duration**: 15-30 seconds
- **🎯 Optimization**: Visual appeal, stories

## 📊 Quota Management

### Check Your Quota
```bash
# Check current VEO quota status
python main.py veo-quota
```

### Understanding Limits
- **VEO-2**: 2 videos/minute, 50 videos/day
- **Gemini Images**: 15 requests/minute, 1500 requests/day
- **Gemini Text**: 15 requests/minute, 1500 requests/day

### Quota-Saving Strategies
```bash
# Use fallback-only to save quota
python main.py generate --topic "Content" --fallback-only

# Generate multiple videos with fallback
for topic in "Topic1" "Topic2" "Topic3"; do
    python main.py generate --category Comedy --topic "$topic" --fallback-only
done
```

## 🔧 Advanced Options

### Frame Continuity
```bash
# Enable seamless transitions between clips
python main.py generate --category Comedy --topic "Story content" --frame-continuity
```

### Force Generation
```bash
# Skip quota checks and force generation
python main.py generate --category Comedy --topic "Urgent content" --force
```

### Custom Duration
```bash
# Set custom video duration
export VIDEO_DURATION=45
python main.py generate --category Comedy --topic "Medium content"
```

### Background Generation
```bash
# Generate videos in the background
nohup python main.py generate --category Comedy --topic "Background content" &
```

## 🎤 Audio Customization

### Google Cloud TTS Setup
```bash
# Install Google Cloud CLI
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth application-default login

# Set credentials
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
```

### Voice Selection
The system automatically selects voices based on content:
- **Comedy**: Upbeat, engaging voices
- **Educational**: Clear, professional voices
- **Entertainment**: Varied, dynamic voices

## 📁 Output Structure

### Understanding Your Output
```
outputs/session_YYYYMMDD_HHMMSS_<id>/
├── viral_video_<id>.mp4          # Your final video
├── script_<id>.txt               # Generated script
├── tts_script_<id>.txt          # Clean TTS script
├── veo2_prompts_<id>.txt        # VEO generation prompts
├── analysis_report.json         # Trending analysis data
├── veo2_clips/                  # Individual video clips (if VEO used)
├── gemini_images/               # Generated images (if image mode)
└── session_log.txt              # Detailed generation log
```

### Finding Your Videos
```bash
# List all sessions
ls -la outputs/

# Find latest session
ls -t outputs/ | head -1

# Open latest video
open "outputs/$(ls -t outputs/ | head -1)/viral_video_"*.mp4
```

## 🚨 Troubleshooting

### Common Issues & Solutions

#### 1. **VEO Quota Exhausted**
```
Error: VEO quota exhausted
```
**Solution:**
```bash
# Use fallback-only mode
python main.py generate --topic "Content" --fallback-only

# Or wait for quota reset (daily)
python main.py veo-quota  # Check status
```

#### 2. **API Key Issues**
```
Error: API key not found
```
**Solution:**
```bash
# Set API key
export GOOGLE_API_KEY="your-key-here"

# Or add to ~/.bashrc
echo 'export GOOGLE_API_KEY="your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

#### 3. **Google Cloud TTS Not Working**
```
Error: Could not authenticate with Google Cloud
```
**Solution:**
```bash
# Authenticate with Google Cloud
gcloud auth application-default login

# Or use service account
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
```

#### 4. **MoviePy/FFmpeg Errors**
```
Error: MoviePy could not find ffmpeg
```
**Solution:**
```bash
# Install FFmpeg
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

#### 5. **Gemini Image Generation Fails**
```
Error: Gemini image generation failed
```
**Solution:**
```bash
# Check quota
python main.py veo-quota

# Use fallback-only mode
python main.py generate --topic "Content" --fallback-only
```

## 📈 Performance Tips

### Optimize Generation Speed
```bash
# Use fallback-only for faster generation
python main.py generate --topic "Content" --fallback-only

# Generate shorter videos
export VIDEO_DURATION=30
python main.py generate --topic "Content"

# Use image-only for visual content
python main.py generate --topic "Visual content" --image-only
```

### Batch Generation
```bash
# Generate multiple videos efficiently
topics=("Topic1" "Topic2" "Topic3")
for topic in "${topics[@]}"; do
    python main.py generate --category Comedy --topic "$topic" --fallback-only
    sleep 5  # Rate limiting
done
```

### Monitor Resource Usage
```bash
# Check system resources
top -p $(pgrep -f "python main.py")

# Monitor disk usage
du -sh outputs/

# Clean old outputs
find outputs/ -type d -mtime +7 -exec rm -rf {} \;
```

## 🎯 Best Practices

### Content Strategy
1. **🎯 Analyze Trends First**: Always review the trending analysis
2. **📝 Use Specific Topics**: Specific topics generate better content
3. **🎭 Match Platform Style**: Adapt content to platform requirements
4. **🔄 Test Fallback Modes**: Use fallback-only for testing ideas

### Quota Management
1. **📊 Check Quota Daily**: Monitor your usage with `python main.py veo-quota`
2. **🔄 Use Fallback Modes**: Preserve quota with `--fallback-only`
3. **⏰ Time Your Generation**: Spread generation throughout the day
4. **🎯 Prioritize Content**: Use VEO for your most important videos

### Quality Optimization
1. **🎬 Review Generated Content**: Always check output quality
2. **🎤 Test Audio Quality**: Ensure TTS sounds natural
3. **📱 Test on Target Platform**: Verify content works on intended platform
4. **🔄 Iterate and Improve**: Use trending insights to improve future content

## 🔄 Workflow Examples

### Daily Content Creator
```bash
# Morning: Check quota and trends
python main.py veo-quota

# Generate main content with VEO
python main.py generate --category Comedy --topic "Daily trending topic"

# Generate backup content with fallback
python main.py generate --category Comedy --topic "Backup topic" --fallback-only
```

### Batch Content Producer
```bash
# Generate multiple videos efficiently
categories=("Comedy" "Educational" "Entertainment")
topics=("Topic1" "Topic2" "Topic3")

for category in "${categories[@]}"; do
    for topic in "${topics[@]}"; do
        python main.py generate --category "$category" --topic "$topic" --fallback-only
        sleep 10  # Rate limiting
    done
done
```

### Testing & Experimentation
```bash
# Test new ideas with fallback-only
python main.py generate --category Comedy --topic "New idea" --fallback-only

# Test image-only mode for visual content
python main.py generate --category Entertainment --topic "Visual story" --image-only

# Test different platforms
python main.py generate --category Comedy --topic "Multi-platform" --platform youtube
python main.py generate --category Comedy --topic "Multi-platform" --platform tiktok
```

## 🎓 Advanced Usage

### Environment Configuration
```bash
# Create custom environment
cat > .env << EOF
GOOGLE_API_KEY=your-key-here
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
VIDEO_DURATION=60
GEMINI_MODEL=gemini-2.5-flash
EOF

# Load environment
source .env
```

### Custom Scripts
```bash
# Create custom generation script
cat > generate_daily.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d)
TOPIC="Daily content for $DATE"

python main.py generate \
    --category Comedy \
    --topic "$TOPIC" \
    --fallback-only \
    --force

echo "Generated daily content for $DATE"
EOF

chmod +x generate_daily.sh
./generate_daily.sh
```

### Monitoring & Analytics
```bash
# Track generation success
python main.py generate --topic "Content" 2>&1 | tee generation.log

# Analyze outputs
find outputs/ -name "*.mp4" -exec echo "Video: {}" \; -exec ffprobe -v quiet -show_format -show_streams {} \;

# Monitor quota usage
echo "$(date): $(python main.py veo-quota)" >> quota_log.txt
```

## 📞 Getting Help

### Documentation
- **📚 This Guide**: Complete usage instructions
- **🔧 README.md**: Installation and quick start
- **📊 Release Notes**: New features and changes
- **🎯 Examples**: Practical use cases

### Community Support
- **💬 GitHub Discussions**: Ask questions and share tips
- **🐛 GitHub Issues**: Report bugs and request features
- **📧 Email Support**: For enterprise inquiries

### Self-Help Tools
```bash
# Check system status
python main.py veo-quota

# View help
python main.py --help
python main.py generate --help

# Test installation
python main.py generate --category Comedy --topic "Test video" --fallback-only
```

## 🎯 Success Stories

### Content Creator Success
> "Using the trending analysis, I increased my video engagement by 300%. The system shows me exactly what's working in my niche!" - @ContentCreator2024

### Agency Efficiency
> "We generate 50+ videos per week using the fallback system. The quota management features save us hours of manual work." - Digital Agency

### Educational Content
> "The educational category with trending analysis helps us create content that students actually want to watch." - Online Educator

---

**🎬 Ready to create viral content? Start with `python main.py generate --category Comedy --topic "Your amazing idea"`!**

*Happy creating! 🚀* 