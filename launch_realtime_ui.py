#!/usr/bin/env python3
"""
Launch script for Real-time Viral Video Generator UI
"""

import os
import sys
import subprocess

def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        'gradio',
        'google-generativeai',
        'moviepy',
        'gtts',
        'colorlog',
        'Pillow',
        'pydantic',
        'requests',
        'click'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'google-generativeai':
                __import__('google.generativeai')
            elif package == 'Pillow':
                __import__('PIL')
            else:
                __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n🔧 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_configuration():
    """Check if configuration is properly set up"""
    config_files = ['config.env', '.env']
    config_found = False
    
    for config_file in config_files:
        if os.path.exists(config_file):
            config_found = True
            break
    
    if not config_found:
        print("⚠️ Configuration file not found")
        print("📝 Please create a config.env file with your API keys")
        print("   Example:")
        print("   GOOGLE_API_KEY=your_google_ai_studio_key")
        return False
    
    return True

def main():
    """Main launch function"""
    print("🎬 Real-time Viral Video Generator UI Launcher")
    print("=" * 50)
    
    # Check requirements
    print("🔍 Checking requirements...")
    if not check_requirements():
        sys.exit(1)
    
    print("✅ All packages installed")
    
    # Check configuration
    print("🔍 Checking configuration...")
    if not check_configuration():
        sys.exit(1)
    
    print("✅ Configuration found")
    
    # Launch the UI
    print("\n🚀 Launching Real-time UI...")
    print("🌐 Access at: http://localhost:7860")
    print("✨ Features: Live progress updates, streaming output, 26+ AI agents")
    print("\n" + "=" * 50)
    
    try:
        # Import and run the UI
        from realtime_ui import create_realtime_ui
        
        demo = create_realtime_ui()
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            show_error=True
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔧 Make sure realtime_ui.py is in the same directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error launching UI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 