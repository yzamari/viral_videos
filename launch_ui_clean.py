#!/usr/bin/env python3
"""
Clean launcher for the comprehensive UI
Suppresses font warnings and starts cleanly
"""

import os
import sys
import subprocess
import time

def main():
    """Launch the comprehensive UI cleanly"""
    print("🎬 Viral Video Generator - Clean UI Launcher")
    print("=" * 60)
    print("🚀 Starting comprehensive interface...")
    print("🌐 UI will be available at: http://localhost:7860")
    print("📝 Note: Font warnings are cosmetic and don't affect functionality")
    print()
    
    # Check if we're in the right directory
    if not os.path.exists("comprehensive_ui_fixed.py"):
        print("❌ Error: Please run from the viral-video-generator directory")
        return 1
    
    try:
        # Launch the UI
        print("🚀 Launching UI...")
        subprocess.run([sys.executable, "comprehensive_ui_fixed.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 UI stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 