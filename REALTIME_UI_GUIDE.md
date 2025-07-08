# 🎬 Real-time Viral Video Generator UI Guide

## ✨ New Features

The new **Real-time UI** (`realtime_ui.py`) provides **live progress updates** and **streaming output** during video generation, solving the issue where users couldn't see progress updates in the previous UI versions.

## 🚀 Quick Start

### Option 1: Using the Launch Script (Recommended)
```bash
python3 launch_realtime_ui.py
```

### Option 2: Direct Launch
```bash
python3 realtime_ui.py
```

### Option 3: Using the Original Launch Script
```bash
./launch.sh
# Then select option 2 (Launch Web Interface)
```

## 🌐 Access the UI

Once launched, access the UI at: **http://localhost:7860**

## 📊 Key Features

### 1. **Live Progress Updates**
- Real-time progress bar showing current phase and completion percentage
- Visual indicators for each generation phase:
  - 🤖 **Agent Discussions** (10%)
  - 📝 **Script Development** (20%)
  - 🎨 **Visual Design** (35%)
  - 🎤 **Audio Production** (50%)
  - 🎬 **Video Generation** (65%)
  - ✂️ **Video Assembly** (80%)
  - ✅ **Complete** (100%)

### 2. **Streaming Output Log**
- Live streaming of all generation output
- Real-time feedback from AI agents
- Detailed progress messages and status updates

### 3. **Session Information**
- Current session ID and elapsed time
- Generation status tracking
- Output file locations

### 4. **Enhanced Controls**
- Start/Stop generation buttons
- All original configuration options
- Auto-refresh every 2 seconds during generation

## 🎯 Testing with Your Persian Mythology Topic

To test the UI with your original topic:

1. **Launch the UI**: `python3 launch_realtime_ui.py`
2. **Access**: Go to http://localhost:7860
3. **Enter Topic**: "A female character from Persian Mythology"
4. **Configure Settings**:
   - Duration: 30 seconds
   - Category: Entertainment
   - Platform: youtube
   - AI Discussion Mode: standard
   - Frame Continuity: auto
5. **Start Generation**: Click "🚀 Generate Video"
6. **Watch Progress**: Monitor the live progress bar and output log

## 📋 Configuration Options

### Topic Settings
- **Video Topic**: Enter your video subject
- **Duration**: 10-60 seconds
- **Category**: Comedy, Educational, Entertainment, News, Tech
- **Platform**: youtube, tiktok, instagram, twitter

### AI Settings
- **AI Discussion Mode**: 
  - `light`: Quick consensus, faster generation
  - `standard`: Balanced discussion and quality
  - `deep`: Thorough analysis, best quality
- **Frame Continuity**: 
  - `auto`: AI decides based on content
  - `on`: Always enabled for smooth transitions
  - `off`: Disabled for jump cuts

## 🔧 Technical Details

### Real-time Implementation
- Uses `subprocess.Popen()` with streaming output capture
- Background thread processes output in real-time
- Queue-based communication between UI and subprocess
- Progress parsing from main.py output

### Progress Phases
The UI monitors these key phases during generation:

1. **Initialization**: Setting up AI agents and resources
2. **Agent Discussions**: AI agents collaborate on strategy
3. **Script Development**: Creating video script
4. **Visual Design**: Designing visual elements
5. **Audio Production**: Generating voiceover
6. **Video Generation**: Creating video clips with VEO-2
7. **Video Assembly**: Assembling final video
8. **Complete**: Video generation finished

### Output Monitoring
- Real-time parsing of stdout/stderr
- Progress indicators extracted from log messages
- Session tracking and file location detection
- Error handling and status reporting

## 🛠️ Troubleshooting

### UI Not Loading
```bash
# Check if UI is running
curl -s -o /dev/null -w "%{http_code}" http://localhost:7860

# If not running, launch again
python3 launch_realtime_ui.py
```

### Progress Not Updating
- The UI auto-refreshes every 2 seconds
- Check the output log for detailed progress
- Ensure main.py is outputting progress information

### Generation Stuck
- Use the "🛑 Stop Generation" button
- Check the output log for error messages
- Restart the UI if needed

## 📁 Output Files

Generated videos are saved in:
```
outputs/
├── session_YYYYMMDD_HHMMSS_XXXXX/
│   ├── final_video_XXXXX.mp4  # Your generated video
│   ├── clips/                 # Individual video clips
│   ├── audio/                 # Audio files
│   └── agent_discussions/     # AI agent discussion logs
```

## 🔄 Comparison with Previous UIs

### Previous UI Issues:
- ❌ No real-time progress updates
- ❌ Users couldn't see generation status
- ❌ Output only shown after completion
- ❌ No way to monitor AI agent progress

### New Real-time UI:
- ✅ Live progress bar with phase indicators
- ✅ Streaming output log
- ✅ Real-time session information
- ✅ Start/stop controls
- ✅ Auto-refresh functionality
- ✅ Visual progress indicators

## 🎬 Example Usage

Here's what you'll see when generating a video about "A female character from Persian Mythology":

1. **Phase 1**: Agent Discussions (10%) - AI agents plan the video strategy
2. **Phase 2**: Script Development (20%) - Creating script about Persian mythology
3. **Phase 3**: Visual Design (35%) - Designing visual elements for the character
4. **Phase 4**: Audio Production (50%) - Generating voiceover narration
5. **Phase 5**: Video Generation (65%) - Creating video clips with VEO-2
6. **Phase 6**: Video Assembly (80%) - Assembling final video
7. **Phase 7**: Complete (100%) - Video ready in outputs directory

## 📞 Support

If you encounter any issues:
1. Check the output log for error messages
2. Verify your API keys are configured
3. Ensure all dependencies are installed
4. Check the session information for file locations

---

**🎉 Enjoy your new real-time video generation experience!** 