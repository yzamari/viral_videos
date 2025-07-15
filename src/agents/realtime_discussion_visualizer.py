"""
Real-Time Discussion Visualizer for 19 AI Agents
Provides live updates and visualization of agent discussions
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass

from ..utils.logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class AgentActivity:
    """Real-time agent activity data"""
    agent_name: str
    message: str
    timestamp: datetime
    round_num: int
    vote: Optional[str] = None
    reasoning: Optional[str] = None

@dataclass
class PhaseStatus:
    """Discussion phase status"""
    phase_name: str
    participating_agents: List[str]
    current_round: int
    consensus_level: float
    start_time: datetime
    status: str  # "active", "completed", "pending"

class RealTimeDiscussionVisualizer:
    """
    Real-time visualizer for AI agent discussions
    Provides live updates and monitoring capabilities
    """

    def __init__(
        self,
        session_dir: str,
        update_callback: Optional[Callable] = None):
        self.session_dir = session_dir
        self.update_callback = update_callback

        # Real-time data
        self.current_phase: Optional[PhaseStatus] = None
        self.agent_activities: List[AgentActivity] = []
        self.phase_history: List[PhaseStatus] = []
        self.consensus_history: Dict[str, List[float]] = {}

        # Agent status tracking
        self.agent_status = {}
        self.active_agents = set()

        # Performance metrics
        self.start_time = datetime.now()
        self.total_messages = 0
        self.average_consensus = 0.0

        logger.info("🎬 Real-time discussion visualizer initialized")

    def start_discussion_phase(self, phase_name: str, agent_names: List[str],
                               max_rounds: int, target_consensus: float):
        """Start a new discussion phase with real-time tracking"""
        self.current_phase = PhaseStatus(
            phase_name=phase_name,
            participating_agents=agent_names,
            current_round=0,
            consensus_level=0.0,
            start_time=datetime.now(),
            status="active"
        )

        # Update agent status
        self.active_agents = set(agent_names)
        for agent in agent_names:
            self.agent_status[agent] = "active"

        # Initialize consensus tracking
        self.consensus_history[phase_name] = []

        logger.info(f"🎭 Started real-time tracking for phase: {phase_name}")
        logger.info(f"👥 Active agents: {', '.join(agent_names)}")

        # Trigger UI update
        if self.update_callback:
            self.update_callback()

    def log_agent_contribution(self, agent_name: str, message: str, round_num: int,
                               vote: Optional[str] = None, reasoning: Optional[str] = None):
        """Log real-time agent contribution"""
        activity = AgentActivity(
            agent_name=agent_name,
            message=message,
            timestamp=datetime.now(),
            round_num=round_num,
            vote=vote,
            reasoning=reasoning
        )

        self.agent_activities.append(activity)
        self.total_messages += 1

        # Update agent status
        self.agent_status[agent_name] = "speaking"

        # Keep only last 50 activities for performance
        if len(self.agent_activities) > 50:
            self.agent_activities = self.agent_activities[-50:]

        logger.info(f"💬 {agent_name} contributed in round {round_num}")

        # Trigger UI update
        if self.update_callback:
            self.update_callback()

    def update_consensus(self, consensus_level: float, round_num: int):
        """Update consensus level with real-time tracking"""
        if self.current_phase:
            self.current_phase.consensus_level = consensus_level
            self.current_phase.current_round = round_num

            # Track consensus history
            phase_name = self.current_phase.phase_name
            if phase_name not in self.consensus_history:
                self.consensus_history[phase_name] = []

            self.consensus_history[phase_name].append(consensus_level)

            # Update average consensus
            all_consensus = []
            for phase_consensus in self.consensus_history.values():
                all_consensus.extend(phase_consensus)

            if all_consensus:
                self.average_consensus = sum(all_consensus) / len(all_consensus)

        logger.info(f"📊 Consensus updated: {consensus_level:.1%} (Round {round_num})")

        # Trigger UI update
        if self.update_callback:
            self.update_callback()

    def complete_discussion_phase(self, consensus_level: float, round_count: int,
                                  key_insights: List[str], final_decision: Dict):
        """Complete current discussion phase"""
        if self.current_phase:
            self.current_phase.status = "completed"
            self.current_phase.consensus_level = consensus_level
            self.current_phase.current_round = round_count

            # Add to history
            self.phase_history.append(self.current_phase)

            # Reset agent status
            for agent in self.active_agents:
                self.agent_status[agent] = "completed"

            self.active_agents.clear()

            logger.info(f"✅ Completed phase: {self.current_phase.phase_name}")
            logger.info(f"📊 Final consensus: {consensus_level:.1%} in {round_count} rounds")

            self.current_phase = None

        # Trigger UI update
        if self.update_callback:
            self.update_callback()

    def get_real_time_status(self) -> Dict[str, Any]:
        """Get current real-time status for UI updates"""
        status = {
            "current_phase": None,
            "active_agents": list(self.active_agents),
            "agent_status": self.agent_status.copy(),
            "recent_activities": [],
            "consensus_progress": 0.0,
            "total_messages": self.total_messages,
            "average_consensus": self.average_consensus,
            "session_duration": (datetime.now() - self.start_time).total_seconds()
        }

        # Current phase info
        if self.current_phase:
            status["current_phase"] = {
                "name": self.current_phase.phase_name,
                "round": self.current_phase.current_round,
                "consensus": self.current_phase.consensus_level,
                "participating_agents": self.current_phase.participating_agents,
                "duration": (datetime.now() - self.current_phase.start_time).total_seconds()
            }
            status["consensus_progress"] = self.current_phase.consensus_level

        # Recent activities (last 10)
        status["recent_activities"] = [
            {
                "agent": activity.agent_name,
                "message": activity.message[:100] + "..." if len(activity.message) > 100 else activity.message,
                "timestamp": activity.timestamp.strftime("%H:%M:%S"),
                "round": activity.round_num,
                "vote": activity.vote
            }
            for activity in self.agent_activities[-10:]
        ]

        return status

    def generate_agent_grid_html(self, all_agents: Dict[str, Dict]) -> str:
        """Generate HTML for real-time agent grid"""
        categories = {
            "Foundation": [],
            "Script": [],
            "Audio": [],
            "Typography": [],
            "Visual": [],
            "Platform": [],
            "Quality": []
        }

        # Group agents by category with real-time status
        for agent_name, agent_info in all_agents.items():
            category = agent_info.get("category", "Foundation")
            status = self.agent_status.get(agent_name, "idle")

            agent_data = {
                "name": agent_name,
                "icon": agent_info.get("icon", "🤖"),
                "status": status
            }

            if category in categories:
                categories[category].append(agent_data)

        html = """
        <div style="display: grid; grid-template-columns: repeat(
            auto-fit,
            minmax(280px, 1fr));
                   gap: 0.8rem; margin: 1rem 0;">
        """

        for category, agents in categories.items():
            if not agents:
                continue

            # Category color based on activity
            active_count = sum(
                1 for agent in agents if agent["status"] in ["active",
                "speaking"])
            if active_count > 0:
                bg_color = "linear-gradient(135deg, #4CAF50 0%, #45a049 100%)"  # Green for active
            else:
                bg_color = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"  # Blue for idle

            html += """
            <div style="background: {bg_color}; color: white; padding: 0.8rem;
                       border-radius: 8px; min-height: 100px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h4 style="margin: 0 0 0.5rem 0; font-size: 0.9em;">
                    {category} ({len(agents)})
                    {f'🟢 {active_count} Active' if active_count > 0 else '⚪ Idle'}
                </h4>
            """

            for agent in agents:
                status = agent["status"]
                icon = agent["icon"]
                name = agent["name"]

                # Status indicators
                if status == "active":
                    status_indicator = "🟢"
                    status_text = "ACTIVE"
                    pulse_animation = "animation: pulse 2s infinite;"
                elif status == "speaking":
                    status_indicator = "🟡"
                    status_text = "SPEAKING"
                    pulse_animation = "animation: pulse 1s infinite;"
                elif status == "completed":
                    status_indicator = "✅"
                    status_text = "DONE"
                    pulse_animation = ""
                else:
                    status_indicator = "⚪"
                    status_text = "IDLE"
                    pulse_animation = ""

                html += """
                <div style="display: flex; align-items: center; margin: 0.2rem 0;
                           padding: 0.3rem; background: rgba(255,255,255,0.15);
                           border-radius: 4px; font-size: 0.8em; {pulse_animation}">
                    <span style="font-size: 1em; margin-right: 0.4rem;">{icon}</span>
                    <span style="flex: 1; font-weight: 500;">{name}</span>
                    <span style="font-size: 0.7em;">
                        {status_indicator} {status_text}
                    </span>
                </div>
                """

            html += "</div>"

        html += """
        </div>
        <style>
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        </style>
        """

        return html

    def generate_activity_feed_html(self) -> str:
        """Generate HTML for real-time activity feed"""
        if not self.agent_activities:
            return """
            <div style="text-align: center; padding: 2rem; color: #666;">
                <h4>🤖 Waiting for Agent Activity...</h4>
                <p>Agents will appear here when discussions begin</p>
            </div>
            """

        html = """
        <div style="max-height: 400px; overflow-y: auto; background: #f8f9fa;
                   padding: 1rem; border-radius: 8px;">
            <h4 style="margin-top: 0; color: #333;">📝 Live Agent Activity Feed</h4>
        """

        # Show last 15 activities in reverse order (newest first)
        recent_activities = self.agent_activities[-15:]
        for activity in reversed(recent_activities):
            # Vote color coding
            vote_color = "#28a745" if activity.vote == "agree" else "#dc3545" if activity.vote == "disagree" else "#6c757d"
            vote_text = activity.vote.upper() if activity.vote else "NEUTRAL"

            html += """
            <div style="margin: 0.5rem 0; padding: 0.7rem; background: white;
                       border-radius: 6px; border-left: 4px solid {vote_color};
                       box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 0.3rem;">
                    <strong style="color: #333;">[{activity.timestamp.strftime("%H:%M:%S")}]
                    Round {activity.round_num} - {activity.agent_name}</strong>
                    <span style="background: {vote_color}; color: white; padding: 0.1rem 0.3rem;
                                border-radius: 3px; font-size: 0.7em; font-weight: bold;">
                        {vote_text}
                    </span>
                </div>
                <div style="color: #555; font-size: 0.9em; line-height: 1.4;">
                    {activity.message[:150] +
                        '...' if len(activity.message) > 150 else activity.message}
                </div>
            </div>
            """

        html += "</div>"
        return html

    def generate_progress_dashboard_html(self) -> str:
        """Generate HTML for progress dashboard"""
        status = self.get_real_time_status()

        html = """
        <div style="background: white; padding: 1.5rem; border-radius: 8px;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        """

        if status["current_phase"]:
            phase = status["current_phase"]
            progress_percent = int(phase["consensus"] * 100)

            html += """
            <h3 style="margin-top: 0; color: #333;">📊 Current Phase: {phase["name"]}</h3>
            <div style="margin: 1rem 0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span><strong>Round:</strong> {phase["round"]}</span>
                    <span><strong>Consensus:</strong> {progress_percent}%</span>
                    <span><strong>Duration:</strong> {phase["duration"]:.0f}s</span>
                </div>
                <div style="background: #e9ecef; border-radius: 10px; overflow: hidden; height: 25px;">
                    <div style="background: linear-gradient(90deg, #28a745, #20c997);
                               width: {progress_percent}%; height: 100%;
                               display: flex; align-items: center; justify-content: center;
                               color: white; font-weight: bold; font-size: 0.8em;
                               transition: width 0.5s ease;">
                        {progress_percent}% Consensus
                    </div>
                </div>
                <div style="margin-top: 0.5rem;">
                    <strong>Active Agents ({len(phase["participating_agents"])}):</strong>
                    {', '.join(phase["participating_agents"])}
                </div>
            </div>
            """
        else:
            html += """
            <h3 style="margin-top: 0; color: #666;">⏸️ No Active Discussion Phase</h3>
            <p style="color: #666;">Waiting for next phase to begin...</p>
            """

        # Session statistics
        html += """
        <div style="display: grid; grid-template-columns: repeat(
            auto-fit,
            minmax(120px, 1fr));
                   gap: 1rem; margin-top: 1.5rem; padding-top: 1rem;
                   border-top: 1px solid #dee2e6;">
            <div style="text-align: center;">
                <div style="font-size: 1.5em; font-weight: bold; color: #007bff;">
                    {status["total_messages"]}
                </div>
                <div style="font-size: 0.8em; color: #666;">Total Messages</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 1.5em; font-weight: bold; color: #28a745;">
                    {status["average_consensus"]:.0%}
                </div>
                <div style="font-size: 0.8em; color: #666;">Avg Consensus</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 1.5em; font-weight: bold; color: #6f42c1;">
                    {len(self.phase_history)}
                </div>
                <div style="font-size: 0.8em; color: #666;">Phases Done</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 1.5em; font-weight: bold; color: #fd7e14;">
                    {status["session_duration"]:.0f}s
                </div>
                <div style="font-size: 0.8em; color: #666;">Session Time</div>
            </div>
        </div>
        """

        html += "</div>"
        return html

    def save_real_time_session_data(self):
        """Save real-time session data for analysis"""
        session_data = {
            "session_start": self.start_time.isoformat(),
            "total_messages": self.total_messages,
            "average_consensus": self.average_consensus,
            "phase_history": [
                {
                    "name": phase.phase_name,
                    "participants": phase.participating_agents,
                    "final_consensus": phase.consensus_level,
                    "rounds": phase.current_round,
                    "duration": (datetime.now() - phase.start_time).total_seconds(),
                    "status": phase.status
                }
                for phase in self.phase_history
            ],
            "consensus_history": self.consensus_history,
            "final_status": self.get_real_time_status()
        }

        # Ensure session directory exists
        os.makedirs(self.session_dir, exist_ok=True)

        # Save to session directory
        session_file = os.path.join(self.session_dir, "realtime_session_data.json")
        try:
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2, default=str)
            logger.info(f"💾 Real-time session data saved: {session_file}")
        except Exception as e:
            logger.error(f"Error saving real-time session data: {e}")
