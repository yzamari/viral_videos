#!/usr/bin/env python3
"""
🚀 Launch Script for Unified Real-time VEO-2 Video Generator

Simple launcher for the unified UI application.
"""

import os
import sys
import subprocess
import argparse

def main():
    """Launch the unified real-time UI"""
    parser = argparse.ArgumentParser(description='🚀 Launch Unified Real-time VEO-2 Video Generator')
    parser.add_argument('--port', type=int, default=7860, help='Port for web interface')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host for web interface')
    parser.add_argument('--share', action='store_true', help='Create public shareable link')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Check if unified_realtime_ui.py exists
    ui_file = os.path.join(os.path.dirname(__file__), 'unified_realtime_ui.py')
    if not os.path.exists(ui_file):
        print("❌ Error: unified_realtime_ui.py not found!")
        sys.exit(1)
    
    # Build command
    cmd = [sys.executable, 'unified_realtime_ui.py', '--port', str(args.port)]
    
    if args.debug:
        print(f"🚀 Launching Unified Real-time UI on port {args.port}")
        print(f"🌐 Access at: http://localhost:{args.port}")
        print(f"📁 Working directory: {os.getcwd()}")
        print(f"🐍 Python executable: {sys.executable}")
        print(f"🔧 Command: {' '.join(cmd)}")
        print("=" * 60)
    
    # Launch the UI
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching UI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 