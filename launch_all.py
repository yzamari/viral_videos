#!/usr/bin/env python3
"""
Comprehensive Launcher for Viral Video Generator
Supports all UI modes, CLI options, and configurations
"""

import os
import sys
import argparse
import subprocess
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

def print_banner():
    """Print application banner"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                          🎬 VIRAL VIDEO GENERATOR v2.0                               ║
║                     AI-Powered Video Creation with Real-Time Visualization          ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
    """)

def check_environment():
    """Check environment setup"""
    print("🔍 Checking environment...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {python_version.major}.{python_version.minor}")
    
    # Check API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("⚠️  GOOGLE_API_KEY not set")
        print("   To set: export GOOGLE_API_KEY=your_api_key_here")
    else:
        print(f"✅ Google API Key: {api_key[:10]}...")
    
    # Check required directories
    required_dirs = ['src', 'outputs', 'config']
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ Directory: {dir_name}")
        else:
            print(f"⚠️  Directory missing: {dir_name}")
            os.makedirs(dir_name, exist_ok=True)
            print(f"   Created: {dir_name}")
    
    return True

def get_ui_options():
    """Get available UI options"""
    return {
        "basic": {
            "file": "gradio_ui.py",
            "description": "Basic Gradio UI with standard controls",
            "features": ["Video generation", "Basic controls", "Session management"]
        },
        "enhanced": {
            "file": "enhanced_realtime_ui.py", 
            "description": "Enhanced UI with real-time AI agent visualization",
            "features": ["Real-time agent status", "Live discussions", "Colorful progress", "Phase tracking"]
        },
        "cli": {
            "file": "cli.py",
            "description": "Command-line interface with all options",
            "features": ["All CLI flags", "Batch processing", "Scripting support"]
        }
    }

def launch_ui(ui_type: str, **kwargs):
    """Launch specified UI type"""
    ui_options = get_ui_options()
    
    if ui_type not in ui_options:
        print(f"❌ Unknown UI type: {ui_type}")
        print(f"Available options: {list(ui_options.keys())}")
        return False
    
    ui_config = ui_options[ui_type]
    ui_file = ui_config["file"]
    
    if not os.path.exists(ui_file):
        print(f"❌ UI file not found: {ui_file}")
        return False
    
    print(f"🚀 Launching {ui_type} UI...")
    print(f"📋 Description: {ui_config['description']}")
    print(f"✨ Features: {', '.join(ui_config['features'])}")
    
    try:
        if ui_type == "cli":
            # For CLI, pass arguments
            args = []
            if kwargs.get('topic'):
                args.extend(['--topic', kwargs['topic']])
            if kwargs.get('duration'):
                args.extend(['--duration', str(kwargs['duration'])])
            if kwargs.get('style'):
                args.extend(['--style', kwargs['style']])
            if kwargs.get('platform'):
                args.extend(['--platform', kwargs['platform']])
            if kwargs.get('enable_discussions'):
                args.append('--enable-discussions')
            if kwargs.get('verbose'):
                args.append('--verbose')
            
            subprocess.run([sys.executable, ui_file] + args, check=True)
        else:
            # For GUI, just launch
            subprocess.run([sys.executable, ui_file], check=True)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to launch {ui_type} UI: {e}")
        return False
    except KeyboardInterrupt:
        print(f"\\n⏹️  {ui_type} UI stopped by user")
        return True

def create_launcher_parser():
    """Create argument parser for launcher"""
    parser = argparse.ArgumentParser(
        description="🎬 Viral Video Generator - Comprehensive Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
UI Options:
  basic     - Basic Gradio UI with standard controls
  enhanced  - Enhanced UI with real-time AI agent visualization  
  cli       - Command-line interface with all options

Examples:
  # Launch enhanced UI
  python launch_all.py --ui enhanced

  # Launch CLI with specific video
  python launch_all.py --ui cli --topic "AI revolution" --duration 60 --verbose

  # Interactive mode
  python launch_all.py --interactive

  # Check system status
  python launch_all.py --check-system
        """
    )
    
    parser.add_argument(
        '--ui',
        choices=['basic', 'enhanced', 'cli'],
        default='enhanced',
        help='UI type to launch (default: enhanced)'
    )
    
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Interactive mode - choose options interactively'
    )
    
    parser.add_argument(
        '--check-system',
        action='store_true',
        help='Check system requirements and configuration'
    )
    
    parser.add_argument(
        '--list-sessions',
        action='store_true',
        help='List available video sessions'
    )
    
    # Video generation options (for CLI mode)
    parser.add_argument('--topic', help='Video topic')
    parser.add_argument('--duration', type=int, help='Video duration in seconds')
    parser.add_argument('--style', help='Video style')
    parser.add_argument('--platform', help='Target platform')
    parser.add_argument('--enable-discussions', action='store_true', help='Enable AI discussions')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    return parser

def interactive_mode():
    """Run interactive mode"""
    print("🎮 Interactive Mode")
    print("=" * 50)
    
    # Choose UI type
    ui_options = get_ui_options()
    print("\\nAvailable UI options:")
    for i, (ui_type, config) in enumerate(ui_options.items(), 1):
        print(f"{i}. {ui_type.title()}: {config['description']}")
    
    while True:
        try:
            choice = input("\\nSelect UI type (1-3): ").strip()
            ui_index = int(choice) - 1
            ui_types = list(ui_options.keys())
            
            if 0 <= ui_index < len(ui_types):
                selected_ui = ui_types[ui_index]
                break
            else:
                print("❌ Invalid choice. Please select 1-3.")
        except ValueError:
            print("❌ Please enter a number.")
    
    # Additional options for CLI
    kwargs = {}
    if selected_ui == "cli":
        print("\\n📝 CLI Configuration:")
        
        topic = input("Video topic (optional): ").strip()
        if topic:
            kwargs['topic'] = topic
        
        duration = input("Duration in seconds (optional): ").strip()
        if duration and duration.isdigit():
            kwargs['duration'] = int(duration)
        
        style = input("Video style (optional): ").strip()
        if style:
            kwargs['style'] = style
        
        platform = input("Target platform (optional): ").strip()
        if platform:
            kwargs['platform'] = platform
        
        discussions = input("Enable AI discussions? (y/n): ").strip().lower()
        if discussions in ['y', 'yes']:
            kwargs['enable_discussions'] = True
        
        verbose = input("Verbose output? (y/n): ").strip().lower()
        if verbose in ['y', 'yes']:
            kwargs['verbose'] = True
    
    print(f"\\n🚀 Launching {selected_ui} UI...")
    return launch_ui(selected_ui, **kwargs)

def check_system():
    """Check system requirements and configuration"""
    print("🔧 System Check")
    print("=" * 50)
    
    # Environment check
    if not check_environment():
        return False
    
    # Check dependencies
    print("\\n📦 Checking dependencies...")
    required_packages = [
        'gradio', 'google-generativeai', 'opencv-python', 
        'numpy', 'pillow', 'requests', 'python-dotenv'
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - install with: pip install {package}")
    
    # Check API connectivity
    print("\\n🌐 Checking API connectivity...")
    try:
        import requests
        response = requests.get("https://generativelanguage.googleapis.com", timeout=5)
        print("✅ Google API endpoint reachable")
    except:
        print("❌ Google API endpoint not reachable")
    
    # Check disk space
    print("\\n💾 Checking disk space...")
    import shutil
    total, used, free = shutil.disk_usage(".")
    free_gb = free // (1024**3)
    print(f"💿 Free space: {free_gb}GB")
    if free_gb < 2:
        print("⚠️  Low disk space - may affect video generation")
    
    # Check GPU availability
    print("\\n🎮 Checking GPU availability...")
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✅ CUDA GPU available: {torch.cuda.get_device_name()}")
        else:
            print("ℹ️  No CUDA GPU detected (CPU mode)")
    except ImportError:
        print("ℹ️  PyTorch not installed (GPU acceleration unavailable)")
    
    return True

def list_sessions():
    """List available video sessions"""
    print("📁 Available Video Sessions")
    print("=" * 50)
    
    outputs_dir = "outputs"
    if not os.path.exists(outputs_dir):
        print("No sessions found (outputs directory doesn't exist)")
        return
    
    sessions = []
    for folder in os.listdir(outputs_dir):
        if folder.startswith("session_"):
            session_path = os.path.join(outputs_dir, folder)
            if os.path.isdir(session_path):
                try:
                    created = datetime.fromtimestamp(os.path.getctime(session_path))
                    
                    # Count files in session
                    file_count = sum(len(files) for _, _, files in os.walk(session_path))
                    
                    # Get session size
                    size = sum(
                        os.path.getsize(os.path.join(dirpath, filename))
                        for dirpath, dirnames, filenames in os.walk(session_path)
                        for filename in filenames
                    )
                    size_mb = size / (1024 * 1024)
                    
                    sessions.append({
                        'name': folder,
                        'created': created,
                        'files': file_count,
                        'size_mb': size_mb
                    })
                except Exception as e:
                    print(f"⚠️  Error reading session {folder}: {e}")
    
    if not sessions:
        print("No sessions found")
        return
    
    # Sort by creation time, newest first
    sessions.sort(key=lambda x: x['created'], reverse=True)
    
    print(f"Found {len(sessions)} sessions:\\n")
    for session in sessions:
        print(f"📁 {session['name']}")
        print(f"   Created: {session['created'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Files: {session['files']}")
        print(f"   Size: {session['size_mb']:.1f}MB")
        print()

def main():
    """Main launcher function"""
    print_banner()
    
    parser = create_launcher_parser()
    args = parser.parse_args()
    
    # Handle utility commands
    if args.check_system:
        return check_system()
    
    if args.list_sessions:
        return list_sessions()
    
    # Check environment first
    if not check_environment():
        print("❌ Environment check failed")
        return False
    
    # Interactive mode
    if args.interactive:
        return interactive_mode()
    
    # Launch specified UI
    kwargs = {
        'topic': args.topic,
        'duration': args.duration,
        'style': args.style,
        'platform': args.platform,
        'enable_discussions': args.enable_discussions,
        'verbose': args.verbose
    }
    
    return launch_ui(args.ui, **kwargs)

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\\n⏹️  Launcher stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Launcher error: {e}")
        sys.exit(1) 