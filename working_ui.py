#!/usr/bin/env python3
"""
Working UI for Viral Video Generator
Calls main.py directly to avoid import issues
"""

import gradio as gr
import subprocess
import os
import json
import time
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional

# Global variables for monitoring
current_process = None
process_output = []
process_status = "idle"

def run_video_generation(topic: str, duration: int, category: str, platform: str, 
                        discussions: str, frame_continuity: str, progress=gr.Progress()) -> tuple:
    """Run video generation via main.py subprocess"""
    global current_process, process_output, process_status
    
    # Reset monitoring
    process_output = []
    process_status = "running"
    
    try:
        # Build command
        cmd = [
            "python3", "main.py", "generate",
            "--topic", topic,
            "--duration", str(duration),
            "--category", category,
            "--platform", platform,
            "--discussions", discussions,
            "--frame-continuity", frame_continuity
        ]
        
        # Start process
        progress(0.1, desc="Starting video generation...")
        current_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Monitor process output
        output_lines = []
        while True:
            line = current_process.stdout.readline()
            if not line and current_process.poll() is not None:
                break
            
            if line:
                line = line.strip()
                output_lines.append(line)
                process_output.append(line)
                
                # Update progress based on output
                if "Script generation completed" in line:
                    progress(0.3, desc="Script generated...")
                elif "Generated" in line and "video clips" in line:
                    progress(0.5, desc="Video clips generated...")
                elif "Enhanced gTTS generated" in line:
                    progress(0.7, desc="Audio generated...")
                elif "Final video composed" in line:
                    progress(0.9, desc="Final video assembled...")
                elif "Video generation complete" in line:
                    progress(1.0, desc="Complete!")
        
        # Wait for completion
        return_code = current_process.wait()
        process_status = "completed" if return_code == 0 else "failed"
        
        # Parse output for results
        full_output = "\n".join(output_lines)
        
        # Extract video path
        video_path = None
        for line in output_lines:
            if "outputs/final_video_" in line and ".mp4" in line:
                # Extract path from log line
                parts = line.split("outputs/final_video_")
                if len(parts) > 1:
                    video_filename = "outputs/final_video_" + parts[1].split()[0].replace(":", "")
                    if os.path.exists(video_filename):
                        video_path = video_filename
                        break
        
        # Extract frame continuity decision
        frame_decision = "Unknown"
        frame_reason = "No decision recorded"
        for line in output_lines:
            if "Frame Continuity" in line and ("✅ ENABLED" in line or "❌ DISABLED" in line):
                frame_decision = "Enabled" if "✅ ENABLED" in line else "Disabled"
            elif "Reason:" in line and frame_decision != "Unknown":
                frame_reason = line.split("Reason:", 1)[1].strip()
                break
        
        # Extract discussion summary
        discussion_summary = "No discussion data available"
        total_discussions = 0
        avg_consensus = 0.0
        
        for line in output_lines:
            if "Total Discussions:" in line:
                try:
                    total_discussions = int(line.split("Total Discussions:")[1].strip())
                except:
                    pass
            elif "Average Consensus:" in line:
                try:
                    avg_consensus = float(line.split("Average Consensus:")[1].strip())
                except:
                    pass
        
        if total_discussions > 0:
            discussion_summary = f"Conducted {total_discussions} discussions with {avg_consensus:.1%} average consensus"
        
        # Create result summary
        if return_code == 0:
            result_summary = f"""
✅ **Video Generation Successful!**

📁 **Output:** {video_path or 'Video file not found'}
🎬 **Frame Continuity:** {frame_decision}
💭 **Reason:** {frame_reason}
🤖 **AI Discussions:** {discussion_summary}

**Generation Details:**
- Topic: {topic}
- Duration: {duration}s
- Platform: {platform}
- Category: {category}
- Discussions: {discussions}
- Frame Continuity: {frame_continuity}
"""
        else:
            result_summary = f"""
❌ **Video Generation Failed**

**Error Details:**
{full_output[-1000:] if len(full_output) > 1000 else full_output}
"""
        
        return result_summary, video_path, full_output
        
    except Exception as e:
        process_status = "failed"
        error_msg = f"❌ **Generation Error:** {str(e)}"
        return error_msg, None, str(e)
    finally:
        current_process = None

def get_recent_videos() -> List[Dict[str, Any]]:
    """Get list of recent videos"""
    videos = []
    if os.path.exists("outputs"):
        for filename in os.listdir("outputs"):
            if filename.startswith("final_video_") and filename.endswith(".mp4"):
                filepath = os.path.join("outputs", filename)
                if os.path.exists(filepath):
                    stat = os.stat(filepath)
                    videos.append({
                        "filename": filename,
                        "path": filepath,
                        "size": f"{stat.st_size / 1024 / 1024:.1f}MB",
                        "created": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
                    })
    
    # Sort by creation time (newest first)
    videos.sort(key=lambda x: x["created"], reverse=True)
    return videos[:10]  # Return last 10 videos

def get_system_status() -> str:
    """Get current system status"""
    status_parts = []
    
    # Process status
    status_parts.append(f"🔄 **Process Status:** {process_status}")
    
    # Recent videos count
    recent_videos = get_recent_videos()
    status_parts.append(f"📹 **Recent Videos:** {len(recent_videos)}")
    
    # Output directory status
    if os.path.exists("outputs"):
        total_files = len([f for f in os.listdir("outputs") if f.endswith(".mp4")])
        status_parts.append(f"📁 **Total Videos:** {total_files}")
    
    # Session directory status
    session_dirs = 0
    if os.path.exists("outputs"):
        session_dirs = len([d for d in os.listdir("outputs") if d.startswith("session_")])
    status_parts.append(f"📊 **Sessions:** {session_dirs}")
    
    return "\n".join(status_parts)

def format_recent_videos() -> str:
    """Format recent videos for display"""
    videos = get_recent_videos()
    if not videos:
        return "No recent videos found."
    
    lines = ["**Recent Videos:**"]
    for video in videos:
        lines.append(f"• {video['filename']} ({video['size']}) - {video['created']}")
    
    return "\n".join(lines)

def get_live_output() -> str:
    """Get live process output"""
    global process_output
    if not process_output:
        return "No active generation process."
    
    # Return last 20 lines
    recent_lines = process_output[-20:] if len(process_output) > 20 else process_output
    return "\n".join(recent_lines)

# Create Gradio interface
with gr.Blocks(title="🎬 Viral Video Generator", theme=gr.themes.Soft()) as app:
    gr.Markdown("# 🎬 Viral Video Generator")
    gr.Markdown("Generate viral videos with AI-powered composition and multi-agent discussions")
    
    with gr.Tabs():
        # Video Generation Tab
        with gr.TabItem("🎬 Generate Video"):
            with gr.Row():
                with gr.Column(scale=2):
                    topic = gr.Textbox(
                        label="Video Topic",
                        placeholder="Enter your video topic (e.g., 'AI revolutionizing content creation')",
                        lines=2
                    )
                    
                    with gr.Row():
                        duration = gr.Slider(
                            label="Duration (seconds)",
                            minimum=5,
                            maximum=60,
                            value=30,
                            step=5
                        )
                        
                        category = gr.Dropdown(
                            label="Category",
                            choices=["Comedy", "Education", "Entertainment", "News", "Technology"],
                            value="Comedy"
                        )
                    
                    with gr.Row():
                        platform = gr.Dropdown(
                            label="Platform",
                            choices=["youtube", "tiktok", "instagram", "facebook"],
                            value="youtube"
                        )
                        
                        discussions = gr.Dropdown(
                            label="Discussion Mode",
                            choices=["light", "standard", "deep"],
                            value="standard"
                        )
                    
                    frame_continuity = gr.Dropdown(
                        label="Frame Continuity",
                        choices=["auto", "on", "off"],
                        value="auto",
                        info="Let AI decide (auto) or force on/off"
                    )
                    
                    generate_btn = gr.Button("🎬 Generate Video", variant="primary", size="lg")
                
                with gr.Column(scale=1):
                    gr.Markdown("### 📊 Quick Stats")
                    system_status = gr.Markdown(get_system_status())
                    
                    gr.Markdown("### 📹 Recent Videos")
                    recent_videos = gr.Markdown(format_recent_videos())
            
            # Results Section
            with gr.Row():
                with gr.Column():
                    result_summary = gr.Markdown("Ready to generate videos!")
                    
                    with gr.Row():
                        video_output = gr.Video(label="Generated Video")
                        
            # Live Output
            with gr.Accordion("📝 Live Generation Log", open=False):
                live_output = gr.Textbox(
                    label="Process Output",
                    lines=10,
                    max_lines=20,
                    show_copy_button=True
                )
        
        # Monitoring Tab
        with gr.TabItem("📊 Monitor"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 🔄 System Status")
                    monitor_status = gr.Markdown(get_system_status())
                    
                    gr.Markdown("### 📹 Recent Sessions")
                    monitor_videos = gr.Markdown(format_recent_videos())
                
                with gr.Column():
                    gr.Markdown("### 📊 Live Output")
                    monitor_output = gr.Textbox(
                        label="Current Process Output",
                        lines=15,
                        max_lines=25,
                        show_copy_button=True
                    )
            
            refresh_btn = gr.Button("🔄 Refresh Status", variant="secondary")
    
    # Event handlers
    generate_btn.click(
        fn=run_video_generation,
        inputs=[topic, duration, category, platform, discussions, frame_continuity],
        outputs=[result_summary, video_output, live_output],
        show_progress=True
    )
    
    refresh_btn.click(
        fn=lambda: [get_system_status(), format_recent_videos(), get_live_output()],
        outputs=[monitor_status, monitor_videos, monitor_output]
    )
    
    # Auto-refresh monitoring every 5 seconds
    app.load(
        fn=lambda: [get_system_status(), format_recent_videos()],
        outputs=[system_status, recent_videos],
        every=5
    )

if __name__ == "__main__":
    print("🎬 Starting Viral Video Generator UI...")
    print("🌐 Access the interface at: http://localhost:7860")
    
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        show_tips=True
    ) 