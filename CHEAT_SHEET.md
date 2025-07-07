# 🎬 Viral AI Video Generator - Quick Start Cheat Sheet

## 🚀 **ONE-LINE QUICK START**
```bash
./run_video_generator.sh --test
```
*Generates a 15-second test video with AI voice in under 2 minutes*

---

## 📋 **ESSENTIAL COMMANDS**

### **Quick Generation (No Setup Required)**
```bash
# 🧪 Test video (15 seconds)
./run_video_generator.sh --test

# ⚡ Quick viral video (30 seconds) 
./run_video_generator.sh --quick

# 🔥 Trending content
./run_video_generator.sh --viral

# 👶 Baby content
./run_video_generator.sh --baby
```

### **Check Status**
```bash
# 📊 Check Google quota
./run_video_generator.sh --quota

# ℹ️ Show all options
./run_video_generator.sh --help
```

### **Interactive Mode**
```bash
# 🎨 Custom interactive generation
./run_video_generator.sh --custom
```

---

## 🎯 **ADVANCED ONE-LINERS**

### **Direct Python Commands**
```bash
# Basic video generation
python generate_custom_video.py "Amazing AI technology breakthrough"

# 30-second energetic video with TTS
python generate_custom_video.py --duration 30 --feeling energetic --realistic-audio "Mind-blowing tech innovation"

# Multi-language viral content
python generate_custom_video.py --languages english arabic hebrew "Global trending news"

# Professional style with specific emotion
python generate_custom_video.py --style professional --feeling inspirational --duration 60 "Future of AI technology"
```

### **CLI Main Commands**
```bash
# Check quota only
python main.py quota

# Generate with full system (includes trending analysis)
python main.py generate --category Technology --topic "AI breakthrough"
```

---

## ⚙️ **SETUP COMMANDS**

### **First Time Setup**
```bash
# 1. Clone repository
git clone https://github.com/yzamari/viralAi.git
cd viralAi

# 2. Setup environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configure API key
cp env.example .env
# Edit .env file and add your GOOGLE_API_KEY

# 4. Test installation
./run_video_generator.sh --test
```

### **Quick Environment Check**
```bash
# Check if everything is working
python -c "import src.generators.optimized_veo_client; print('✅ Setup OK')"
```

---

## 🎬 **VIDEO GENERATION OPTIONS**

### **Duration Options**
```bash
# Quick test (15 seconds)
./run_video_generator.sh --test

# Standard (30 seconds) 
python generate_custom_video.py --duration 30 "Your prompt here"

# Long form (60 seconds)
python generate_custom_video.py --duration 60 "Your prompt here"
```

### **Style & Emotion Combos**
```bash
# Funny energetic content
python generate_custom_video.py --feeling funny --style engaging "Hilarious life hack"

# Professional inspiration
python generate_custom_video.py --feeling inspirational --style professional "Success story"

# Emotional family content
python generate_custom_video.py --feeling emotional --narrative pro_family "Family moments"
```

### **Audio Options**
```bash
# With realistic Google TTS voice
python generate_custom_video.py --realistic-audio "Your content here"

# Multi-language versions
python generate_custom_video.py --languages english arabic hebrew "Global content"

# Both realistic voice AND multi-language
python generate_custom_video.py --realistic-audio --languages english arabic "Professional content"
```

---

## 📊 **QUOTA MANAGEMENT**

### **Check & Monitor**
```bash
# Quick quota check
python main.py quota

# Detailed status via shell script
./run_video_generator.sh --quota

# Check before generation (automatic)
./run_video_generator.sh --viral  # Auto-checks quota first
```

### **Understanding Limits**
- **Daily Limit**: 50 video generations per day
- **Rate Limit**: 2 videos per minute (30-second spacing)
- **Optimization**: 8-second clips = 50% fewer API calls
- **Reset Time**: Midnight (Google's timezone)

---

## 🎯 **RECOMMENDED WORKFLOWS**

### **First Time User**
```bash
# 1. Test everything works
./run_video_generator.sh --test

# 2. Check quota status
./run_video_generator.sh --quota

# 3. Generate your first real video
./run_video_generator.sh --custom
```

### **Daily Content Creator**
```bash
# Morning quota check
./run_video_generator.sh --quota

# Generate multiple videos efficiently
python generate_custom_video.py --duration 30 "Topic 1"
# Wait 30 seconds (rate limit)
python generate_custom_video.py --duration 30 "Topic 2"
```

### **Professional Production**
```bash
# High-quality multi-language content
python generate_custom_video.py \
  --duration 60 \
  --style professional \
  --feeling inspirational \
  --realistic-audio \
  --languages english arabic hebrew \
  "Professional presentation topic"
```

---

## 🔧 **TROUBLESHOOTING**

### **Common Issues**
```bash
# API key not found
echo "GOOGLE_API_KEY=your_key_here" >> .env

# Quota exhausted
./run_video_generator.sh --quota  # Check reset time

# Virtual environment issues
source venv/bin/activate

# Permission denied
chmod +x run_video_generator.sh
```

### **Quick Diagnostics**
```bash
# Test API connection
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('✅ API Key:', 'Found' if os.getenv('GOOGLE_API_KEY') else 'Missing')"

# Test quota system
python main.py quota

# Test video generation (dry run)
python generate_custom_video.py --help
```

---

## 💡 **PRO TIPS**

### **Cost Optimization**
- ✅ **Veo-3 is disabled by default** (saves money)
- ✅ **Use 8-second clips** (50% fewer API calls)
- ✅ **Check quota before big generations**
- ✅ **Plan daily usage** (50 videos max per day)

### **Best Results**
```bash
# For viral content
python generate_custom_video.py --feeling energetic --style modern "trending topic"

# For professional content  
python generate_custom_video.py --style professional --realistic-audio "business topic"

# For emotional content
python generate_custom_video.py --feeling emotional --narrative pro_family "heartwarming story"
```

### **Batch Processing**
```bash
# Multiple videos with different emotions
for emotion in energetic funny inspirational; do
  python generate_custom_video.py --feeling $emotion "Topic for $emotion video"
  sleep 30  # Respect rate limits
done
```

---

## 🎬 **OUTPUT LOCATIONS**

- **Videos**: `outputs/session_YYYYMMDD_HHMMSS_ID/`
- **Scripts**: `outputs/session_*/script.txt`
- **Audio**: `outputs/session_*/audio/`
- **Logs**: `logs/`

---

**🚀 Most Common Command**: `./run_video_generator.sh --test`  
**📊 Most Useful Command**: `./run_video_generator.sh --quota`  
**🎯 Most Powerful Command**: `./run_video_generator.sh --custom`

---

*Need help? Run `./run_video_generator.sh --help` or check the [full documentation](README.md)* 