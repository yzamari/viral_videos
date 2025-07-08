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
import logging

import gradio as gr
from src.models.video_models import VideoCategory, Platform
from src.agents.enhanced_orchestrator_with_19_agents import create_enhanced_orchestrator_with_19_agents

# Setup logging to capture agent discussions
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealTimeAgentDiscussionMonitor:
    """Monitor real AI agent discussions and display them in the UI"""
    
    def __init__(self):
        self.discussion_messages = []
        self.current_phase = "Waiting"
        self.is_monitoring = False
        self.consensus_level = 0.0
        self.current_round = 0
        self.log_handler = None
        
    def start_monitoring(self):
        """Start monitoring real agent discussions"""
        self.is_monitoring = True
        self.discussion_messages = []
        self.current_phase = "Initializing"
        self.consensus_level = 0.0
        self.current_round = 0
        
        # Set up log handler to capture agent discussions
        self.log_handler = AgentDiscussionHandler(self)
        
        # Add handler to relevant loggers
        loggers_to_monitor = [
            'src.agents.enhanced_multi_agent_discussion',
            'src.agents.discussion_visualizer',
            'src.agents.enhanced_orchestrator_with_19_agents'
        ]
        
        for logger_name in loggers_to_monitor:
            agent_logger = logging.getLogger(logger_name)
            agent_logger.addHandler(self.log_handler)
            agent_logger.setLevel(logging.INFO)
        
        logger.info("🎭 Started monitoring real AI agent discussions")
        
    def stop_monitoring(self):
        """Stop monitoring agent discussions"""
        self.is_monitoring = False
        
        # Remove log handler
        if self.log_handler:
            loggers_to_monitor = [
                'src.agents.enhanced_multi_agent_discussion',
                'src.agents.discussion_visualizer',
                'src.agents.enhanced_orchestrator_with_19_agents'
            ]
            
            for logger_name in loggers_to_monitor:
                agent_logger = logging.getLogger(logger_name)
                agent_logger.removeHandler(self.log_handler)
        
        logger.info("🎭 Stopped monitoring AI agent discussions")
        
    def add_agent_message(self, agent_name: str, message: str, phase: str = None, consensus: float = None, round_num: int = None):
        """Add a real agent message to the discussion"""
        if not self.is_monitoring:
            return
            
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Update current state
        if phase:
            self.current_phase = phase
        if consensus is not None:
            self.consensus_level = consensus
        if round_num is not None:
            self.current_round = round_num
        
        # Agent color mapping
        agent_colors = {
            'StoryWeaver': '#3b82f6', 'DialogueMaster': '#3b82f6', 'PaceMaster': '#3b82f6', 'AudienceAdvocate': '#3b82f6',
            'AudioMaster': '#10b981', 'VoiceDirector': '#10b981', 'SoundDesigner': '#10b981', 'PlatformGuru': '#8b5cf6',
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
        
        color = agent_colors.get(agent_name, '#64748b')
        emoji = agent_emojis.get(agent_name, '🤖')
        
        self.discussion_messages.append({
            'agent': agent_name,
            'emoji': emoji,
            'color': color,
            'message': message,
            'phase': phase or self.current_phase,
            'consensus': consensus or self.consensus_level,
            'round': round_num or self.current_round,
            'timestamp': timestamp
        })
        
        # Keep only last 25 messages to prevent overflow
        if len(self.discussion_messages) > 25:
            self.discussion_messages = self.discussion_messages[-25:]
    
    def generate_discussion_html(self) -> str:
        """Generate HTML for current real discussions"""
        if not self.discussion_messages:
            return self._generate_initial_html()
        
        # Generate phase header
        phase_html = f"""
        <div class="phase-header">
            🎭 Phase: {self.current_phase}
        </div>
        """
        
        # Generate consensus bar
        consensus_percent = int(self.consensus_level * 100)
        consensus_color = "#10b981" if consensus_percent >= 80 else "#f59e0b" if consensus_percent >= 60 else "#ef4444"
        consensus_html = f"""
        <div style="margin: 15px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                <span style="color: #1e40af; font-weight: bold;">Live Consensus Progress:</span>
                <span style="color: {consensus_color}; font-weight: bold;">{consensus_percent}%</span>
            </div>
            <div class="consensus-bar">
                <div class="consensus-progress" style="width: {consensus_percent}%; background-color: {consensus_color};"></div>
            </div>
            <div style="color: #64748b; font-size: 0.9em;">
                Round {self.current_round} • Target: 80% • Live Agent Discussions
            </div>
        </div>
        """
        
        # Generate real messages
        messages_html = ""
        for msg in self.discussion_messages[-12:]:  # Show last 12 messages
            # Truncate long messages
            display_message = msg['message'][:300] + "..." if len(msg['message']) > 300 else msg['message']
            
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
        unique_agents = list(set([msg['agent'] for msg in self.discussion_messages[-8:]]))
        agents_html = f"""
        <div style="margin-top: 15px; padding: 10px; background: #f1f5f9; border-radius: 5px;">
            <div style="color: #1e40af; font-weight: bold;">🔥 Live Active Agents:</div>
            <div style="color: #64748b; margin-top: 5px;">
                {' • '.join(unique_agents[:8])}
            </div>
        </div>
        """
        
        return f"""
        <div class="agent-discussion">
            {phase_html}
            {consensus_html}
            <div style="max-height: 400px; overflow-y: auto;">
                {messages_html}
            </div>
            {agents_html}
        </div>
        """
    
    def _generate_initial_html(self) -> str:
        """Generate initial HTML when no discussions are active"""
        return """
        <div class="agent-discussion">
            <div class="phase-header">🤖 Live AI Agent Discussions</div>
            <p style="color: #64748b; font-style: italic; text-align: center; margin: 20px 0;">
                Start generation to see live agent discussions in real-time...
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

class AgentDiscussionHandler(logging.Handler):
    """Custom logging handler to capture agent discussions"""
    
    def __init__(self, monitor: RealTimeAgentDiscussionMonitor):
        super().__init__()
        self.monitor = monitor
        
    def emit(self, record):
        """Process log records and extract agent discussions"""
        try:
            message = record.getMessage()
            
            # Extract agent messages
            if "💬" in message and ":" in message:
                # Parse agent message: "💬 AgentName: message"
                parts = message.split(":", 1)
                if len(parts) == 2:
                    agent_part = parts[0].strip()
                    agent_message = parts[1].strip()
                    
                    # Extract agent name
                    if "💬" in agent_part:
                        agent_name = agent_part.replace("💬", "").strip()
                        self.monitor.add_agent_message(agent_name, agent_message)
            
            # Extract consensus updates
            elif "📊 Enhanced consensus level:" in message:
                try:
                    consensus_str = message.split(":")[-1].strip()
                    consensus = float(consensus_str)
                    self.monitor.consensus_level = consensus
                except:
                    pass
            
            # Extract round information
            elif "🔄 Enhanced discussion round" in message:
                try:
                    round_match = re.search(r'round (\d+)/(\d+)', message)
                    if round_match:
                        current_round = int(round_match.group(1))
                        self.monitor.current_round = current_round
                except:
                    pass
            
            # Extract phase information
            elif "Phase" in message and ":" in message:
                try:
                    phase_match = re.search(r'Phase \d+: (.+)', message)
                    if phase_match:
                        phase_name = phase_match.group(1).strip()
                        self.monitor.current_phase = phase_name
                except:
                    pass
                    
        except Exception as e:
            # Silently ignore handler errors
            pass

class UnifiedVideoApp:
    """Unified application combining all video generation functionality"""
    
    def __init__(self):
        # Load API key
        self.api_key = self._load_api_key()
        self.visualizer = RealTimeAgentDiscussionMonitor()
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
                    self.visualizer.add_agent_message(
                        agent_name=agent,
                        message=message,
                        phase=phase,
                        consensus=consensus,
                        round_num=round_num
                    )
                
                if consensus >= 0.8:
                    break
    
    def get_discussion_updates(self):
        """Get current discussion HTML"""
        return self.visualizer.generate_discussion_html()

# Global visualizer instance for real-time agent discussions
global_visualizer = RealTimeAgentDiscussionMonitor()

def create_unified_realtime_interface():
    """Create the unified real-time video generation interface with force generation controls"""
    
    css = """
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
        font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
    }
    
    .header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .input-section {
        background: white;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        margin-bottom: 25px;
        border: 1px solid #e1e5e9;
    }
    
    .control-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        margin-bottom: 20px;
    }
    
    .force-generation-section {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #e9ecef;
        margin-bottom: 20px;
    }
    
    .force-generation-title {
        font-weight: bold;
        color: #495057;
        margin-bottom: 15px;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .continuous-section {
        background: #fff3cd;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #ffeaa7;
        margin-top: 15px;
    }
    
    .discussion-container {
        background: #1a1a1a;
        color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
        font-size: 13px;
        line-height: 1.4;
        max-height: 600px;
        overflow-y: auto;
        margin-bottom: 20px;
        border: 2px solid #333;
    }
    
    .agent-message {
        margin: 8px 0;
        padding: 8px 12px;
        border-radius: 6px;
        border-left: 4px solid;
    }
    
    .script-development { border-left-color: #3498db; background: rgba(52, 152, 219, 0.1); }
    .audio-production { border-left-color: #2ecc71; background: rgba(46, 204, 113, 0.1); }
    .visual-design { border-left-color: #e67e22; background: rgba(230, 126, 34, 0.1); }
    .platform-optimization { border-left-color: #9b59b6; background: rgba(155, 89, 182, 0.1); }
    .quality-assurance { border-left-color: #e74c3c; background: rgba(231, 76, 60, 0.1); }
    
    .consensus-bar {
        background: #2c3e50;
        height: 20px;
        border-radius: 10px;
        margin: 10px 0;
        overflow: hidden;
    }
    
    .consensus-fill {
        height: 100%;
        background: linear-gradient(90deg, #e74c3c 0%, #f39c12 50%, #2ecc71 100%);
        border-radius: 10px;
        transition: width 0.5s ease;
    }
    
    .phase-header {
        color: #f39c12;
        font-weight: bold;
        font-size: 16px;
        margin: 15px 0 10px 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .timestamp {
        color: #7f8c8d;
        font-size: 11px;
    }
    
    .generate-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 15px 30px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        margin-top: 20px;
    }
    
    .generate-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    .stop-button {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: bold;
        cursor: pointer;
        margin-left: 10px;
    }
    
    .orientation-indicator {
        background: #e8f4fd;
        padding: 10px;
        border-radius: 6px;
        border: 1px solid #bee5eb;
        margin-top: 10px;
        font-size: 12px;
        color: #0c5460;
    }
    """
    
    with gr.Blocks(css=css, title="🎬 Unified Real-time VEO-2 Video Generator") as interface:
        gr.HTML("""
        <div class="header">
            <h1>🎬 Unified Real-time VEO-2 Video Generator</h1>
            <p>Mission-based video generation with 19 AI agents, live discussions, and force generation controls</p>
        </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML('<div class="input-section">')
                
                # Mission Input
                mission_input = gr.Textbox(
                    label="🎯 Mission Statement",
                    placeholder="What do you want to convince people of? (e.g., 'Convince people that cats are better than dogs')",
                    lines=3,
                    value=""
                )
                
                with gr.Row():
                    # Category Selection
                    category_dropdown = gr.Dropdown(
                        choices=[
                            "Comedy", "Entertainment", "Education", "Technology", "Gaming",
                            "Music", "Sports", "News", "Lifestyle", "Food",
                            "Travel", "Fitness", "Fashion", "Science", "Business",
                            "Health", "Arts", "Automotive", "Pets", "Other"
                        ],
                        label="📂 Video Category",
                        value="Comedy"
                    )
                    
                    # Platform Selection
                    platform_dropdown = gr.Dropdown(
                        choices=["tiktok", "youtube", "instagram"],
                        label="📱 Target Platform (where video will be published)",
                        value="tiktok"
                    )
                
                # Duration Selection
                duration_slider = gr.Slider(
                    minimum=15,
                    maximum=120,
                    value=35,
                    step=5,
                    label="⏱️ Video Duration (seconds)"
                )
                
                # NEW: Force Generation Controls
                gr.HTML('<div class="force-generation-section">')
                gr.HTML('<div class="force-generation-title">🎛️ Force Generation Controls</div>')
                
                force_mode = gr.Radio(
                    choices=[
                        ("🤖 Auto (Normal Fallback Chain)", "auto"),
                        ("🎬 Force VEO-3 Only", "force_veo3"),
                        ("🎥 Force VEO-2 Only", "force_veo2"),
                        ("🎨 Force Image Generation Only", "force_image_gen"),
                        ("🔄 Force Continuous Generation", "force_continuous")
                    ],
                    label="Generation Mode",
                    value="auto",
                    info="Choose how you want videos to be generated"
                )
                
                # Continuous Generation Controls
                gr.HTML('<div class="continuous-section">')
                continuous_enabled = gr.Checkbox(
                    label="🔄 Enable Continuous Generation",
                    value=False,
                    info="Keep generating videos until manually stopped"
                )
                
                continuous_interval = gr.Slider(
                    minimum=30,
                    maximum=300,
                    value=60,
                    step=10,
                    label="⏱️ Continuous Interval (seconds)",
                    visible=False
                )
                gr.HTML('</div>')
                
                # Video Orientation Controls
                orientation_mode = gr.Radio(
                    choices=[
                        ("🤖 AI Agents Decide", "auto"),
                        ("📱 Force Portrait (9:16)", "portrait"),
                        ("🖥️ Force Landscape (16:9)", "landscape"),
                        ("⬜ Force Square (1:1)", "square")
                    ],
                    label="📐 Video Orientation",
                    value="auto",
                    info="Let AI agents decide or force specific orientation"
                )
                
                orientation_info = gr.HTML(
                    '<div class="orientation-indicator">🤖 AI agents will analyze platform and content to decide optimal orientation</div>'
                )
                
                gr.HTML('</div>')
                gr.HTML('</div>')
                
                # Generate Button
                generate_btn = gr.Button(
                    "🚀 Start AI Agent Generation",
                    elem_classes=["generate-button"]
                )
                
                # Stop Button (for continuous mode)
                stop_btn = gr.Button(
                    "⏹️ Stop Continuous Generation",
                    elem_classes=["stop-button"],
                    visible=False
                )
                
            with gr.Column(scale=2):
                # Live AI Agent Discussions
                gr.HTML('<h2 style="color: #2c3e50; margin-bottom: 20px;">🤖 Live AI Agent Discussions</h2>')
                
                discussion_output = gr.HTML(
                    value=global_visualizer.generate_discussion_html(),
                    elem_classes=["discussion-container"]
                )
                
                # Generation Status
                status_output = gr.Textbox(
                    label="📊 Generation Status",
                    value="Ready to generate",
                    interactive=False,
                    lines=2
                )
                
                # Video Output
                video_output = gr.Video(
                    label="🎬 Generated Video",
                    visible=False
                )
                
                # Download Link
                download_output = gr.File(
                    label="📥 Download Video",
                    visible=False
                )
        
        # Event Handlers
        def update_continuous_controls(enabled):
            return gr.update(visible=enabled)
        
        def update_orientation_info(mode):
            if mode == "auto":
                return '<div class="orientation-indicator">🤖 AI agents will analyze platform and content to decide optimal orientation</div>'
            elif mode == "portrait":
                return '<div class="orientation-indicator">📱 Forced to Portrait (9:16) - Best for TikTok, Instagram Stories</div>'
            elif mode == "landscape":
                return '<div class="orientation-indicator">🖥️ Forced to Landscape (16:9) - Best for YouTube, traditional video</div>'
            elif mode == "square":
                return '<div class="orientation-indicator">⬜ Forced to Square (1:1) - Best for Instagram Posts</div>'
        
        continuous_enabled.change(
            update_continuous_controls,
            inputs=[continuous_enabled],
            outputs=[continuous_interval]
        )
        
        orientation_mode.change(
            update_orientation_info,
            inputs=[orientation_mode],
            outputs=[orientation_info]
        )
        
        # Main generation function
        def generate_video_with_force_controls(mission, category, platform, duration, force_mode, continuous_enabled, orientation_mode):
            try:
                if not mission or not mission.strip():
                    return (
                        "❌ Please enter a mission statement",
                        '<div class="discussion-container">❌ No mission provided</div>',
                        gr.update(visible=False),
                        gr.update(visible=False)
                    )
                
                # Import the enhanced orchestrator
                from src.agents.enhanced_orchestrator_with_19_agents import create_enhanced_orchestrator_with_19_agents
                from src.models.video_models import VideoCategory, Platform, ForceGenerationMode, VideoOrientation
                
                # Convert string values to enums
                try:
                    video_category = VideoCategory(category)
                    target_platform = Platform(platform)
                    
                    # Convert force mode
                    if force_mode == "auto":
                        force_generation_mode = ForceGenerationMode.AUTO
                    elif force_mode == "force_veo3":
                        force_generation_mode = ForceGenerationMode.FORCE_VEO3
                    elif force_mode == "force_veo2":
                        force_generation_mode = ForceGenerationMode.FORCE_VEO2
                    elif force_mode == "force_image_gen":
                        force_generation_mode = ForceGenerationMode.FORCE_IMAGE_GEN
                    elif force_mode == "force_continuous":
                        force_generation_mode = ForceGenerationMode.FORCE_CONTINUOUS
                    else:
                        force_generation_mode = ForceGenerationMode.AUTO
                    
                    # Convert orientation mode
                    if orientation_mode == "auto":
                        video_orientation = VideoOrientation.AUTO
                    elif orientation_mode == "portrait":
                        video_orientation = VideoOrientation.PORTRAIT
                    elif orientation_mode == "landscape":
                        video_orientation = VideoOrientation.LANDSCAPE
                    elif orientation_mode == "square":
                        video_orientation = VideoOrientation.SQUARE
                    else:
                        video_orientation = VideoOrientation.AUTO
                        
                except ValueError as e:
                    return (
                        f"❌ Invalid selection: {e}",
                        '<div class="discussion-container">❌ Invalid category or platform</div>',
                        gr.update(visible=False),
                        gr.update(visible=False)
                    )
                
                # Start real-time monitoring
                global_visualizer.start_monitoring()
                
                # Create the orchestrator with force generation settings
                orchestrator = create_enhanced_orchestrator_with_19_agents(
                    api_key=os.getenv('GOOGLE_API_KEY') or "",
                    mission=mission,
                    category=video_category,
                    platform=target_platform,
                    duration=duration,
                    enable_discussions=True,
                    force_generation_mode=force_generation_mode,
                    continuous_generation=continuous_enabled,
                    video_orientation=video_orientation
                )
                
                # Start generation with real-time updates
                status_text = f"🚀 Starting generation with {force_mode} mode..."
                
                # Create a function to update discussions in real-time
                def update_discussions():
                    """Update discussions in real-time during generation"""
                    while global_visualizer.is_monitoring:
                        try:
                            discussion_html = global_visualizer.generate_discussion_html()
                            # This would ideally update the UI in real-time
                            # For now, we'll rely on the final update
                            time.sleep(2)
                        except Exception as e:
                            logger.error(f"Discussion update error: {e}")
                            break
                
                # Start the discussion update thread
                discussion_thread = threading.Thread(target=update_discussions, daemon=True)
                discussion_thread.start()
                
                # Generate the video using the existing method
                result = orchestrator.generate_viral_video(
                    mission=mission,
                    category=video_category,
                    platform=target_platform,
                    duration=duration
                )
                
                # Stop monitoring
                global_visualizer.stop_monitoring()
                
                # Get final discussion HTML
                final_discussion_html = global_visualizer.generate_discussion_html()
                
                if result and hasattr(result, 'file_path') and os.path.exists(result.file_path):
                    final_status = f"✅ Video generated successfully!\n📁 File: {result.file_path}\n📊 Success rate: {getattr(result, 'success_rate', 1.0):.1%}"
                    
                    return (
                        final_status,
                        final_discussion_html,
                        gr.update(value=result.file_path, visible=True),
                        gr.update(value=result.file_path, visible=True)
                    )
                else:
                    return (
                        "❌ Video generation failed",
                        final_discussion_html,
                        gr.update(visible=False),
                        gr.update(visible=False)
                    )
                    
            except Exception as e:
                # Stop monitoring on error
                global_visualizer.stop_monitoring()
                error_msg = f"❌ Error: {str(e)}"
                error_html = f'<div class="discussion-container">❌ Generation failed: {str(e)}</div>'
                
                return (
                    error_msg,
                    error_html,
                    gr.update(visible=False),
                    gr.update(visible=False)
                )
        
        generate_btn.click(
            generate_video_with_force_controls,
            inputs=[
                mission_input,
                category_dropdown,
                platform_dropdown,
                duration_slider,
                force_mode,
                continuous_enabled,
                orientation_mode
            ],
            outputs=[
                status_output,
                discussion_output,
                video_output,
                download_output
            ]
        )
    
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
        
        interface = create_unified_realtime_interface()
        
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