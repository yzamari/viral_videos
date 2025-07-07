# 🎬 Real Veo-2 Integration Guide

This guide shows you how to integrate **real Google Veo-2 AI video generation** into your viral video generator instead of using mock clips.

## 🎯 What Real Veo-2 Gives You

✅ **Actual AI-generated videos** - Real content, not colored backgrounds  
✅ **720p HD quality** - Professional resolution at 24fps  
✅ **5-8 second clips** - Perfect for social media content  
✅ **Text-to-video & Image-to-video** - Multiple generation modes  
✅ **Cinematic quality** - Realistic physics and motion  
✅ **Multiple aspect ratios** - 16:9 and 9:16 support  

## 📋 Prerequisites

### 1. Google AI API Access
You need a Google AI Studio account with Veo-2 access:
- Go to [Google AI Studio](https://aistudio.google.com/)
- Create an account and generate an API key
- **Important**: Veo-2 is a **paid feature** - not available in free tier

### 2. Install Required Dependencies
```bash
# Install the Google AI SDK
pip install google-generativeai
pip install google-ai-generativelanguage

# Or update your existing installation
pip install --upgrade google-generativeai
```

### 3. Set Your API Key
```bash
# Option 1: Environment variable
export GEMINI_API_KEY="your_google_ai_api_key_here"

# Option 2: Add to your .env file
echo "GEMINI_API_KEY=your_google_ai_api_key_here" >> .env
echo "USE_REAL_VEO2=true" >> .env
```

## 🚀 Quick Start Example

Here's a simple example to generate your first real Veo-2 video:

```python
#!/usr/bin/env python3
"""
Quick test of real Veo-2 video generation
"""
import os
import time
from google import genai
from google.genai import types

# Configure API
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("❌ GEMINI_API_KEY not found!")
    exit(1)

genai.configure(api_key=api_key)
client = genai.Client()

print("🎬 Generating real Veo-2 video...")

# Start video generation
operation = client.models.generate_videos(
    model="veo-2.0-generate-001",
    prompt="Cute baby crawling on soft carpet, giggles and smiles, natural home lighting, heartwarming family moment",
    config=types.GenerateVideosConfig(
        person_generation="allow_adult",
        aspect_ratio="16:9",
        duration_seconds=5,
        enhance_prompt=True
    ),
)

print("⏳ Waiting for Veo-2 generation (this takes 2-3 minutes)...")

# Wait for completion
start_time = time.time()
while not operation.done:
    elapsed = time.time() - start_time
    print(f"   Generation in progress... {elapsed:.1f}s elapsed")
    time.sleep(20)
    operation = client.operations.get(operation)

# Save the video
if operation.response and operation.response.generated_videos:
    video = operation.response.generated_videos[0]
    client.files.download(file=video.video)
    video.video.save("test_veo2_baby.mp4")
    print("✅ Real Veo-2 video saved: test_veo2_baby.mp4")
else:
    print("❌ No video generated")
```

## 🔧 Integration with Your Video Generator

### Method 1: Use the Real Veo-2 Client

The system now includes a `RealVeo2Client` that integrates seamlessly:

```python
# Enable real Veo-2 in your video generator
from src.generators.video_generator import VideoGenerator

generator = VideoGenerator(
    api_key=os.getenv('GEMINI_API_KEY'),
    use_real_veo2=True  # Enable real Veo-2
)

# Generate videos as normal - now with real AI clips!
config = GeneratedVideoConfig(
    topic="Baby's first steps",
    duration_seconds=15,  # Will be 3 clips of 5s each
    style="heartwarming",
    # ... other config
)

video = generator.generate_video(config)
```

### Method 2: Environment Variable Control

Set the environment variable to automatically use real Veo-2:

```bash
# Enable real Veo-2 for all generations
export USE_REAL_VEO2=true
export GEMINI_API_KEY="your_api_key"

# Run your video generation
python example_usage.py
```

## 💰 Cost Considerations

**Important**: Real Veo-2 API usage has costs:

- **Estimated cost**: $0.10-0.30 per video clip
- **Generation time**: 2-3 minutes per clip
- **Daily limits**: Check Google AI Studio for your quota

### Cost Optimization Tips:
1. **Start with shorter videos** (5s clips)
2. **Test prompts with mock first**, then switch to real Veo-2
3. **Use batch generation** to minimize API calls
4. **Cache successful generations** - don't regenerate identical content

## 🎨 Optimizing Your Veo-2 Prompts

Real Veo-2 works best with detailed, cinematic prompts:

### ❌ Basic Prompt:
```
"Baby playing with toys"
```

### ✅ Optimized Veo-2 Prompt:
```
"Close-up shot of adorable baby crawling on soft carpet towards colorful toys, 
natural sunlight streaming through window, shallow depth of field, 
heartwarming family moment, cinematic quality, 24fps smooth motion"
```

### Key Elements for Better Results:
- **Camera angles**: "close-up shot", "wide angle", "tracking shot"
- **Lighting**: "natural sunlight", "soft lighting", "golden hour"
- **Motion**: "smooth movement", "gentle motion", "realistic physics"
- **Style**: "cinematic quality", "heartwarming", "professional"
- **Context**: "home environment", "family moment", "natural setting"

## 🔄 Switching Between Mock and Real

The system supports both modes:

```python
# Use real Veo-2 for production
generator = VideoGenerator(api_key=api_key, use_real_veo2=True)

# Use mock for testing/development  
generator = VideoGenerator(api_key=api_key, use_real_veo2=False)
```

Or via environment variables:
```bash
# Real Veo-2
export USE_REAL_VEO2=true

# Mock Veo-2  
export USE_REAL_VEO2=false
```

## 🛠️ Troubleshooting

### "API key not found"
```bash
# Check your API key is set
echo $GEMINI_API_KEY

# If empty, set it:
export GEMINI_API_KEY="your_key_here"
```

### "Model not available"
Veo-2 requires paid access. Check:
1. Your Google AI Studio account has billing enabled
2. Veo-2 is available in your region
3. You have sufficient quota

### "Generation timeout"
Veo-2 can take 2-10 minutes per clip. If it times out:
1. Try a simpler prompt
2. Check Google AI Studio status
3. Try during off-peak hours

### "Import error for RealVeo2Client"
Install the required dependencies:
```bash
pip install google-generativeai google-ai-generativelanguage
```

## 📊 Comparison: Mock vs Real Veo-2

| Feature | Mock Veo-2 | Real Veo-2 |
|---------|------------|-------------|
| **Cost** | Free | $0.10-0.30/clip |
| **Speed** | ~2 seconds | 2-3 minutes |
| **Quality** | Test patterns | AI-generated HD |
| **Content** | Colored backgrounds | Realistic videos |
| **Use Case** | Development/testing | Production |

## 🎬 Example Real Veo-2 Outputs

Here's what you can expect from real Veo-2 generation:

### Baby Content Examples:
- **"Baby's first steps"** → Realistic toddler taking wobbly steps
- **"Baby laughing"** → Genuine infant giggling and smiling  
- **"Baby playing with toys"** → Natural play behavior with realistic motion
- **"Baby crawling"** → Smooth crawling motion with correct physics

### Quality Features:
- **720p resolution** - Sharp, clear video
- **24fps smooth motion** - Natural movement
- **Realistic lighting** - Proper shadows and illumination
- **Coherent scenes** - Objects stay consistent throughout
- **Natural physics** - Gravity, momentum work correctly

## 🔮 Next Steps

1. **Get API access** from Google AI Studio
2. **Test the quick example** above
3. **Run your first real generation**:
   ```bash
   export GEMINI_API_KEY="your_key"
   export USE_REAL_VEO2=true
   python example_usage.py
   ```
4. **Optimize your prompts** for better results
5. **Scale up** once you're happy with the quality!

## 📝 Notes

- **Generation time**: Real Veo-2 takes 2-3 minutes per clip
- **File size**: Videos are typically 10-50MB per clip
- **Quality**: 720p, 24fps, professional grade
- **Formats**: MP4 output with H.264 encoding
- **Storage**: Videos are temporarily stored on Google's servers

---

🎉 **Congratulations!** You're now ready to generate **real AI videos** with Google's state-of-the-art Veo-2 model! 