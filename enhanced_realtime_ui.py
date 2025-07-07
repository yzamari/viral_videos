#!/usr/bin/env python3
"""
Enhanced Real-Time UI for Viral Video Generator
Features:
- Real-time AI agent conversation visualization
- Colorful status updates and progress tracking
- Live generation process monitoring
- Interactive agent discussion panels
"""

import gradio as gr
import os
import sys
import json
import time
import threading
import asyncio
import queue
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import logging
from dataclasses import dataclass
import uuid

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.workflows.generate_viral_video import generate_viral_video
from src.agents.enhanced_orchestrator_with_discussions import EnhancedOrchestratorWithDiscussions
from src.agents.discussion_visualizer import DiscussionVisualizer
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class AgentStatus:
    """Agent status information"""
    name: str
    status: str  # idle, active, speaking, completed
    current_task: str
    messages_count: int
    last_activity: datetime
    color: str
    emoji: str

@dataclass
class GenerationPhase:
    """Generation phase information"""
    name: str
    status: str  # pending, active, completed, error
    progress: float
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    agents: List[str]
    messages: List[Dict]

class EnhancedRealtimeUI:
    """Enhanced real-time UI with comprehensive visualization"""
    
    def __init__(self):
        self.session_id = str(uuid.uuid4())[:8]
        self.generation_active = False
        self.current_phase = None
        
        # Agent configurations
        self.agents = {
            "TrendMaster": AgentStatus("TrendMaster", "idle", "", 0, datetime.now(), "#ff6b6b", "🔥"),
            "StoryWeaver": AgentStatus("StoryWeaver", "idle", "", 0, datetime.now(), "#4ecdc4", "📖"),
            "VisionCraft": AgentStatus("VisionCraft", "idle", "", 0, datetime.now(), "#45b7d1", "🎨"),
            "PixelForge": AgentStatus("PixelForge", "idle", "", 0, datetime.now(), "#6c5ce7", "⚡"),
            "AudioMaster": AgentStatus("AudioMaster", "idle", "", 0, datetime.now(), "#f9ca24", "🎵"),
            "CutMaster": AgentStatus("CutMaster", "idle", "", 0, datetime.now(), "#f0932b", "✂️"),
            "SyncMaster": AgentStatus("SyncMaster", "idle", "", 0, datetime.now(), "#eb4d4b", "🎯"),
            "DialogueMaster": AgentStatus("DialogueMaster", "idle", "", 0, datetime.now(), "#00d2d3", "💬"),
            "PaceMaster": AgentStatus("PaceMaster", "idle", "", 0, datetime.now(), "#ff9ff3", "⚡"),
            "VoiceDirector": AgentStatus("VoiceDirector", "idle", "", 0, datetime.now(), "#54a0ff", "🎭"),
            "SoundDesigner": AgentStatus("SoundDesigner", "idle", "", 0, datetime.now(), "#5f27cd", "🔊"),
            "TypeMaster": AgentStatus("TypeMaster", "idle", "", 0, datetime.now(), "#00d2d3", "📝"),
            "HeaderCraft": AgentStatus("HeaderCraft", "idle", "", 0, datetime.now(), "#ff6348", "📋"),
            "StyleDirector": AgentStatus("StyleDirector", "idle", "", 0, datetime.now(), "#2ed573", "🎬"),
            "ColorMaster": AgentStatus("ColorMaster", "idle", "", 0, datetime.now(), "#ffa502", "🌈"),
            "PlatformGuru": AgentStatus("PlatformGuru", "idle", "", 0, datetime.now(), "#3742fa", "📱"),
            "EngagementHacker": AgentStatus("EngagementHacker", "idle", "", 0, datetime.now(), "#2f3542", "💡"),
            "QualityGuard": AgentStatus("QualityGuard", "idle", "", 0, datetime.now(), "#ff4757", "🛡️"),
            "AudienceAdvocate": AgentStatus("AudienceAdvocate", "idle", "", 0, datetime.now(), "#5352ed", "👥")
        }
        
        # Generation phases
        self.phases = {
            "script_development": GenerationPhase("Script Development", "pending", 0.0, None, None, 
                                                ["StoryWeaver", "DialogueMaster", "PaceMaster", "AudienceAdvocate"], []),
            "audio_production": GenerationPhase("Audio Production", "pending", 0.0, None, None,
                                              ["AudioMaster", "VoiceDirector", "SoundDesigner", "PlatformGuru"], []),
            "visual_design": GenerationPhase("Visual Design", "pending", 0.0, None, None,
                                           ["VisionCraft", "StyleDirector", "ColorMaster", "TypeMaster", "HeaderCraft"], []),
            "platform_optimization": GenerationPhase("Platform Optimization", "pending", 0.0, None, None,
                                                    ["PlatformGuru", "EngagementHacker", "TrendMaster", "QualityGuard"], []),
            "quality_review": GenerationPhase("Quality Review", "pending", 0.0, None, None,
                                            ["QualityGuard", "AudienceAdvocate", "SyncMaster", "CutMaster"], [])
        }
        
        # Message queues
        self.message_queue = queue.Queue()
        self.status_queue = queue.Queue()
        
        # UI state
        self.ui_state = {
            "total_progress": 0.0,
            "current_phase": "idle",
            "generation_start": None,
            "estimated_completion": None,
            "messages": [],
            "errors": []
        }
    
    def update_agent_status(self, agent_name: str, status: str, task: str = ""):
        """Update agent status"""
        if agent_name in self.agents:
            agent = self.agents[agent_name]
            agent.status = status
            agent.current_task = task
            agent.last_activity = datetime.now()
            if status == "speaking":
                agent.messages_count += 1
    
    def add_agent_message(self, agent_name: str, message: str, message_type: str = "discussion"):
        """Add agent message"""
        timestamp = datetime.now()
        message_data = {
            "timestamp": timestamp,
            "agent": agent_name,
            "message": message,
            "type": message_type,
            "id": str(uuid.uuid4())[:8]
        }
        
        self.message_queue.put(message_data)
        self.ui_state["messages"].append(message_data)
        
        # Update agent status
        self.update_agent_status(agent_name, "speaking", "Contributing to discussion")
    
    def start_phase(self, phase_name: str):
        """Start a generation phase"""
        if phase_name in self.phases:
            phase = self.phases[phase_name]
            phase.status = "active"
            phase.start_time = datetime.now()
            self.current_phase = phase_name
            
            # Activate phase agents
            for agent_name in phase.agents:
                self.update_agent_status(agent_name, "active", f"Working on {phase.name}")
    
    def complete_phase(self, phase_name: str):
        """Complete a generation phase"""
        if phase_name in self.phases:
            phase = self.phases[phase_name]
            phase.status = "completed"
            phase.end_time = datetime.now()
            phase.progress = 100.0
            
            # Complete phase agents
            for agent_name in phase.agents:
                self.update_agent_status(agent_name, "completed", f"Completed {phase.name}")
    
    def get_agent_grid_html(self) -> str:
        """Generate HTML for agent status grid"""
        html = """
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; margin: 10px 0;">
            <h3 style="color: white; margin: 0 0 15px 0; display: flex; align-items: center;">
                <span style="font-size: 24px; margin-right: 10px;">🤖</span>
                AI Agent Status Grid
            </h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
        """
        
        for agent_name, agent in self.agents.items():
            # Status colors and icons
            status_colors = {
                "idle": "#95a5a6",
                "active": "#3498db", 
                "speaking": "#e74c3c",
                "completed": "#27ae60"
            }
            
            status_icons = {
                "idle": "⚪",
                "active": "🟢",
                "speaking": "🟡", 
                "completed": "✅"
            }
            
            color = status_colors.get(agent.status, "#95a5a6")
            icon = status_icons.get(agent.status, "⚪")
            
            # Agent card
            html += f"""
            <div style="background: rgba(255,255,255,0.1); border-radius: 10px; padding: 15px; 
                        border-left: 4px solid {agent.color}; backdrop-filter: blur(10px);">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 20px; margin-right: 8px;">{agent.emoji}</span>
                    <strong style="color: white; font-size: 14px;">{agent_name}</strong>
                    <span style="margin-left: auto; font-size: 16px;">{icon}</span>
                </div>
                <div style="color: rgba(255,255,255,0.8); font-size: 12px; margin-bottom: 5px;">
                    Status: <span style="color: {color}; font-weight: bold;">{agent.status.title()}</span>
                </div>
                <div style="color: rgba(255,255,255,0.7); font-size: 11px; line-height: 1.3;">
                    {agent.current_task if agent.current_task else "Waiting for assignment..."}
                </div>
                <div style="color: rgba(255,255,255,0.6); font-size: 10px; margin-top: 5px;">
                    Messages: {agent.messages_count} | Last: {agent.last_activity.strftime('%H:%M:%S')}
                </div>
            </div>
            """
        
        html += """
            </div>
        </div>
        """
        
        return html
    
    def get_phase_progress_html(self) -> str:
        """Generate HTML for phase progress"""
        html = """
        <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 20px; border-radius: 15px; margin: 10px 0;">
            <h3 style="color: white; margin: 0 0 15px 0; display: flex; align-items: center;">
                <span style="font-size: 24px; margin-right: 10px;">📊</span>
                Generation Phase Progress
            </h3>
        """
        
        for phase_name, phase in self.phases.items():
            # Phase status colors
            status_colors = {
                "pending": "#95a5a6",
                "active": "#3498db",
                "completed": "#27ae60",
                "error": "#e74c3c"
            }
            
            status_icons = {
                "pending": "⏳",
                "active": "🔄",
                "completed": "✅",
                "error": "❌"
            }
            
            color = status_colors.get(phase.status, "#95a5a6")
            icon = status_icons.get(phase.status, "⏳")
            
            # Calculate duration
            duration_text = ""
            if phase.start_time:
                if phase.end_time:
                    duration = (phase.end_time - phase.start_time).total_seconds()
                    duration_text = f"Duration: {duration:.1f}s"
                else:
                    duration = (datetime.now() - phase.start_time).total_seconds()
                    duration_text = f"Running: {duration:.1f}s"
            
            html += f"""
            <div style="background: rgba(255,255,255,0.1); border-radius: 10px; padding: 15px; margin-bottom: 10px;
                        border-left: 4px solid {color}; backdrop-filter: blur(10px);">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <span style="font-size: 18px; margin-right: 10px;">{icon}</span>
                    <strong style="color: white; font-size: 16px;">{phase.name}</strong>
                    <span style="margin-left: auto; color: {color}; font-weight: bold; font-size: 14px;">
                        {phase.status.title()}
                    </span>
                </div>
                
                <div style="width: 100%; background: rgba(255,255,255,0.2); border-radius: 8px; height: 8px; margin-bottom: 8px;">
                    <div style="width: {phase.progress}%; background: {color}; height: 100%; border-radius: 8px; 
                                transition: width 0.3s ease;"></div>
                </div>
                
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="color: rgba(255,255,255,0.7); font-size: 12px;">
                        Agents: {len(phase.agents)} | Messages: {len(phase.messages)}
                    </div>
                    <div style="color: rgba(255,255,255,0.6); font-size: 11px;">
                        {duration_text}
                    </div>
                </div>
            </div>
            """
        
        html += """
        </div>
        """
        
        return html
    
    def get_live_discussion_html(self) -> str:
        """Generate HTML for live discussions"""
        html = """
        <div style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); padding: 20px; border-radius: 15px; margin: 10px 0;">
            <h3 style="color: white; margin: 0 0 15px 0; display: flex; align-items: center;">
                <span style="font-size: 24px; margin-right: 10px;">💬</span>
                Live AI Agent Discussions
            </h3>
            <div style="max-height: 400px; overflow-y: auto; background: rgba(255,255,255,0.1); 
                        border-radius: 10px; padding: 15px; backdrop-filter: blur(10px);">
        """
        
        # Get recent messages
        recent_messages = self.ui_state["messages"][-20:] if self.ui_state["messages"] else []
        
        if not recent_messages:
            html += """
            <div style="text-align: center; color: rgba(255,255,255,0.7); padding: 20px;">
                <p>💭 No discussions yet. Start generation to see AI agents collaborate!</p>
            </div>
            """
        else:
            for msg in recent_messages:
                agent_name = msg["agent"]
                agent = self.agents.get(agent_name)
                agent_color = agent.color if agent else "#95a5a6"
                agent_emoji = agent.emoji if agent else "🤖"
                
                # Message type styling
                type_colors = {
                    "discussion": "rgba(255,255,255,0.1)",
                    "decision": "rgba(52, 152, 219, 0.2)",
                    "consensus": "rgba(46, 213, 115, 0.2)",
                    "error": "rgba(231, 76, 60, 0.2)"
                }
                
                bg_color = type_colors.get(msg["type"], "rgba(255,255,255,0.1)")
                
                html += f"""
                <div style="margin: 8px 0; padding: 12px; background: {bg_color}; 
                            border-radius: 8px; border-left: 4px solid {agent_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <div style="display: flex; align-items: center;">
                            <span style="font-size: 16px; margin-right: 8px;">{agent_emoji}</span>
                            <strong style="color: {agent_color}; font-size: 14px;">{agent_name}</strong>
                        </div>
                        <span style="color: rgba(255,255,255,0.6); font-size: 11px;">
                            {msg['timestamp'].strftime('%H:%M:%S')}
                        </span>
                    </div>
                    <div style="color: rgba(255,255,255,0.9); font-size: 13px; line-height: 1.4;">
                        {msg['message'][:200]}{'...' if len(msg['message']) > 200 else ''}
                    </div>
                </div>
                """
        
        html += """
            </div>
        </div>
        """
        
        return html
    
    def get_overall_status_html(self) -> str:
        """Generate HTML for overall status"""
        status = self.ui_state
        
        # Calculate overall progress
        total_progress = sum(phase.progress for phase in self.phases.values()) / len(self.phases)
        
        # Status determination
        if self.generation_active:
            if total_progress < 10:
                status_text = "🚀 Initializing..."
                status_color = "#3498db"
            elif total_progress < 100:
                status_text = f"🎬 Generating... ({total_progress:.1f}%)"
                status_color = "#e67e22"
            else:
                status_text = "✅ Generation Complete!"
                status_color = "#27ae60"
        else:
            status_text = "⚪ Ready to Generate"
            status_color = "#95a5a6"
        
        # Time calculations
        time_info = ""
        if status["generation_start"]:
            elapsed = (datetime.now() - status["generation_start"]).total_seconds()
            time_info = f"Elapsed: {elapsed:.1f}s"
            
            if status["estimated_completion"]:
                remaining = (status["estimated_completion"] - datetime.now()).total_seconds()
                if remaining > 0:
                    time_info += f" | ETA: {remaining:.1f}s"
        
        html = f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; margin: 10px 0;">
            <h2 style="color: white; margin: 0 0 15px 0; display: flex; align-items: center;">
                <span style="font-size: 28px; margin-right: 10px;">🎬</span>
                Viral Video Generator Status
            </h2>
            
            <div style="background: rgba(255,255,255,0.1); border-radius: 10px; padding: 20px; backdrop-filter: blur(10px);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <div style="color: white; font-size: 18px; font-weight: bold;">
                        {status_text}
                    </div>
                    <div style="color: rgba(255,255,255,0.8); font-size: 14px;">
                        {time_info}
                    </div>
                </div>
                
                <div style="width: 100%; background: rgba(255,255,255,0.2); border-radius: 10px; height: 20px; margin-bottom: 15px;">
                    <div style="width: {total_progress}%; background: {status_color}; height: 100%; border-radius: 10px; 
                                transition: width 0.3s ease; display: flex; align-items: center; justify-content: center;">
                        <span style="color: white; font-size: 12px; font-weight: bold;">
                            {total_progress:.1f}%
                        </span>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px;">
                    <div style="text-align: center; color: white;">
                        <div style="font-size: 24px; font-weight: bold;">{len([a for a in self.agents.values() if a.status == 'active'])}</div>
                        <div style="font-size: 12px; opacity: 0.8;">Active Agents</div>
                    </div>
                    <div style="text-align: center; color: white;">
                        <div style="font-size: 24px; font-weight: bold;">{len(status['messages'])}</div>
                        <div style="font-size: 12px; opacity: 0.8;">Total Messages</div>
                    </div>
                    <div style="text-align: center; color: white;">
                        <div style="font-size: 24px; font-weight: bold;">{len([p for p in self.phases.values() if p.status == 'completed'])}</div>
                        <div style="font-size: 12px; opacity: 0.8;">Completed Phases</div>
                    </div>
                    <div style="text-align: center; color: white;">
                        <div style="font-size: 24px; font-weight: bold;">{len(status['errors'])}</div>
                        <div style="font-size: 12px; opacity: 0.8;">Errors</div>
                    </div>
                </div>
            </div>
        </div>
        """
        
        return html
    
    def simulate_generation(self, topic: str, duration: int, style: str, platform: str, 
                          voice_speed: float, enable_discussions: bool, max_rounds: int,
                          progress=gr.Progress()):
        """Simulate video generation with real-time updates"""
        
        try:
            self.generation_active = True
            self.ui_state["generation_start"] = datetime.now()
            self.ui_state["estimated_completion"] = datetime.now() + timedelta(minutes=5)
            
            # Clear previous state
            self.ui_state["messages"] = []
            self.ui_state["errors"] = []
            
            # Reset all agents and phases
            for agent in self.agents.values():
                agent.status = "idle"
                agent.current_task = ""
                agent.messages_count = 0
            
            for phase in self.phases.values():
                phase.status = "pending"
                phase.progress = 0.0
                phase.start_time = None
                phase.end_time = None
                phase.messages = []
            
            progress(0.0, desc="Starting generation...")
            
            # Simulate each phase
            phase_names = list(self.phases.keys())
            for i, phase_name in enumerate(phase_names):
                self.start_phase(phase_name)
                phase = self.phases[phase_name]
                
                progress(i / len(phase_names), desc=f"Phase: {phase.name}")
                
                # Simulate agent discussions
                if enable_discussions:
                    for j, agent_name in enumerate(phase.agents):
                        self.add_agent_message(
                            agent_name,
                            f"Working on {phase.name} for topic '{topic}' with {style} style...",
                            "discussion"
                        )
                        
                        # Simulate progress
                        phase.progress = ((j + 1) / len(phase.agents)) * 100
                        time.sleep(0.5)  # Simulate processing time
                
                self.complete_phase(phase_name)
                time.sleep(1)  # Pause between phases
            
            # Final generation
            progress(0.9, desc="Finalizing video...")
            
            # Call actual generation function
            result = generate_viral_video(
                topic=topic,
                duration=duration,
                style=style,
                platform=platform,
                voice_speed=voice_speed
            )
            
            self.generation_active = False
            progress(1.0, desc="Complete!")
            
            return result, "✅ Video generated successfully with real-time AI collaboration!"
            
        except Exception as e:
            self.generation_active = False
            self.ui_state["errors"].append(str(e))
            logger.error(f"Generation failed: {e}")
            return None, f"❌ Generation failed: {str(e)}"
    
    def create_interface(self):
        """Create the enhanced Gradio interface"""
        
        with gr.Blocks(
            title="🎬 Enhanced Viral Video Generator",
            theme=gr.themes.Soft(
                primary_hue="blue",
                secondary_hue="green",
                neutral_hue="gray"
            ),
            css="""
            .gradio-container {
                max-width: 1400px !important;
                margin: auto;
            }
            .status-panel {
                border-radius: 15px;
                padding: 20px;
                margin: 10px 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .agent-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 10px;
            }
            """
        ) as interface:
            
            # Header
            gr.HTML("""
            <div style="text-align: center; padding: 25px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.1);">
                <h1 style="margin: 0; font-size: 42px; font-weight: 800;">🎬 Enhanced Viral Video Generator</h1>
                <p style="margin: 15px 0 0 0; font-size: 20px; opacity: 0.9;">
                    Real-Time AI Agent Collaboration & Colorful Process Visualization
                </p>
            </div>
            """)
            
            with gr.Row():
                # Left Panel - Controls
                with gr.Column(scale=1):
                    gr.HTML("<h2 style='color: #667eea; margin-bottom: 20px;'>⚙️ Generation Controls</h2>")
                    
                    topic = gr.Textbox(
                        label="🎯 Video Topic",
                        placeholder="Enter your video topic (e.g., 'Persian mythology vs modern Iran')",
                        lines=3,
                        value=""
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
                    
                    with gr.Row():
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
                    
                    gr.HTML("<h3 style='color: #667eea; margin: 20px 0 10px 0;'>🤖 AI Agent Configuration</h3>")
                    
                    with gr.Row():
                        enable_discussions = gr.Checkbox(
                            label="Enable AI Agent Discussions",
                            value=True
                        )
                        max_rounds = gr.Slider(
                            label="Max Discussion Rounds",
                            minimum=1,
                            maximum=10,
                            value=5,
                            step=1
                        )
                    
                    generate_btn = gr.Button(
                        "🚀 Generate Viral Video",
                        variant="primary",
                        size="lg",
                        elem_classes=["generate-btn"]
                    )
                    
                    # Output
                    gr.HTML("<h3 style='color: #667eea; margin: 20px 0 10px 0;'>📹 Generated Video</h3>")
                    
                    video_output = gr.Video(
                        label="Generated Video",
                        interactive=False
                    )
                    
                    result_text = gr.Textbox(
                        label="Generation Result",
                        interactive=False,
                        lines=3
                    )
                
                # Right Panel - Real-time Visualization
                with gr.Column(scale=2):
                    gr.HTML("<h2 style='color: #667eea; margin-bottom: 20px;'>📊 Real-Time Process Visualization</h2>")
                    
                    # Overall Status
                    overall_status = gr.HTML(
                        value=self.get_overall_status_html(),
                        elem_classes=["status-panel"]
                    )
                    
                    # Tabbed visualization
                    with gr.Tabs():
                        with gr.Tab("🤖 AI Agents"):
                            agent_grid = gr.HTML(
                                value=self.get_agent_grid_html(),
                                elem_classes=["agent-grid"]
                            )
                        
                        with gr.Tab("📊 Phase Progress"):
                            phase_progress = gr.HTML(
                                value=self.get_phase_progress_html()
                            )
                        
                        with gr.Tab("💬 Live Discussions"):
                            live_discussions = gr.HTML(
                                value=self.get_live_discussion_html()
                            )
            
            # Event handlers
            generate_btn.click(
                fn=self.simulate_generation,
                inputs=[topic, duration, style, platform, voice_speed, enable_discussions, max_rounds],
                outputs=[video_output, result_text]
            )
            
            # Auto-refresh all displays every 1 second
            def refresh_all_displays():
                return (
                    self.get_overall_status_html(),
                    self.get_agent_grid_html(),
                    self.get_phase_progress_html(),
                    self.get_live_discussion_html()
                )
            
            interface.load(
                fn=refresh_all_displays,
                outputs=[overall_status, agent_grid, phase_progress, live_discussions],
                every=1
            )
        
        return interface

def main():
    """Main function to run the enhanced UI"""
    
    # Check environment
    if not os.getenv('GOOGLE_API_KEY'):
        print("⚠️  Warning: GOOGLE_API_KEY not set")
        print("   export GOOGLE_API_KEY=your_api_key_here")
    
    # Create UI instance
    ui = EnhancedRealtimeUI()
    
    # Create and launch interface
    interface = ui.create_interface()
    
    print("🚀 Launching Enhanced Viral Video Generator UI...")
    print("🌐 Interface: http://localhost:7860")
    print("✨ Features:")
    print("   🤖 Real-time AI agent status grid")
    print("   📊 Live generation phase progress")
    print("   💬 Interactive agent discussions")
    print("   🎨 Colorful process visualization")
    print("   ⚡ Auto-refreshing displays")
    
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True,
        show_error=True
    )

if __name__ == "__main__":
    main() 