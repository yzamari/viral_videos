#!/usr/bin/env python3
"""
🎬 Unified Real-time VEO-2 Video Generator with Live Agent Discussions

Complete, consolidated UI with real-time agent discussion visualization,
force generation controls, and all features in one file.
"""

import os
import sys
import threading
import time
import json
import re
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

import gradio as gr

# Setup logging to capture agent discussions
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealTimeAgentDiscussionMonitor:
    """Monitor and capture real-time AI agent discussions with full structure"""
    
    def __init__(self):
        self.discussions = {}  # discussions[topic] = discussion_data
        self.current_discussion = None
        self.is_monitoring = False
        self.log_handler = None
        self.pending_agent_data = {}  # Store incomplete agent data
        
    def start_monitoring(self):
        """Start monitoring agent discussions"""
        self.is_monitoring = True
        self.discussions = {}
        self.current_discussion = None
        self.pending_agent_data = {}
        
        # Create and configure log handler
        self.log_handler = AgentDiscussionHandler(self)
        
        # Add handler to relevant loggers
        loggers_to_monitor = [
            'src.agents.enhanced_multi_agent_discussion',
            'src.agents.discussion_visualizer',
            'src.agents.enhanced_orchestrator_with_19_agents',
            'src.agents.multi_agent_discussion',
            'src.utils.comprehensive_logger'
        ]
        
        for logger_name in loggers_to_monitor:
            agent_logger = logging.getLogger(logger_name)
            agent_logger.addHandler(self.log_handler)
            agent_logger.setLevel(logging.INFO)
        
        logger.info("🎭 Started monitoring AI agent discussions")
    
    def stop_monitoring(self):
        """Stop monitoring agent discussions"""
        self.is_monitoring = False
        
        # Remove log handler
        if self.log_handler:
            loggers_to_monitor = [
                'src.agents.enhanced_multi_agent_discussion',
                'src.agents.discussion_visualizer',
                'src.agents.enhanced_orchestrator_with_19_agents',
                'src.agents.multi_agent_discussion',
                'src.utils.comprehensive_logger'
            ]
            
            for logger_name in loggers_to_monitor:
                agent_logger = logging.getLogger(logger_name)
                agent_logger.removeHandler(self.log_handler)
        
        logger.info("🎭 Stopped monitoring AI agent discussions")
    
    def start_new_discussion(self, topic: str, participants: List[str]):
        """Start a new discussion topic"""
        self.current_discussion = topic
        self.discussions[topic] = {
            'topic': topic,
            'participants': participants,
            'rounds': {},
            'consensus_history': [],
            'status': 'ongoing',
            'start_time': datetime.now().strftime("%H:%M:%S"),
            'final_consensus': 0.0,
            'total_rounds': 0
        }
    
    def add_round_data(self, round_num: int, agent_name: str, opinion: str, message: str = "", reasoning: str = "", timestamp: str = ""):
        """Add complete round data for an agent"""
        if not self.current_discussion or self.current_discussion not in self.discussions:
            return
            
        discussion = self.discussions[self.current_discussion]
        
        if round_num not in discussion['rounds']:
            discussion['rounds'][round_num] = {
                'round_number': round_num,
                'agents': {},
                'consensus_level': 0.0,
                'timestamp': timestamp or datetime.now().strftime("%H:%M:%S")
            }
        
        # Agent color and emoji mapping
        agent_styles = {
            'StoryWeaver': {'emoji': '📝', 'color': '#3b82f6', 'team': 'Script Development'},
            'DialogueMaster': {'emoji': '💬', 'color': '#1e40af', 'team': 'Script Development'},
            'PaceMaster': {'emoji': '⏱️', 'color': '#2563eb', 'team': 'Script Development'},
            'AudienceAdvocate': {'emoji': '👥', 'color': '#1d4ed8', 'team': 'Script Development'},
            'AudioMaster': {'emoji': '🎵', 'color': '#10b981', 'team': 'Audio Production'},
            'VoiceMaster': {'emoji': '🗣️', 'color': '#059669', 'team': 'Audio Production'},
            'SoundMaster': {'emoji': '🔊', 'color': '#047857', 'team': 'Audio Production'},
            'MusicMaster': {'emoji': '🎶', 'color': '#065f46', 'team': 'Audio Production'},
            'VisualDirector': {'emoji': '🎨', 'color': '#f97316', 'team': 'Visual Design'},
            'VisionCraft': {'emoji': '🎨', 'color': '#f97316', 'team': 'Visual Design'},
            'ColorMaster': {'emoji': '🌈', 'color': '#ea580c', 'team': 'Visual Design'},
            'LayoutMaster': {'emoji': '📐', 'color': '#dc2626', 'team': 'Visual Design'},
            'EffectsMaster': {'emoji': '✨', 'color': '#c2410c', 'team': 'Visual Design'},
            'PlatformExpert': {'emoji': '📱', 'color': '#8b5cf6', 'team': 'Platform Optimization'},
            'EngagementMaster': {'emoji': '🎯', 'color': '#7c3aed', 'team': 'Platform Optimization'},
            'TrendMaster': {'emoji': '📈', 'color': '#6d28d9', 'team': 'Platform Optimization'},
            'AlgorithmMaster': {'emoji': '🤖', 'color': '#5b21b6', 'team': 'Platform Optimization'},
            'QualityGuard': {'emoji': '🛡️', 'color': '#ef4444', 'team': 'Quality Assurance'},
            'CutMaster': {'emoji': '✂️', 'color': '#dc2626', 'team': 'Quality Assurance'},
            'SyncMaster': {'emoji': '🎯', 'color': '#b91c1c', 'team': 'Quality Assurance'},
            'SuperMaster': {'emoji': '👑', 'color': '#f59e0b', 'team': 'SuperMaster'},
            'ExecutiveChief': {'emoji': '🤖', 'color': '#6b7280', 'team': 'Executive'},
            'BrandMaster': {'emoji': '🤖', 'color': '#6b7280', 'team': 'Brand'},
            'AccessGuard': {'emoji': '🤖', 'color': '#6b7280', 'team': 'Accessibility'},
            'SpeedDemon': {'emoji': '🤖', 'color': '#6b7280', 'team': 'Performance'},
            'PixelForge': {'emoji': '⚡', 'color': '#6b7280', 'team': 'Technical'},
        }
        
        agent_info = agent_styles.get(agent_name, {'emoji': '🤖', 'color': '#6b7280', 'team': 'Other'})
        
        discussion['rounds'][round_num]['agents'][agent_name] = {
            'name': agent_name,
            'emoji': agent_info['emoji'],
            'color': agent_info['color'],
            'team': agent_info['team'],
            'opinion': opinion,
            'message': message,
            'reasoning': reasoning,
            'timestamp': timestamp or datetime.now().strftime("%H:%M:%S")
        }
        
        # Update total rounds
        discussion['total_rounds'] = max(discussion['total_rounds'], round_num)
    
    def update_consensus(self, round_num: int, consensus_level: float):
        """Update consensus level for a round"""
        if not self.current_discussion or self.current_discussion not in self.discussions:
            return
            
        discussion = self.discussions[self.current_discussion]
        
        if round_num in discussion['rounds']:
            discussion['rounds'][round_num]['consensus_level'] = consensus_level
        
        # Add to consensus history
        discussion['consensus_history'].append({
            'round': round_num,
            'consensus': consensus_level,
            'timestamp': datetime.now().strftime("%H:%M:%S")
        })
    
    def complete_discussion(self, final_consensus: float, duration: str):
        """Mark discussion as complete"""
        if not self.current_discussion or self.current_discussion not in self.discussions:
            return
            
        discussion = self.discussions[self.current_discussion]
        discussion['status'] = 'completed'
        discussion['final_consensus'] = final_consensus
        discussion['duration'] = duration
        discussion['end_time'] = datetime.now().strftime("%H:%M:%S")
    
    def generate_discussion_html(self) -> str:
        """Generate comprehensive HTML for all discussions"""
        if not self.discussions:
            return self._generate_initial_html()
        
        html = """
        <div class="discussions-container">
            <div class="discussions-header">
                <h2>🤖 AI Agent Discussions</h2>
                <div class="discussions-stats">
                    <span class="total-discussions">Total Discussions: {}</span>
                    <span class="active-discussions">Active: {}</span>
                    <span class="completed-discussions">Completed: {}</span>
                </div>
            </div>
        """.format(
            len(self.discussions),
            len([d for d in self.discussions.values() if d['status'] == 'ongoing']),
            len([d for d in self.discussions.values() if d['status'] == 'completed'])
        )
        
        # Generate accordion for each discussion
        for topic, discussion in self.discussions.items():
            status_icon = "✅" if discussion['status'] == 'completed' else "🔄"
            consensus_color = "green" if discussion['final_consensus'] >= 0.7 else "orange" if discussion['final_consensus'] >= 0.4 else "red"
            
            html += f"""
            <details class="discussion-accordion" open>
                <summary class="discussion-summary">
                    <div class="discussion-title">
                        {status_icon} {topic}
                    </div>
                    <div class="discussion-meta">
                        <span class="consensus-badge" style="background-color: {consensus_color};">
                            {discussion['final_consensus']:.1%} Consensus
                        </span>
                        <span class="rounds-badge">{discussion['total_rounds']} Rounds</span>
                        <span class="time-badge">{discussion['start_time']}</span>
                    </div>
                </summary>
                
                <div class="discussion-content">
                    <div class="discussion-info">
                        <div class="participants">
                            <strong>Participants:</strong> {', '.join(discussion['participants'])}
                        </div>
                        <div class="consensus-progress">
                            <div class="consensus-bar">
                                <div class="consensus-fill" style="width: {discussion['final_consensus'] * 100}%; background-color: {consensus_color};"></div>
                            </div>
                        </div>
                    </div>
            """
            
            # Generate rounds accordion
            for round_num in sorted(discussion['rounds'].keys()):
                round_data = discussion['rounds'][round_num]
                round_consensus = round_data['consensus_level']
                round_color = "green" if round_consensus >= 0.7 else "orange" if round_consensus >= 0.4 else "red"
                
                html += f"""
                <details class="round-accordion">
                    <summary class="round-summary">
                        <div class="round-title">
                            Round {round_num}
                        </div>
                        <div class="round-meta">
                            <span class="round-consensus" style="color: {round_color};">
                                {round_consensus:.1%} Consensus
                            </span>
                            <span class="round-time">{round_data['timestamp']}</span>
                        </div>
                    </summary>
                    
                    <div class="round-content">
                """
                
                # Group agents by team
                teams = {}
                for agent_data in round_data['agents'].values():
                    team = agent_data['team']
                    if team not in teams:
                        teams[team] = []
                    teams[team].append(agent_data)
                
                # Generate team accordions
                for team_name, team_agents in teams.items():
                    team_colors = {
                        'Script Development': '#3b82f6',
                        'Audio Production': '#10b981',
                        'Visual Design': '#f97316',
                        'Platform Optimization': '#8b5cf6',
                        'Quality Assurance': '#ef4444',
                        'SuperMaster': '#f59e0b',
                        'Executive': '#6b7280',
                        'Brand': '#6b7280',
                        'Accessibility': '#6b7280',
                        'Performance': '#6b7280',
                        'Technical': '#6b7280',
                        'Other': '#6b7280'
                    }
                    team_color = team_colors.get(team_name, '#6b7280')
                    
                    html += f"""
                    <details class="team-accordion">
                        <summary class="team-summary" style="border-left-color: {team_color};">
                            <div class="team-title" style="color: {team_color};">
                                {team_name} ({len(team_agents)} agents)
                            </div>
                        </summary>
                        
                        <div class="team-content">
                    """
                    
                    # Generate agent messages
                    for agent in team_agents:
                        opinion_icon = "✅" if agent['opinion'] == "AGREE" else "❌" if agent['opinion'] == "DISAGREE" else "⚪"
                        opinion_color = "green" if agent['opinion'] == "AGREE" else "red" if agent['opinion'] == "DISAGREE" else "gray"
                        
                        html += f"""
                        <details class="agent-accordion">
                            <summary class="agent-summary" style="border-left-color: {agent['color']};">
                                <div class="agent-info">
                                    <span class="agent-name" style="color: {agent['color']};">
                                        {agent['emoji']} {agent['name']}
                                    </span>
                                    <span class="agent-opinion" style="color: {opinion_color};">
                                        {opinion_icon} {agent['opinion']}
                                    </span>
                                    <span class="agent-time">{agent['timestamp']}</span>
                                </div>
                            </summary>
                            
                            <div class="agent-content">
                                <div class="agent-message">
                                    <strong>Message:</strong>
                                    <p>{agent['message']}</p>
                                </div>
                                {f'<div class="agent-reasoning"><strong>Reasoning:</strong><p>{agent["reasoning"]}</p></div>' if agent['reasoning'] else ''}
                            </div>
                        </details>
                        """
                    
                    html += """
                        </div>
                    </details>
                    """
                
                html += """
                    </div>
                </details>
                """
            
            html += """
                </div>
            </details>
            """
        
        html += """
        </div>
        """
        
        return html
    
    def _generate_initial_html(self) -> str:
        """Generate initial HTML when no discussions are available"""
        return """
        <div class="discussions-container">
            <div class="discussions-header">
                <h2>🤖 AI Agent Discussions</h2>
                <div class="discussions-stats">
                    <span class="status-indicator">Waiting for discussions...</span>
                </div>
            </div>
            
            <div class="waiting-message">
                <p>🎭 AI agents are ready to discuss your mission...</p>
                <p>Start generation to see live discussions!</p>
                <p><strong>Features:</strong></p>
                <ul>
                    <li>📋 Discussion topics with consensus tracking</li>
                    <li>🔄 Round-by-round progression</li>
                    <li>👥 Team-organized agent responses</li>
                    <li>💬 Complete messages and reasoning</li>
                    <li>📊 Real-time consensus updates</li>
                </ul>
            </div>
        </div>
        """

class AgentDiscussionHandler(logging.Handler):
    """Enhanced logging handler to capture complete agent discussion structure"""
    
    def __init__(self, monitor: RealTimeAgentDiscussionMonitor):
        super().__init__()
        self.monitor = monitor
        self.setLevel(logging.INFO)
        self.current_agent = None
        self.current_round = None
        self.pending_message = ""
        self.pending_reasoning = ""
    
    def emit(self, record):
        """Process log records and extract complete agent discussion structure"""
        if not self.monitor.is_monitoring:
            return
            
        try:
            message = record.getMessage()
            
            # 1. Detect new discussion starting
            if "🎭 Starting ENHANCED agent discussion:" in message:
                # Format: "🎭 Starting ENHANCED agent discussion: Script Development Strategy"
                topic = message.split("🎭 Starting ENHANCED agent discussion:")[1].strip()
                # We'll get participants from the next message
                
            elif "👥 Participating agents" in message:
                # Format: "👥 Participating agents (4): StoryWeaver, DialogueMaster, PaceMaster, AudienceAdvocate"
                if ":" in message:
                    participants_part = message.split(":", 1)[1].strip()
                    participants = [p.strip() for p in participants_part.split(",")]
                    # Find the current discussion topic from previous message
                    if hasattr(self.monitor, 'current_discussion') and self.monitor.current_discussion:
                        self.monitor.start_new_discussion(self.monitor.current_discussion, participants)
                        
            elif "🎭 Starting discussion:" in message:
                # Format: "🎭 Starting discussion: Script Development Strategy"
                topic = message.split("🎭 Starting discussion:")[1].strip()
                self.monitor.current_discussion = topic
                
            # 2. Detect round headers with agent info
            elif "Round" in message and "│" in message and any(emoji in message for emoji in ['📝', '💬', '⏱️', '👥', '🎵', '🗣️', '🔊', '🎶', '🎨', '🌈', '📐', '✨', '📱', '🎯', '📈', '🤖', '🛡️', '✂️', '👑', '⚡']):
                # Format: "Round 1 │ 🤖 QualityGuard [DISAGREE]"
                parts = message.split("│")
                if len(parts) >= 2:
                    round_part = parts[0].strip()
                    agent_part = parts[1].strip()
                    
                    # Extract round number
                    round_match = re.search(r'Round (\d+)', round_part)
                    if round_match:
                        self.current_round = int(round_match.group(1))
                    
                    # Extract agent name and opinion
                    # Look for pattern: emoji space agent_name [OPINION]
                    agent_pattern = r'(📝|💬|⏱️|👥|🎵|🗣️|🔊|🎶|🎨|🌈|📐|✨|📱|🎯|📈|🤖|🛡️|✂️|👑|⚡)\s+(\w+)\s*\[(\w+)\]'
                    agent_match = re.search(agent_pattern, agent_part)
                    
                    if agent_match:
                        emoji = agent_match.group(1)
                        agent_name = agent_match.group(2)
                        opinion = agent_match.group(3)
                        
                        self.current_agent = agent_name
                        self.pending_message = ""
                        self.pending_reasoning = ""
                        
                        # Get timestamp from record
                        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
                        
                        # Store the basic round data
                        self.monitor.add_round_data(
                            round_num=self.current_round,
                            agent_name=agent_name,
                            opinion=opinion,
                            timestamp=timestamp
                        )
                        
            # 3. Capture agent message content
            elif "├─ Message:" in message and self.current_agent and self.current_round:
                # Format: "├─ Message: The proposed approach aligns well with viral content strategies..."
                msg_content = message.split("├─ Message:", 1)[1].strip()
                self.pending_message = msg_content
                
            # 4. Capture agent reasoning
            elif "├─ Reasoning:" in message and self.current_agent and self.current_round:
                # Format: "├─ Reasoning: Effective comedy requires precise timing and clear narrative structure..."
                reasoning_content = message.split("├─ Reasoning:", 1)[1].strip()
                self.pending_reasoning = reasoning_content
                
            # 5. Capture timestamp and finalize agent data
            elif "└─ Time:" in message and self.current_agent and self.current_round:
                # Format: "└─ Time: 06:36:34"
                time_content = message.split("└─ Time:", 1)[1].strip()
                
                # Now we have complete data for this agent in this round
                if self.monitor.current_discussion in self.monitor.discussions:
                    discussion = self.monitor.discussions[self.monitor.current_discussion]
                    if self.current_round in discussion['rounds'] and self.current_agent in discussion['rounds'][self.current_round]['agents']:
                        # Update the agent data with complete message and reasoning
                        discussion['rounds'][self.current_round]['agents'][self.current_agent]['message'] = self.pending_message
                        discussion['rounds'][self.current_round]['agents'][self.current_agent]['reasoning'] = self.pending_reasoning
                        discussion['rounds'][self.current_round]['agents'][self.current_agent]['timestamp'] = time_content
                
                # Reset pending data
                self.pending_message = ""
                self.pending_reasoning = ""
                
            # 6. Capture consensus updates
            elif "📊 Enhanced consensus level:" in message:
                # Format: "📊 Enhanced consensus level: 0.50"
                try:
                    consensus_str = message.split("📊 Enhanced consensus level:")[1].strip()
                    consensus_level = float(consensus_str)
                    if self.current_round:
                        self.monitor.update_consensus(self.current_round, consensus_level)
                except (IndexError, ValueError):
                    pass
                    
            elif "📊 Consensus level:" in message:
                # Format: "📊 Consensus level: 0.75 (Round 3)"
                try:
                    consensus_match = re.search(r'📊 Consensus level: ([\d.]+)', message)
                    round_match = re.search(r'\(Round (\d+)\)', message)
                    
                    if consensus_match:
                        consensus_level = float(consensus_match.group(1))
                        round_num = int(round_match.group(1)) if round_match else self.current_round
                        if round_num:
                            self.monitor.update_consensus(round_num, consensus_level)
                except (ValueError, AttributeError):
                    pass
                    
            # 7. Detect discussion completion
            elif "🎯 Discussion completed:" in message:
                # Format: "🎯 Discussion completed: 0.75 consensus in 3 rounds (148.7s)"
                try:
                    consensus_match = re.search(r'(\d+\.\d+) consensus', message)
                    rounds_match = re.search(r'(\d+) rounds', message)
                    time_match = re.search(r'\(([\d.]+)s\)', message)
                    
                    if consensus_match:
                        final_consensus = float(consensus_match.group(1))
                        duration = time_match.group(1) if time_match else "unknown"
                        self.monitor.complete_discussion(final_consensus, f"{duration}s")
                except (ValueError, AttributeError):
                    pass
                    
            # 8. Detect consensus reached
            elif "✅ Enhanced consensus reached!" in message:
                # Update status but don't complete yet (wait for final stats)
                if self.monitor.current_discussion in self.monitor.discussions:
                    self.monitor.discussions[self.monitor.current_discussion]['status'] = 'consensus_reached'
                    
        except Exception as e:
            # Don't let logging errors break the system
            logger.error(f"Error in enhanced AgentDiscussionHandler: {e}")
            pass

# Create global visualizer instance
global_visualizer = RealTimeAgentDiscussionMonitor()

class UnifiedVideoApp:
    """Main application class for unified video generation"""
    
    def __init__(self):
        # Load API key
        self.api_key = self._load_api_key()
        
    def _load_api_key(self) -> str:
        """Load Google API key from environment"""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            # Try to load from config file
            config_file = os.path.join(os.path.dirname(__file__), 'config', 'config.py')
            if os.path.exists(config_file):
                import sys
                sys.path.append(os.path.dirname(config_file))
                try:
                    import config
                    api_key = getattr(config, 'GOOGLE_API_KEY', None)
                except ImportError:
                    pass
        
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables or config file")
        
        return api_key
    
    def generate_video_with_realtime_updates(self, mission: str, duration: int, platform: str, 
                                           category: str, use_discussions: bool) -> Any:
        """Generate video with real-time discussion updates"""
        try:
            # Import the enhanced orchestrator
            from src.agents.enhanced_orchestrator_with_19_agents import create_enhanced_orchestrator_with_19_agents
            from src.models.video_models import VideoCategory, Platform
            
            # Convert string values to enums
            video_category = VideoCategory(category)
            target_platform = Platform(platform)
            
            # Start real-time monitoring
            global_visualizer.start_monitoring()
            
            # Create the orchestrator
            orchestrator = create_enhanced_orchestrator_with_19_agents(
                api_key=self.api_key,
                mission=mission,
                category=video_category,
                platform=target_platform,
                duration=duration,
                enable_discussions=use_discussions
            )
            
            # Generate the video
            result = orchestrator.generate_viral_video(
                mission=mission,
                category=video_category,
                platform=target_platform,
                duration=duration,
                discussion_mode=use_discussions
            )
            
            # Stop monitoring
            global_visualizer.stop_monitoring()
            
            return result
            
        except Exception as e:
            # Stop monitoring on error
            global_visualizer.stop_monitoring()
            raise e
    
    def _simulate_discussions(self):
        """Simulate agent discussions for testing"""
        agents = [
            ("StoryWeaver", "Analyzing mission requirements..."),
            ("DialogueMaster", "Crafting compelling dialogue..."),
            ("AudioMaster", "Optimizing audio levels..."),
            ("VisualDirector", "Designing visual composition..."),
            ("QualityGuard", "Performing quality checks...")
        ]
        
        for i, (agent, message) in enumerate(agents):
            time.sleep(2)
            global_visualizer.add_round_data(
                global_visualizer.pending_agent_data.get('round_num', 0),
                agent, 
                "AGREE", 
                message, 
                "", # No reasoning for simulation
                datetime.now().strftime("%H:%M:%S")
            )
            global_visualizer.update_consensus(global_visualizer.pending_agent_data.get('round_num', 0), 1.0) # Simulate consensus
            global_visualizer.pending_agent_data = {} # Clear pending data
    
    def get_discussion_updates(self):
        """Get current discussion updates"""
        return global_visualizer.generate_discussion_html()

def get_enhanced_css():
    """Get enhanced CSS for the improved discussion UI with better text visibility"""
    return """
    <style>
        /* Global text color override - ENHANCED VISIBILITY */
        .discussions-container * {
            color: #1e293b !important;
        }
        
        /* Specific overrides for elements that should have different colors */
        .discussion-summary, .discussion-summary * {
            color: white !important;
        }
        
        .consensus-badge, .rounds-badge, .time-badge {
            color: rgba(255, 255, 255, 0.95) !important;
            background: rgba(0, 0, 0, 0.3) !important;
            padding: 4px 8px !important;
            border-radius: 4px !important;
            font-weight: bold !important;
        }
        
        /* Main container styling */
        .discussions-container {
            max-width: 100%;
            margin: 0 auto;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #ffffff !important;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            color: #1e293b !important;
            border: 2px solid #e2e8f0;
        }
        
        .discussions-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e2e8f0;
        }
        
        .discussions-header h2 {
            margin: 0;
            color: #1e293b !important;
            font-size: 1.5rem;
            font-weight: 600;
        }
        
        .discussions-stats {
            display: flex;
            gap: 15px;
            font-size: 0.9rem;
        }
        
        .discussions-stats span {
            padding: 6px 12px;
            border-radius: 6px;
            background: #e2e8f0;
            color: #1e293b !important;
            font-weight: 600;
        }
        
        /* Discussion accordion styling */
        .discussion-accordion {
            margin-bottom: 20px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            background: white;
            overflow: hidden;
        }
        
        .discussion-summary {
            padding: 15px 20px;
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            color: white !important;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .discussion-summary:hover {
            background: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%);
        }
        
        .discussion-title {
            font-size: 1.1rem;
            color: white !important;
        }
        
        .discussion-meta {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .discussion-content {
            padding: 20px;
            background: #f8fafc;
            color: #1e293b !important;
        }
        
        .discussion-info {
            margin-bottom: 20px;
            padding: 15px;
            background: white;
            border-radius: 6px;
            border-left: 4px solid #3b82f6;
            color: #1e293b !important;
        }
        
        .participants {
            margin-bottom: 10px;
            font-size: 0.9rem;
            color: #475569 !important;
            font-weight: 500;
        }
        
        .consensus-progress {
            margin-top: 10px;
        }
        
        .consensus-bar {
            width: 100%;
            height: 8px;
            background: #e2e8f0;
            border-radius: 4px;
            overflow: hidden;
        }
        
        .consensus-fill {
            height: 100%;
            background: linear-gradient(90deg, #ef4444 0%, #f97316 50%, #10b981 100%);
            transition: width 0.3s ease;
        }
        
        /* Round accordion styling */
        .round-accordion {
            margin-bottom: 15px;
            border: 2px solid #d1d5db;
            border-radius: 6px;
            background: white;
            overflow: hidden;
        }
        
        .round-summary {
            padding: 12px 16px;
            background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: 600;
            color: #1e293b !important;
            transition: all 0.2s ease;
        }
        
        .round-summary:hover {
            background: linear-gradient(135deg, #e5e7eb 0%, #d1d5db 100%);
        }
        
        .round-title {
            font-size: 1rem;
            color: #1e293b !important;
        }
        
        .round-meta {
            display: flex;
            gap: 8px;
            align-items: center;
            font-size: 0.8rem;
        }
        
        .round-consensus {
            font-weight: 600;
            color: #059669 !important;
        }
        
        .round-time {
            color: #6b7280 !important;
        }
        
        .round-content {
            padding: 15px;
            background: #f9fafb;
        }
        
        /* Team accordion styling */
        .team-accordion {
            margin-bottom: 12px;
            border: 2px solid #e5e7eb;
            border-radius: 6px;
            background: white;
            overflow: hidden;
        }
        
        .team-summary {
            padding: 10px 14px;
            background: #f8fafc;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: 600;
            color: #1e293b !important;
            border-left: 4px solid #d1d5db;
            transition: all 0.2s ease;
        }
        
        .team-summary:hover {
            background: #f1f5f9;
        }
        
        .team-title {
            font-size: 0.9rem;
            color: #1e293b !important;
        }
        
        .team-content {
            padding: 12px;
            background: #fefefe;
        }
        
        /* Agent accordion styling */
        .agent-accordion {
            margin-bottom: 8px;
            border: 2px solid #f3f4f6;
            border-radius: 4px;
            background: white;
            overflow: hidden;
        }
        
        .agent-summary {
            padding: 8px 12px;
            background: #fafafa;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.9rem;
            border-left: 3px solid #e5e7eb;
            transition: all 0.2s ease;
        }
        
        .agent-summary:hover {
            background: #f5f5f5;
        }
        
        .agent-info {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .agent-name {
            font-weight: 600;
            color: #1e293b !important;
        }
        
        .agent-opinion {
            font-size: 0.8rem;
            font-weight: 500;
            padding: 2px 6px;
            border-radius: 4px;
            background: rgba(0, 0, 0, 0.1);
        }
        
        .agent-time {
            font-size: 0.8rem;
            color: #6b7280 !important;
        }
        
        .agent-content {
            padding: 12px;
            background: #fdfdfd;
        }
        
        .agent-message, .agent-reasoning {
            margin-bottom: 10px;
        }
        
        .agent-message strong, .agent-reasoning strong {
            color: #1e293b !important;
            font-weight: 600;
        }
        
        .agent-message p, .agent-reasoning p {
            margin: 5px 0 0 0;
            color: #374151 !important;
            line-height: 1.5;
        }
        
        /* Waiting state styling */
        .waiting-message {
            text-align: center;
            padding: 40px 20px;
            background: white;
            border-radius: 8px;
            border: 2px dashed #d1d5db;
            color: #1e293b !important;
        }
        
        .waiting-message p {
            margin: 10px 0;
            color: #6b7280 !important;
        }
        
        .waiting-message ul {
            text-align: left;
            display: inline-block;
            margin: 20px 0;
        }
        
        .waiting-message li {
            margin: 5px 0;
            color: #4b5563 !important;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .discussions-header {
                flex-direction: column;
                gap: 10px;
            }
            
            .discussions-stats {
                flex-wrap: wrap;
                justify-content: center;
            }
            
            .discussion-summary, .round-summary, .team-summary, .agent-summary {
                flex-direction: column;
                gap: 8px;
                text-align: center;
            }
            
            .discussion-meta, .round-meta, .agent-info {
                flex-wrap: wrap;
                justify-content: center;
            }
        }
        
        /* Animation for opening/closing */
        details[open] > summary {
            margin-bottom: 0;
        }
        
        details > summary {
            transition: margin-bottom 0.3s ease;
        }
        
        /* Custom scrollbar */
        .discussions-container::-webkit-scrollbar {
            width: 8px;
        }
        
        .discussions-container::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 4px;
        }
        
        .discussions-container::-webkit-scrollbar-thumb {
            background: #c1c1c1;
            border-radius: 4px;
        }
        
        .discussions-container::-webkit-scrollbar-thumb:hover {
            background: #a8a8a8;
        }
        
        /* Error message styling */
        .error-message {
            background: #fef2f2 !important;
            border: 2px solid #fecaca !important;
            color: #dc2626 !important;
            padding: 15px !important;
            border-radius: 8px !important;
            margin: 10px 0 !important;
        }
        
        .error-message h3 {
            color: #dc2626 !important;
            margin-top: 0 !important;
        }
        
        .error-message p {
            color: #dc2626 !important;
        }
    </style>
    """

def create_unified_realtime_interface():
    """Create the unified Gradio interface"""
    
    # Custom CSS for the interface
    css = """
    .header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .header h1 {
        font-size: 2.5em;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .input-section {
        background: #f8f9fa;
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 2px solid #e9ecef;
    }
    
    .force-generation-section {
        background: #e8f4fd;
        padding: 20px;
        border-radius: 8px;
        margin: 15px 0;
        border: 1px solid #bee5eb;
    }
    
    .force-generation-title {
        font-weight: bold;
        color: #0c5460;
        margin-bottom: 15px;
        font-size: 16px;
    }
    
    .continuous-section {
        background: #fff3cd;
        padding: 15px;
        border-radius: 6px;
        margin: 10px 0;
        border: 1px solid #ffeaa7;
    }
    
    .discussions-container {
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
    
    .discussions-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid #333;
    }
    
    .discussions-stats {
        display: flex;
        gap: 15px;
        font-size: 12px;
    }
    
    .total-discussions { color: #f39c12; }
    .active-discussions { color: #3498db; }
    .completed-discussions { color: #2ecc71; }
    
    .discussion-accordion {
        border: 1px solid #444;
        border-radius: 8px;
        margin-bottom: 10px;
        background: rgba(255, 255, 255, 0.05);
    }
    
    .discussion-summary {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 15px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    
    .discussion-summary:hover {
        background-color: rgba(255, 255, 255, 0.08);
    }
    
    .discussion-title {
        font-weight: bold;
        font-size: 16px;
        color: #f39c12;
    }
    
    .discussion-meta {
        display: flex;
        gap: 10px;
        font-size: 12px;
        color: #7f8c8d;
    }
    
    .consensus-badge {
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: bold;
        color: white;
    }
    
    .rounds-badge {
        background-color: #3498db;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: bold;
        color: white;
    }
    
    .time-badge {
        background-color: #2ecc71;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: bold;
        color: white;
    }
    
    .discussion-content {
        padding: 15px;
        border-top: 1px solid #444;
        background: rgba(255, 255, 255, 0.02);
    }
    
    .discussion-info {
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 1px dashed #555;
    }
    
    .participants {
        font-size: 14px;
        color: #ecf0f1;
        margin-bottom: 8px;
    }
    
    .consensus-progress {
        height: 10px;
        background-color: #2c3e50;
        border-radius: 5px;
        overflow: hidden;
    }
    
    .consensus-fill {
        height: 100%;
        background: linear-gradient(90deg, #e74c3c 0%, #f39c12 50%, #2ecc71 100%);
        border-radius: 5px;
        transition: width 0.5s ease;
    }
    
    .round-accordion {
        border: 1px solid #444;
        border-radius: 8px;
        margin-bottom: 10px;
        background: rgba(255, 255, 255, 0.03);
    }
    
    .round-summary {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 15px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    
    .round-summary:hover {
        background-color: rgba(255, 255, 255, 0.06);
    }
    
    .round-title {
        font-weight: bold;
        font-size: 15px;
        color: #f39c12;
    }
    
    .round-meta {
        display: flex;
        gap: 10px;
        font-size: 12px;
        color: #7f8c8d;
    }
    
    .round-consensus {
        font-weight: bold;
        font-size: 13px;
    }
    
    .team-accordion {
        border: 1px solid #444;
        border-radius: 8px;
        margin-bottom: 10px;
        background: rgba(255, 255, 255, 0.03);
    }
    
    .team-summary {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 15px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    
    .team-summary:hover {
        background-color: rgba(255, 255, 255, 0.06);
    }
    
    .team-title {
        font-weight: bold;
        font-size: 15px;
        color: #f39c12;
    }
    
    .team-content {
        padding: 10px 20px;
        border-top: 1px dashed #555;
    }
    
    .agent-accordion {
        border: 1px solid #444;
        border-radius: 8px;
        margin-bottom: 10px;
        background: rgba(255, 255, 255, 0.03);
    }
    
    .agent-summary {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 15px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    
    .agent-summary:hover {
        background-color: rgba(255, 255, 255, 0.06);
    }
    
    .agent-info {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 14px;
        color: #ecf0f1;
    }
    
    .agent-name {
        font-weight: bold;
        font-size: 14px;
    }
    
    .agent-opinion {
        font-weight: bold;
        font-size: 13px;
        padding: 3px 8px;
        border-radius: 6px;
    }
    
    .agent-time {
        font-size: 11px;
        color: #7f8c8d;
    }
    
    .agent-content {
        padding: 10px 20px;
        border-top: 1px dashed #555;
    }
    
    .agent-message {
        margin-bottom: 8px;
        padding-bottom: 8px;
        border-bottom: 1px dashed #555;
    }
    
    .agent-message strong {
        font-weight: bold;
        color: #f39c12;
    }
    
    .agent-message p {
        color: #ecf0f1;
        line-height: 1.3;
        margin-top: 5px;
    }
    
    .agent-reasoning {
        margin-top: 10px;
        padding-top: 10px;
        border-top: 1px dashed #555;
    }
    
    .agent-reasoning strong {
        font-weight: bold;
        color: #f39c12;
    }
    
    .agent-reasoning p {
        color: #ecf0f1;
        line-height: 1.3;
        margin-top: 5px;
    }
    
    .waiting-message {
        text-align: center;
        color: #7f8c8d;
        padding: 40px 20px;
        font-style: italic;
    }
    
    .log-container {
        background: #1a1a1a;
        color: #00ff00;
        font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
        font-size: 12px;
        line-height: 1.3;
        border: 1px solid #333;
        border-radius: 6px;
        padding: 10px;
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
                        label="📱 Target Platform",
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
                
                # Force Generation Controls
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
                
                # Video Orientation Controls
                orientation_mode = gr.Radio(
                    choices=[
                        ("�� AI Agents Decide", "auto"),
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
                
            with gr.Column(scale=2):
                # Live AI Agent Discussions with enhanced CSS
                discussion_output = gr.HTML(
                    value=get_enhanced_css() + global_visualizer.generate_discussion_html(),
                    elem_classes=["discussions-container"]
                )
                
                # Raw Log Viewer
                with gr.Accordion("📋 Raw Agent Logs", open=False):
                    log_output = gr.Textbox(
                        label="Live Agent Discussion Logs",
                        value="Click 'Refresh Logs' to see recent agent discussions...",
                        interactive=False,
                        lines=15,
                        max_lines=15,
                        elem_classes=["log-container"]
                    )
                    
                    refresh_logs_btn = gr.Button("🔄 Refresh Logs", size="sm")
                
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
        def update_orientation_info(mode):
            if mode == "auto":
                return '<div class="orientation-indicator">🤖 AI agents will analyze platform and content to decide optimal orientation</div>'
            elif mode == "portrait":
                return '<div class="orientation-indicator">📱 Forced to Portrait (9:16) - Best for TikTok, Instagram Stories</div>'
            elif mode == "landscape":
                return '<div class="orientation-indicator">🖥️ Forced to Landscape (16:9) - Best for YouTube, traditional video</div>'
            elif mode == "square":
                return '<div class="orientation-indicator">⬜ Forced to Square (1:1) - Best for Instagram Posts</div>'
        
        def refresh_agent_logs():
            """Refresh and display recent agent logs"""
            try:
                log_file = os.path.join(os.path.dirname(__file__), 'logs', f'viral_video_{datetime.now().strftime("%Y%m%d")}.log')
                if os.path.exists(log_file):
                    # Get last 50 lines and filter for agent discussions
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        recent_lines = lines[-100:]  # Get last 100 lines
                        
                        # Filter for agent discussion lines
                        agent_lines = []
                        for line in recent_lines:
                            if any(keyword in line for keyword in ['💬', '📊', 'Round', '🔄', '🎭', 'consensus']):
                                agent_lines.append(line.strip())
                        
                        # Return last 30 agent discussion lines
                        return '\n'.join(agent_lines[-30:]) if agent_lines else "No recent agent discussions found"
                else:
                    return f"Log file not found: {log_file}"
            except Exception as e:
                return f"Error reading logs: {str(e)}"
        
        orientation_mode.change(
            update_orientation_info,
            inputs=[orientation_mode],
            outputs=[orientation_info]
        )
        
        refresh_logs_btn.click(
            refresh_agent_logs,
            inputs=[],
            outputs=[log_output]
        )
        
        # Main generation function
        def generate_video_with_force_controls(mission, category, platform, duration, force_mode, orientation_mode):
            try:
                if not mission or not mission.strip():
                    return (
                        "❌ Please enter a mission statement",
                        get_enhanced_css() + '<div class="discussions-container">❌ No mission provided</div>',
                        "No mission provided - no logs available",
                        gr.update(visible=False),
                        gr.update(visible=False),
                        gr.update(interactive=True)  # Re-enable button
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
                        get_enhanced_css() + '<div class="discussions-container">❌ Invalid category or platform</div>',
                        f"Error: {e}",
                        gr.update(visible=False),
                        gr.update(visible=False),
                        gr.update(interactive=True)  # Re-enable button
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
                    continuous_generation=False,
                    video_orientation=video_orientation
                )
                
                # Add initial status message
                global_visualizer.pending_agent_data = {
                    'name': 'System',
                    'message': f"🚀 Starting video generation with {force_mode} mode...",
                    'opinion': 'NEUTRAL',
                    'reasoning': '',
                    'round_num': 0,
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                }
                
                # Generate the video
                result = orchestrator.generate_viral_video(
                    mission=mission,
                    category=video_category,
                    platform=target_platform,
                    duration=duration,
                    discussion_mode=True
                )
                
                # Stop monitoring
                global_visualizer.stop_monitoring()
                
                # Get final discussion HTML and logs with enhanced CSS
                final_discussion_html = get_enhanced_css() + global_visualizer.generate_discussion_html()
                final_logs = refresh_agent_logs()
                
                if result and hasattr(result, 'file_path') and os.path.exists(result.file_path):
                    final_status = f"✅ Video generated successfully!\n📁 File: {result.file_path}\n📊 Success rate: {getattr(result, 'success_rate', 1.0):.1%}"
                    
                    # Add completion message
                    global_visualizer.complete_discussion(1.0, "N/A")
                    final_discussion_html = global_visualizer.generate_discussion_html()
                    
                    return (
                        final_status,
                        final_discussion_html,
                        final_logs,
                        gr.update(value=result.file_path, visible=True),
                        gr.update(value=result.file_path, visible=True),
                        gr.update(interactive=True)  # Re-enable button
                    )
                else:
                    global_visualizer.pending_agent_data = {
                        'name': 'System',
                        'message': "❌ Video generation failed",
                        'opinion': 'NEUTRAL',
                        'reasoning': '',
                        'round_num': 0,
                        'timestamp': datetime.now().strftime("%H:%M:%S")
                    }
                    final_discussion_html = get_enhanced_css() + global_visualizer.generate_discussion_html()
                    
                    return (
                        "❌ Video generation failed",
                        final_discussion_html,
                        final_logs,
                        gr.update(visible=False),
                        gr.update(visible=False),
                        gr.update(interactive=True)  # Re-enable button
                    )
                    
            except Exception as e:
                # Stop monitoring on error
                global_visualizer.stop_monitoring()
                error_msg = f"❌ Error: {str(e)}"
                error_html = f'<div class="discussions-container">❌ Generation failed: {str(e)}</div>'
                error_logs = refresh_agent_logs()
                
                global_visualizer.pending_agent_data = {
                    'name': 'System',
                    'message': f"❌ Error: {str(e)}",
                    'opinion': 'NEUTRAL',
                    'reasoning': '',
                    'round_num': 0,
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                }
                error_html = get_enhanced_css() + global_visualizer.generate_discussion_html()
                
                return (
                    error_msg,
                    error_html,
                    error_logs,
                    gr.update(visible=False),
                    gr.update(visible=False),
                    gr.update(interactive=True)  # Re-enable button
                )
        
        def start_generation_with_button_disable(*args):
            """Wrapper to disable button during generation"""
            return generate_video_with_force_controls(*args)
        
        generate_btn.click(
            start_generation_with_button_disable,
            inputs=[
                mission_input,
                category_dropdown,
                platform_dropdown,
                duration_slider,
                force_mode,
                orientation_mode
            ],
            outputs=[
                status_output,
                discussion_output,
                log_output,
                video_output,
                download_output,
                generate_btn  # Add button to outputs to control its state
            ]
        ).then(
            lambda: gr.update(interactive=False),  # Disable button immediately
            outputs=[generate_btn]
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