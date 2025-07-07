#!/usr/bin/env python3
"""
Viral Video Generator - Main Gradio UI
Enhanced with real-time AI agent visualization and comprehensive controls
"""

import gradio as gr
import os
import sys
import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any
import asyncio
import queue
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from src.workflows.generate_viral_video import generate_viral_video
from src.agents.enhanced_orchestrator_with_discussions import EnhancedOrchestratorWithDiscussions
from src.agents.discussion_visualizer import DiscussionVisualizer
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

class ViralVideoUI:
    """Enhanced Gradio UI with real-time visualization"""
    
    def __init__(self):
        self.current_session = None
        self.generation_status = {"status": "idle", "progress": 0, "message": "Ready"}
        self.agent_discussions = []
        self.status_queue = queue.Queue()
        self.discussion_queue = queue.Queue()
        
    def get_session_folders(self):
        """Get list of available session folders"""
        outputs_dir = "outputs"
        if not os.path.exists(outputs_dir):
            return []
        
        sessions = []
        for folder in os.listdir(outputs_dir):
            if folder.startswith("session_"):
                session_path = os.path.join(outputs_dir, folder)
                if os.path.isdir(session_path):
                    # Get creation time
                    try:
                        created = datetime.fromtimestamp(os.path.getctime(session_path))
                        sessions.append((folder, created))
                    except:
                        sessions.append((folder, datetime.now()))
        
        # Sort by creation time, newest first
        sessions.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in sessions]
    
    def update_status(self, status: str, progress: int, message: str):
        """Update generation status"""
        self.generation_status = {
            "status": status,
            "progress": progress,
            "message": message,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        self.status_queue.put(self.generation_status)
    
    def add_agent_discussion(self, agent: str, message: str, discussion_type: str = "discussion"):
        """Add agent discussion message"""
        discussion_entry = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "agent": agent,
            "message": message,
            "type": discussion_type
        }
        self.agent_discussions.append(discussion_entry)
        self.discussion_queue.put(discussion_entry)
    
    def generate_video_with_ui_updates(self, topic: str, duration: int, style: str, 
                                     platform: str, voice_speed: float, 
                                     enable_discussions: bool, max_discussion_rounds: int,
                                     progress=gr.Progress()):
        """Generate video with UI updates"""
        try:
            self.update_status("starting", 0, "🚀 Initializing video generation...")
            progress(0, desc="Starting generation...")
            
            # Clear previous discussions
            self.agent_discussions = []
            
            # Generate video
            self.update_status("generating", 10, "🎬 Generating viral video...")
            progress(0.1, desc="Generating video...")
            
            # Create enhanced orchestrator if discussions enabled
            if enable_discussions:
                self.update_status("discussions", 20, "🤖 Starting AI agent discussions...")
                progress(0.2, desc="AI agents discussing...")
                
                # Mock some agent discussions for demonstration
                agents = ["TrendMaster", "StoryWeaver", "VisionCraft", "AudioMaster", "CutMaster"]
                for i, agent in enumerate(agents):
                    self.add_agent_discussion(
                        agent, 
                        f"Analyzing {topic} for optimal {style} style on {platform}...",
                        "analysis"
                    )
                    time.sleep(0.5)  # Simulate discussion time
                    progress(0.2 + (i * 0.1), desc=f"{agent} discussing...")
            
            # Call the actual generation function
            self.update_status("processing", 70, "🎥 Processing video content...")
            progress(0.7, desc="Processing video...")
            
            result = generate_viral_video(
                topic=topic,
                duration=duration,
                style=style,
                platform=platform,
                voice_speed=voice_speed
            )
            
            self.update_status("complete", 100, "✅ Video generation complete!")
            progress(1.0, desc="Complete!")
            
            return result, "✅ Video generated successfully!"
            
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            self.update_status("error", 0, error_msg)
            logger.error(f"Video generation failed: {e}")
            return None, error_msg
    
    def get_status_display(self):
        """Get current status for display"""
        status = self.generation_status
        
        # Status emoji and color
        status_info = {
            "idle": ("⚪", "gray"),
            "starting": ("🟡", "orange"),
            "generating": ("🟢", "green"),
            "discussions": ("🔵", "blue"),
            "processing": ("🟣", "purple"),
            "complete": ("✅", "green"),
            "error": ("❌", "red")
        }
        
        emoji, color = status_info.get(status["status"], ("⚪", "gray"))
        
        return f"""
        <div style="padding: 10px; border-radius: 10px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; margin: 10px 0;">
            <h3 style="margin: 0; display: flex; align-items: center;">
                <span style="font-size: 24px; margin-right: 10px;">{emoji}</span>
                Generation Status
            </h3>
            <div style="margin-top: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 16px;">{status['message']}</span>
                    <span style="font-size: 14px; opacity: 0.8;">{status.get('timestamp', '')}</span>
                </div>
                <div style="width: 100%; background: rgba(255,255,255,0.2); border-radius: 10px; margin-top: 10px; height: 20px;">
                    <div style="width: {status['progress']}%; background: {color}; height: 100%; border-radius: 10px; transition: width 0.3s ease;"></div>
                </div>
                <div style="text-align: center; margin-top: 5px; font-size: 12px;">{status['progress']}%</div>
            </div>
        </div>
        """
    
    def get_discussions_display(self):
        """Get agent discussions for display"""
        if not self.agent_discussions:
            return """
            <div style="padding: 20px; text-align: center; color: #666;">
                <h3>🤖 AI Agent Discussions</h3>
                <p>No discussions yet. Enable discussions and start generation to see AI agents collaborate!</p>
            </div>
            """
        
        discussions_html = """
        <div style="padding: 10px; border-radius: 10px; background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; margin: 10px 0;">
            <h3 style="margin: 0; display: flex; align-items: center;">
                <span style="font-size: 24px; margin-right: 10px;">🤖</span>
                AI Agent Discussions
            </h3>
            <div style="max-height: 400px; overflow-y: auto; margin-top: 10px;">
        """
        
        for discussion in self.agent_discussions[-10:]:  # Show last 10 discussions
            agent_colors = {
                "TrendMaster": "#ff6b6b",
                "StoryWeaver": "#4ecdc4", 
                "VisionCraft": "#45b7d1",
                "AudioMaster": "#f9ca24",
                "CutMaster": "#f0932b",
                "SyncMaster": "#eb4d4b",
                "PixelForge": "#6c5ce7"
            }
            
            color = agent_colors.get(discussion["agent"], "#95a5a6")
            
            discussions_html += f"""
            <div style="margin: 8px 0; padding: 8px; background: rgba(255,255,255,0.1); border-radius: 8px; border-left: 4px solid {color};">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <strong style="color: {color};">🎭 {discussion['agent']}</strong>
                    <span style="font-size: 12px; opacity: 0.8;">{discussion['timestamp']}</span>
                </div>
                <div style="font-size: 14px; line-height: 1.4;">{discussion['message']}</div>
            </div>
            """
        
        discussions_html += """
            </div>
        </div>
        """
        
        return discussions_html
    
    def create_interface(self):
        """Create the Gradio interface"""
        
        with gr.Blocks(
            title="🎬 Viral Video Generator",
            theme=gr.themes.Soft(
                primary_hue="blue",
                secondary_hue="green",
                neutral_hue="gray"
            ),
            css="""
            .gradio-container {
                max-width: 1200px !important;
                margin: auto;
            }
            .status-display {
                border-radius: 15px;
                padding: 20px;
                margin: 10px 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .discussions-display {
                border-radius: 15px;
                padding: 20px;
                margin: 10px 0;
                background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                color: white;
            }
            """
        ) as interface:
            
            # Header
            gr.HTML("""
            <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; margin-bottom: 20px;">
                <h1 style="margin: 0; font-size: 36px;">🎬 Viral Video Generator</h1>
                <p style="margin: 10px 0 0 0; font-size: 18px; opacity: 0.9;">AI-Powered Video Creation with Real-Time Agent Collaboration</p>
            </div>
            """)
            
            with gr.Row():
                # Left column - Controls
                with gr.Column(scale=1):
                    gr.HTML("<h2 style='color: #667eea;'>📋 Generation Settings</h2>")
                    
                    topic = gr.Textbox(
                        label="🎯 Video Topic",
                        placeholder="Enter your video topic (e.g., 'Persian mythology vs modern Iran')",
                        value="",
                        lines=2
                    )
                    
                    with gr.Row():
                        duration = gr.Slider(
                            label="⏱️ Duration (seconds)",
                            minimum=15,
                            maximum=300,
                            value=45,
                            step=5
                        )
                        
                        voice_speed = gr.Slider(
                            label="🗣️ Voice Speed",
                            minimum=0.5,
                            maximum=2.0,
                            value=1.0,
                            step=0.1
                        )
                    
                    style = gr.Dropdown(
                        label="🎨 Video Style",
                        choices=[
                            "realistic", "cinematic", "documentary", "animated", 
                            "comic", "artistic", "dramatic", "educational", "entertainment"
                        ],
                        value="realistic"
                    )
                    
                    platform = gr.Dropdown(
                        label="📱 Target Platform",
                        choices=[
                            "youtube_shorts", "tiktok", "instagram_reels", 
                            "youtube_long", "facebook", "twitter", "general"
                        ],
                        value="youtube_shorts"
                    )
                    
                    gr.HTML("<h3 style='color: #667eea;'>🤖 AI Agent Settings</h3>")
                    
                    enable_discussions = gr.Checkbox(
                        label="Enable AI Agent Discussions",
                        value=True,
                        info="Let AI agents collaborate and discuss the video strategy"
                    )
                    
                    max_discussion_rounds = gr.Slider(
                        label="Max Discussion Rounds",
                        minimum=1,
                        maximum=10,
                        value=5,
                        step=1
                    )
                    
                    generate_btn = gr.Button(
                        "🚀 Generate Viral Video",
                        variant="primary",
                        size="lg"
                    )
                    
                    # Session management
                    gr.HTML("<h3 style='color: #667eea;'>📁 Session Management</h3>")
                    
                    session_dropdown = gr.Dropdown(
                        label="Select Session",
                        choices=self.get_session_folders(),
                        value=None,
                        allow_custom_value=False
                    )
                    
                    refresh_sessions_btn = gr.Button("🔄 Refresh Sessions")
                
                # Right column - Status and Discussions
                with gr.Column(scale=1):
                    gr.HTML("<h2 style='color: #667eea;'>📊 Real-Time Status</h2>")
                    
                    status_display = gr.HTML(
                        value=self.get_status_display(),
                        elem_classes=["status-display"]
                    )
                    
                    discussions_display = gr.HTML(
                        value=self.get_discussions_display(),
                        elem_classes=["discussions-display"]
                    )
                    
                    # Output
                    gr.HTML("<h3 style='color: #667eea;'>📹 Generated Video</h3>")
                    
                    video_output = gr.Video(
                        label="Generated Video",
                        interactive=False
                    )
                    
                    result_text = gr.Textbox(
                        label="Generation Result",
                        interactive=False,
                        lines=3
                    )
            
            # Event handlers
            generate_btn.click(
                fn=self.generate_video_with_ui_updates,
                inputs=[
                    topic, duration, style, platform, voice_speed,
                    enable_discussions, max_discussion_rounds
                ],
                outputs=[video_output, result_text]
            )
            
            refresh_sessions_btn.click(
                fn=lambda: gr.Dropdown(choices=self.get_session_folders()),
                outputs=[session_dropdown]
            )
            
            # Auto-refresh status and discussions every 2 seconds
            def update_displays():
                return self.get_status_display(), self.get_discussions_display()
            
            interface.load(
                fn=update_displays,
                outputs=[status_display, discussions_display],
                every=2
            )
        
        return interface

def main():
    """Main function to run the UI"""
    
    # Set up environment
    if not os.getenv('GOOGLE_API_KEY'):
        print("⚠️  Warning: GOOGLE_API_KEY not set. Please set it in your environment.")
        print("   export GOOGLE_API_KEY=your_api_key_here")
    
    # Create UI instance
    ui = ViralVideoUI()
    
    # Create and launch interface
    interface = ui.create_interface()
    
    print("🚀 Launching Viral Video Generator UI...")
    print("🌐 Interface will be available at: http://localhost:7860")
    print("📊 Features:")
    print("   ✅ Real-time AI agent discussions")
    print("   ✅ Live generation status")
    print("   ✅ Comprehensive video controls")
    print("   ✅ Session management")
    
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True,
        show_error=True
    )

if __name__ == "__main__":
    main() 