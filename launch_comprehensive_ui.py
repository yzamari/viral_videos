#!/usr/bin/env python3
"""
Simple launcher for the comprehensive UI
"""

import subprocess
import sys
import os

def main():
    """Launch the comprehensive UI"""
    print("🎬 Viral Video Generator - Comprehensive UI Launcher")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("comprehensive_ui.py"):
        print("❌ Error: comprehensive_ui.py not found")
        print("Please run from the viral-video-generator directory")
        return 1
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8+ required")
        return 1
    
    print("✅ Environment check passed")
    print("🚀 Launching comprehensive UI...")
    
    try:
        # Launch the comprehensive UI
        subprocess.run([sys.executable, "comprehensive_ui.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 UI stopped by user")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching UI: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 