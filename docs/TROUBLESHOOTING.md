# 🛠️ Troubleshooting Guide - Enhanced Viral Video Generator v2.1

**Enterprise-Grade Error Handling and Recovery**

## 🎯 Overview

The Enhanced Viral Video Generator v2.1 includes comprehensive error handling that automatically resolves most issues without user intervention. This guide explains how the system handles errors and what to do when manual intervention is needed.

## 🔄 Automatic Error Recovery

### ✅ **Quota Errors (429) - AUTO-RESOLVED**

**What happens:**
- API quota limits reached during agent discussions
- System receives 429 "Too Many Requests" errors
- Generation appears to pause or slow down

**Automatic solution:**
```
2025-01-09 22:58:10 - WARNING - Quota error for SyncMaster, retrying in 1.0s (attempt 1/3)
2025-01-09 22:58:11 - WARNING - Quota error for SyncMaster, retrying in 2.0s (attempt 2/3)
2025-01-09 22:58:13 - INFO - SyncMaster response successful after retry
```

**How it works:**
1. **Error Detection**: System identifies 429 quota errors
2. **Exponential Backoff**: Retries with increasing delays (1s, 2s, 4s)
3. **Progress Preservation**: All session data maintained during retries
4. **Automatic Recovery**: Generation continues after quota restoration
5. **Logging**: Complete audit trail of retry attempts

**User action required:** None - system handles automatically

### ✅ **VEO Content Rejections - AUTO-RESOLVED**

**What happens:**
- VEO rejects content due to sensitive content policies
- System receives "SENSITIVE_CONTENT_ERROR" response
- Content needs to be sanitized before resubmission

**Automatic solution:**
```
2025-01-09 23:15:22 - WARNING - VEO rejected prompt due to sensitive content, attempting rephrasing...
2025-01-09 23:15:23 - INFO - Rephrasing attempt 1/3 with Gemini
2025-01-09 23:15:25 - INFO - Prompt rephrased successfully
2025-01-09 23:15:26 - INFO - VEO generation successful with sanitized content
```

**How it works:**
1. **Content Detection**: System identifies sensitive content rejection
2. **AI Rephrasing**: Gemini-powered prompt optimization
3. **Fallback Strategies**: Multiple rephrasing approaches
4. **Quality Preservation**: Content quality maintained through sanitization
5. **Final Generation**: Successful video creation with compliant content

**User action required:** None - system handles automatically

### ✅ **Session Path Issues - AUTO-RESOLVED**

**What happens:**
- File system errors or path conflicts
- Missing directories or incorrect paths
- Session organization problems

**Automatic solution:**
```
2025-01-09 23:20:15 - INFO - Creating session directory: outputs/session_20250109_232015_abc123/
2025-01-09 23:20:15 - INFO - MonitoringService initialized with path validation
2025-01-09 23:20:15 - INFO - All session files properly organized
```

**How it works:**
1. **Path Validation**: System checks all file paths before use
2. **Directory Creation**: Automatic creation of missing directories
3. **Consistent Naming**: All sessions use `session_timestamp_uid` format
4. **Error Prevention**: Proactive path validation and correction
5. **File Organization**: All outputs properly contained in session directories

**User action required:** None - system handles automatically

## 🚨 Manual Troubleshooting

### 🔧 **Installation Issues**

#### Python Version Problems
```bash
# Check Python version
python3 --version
# Should be 3.8+ (3.10+ recommended)

# If wrong version, install correct Python
# macOS: brew install python@3.10
# Ubuntu: sudo apt install python3.10
```

#### Virtual Environment Issues
```bash
# Verify virtual environment
which python3
# Should point to .venv/bin/python3

# Recreate if needed
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### Dependency Problems
```bash
# Check critical dependencies
pip list | grep -E "(google|gradio|moviepy)"

# Reinstall if missing
pip install --force-reinstall -r requirements.txt
```

### 🔑 **API Configuration Issues**

#### Google AI Studio API Key
```bash
# Test API key configuration
python3 -c "
import os
from google.generativeai import configure
configure(api_key=os.getenv('GOOGLE_API_KEY'))
print('✅ API key configured successfully')
"
```

#### Quota Limits
```bash
# Check quota status
python3 -c "
from src.utils.quota_verification import check_quota_status
status = check_quota_status()
print(f'Quota status: {status}')
"
```

#### VEO Configuration
```bash
# Verify VEO settings
python3 -c "
import os
print(f'VEO Project: {os.getenv(\"VEO_PROJECT_ID\")}')
print(f'VEO Location: {os.getenv(\"VEO_LOCATION\")}')
"
```

### 📁 **File System Issues**

#### Session Directory Problems
```bash
# Check session structure
ls -la outputs/
# Should show session_* directories

# Verify permissions
ls -la outputs/session_*/
# Should be readable/writable

# Clean up if needed
python3 -c "
from src.utils.session_manager import SessionManager
SessionManager.cleanup_old_sessions()
"
```

#### Disk Space Issues
```bash
# Check available space
df -h .
# Should have 5GB+ free

# Clean up old sessions
find outputs/ -name "session_*" -mtime +30 -exec rm -rf {} \;
```

### 🌐 **Network Issues**

#### Connection Problems
```bash
# Test internet connectivity
ping -c 3 generativelanguage.googleapis.com

# Test API endpoint
curl -s "https://generativelanguage.googleapis.com/v1/models?key=$GOOGLE_API_KEY" | head -c 100
```

#### Timeout Issues
```bash
# Increase timeout settings in config.env
AGENT_TIMEOUT_SECONDS=60
NETWORK_TIMEOUT_SECONDS=30
```

## 📊 **Monitoring and Diagnostics**

### 📈 **System Health Check**
```bash
# Run comprehensive system test
python3 main.py generate --topic "system health check" --duration 5

# Check for errors
grep -i error outputs/session_*/generation_log.txt
```

### 🔍 **Error Log Analysis**
```bash
# View recent errors
tail -f outputs/session_*/error_recovery_log.txt

# Search for specific error types
grep "QUOTA_ERROR" outputs/session_*/generation_log.txt
grep "SENSITIVE_CONTENT" outputs/session_*/generation_log.txt
grep "PATH_ERROR" outputs/session_*/generation_log.txt
```

### 📋 **Session Status**
```bash
# Check active sessions
python3 main.py status

# View session details
cat outputs/session_*/session_summary.md
```

## 🎯 **Performance Optimization**

### 💾 **Memory Optimization**
```bash
# Monitor memory usage
python3 -c "
import psutil
print(f'Memory usage: {psutil.virtual_memory().percent}%')
print(f'Available: {psutil.virtual_memory().available / 1024**3:.1f}GB')
"

# Optimize for limited memory
# In config.env:
MAX_CONCURRENT_AGENTS=3
AGENT_MEMORY_LIMIT=512MB
```

### 🚀 **Speed Optimization**
```bash
# Use light discussion mode for faster generation
python3 main.py generate --topic "test" --duration 10 --discussions light

# Optimize retry settings
# In config.env:
ERROR_RETRY_ATTEMPTS=2
QUOTA_RETRY_DELAY=0.5
```

### 🌐 **Network Optimization**
```bash
# Optimize for slow connections
# In config.env:
NETWORK_TIMEOUT_SECONDS=60
MAX_BACKOFF_DELAY=15.0
AGENT_TIMEOUT_SECONDS=90
```

## 🔧 **Advanced Troubleshooting**

### 🤖 **AI Agent Issues**
```bash
# Test individual agent responses
python3 -c "
from src.agents.enhanced_multi_agent_discussion import EnhancedMultiAgentDiscussionSystem
system = EnhancedMultiAgentDiscussionSystem()
print('✅ Discussion system initialized')
"

# Check agent personalities
python3 -c "
from src.agents.enhanced_multi_agent_discussion import AgentRole
print('Available agents:', list(AgentRole))
"
```

### 🎬 **Video Generation Issues**
```bash
# Test video generation components
python3 -c "
from src.generators.vertex_ai_veo2_client import VertexAIVeo2Client
client = VertexAIVeo2Client('test', 'us-central1', 'test-bucket', 'test-output')
print('✅ VEO client initialized')
"

# Test audio generation
python3 -c "
from src.generators.google_tts_client import GoogleTTSClient
client = GoogleTTSClient()
print('✅ TTS client initialized')
"
```

### 🔍 **Debug Mode**
```bash
# Enable debug logging
export DEBUG=true
python3 main.py generate --topic "debug test" --duration 5

# View debug logs
grep -i debug outputs/session_*/generation_log.txt
```

## 📞 **Getting Help**

### 🆘 **When to Seek Help**
- System fails after multiple automatic recovery attempts
- Persistent API authentication issues
- Unusual error patterns not covered in this guide
- Performance issues not resolved by optimization

### 📋 **Information to Provide**
1. **Error logs**: Contents of `outputs/session_*/error_recovery_log.txt`
2. **System info**: Python version, OS, available memory
3. **Configuration**: Relevant settings from `config.env`
4. **Steps to reproduce**: Exact commands and parameters used
5. **Session ID**: Timestamp and session identifier

### 🔗 **Support Resources**
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check README.md and docs/ folder
- **Community**: Discussions tab for questions
- **Error Logs**: Always include relevant log files

## ✅ **Success Indicators**

### 🎯 **Healthy System**
- Sessions complete without manual intervention
- Error logs show successful recovery attempts
- Consistent session directory structure
- Regular quota error recovery without failures

### 📊 **Performance Metrics**
- Generation time within expected ranges
- Memory usage stable during generation
- Error recovery success rate above 95%
- Session organization 100% consistent

### 🚀 **Ready for Production**
- All tests pass without manual intervention
- Error handling working for all scenarios
- Monitoring showing healthy system status
- Documentation reviewed and understood

---

**🎬 Enhanced Viral Video Generator v2.1 - Enterprise-Ready Error Handling!** 🚀

*Remember: The system is designed to handle most errors automatically. This guide is for the rare cases where manual intervention is needed.* 