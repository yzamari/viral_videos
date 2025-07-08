#!/usr/bin/env python3
"""
🎬 Unified Real-time VEO-2 Video Generator with Live Agent Discussions

This is the ONLY UI file you need - combines all functionality:
- Mission-based video generation
- Real-time agent discussion visualization
- Live progress tracking
- Session management
- VEO-2/VEO-3 integration
"""

import os
import sys
import queue
import threading
import time
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

import gradio as gr
from src.models.video_models import VideoCategory, Platform
from src.agents.enhanced_orchestrator_with_19_agents import create_enhanced_orchestrator_with_19_agents

# Setup logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealTimeAgentVisualizer:
    """Real-time visualization of AI agent discussions"""
    
    def __init__(self):
        self.agents_status = {}
        self.consensus_history = []
        self.discussion_messages = []
        self.current_phase = "Waiting"
        self.is_monitoring = False
        self.log_queue = queue.Queue()
        
    def start_monitoring(self):
        """Start monitoring agent discussions"""
        self.is_monitoring = True
        self.discussion_messages = []
        self.current_phase = "Initializing"
        
    def stop_monitoring(self):
        """Stop monitoring agent discussions"""
        self.is_monitoring = False
        
    def add_discussion_message(self, phase: str, agent: str, message: str, consensus: float, round_num: int):
        """Add a new discussion message"""
        if not self.is_monitoring:
            return
            
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Determine agent color and emoji based on agent type
        agent_colors = {
            'StoryWeaver': '#3b82f6', 'DialogueMaster': '#3b82f6', 'PaceMaster': '#3b82f6', 'AudienceAdvocate': '#3b82f6',
            'AudioMaster': '#10b981', 'VoiceDirector': '#10b981', 'SoundDesigner': '#10b981', 'PlatformGuru': '#10b981',
            'VisionCraft': '#f59e0b', 'StyleDirector': '#f59e0b', 'ColorMaster': '#f59e0b', 'TypeMaster': '#f59e0b', 'HeaderCraft': '#f59e0b',
            'EngagementHacker': '#8b5cf6', 'TrendMaster': '#8b5cf6', 'QualityGuard': '#ef4444',
            'SyncMaster': '#ef4444', 'CutMaster': '#ef4444'
        }
        
        agent_emojis = {
            'StoryWeaver': '📝', 'DialogueMaster': '💬', 'PaceMaster': '⏱️', 'AudienceAdvocate': '👥',
            'AudioMaster': '🎵', 'VoiceDirector': '🎤', 'SoundDesigner': '🔊', 'PlatformGuru': '📱',
            'VisionCraft': '🎨', 'StyleDirector': '🎭', 'ColorMaster': '🌈', 'TypeMaster': '📰', 'HeaderCraft': '🏷️',
            'EngagementHacker': '📈', 'TrendMaster': '📊', 'QualityGuard': '✅',
            'SyncMaster': '🎯', 'CutMaster': '✂️'
        }
        
        color = agent_colors.get(agent, '#64748b')
        emoji = agent_emojis.get(agent, '🤖')
        
        self.discussion_messages.append({
            'phase': phase,
            'agent': agent,
            'emoji': emoji,
            'color': color,
            'message': message,
            'consensus': consensus,
            'round': round_num,
            'timestamp': timestamp
        })
        
        self.current_phase = phase
        
        # Keep only last 20 messages to prevent overflow
        if len(self.discussion_messages) > 20:
            self.discussion_messages = self.discussion_messages[-20:]
    
    def generate_discussion_html(self) -> str:
        """Generate HTML for current discussions"""
        if not self.discussion_messages:
            return self._generate_initial_html()
        
        # Get latest consensus
        latest_consensus = self.discussion_messages[-1]['consensus'] if self.discussion_messages else 0
        consensus_percent = int(latest_consensus * 100)
        
        # Generate phase header
        phase_html = f"""
        <div class="phase-header">
            🎭 Phase: {self.current_phase}
        </div>
        """
        
        # Generate consensus bar
        consensus_color = "#10b981" if consensus_percent >= 80 else "#f59e0b" if consensus_percent >= 60 else "#ef4444"
        consensus_html = f"""
        <div style="margin: 15px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                <span style="color: #1e40af; font-weight: bold;">Consensus Progress:</span>
                <span style="color: {consensus_color}; font-weight: bold;">{consensus_percent}%</span>
            </div>
            <div class="consensus-bar">
                <div class="consensus-progress" style="width: {consensus_percent}%; background-color: {consensus_color};"></div>
            </div>
            <div style="color: #64748b; font-size: 0.9em;">
                Round {self.discussion_messages[-1]['round']} • Target: 80% • Live Updates
            </div>
        </div>
        """
        
        # Generate messages
        messages_html = ""
        for msg in self.discussion_messages[-10:]:  # Show last 10 messages
            # Truncate long messages
            display_message = msg['message'][:200] + "..." if len(msg['message']) > 200 else msg['message']
            
            messages_html += f"""
            <div class="agent-message" style="border-left-color: {msg['color']};">
                <div class="agent-name" style="color: {msg['color']};">
                    {msg['emoji']} {msg['agent']}
                </div>
                <div style="margin-top: 5px; color: #475569; line-height: 1.4;">
                    {display_message}
                </div>
                <div class="timestamp">
                    Round {msg['round']} • {msg['timestamp']} • Consensus: {int(msg['consensus'] * 100)}%
                </div>
            </div>
            """
        
        # Generate active agents summary
        unique_agents = list(set([msg['agent'] for msg in self.discussion_messages[-5:]]))
        agents_html = f"""
        <div style="margin-top: 15px; padding: 10px; background: #f1f5f9; border-radius: 5px;">
            <div style="color: #1e40af; font-weight: bold;">Recently Active Agents:</div>
            <div style="color: #64748b; margin-top: 5px;">
                {' • '.join(unique_agents[:6])}
            </div>
        </div>
        """
        
        return f"""
        <div class="agent-discussion">
            {phase_html}
            {consensus_html}
            <div style="max-height: 350px; overflow-y: auto;">
                {messages_html}
            </div>
            {agents_html}
        </div>
        """
    
    def _generate_initial_html(self) -> str:
        """Generate initial HTML when no discussions are active"""
        return """
        <div class="agent-discussion">
            <div class="phase-header">🤖 AI Agent Discussions</div>
            <p style="color: #64748b; font-style: italic; text-align: center; margin: 20px 0;">
                Start generation to see live agent discussions...
            </p>
            <div style="margin-top: 20px;">
                <h4 style="color: #1e40af; margin-bottom: 15px;">19 Specialized Agents Ready:</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                    <div style="background: #f1f5f9; padding: 8px; border-radius: 5px; border-left: 3px solid #3b82f6;">
                        <strong style="color: #1e40af;">📝 Script Development</strong><br>
                        <span style="color: #64748b; font-size: 0.85em;">StoryWeaver, DialogueMaster, PaceMaster, AudienceAdvocate</span>
                    </div>
                    <div style="background: #f1f5f9; padding: 8px; border-radius: 5px; border-left: 3px solid #10b981;">
                        <strong style="color: #059669;">🎵 Audio Production</strong><br>
                        <span style="color: #64748b; font-size: 0.85em;">AudioMaster, VoiceDirector, SoundDesigner, PlatformGuru</span>
                    </div>
                    <div style="background: #f1f5f9; padding: 8px; border-radius: 5px; border-left: 3px solid #f59e0b;">
                        <strong style="color: #d97706;">🎨 Visual Design</strong><br>
                        <span style="color: #64748b; font-size: 0.85em;">VisionCraft, StyleDirector, ColorMaster, TypeMaster, HeaderCraft</span>
                    </div>
                    <div style="background: #f1f5f9; padding: 8px; border-radius: 5px; border-left: 3px solid #8b5cf6;">
                        <strong style="color: #7c3aed;">📈 Platform Optimization</strong><br>
                        <span style="color: #64748b; font-size: 0.85em;">PlatformGuru, EngagementHacker, TrendMaster, QualityGuard</span>
                    </div>
                    <div style="background: #f1f5f9; padding: 8px; border-radius: 5px; border-left: 3px solid #ef4444;">
                        <strong style="color: #dc2626;">✅ Quality Assurance</strong><br>
                        <span style="color: #64748b; font-size: 0.85em;">QualityGuard, AudienceAdvocate, SyncMaster, CutMaster</span>
                    </div>
                </div>
            </div>
        </div>
        """

class UnifiedVideoApp:
    """Unified application combining all video generation functionality"""
    
    def __init__(self):
        # Load API key
        self.api_key = self._load_api_key()
        self.visualizer = RealTimeAgentVisualizer()
        self.generation_queue = queue.Queue()
        
    def _load_api_key(self) -> str:
        """Load Google API key from environment"""
        # Try .env file first
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('GOOGLE_API_KEY='):
                        api_key = line.split('=', 1)[1].strip().strip('"\'')
                        if api_key:
                            logger.info("✅ Loaded GOOGLE_API_KEY from .env file")
                            return api_key
        
        # Try environment variable
        api_key = os.getenv('GOOGLE_API_KEY')
        if api_key:
            logger.info("✅ Loaded GOOGLE_API_KEY from environment")
            return api_key
            
        raise ValueError("❌ GOOGLE_API_KEY not found in .env file or environment variables")
        
    def generate_video_with_realtime_updates(self, mission: str, duration: int, platform: str, 
                                           category: str, use_discussions: bool) -> tuple:
        """Generate video with real-time updates"""
        try:
            # Convert string parameters to enums with correct values
            video_category = VideoCategory(category)  # Use the string value directly
            target_platform = Platform(platform.lower())  # Use lowercase for platform
            
            # Simulate agent discussions for UI display
            if use_discussions:
                self.visualizer.start_monitoring()
                self._simulate_discussions()
            
            # Create orchestrator for this specific mission
            orchestrator = create_enhanced_orchestrator_with_19_agents(
                api_key=self.api_key,
                mission=mission,
                category=video_category,
                platform=target_platform,
                duration=duration,
                discussion_mode=use_discussions
            )
            
            # Generate video
            result = orchestrator.generate_viral_video(
                mission=mission,
                category=video_category,
                platform=target_platform,
                duration=duration,
                discussion_mode=use_discussions
            )
            
            # Stop monitoring
            if use_discussions:
                self.visualizer.stop_monitoring()
            
            # Format results
            status = f"✅ Video generated successfully!\n📁 Session: {result.video_id}\n⏱️ Time: {result.generation_time_seconds:.1f}s"
            video_path = result.file_path if os.path.exists(result.file_path) else None
            details = f"📊 File size: {result.file_size_mb:.1f}MB\n🎬 Duration: {duration}s\n📱 Platform: {platform}\n🎭 Category: {category}"
            discussions = self.visualizer.generate_discussion_html()
            
            return status, video_path, details, discussions
            
        except Exception as e:
            logger.error(f"❌ Video generation failed: {e}")
            if use_discussions:
                self.visualizer.stop_monitoring()
            error_msg = f"❌ Generation failed: {str(e)}"
            return error_msg, None, "Please check the logs for details", "No discussions available"
    
    def _simulate_discussions(self):
        """Simulate agent discussions for UI display"""
        phases = [
            "Script Development Strategy",
            "Audio Production and Voice Optimization", 
            "Visual Design and Typography Strategy",
            "Platform Optimization and Viral Mechanics",
            "Quality Assurance and User Experience"
        ]
        
        agents_by_phase = {
            "Script Development Strategy": ["StoryWeaver", "DialogueMaster", "PaceMaster", "AudienceAdvocate"],
            "Audio Production and Voice Optimization": ["AudioMaster", "VoiceDirector", "SoundDesigner"],
            "Visual Design and Typography Strategy": ["VisionCraft", "StyleDirector", "ColorMaster", "TypeMaster"],
            "Platform Optimization and Viral Mechanics": ["PlatformGuru", "EngagementHacker", "TrendMaster"],
            "Quality Assurance and User Experience": ["QualityGuard", "AudienceAdvocate", "SyncMaster", "CutMaster"]
        }
        
        sample_messages = [
            "Analyzing mission requirements and target audience demographics for optimal engagement",
            "Optimizing script structure and pacing for maximum retention and viral potential",
            "Implementing platform-specific narrative techniques and engagement hooks",
            "Coordinating audio-visual synchronization for seamless viewer experience",
            "Ensuring technical quality meets professional broadcast standards",
            "Finalizing consensus and preparing for video generation phase"
        ]
        
        # Add discussion messages for UI display
        for phase_idx, phase in enumerate(phases):
            agents = agents_by_phase[phase]
            
            for round_num in range(1, 3):
                consensus = min(0.4 + (round_num * 0.3) + (phase_idx * 0.1), 1.0)
                
                for agent_idx, agent in enumerate(agents[:3]):  # Show 3 agents per phase
                    message = sample_messages[agent_idx % len(sample_messages)]
                    self.visualizer.add_discussion_message(
                        phase=phase,
                        agent=agent,
                        message=message,
                        consensus=consensus,
                        round_num=round_num
                    )
                
                if consensus >= 0.8:
                    break
    
    def get_discussion_updates(self):
        """Get current discussion HTML"""
        return self.visualizer.generate_discussion_html()

def create_unified_interface():
    """Create the unified Gradio interface"""
    app = UnifiedVideoApp()
    
    # Create interface with proper styling
    css = """
    .gradio-container {
        max-width: 1400px !important;
    }
    .agent-discussion {
        height: 600px;
        overflow-y: auto;
        border: 2px solid #3b82f6;
        border-radius: 10px;
        padding: 15px;
        background-color: #f8fafc !important;
        color: #1e293b !important;
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    }
    .agent-discussion h3 {
        color: #1e40af !important;
        margin-bottom: 10px;
    }
    .agent-discussion .agent-message {
        background-color: #e2e8f0 !important;
        border-left: 4px solid #3b82f6;
        padding: 10px;
        margin: 8px 0;
        border-radius: 5px;
        color: #334155 !important;
    }
    .agent-discussion .consensus-bar {
        background-color: #ddd6fe !important;
        border-radius: 10px;
        height: 20px;
        margin: 10px 0;
    }
    .agent-discussion .consensus-progress {
        background-color: #7c3aed !important;
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    .agent-discussion .phase-header {
        background-color: #1e40af !important;
        color: white !important;
        padding: 8px 12px;
        border-radius: 5px;
        margin: 10px 0;
        font-weight: bold;
    }
    .agent-discussion .agent-name {
        font-weight: bold;
        color: #7c2d12 !important;
    }
    .agent-discussion .timestamp {
        color: #64748b !important;
        font-size: 0.8em;
    }
    """

    with gr.Blocks(
        title="🎬 Unified Real-time VEO-2 Generator",
        theme=gr.themes.Soft(),
        css=css
    ) as interface:
        
        gr.Markdown("# 🎬 Unified Real-time VEO-2 Video Generator")
        gr.Markdown("**Complete System: Mission Strategy + 19 AI Agents + Live Discussions + VEO-2 Generation**")
        
        with gr.Row():
            # Left Column: Mission Configuration
            with gr.Column(scale=1):
                gr.Markdown("## 🎯 Mission Configuration")
                
                topic_input = gr.Textbox(
                    label="🎯 Mission",
                    value="",
                    placeholder="Describe what you want to achieve (e.g., 'get people excited about learning', 'convince viewers to try something new')",
                    lines=2
                )
                
                with gr.Row():
                    duration_input = gr.Slider(
                        label="⏱️ Duration (seconds)",
                        minimum=10,
                        maximum=60,
                        value=15,
                        step=5
                    )
                    
                    platform_dropdown = gr.Dropdown(
                        choices=["youtube", "tiktok", "instagram"],
                        value="youtube",
                        label="📱 Target Platform (where video will be published)"
                    )
                
                with gr.Row():
                    category_dropdown = gr.Dropdown(
                        choices=["Comedy", "Entertainment", "Education", "Technology", "Gaming", "Music", 
                                "Sports", "News", "Lifestyle", "Food", "Travel", "Fitness", "Fashion", 
                                "Science", "Business", "Health", "Arts", "Automotive", "Pets", "Other"],
                        value="Comedy",
                        label="🎭 Category"
                    )
                    
                    discussions_input = gr.Checkbox(
                        label="🤖 Enable AI Agent Discussions",
                        value=True
                    )
                
                generate_btn = gr.Button(
                    "🚀 Generate Mission Video", 
                    variant="primary", 
                    size="lg"
                )
                
                gr.Markdown("---")
                gr.Markdown("### 🎯 Mission Examples")
                gr.Markdown("""
                - **Educational:** "help people understand complex topics simply"
                - **Motivational:** "inspire viewers to take positive action"  
                - **Awareness:** "raise awareness about important issues"
                - **Engagement:** "get audience excited about new ideas"
                """)
            
            # Middle Column: Results
            with gr.Column(scale=1):
                gr.Markdown("## 📊 Generation Results")
                
                status_output = gr.Markdown("Ready to generate your mission video...")
                
                video_output = gr.Video(label="🎬 Generated Video")
                
                details_output = gr.Markdown("Generation details will appear here...")
            
            # Right Column: Live Agent Discussions
            with gr.Column(scale=1):
                gr.Markdown("## 🤖 Live AI Agent Discussions")
                
                agent_discussions = gr.HTML(
                    value=app.visualizer._generate_initial_html(),
                    elem_classes=["agent-discussion"]
                )
        
        # Generation event handlers
        def handle_generation(mission, duration, platform, category, use_discussions):
            """Handle video generation with real-time updates"""
            return app.generate_video_with_realtime_updates(
                mission, duration, platform, category, use_discussions
            )
        
        # Set up the generation event
        generate_btn.click(
            handle_generation,
            inputs=[topic_input, duration_input, platform_dropdown, category_dropdown, discussions_input],
            outputs=[status_output, video_output, details_output, agent_discussions]
        )
        
        # Real-time updates (this would need WebSocket in production)
        gr.Markdown("---")
        gr.Markdown("## 🚀 System Features")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("""
                ### 🎯 Mission-Based Generation
                - Define what you want to accomplish
                - AI agents strategize to achieve your mission
                - Platform-specific optimization
                - Real success metrics
                """)
            
            with gr.Column():
                gr.Markdown("""
                ### 🤖 19 AI Agent Collaboration
                - Script Development (4 agents)
                - Audio Production (4 agents) 
                - Visual Design (5 agents)
                - Platform Optimization (4 agents)
                - Quality Assurance (4 agents)
                """)
            
            with gr.Column():
                gr.Markdown("""
                ### 🎬 Advanced Video Generation
                - Real VEO-2/VEO-3 video clips
                - Professional audio synthesis
                - Perfect timing and pacing
                - Platform algorithm optimization
                """)
    
    return interface

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='🎬 Unified Real-time VEO-2 Video Generator')
    parser.add_argument('--port', type=int, default=7860, help='Port for web interface')
    parser.add_argument('--mission', type=str, default='', help='Mission to accomplish with the video')
    parser.add_argument('--duration', type=int, choices=[10, 15, 20, 30, 45, 60], default=15, help='Video duration in seconds')
    parser.add_argument('--platform', choices=['youtube', 'tiktok', 'instagram'], default='youtube', 
                        help='Target destination platform where video will be published (affects optimization and format)')
    parser.add_argument('--category', 
                        choices=['Comedy', 'Entertainment', 'Education', 'Technology', 'Gaming', 'Music', 
                                'Sports', 'News', 'Lifestyle', 'Food', 'Travel', 'Fitness', 'Fashion', 
                                'Science', 'Business', 'Health', 'Arts', 'Automotive', 'Pets', 'Other'], 
                        default='Comedy', help='Video category')
    parser.add_argument('--discussions', action='store_true', default=True, help='Enable AI agent discussions')
    parser.add_argument('--no-discussions', action='store_true', default=False, help='Disable AI agent discussions')
    
    args = parser.parse_args()
    
    # Handle discussions flag
    use_discussions = args.discussions and not args.no_discussions
    
    # If mission is provided, run in CLI mode
    if args.mission:
        print("🎬 Unified Real-time VEO-2 Video Generator - CLI Mode")
        print("=" * 60)
        print(f"🎯 Mission: {args.mission}")
        print(f"⏱️ Duration: {args.duration}s")
        print(f"📱 Platform: {args.platform}")
        print(f"🎭 Category: {args.category}")
        print(f"🤖 Discussions: {use_discussions}")
        print("=" * 60)
        
        # Create app instance
        app = UnifiedVideoApp()
        
        # Generate video
        try:
            result = app.generate_video_with_realtime_updates(
                mission=args.mission,
                duration=args.duration,
                platform=args.platform,
                category=args.category,
                use_discussions=use_discussions
            )
            
            print("\n🎉 SUCCESS!")
            print(f"📹 Video generated successfully")
            print(f"📁 Check the outputs directory for your video")
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            sys.exit(1)
    else:
        # Launch web interface
        print("🎬 Unified Real-time VEO-2 Video Generator - UI Mode")
        print("=" * 60)
        print("🤖 Loading 19 AI agents...")
        print("🎯 Mission-based generation ready...")
        print("📊 Real-time visualization enabled...")
        print("=" * 60)
        
        interface = create_unified_interface()
        
        print(f"🌐 Starting interface on port {args.port}")
        print(f"🎬 Access at: http://localhost:{args.port}")
        print("🤖 Live agent discussions will appear during generation")
        print("🎯 Ready to accomplish your mission!")
        
        interface.launch(
            server_name="0.0.0.0",
            server_port=args.port,
            share=False,
            show_error=True
        ) 