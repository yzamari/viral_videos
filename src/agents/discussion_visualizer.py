"""
AI Agent Discussion Visualizer
Provides enhanced logging and visualization for multi-agent discussions
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class DiscussionPhase(Enum):
    """Discussion phases for visualization"""
    STARTING = "🚀 Starting"
    IN_PROGRESS = "🔄 In Progress"
    CONSENSUS_BUILDING = "🤝 Building Consensus"
    COMPLETED = "✅ Completed"
    FAILED = "❌ Failed"


@dataclass
class AgentContribution:
    """Individual agent contribution tracking"""
    agent_name: str
    message: str
    timestamp: datetime
    round_number: int
    vote: Optional[str] = None
    key_points: Optional[List[str]] = None


class DiscussionVisualizer:
    """Enhanced visualization and logging for AI agent discussions"""

    def __init__(self, session_dir: str):
        self.session_dir = session_dir
        self.discussions_dir = os.path.join(session_dir, "agent_discussions")
        os.makedirs(self.discussions_dir, exist_ok=True)

        # Real-time tracking
        self.current_discussion: Optional[Dict[str, Any]] = None
        self.discussion_history: List[Dict[str, Any]] = []
        self.start_time: Optional[float] = None

        # Visual elements
        self.agent_emojis = {
            "SyncMaster": "🎯",
            "TrendMaster": "📈",
            "StoryWeaver": "📝",
            "VisionCraft": "🎨",
            "PixelForge": "⚡",
            "AudioMaster": "🎵",
            "CutMaster": "✂️"
        }

        # Console formatting
        self.colors = {
            "header": "\033[95m",
            "blue": "\033[94m",
            "cyan": "\033[96m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "red": "\033[91m",
            "bold": "\033[1m",
            "underline": "\033[4m",
            "end": "\033[0m"
        }

    def start_discussion_visualization(self, topic: str, participating_agents: List[str],
                                       max_rounds: int, target_consensus: float):
        """Start visualizing a new discussion"""
        self.current_discussion = {
            "topic": topic,
            "participating_agents": participating_agents,
            "max_rounds": max_rounds,
            "target_consensus": target_consensus,
            "start_time": datetime.now(),
            "phase": DiscussionPhase.STARTING,
            "contributions": [],
            "consensus_history": [],
            "current_round": 0,
            "duration": 0.0,
            "final_consensus": 0.0,
            "total_rounds": 0,
            "end_time": None
        }
        self.start_time = time.time()

        # Print beautiful header
        self._print_discussion_header(topic, participating_agents, max_rounds, target_consensus)

    def log_agent_contribution(self, agent_name: str, message: str, round_number: int,
                               vote: Optional[str] = None, reasoning: Optional[str] = None):
        """Log and visualize an agent contribution"""
        if not self.current_discussion:
            return

        contribution = AgentContribution(
            agent_name=agent_name,
            message=message,
            timestamp=datetime.now(),
            round_number=round_number,
            vote=vote
        )

        self.current_discussion["contributions"].append(contribution)
        self.current_discussion["current_round"] = round_number
        self.current_discussion["phase"] = DiscussionPhase.IN_PROGRESS

        # Real-time console output
        self._print_agent_contribution(agent_name, message, round_number, vote, reasoning)

    def update_consensus(self, consensus_level: float, round_number: int):
        """Update and visualize consensus progress"""
        if not self.current_discussion:
            return

        self.current_discussion["consensus_history"].append({
            "round": round_number,
            "consensus": consensus_level,
            "timestamp": datetime.now()
        })

        target_consensus = self.current_discussion.get("target_consensus", 0.7)
        if consensus_level >= target_consensus:
            self.current_discussion["phase"] = DiscussionPhase.CONSENSUS_BUILDING

        # Visual consensus progress
        self._print_consensus_update(consensus_level, round_number)

    def complete_discussion(self, final_consensus: float, total_rounds: int,
                            key_insights: List[str], final_decision: Dict):
        """Complete discussion visualization"""
        if not self.current_discussion:
            return

        self.current_discussion["phase"] = DiscussionPhase.COMPLETED
        self.current_discussion["final_consensus"] = final_consensus
        self.current_discussion["total_rounds"] = total_rounds
        self.current_discussion["end_time"] = datetime.now()
        
        if self.start_time is not None:
            self.current_discussion["duration"] = time.time() - self.start_time
        else:
            self.current_discussion["duration"] = 0.0

        # Print completion summary
        self._print_discussion_completion(final_consensus, total_rounds, key_insights)

        # Save detailed visualization
        self._save_discussion_visualization()

        # Add to history
        self.discussion_history.append(self.current_discussion.copy())
        self.current_discussion = None

    def _print_discussion_header(self, topic: str, agents: List[str], max_rounds: int, target_consensus: float):
        """Print beautiful discussion header"""
        header = f"""
{self.colors['bold']}{self.colors['cyan']}╔══════════════════════════════════════════════════════════════════════════════════════╗
║                           🤖 AI AGENT DISCUSSION STARTING                           ║
╚══════════════════════════════════════════════════════════════════════════════════════╝{self.colors['end']}

{self.colors['bold']}📋 Topic:{self.colors['end']} {self.colors['yellow']}{topic}{self.colors['end']}
{self.colors['bold']}👥 Participants:{self.colors['end']} {self._format_agent_list(agents)}
{self.colors['bold']}🎯 Target Consensus:{self.colors['end']} {self.colors['green']}{target_consensus:.0%}{self.colors['end']}
{self.colors['bold']}🔄 Max Rounds:{self.colors['end']} {self.colors['blue']}{max_rounds}{self.colors['end']}
{self.colors['bold']}⏰ Started:{self.colors['end']} {datetime.now().strftime('%H:%M:%S')}

{self.colors['bold']}{self.colors['underline']}Discussion Progress:{self.colors['end']}
        """
        print(header)
        logger.info(f"🎭 Starting discussion: {topic}")

    def _print_agent_contribution(self, agent_name: str, message: str, round_number: int,
                                  vote: Optional[str], reasoning: Optional[str]):
        """Print formatted agent contribution"""
        emoji = self.agent_emojis.get(agent_name, "🤖")
        vote_indicator = ""

        if vote:
            vote_colors = {
                "agree": self.colors['green'],
                "disagree": self.colors['red'],
                "neutral": self.colors['yellow']}
            vote_color = vote_colors.get(vote, self.colors['end'])
            vote_indicator = f" {vote_color}[{vote.upper()}]{self.colors['end']}"

        # Truncate long messages for console
        display_message = message[:120] + "..." if len(message) > 120 else message

        contribution = f"""
{self.colors['bold']}Round {round_number}{self.colors['end']} │ {emoji} {self.colors['cyan']}{agent_name}{self.colors['end']}{vote_indicator}
├─ {self.colors['bold']}Message:{self.colors['end']} {display_message}"""

        if reasoning:
            reasoning_short = reasoning[:80] + "..." if len(reasoning) > 80 else reasoning
            contribution += f"\n├─ {self.colors['bold']}Reasoning:{self.colors['end']} {reasoning_short}"

        contribution += f"\n└─ {self.colors['blue']}Time:{self.colors['end']} {datetime.now().strftime('%H:%M:%S')}\n"

        print(contribution)
        logger.info(f"💬 {agent_name}: {message[:100]}...")

    def _print_consensus_update(self, consensus_level: float, round_number: int):
        """Print consensus progress bar"""
        if not self.current_discussion:
            return
            
        target = self.current_discussion.get("target_consensus", 0.7)
        progress = min(consensus_level / target, 1.0)
        bar_length = 30
        filled_length = int(bar_length * progress)

        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        percentage = consensus_level * 100

        status_color = self.colors['green'] if consensus_level >= target else self.colors['yellow']
        status_text = "CONSENSUS REACHED!" if consensus_level >= target else "Building consensus..."

        consensus_display = f"""
{self.colors['bold']}📊 Consensus Progress:{self.colors['end']} Round {round_number}
{status_color}[{bar}] {percentage:.1f}%{self.colors['end']} │ Target: {target:.0%}
{self.colors['bold']}{status_color}{status_text}{self.colors['end']}
        """

        print(consensus_display)
        logger.info(f"📊 Consensus level: {consensus_level:.2f} (Round {round_number})")

    def _print_discussion_completion(self, final_consensus: float, total_rounds: int, key_insights: List[str]):
        """Print discussion completion summary"""
        if not self.current_discussion or self.start_time is None:
            return
            
        duration = time.time() - self.start_time
        target_consensus = self.current_discussion.get("target_consensus", 0.7)
        status_emoji = "✅" if final_consensus >= target_consensus else "⚠️"
        participating_agents = self.current_discussion.get("participating_agents", [])

        completion = f"""
{self.colors['bold']}{self.colors['green']}╔══════════════════════════════════════════════════════════════════════════════════════╗
║                          {status_emoji} DISCUSSION COMPLETED                                    ║
╚══════════════════════════════════════════════════════════════════════════════════════╝{self.colors['end']}

{self.colors['bold']}🎯 Final Consensus:{self.colors['end']} {self.colors['green']}{final_consensus:.1%}{self.colors['end']}
{self.colors['bold']}🔄 Total Rounds:{self.colors['end']} {self.colors['blue']}{total_rounds}{self.colors['end']}
{self.colors['bold']}⏱️ Duration:{self.colors['end']} {self.colors['cyan']}{duration:.1f}s{self.colors['end']}
{self.colors['bold']}👥 Participants:{self.colors['end']} {len(participating_agents)} agents

{self.colors['bold']}💡 Key Insights:{self.colors['end']}"""

        for i, insight in enumerate(key_insights[:3], 1):
            insight_short = insight[:100] + "..." if len(insight) > 100 else insight
            completion += f"\n   {i}. {insight_short}"

        completion += f"\n\n{self.colors['bold']}📁 Full details saved to:{self.colors['end']} agent_discussions/\n"

        print(completion)
        logger.info(f"🎯 Discussion completed: {final_consensus:.2f} consensus in {total_rounds} rounds ({duration:.1f}s)")

    def _format_agent_list(self, agents: List[str]) -> str:
        """Format agent list with emojis"""
        formatted = []
        for agent in agents:
            emoji = self.agent_emojis.get(agent, "🤖")
            formatted.append(f"{emoji} {agent}")
        return " • ".join(formatted)

    def _sanitize_filename(self, text: str, max_length: int = 50) -> str:
        """
        Sanitize text for safe filename usage
        
        Args:
            text: Input text to sanitize
            max_length: Maximum filename length (default 50)
            
        Returns:
            Safe filename string
        """
        if not text:
            return "unnamed"
            
        # Remove/replace problematic characters
        safe_text = text.replace(" ", "_").replace("/", "_").replace("\\", "_")
        safe_text = safe_text.replace(":", "_").replace("*", "_").replace("?", "_")
        safe_text = safe_text.replace('"', "_").replace("<", "_").replace(">", "_")
        safe_text = safe_text.replace("|", "_").replace(".", "_").replace(",", "_")
        safe_text = safe_text.replace("(", "_").replace(")", "_").replace("[", "_")
        safe_text = safe_text.replace("]", "_").replace("{", "_").replace("}", "_")
        safe_text = safe_text.replace("'", "_").replace("`", "_").replace("~", "_")
        safe_text = safe_text.replace("!", "_").replace("@", "_").replace("#", "_")
        safe_text = safe_text.replace("$", "_").replace("%", "_").replace("^", "_")
        safe_text = safe_text.replace("&", "_").replace("+", "_").replace("=", "_")
        
        # Convert to lowercase and remove multiple underscores
        safe_text = safe_text.lower()
        while "__" in safe_text:
            safe_text = safe_text.replace("__", "_")
            
        # Trim to max length
        if len(safe_text) > max_length:
            safe_text = safe_text[:max_length]
            
        # Remove trailing underscore
        safe_text = safe_text.rstrip("_")
        
        # Ensure it's not empty
        if not safe_text:
            safe_text = "unnamed"
            
        return safe_text

    def _save_discussion_visualization(self):
        """Save detailed discussion visualization"""
        if not self.current_discussion:
            return

        # Create visualization report
        viz_data = {
            "discussion_summary": {
                "topic": self.current_discussion["topic"],
                "participants": self.current_discussion["participating_agents"],
                "duration_seconds": self.current_discussion["duration"],
                "total_rounds": self.current_discussion["total_rounds"],
                "final_consensus": self.current_discussion["final_consensus"],
                "target_consensus": self.current_discussion["target_consensus"],
                "success": self.current_discussion["final_consensus"] >= self.current_discussion["target_consensus"]
            },
            "round_by_round": self._generate_round_breakdown(),
            "consensus_progression": self.current_discussion["consensus_history"],
            "agent_contributions": self._generate_agent_stats(),
            "timeline": self._generate_timeline()
        }

        # Save visualization with safe filename
        topic_safe = self._sanitize_filename(self.current_discussion["topic"])
        viz_file = os.path.join(self.discussions_dir, f"visualization_{topic_safe}.json")

        with open(viz_file, 'w') as f:
            json.dump(viz_data, f, indent=2, default=str)

        # Also create a markdown report
        try:
            self._create_markdown_report(viz_data, topic_safe)
        except Exception as e:
            logger.warning(f"Failed to create markdown report: {e}")

    def _generate_round_breakdown(self) -> List[Dict]:
        """Generate round-by-round breakdown"""
        if not self.current_discussion:
            return []
            
        rounds = {}
        for contrib in self.current_discussion["contributions"]:
            round_num = contrib.round_number
            if round_num not in rounds:
                rounds[round_num] = {
                    "round": round_num,
                    "contributions": [],
                    "votes": {"agree": 0, "disagree": 0, "neutral": 0}
                }

            rounds[round_num]["contributions"].append({
                "agent": contrib.agent_name,
                "message": contrib.message,
                "vote": contrib.vote,
                "timestamp": contrib.timestamp
            })

            if contrib.vote:
                rounds[round_num]["votes"][contrib.vote] = rounds[round_num]["votes"].get(contrib.vote, 0) + 1

        return list(rounds.values())

    def _generate_agent_stats(self) -> Dict:
        """Generate agent participation statistics"""
        if not self.current_discussion:
            return {}
            
        stats = {}
        for contrib in self.current_discussion["contributions"]:
            agent = contrib.agent_name
            if agent not in stats:
                stats[agent] = {
                    "total_contributions": 0,
                    "votes": {"agree": 0, "disagree": 0, "neutral": 0},
                    "avg_message_length": 0,
                    "first_contribution": None,
                    "last_contribution": None
                }

            stats[agent]["total_contributions"] += 1
            if contrib.vote:
                stats[agent]["votes"][contrib.vote] += 1

            if not stats[agent]["first_contribution"]:
                stats[agent]["first_contribution"] = contrib.timestamp
            stats[agent]["last_contribution"] = contrib.timestamp

        return stats

    def _generate_timeline(self) -> List[Dict]:
        """Generate discussion timeline"""
        if not self.current_discussion:
            return []
            
        timeline = []
        start_time = self.current_discussion.get("start_time")
        end_time = self.current_discussion.get("end_time")

        # Add start event
        if start_time:
            timeline.append({
                "timestamp": start_time,
                "event": "discussion_started",
                "description": f"Discussion '{self.current_discussion['topic']}' started"
            })

        # Add contributions
        for contrib in self.current_discussion["contributions"]:
            timeline.append({
                "timestamp": contrib.timestamp,
                "event": "agent_contribution",
                "agent": contrib.agent_name,
                "round": contrib.round_number,
                "description": f"{contrib.agent_name} contributed in round {contrib.round_number}"
            })

        # Add consensus updates
        for consensus in self.current_discussion["consensus_history"]:
            timeline.append({
                "timestamp": consensus["timestamp"],
                "event": "consensus_update",
                "round": consensus["round"],
                "consensus_level": consensus["consensus"],
                "description": f"Consensus updated to {consensus['consensus']:.1%} in round {consensus['round']}"
            })

        # Add end event
        if end_time:
            timeline.append({
                "timestamp": end_time,
                "event": "discussion_completed",
                "description": f"Discussion completed with {self.current_discussion['final_consensus']:.1%} consensus"
            })

        return sorted(timeline, key=lambda x: x["timestamp"])

    def _create_markdown_report(self, viz_data: Dict, topic_safe: str):
        """Create a markdown report for the discussion"""
        report_file = os.path.join(self.discussions_dir, f"report_{topic_safe}.md")

        with open(report_file, 'w') as f:
            f.write(f"# AI Agent Discussion Report\n\n")
            f.write(f"**Topic:** {viz_data['discussion_summary']['topic']}\n\n")
            f.write(f"**Duration:** {viz_data['discussion_summary']['duration_seconds']:.1f} seconds\n\n")
            f.write(f"**Final Consensus:** {viz_data['discussion_summary']['final_consensus']:.1%}\n\n")
            f.write(f"**Success:** {'✅ Yes' if viz_data['discussion_summary']['success'] else '❌ No'}\n\n")

            f.write("## Participants\n\n")
            for agent in viz_data['discussion_summary']['participants']:
                emoji = self.agent_emojis.get(agent, "🤖")
                f.write(f"- {emoji} **{agent}**\n")

            f.write("\n## Round-by-Round Breakdown\n\n")
            for round_data in viz_data['round_by_round']:
                f.write(f"### Round {round_data['round']}\n\n")
                for contrib in round_data['contributions']:
                    emoji = self.agent_emojis.get(contrib['agent'], "🤖")
                    vote = f" [{contrib['vote'].upper()}]" if contrib['vote'] else ""
                    f.write(f"**{emoji} {contrib['agent']}{vote}:** {contrib['message'][:200]}...\n\n")

            f.write("## Consensus Progression\n\n")
            for consensus in viz_data['consensus_progression']:
                f.write(f"- **Round {consensus['round']}:** {consensus['consensus']:.1%}\n")

        logger.info(f"📊 Discussion report saved: {report_file}")

    def generate_session_summary(self) -> Dict:
        """Generate overall session summary"""
        if not self.discussion_history:
            return {}

        total_discussions = len(self.discussion_history)
        avg_consensus = sum(d["final_consensus"] for d in self.discussion_history) / total_discussions
        total_duration = sum(d["duration"] for d in self.discussion_history)

        summary = {
            "session_overview": {
                "total_discussions": total_discussions,
                "average_consensus": avg_consensus,
                "total_duration_seconds": total_duration,
                "success_rate": len([d for d in self.discussion_history if d["final_consensus"] >= d["target_consensus"]]) / total_discussions
            },
            "discussion_topics": [d["topic"] for d in self.discussion_history],
            "most_active_agents": self._get_most_active_agents(),
            "consensus_trends": [d["final_consensus"] for d in self.discussion_history]
        }

        return summary

    def _get_most_active_agents(self) -> Dict:
        """Get most active agents across all discussions"""
        agent_activity = {}

        for discussion in self.discussion_history:
            for contrib in discussion["contributions"]:
                agent = contrib.agent_name
                if agent not in agent_activity:
                    agent_activity[agent] = 0
                agent_activity[agent] += 1

        return dict(sorted(agent_activity.items(), key=lambda x: x[1], reverse=True))

