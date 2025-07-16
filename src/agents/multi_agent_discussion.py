"""
Multi-Agent Discussion System
Collaborative decision-making with specialized AI agents
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
try:
    import google.generativeai as genai
except ImportError:
    # Fallback for when google.generativeai is not available
    genai = None

from .discussion_visualizer import DiscussionVisualizer
from ..services.monitoring_service import MonitoringService
from ..utils.logging_config import get_logger

logger = get_logger(__name__)
class AgentRole(Enum):
    """Available agent roles for discussions"""
    TREND_ANALYST = "trend_analyst"
    SCRIPT_WRITER = "script_writer"
    DIRECTOR = "director"
    VIDEO_GENERATOR = "video_generator"
    SOUNDMAN = "soundman"
    EDITOR = "editor"
    ORCHESTRATOR = "orchestrator"

@dataclass
class AgentMessage:
    """Message from an AI agent during discussion"""
    agent_role: AgentRole
    agent_name: str
    message: str
    timestamp: datetime
    message_id: str
    reasoning: Optional[str] = None
    suggestions: Optional[List[str]] = None
    concerns: Optional[List[str]] = None
    vote: Optional[str] = None

@dataclass
class DiscussionTopic:
    """Represents a topic for agent discussion"""
    topic_id: str
    title: str
    description: str
    context: Dict[str, Any]
    required_decisions: List[str]
    max_rounds: int = 10
    min_consensus: float = 0.7

@dataclass
class DiscussionResult:
    """Final result of agent discussion"""
    topic_id: str
    decision: Dict[str, Any]
    consensus_level: float
    total_rounds: int
    participating_agents: List[str]
    key_insights: List[str]
    alternative_approaches: List[str]

class MultiAgentDiscussionSystem:
    """
    Multi-agent discussion system for collaborative decision-making

    This system enables multiple AI agents with different specializations
    to discuss and reach consensus on complex topics.
    """

    def __init__(self, api_key: str, session_id: str,
                 enable_visualization: bool = True):
        self.api_key = api_key
        self.session_id = session_id
        self.enable_visualization = enable_visualization

        # Initialize Gemini client
        if genai:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None
            logger.warning("Google Generative AI not available")

        # ENHANCED: Use session manager for proper file organization
        from ..utils.session_manager import session_manager
        self.session_manager = session_manager

        # Create discussions directory
        session_dir_name = session_id if session_id.startswith('session_') else f"session_{session_id}"
        self.discussions_dir = os.path.join(
            "outputs", session_dir_name, "agent_discussions")
        os.makedirs(self.discussions_dir, exist_ok=True)
        
        # Session management
        session_dir = f"outputs/{session_dir_name}"
        self.session_managed = session_id is not None
        if self.session_managed:
            os.makedirs(session_dir, exist_ok=True)

        # Initialize monitoring
        self.monitoring_service = MonitoringService(session_id)

        # Initialize visualizer
        if enable_visualization:
            if hasattr(self.session_manager, 'current_session') and self.session_manager.current_session:
                session_dir = self.session_manager.get_session_path()
            else:
                # Fix to avoid double session_ prefix
                session_dir = f"outputs/{session_id}" if session_id.startswith("session_") else f"outputs/session_{session_id}"

            self.visualizer = DiscussionVisualizer(session_dir)
        else:
            self.visualizer = None

        # Agent personalities and expertise
        self.agent_personalities = self._initialize_agent_personalities()

        logger.info("🎭 Multi-agent discussion system initialized")
        logger.info(f"   Session: {session_id}")
        logger.info(f"   Agents available: {len(self.agent_personalities)}")
        logger.info(f"   Session-managed discussions: {'✅' if hasattr(self.session_manager, 'current_session') and self.session_manager.current_session else '❌'}")

    def _initialize_agent_personalities(self) -> Dict[AgentRole, Dict[str, Any]]:
        """Initialize agent personalities and expertise"""
        return {
            AgentRole.TREND_ANALYST: {
                "name": "TrendMaster",
                "personality": ("Data-driven, analytical, focused on viral patterns "
                                "and audience engagement metrics"),
                "expertise": ["viral trends", "audience analysis", "platform optimization",
                              "engagement metrics"],
                "decision_style": "Evidence-based with statistical backing"
            },
            AgentRole.SCRIPT_WRITER: {
                "name": "StoryWeaver",
                "personality": ("Creative, narrative-focused, emphasizes storytelling "
                                "and emotional connection"),
                "expertise": ["storytelling", "narrative structure", "emotional hooks",
                              "viral content patterns"],
                "decision_style": "Creative with focus on narrative impact"
            },
            AgentRole.DIRECTOR: {
                "name": "VisionCraft",
                "personality": ("Visual storyteller, focused on cinematic quality "
                                "and scene composition"),
                "expertise": ["visual storytelling", "scene composition", "cinematic techniques",
                              "continuity"],
                "decision_style": "Artistic with technical precision"
            },
            AgentRole.VIDEO_GENERATOR: {
                "name": "PixelForge",
                "personality": ("Technical expert, focused on AI video generation "
                                "capabilities and limitations"),
                "expertise": ["AI video generation", "VEO-2 capabilities", "technical constraints",
                              "quality optimization"],
                "decision_style": "Technical feasibility with quality focus"
            },
            AgentRole.SOUNDMAN: {
                "name": "AudioMaster",
                "personality": ("Audio specialist, focused on sound design "
                                "and voice optimization"),
                "expertise": ["audio production", "voice synthesis", "sound design",
                              "audio-visual sync"],
                "decision_style": "Audio-centric with synchronization priority"
            },
            AgentRole.EDITOR: {
                "name": "CutMaster",
                "personality": ("Post-production expert, focused on final assembly "
                                "and polish"),
                "expertise": ["video editing", "post-production", "final assembly",
                              "quality control"],
                "decision_style": "Quality-focused with practical execution"
            },
            AgentRole.ORCHESTRATOR: {
                "name": "SyncMaster",
                "personality": ("Coordination expert, focused on overall workflow "
                                "and agent synchronization"),
                "expertise": ["workflow coordination", "agent synchronization",
                              "resource management", "timeline optimization"],
                "decision_style": "Holistic with coordination priority"
            }
        }

    def _sanitize_filename(self, text: str, max_length: int = 50) -> str:
        """
        Sanitize text for safe filename usage:
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
        safe_text = safe_text.replace(
            ":",
            "_").replace(
            "*",
            "_").replace(
            "?",
            "_")
        safe_text = safe_text.replace(
            '"',
            "_").replace(
            "<",
            "_").replace(
            ">",
            "_")
        safe_text = safe_text.replace(
            "|",
            "_").replace(
            ".",
            "_").replace(
            ",",
            "_")
        safe_text = safe_text.replace(
            "(", "_").replace(
            ")", "_").replace(
            "[", "_")
        safe_text = safe_text.replace(
            "]", "_").replace(
            "{", "_").replace(
            "}", "_")
        safe_text = safe_text.replace(
            "'",
            "_").replace(
            "`",
            "_").replace(
            "~",
            "_")
        safe_text = safe_text.replace(
            "!",
            "_").replace(
            "@",
            "_").replace(
            "#",
            "_")
        safe_text = safe_text.replace(
            "$",
            "_").replace(
            "%",
            "_").replace(
            "^",
            "_")
        safe_text = safe_text.replace(
            "&",
            "_").replace(
            "+",
            "_").replace(
            "=",
            "_")

        # Convert to lowercase and remove multiple underscores
        safe_text = safe_text.lower()
        while "__" in safe_text:
            safe_text = safe_text.replace("__", "_")

        # Trim to max length
        if len(safe_text) > max_length:
            safe_text = safe_text[:max_length]

        # Remove trailing underscore
        safe_text = safe_text.rstrip("_")

        # Ensure it's not empty'
        if not safe_text:
            safe_text = "unnamed"

        return safe_text

    def start_discussion(self,
            topic: DiscussionTopic,
            participating_agents: List[AgentRole]) -> DiscussionResult:
        """
        Start a multi-agent discussion on a specific topic

        Args:
            topic: The discussion topic and context
            participating_agents: List of agent roles to participate

        Returns:
            DiscussionResult with final decision and insights
        """
        logger.info(f"🎭 Starting agent discussion: {topic.title}")
        agent_names = [self.agent_personalities[agent]['name']
                       for agent in participating_agents]
        logger.info(f"👥 Participating agents: {', '.join(agent_names)}")

        # ENHANCED: Start visualization
        if self.visualizer:
            self.visualizer.start_discussion_visualization(
                topic.title, agent_names, topic.max_rounds, topic.min_consensus
            )

        # Initialize discussion
        discussion_id = str(uuid.uuid4())[:8]
        discussion_log = []
        current_round = 0
        consensus_reached = False

        # Create discussion file with safe filename
        safe_topic_id = self._sanitize_filename(topic.topic_id)
        discussion_file = os.path.join(
            self.discussions_dir,
            f"discussion_{safe_topic_id}_{discussion_id}.json")

        # Initial context message
        context_message = self._create_context_message(topic)
        discussion_log.append(context_message)

        # Discussion rounds:
        while current_round < topic.max_rounds and not consensus_reached:
            current_round += 1
            logger.info(
                f"🔄 Discussion round {current_round}/{topic.max_rounds}")

            round_messages = []

            # Each agent contributes to the discussion
            for agent_role in participating_agents:
                agent_message = self._get_agent_response(
                    agent_role, topic, discussion_log, current_round
                )
                round_messages.append(agent_message)
                discussion_log.append(agent_message)

                # ENHANCED: Log to visualizer
                agent_name = self.agent_personalities[agent_role]['name']
                if self.visualizer:
                    self.visualizer.log_agent_contribution(
                        agent_name, agent_message.message, current_round, getattr(
                            agent_message, 'vote', None), getattr(
                            agent_message, 'reasoning', None))

                # Log agent contribution
                logger.info(
                    f"💬 {agent_name}: {agent_message.message[:100]}...")

            # Check for consensus
            consensus_level = self._calculate_consensus(round_messages)
            logger.info(f"📊 Consensus level: {consensus_level:.2f}")

            # ENHANCED: Update visualizer
            if self.visualizer:
                self.visualizer.update_consensus(
                    consensus_level, current_round)

            if consensus_level >= topic.min_consensus:
                consensus_reached = True
                logger.info("✅ Consensus reached!")

            # Save discussion progress
            self._save_discussion_progress(
                discussion_file,
                topic,
                discussion_log,
                current_round,
                consensus_level)

        # Generate final decision
        final_decision = self._generate_final_decision(
            topic, discussion_log, participating_agents)

        # Extract key insights
        key_insights = self._extract_key_insights(discussion_log)

        # Create result
        result = DiscussionResult(
            topic_id=topic.topic_id,
            decision=final_decision,
            consensus_level=consensus_level,
            total_rounds=current_round,
            participating_agents=[self.agent_personalities[agent]['name']
                                  for agent in participating_agents],
            key_insights=key_insights,
            alternative_approaches=self._extract_alternatives(discussion_log)
        )

        # ENHANCED: Complete visualization
        if self.visualizer:
            self.visualizer.complete_discussion(
                consensus_level, current_round, key_insights, final_decision
            )

        # Save final result
        self._save_final_result(discussion_file, result)

        logger.info(
            f"🎯 Discussion completed: {result.consensus_level:.2f} consensus "
            f"in {current_round} rounds")
        return result

    def _create_context_message(self, topic: DiscussionTopic) -> Dict[str, Any]:
        """Create initial context message for the discussion"""
        return {
            "type": "context",
            "topic_id": topic.topic_id,
            "title": topic.title,
            "description": topic.description,
            "context": topic.context,
            "required_decisions": topic.required_decisions,
            "timestamp": datetime.now().isoformat()
        }

    def _get_agent_response(self,
            agent_role: AgentRole,
            topic: DiscussionTopic,
            discussion_log: List[Dict],
            round_num: int) -> AgentMessage:
        """Get response from a specific agent with improved error handling"""
        agent_info = self.agent_personalities[agent_role]

        # Create discussion context for the agent
        discussion_context = self._format_discussion_for_agent(
            discussion_log, agent_role)

        # Create agent-specific prompt
        prompt = self._create_agent_prompt(
            agent_info, topic, discussion_context, round_num)

        # Retry logic for quota errors
        max_retries = 3
        base_delay = 1.0
        for attempt in range(max_retries):
            try:
                # Get response from Gemini model
                if self.model:
                    response = self.model.generate_content(prompt)
                    response_text = response.text
                else:
                    response_text = "Model not available"

                # Parse agent response
                agent_response = self._parse_agent_response(
                    response_text, agent_role)

                return AgentMessage(
                    agent_role=agent_role,
                    agent_name=agent_info['name'],
                    message=agent_response.get('message', ''),
                    timestamp=datetime.now(),
                    message_id=str(uuid.uuid4())[:8],
                    reasoning=agent_response.get('reasoning'),
                    suggestions=agent_response.get('suggestions', []),
                    concerns=agent_response.get('concerns', []),
                    vote=agent_response.get('vote')
                )

            except Exception as e:
                error_message = str(e)

                # Check if this is a quota error (429 status):
                if "429" in error_message or "quota" in error_message.lower():
                    if attempt < max_retries - 1:
                        # Exponential backoff delay
                        delay = base_delay * (2 ** attempt)
                        logger.warning(
                            f"Quota error for {agent_info['name']}, retrying in {delay:.1f}s (attempt {attempt + 1}/{max_retries})")
                        import time
                        time.sleep(delay)
                        continue
                    else:
                        logger.error(
                            f"❌ Failed to get response from {agent_info['name']} after {max_retries} attempts: {e}")
                        # Return quota-specific fallback response
                        return AgentMessage(
                            agent_role=agent_role,
                            agent_name=agent_info['name'],
                            message=f"I need more information to provide a detailed response about {topic.title}.",
                            timestamp=datetime.now(),
                            message_id=str(
                                uuid.uuid4())[
                                :8],
                            reasoning="API quota limit reached, unable to generate detailed response",
                            vote="neutral")
                else:
                    # Non-quota error, log and return fallback
                    logger.error(
                        f"Error getting response from {agent_info['name']}: {e}")
                    return AgentMessage(
                        agent_role=agent_role,
                        agent_name=agent_info['name'],
                        message=f"I need more information to provide a detailed response about {topic.title}.",
                        timestamp=datetime.now(),
                        message_id=str(
                            uuid.uuid4())[
                            :8],
                        vote="neutral")

        # This should never be reached, but just in case
        return AgentMessage(
            agent_role=agent_role,
            agent_name=agent_info['name'],
            message=f"I need more information to provide a detailed response about {topic.title}.",
            timestamp=datetime.now(),
            message_id=str(
                uuid.uuid4())[
                :8],
            vote="neutral")

    def _create_agent_prompt(self, agent_info: Dict, topic: DiscussionTopic,
                             discussion_context: str, round_num: int) -> str:
        """Create a prompt for a specific agent"""

        # Convert context to JSON-serializable format
        serializable_context = {}
        for key, value in topic.context.items():
            try:
                # Test if value is JSON serializable
                json.dumps(value)
                serializable_context[key] = value
            except (TypeError, ValueError):
                # Convert non-serializable objects to string representation
                serializable_context[key] = str(value)

        # Extract the mission/topic from context for emphasis
        mission = serializable_context.get('mission', 'Unknown Mission')
        platform = serializable_context.get('platform', 'Unknown Platform')
        duration = serializable_context.get('duration', 'Unknown Duration')

        return f"""
You are {agent_info['name']}, an AI agent with the following characteristics:
PERSONALITY: {agent_info['personality']}
EXPERTISE: {', '.join(agent_info['expertise'])}
DECISION STYLE: {agent_info['decision_style']}

🎯 VIDEO MISSION: "{mission}"
📱 PLATFORM: {platform}
⏱️ DURATION: {duration} seconds

DISCUSSION TOPIC: {topic.title}
DESCRIPTION: {topic.description}

FULL CONTEXT: {json.dumps(serializable_context, indent=2)}

REQUIRED DECISIONS: {', '.join(topic.required_decisions)}

DISCUSSION ROUND: {round_num}

PREVIOUS DISCUSSION:
{discussion_context}

🚨 CRITICAL INSTRUCTIONS:
- You MUST discuss the specific mission: "{mission}"
- Focus on how to create the best video for this exact topic
- Consider the platform ({platform}) and duration ({duration}s) requirements
- Provide specific, actionable advice for THIS mission only
- Do NOT discuss generic topics or unrelated business scenarios

Your task is to contribute to this discussion by providing your expert perspective on how to create the best possible video for the mission "{mission}".

Please respond in the following JSON format:
{{
    "message": "Your main contribution about creating a video for '{mission}' (2-3 sentences)",
    "reasoning": "Your reasoning for this approach to '{mission}' (1-2 sentences)",
    "suggestions": ["Specific suggestion for '{mission}' video", "Another '{mission}' suggestion"],
    "concerns": ["Concern about '{mission}' video if any"],
    "vote": "agree/disagree/neutral"
}}

Focus specifically on:
1. How to make "{mission}" engaging for {platform}
2. Best practices for {duration}-second videos about "{mission}"
3. Viral potential of "{mission}" content
4. Technical considerations for "{mission}" video production

Be concise but insightful about THIS SPECIFIC MISSION: "{mission}"
"""

    def _parse_agent_response(self, response_text: str,
                              agent_role: AgentRole) -> Dict[str, Any]:
        """Parse agent response from Gemini model"""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                # Fallback parsing
                return {
                    "message": response_text[:200],
                    "reasoning": "Generated response without structured format",
                    "suggestions": [],
                    "concerns": [],
                    "vote": "neutral"
                }
        except Exception as e:
            logger.warning(f"Error parsing agent response: {e}")
            return {
                "message": response_text[:200] if response_text else "Unable to generate response",
                "reasoning": "Response parsing failed",
                "suggestions": [],
                "concerns": [],
                "vote": "neutral"
            }

    def _format_discussion_for_agent(self,
            discussion_log: List,
            current_agent: AgentRole) -> str:
        """Format discussion history for agent context"""
        formatted = []

        # Last 6 entries to keep context manageable:
        for entry in discussion_log[-6:]:
            # Handle dictionary entries (context messages)
            if isinstance(entry, dict):
                if entry.get('type') == 'context':
                    continue
                agent_name = entry.get('agent_name', 'Unknown')
                message = entry.get('message', '')
                if message:
                    formatted.append(f"{agent_name}: {message}")

            # Handle AgentMessage objects
            elif hasattr(entry, 'agent_name') and hasattr(entry, 'message'):
                formatted.append(f"{entry.agent_name}: {entry.message}")

        return "\n".join(formatted) if formatted else "No previous discussion"

    def _calculate_consensus(self,
            round_messages: List[AgentMessage]) -> float:
        """Calculate consensus level from agent votes"""
        if not round_messages:
            return 0.0

        votes = [msg.vote for msg in round_messages if msg.vote]
        if not votes:
            return 0.0

        agree_count = votes.count('agree')
        total_votes = len(votes)

        return agree_count / total_votes if total_votes > 0 else 0.0

    def _generate_final_decision(self,
                                 topic: DiscussionTopic,
                                 discussion_log: List,
                                 participating_agents: List[AgentRole]) -> Dict[str,
                                                                                Any]:
        """Generate final decision based on discussion"""
        # Extract key points from discussion
        key_points = []
        suggestions = []
        concerns = []

        for entry in discussion_log:
            if isinstance(entry, dict):
                if entry.get('reasoning'):
                    key_points.append(entry.get('reasoning'))
                if entry.get('suggestions'):
                    entry_suggestions = entry.get('suggestions', [])
                    if isinstance(entry_suggestions, list):
                        for suggestion in entry_suggestions:
                            if isinstance(suggestion, str):
                                suggestions.append(suggestion)
                if entry.get('concerns'):
                    entry_concerns = entry.get('concerns', [])
                    if isinstance(entry_concerns, list):
                        for concern in entry_concerns:
                            if isinstance(concern, str):
                                concerns.append(concern)
            elif hasattr(entry, 'reasoning') and getattr(entry, 'reasoning', None):
                key_points.append(getattr(entry, 'reasoning'))
                if hasattr(
                        entry,
                        'suggestions') and getattr(
                        entry,
                        'suggestions',
                        None):
                    entry_suggestions = getattr(entry, 'suggestions', [])
                    if isinstance(entry_suggestions, list):
                        for suggestion in entry_suggestions:
                            if isinstance(suggestion, str):
                                suggestions.append(suggestion)
                if hasattr(
                        entry,
                        'concerns') and getattr(
                        entry,
                        'concerns',
                        None):
                    entry_concerns = getattr(entry, 'concerns', [])
                    if isinstance(entry_concerns, list):
                        for concern in entry_concerns:
                            if isinstance(concern, str):
                                concerns.append(concern)

        # Create final decision
        decision = {
            "topic": topic.title,
            "final_approach": self._synthesize_approach(
                key_points,
                suggestions),
            "key_considerations": list(set(concerns)) if concerns else [],
            "recommended_actions": list(set(suggestions)) if suggestions else [],
            "consensus_points": self._extract_consensus_points(discussion_log),
            "implementation_notes": self._generate_implementation_notes(
                    topic,
                key_points)}

        return decision

    def _synthesize_approach(self,
            key_points: List[str],
            suggestions: List[str]) -> str:
        """Synthesize the final approach from discussion points"""
        # This is a simplified synthesis - in practice, you might use another
        # AI model
        if suggestions:
            return f"Based on agent discussion, the recommended approach combines: {', '.join(suggestions[:3])}"
        elif key_points:
            return f"The discussion centered on: {key_points[0][:100]}..."
        else:
            return "No clear consensus reached, default approach recommended"

    def _extract_key_insights(self, discussion_log: List) -> List[str]:
        """Extract key insights from discussion"""
        insights = []
        for entry in discussion_log:
            if isinstance(entry, dict) and entry.get('reasoning'):
                insights.append(entry.get('reasoning'))
            elif hasattr(entry, 'reasoning') and getattr(entry, 'reasoning', None):
                insights.append(getattr(entry, 'reasoning'))
        return insights[:5]  # Top 5 insights

    def _extract_alternatives(self, discussion_log: List) -> List[str]:
        """Extract alternative approaches mentioned"""
        alternatives = []
        for entry in discussion_log:
            if isinstance(entry, dict) and entry.get('suggestions'):
                # Ensure suggestions is a list and contains only strings
                suggestions = entry.get('suggestions', [])
                if isinstance(suggestions, list):
                    for suggestion in suggestions:
                        if isinstance(suggestion, str):
                            alternatives.append(suggestion)
            elif hasattr(entry, 'suggestions') and getattr(entry, 'suggestions', None):
                # Ensure suggestions is a list and contains only strings
                entry_suggestions = getattr(entry, 'suggestions', [])
                if isinstance(entry_suggestions, list):
                    for suggestion in entry_suggestions:
                        if isinstance(suggestion, str):
                            alternatives.append(suggestion)

        # Remove duplicates by converting to set, but ensure all items are
        # strings
        unique_alternatives = []
        seen = set()
        for alt in alternatives:
            if isinstance(alt, str) and alt not in seen:
                unique_alternatives.append(alt)
                seen.add(alt)

        return unique_alternatives[:3]  # Top 3 alternatives

    def _extract_consensus_points(self, discussion_log: List) -> List[str]:
        """Extract points where agents agreed"""
        consensus_points = []
        # This is simplified - you could implement more sophisticated consensus
        # detection
        for entry in discussion_log:
            if isinstance(entry, dict) and entry.get('vote') == 'agree' and entry.get('message'):
                consensus_points.append(entry.get('message', ''))
            elif hasattr(
                entry,
                'vote') and hasattr(entry,
                'message') and getattr(entry,
                'vote',
                None) == 'agree':
                consensus_points.append(getattr(entry, 'message', ''))
        return consensus_points[:3]

    def _generate_implementation_notes(self,
            topic: DiscussionTopic,
            key_points: List[str]) -> List[str]:
        """Generate implementation notes based on discussion"""
        return [
            f"Consider {topic.context.get('platform', 'platform')} specific requirements",
            "Ensure coordination between all agents during implementation",
            "Monitor consensus points during execution"]

    def _save_discussion_progress(self,
            discussion_file: str,
            topic: DiscussionTopic,
            discussion_log: List,
            round_num: int,
            consensus_level: float):
        """Save discussion progress to file with session management"""
        # Convert discussion log to serializable format
        serializable_log = []
        for entry in discussion_log:
            if isinstance(entry, dict):
                serializable_log.append(entry)
            elif hasattr(entry, '__dict__'):
                serializable_log.append(asdict(entry))
            else:
                serializable_log.append(str(entry))

        progress_data = {
            "topic": asdict(topic),
            "discussion_log": serializable_log,
            "current_round": round_num,
            "consensus_level": consensus_level,
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id
        }

        with open(discussion_file, 'w') as f:
            json.dump(progress_data, f, indent=2, default=str)

        # ENHANCED: Track file with session manager:
        if hasattr(self.session_manager, 'current_session') and self.session_manager.current_session:
            self.session_manager.track_file(
                discussion_file,
                "discussion",
                "MultiAgentDiscussion")

    def _save_final_result(self,
            discussion_file: str,
            result: DiscussionResult):
        """Save final discussion result with session management"""
        result_file = discussion_file.replace('.json', '_final.json')

        # Enhanced result data with session info
        result_data = asdict(result)
        result_data["session_id"] = self.session_id
        result_data["final_timestamp"] = datetime.now().isoformat()

        with open(result_file, 'w') as f:
            json.dump(result_data, f, indent=2, default=str)

        # ENHANCED: Track file with session manager:
        if hasattr(self.session_manager, 'current_session') and self.session_manager.current_session:
            self.session_manager.track_file(
                result_file,
                "discussion",
                "MultiAgentDiscussion")

            # Also save to session manager's discussion tracking'
            self.session_manager.save_discussion(result_data, result.topic_id)

        # Also log to monitoring service
        self.monitoring_service.log(
            f"🎯 Agent Discussion Complete: {result.topic_id}")
        self.monitoring_service.log(
            f"   Consensus: {result.consensus_level:.2f}")
        self.monitoring_service.log(f"   Rounds: {result.total_rounds}")
        self.monitoring_service.log(
            f"   Participants: {', '.join(result.participating_agents)}")

# Predefined discussion topics for common video generation decisions:
class VideoGenerationTopics:
    """Predefined discussion topics for video generation"""

    @staticmethod
    def script_optimization(context: Dict[str, Any]) -> DiscussionTopic:
        # Get the actual user topic from context
        user_topic = context.get('topic', 'Unknown Topic')

        return DiscussionTopic(
            topic_id="script_optimization",
            title=f"Script Content and Structure Optimization for '{user_topic}'",
            description=(f"Determine the optimal script structure, content, and style for '{user_topic}' "
                         "with maximum viral potential"),
            context=context,
            required_decisions=[
                "script_length_and_pacing",
                "hook_strategy",
                "content_structure",
                "call_to_action_placement",
                "viral_elements_integration"],
            max_rounds=8,
            min_consensus=0.6)

    @staticmethod
    def visual_strategy(context: Dict[str, Any]) -> DiscussionTopic:
        return DiscussionTopic(
            topic_id="visual_strategy",
            title="Visual Style and Composition Strategy",
            description=("Determine optimal visual approach, style, and "
                    "composition for maximum impact"),
            context=context,
            required_decisions=[
                "visual_style_direction",
                "color_palette_selection",
                "composition_approach",
                "visual_transitions",
                "brand_consistency"],
            max_rounds=6,
            min_consensus=0.7)

    @staticmethod
    def audio_synchronization(context: Dict[str, Any]) -> DiscussionTopic:
        return DiscussionTopic(
            topic_id="audio_sync",
            title="Audio Production and Synchronization",
            description="Optimize audio elements, voice, music, and synchronization",
            context=context,
            required_decisions=[
                "voice_style_selection",
                "background_music_choice",
                "audio_timing_optimization",
                "sound_effects_integration",
                "audio_visual_sync"],
            max_rounds=5,
            min_consensus=0.8)

    @staticmethod
    def platform_optimization(context: Dict[str, Any]) -> DiscussionTopic:
        return DiscussionTopic(
            topic_id="platform_optimization",
            title="Platform-Specific Optimization",
            description=("Optimize content for specific platform requirements and "
                    "algorithms"),
            context=context,
            required_decisions=[
                "platform_format_optimization",
                "algorithm_compliance",
                "engagement_optimization",
                "trending_elements_integration",
                "audience_targeting"],
            max_rounds=4,
            min_consensus=0.75
        )