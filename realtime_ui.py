#!/usr/bin/env python3
"""
Real-time Viral Video Generator UI
Fully functional with live progress updates and streaming output
"""

import gradio as gr
import subprocess
import os
import sys
import threading
import time
import queue
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class RealTimeVideoGenerator:
    """Real-time video generator with streaming progress updates"""
    
    def __init__(self):
        self.current_process = None
        self.output_queue = queue.Queue()
        self.progress_queue = queue.Queue()
        self.is_generating = False
        self.session_id = None
        self.start_time = None
        
    def parse_progress_from_output(self, line: str) -> Dict[str, Any]:
        """Parse progress information from output lines"""
        progress_info = {
            'progress': 0,
            'status': 'Processing...',
            'phase': 'Unknown',
            'details': line.strip()
        }
        
        # Parse different progress indicators
        if "Starting agent discussion" in line:
            progress_info.update({'progress': 10, 'phase': 'Agent Discussions', 'status': 'AI agents discussing strategy...'})
        elif "Script Discussion" in line or "script" in line.lower():
            progress_info.update({'progress': 20, 'phase': 'Script Development', 'status': 'Creating video script...'})
        elif "Visual Discussion" in line or "visual" in line.lower():
            progress_info.update({'progress': 35, 'phase': 'Visual Design', 'status': 'Designing visual elements...'})
        elif "Audio Discussion" in line or "audio" in line.lower() or "voice" in line.lower():
            progress_info.update({'progress': 50, 'phase': 'Audio Production', 'status': 'Generating voiceover...'})
        elif "VEO" in line or "video generation" in line.lower():
            progress_info.update({'progress': 65, 'phase': 'Video Generation', 'status': 'Creating video clips...'})
        elif "Assembly Discussion" in line or "composing" in line.lower():
            progress_info.update({'progress': 80, 'phase': 'Video Assembly', 'status': 'Assembling final video...'})
        elif "Generation Complete" in line or "completed successfully" in line:
            progress_info.update({'progress': 100, 'phase': 'Complete', 'status': 'Video generation completed!'})
        elif "Error" in line or "Failed" in line:
            progress_info.update({'progress': -1, 'phase': 'Error', 'status': 'Error occurred during generation'})
        
        return progress_info
    
    def stream_subprocess_output(self, cmd: List[str], session_id: str):
        """Stream subprocess output in real-time"""
        try:
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Read output line by line
            if self.current_process.stdout:
                for line in iter(self.current_process.stdout.readline, ''):
                    if not line:
                        break
                        
                    # Add to output queue
                    self.output_queue.put(line)
                    
                    # Parse progress
                    progress_info = self.parse_progress_from_output(line)
                    self.progress_queue.put(progress_info)
                    
                    # Check if process is still running
                    if self.current_process.poll() is not None:
                        break
            
            # Wait for process to complete
            return_code = self.current_process.wait()
            
            # Final status update
            if return_code == 0:
                self.progress_queue.put({
                    'progress': 100,
                    'phase': 'Complete',
                    'status': '✅ Video generation completed successfully!',
                    'details': 'Check the outputs directory for your video'
                })
            else:
                self.progress_queue.put({
                    'progress': -1,
                    'phase': 'Error',
                    'status': f'❌ Generation failed with code {return_code}',
                    'details': 'Check the output log for error details'
                })
                
        except Exception as e:
            self.progress_queue.put({
                'progress': -1,
                'phase': 'Error',
                'status': f'❌ Error: {str(e)}',
                'details': 'Subprocess execution failed'
            })
    
    def start_generation(self, topic: str, duration: int, category: str, platform: str, 
                        discussions: str, frame_continuity: str) -> str:
        """Start video generation process"""
        
        if self.is_generating:
            return "❌ Generation already in progress! Please wait for it to complete."
        
        if not topic.strip():
            return "❌ Please enter a topic!"
        
        # Create session ID
        self.session_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        self.start_time = datetime.now()
        self.is_generating = True
        
        # Clear queues
        while not self.output_queue.empty():
            self.output_queue.get()
        while not self.progress_queue.empty():
            self.progress_queue.get()
        
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
        
        # Start subprocess in background thread
        thread = threading.Thread(
            target=self.stream_subprocess_output,
            args=(cmd, self.session_id),
            daemon=True
        )
        thread.start()
        
        return f"🚀 Started generation for: '{topic}'\n📁 Session ID: {self.session_id}"
    
    def get_current_progress(self) -> Dict[str, Any]:
        """Get current progress information"""
        if not self.progress_queue.empty():
            return self.progress_queue.get()
        
        if self.is_generating:
            return {
                'progress': 5,
                'phase': 'Initializing',
                'status': 'Setting up generation...',
                'details': 'Preparing AI agents and resources'
            }
        else:
            return {
                'progress': 0,
                'phase': 'Ready',
                'status': 'Ready to generate video',
                'details': 'Enter a topic and click Generate to start'
            }
    
    def get_output_log(self) -> str:
        """Get accumulated output log"""
        lines = []
        while not self.output_queue.empty():
            lines.append(self.output_queue.get())
        
        if lines:
            return ''.join(lines)
        elif self.is_generating:
            return "🚀 Generation started...\n⏳ Waiting for output...\n"
        else:
            return "📋 Output log will appear here during generation\n"
    
    def stop_generation(self) -> str:
        """Stop current generation"""
        if self.current_process and self.current_process.poll() is None:
            self.current_process.terminate()
            self.is_generating = False
            return "🛑 Generation stopped by user"
        else:
            return "❌ No active generation to stop"
    
    def check_completion(self) -> bool:
        """Check if generation is complete"""
        if self.current_process and self.current_process.poll() is not None:
            self.is_generating = False
            return True
        return False
    
    def get_session_info(self) -> str:
        """Get current session information"""
        if not self.session_id:
            return "No active session"
        
        elapsed = datetime.now() - self.start_time if self.start_time else None
        elapsed_str = str(elapsed).split('.')[0] if elapsed else "Unknown"
        
        info = f"📁 Session ID: {self.session_id}\n"
        info += f"⏱️ Elapsed Time: {elapsed_str}\n"
        info += f"🔄 Status: {'Generating' if self.is_generating else 'Idle'}\n"
        
        # Check for output files
        outputs_dir = "outputs"
        if os.path.exists(outputs_dir):
            session_dirs = [d for d in os.listdir(outputs_dir) if d.startswith("session_")]
            if session_dirs:
                latest_session = max(session_dirs, key=lambda x: os.path.getctime(os.path.join(outputs_dir, x)))
                session_path = os.path.join(outputs_dir, latest_session)
                
                # Check for final video
                video_files = [f for f in os.listdir(session_path) if f.endswith('.mp4') and 'final' in f]
                if video_files:
                    info += f"🎬 Final Video: {video_files[0]}\n"
                    info += f"📂 Location: {os.path.join(session_path, video_files[0])}\n"
        
        return info

# Create global generator instance
generator = RealTimeVideoGenerator()

def create_realtime_ui():
    """Create the real-time UI with progress updates"""
    
    def update_progress():
        """Update progress display"""
        progress_info = generator.get_current_progress()
        
        # Create progress bar HTML
        progress_value = max(0, progress_info['progress'])
        if progress_value < 0:  # Error state
            progress_color = "#dc3545"
            progress_value = 100
        elif progress_value == 100:  # Complete
            progress_color = "#28a745"
        else:  # In progress
            progress_color = "#007bff"
        
        progress_html = f"""
        <div style="margin: 10px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span><strong>Phase:</strong> {progress_info['phase']}</span>
                <span><strong>Progress:</strong> {progress_value}%</span>
            </div>
            <div style="background: #e9ecef; border-radius: 10px; height: 25px; overflow: hidden;">
                <div style="background: {progress_color}; height: 100%; width: {progress_value}%; 
                           transition: width 0.5s ease; display: flex; align-items: center; 
                           justify-content: center; color: white; font-weight: bold; font-size: 12px;">
                    {progress_value}%
                </div>
            </div>
            <div style="margin-top: 5px; font-size: 14px;">
                <strong>Status:</strong> {progress_info['status']}
            </div>
        </div>
        """
        
        return progress_html
    
    def update_output():
        """Update output log"""
        return generator.get_output_log()
    
    def update_session_info():
        """Update session information"""
        return generator.get_session_info()
    
    def start_generation_wrapper(topic, duration, category, platform, discussions, frame_continuity):
        """Wrapper for starting generation"""
        return generator.start_generation(topic, duration, category, platform, discussions, frame_continuity)
    
    def stop_generation_wrapper():
        """Wrapper for stopping generation"""
        return generator.stop_generation()
    
    # Create the Gradio interface
    with gr.Blocks(title="🎬 Real-time Viral Video Generator") as demo:
        gr.HTML("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; margin-bottom: 20px;">
            <h1>🎬 Real-time Viral Video Generator</h1>
            <h3>✨ Live Progress Updates with 26+ AI Agents</h3>
            <p>Watch your video come to life in real-time with streaming progress updates!</p>
        </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML("<h3>📝 Generation Settings</h3>")
                
                topic_input = gr.Textbox(
                    label="🎯 Video Topic",
                    placeholder="Enter your video topic (e.g., 'A female character from Persian Mythology')",
                    lines=2,
                    value=""
                )
                
                with gr.Row():
                    duration_input = gr.Slider(
                        label="⏱️ Duration (seconds)",
                        minimum=10,
                        maximum=60,
                        value=30,
                        step=5
                    )
                    
                    category_input = gr.Dropdown(
                        label="📂 Category",
                        choices=["Comedy", "Educational", "Entertainment", "News", "Tech"],
                        value="Entertainment"
                    )
                
                with gr.Row():
                    platform_input = gr.Dropdown(
                        label="📱 Platform",
                        choices=["youtube", "tiktok", "instagram", "twitter"],
                        value="youtube"
                    )
                    
                    discussions_input = gr.Dropdown(
                        label="🤖 AI Discussion Mode",
                        choices=["light", "standard", "deep"],
                        value="standard"
                    )
                
                frame_continuity_input = gr.Dropdown(
                    label="🎬 Frame Continuity",
                    choices=["auto", "on", "off"],
                    value="auto"
                )
                
                with gr.Row():
                    generate_btn = gr.Button("🚀 Generate Video", variant="primary", size="lg")
                    stop_btn = gr.Button("🛑 Stop Generation", variant="stop", size="lg")
                
                generation_status = gr.Textbox(
                    label="🔄 Generation Status",
                    lines=3,
                    interactive=False
                )
            
            with gr.Column(scale=2):
                gr.HTML("<h3>📊 Live Progress Monitor</h3>")
                
                progress_display = gr.HTML(
                    value="<div style='padding: 20px; text-align: center; color: #666;'>Ready to generate video</div>",
                    label="Progress"
                )
                
                session_info = gr.Textbox(
                    label="📁 Session Information",
                    lines=6,
                    interactive=False,
                    value="No active session"
                )
                
                output_log = gr.Textbox(
                    label="📋 Live Output Log",
                    lines=15,
                    interactive=False,
                    value="Output log will appear here during generation...",
                    max_lines=30
                )
        
        # Help section
        with gr.Accordion("❓ Help & Information", open=False):
            gr.HTML("""
            <div style="padding: 15px;">
                <h4>🎬 How to Use</h4>
                <ul>
                    <li><strong>Topic:</strong> Enter your video topic (e.g., "A female character from Persian Mythology")</li>
                    <li><strong>Duration:</strong> Set video length (10-60 seconds)</li>
                    <li><strong>Category:</strong> Choose content category for optimization</li>
                    <li><strong>Platform:</strong> Target platform affects video format and style</li>
                    <li><strong>AI Discussion Mode:</strong> Level of AI agent collaboration</li>
                    <li><strong>Frame Continuity:</strong> How video clips connect visually</li>
                </ul>
                
                <h4>📊 Progress Phases</h4>
                <ul>
                    <li><strong>Agent Discussions:</strong> AI agents plan the video strategy</li>
                    <li><strong>Script Development:</strong> Creating the video script</li>
                    <li><strong>Visual Design:</strong> Designing visual elements</li>
                    <li><strong>Audio Production:</strong> Generating voiceover</li>
                    <li><strong>Video Generation:</strong> Creating video clips with VEO-2</li>
                    <li><strong>Video Assembly:</strong> Assembling the final video</li>
                </ul>
                
                <h4>🤖 AI Agent System</h4>
                <p>The system uses 26+ specialized AI agents working together:</p>
                <ul>
                    <li>Script Writers, Directors, and Editors</li>
                    <li>Audio Engineers and Voice Directors</li>
                    <li>Visual Designers and Style Directors</li>
                    <li>Platform Optimization Specialists</li>
                    <li>Quality Assurance Team</li>
                </ul>
            </div>
            """)
        
        # Event handlers
        generate_btn.click(
            fn=start_generation_wrapper,
            inputs=[topic_input, duration_input, category_input, platform_input, discussions_input, frame_continuity_input],
            outputs=[generation_status]
        )
        
        stop_btn.click(
            fn=stop_generation_wrapper,
            outputs=[generation_status]
        )
        
        # Auto-refresh components every 2 seconds during generation
        refresh_timer = gr.Timer(2)
        refresh_timer.tick(
            fn=lambda: [update_progress(), update_output(), update_session_info()],
            outputs=[progress_display, output_log, session_info]
        )
    
    return demo

if __name__ == "__main__":
    print("🎬 Starting Real-time Viral Video Generator UI...")
    print("🌐 Access at: http://localhost:7860")
    print("✨ Features: Live progress updates, streaming output, 26+ AI agents")
    
    demo = create_realtime_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    ) 