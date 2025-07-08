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
        
        # Run command
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        end_time = time.time()
        
        # Process output
        if result.returncode == 0:
            # Success
            output_text = f"✅ Video generated successfully!\n\n"
            output_text += f"⏱️ Generation time: {end_time - start_time:.1f} seconds\n\n"
            output_text += "📋 Generation Log:\n"
            output_text += result.stdout
            
            # Try to find the video file
            video_file = None
            for line in result.stdout.split('\n'):
                if 'final_video_' in line and '.mp4' in line:
                    # Extract file path
                    if 'Output:' in line:
                        video_file = line.split('Output:')[-1].strip()
                    elif 'Video file:' in line:
                        video_file = line.split('Video file:')[-1].strip()
            
            return output_text, video_file, "Success"
        else:
            # Error
            error_text = f"❌ Video generation failed!\n\n"
            error_text += f"Exit code: {result.returncode}\n\n"
            error_text += "Error output:\n"
            error_text += result.stderr
            error_text += "\n\nStdout:\n"
            error_text += result.stdout
            
            return error_text, None, "Error"
            
    except subprocess.TimeoutExpired:
        return "❌ Generation timed out (5 minutes)", None, "Timeout"
    except Exception as e:
        return f"❌ Error running generation: {str(e)}", None, "Error"

def run_topic_generation(idea: str, platform: str, audience: str, style: str, 
                        duration: int, category: str, auto_generate: bool):
    """Run topic generation via main.py subprocess"""
    
    if not idea.strip():
        return "❌ Please enter an idea!", None, "Error: No idea provided"
    
    try:
        # Build command
        cmd = [
            "python3", "main.py", "generate-topic",
            "--idea", idea,
            "--platform", platform,
            "--duration", str(duration),
            "--category", category
        ]
        
        # Add optional parameters
        if audience:
            cmd.extend(["--audience", audience])
        if style:
            cmd.extend(["--style", style])
        if auto_generate:
            cmd.append("--generate-video")
        
        # Run command
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        end_time = time.time()
        
        # Process output
        if result.returncode == 0:
            # Success
            output_text = f"✅ Topic generated successfully!\n\n"
            output_text += f"⏱️ Generation time: {end_time - start_time:.1f} seconds\n\n"
            output_text += "📋 Generation Log:\n"
            output_text += result.stdout
            
            # Try to extract the generated topic
            generated_topic = None
            for line in result.stdout.split('\n'):
                if 'Generated Topic:' in line:
                    generated_topic = line.split('Generated Topic:')[-1].strip()
                    break
            
            return output_text, generated_topic, "Success"
        else:
            # Error
            error_text = f"❌ Topic generation failed!\n\n"
            error_text += f"Exit code: {result.returncode}\n\n"
            error_text += "Error output:\n"
            error_text += result.stderr
            error_text += "\n\nStdout:\n"
            error_text += result.stdout
            
            return error_text, None, "Error"
            
    except subprocess.TimeoutExpired:
        return "❌ Topic generation timed out (5 minutes)", None, "Timeout"
    except Exception as e:
        return f"❌ Error running topic generation: {str(e)}", None, "Error"

def create_ui():
    """Create the Gradio UI"""
    
    with gr.Blocks(title="🎬 Viral Video Generator", theme=gr.themes.Soft()) as demo:
        gr.HTML("<h1>🎬 Enhanced Viral Video Generator v2.0</h1>")
        gr.HTML("<p>Professional-grade viral video generation with AI agents and advanced composition</p>")
        
        with gr.Tabs():
            # Video Generation Tab
            with gr.TabItem("🎬 Generate Video"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.HTML("<h3>📝 Video Configuration</h3>")
                        
                        topic = gr.Textbox(
                            label="Video Topic",
                            placeholder="Enter your video topic here...",
                            lines=2
                        )
                        
                        with gr.Row():
                            duration = gr.Slider(
                                label="Duration (seconds)",
                                minimum=10,
                                maximum=60,
                                value=30,
                                step=5
                            )
                            
                            category = gr.Dropdown(
                                label="Category",
                                choices=["Comedy", "Educational", "Entertainment", "News", "Technology"],
                                value="Comedy"
                            )
                        
                        with gr.Row():
                            platform = gr.Dropdown(
                                label="Platform",
                                choices=["youtube", "tiktok", "instagram", "twitter"],
                                value="youtube"
                            )
                            
                            discussions = gr.Dropdown(
                                label="AI Discussions",
                                choices=["light", "standard", "deep"],
                                value="standard"
                            )
                        
                        frame_continuity = gr.Dropdown(
                            label="Frame Continuity",
                            choices=["auto", "on", "off"],
                            value="auto"
                        )
                        
                        generate_btn = gr.Button("🎬 Generate Video", variant="primary")
                    
                    with gr.Column(scale=2):
                        gr.HTML("<h3>📊 Generation Results</h3>")
                        
                        output_text = gr.Textbox(
                            label="Generation Log",
                            lines=15,
                            max_lines=20,
                            interactive=False
                        )
                        
                        video_file = gr.File(
                            label="Generated Video",
                            file_types=[".mp4"]
                        )
                        
                        status = gr.Textbox(
                            label="Status",
                            interactive=False
                        )
                
                generate_btn.click(
                    fn=run_video_generation,
                    inputs=[topic, duration, category, platform, discussions, frame_continuity],
                    outputs=[output_text, video_file, status]
                )
            
            # Topic Generation Tab
            with gr.TabItem("🎯 Generate Topic"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.HTML("<h3>💡 AI-Powered Topic Generation</h3>")
                        gr.HTML("<p>Let AI agents discuss and create the perfect topic for your idea</p>")
                        
                        idea = gr.Textbox(
                            label="High-Level Idea",
                            placeholder="e.g., 'convince people to vote', 'promote environmental awareness'",
                            lines=3
                        )
                        
                        with gr.Row():
                            topic_platform = gr.Dropdown(
                                label="Target Platform",
                                choices=["youtube", "tiktok", "instagram", "twitter"],
                                value="youtube"
                            )
                            
                            topic_category = gr.Dropdown(
                                label="Category",
                                choices=["Comedy", "Educational", "Entertainment", "News", "Technology"],
                                value="Educational"
                            )
                        
                        with gr.Row():
                            audience = gr.Textbox(
                                label="Target Audience (Optional)",
                                placeholder="e.g., 'Young adults', 'Professionals'"
                            )
                            
                            style = gr.Textbox(
                                label="Content Style (Optional)",
                                placeholder="e.g., 'Engaging', 'Educational', 'Humorous'"
                            )
                        
                        topic_duration = gr.Slider(
                            label="Target Duration (seconds)",
                            minimum=10,
                            maximum=60,
                            value=30,
                            step=5
                        )
                        
                        auto_generate = gr.Checkbox(
                            label="🎬 Auto-generate video after topic creation",
                            value=False
                        )
                        
                        generate_topic_btn = gr.Button("🎯 Generate Topic", variant="primary")
                    
                    with gr.Column(scale=2):
                        gr.HTML("<h3>📋 Topic Generation Results</h3>")
                        
                        topic_output = gr.Textbox(
                            label="Generation Log",
                            lines=15,
                            max_lines=20,
                            interactive=False
                        )
                        
                        generated_topic = gr.Textbox(
                            label="Generated Topic",
                            interactive=False
                        )
                        
                        topic_status = gr.Textbox(
                            label="Status",
                            interactive=False
                        )
                
                generate_topic_btn.click(
                    fn=run_topic_generation,
                    inputs=[idea, topic_platform, audience, style, topic_duration, topic_category, auto_generate],
                    outputs=[topic_output, generated_topic, topic_status]
                )
            
            # Help Tab
            with gr.TabItem("❓ Help"):
                gr.HTML("""
                <h3>🎬 How to Use</h3>
                
                <h4>📝 Video Generation</h4>
                <ul>
                    <li><strong>Topic:</strong> Enter the main subject of your video</li>
                    <li><strong>Duration:</strong> Set video length (10-60 seconds)</li>
                    <li><strong>Category:</strong> Choose content category for optimization</li>
                    <li><strong>Platform:</strong> Target platform affects video format and style</li>
                    <li><strong>AI Discussions:</strong> Level of AI agent collaboration</li>
                    <li><strong>Frame Continuity:</strong> How clips connect visually</li>
                </ul>
                
                <h4>🎯 Topic Generation</h4>
                <ul>
                    <li><strong>High-Level Idea:</strong> Your broad goal or message</li>
                    <li><strong>Target Platform:</strong> Where the video will be published</li>
                    <li><strong>Target Audience:</strong> Who you want to reach</li>
                    <li><strong>Content Style:</strong> Tone and approach</li>
                    <li><strong>Auto-generate:</strong> Automatically create video after topic</li>
                </ul>
                
                <h4>🤖 AI Agent System</h4>
                <p>The system uses 26+ specialized AI agents across 6 phases:</p>
                <ul>
                    <li><strong>Script Development:</strong> Content creation and optimization</li>
                    <li><strong>Audio Production:</strong> Voice and sound design</li>
                    <li><strong>Visual Design:</strong> Graphics and visual elements</li>
                    <li><strong>Platform Optimization:</strong> Platform-specific adjustments</li>
                    <li><strong>Quality Assurance:</strong> Final review and polish</li>
                    <li><strong>Advanced Specialists:</strong> Cutting-edge enhancements</li>
                </ul>
                
                <h4>📊 Discussion Modes</h4>
                <ul>
                    <li><strong>Light:</strong> Quick consensus, faster generation</li>
                    <li><strong>Standard:</strong> Balanced discussion and quality</li>
                    <li><strong>Deep:</strong> Thorough analysis, best quality</li>
                </ul>
                
                <h4>🎬 Frame Continuity</h4>
                <ul>
                    <li><strong>Auto:</strong> AI decides based on content and platform</li>
                    <li><strong>On:</strong> Smooth transitions between clips</li>
                    <li><strong>Off:</strong> Jump cuts for dynamic pacing</li>
                </ul>
                """)
    
    return demo

if __name__ == "__main__":
    print("🎬 Starting Simple Viral Video Generator UI...")
    print("🌐 Access at: http://localhost:7860")
    
    demo = create_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    ) 