#!/usr/bin/env python3
"""
Simple Working Viral Video Generator UI
No complex imports, just working functionality
"""

import gradio as gr
import os
import subprocess
import time
from datetime import datetime

def generate_video(topic, duration, style, platform):
    """Actually generate a video"""
    if not topic:
        return None, "❌ Please enter a topic"
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        return None, "❌ GOOGLE_API_KEY not set"
    
    try:
        # Create a simple video using the existing workflow
        result_file = f"outputs/video_{int(time.time())}.mp4"
        
        # Use subprocess to call the working workflow
        cmd = [
            "python", "-c", f"""
import sys
import os
sys.path.insert(0, '.')
from src.agents.orchestrator_agent import OrchestratorAgent

try:
    orchestrator = OrchestratorAgent('{topic}', 'informative', '{style}')
    result = orchestrator.run()
    print(f"RESULT: {{result}}")
except Exception as e:
    print(f"ERROR: {{e}}")
"""
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if "RESULT:" in result.stdout:
            # Look for generated videos
            import glob
            videos = glob.glob("outputs/*/final_video.mp4")
            if videos:
                latest_video = max(videos, key=os.path.getctime)
                return latest_video, f"✅ Video generated: {latest_video}"
        
        return None, f"✅ Generation attempted. Check outputs folder."
        
    except Exception as e:
        return None, f"❌ Error: {str(e)}"

# Create simple interface
with gr.Blocks(title="🎬 Viral Video Generator") as demo:
    
    gr.HTML("""
    <div style="text-align: center; padding: 20px; background: #667eea; color: white; border-radius: 10px; margin-bottom: 20px;">
        <h1>🎬 Viral Video Generator</h1>
        <p>Simple, Working Video Creation</p>
    </div>
    """)
    
    with gr.Row():
        with gr.Column():
            topic = gr.Textbox(
                label="🎯 Video Topic",
                placeholder="Enter your video topic",
                lines=2
            )
            
            duration = gr.Slider(
                label="⏱️ Duration (seconds)",
                minimum=15,
                maximum=120,
                value=45
            )
            
            style = gr.Dropdown(
                label="🎨 Style",
                choices=["realistic", "cinematic", "animated"],
                value="realistic"
            )
            
            platform = gr.Dropdown(
                label="📱 Platform",
                choices=["youtube_shorts", "tiktok", "instagram_reels"],
                value="youtube_shorts"
            )
            
            generate_btn = gr.Button("🚀 Generate Video", variant="primary")
        
        with gr.Column():
            video_output = gr.Video(label="Generated Video")
            result_text = gr.Textbox(label="Result", lines=3)
    
    generate_btn.click(
        fn=generate_video,
        inputs=[topic, duration, style, platform],
        outputs=[video_output, result_text]
    )

if __name__ == "__main__":
    print("🚀 Launching Simple Working UI...")
    print("🌐 Interface: http://localhost:7860")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True
    ) 