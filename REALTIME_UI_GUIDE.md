# 🎬 Real-time Viral Video Generator UI

**Experience AI agents collaborating in real-time to create viral videos!**

## ✨ Features

### 🤖 **Live AI Agent Discussions**
- Watch 19 specialized AI agents discuss and collaborate
- Real-time consensus tracking with progress bars
- See individual agent messages and reasoning
- Monitor discussion phases: Planning → Script → Visual → Audio → Assembly

### 🎬 **In-Browser Video Playback**
- Play generated videos directly in the browser
- Download videos with one click
- Video file info and metadata display
- Responsive video player

### 🎛️ **Advanced Controls**
- Force generation modes (VEO-3, VEO-2, Image-only)
- Platform optimization (TikTok, YouTube, Instagram, Facebook)
- Duration control (15-120 seconds)
- Category selection (Business, Entertainment, Education, etc.)

### 📊 **Real-time Metrics**
- Generation status tracking
- Active discussion count
- Consensus levels and round progress
- Success/failure indicators

## 🚀 Quick Start

### 1. **Set Environment Variables**
```bash
export GEMINI_API_KEY="your-gemini-api-key-here"
```

### 2. **Launch the UI**
```bash
python launch_realtime_ui.py
```

### 3. **Open Browser**
The UI will automatically open at: **http://localhost:8501**

## 🎯 How to Use

### **Step 1: Enter Mission**
In the sidebar, describe what video you want:
```
An ad for Shakes bar that during day time is shakes bar and 
during night it is alcoholic shakes bar. The ad is for ages 18-31. 
It is business in Israel.
```

### **Step 2: Configure Settings**
- **Platform**: Choose TikTok, YouTube, Instagram, or Facebook
- **Category**: Select Business, Entertainment, Education, etc.
- **Duration**: Set video length (15-120 seconds)
- **Generation Mode**: Choose AI model preference

### **Step 3: Generate & Watch**
1. Click **"🚀 Generate Video"**
2. Watch AI agents discuss in real-time
3. See consensus building and decision-making
4. View the final video when complete

## 🤖 AI Agent Discussion Phases

### **Phase 1: Planning** 🗺️
- ExecutiveChief, SyncMaster, TrendMaster, StoryWeaver
- Strategic planning and resource allocation
- Mission analysis and approach decisions

### **Phase 2: Script Development** 📝
- StoryWeaver, DialogueMaster, PaceMaster, TrendMaster
- Content structure and narrative flow
- Hook, main content, and call-to-action optimization

### **Phase 3: Visual Strategy** 🎨
- VisionCraft, PixelForge, StoryWeaver, SyncMaster
- Visual style and generation strategy
- VEO-2/VEO-3 model selection and parameters

### **Phase 4: Audio Production** 🎵
- AudioMaster, CutMaster, SyncMaster, StoryWeaver
- Voice generation and synchronization
- Audio-visual timing optimization

### **Phase 5: Final Assembly** 🎬
- CutMaster, SyncMaster, AudioMaster, PixelForge
- Video composition and quality assurance
- Final rendering and output optimization

## 🎨 UI Elements

### **Agent Message Cards**
- Beautiful gradient backgrounds
- Agent names and timestamps
- Message content with reasoning
- Consensus indicators

### **Progress Tracking**
- Animated consensus bars
- Round-by-round progress
- Participant count displays
- Phase completion status

### **Video Player**
- Native HTML5 video player
- File size and metadata
- Download functionality
- Responsive design

## 🔧 Technical Details

### **Built With**
- **Streamlit**: Web framework for real-time UI
- **Python Threading**: Background video generation
- **Session State**: Live updates and status tracking
- **HTML5 Video**: In-browser video playback

### **Real-time Updates**
- Auto-refresh during generation
- Live discussion streaming
- Dynamic consensus tracking
- Status change notifications

### **Browser Compatibility**
- Chrome (recommended)
- Firefox
- Safari
- Edge

## 🎯 Example Missions

### **Business Ad**
```
An ad for Shakes bar that during day time is shakes bar and 
during night it is alcoholic shakes bar. The ad is for ages 18-31.
```

### **Educational Content**
```
toys are bad for bed - educational video about sleep hygiene 
and why children shouldn't have toys in their beds
```

### **Entertainment**
```
Funny video about cats vs dogs - which pet is better? 
Comedy style with dramatic music and over-the-top reactions
```

## 🚨 Troubleshooting

### **"API Key Not Found"**
- Set GEMINI_API_KEY environment variable
- Restart the terminal and try again

### **"Video Generation Failed"**
- Check internet connection
- Verify API key is valid
- Try a different generation mode

### **"UI Won't Load"**
- Check if port 8501 is available
- Try: `streamlit run realtime_ui_with_video.py --server.port 8502`

### **"No Video Appears"**
- Wait for generation to complete
- Check the status indicators
- Refresh the page if needed

## 🎉 Success Indicators

✅ **Green Status**: Generation completed successfully  
✅ **High Consensus**: AI agents reached strong agreement  
✅ **Video Ready**: File available for playback/download  
✅ **All Phases Complete**: Full discussion cycle finished  

## 🔮 Advanced Features

### **Force Generation Modes**
- **Auto**: Smart fallback chain (VEO-3 → VEO-2 → Images)
- **Force VEO-3**: Use only the latest VEO-3 model
- **Force VEO-2**: Use only VEO-2 model
- **Force Image**: Use only image generation

### **Platform Optimization**
Each platform gets specialized treatment:
- **TikTok**: 9:16 aspect ratio, trending sounds, quick hooks
- **YouTube**: Optimized for retention and search
- **Instagram**: Square/portrait formats, hashtag optimization
- **Facebook**: Engagement-focused with social sharing

---

**🎬 Ready to watch AI agents create viral videos? Launch the UI and start generating!** 