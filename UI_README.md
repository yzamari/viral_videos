# 🎬 Viral Video Generator - Web UI

A comprehensive web interface for the Viral Video Generator with real-time progress tracking, analytics, and session management.

## 🚀 Quick Start

### Option 1: Using the Launch Script (Recommended)
```bash
cd viralAi
./launch_ui.sh
```

### Option 2: Using Python Directly
```bash
cd viralAi
python3 launch_ui.py
```

### Option 3: Manual Launch
```bash
cd viralAi
python3 -m pip install -r requirements.txt
python3 gradio_ui.py
```

## 🌟 Features

### 🎬 Video Generation
- **Interactive Configuration**: Easy-to-use form for all generation parameters
- **Real-time Progress**: Live progress tracking with estimated completion times
- **AI Agent Discussions**: Configurable AI agent collaboration levels
- **Multiple Platforms**: Support for YouTube, TikTok, Instagram, and Twitter
- **Flexible Duration**: Generate videos from 5 seconds to 2 minutes

### 📊 Analytics & Monitoring
- **Generation History**: Track all your video generations with detailed metadata
- **Quota Monitoring**: Real-time API quota status and usage tracking
- **Performance Metrics**: Generation times, success rates, and system health
- **Interactive Charts**: Visual representations of data using Plotly

### 📁 Session Management
- **Session Explorer**: Browse and manage all generation sessions
- **File Downloads**: Download videos, logs, and configuration files
- **Session Analytics**: Detailed insights into each generation session
- **Content Preview**: Preview videos and view file contents directly in the UI

### ⚙️ System Management
- **API Status**: Monitor Google API connection and quota status
- **Cache Management**: Clear system cache and temporary files
- **Configuration**: Easy access to system settings and documentation

## 🖥️ Interface Overview

### Generation Tab
- **Topic Input**: Enter your video topic with smart suggestions
- **Category Selection**: Choose from Comedy, Educational, Entertainment, News, Tech
- **Platform Targeting**: Optimize for specific social media platforms
- **Duration Control**: Set precise video length with slider
- **Advanced Options**: Image-only mode, fallback options, force generation
- **AI Discussions**: Configure agent collaboration depth
- **Real-time Feedback**: Live progress updates and status messages

### Analytics Tab
- **Generation History Table**: Sortable table of all previous generations
- **System Status Dashboard**: API quotas, system health, and performance metrics
- **Interactive Charts**: Visual representation of quota usage and generation trends
- **Refresh Controls**: Manual refresh buttons for real-time data

### Session Explorer Tab
- **Session Browser**: Dropdown list of all generation sessions
- **File Explorer**: Browse all files within selected sessions
- **Content Viewer**: View file contents directly in the interface
- **Download Manager**: Easy file downloads with one-click access
- **Video Player**: Integrated video player for generated content

### Settings Tab
- **API Configuration**: Check and test API connections
- **System Tools**: Cache management and system utilities
- **Documentation**: Built-in help and usage instructions
- **Troubleshooting**: Common issues and solutions

## 🔧 Technical Features

### Real-time Updates
- **WebSocket Integration**: Live progress updates without page refresh
- **Auto-refresh Timers**: Automatic data updates every 2 seconds
- **Background Processing**: Non-blocking video generation
- **Progress Visualization**: Dynamic charts and progress bars

### Data Visualization
- **Plotly Integration**: Interactive charts and graphs
- **Pandas DataFrames**: Structured data display and manipulation
- **Real-time Metrics**: Live updating charts and status indicators
- **Export Capabilities**: Download data in various formats

### Session Management
- **Automatic Organization**: Sessions organized by timestamp and ID
- **Comprehensive Logging**: Detailed logs for debugging and analysis
- **File Management**: Organized file structure with easy navigation
- **Backup and Recovery**: Session data preservation and recovery

## 🛠️ Requirements

### System Requirements
- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space
- Internet connection for API access

### Dependencies
The UI automatically installs required packages:
- `gradio>=4.16.0` - Web interface framework
- `plotly>=5.17.0` - Interactive charts
- `pandas>=2.1.4` - Data manipulation
- `google-generativeai>=0.3.1` - AI model access
- `moviepy>=1.0.3` - Video processing
- All existing project dependencies

## 🔐 Configuration

### Environment Variables
Create a `.env` file in the project root:
```env
GOOGLE_API_KEY=your_google_api_key_here
```

### Optional Configuration
```env
# Custom output directory
OUTPUT_DIR=custom_outputs

# UI Configuration
UI_HOST=0.0.0.0
UI_PORT=7860
UI_SHARE=false
```

## 🚀 Usage Instructions

### 1. Basic Video Generation
1. Open the web interface (usually at `http://localhost:7860`)
2. Navigate to the "Generate Video" tab
3. Enter your video topic
4. Configure generation parameters
5. Click "Generate Video"
6. Monitor real-time progress
7. Download your generated video

### 2. Monitoring Progress
- Watch the progress bar for real-time updates
- Check the status text for current generation stage
- View estimated completion time
- Monitor system resources and API usage

### 3. Exploring Sessions
1. Go to the "Session Explorer" tab
2. Select a session from the dropdown
3. Browse session files
4. Preview videos and view logs
5. Download files as needed

### 4. Analytics and Insights
1. Visit the "Analytics" tab
2. Review generation history
3. Check system status and quotas
4. Analyze performance trends
5. Export data for further analysis

## 🔧 Troubleshooting

### Common Issues

**UI Won't Start**
- Check Python version (3.8+ required)
- Verify all dependencies are installed
- Ensure you're in the correct directory

**API Errors**
- Verify your Google API key is set correctly
- Check API quota limits
- Test API connection in Settings tab

**Generation Fails**
- Check quota status
- Verify topic is appropriate
- Try with force generation enabled
- Check logs in Session Explorer

**Slow Performance**
- Reduce AI discussion depth
- Use image-only mode for faster generation
- Check system resources
- Clear cache if needed

### Debug Mode
Launch with debug mode for detailed logging:
```bash
python3 gradio_ui.py --debug
```

## 📚 API Reference

### Generation Parameters
- `topic`: Video topic string
- `category`: Video category (Comedy, Educational, etc.)
- `platform`: Target platform (youtube, tiktok, etc.)
- `duration`: Video duration in seconds
- `image_only`: Use image-only generation mode
- `fallback_only`: Use fallback generation only
- `force`: Force generation despite quota warnings
- `discussions`: AI discussion level (light, standard, deep)
- `discussion_log`: Enable detailed discussion logging

### Status Codes
- `Ready`: System ready for generation
- `Initializing`: Setting up generation parameters
- `Generating`: Video generation in progress
- `Complete`: Generation finished successfully
- `Error`: Generation failed with error

## 🤝 Contributing

### Development Setup
1. Clone the repository
2. Install development dependencies
3. Run tests: `pytest`
4. Start development server: `python3 gradio_ui.py`

### Adding Features
1. Create feature branch
2. Implement changes
3. Add tests
4. Update documentation
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
1. Check the troubleshooting section
2. Review the documentation
3. Check existing issues
4. Create a new issue with detailed information

## 🔄 Updates

The UI automatically checks for updates and installs required dependencies. For manual updates:
```bash
git pull origin main
pip install -r requirements.txt
```

---

**Happy Video Generating! 🎬✨** 