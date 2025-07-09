#!/usr/bin/env python3
"""
Launch the Real-time UI for Viral Video Generator
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit real-time UI"""
    
    # Check if streamlit is installed
    try:
        import streamlit
    except ImportError:
        print("❌ Streamlit not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
    
    # Set environment variables if needed
    if not os.getenv('GEMINI_API_KEY'):
        print("⚠️ Warning: GEMINI_API_KEY not found in environment variables")
        print("Please set your API key: export GEMINI_API_KEY='your-key-here'")
    
    # Launch Streamlit app
    print("🚀 Launching Real-time Viral Video Generator UI...")
    print("🌐 Opening in browser at http://localhost:8501")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "realtime_ui_with_video.py",
            "--server.port", "8501",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 UI closed by user")
    except Exception as e:
        print(f"❌ Error launching UI: {e}")

if __name__ == "__main__":
    main() 