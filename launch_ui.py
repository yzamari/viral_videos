#!/usr/bin/env python3
"""
Viral Video Generator - UI Launcher
Simple script to launch the Gradio web interface
"""

import os
import sys
import subprocess
import platform

def check_requirements():
    """Check if all required packages are installed"""
    required_packages = [
        'gradio',
        'plotly',
        'pandas',
        'google-generativeai',
        'moviepy',
        'click'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Installing missing packages...")
        
        # Install missing packages
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✅ Installed {package}")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}")
                return False
    
    return True

def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Checking environment...")
    
    # Check if we're in the right directory
    if not os.path.exists("config"):
        print("❌ Error: Please run this script from the viral-video-generator directory")
        print("Usage: cd viral-video-generator && python launch_ui.py")
        return False
    
    # Check for .env file
    if not os.path.exists(".env"):
        print("⚠️  Warning: .env file not found")
        print("Please create a .env file with your GOOGLE_API_KEY")
        print("Example:")
        print("GOOGLE_API_KEY=your_api_key_here")
        
        # Ask if user wants to continue anyway
        response = input("\nContinue anyway? (y/N): ").lower()
        if response != 'y':
            return False
    
    # Check Python version
    if sys.version_info < (3, 8):
        print(f"❌ Error: Python 3.8+ required, you have {sys.version}")
        return False
    
    print("✅ Environment check passed")
    return True

def main():
    """Main launcher function"""
    print("🎬 Viral Video Generator - UI Launcher")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Check requirements
    if not check_requirements():
        print("❌ Failed to install required packages")
        sys.exit(1)
    
    print("✅ All requirements satisfied")
    print("🚀 Launching Gradio UI...")
    print("🌐 The interface will open in your browser")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Launch the Gradio UI
        from gradio_ui import main as launch_gradio
        launch_gradio()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        sys.exit(0)
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure gradio_ui.py is in the same directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error launching UI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 