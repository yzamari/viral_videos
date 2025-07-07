#!/usr/bin/env python3
"""
Simple Test UI for Viral Video Generator
"""

import gradio as gr
import subprocess
import os
import time
from datetime import datetime

def run_video_generation(topic: str, duration: int, category: str, platform: str, 
                        discussions: str, frame_continuity: str):
    """Run video generation via main.py subprocess"""
    
    if not topic.strip():
        return "❌ Please enter a topic!", None, "Error: No topic provided"
    
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
        
        # Run process
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        # Parse output
        output = result.stdout + result.stderr
        
        if result.returncode == 0:
            # Find video file
            video_path = None
            for line in output.split('\n'):
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
            for line in output.split('\n'):
                if "Frame Continuity" in line and ("✅ ENABLED" in line or "❌ DISABLED" in line):
                    frame_decision = "Enabled" if "✅ ENABLED" in line else "Disabled"
                    break
            
            # Extract discussion info
            total_discussions = 0
            avg_consensus = 0.0
            
            for line in output.split('\n'):
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
            
            summary = f"""
✅ **Video Generation Successful!**

📁 **Output:** {video_path or 'Video file not found'}
🎬 **Frame Continuity:** {frame_decision}
🤖 **AI Discussions:** {total_discussions} discussions, {avg_consensus:.1%} avg consensus

**Settings:**
- Topic: {topic}
- Duration: {duration}s
- Platform: {platform}
- Category: {category}
"""
            
            return summary, video_path, output
            
        else:
            error_summary = f"""
❌ **Video Generation Failed**

**Error Code:** {result.returncode}
**Error Output:**
{output[-1000:] if len(output) > 1000 else output}
"""
            return error_summary, None, output
            
    except subprocess.TimeoutExpired:
        return "❌ Generation timed out (10 minutes)", None, "Process timed out"
    except Exception as e:
        return f"❌ Error: {str(e)}", None, str(e)

def get_recent_videos():
    """Get recent videos info"""
    if not os.path.exists("outputs"):
        return "No outputs directory found."
    
    videos = []
    for filename in os.listdir("outputs"):
        if filename.startswith("final_video_") and filename.endswith(".mp4"):
            filepath = os.path.join("outputs", filename)
            if os.path.exists(filepath):
                stat = os.stat(filepath)
                videos.append({
                    "filename": filename,
                    "size": f"{stat.st_size / 1024 / 1024:.1f}MB",
                    "created": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
                })
    
    if not videos:
        return "No recent videos found."
    
    # Sort by creation time (newest first)
    videos.sort(key=lambda x: x["created"], reverse=True)
    
    lines = ["**Recent Videos:**"]
    for video in videos[:5]:  # Show last 5
        lines.append(f"• {video['filename']} ({video['size']}) - {video['created']}")
    
    return "\n".join(lines)

# Create interface
with gr.Blocks(title="🎬 Viral Video Generator") as app:
    gr.Markdown("# 🎬 Viral Video Generator")
    gr.Markdown("Generate viral videos with AI-powered composition and multi-agent discussions")
    
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
            gr.Markdown("### 📊 System Info")
            recent_videos = gr.Markdown(get_recent_videos())
            
            refresh_btn = gr.Button("🔄 Refresh", variant="secondary")
    
    # Results
    with gr.Row():
        result_summary = gr.Markdown("Ready to generate videos!")
    
    with gr.Row():
        video_output = gr.Video(label="Generated Video")
    
    with gr.Accordion("📝 Full Output Log", open=False):
        full_output = gr.Textbox(
            label="Process Output",
            lines=15,
            max_lines=30,
            show_copy_button=True
        )
    
    # Event handlers
    generate_btn.click(
        fn=run_video_generation,
        inputs=[topic, duration, category, platform, discussions, frame_continuity],
        outputs=[result_summary, video_output, full_output]
    )
    
    refresh_btn.click(
        fn=get_recent_videos,
        outputs=[recent_videos]
    )

if __name__ == "__main__":
    print("🎬 Starting Simple Viral Video Generator UI...")
    print("🌐 Access at: http://localhost:7860")
    
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    ) 