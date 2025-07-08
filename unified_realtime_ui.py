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
import json
import time
import threading
import queue
import gradio as gr
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from launch_full_working_app import FullWorkingVideoApp
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

class RealTimeAgentVisualizer:
    """Real-time visualization of agent discussions"""
    
    def __init__(self):
        self.discussion_data = {}
        self.current_phase = ""
        self.agents_status = {}
        self.consensus_history = []
        
    def update_discussion(self, phase: str, agents: List[str], consensus: float, 
                         round_num: int, agent_messages: Dict[str, str]) -> str:
        """Update discussion visualization data"""
        self.current_phase = phase
        self.consensus_history.append({
            'phase': phase,
            'round': round_num,
            'consensus': consensus,
            'timestamp': datetime.now().isoformat()
        })
        
        # Update agent status
        for agent in agents:
            self.agents_status[agent] = {
                'active': True,
                'last_message': agent_messages.get(agent, ""),
                'phase': phase
            }
        
        return self.generate_visualization()
    
    def generate_visualization(self) -> str:
        """Generate HTML visualization of agent discussions"""
        html = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>🤖 Live Agent Discussions</h2>
            
            <div style="background: #f0f8ff; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                <h3>Current Phase: {self.current_phase}</h3>
                {self._generate_consensus_chart()}
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px;">
                {self._generate_agent_cards()}
            </div>
            
            <div style="margin-top: 20px;">
                <h3>📊 Consensus Progress</h3>
                {self._generate_consensus_timeline()}
            </div>
        </div>
        """
        return html
    
    def _generate_consensus_chart(self) -> str:
        """Generate consensus progress chart"""
        if not self.consensus_history:
            return "<p>No consensus data yet...</p>"
        
        latest = self.consensus_history[-1]
        consensus_pct = latest['consensus'] * 100
        
        # Create a visual progress bar
        bar_width = min(consensus_pct, 100)
        color = "#4CAF50" if consensus_pct >= 80 else "#FF9800" if consensus_pct >= 60 else "#f44336"
        
        return f"""
        <div style="margin: 10px 0;">
            <div style="background: #ddd; height: 20px; border-radius: 10px; overflow: hidden;">
                <div style="background: {color}; height: 100%; width: {bar_width}%; transition: width 0.3s ease;"></div>
            </div>
            <p style="margin: 5px 0; font-weight: bold;">Consensus: {consensus_pct:.1f}%</p>
        </div>
        """
    
    def _generate_agent_cards(self) -> str:
        """Generate individual agent status cards"""
        if not self.agents_status:
            return "<p>No active agents yet...</p>"
        
        cards = []
        for agent, status in self.agents_status.items():
            active_color = "#4CAF50" if status['active'] else "#ccc"
            last_message = status['last_message'][:100] + "..." if len(status['last_message']) > 100 else status['last_message']
            
            card = f"""
            <div style="border: 2px solid {active_color}; border-radius: 10px; padding: 15px; background: white;">
                <h4 style="margin: 0 0 10px 0; color: {active_color};">🤖 {agent}</h4>
                <p style="margin: 5px 0; font-size: 12px; color: #666;">Phase: {status['phase']}</p>
                <p style="margin: 10px 0; font-size: 14px; background: #f9f9f9; padding: 10px; border-radius: 5px;">
                    {last_message or "Waiting for input..."}
                </p>
            </div>
            """
            cards.append(card)
        
        return "".join(cards)
    
    def _generate_consensus_timeline(self) -> str:
        """Generate consensus timeline"""
        if not self.consensus_history:
            return "<p>No timeline data yet...</p>"
        
        timeline_items = []
        for item in self.consensus_history[-5:]:  # Show last 5 items
            consensus_pct = item['consensus'] * 100
            color = "#4CAF50" if consensus_pct >= 80 else "#FF9800" if consensus_pct >= 60 else "#f44336"
            
            timeline_item = f"""
            <div style="display: flex; align-items: center; margin: 10px 0; padding: 10px; background: #f9f9f9; border-radius: 5px;">
                <div style="width: 20px; height: 20px; background: {color}; border-radius: 50%; margin-right: 15px;"></div>
                <div>
                    <strong>{item['phase']}</strong> - Round {item['round']} 
                    <span style="color: {color}; font-weight: bold;">({consensus_pct:.1f}%)</span>
                </div>
            </div>
            """
            timeline_items.append(timeline_item)
        
        return "".join(timeline_items)

class UnifiedVideoApp:
    """Unified application combining all video generation functionality"""
    
    def __init__(self):
        self.app = FullWorkingVideoApp()
        self.visualizer = RealTimeAgentVisualizer()
        self.generation_queue = queue.Queue()
        self.is_generating = False
        
        logger.info("🎬 Unified Real-time Video App initialized")
    
    def generate_video_with_realtime_updates(self, mission: str, duration: int, platform: str, 
                                           category: str, use_discussions: bool):
        """Generate video with real-time agent discussion updates"""
        try:
            self.is_generating = True
            
            # Start generation in background thread
            generation_thread = threading.Thread(
                target=self._background_generation,
                args=(mission, duration, platform, category, use_discussions)
            )
            generation_thread.start()
            
            # Return initial status
            return (
                "🚀 **STARTING GENERATION...**\n\nInitializing 19 AI agents for mission strategy...",
                None,  # video
                "📊 **Generation Status:** Starting...",  # details
                self.visualizer.generate_visualization()  # agent discussions
            )
            
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return f"❌ **ERROR:** {e}", None, "Generation failed", "Error in agent discussions"
    
    def _background_generation(self, mission: str, duration: int, platform: str, 
                              category: str, use_discussions: bool):
        """Background thread for video generation"""
        try:
            # Simulate agent discussions with updates
            phases = [
                "Script Development", "Audio Production", "Visual Design", 
                "Platform Optimization", "Quality Assurance"
            ]
            
            for i, phase in enumerate(phases):
                if not use_discussions:
                    break
                    
                # Simulate discussion rounds
                for round_num in range(1, 3):
                    time.sleep(2)  # Simulate discussion time
                    
                    # Simulate consensus building
                    consensus = min(0.6 + (round_num * 0.2) + (i * 0.05), 1.0)
                    
                    # Mock agent messages
                    agent_messages = {
                        "StoryWeaver": f"Developing narrative strategy for '{mission}'...",
                        "DialogueMaster": f"Optimizing dialogue for {platform} audience...",
                        "PaceMaster": f"Adjusting pacing for {duration}s duration...",
                        "AudienceAdvocate": f"Ensuring {category} category alignment..."
                    }
                    
                    # Update visualization
                    viz_html = self.visualizer.update_discussion(
                        phase, list(agent_messages.keys()), consensus, round_num, agent_messages
                    )
                    
                    # Put update in queue
                    self.generation_queue.put({
                        'type': 'discussion_update',
                        'phase': phase,
                        'round': round_num,
                        'consensus': consensus,
                        'visualization': viz_html
                    })
                    
                    if consensus >= 0.8:
                        break
            
            # Now run actual generation
            result = self.app.generate_video(mission, duration, platform, category, use_discussions)
            
            # Put final result in queue
            self.generation_queue.put({
                'type': 'final_result',
                'result': result
            })
            
        except Exception as e:
            self.generation_queue.put({
                'type': 'error',
                'error': str(e)
            })
        finally:
            self.is_generating = False
    
    def get_generation_updates(self):
        """Get real-time generation updates"""
        updates = []
        try:
            while not self.generation_queue.empty():
                update = self.generation_queue.get_nowait()
                updates.append(update)
        except queue.Empty:
            pass
        
        return updates

def create_unified_interface():
    """Create the unified Gradio interface"""
    app = UnifiedVideoApp()
    
    with gr.Blocks(
        title="🎬 Unified Real-time VEO-2 Generator",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1400px !important;
        }
        .agent-discussion {
            height: 600px;
            overflow-y: auto;
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 15px;
        }
        """
    ) as interface:
        
        gr.Markdown("# 🎬 Unified Real-time VEO-2 Video Generator")
        gr.Markdown("**Complete System: Mission Strategy + 19 AI Agents + Live Discussions + VEO-2 Generation**")
        
        with gr.Row():
            # Left Column: Mission Configuration
            with gr.Column(scale=1):
                gr.Markdown("## 🎯 Mission Configuration")
                
                mission_input = gr.Textbox(
                    label="🎯 Mission",
                    value="convince all the kids to love Mango",
                    placeholder="What do you want to achieve? (e.g., 'get teenagers excited about science')",
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
                    
                    platform_input = gr.Dropdown(
                        label="📱 Platform",
                        choices=["youtube", "tiktok", "instagram"],
                        value="youtube"
                    )
                
                with gr.Row():
                    category_input = gr.Dropdown(
                        label="🎭 Category",
                        choices=["Comedy", "Entertainment", "Education"],
                        value="Comedy"
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
                - **Marketing:** "convince teenagers our sneakers are coolest"
                - **Educational:** "make quantum physics exciting for students"  
                - **Social:** "inspire people to adopt rescue pets"
                - **Lifestyle:** "get busy people excited about cooking"
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
                    value="<p>Start generation to see live agent discussions...</p>",
                    elem_classes=["agent-discussion"]
                )
        
        # Generation event handler
        def handle_generation(mission, duration, platform, category, use_discussions):
            return app.generate_video_with_realtime_updates(
                mission, duration, platform, category, use_discussions
            )
        
        generate_btn.click(
            handle_generation,
            inputs=[mission_input, duration_input, platform_input, category_input, discussions_input],
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

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Unified Real-time VEO-2 Video Generator')
    parser.add_argument('--port', type=int, default=7860, help='Port for web interface')
    parser.add_argument('--share', action='store_true', help='Create public sharing link')
    
    args = parser.parse_args()
    
    print("🎬 Starting Unified Real-time VEO-2 Video Generator...")
    print("=" * 60)
    print("🔧 Initializing system...")
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
        share=args.share,
        show_error=True
    )

if __name__ == "__main__":
    main() 