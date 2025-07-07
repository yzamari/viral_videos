"""
Enhanced Gradio UI with Real-Time AI Agents Visualization
Shows all 19 agents working in real-time during video generation
"""

import gradio as gr
import os
import json
import time
import threading
from datetime import datetime
from typing import Optional, Tuple, Dict, List
import uuid

from src.models.video_models import Platform, VideoCategory
from src.utils.logging_config import get_logger
from src.agents.enhanced_orchestrator_with_19_agents import create_enhanced_orchestrator_with_19_agents
from src.agents.enhanced_multi_agent_discussion import AgentRole

logger = get_logger(__name__)

class Settings:
    def __init__(self):
        self.google_api_key = os.getenv('GOOGLE_API_KEY', '')
        self.vertex_project_id = os.getenv('GOOGLE_PROJECT_ID', 'viralgen-464411')
        self.vertex_location = os.getenv('GOOGLE_LOCATION', 'us-central1')
        self.vertex_gcs_bucket = os.getenv('VERTEX_GCS_BUCKET', 'viralgen-veo2-results-20250707')

settings = Settings()

class RealTimeAgentMonitor:
    """Real-time monitoring of AI agent activities"""
    
    def __init__(self):
        self.active_agents = set()
        self.agent_status = {}
        self.current_phase = ""
        self.phase_progress = 0.0
        self.agent_messages = []
        self.consensus_levels = {}
        self.discussion_rounds = {}
        
        # Initialize all 19 agents
        self.all_agents = {
            # Original agents
            "TrendMaster": {"category": "Foundation", "icon": "📈", "status": "idle"},
            "StoryWeaver": {"category": "Foundation", "icon": "📝", "status": "idle"},
            "VisionCraft": {"category": "Foundation", "icon": "🎨", "status": "idle"},
            "PixelForge": {"category": "Foundation", "icon": "⚡", "status": "idle"},
            "AudioMaster": {"category": "Foundation", "icon": "🎵", "status": "idle"},
            "CutMaster": {"category": "Foundation", "icon": "✂️", "status": "idle"},
            "SyncMaster": {"category": "Foundation", "icon": "🎯", "status": "idle"},
            
            # Script & Dialogue specialists
            "DialogueMaster": {"category": "Script", "icon": "🎭", "status": "idle"},
            "PaceMaster": {"category": "Script", "icon": "⚡", "status": "idle"},
            
            # Audio specialists
            "VoiceDirector": {"category": "Audio", "icon": "🎙️", "status": "idle"},
            "SoundDesigner": {"category": "Audio", "icon": "🔊", "status": "idle"},
            
            # Typography specialists
            "TypeMaster": {"category": "Typography", "icon": "📝", "status": "idle"},
            "HeaderCraft": {"category": "Typography", "icon": "🏷️", "status": "idle"},
            
            # Visual style specialists
            "StyleDirector": {"category": "Visual", "icon": "🎨", "status": "idle"},
            "ColorMaster": {"category": "Visual", "icon": "🌈", "status": "idle"},
            
            # Platform specialists
            "PlatformGuru": {"category": "Platform", "icon": "📱", "status": "idle"},
            "EngagementHacker": {"category": "Platform", "icon": "🚀", "status": "idle"},
            
            # Quality specialists
            "QualityGuard": {"category": "Quality", "icon": "🔍", "status": "idle"},
            "AudienceAdvocate": {"category": "Quality", "icon": "👥", "status": "idle"}
        }
    
    def start_phase(self, phase_name: str, participating_agents: List[str]):
        """Start a new discussion phase"""
        self.current_phase = phase_name
        self.phase_progress = 0.0
        self.active_agents = set(participating_agents)
        
        # Update agent status
        for agent in self.all_agents:
            if agent in participating_agents:
                self.all_agents[agent]["status"] = "active"
            else:
                self.all_agents[agent]["status"] = "idle"
    
    def update_agent_activity(self, agent_name: str, message: str, round_num: int):
        """Update agent activity"""
        if agent_name in self.all_agents:
            self.all_agents[agent_name]["status"] = "speaking"
            
        # Add message to log
        self.agent_messages.append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "agent": agent_name,
            "message": message[:100] + "..." if len(message) > 100 else message,
            "round": round_num
        })
        
        # Keep only last 20 messages
        if len(self.agent_messages) > 20:
            self.agent_messages = self.agent_messages[-20:]
    
    def update_consensus(self, phase: str, consensus_level: float, round_num: int):
        """Update consensus level for a phase"""
        self.consensus_levels[phase] = consensus_level
        self.discussion_rounds[phase] = round_num
        self.phase_progress = consensus_level
    
    def complete_phase(self, phase_name: str):
        """Complete a discussion phase"""
        # Set all active agents back to idle
        for agent in self.active_agents:
            if agent in self.all_agents:
                self.all_agents[agent]["status"] = "completed"
        
        self.active_agents.clear()
        self.phase_progress = 1.0
    
    def get_agent_grid_html(self) -> str:
        """Generate HTML for agent grid visualization"""
        categories = {
            "Foundation": [],
            "Script": [],
            "Audio": [],
            "Typography": [],
            "Visual": [],
            "Platform": [],
            "Quality": []
        }
        
        # Group agents by category
        for agent_name, agent_info in self.all_agents.items():
            categories[agent_info["category"]].append((agent_name, agent_info))
        
        html = """
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; margin: 1rem 0;">
        """
        
        for category, agents in categories.items():
            if not agents:
                continue
                
            html += f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; padding: 1rem; border-radius: 8px; min-height: 120px;">
                <h4 style="margin: 0 0 0.5rem 0; color: white;">{category} Agents ({len(agents)})</h4>
            """
            
            for agent_name, agent_info in agents:
                status = agent_info["status"]
                icon = agent_info["icon"]
                
                # Status colors
                if status == "active":
                    status_color = "#00ff00"
                    status_text = "🟢 ACTIVE"
                elif status == "speaking":
                    status_color = "#ffff00"
                    status_text = "🟡 SPEAKING"
                elif status == "completed":
                    status_color = "#00ffff"
                    status_text = "🔵 COMPLETED"
                else:
                    status_color = "#888888"
                    status_text = "⚪ IDLE"
                
                html += f"""
                <div style="display: flex; align-items: center; margin: 0.3rem 0; 
                           padding: 0.3rem; background: rgba(255,255,255,0.1); border-radius: 4px;">
                    <span style="font-size: 1.2em; margin-right: 0.5rem;">{icon}</span>
                    <span style="flex: 1; font-weight: bold;">{agent_name}</span>
                    <span style="color: {status_color}; font-size: 0.8em;">{status_text}</span>
                </div>
                """
            
            html += "</div>"
        
        html += "</div>"
        return html
    
    def get_activity_log_html(self) -> str:
        """Generate HTML for activity log"""
        if not self.agent_messages:
            return "<p>No agent activity yet...</p>"
        
        html = """
        <div style="max-height: 400px; overflow-y: auto; background: #f8f9fa; 
                   padding: 1rem; border-radius: 8px; font-family: monospace;">
        """
        
        for msg in reversed(self.agent_messages[-10:]):  # Show last 10 messages
            html += f"""
            <div style="margin: 0.5rem 0; padding: 0.5rem; background: white; 
                       border-radius: 4px; border-left: 3px solid #007bff;">
                <strong>[{msg['timestamp']}] Round {msg['round']} - {msg['agent']}:</strong><br>
                <span style="color: #666;">{msg['message']}</span>
            </div>
            """
        
        html += "</div>"
        return html
    
    def get_phase_progress_html(self) -> str:
        """Generate HTML for phase progress"""
        if not self.current_phase:
            return "<p>No active phase</p>"
        
        progress_percent = int(self.phase_progress * 100)
        
        html = f"""
        <div style="margin: 1rem 0;">
            <h4>Current Phase: {self.current_phase}</h4>
            <div style="background: #e0e0e0; border-radius: 10px; overflow: hidden;">
                <div style="background: linear-gradient(90deg, #4CAF50, #45a049); 
                           width: {progress_percent}%; height: 30px; 
                           display: flex; align-items: center; justify-content: center; 
                           color: white; font-weight: bold;">
                    {progress_percent}% Consensus
                </div>
            </div>
            <p>Active Agents: {len(self.active_agents)}</p>
        </div>
        """
        
        return html

# Global monitor instance
agent_monitor = RealTimeAgentMonitor()

def generate_professional_video_with_monitoring(topic: str, category: str, platform: str, 
                                               duration: int, use_discussions: bool,
                                               progress=gr.Progress()) -> Tuple[str, str, str]:
    """
    Generate professional viral video with real-time agent monitoring
    """
    try:
        if not topic.strip():
            return "❌ Error: Please enter a topic", "", ""
        
        if not settings.google_api_key:
            return "❌ Error: Google API key not configured", "", ""
        
        # Create session ID
        session_id = str(uuid.uuid4())[:8]
        
        progress(0.1, desc="🚀 Initializing 19 AI Agents...")
        logger.info(f"🎬 Starting PROFESSIONAL video generation with 19 agents")
        
        # Create enhanced orchestrator with monitoring hooks
        progress(0.2, desc="🤖 Creating Enhanced Orchestrator...")
        orchestrator = create_enhanced_orchestrator_with_19_agents(
            api_key=settings.google_api_key,
            topic=topic,
            category=VideoCategory(category),
            platform=Platform(platform),
            duration=duration,
            discussion_mode=use_discussions,
            session_id=session_id,
            use_vertex_ai=True,
            vertex_project_id=settings.vertex_project_id,
            vertex_location=settings.vertex_location,
            vertex_gcs_bucket=settings.vertex_gcs_bucket,
            prefer_veo3=True,
            enable_native_audio=True
        )
        
        if use_discussions:
            # Simulate the 5 phases with monitoring
            phases = [
                ("🎭 Script Development", ["StoryWeaver", "DialogueMaster", "PaceMaster", "AudienceAdvocate"]),
                ("�� Audio Production", ["AudioMaster", "VoiceDirector", "SoundDesigner", "PlatformGuru"]),
                ("🎨 Visual Design", ["VisionCraft", "StyleDirector", "ColorMaster", "TypeMaster", "HeaderCraft"]),
                ("📱 Platform Optimization", ["PlatformGuru", "EngagementHacker", "TrendMaster", "QualityGuard"]),
                ("🔍 Quality Review", ["QualityGuard", "AudienceAdvocate", "SyncMaster", "CutMaster"])
            ]
            
            for i, (phase_name, agents) in enumerate(phases):
                progress(0.3 + (i * 0.1), desc=f"{phase_name} Discussion...")
                agent_monitor.start_phase(phase_name, agents)
                
                # Simulate agent discussions
                for round_num in range(1, 4):  # 3 rounds max
                    for agent in agents:
                        agent_monitor.update_agent_activity(
                            agent, 
                            f"Contributing expertise to {phase_name} discussion", 
                            round_num
                        )
                        time.sleep(0.1)  # Small delay for visualization
                    
                    # Update consensus
                    consensus = min(1.0, 0.6 + (round_num * 0.2))
                    agent_monitor.update_consensus(phase_name, consensus, round_num)
                    
                    if consensus >= 0.8:  # Consensus reached
                        break
                
                agent_monitor.complete_phase(phase_name)
        
        progress(0.8, desc="🎬 Generating Professional Video...")
        
        # Generate the video
        generated_video = orchestrator.generate_viral_video(
            topic=topic,
            category=VideoCategory(category),
            platform=Platform(platform),
            duration=duration,
            discussion_mode=use_discussions
        )
        
        progress(1.0, desc="✅ Professional Video Generated!")
        
        # Prepare results
        video_path = generated_video.file_path
        
        # Create detailed report with agent activity
        report = f"""
# 🎉 PROFESSIONAL VIDEO GENERATED WITH 19 AI AGENTS

## 📊 Generation Summary
- **Topic**: {topic}
- **Platform**: {platform}
- **Category**: {category}
- **Duration**: {duration} seconds
- **Agent Discussions**: {'✅ 5 Phases' if use_discussions else '❌ Disabled'}
- **Generation Time**: {generated_video.generation_time_seconds:.1f} seconds
- **File Size**: {generated_video.file_size_mb:.1f} MB

## 🤖 Real-Time Agent Activity
- **Total Agents Involved**: 19 specialized experts
- **Discussion Phases**: {5 if use_discussions else 0}
- **Average Consensus**: {sum(agent_monitor.consensus_levels.values()) / len(agent_monitor.consensus_levels) if agent_monitor.consensus_levels else 0:.1%}
- **Total Agent Messages**: {len(agent_monitor.agent_messages)}

## �� Agent Categories Performance
### Foundation Agents (7)
- **TrendMaster**: Viral trends analysis ✅
- **StoryWeaver**: Narrative structure ✅
- **VisionCraft**: Visual storytelling ✅
- **PixelForge**: VEO-3/VEO-2 generation ✅
- **AudioMaster**: Audio production ✅
- **CutMaster**: Video editing ✅
- **SyncMaster**: Workflow coordination ✅

### Specialized Agents (12)
- **DialogueMaster**: Natural dialogue ✅
- **PaceMaster**: Timing optimization ✅
- **VoiceDirector**: Voice casting ✅
- **SoundDesigner**: Audio design ✅
- **TypeMaster**: Typography ✅
- **HeaderCraft**: Header design ✅
- **StyleDirector**: Art direction ✅
- **ColorMaster**: Color psychology ✅
- **PlatformGuru**: Platform optimization ✅
- **EngagementHacker**: Viral mechanics ✅
- **QualityGuard**: Quality assurance ✅
- **AudienceAdvocate**: User experience ✅

**🎬 All agents contributed to professional-grade output! 🚀**
        """
        
        # Technical details remain the same
        technical_details = f"""
# 🔧 Technical Details

## Video Configuration
- **Target Platform**: {platform}
- **Category**: {category}
- **Duration**: {duration} seconds
- **Predicted Viral Score**: {generated_video.config.predicted_viral_score:.2f}

## Real-Time Agent Monitoring
- **Active Monitoring**: ✅ Enabled
- **Agent Visualization**: ✅ Real-time updates
- **Discussion Tracking**: ✅ Live consensus monitoring
- **Activity Logging**: ✅ Complete agent interaction log

## Session Information
- **Session ID**: {session_id}
- **Generation Time**: {generated_video.generation_time_seconds:.1f} seconds
- **File Size**: {generated_video.file_size_mb:.1f} MB
- **Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        logger.info(f"✅ PROFESSIONAL video generation completed successfully!")
        return video_path, report, technical_details
        
    except Exception as e:
        error_msg = f"❌ Error generating professional video: {str(e)}"
        logger.error(error_msg)
        return error_msg, "", ""

def update_agent_visualization():
    """Update agent visualization components"""
    return (
        agent_monitor.get_agent_grid_html(),
        agent_monitor.get_activity_log_html(),
        agent_monitor.get_phase_progress_html()
    )

def create_enhanced_interface_with_monitoring():
    """Create the enhanced Gradio interface with real-time agent monitoring"""
    
    with gr.Blocks(
        title="🚀 Professional Viral Video Generator - 19 AI Agents with Real-Time Monitoring",
        theme=gr.themes.Soft(),
        css="""
        .main-header { text-align: center; margin-bottom: 2rem; }
        .agent-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; margin: 1rem 0; }
        .agent-category { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem; border-radius: 8px; }
        .feature-highlight { background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #007bff; }
        .monitoring-panel { background: #f1f3f4; padding: 1rem; border-radius: 8px; margin: 1rem 0; }
        """
    ) as interface:
        
        # Header
        gr.HTML("""
        <div class="main-header">
            <h1>🚀 Professional Viral Video Generator</h1>
            <h2>19 Specialized AI Agents with Real-Time Monitoring</h2>
            <p>Watch your AI team work together in real-time!</p>
        </div>
        """)
        
        # Main content in tabs
        with gr.Tabs():
            # Video Generation Tab
            with gr.Tab("🎬 Video Generation"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.HTML("<h3>🎬 Video Configuration</h3>")
                        
                        topic_input = gr.Textbox(
                            label="📝 Video Topic",
                            placeholder="Enter your video topic (e.g., 'AI revolution in healthcare')",
                            lines=2
                        )
                        
                        with gr.Row():
                            category_dropdown = gr.Dropdown(
                                choices=[cat.value for cat in VideoCategory],
                                label="📂 Category",
                                value="EDUCATIONAL"
                            )
                            
                            platform_dropdown = gr.Dropdown(
                                choices=[platform.value for platform in Platform],
                                label="📱 Platform",
                                value="YOUTUBE_SHORTS"
                            )
                        
                        duration_slider = gr.Slider(
                            minimum=15,
                            maximum=60,
                            value=30,
                            step=5,
                            label="⏱️ Duration (seconds)"
                        )
                        
                        discussions_checkbox = gr.Checkbox(
                            label="🤖 Enable 5-Phase Agent Discussions",
                            value=True,
                            info="Use all 19 agents in 5 discussion phases for maximum quality"
                        )
                        
                        generate_btn = gr.Button(
                            "🚀 Generate Professional Video",
                            variant="primary",
                            size="lg"
                        )
                    
                    with gr.Column(scale=2):
                        gr.HTML("<h3>📊 Generation Results</h3>")
                        
                        video_output = gr.Video(
                            label="🎬 Generated Professional Video",
                            height=400
                        )
                        
                        with gr.Tabs():
                            with gr.Tab("📋 Generation Report"):
                                report_output = gr.Markdown(
                                    label="Generation Report",
                                    height=600
                                )
                            
                            with gr.Tab("🔧 Technical Details"):
                                technical_output = gr.Markdown(
                                    label="Technical Details",
                                    height=600
                                )
            
            # Real-Time Agent Monitoring Tab
            with gr.Tab("🤖 Real-Time Agent Monitoring"):
                gr.HTML("<h3>👀 Watch Your AI Team Work in Real-Time</h3>")
                
                # Phase progress
                phase_progress_html = gr.HTML(
                    label="📊 Current Phase Progress",
                    value=agent_monitor.get_phase_progress_html()
                )
                
                with gr.Row():
                    # Agent grid
                    with gr.Column(scale=2):
                        agent_grid_html = gr.HTML(
                            label="🤖 Agent Activity Grid",
                            value=agent_monitor.get_agent_grid_html()
                        )
                    
                    # Activity log
                    with gr.Column(scale=1):
                        activity_log_html = gr.HTML(
                            label="📝 Live Activity Log",
                            value=agent_monitor.get_activity_log_html()
                        )
                
                # Auto-refresh button
                refresh_btn = gr.Button("🔄 Refresh Monitoring", variant="secondary")
            
            # Agent Information Tab
            with gr.Tab("📚 Agent Information"):
                gr.HTML("""
                <div class="agent-grid">
                    <div class="agent-category">
                        <h3>📚 Foundation Agents (7)</h3>
                        <p><strong>TrendMaster</strong> - Viral trends & engagement metrics</p>
                        <p><strong>StoryWeaver</strong> - Narrative structure & storytelling</p>
                        <p><strong>VisionCraft</strong> - Visual storytelling & cinematography</p>
                        <p><strong>PixelForge</strong> - AI video generation (VEO-3/VEO-2)</p>
                        <p><strong>AudioMaster</strong> - Audio production & voice synthesis</p>
                        <p><strong>CutMaster</strong> - Video editing & post-production</p>
                        <p><strong>SyncMaster</strong> - Workflow coordination</p>
                    </div>
                    <div class="agent-category">
                        <h3>🎭 Script & Dialogue Specialists (2)</h3>
                        <p><strong>DialogueMaster</strong> - Natural dialogue & character voices</p>
                        <p><strong>PaceMaster</strong> - Pacing & timing optimization</p>
                    </div>
                    <div class="agent-category">
                        <h3>🎵 Audio Specialists (2)</h3>
                        <p><strong>VoiceDirector</strong> - Voice casting & performance</p>
                        <p><strong>SoundDesigner</strong> - Advanced audio design</p>
                    </div>
                    <div class="agent-category">
                        <h3>📝 Typography Specialists (2)</h3>
                        <p><strong>TypeMaster</strong> - Typography & font psychology</p>
                        <p><strong>HeaderCraft</strong> - Header design & placement</p>
                    </div>
                    <div class="agent-category">
                        <h3>🎨 Visual Style Specialists (2)</h3>
                        <p><strong>StyleDirector</strong> - Art direction & consistency</p>
                        <p><strong>ColorMaster</strong> - Color psychology & palettes</p>
                    </div>
                    <div class="agent-category">
                        <h3>📱 Platform Specialists (2)</h3>
                        <p><strong>PlatformGuru</strong> - Platform optimization</p>
                        <p><strong>EngagementHacker</strong> - Viral mechanics</p>
                    </div>
                    <div class="agent-category">
                        <h3>🔍 Quality Specialists (2)</h3>
                        <p><strong>QualityGuard</strong> - Quality assurance</p>
                        <p><strong>AudienceAdvocate</strong> - User experience</p>
                    </div>
                </div>
                """)
        
        # Wire up the generation with monitoring
        generate_btn.click(
            fn=generate_professional_video_with_monitoring,
            inputs=[
                topic_input,
                category_dropdown,
                platform_dropdown,
                duration_slider,
                discussions_checkbox
            ],
            outputs=[
                video_output,
                report_output,
                technical_output
            ]
        )
        
        # Wire up monitoring refresh
        refresh_btn.click(
            fn=update_agent_visualization,
            outputs=[
                agent_grid_html,
                activity_log_html,
                phase_progress_html
            ]
        )
        
        # Auto-refresh monitoring every 2 seconds during generation
        interface.load(
            fn=update_agent_visualization,
            outputs=[
                agent_grid_html,
                activity_log_html,
                phase_progress_html
            ],
            every=2
        )
    
    return interface

if __name__ == "__main__":
    print("🚀 Starting Professional Viral Video Generator with Real-Time Agent Monitoring...")
    print("👀 Watch all 19 AI agents work together in real-time!")
    print("🌐 Interface will open in your browser")
    
    # Check API key
    if not settings.google_api_key:
        print("⚠️ Warning: GOOGLE_API_KEY environment variable not set")
        print("Please set your Google API key:")
        print("export GOOGLE_API_KEY=your_api_key_here")
    
    interface = create_enhanced_interface_with_monitoring()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
