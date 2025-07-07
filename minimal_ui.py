#!/usr/bin/env python3
"""
Viral Video Generator - Minimal UI
Guaranteed to work with current Gradio version
"""

import gradio as gr
import os
import sys
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def generate_video(topic: str, duration: int, platform: str, discussions: str, image_only: bool):
    """Generate video using the main.py script"""
    
    if not topic.strip():
        return "❌ Please enter a topic"
    
    try:
        # Build command
        cmd = [
            "python", "main.py", "generate",
            "--topic", topic,
            "--duration", str(duration),
            "--platform", platform,
            "--discussions", discussions
        ]
        
        if image_only:
            cmd.append("--image-only")
        
        # Show command being executed
        cmd_str = " ".join(cmd)
        result = f"🚀 Executing: {cmd_str}\n\n"
        
        # Run the command
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if process.returncode == 0:
            result += "✅ SUCCESS!\n\n"
            result += "📋 Output:\n" + process.stdout
            
            # Try to find the generated video
            outputs_dir = Path("outputs")
            if outputs_dir.exists():
                recent_sessions = sorted(
                    [d for d in outputs_dir.iterdir() if d.is_dir() and d.name.startswith("session_")],
                    key=lambda x: x.stat().st_mtime,
                    reverse=True
                )
                
                if recent_sessions:
                    latest_session = recent_sessions[0]
                    video_files = list(latest_session.glob("*.mp4"))
                    if video_files:
                        result += f"\n🎬 Generated video: {video_files[0]}"
        else:
            result += "❌ FAILED!\n\n"
            result += "📋 Error output:\n" + process.stderr
            
        return result
        
    except subprocess.TimeoutExpired:
        return "⏰ Generation timed out (5 minutes). The process may still be running in the background."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def get_recent_outputs():
    """Get list of recent video outputs"""
    outputs_dir = Path("outputs")
    if not outputs_dir.exists():
        return "No outputs directory found"
    
    sessions = []
    for session_dir in outputs_dir.iterdir():
        if session_dir.is_dir() and session_dir.name.startswith("session_"):
            video_files = list(session_dir.glob("*.mp4"))
            if video_files:
                sessions.append({
                    "session": session_dir.name,
                    "videos": [f.name for f in video_files],
                    "created": datetime.fromtimestamp(session_dir.stat().st_mtime)
                })
    
    if not sessions:
        return "No video outputs found"
    
    # Sort by creation time (newest first)
    sessions.sort(key=lambda x: x["created"], reverse=True)
    
    result = "📁 Recent Video Outputs:\n\n"
    for session in sessions[:5]:  # Show last 5 sessions
        result += f"🎬 {session['session']}\n"
        result += f"   Created: {session['created'].strftime('%Y-%m-%d %H:%M:%S')}\n"
        for video in session['videos']:
            result += f"   └── 🎥 {video}\n"
        result += "\n"
    
    return result

def main():
    """Main function to create and launch the UI"""
    
    print("🎬 Viral Video Generator - Minimal UI")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("config"):
        print("❌ Error: Please run from the viralAi directory")
        return
    
    print("✅ Environment check passed")
    print("🚀 Starting Gradio UI...")
    
    # Create the interface
    interface = gr.Interface(
        fn=generate_video,
        inputs=[
            gr.Textbox(
                label="Video Topic",
                placeholder="Enter your video topic (e.g., 'Latest tech trends')",
                lines=2
            ),
            gr.Slider(
                minimum=5,
                maximum=60,
                value=15,
                step=5,
                label="Duration (seconds)"
            ),
            gr.Dropdown(
                choices=["youtube", "tiktok", "instagram", "twitter"],
                value="youtube",
                label="Platform"
            ),
            gr.Dropdown(
                choices=["light", "standard", "deep"],
                value="standard",
                label="AI Discussions Level"
            ),
            gr.Checkbox(
                label="Image-only mode",
                value=False
            )
        ],
        outputs=gr.Textbox(
            label="Generation Result",
            lines=20
        ),
        title="🎬 Viral Video Generator",
        description="""
        Generate viral videos with AI-powered content creation.
        
        **Features:**
        - AI Script Generation
        - Multi-Platform Optimization  
        - AI Agent Discussions
        - Image-only Mode
        
        **Usage:**
        1. Enter your video topic
        2. Configure settings
        3. Click Submit
        4. Wait for generation to complete
        """,
        allow_flagging="never"
    )
    
    # Add a second interface for viewing outputs
    outputs_interface = gr.Interface(
        fn=get_recent_outputs,
        inputs=[],
        outputs=gr.Textbox(
            label="Recent Outputs",
            lines=15
        ),
        title="📁 Recent Outputs",
        description="View recently generated videos",
        allow_flagging="never"
    )
    
    # Create tabbed interface
    demo = gr.TabbedInterface(
        [interface, outputs_interface],
        ["🎬 Generate", "📁 Outputs"]
    )
    
    try:
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            show_api=False,
            share=False
        )
    except Exception as e:
        print(f"❌ Error launching UI: {e}")
        print("💡 Make sure Gradio is installed: pip install gradio")

if __name__ == "__main__":
    main() 