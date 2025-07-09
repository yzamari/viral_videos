# 🚀 Enhanced Viral Video Generator v2.1 - Setup Guide

**Enterprise-Ready Production System with Robust Error Handling**

## 📋 Prerequisites

- **Python 3.8+** (3.10+ recommended for optimal error handling)
- **Google AI Studio API Key** (for Gemini models)
- **Google Cloud Account** (optional, for advanced TTS)
- **Git** for version control
- **6GB RAM** (recommended for error recovery and session management)
- **5GB disk space** (for session logs and error tracking)

## ⚡ Quick Setup (5 minutes)

### 1. Clone and Install
```bash
git clone https://github.com/yzamari/viral_videos.git
cd viral_videos
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp config.env.example config.env
# Edit config.env with your API keys
```

### 3. Test Installation with Error Handling
```bash
# Generate a quick test video (includes error recovery testing)
python3 main.py generate --topic "AI creating amazing content" --duration 10

# Launch web interface with monitoring
python3 simple_test_ui.py
```

## 🔑 API Configuration

### Google AI Studio (Required)
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create API key with sufficient quota
3. Add to `config.env`:
```bash
GOOGLE_API_KEY=your_api_key_here
```

### Google Cloud TTS (Optional - Enhanced Audio)
1. Enable Cloud Text-to-Speech API
2. Create service account
3. Download JSON key
4. Add to `config.env`:
```bash
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
```

## 🛡️ NEW: Reliability Configuration

### Error Handling Settings
Add these to your `config.env` for optimal reliability:
```bash
# Quota Management
ERROR_RETRY_ATTEMPTS=3
QUOTA_RETRY_DELAY=1.0
MAX_BACKOFF_DELAY=8.0

# VEO Content Filtering
VEO_CONTENT_FILTERING=true
VEO_REPHRASING_ATTEMPTS=3

# Session Management
SESSION_CLEANUP_ENABLED=true
SESSION_LOG_RETENTION_DAYS=30

# Monitoring
MONITORING_ENABLED=true
ERROR_TRACKING_ENABLED=true
```

### Performance Optimization
```bash
# Memory Management
MAX_CONCURRENT_AGENTS=5
AGENT_TIMEOUT_SECONDS=30

# Disk Management
MAX_SESSION_SIZE_MB=500
TEMP_FILE_CLEANUP=true
```

## 🎬 Usage Examples

### CLI Commands with Error Handling
```bash
# Generate topic from idea (with automatic retry)
python3 main.py generate-topic --idea "convince people to exercise"

# Generate video with quota management
python3 main.py generate --topic "Quick fitness tips" --duration 30

# Auto-generate video with full error recovery
python3 main.py generate-topic --idea "promote sustainability" --generate-video
```

### Web Interface with Real-time Monitoring
```bash
python3 simple_test_ui.py
# Access at http://localhost:7860
# Features real-time error tracking and recovery status
```

## 🔧 Troubleshooting

### Common Issues & Automatic Solutions

#### Quota Errors (429) - AUTO-RESOLVED ✅
**What happens:** API quota limits reached during generation
**Automatic solution:** 
- System automatically retries with exponential backoff (1s, 2s, 4s)
- Detailed logging shows retry attempts
- Generation continues after quota restoration
- No user intervention required

#### VEO Content Rejections - AUTO-RESOLVED ✅
**What happens:** VEO rejects content due to policy violations
**Automatic solution:**
- Multi-tier content sanitization system activates
- AI-powered rephrasing with Gemini
- Fallback to safe generic prompts
- Up to 3 rephrasing attempts
- Final video generated successfully

#### Session Path Issues - AUTO-RESOLVED ✅
**What happens:** File system errors or path conflicts
**Automatic solution:**
- Consistent `session_timestamp_uid` naming
- Automatic directory creation
- Path validation and error recovery
- All outputs properly organized

### Manual Troubleshooting

#### Installation Issues
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Verify virtual environment
which python3  # Should point to .venv/bin/python3

# Check dependencies
pip list | grep -E "(google|gradio|moviepy)"
```

#### API Configuration
```bash
# Test API key
python3 -c "
import os
from google.generativeai import configure
configure(api_key=os.getenv('GOOGLE_API_KEY'))
print('API key configured successfully')
"
```

#### Session Management
```bash
# Check session directory structure
ls -la outputs/
# Should show session_* directories

# Verify monitoring service
python3 -c "
from src.services.monitoring_service import MonitoringService
monitor = MonitoringService('test_session')
print(f'Log file: {monitor.log_file}')
"
```

### Getting Help
- **Real-time Monitoring**: Check `outputs/session_*/generation_log.txt`
- **Error Logs**: Review `outputs/session_*/error_recovery_log.txt`
- **System Status**: Use `python3 main.py status`
- **Debug Mode**: Set `DEBUG=true` in config.env

## 🎯 Advanced Configuration

### Discussion Modes with Error Handling
- **Light**: Quick consensus, faster generation, basic error recovery
- **Standard**: Balanced discussion and quality, robust error handling
- **Deep**: Thorough analysis, best quality, comprehensive error recovery

### Platform Optimization with Content Filtering
- **YouTube**: Longer form, educational content, content policy compliance
- **TikTok**: Short, viral, jump cuts, trend-safe content
- **Instagram**: Visual focus, engagement, brand-safe filtering
- **Twitter**: Concise, trending topics, policy-compliant content

### Error Recovery Strategies
- **Immediate Retry**: For temporary API failures
- **Exponential Backoff**: For quota management
- **Content Rephrasing**: For policy violations
- **Fallback Systems**: For complete failure scenarios

## 🚀 Production Deployment

### System Requirements
```bash
# Minimum Production Setup
CPU: 2+ cores
RAM: 6GB+ (recommended 8GB)
Storage: 10GB+ free space
Network: Stable internet connection

# Python Environment
Python 3.10+ (recommended)
Virtual environment (required)
All dependencies from requirements.txt
```

### Environment Variables
```bash
# Required
GOOGLE_API_KEY=your_api_key_here

# Optional but Recommended
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
VEO_PROJECT_ID=your_project_id
VEO_LOCATION=us-central1

# Production Settings
ERROR_RETRY_ATTEMPTS=5
QUOTA_RETRY_DELAY=2.0
MONITORING_ENABLED=true
SESSION_CLEANUP_ENABLED=true
```

### Monitoring and Maintenance
```bash
# Check system health
python3 main.py status

# Monitor active sessions
ls -la outputs/session_*/

# Review error logs
tail -f outputs/session_*/error_recovery_log.txt

# Cleanup old sessions (if enabled)
python3 -c "from src.utils.session_manager import SessionManager; SessionManager.cleanup_old_sessions()"
```

## 📊 Performance Tuning

### Memory Optimization
```bash
# Limit concurrent agents
MAX_CONCURRENT_AGENTS=3  # For 6GB RAM
MAX_CONCURRENT_AGENTS=5  # For 8GB+ RAM

# Optimize session cleanup
SESSION_CLEANUP_ENABLED=true
TEMP_FILE_CLEANUP=true
```

### Network Optimization
```bash
# Adjust retry settings for slow connections
QUOTA_RETRY_DELAY=3.0
MAX_BACKOFF_DELAY=15.0
AGENT_TIMEOUT_SECONDS=60
```

### Storage Management
```bash
# Automatic cleanup settings
SESSION_LOG_RETENTION_DAYS=30
MAX_SESSION_SIZE_MB=500
COMPRESS_OLD_SESSIONS=true
```

## 🎉 Verification

### System Health Check
```bash
# Full system test
python3 main.py generate --topic "system test" --duration 5

# Expected output structure:
outputs/
├── session_YYYYMMDD_HHMMSS_abc123/
│   ├── final_video_abc123.mp4 ✅
│   ├── generation_log.txt ✅
│   ├── error_recovery_log.txt ✅
│   └── session_summary.md ✅
```

### Error Handling Verification
```bash
# Test quota management (will auto-recover)
python3 main.py generate --topic "quota test" --duration 10

# Test content filtering (will auto-sanitize)
python3 main.py generate --topic "content with sensitive elements" --duration 10

# Check logs for successful error recovery
grep "ERROR" outputs/session_*/generation_log.txt
grep "RECOVERED" outputs/session_*/error_recovery_log.txt
```

**✅ Ready for production deployment with enterprise-grade reliability!** 🚀 