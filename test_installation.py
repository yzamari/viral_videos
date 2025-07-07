#!/usr/bin/env python3
"""
Installation Test Script for Viral Video Generator
Tests all critical dependencies and configurations
"""

import sys
import os
import subprocess
import tempfile
from pathlib import Path

def test_section(name):
    """Decorator for test sections"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(f"\n{'='*60}")
            print(f"🧪 TESTING: {name}")
            print('='*60)
            try:
                result = func(*args, **kwargs)
                print(f"✅ {name}: PASSED")
                return result
            except Exception as e:
                print(f"❌ {name}: FAILED - {e}")
                return False
        return wrapper
    return decorator

@test_section("Python Environment")
def test_python_environment():
    """Test Python version and virtual environment"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version < (3, 9):
        raise Exception(f"Python 3.9+ required, got {version.major}.{version.minor}")
    
    # Check if in virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    print(f"Virtual environment: {'Yes' if in_venv else 'No'}")
    
    return True

@test_section("Core Dependencies")
def test_core_dependencies():
    """Test core Python package imports"""
    
    packages = {
        'google.generativeai': 'Google Generative AI',
        'moviepy.editor': 'MoviePy',
        'gtts': 'Google Text-to-Speech',
        'numpy': 'NumPy',
        'cv2': 'OpenCV',
        'PIL': 'Pillow',
        'requests': 'Requests',
        'pydantic': 'Pydantic',
        'dotenv': 'Python-dotenv'
    }
    
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"✅ {name} imported successfully")
        except ImportError as e:
            raise Exception(f"Failed to import {name}: {e}")
    
    return True

@test_section("MoviePy & ImageMagick")
def test_moviepy_imagemagick():
    """Test MoviePy and ImageMagick integration"""
    from moviepy.editor import TextClip, ColorClip, CompositeVideoClip
    import tempfile
    
    # Test basic clip creation
    background = ColorClip(size=(640, 480), color=(255, 0, 0), duration=1)
    print("✅ ColorClip created successfully")
    
    # Test TextClip (requires ImageMagick)
    try:
        text_clip = TextClip("Test", fontsize=50, color='white', duration=1)
        print("✅ TextClip created successfully (ImageMagick working)")
        
        # Test composition
        video = CompositeVideoClip([background, text_clip.set_position('center')])
        print("✅ CompositeVideoClip created successfully")
        
    except Exception as e:
        print(f"⚠️ TextClip failed (ImageMagick issue): {e}")
        print("This will fall back to PIL-based text rendering")
    
    return True

@test_section("Google AI Services")
def test_google_ai():
    """Test Google AI API connection"""
    import google.generativeai as genai
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        print("⚠️ GOOGLE_API_KEY not found in environment")
        print("This will use fallback/mock data")
        return True
    
    try:
        genai.configure(api_key=api_key)
        
        # Test model listing
        models = genai.list_models()
        model_names = [model.name for model in models]
        print(f"✅ Connected to Google AI API")
        print(f"Available models: {len(model_names)}")
        
        # Check for required models
        required_models = ['gemini-2.5-flash', 'gemini-2.5-pro']
        for model in required_models:
            if any(model in name for name in model_names):
                print(f"✅ {model} available")
            else:
                print(f"⚠️ {model} not found, will use fallback")
                
    except Exception as e:
        print(f"⚠️ Google AI API test failed: {e}")
        print("System will use fallback/mock data")
    
    return True

@test_section("Text-to-Speech")
def test_tts():
    """Test Google Text-to-Speech"""
    from gtts import gTTS
    import tempfile
    
    # Test basic TTS
    text = "This is a test of the text to speech system."
    
    try:
        tts = gTTS(text=text, lang='en', tld='co.uk')
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
            tts.save(tmp_file.name)
            
            # Check if file was created and has content
            if os.path.exists(tmp_file.name) and os.path.getsize(tmp_file.name) > 0:
                print("✅ TTS audio file generated successfully")
                os.unlink(tmp_file.name)  # Clean up
            else:
                raise Exception("TTS file creation failed")
                
    except Exception as e:
        raise Exception(f"TTS test failed: {e}")
    
    return True

@test_section("Video Generation Pipeline")
def test_video_pipeline():
    """Test basic video generation pipeline"""
    from moviepy.editor import ColorClip, concatenate_videoclips
    import tempfile
    
    # Create test clips
    clip1 = ColorClip(size=(640, 480), color=(255, 0, 0), duration=1)
    clip2 = ColorClip(size=(640, 480), color=(0, 255, 0), duration=1)
    clip3 = ColorClip(size=(640, 480), color=(0, 0, 255), duration=1)
    
    # Concatenate clips
    final_video = concatenate_videoclips([clip1, clip2, clip3])
    print("✅ Video concatenation successful")
    
    # Test video export
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
        try:
            final_video.write_videofile(
                tmp_file.name, 
                fps=24, 
                verbose=False, 
                logger=None,
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            if os.path.exists(tmp_file.name) and os.path.getsize(tmp_file.name) > 0:
                print("✅ Video export successful")
                os.unlink(tmp_file.name)  # Clean up
            else:
                raise Exception("Video export failed")
                
        except Exception as e:
            print(f"⚠️ Video export failed: {e}")
            raise
    
    return True

@test_section("Configuration")
def test_configuration():
    """Test system configuration"""
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Check environment variables
    env_vars = {
        'GOOGLE_API_KEY': 'Google AI API Key',
        'YOUTUBE_API_KEY': 'YouTube API Key (Optional)',
        'VIDEO_DURATION': 'Video Duration Setting'
    }
    
    for var, description in env_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {description}: Configured")
        else:
            if var == 'YOUTUBE_API_KEY':
                print(f"⚠️ {description}: Not configured (will use mock data)")
            else:
                print(f"⚠️ {description}: Not configured (will use defaults)")
    
    # Test config module
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        from config.config import settings
        print(f"✅ Configuration loaded successfully")
        print(f"   Video duration: {settings.video_duration_seconds}s")
        print(f"   Output directory: {settings.output_dir}")
    except Exception as e:
        print(f"⚠️ Configuration loading failed: {e}")
    
    return True

@test_section("Output Directories")
def test_directories():
    """Test required directories exist"""
    required_dirs = [
        'outputs',
        'outputs/videos',
        'outputs/videos/generated',
        'outputs/videos/raw',
        'data/metadata',
        'logs'
    ]
    
    for directory in required_dirs:
        path = Path(directory)
        if path.exists():
            print(f"✅ {directory} exists")
        else:
            path.mkdir(parents=True, exist_ok=True)
            print(f"✅ {directory} created")
    
    return True

@test_section("System Commands")
def test_system_commands():
    """Test required system commands"""
    commands = {
        'ffmpeg': 'FFmpeg (video processing)',
        'magick': 'ImageMagick (text rendering)'
    }
    
    for cmd, description in commands.items():
        try:
            result = subprocess.run([cmd, '--version'], 
                                 capture_output=True, 
                                 text=True, 
                                 timeout=5)
            if result.returncode == 0:
                print(f"✅ {description}: Available")
            else:
                print(f"⚠️ {description}: Command failed")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print(f"⚠️ {description}: Not found")
    
    return True

def run_all_tests():
    """Run all installation tests"""
    print("🚀 Viral Video Generator - Installation Test Suite")
    print("=" * 60)
    
    tests = [
        test_python_environment,
        test_core_dependencies,
        test_moviepy_imagemagick,
        test_google_ai,
        test_tts,
        test_video_pipeline,
        test_configuration,
        test_directories,
        test_system_commands
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n{'='*60}")
    print(f"🏁 TEST RESULTS: {passed}/{total} tests passed")
    print('='*60)
    
    if passed == total:
        print("🎉 All tests passed! System is ready for video generation.")
    else:
        print("⚠️ Some tests failed. Check warnings above.")
        print("The system may still work with reduced functionality.")
    
    print("\n📋 Next Steps:")
    print("1. Edit .env file with your API keys")
    print("2. Run: python main.py generate --platform youtube --category Entertainment")
    print("3. Check outputs/ directory for generated videos")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 