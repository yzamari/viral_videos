# 🎬 Viral Video Generator - Complete Usage Guide

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Clone and navigate to the project
cd viralAi

# Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install google-generativeai gradio moviepy==1.0.3 gtts colorlog Pillow pydantic requests google-auth

# Set environment variables
export GOOGLE_API_KEY="your_gemini_api_key_here"
```

### 2. Basic Usage

#### Web Interface (Recommended)
```bash
# Launch web UI (auto-detects available port)
./run_video_generator.sh ui

# Access at: http://localhost:7860
```

#### Command Line Interface
```bash
# Generate a 10-second comedy video
python launch_full_working_app.py --topic "dancing robots" --duration 10

# Generate with all features
python launch_full_working_app.py \
  --topic "funny cats doing yoga" \
  --duration 30 \
  --platform youtube \
  --category Comedy \
  --discussions
```

## 🎥 VEO-2 Setup (Optional but Recommended)

### Enable Real AI Video Generation

#### 1. Google Cloud Authentication
```bash
# Install Google Cloud SDK
# macOS: brew install google-cloud-sdk
# Ubuntu: sudo apt-get install google-cloud-sdk

# Authenticate
gcloud auth application-default login

# Set project
gcloud config set project viralgen-464411
```

#### 2. Verify VEO-2 Access
```bash
# Test VEO-2 client
python veo_client.py

# Should output: "Video generated successfully"
```

#### 3. Without VEO-2 (Fallback Mode)
- System automatically uses placeholder clips
- All other features work normally
- Still generates professional videos with:
  - 19 AI agent discussions
  - Professional audio
  - Platform optimization

## 🤖 19 AI Agents System

### Agent Categories
1. **Script Development** (4 agents)
   - StoryWeaver: Narrative structure
   - DialogueMaster: Natural dialogue
   - PaceMaster: Timing optimization
   - AudienceAdvocate: User experience

2. **Audio Production** (3 agents)
   - AudioMaster: Audio production
   - VoiceDirector: Voice casting
   - SoundDesigner: Audio design

3. **Visual Design** (5 agents)
   - VisionCraft: Visual storytelling
   - StyleDirector: Art direction
   - ColorMaster: Color psychology
   - TypeMaster: Typography
   - HeaderCraft: Header design

4. **Platform Optimization** (3 agents)
   - PlatformGuru: Platform optimization
   - EngagementHacker: Viral mechanics
   - TrendMaster: Viral trends

5. **Quality Assurance** (4 agents)
   - QualityGuard: Quality standards
   - SyncMaster: Coordination
   - CutMaster: Final assembly
   - AudienceAdvocate: User experience

### Discussion Process
- **5 Phases**: Script → Audio → Visual → Platform → Quality
- **Consensus Target**: 80-90% agreement
- **Duration**: 4-6 minutes total
- **Output**: Professional-grade content decisions

## 📱 Platform Options

### YouTube Shorts (Default)
```bash
--platform youtube
```
- Optimized for 9:16 aspect ratio
- High retention focus
- Algorithm-friendly content

### TikTok
```bash
--platform tiktok
```
- Trend-aware content
- Engagement optimization
- Music integration

### Instagram Reels
```bash
--platform instagram
```
- Visual-first approach
- Story integration
- Hashtag optimization

## 🎯 Content Categories

### Comedy (Default)
```bash
--category Comedy
```
- Humorous content
- Entertainment focus
- Viral potential

### Other Categories
```bash
--category Entertainment  # General entertainment
--category Education     # Educational content
--category Technology    # Tech-focused content
--category Gaming        # Gaming content
--category Music         # Music-related content
```

## ⏱️ Duration Options

### Short Form (10-30 seconds)
```bash
--duration 10   # 1-2 VEO-2 clips
--duration 30   # 3-4 VEO-2 clips
```
- Optimized for Shorts/Reels
- High engagement
- Quick consumption

### Long Form (60+ seconds)
```bash
--duration 60   # 7-8 VEO-2 clips
--duration 120  # 15-16 VEO-2 clips
```
- More detailed content
- Complex narratives
- Educational focus

## 🛠️ Advanced Options

### Skip Agent Discussions (Faster)
```bash
python launch_full_working_app.py --topic "test" --discussions false
```
- Generates in ~2 minutes
- Uses basic configuration
- Good for testing

### Debug Mode
```bash
python launch_full_working_app.py --topic "test" --debug
```
- Verbose logging
- Detailed error messages
- Session file analysis

### Custom Configuration
```python
# Edit launch_full_working_app.py
config = GeneratedVideoConfig(
    target_platform=Platform.YOUTUBE,
    category=VideoCategory.COMEDY,
    duration_seconds=10,
    topic="your custom topic",
    style="your style",
    tone="your tone"
)
```

## 📊 Expected Output

### Successful Generation
```
🎉 SUCCESS!
📹 Video: outputs/session_abc123/final_video.mp4
📁 Session: outputs/session_20250707_123456
⏱️ Time: 348.68s (~6 minutes)
📏 Duration: 10.0s
💾 Size: 0.2MB

🤖 Agent discussions: 15 comprehensive files
🎬 VEO-2 clips: 1-2 real AI videos (if authenticated)
🎵 Audio: Professional TTS with script timing
```

### File Structure
```
outputs/session_abc123/
├── final_video.mp4              # Final composed video
├── video_analysis.txt           # Generation analysis
└── agent_discussions/           # 19 agent discussion files
    ├── enhanced_discussion_script_*.json
    ├── enhanced_discussion_audio_*.json
    ├── enhanced_discussion_visual_*.json
    ├── enhanced_discussion_platform_*.json
    ├── enhanced_discussion_quality_*.json
    └── report_*.md              # Human-readable reports
```

## 🔧 Troubleshooting

### Common Issues

#### 1. "ModuleNotFoundError: No module named 'google.generativeai'"
```bash
# Solution: Install dependencies
pip install google-generativeai gradio moviepy==1.0.3 gtts colorlog Pillow
```

#### 2. "GOOGLE_API_KEY environment variable not set"
```bash
# Solution: Set your Gemini API key
export GOOGLE_API_KEY="your_api_key_here"

# Or add to your shell profile
echo 'export GOOGLE_API_KEY="your_key"' >> ~/.bashrc
source ~/.bashrc
```

#### 3. "VEO-2 generation failed"
```bash
# Check authentication
gcloud auth application-default login

# Verify project access
gcloud config set project viralgen-464411

# Test VEO client
python veo_client.py
```

#### 4. "Agent discussions timeout"
```bash
# Check API key
echo $GOOGLE_API_KEY

# Use faster mode
python launch_full_working_app.py --topic "test" --discussions false
```

#### 5. "Port 7860 already in use"
```bash
# System auto-detects available ports
# Or manually specify:
python launch_full_working_app.py --ui --port 7861
```

### Debug Commands
```bash
# Check session files
ls -la outputs/session_*/

# View agent discussions
cat outputs/session_*/agent_discussions/*.json

# Check video properties
ffprobe outputs/session_*/final_video.mp4

# Test individual components
python veo_client.py                    # Test VEO-2
python -c "import google.generativeai"  # Test Gemini
```

## 🎬 Example Generations

### 1. Comedy Video
```bash
python launch_full_working_app.py \
  --topic "cats learning to use smartphones" \
  --duration 15 \
  --category Comedy \
  --platform youtube
```

### 2. Educational Content
```bash
python launch_full_working_app.py \
  --topic "how quantum computers work" \
  --duration 60 \
  --category Education \
  --platform youtube
```

### 3. Entertainment
```bash
python launch_full_working_app.py \
  --topic "epic battle between pizza and tacos" \
  --duration 30 \
  --category Entertainment \
  --platform tiktok
```

## 📈 Performance Tips

### Faster Generation
- Use `--discussions false` (2-3 minutes)
- Shorter durations (10-15 seconds)
- Skip VEO-2 authentication (fallback mode)

### Higher Quality
- Enable all agent discussions (6-8 minutes)
- Set up VEO-2 authentication
- Use longer durations (30-60 seconds)
- Review and iterate on prompts

### Optimal Settings
```bash
# Balanced approach (recommended)
python launch_full_working_app.py \
  --topic "your topic" \
  --duration 15 \
  --discussions true \
  --platform youtube \
  --category Comedy
```

## 🚀 Production Deployment

### Environment Setup
```bash
# Production environment variables
export GOOGLE_API_KEY="production_key"
export PROJECT_ID="your_production_project"
export GCS_BUCKET_NAME="your_production_bucket"
```

### Batch Processing
```bash
# Generate multiple videos
for topic in "topic1" "topic2" "topic3"; do
  python launch_full_working_app.py --topic "$topic" --duration 15
done
```

### Monitoring
```bash
# Check generation success rates
grep "SUCCESS" outputs/*/video_analysis.txt | wc -l

# Monitor file sizes
du -sh outputs/session_*/final_video.mp4
```

## 📞 Support

### Getting Help
1. **Check logs**: Look at session files and error messages
2. **Debug mode**: Use `--debug` flag for verbose output
3. **Test components**: Run individual tests (VEO-2, Gemini, etc.)
4. **Documentation**: Review README.md and SYSTEM_STATUS.md

### Common Solutions
- **Authentication issues**: Re-run `gcloud auth application-default login`
- **API limits**: Wait a few minutes and retry
- **Memory issues**: Use shorter durations or disable discussions
- **Network issues**: Check internet connection and firewall

---

**🎬 Ready to create viral videos with 19 AI agents and VEO-2!** 