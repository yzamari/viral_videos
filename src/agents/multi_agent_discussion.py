"""
Multi-Agent Discussion System for Viral Video Generation

This system allows AI agents to have structured discussions to collaboratively
decide on the best approach for each step of video generation.
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import google.generativeai as genai
from dataclasses import dataclass, asdict
from enum import Enum

from ..utils.logging_config import get_logger
from ..utils.session_manager import SessionManager
from ..services.monitoring_service import MonitoringService
from ..services.file_service import FileService
from .discussion_visualizer import DiscussionVisualizer

logger = get_logger(__name__)

class AgentRole(Enum):
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
    Manages discussions between AI agents for collaborative decision making
    """
    
    def __init__(self, api_key: str, session_id: str):
        self.api_key = api_key
        self.session_id = session_id
        
        # Use SessionManager to find or create session directory
        self.session_dir = SessionManager.find_most_recent_session()
        if not self.session_dir:
            # Create new session directory if none exists
            self.session_dir = SessionManager.create_session_folder(session_id)
        
        # Initialize Gemini models for different agent personalities
        genai.configure(api_key=api_key)
        self.discussion_model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Initialize services
        self.monitoring_service = MonitoringService(session_id)
        self.file_service = FileService(session_id)
        
        # Discussion storage
        self.discussions_dir = os.path.join(self.session_dir, "agent_discussions")
        os.makedirs(self.discussions_dir, exist_ok=True)
        
        # ENHANCED: Initialize discussion visualizer
        self.visualizer = DiscussionVisualizer(self.session_dir)
        
        # Agent personalities and expertise
        self.agent_personalities = {
            AgentRole.TREND_ANALYST: {
                "name": "TrendMaster",
                "personality": "Data-driven, analytical, focused on viral patterns and audience engagement metrics",
                "expertise": ["viral trends", "audience analysis", "platform optimization", "engagement metrics"],
                "decision_style": "Evidence-based with statistical backing"
            },
            AgentRole.SCRIPT_WRITER: {
                "name": "StoryWeaver",
                "personality": "Creative, narrative-focused, emphasizes storytelling and emotional connection",
                "expertise": ["storytelling", "narrative structure", "emotional hooks", "viral content patterns"],
                "decision_style": "Creative with focus on narrative impact"
            },
            AgentRole.DIRECTOR: {
                "name": "VisionCraft",
                "personality": "Visual storyteller, focused on cinematic quality and scene composition",
                "expertise": ["visual storytelling", "scene composition", "cinematic techniques", "continuity"],
                "decision_style": "Artistic with technical precision"
            },
            AgentRole.VIDEO_GENERATOR: {
                "name": "PixelForge",
                "personality": "Technical expert, focused on AI video generation capabilities and limitations",
                "expertise": ["AI video generation", "VEO-2 capabilities", "technical constraints", "quality optimization"],
                "decision_style": "Technical feasibility with quality focus"
            },
            AgentRole.SOUNDMAN: {
                "name": "AudioMaster",
                "personality": "Audio specialist, focused on sound design and voice optimization",
                "expertise": ["audio production", "voice synthesis", "sound design", "audio-visual sync"],
                "decision_style": "Audio-centric with synchronization priority"
            },
            AgentRole.EDITOR: {
                "name": "CutMaster",
                "personality": "Post-production expert, focused on final assembly and polish",
                "expertise": ["video editing", "post-production", "final assembly", "quality control"],
                "decision_style": "Quality-focused with practical execution"
            },
            AgentRole.ORCHESTRATOR: {
                "name": "SyncMaster",
                "personality": "Coordination expert, focused on overall workflow and agent synchronization",
                "expertise": ["workflow coordination", "agent synchronization", "resource management", "timeline optimization"],
                "decision_style": "Holistic with coordination priority"
            }
        }
        
        logger.info(f"🤖 Multi-Agent Discussion System initialized for session {session_id}")
        logger.info(f"💬 Available agents: {', '.join([p['name'] for p in self.agent_personalities.values()])}")
    
    def _find_existing_session_directory(self, session_id: str) -> str:
        """Find existing session directory that contains the session_id"""
        outputs_dir = "outputs"
        if not os.path.exists(outputs_dir):
            return ""
        
        # Look for session directories that contain the session_id
        for item in os.listdir(outputs_dir):
            item_path = os.path.join(outputs_dir, item)
            if os.path.isdir(item_path) and item.startswith("session_"):
                # Check if this session contains our session_id
                if session_id in item:
                    logger.info(f"📁 Found existing session directory: {item_path}")
                    return item_path
        
        # If no exact match, look for the most recent session directory
        # This handles cases where session_id format might be different
        session_dirs = []
        for item in os.listdir(outputs_dir):
            item_path = os.path.join(outputs_dir, item)
            if os.path.isdir(item_path) and item.startswith("session_"):
                session_dirs.append((item_path, os.path.getctime(item_path)))
        
        if session_dirs:
            # Sort by creation time and return the most recent
            session_dirs.sort(key=lambda x: x[1], reverse=True)
            most_recent_session = session_dirs[0][0]
            logger.info(f"📁 Using most recent session directory: {most_recent_session}")
            return most_recent_session
        
        return ""
    
    def start_discussion(self, topic: DiscussionTopic, participating_agents: List[AgentRole]) -> DiscussionResult:
        """
        Start a multi-agent discussion on a specific topic
        
        Args:
            topic: The discussion topic and context
            participating_agents: List of agent roles to participate
            
        Returns:
            DiscussionResult with final decision and insights
        """
        logger.info(f"🎭 Starting agent discussion: {topic.title}")
        logger.info(f"👥 Participating agents: {', '.join([self.agent_personalities[agent]['name'] for agent in participating_agents])}")
        
        # ENHANCED: Start visualization
        agent_names = [self.agent_personalities[agent]['name'] for agent in participating_agents]
        self.visualizer.start_discussion_visualization(
            topic.title, agent_names, topic.max_rounds, topic.min_consensus
        )
        
        # Initialize discussion
        discussion_id = str(uuid.uuid4())[:8]
        discussion_log = []
        current_round = 0
        consensus_reached = False
        
        # Create discussion file
        discussion_file = os.path.join(self.discussions_dir, f"discussion_{topic.topic_id}_{discussion_id}.json")
        
        # Initial context message
        context_message = self._create_context_message(topic)
        discussion_log.append(context_message)
        
        # Discussion rounds
        while current_round < topic.max_rounds and not consensus_reached:
            current_round += 1
            logger.info(f"🔄 Discussion round {current_round}/{topic.max_rounds}")
            
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
                self.visualizer.log_agent_contribution(
                    agent_name, agent_message.message, current_round, 
                    agent_message.vote, agent_message.reasoning
                )
                
                # Log agent contribution
                logger.info(f"💬 {agent_name}: {agent_message.message[:100]}...")
            
            # Check for consensus
            consensus_level = self._calculate_consensus(round_messages)
            logger.info(f"📊 Consensus level: {consensus_level:.2f}")
            
            # ENHANCED: Update visualizer
            self.visualizer.update_consensus(consensus_level, current_round)
            
            if consensus_level >= topic.min_consensus:
                consensus_reached = True
                logger.info("✅ Consensus reached!")
            
            # Save discussion progress
            self._save_discussion_progress(discussion_file, topic, discussion_log, current_round, consensus_level)
        
        # Generate final decision
        final_decision = self._generate_final_decision(topic, discussion_log, participating_agents)
        
        # Extract key insights
        key_insights = self._extract_key_insights(discussion_log)
        
        # Create result
        result = DiscussionResult(
            topic_id=topic.topic_id,
            decision=final_decision,
            consensus_level=consensus_level,
            total_rounds=current_round,
            participating_agents=[self.agent_personalities[agent]['name'] for agent in participating_agents],
            key_insights=key_insights,
            alternative_approaches=self._extract_alternatives(discussion_log)
        )
        
        # ENHANCED: Complete visualization
        self.visualizer.complete_discussion(
            consensus_level, current_round, key_insights, final_decision
        )
        
        # Save final result
        self._save_final_result(discussion_file, result)
        
        logger.info(f"🎯 Discussion completed: {result.consensus_level:.2f} consensus in {current_round} rounds")
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
    
    def _get_agent_response(self, agent_role: AgentRole, topic: DiscussionTopic, 
                           discussion_log: List[Dict], round_num: int) -> AgentMessage:
        """Get response from a specific agent"""
        agent_info = self.agent_personalities[agent_role]
        
        # Create discussion context for the agent
        discussion_context = self._format_discussion_for_agent(discussion_log, agent_role)
        
        # Create agent-specific prompt
        prompt = self._create_agent_prompt(agent_info, topic, discussion_context, round_num)
        
        try:
            # Get response from Gemini model
            response = self.discussion_model.generate_content(prompt)
            
            # Parse agent response
            agent_response = self._parse_agent_response(response.text, agent_role)
            
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
            logger.error(f"Error getting response from {agent_info['name']}: {e}")
            # Return fallback response
            return AgentMessage(
                agent_role=agent_role,
                agent_name=agent_info['name'],
                message=f"I need more information to provide a detailed response about {topic.title}.",
                timestamp=datetime.now(),
                message_id=str(uuid.uuid4())[:8],
                vote="neutral"
            )
    
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
        
        return f"""
You are {agent_info['name']}, an AI agent with the following characteristics:

PERSONALITY: {agent_info['personality']}
EXPERTISE: {', '.join(agent_info['expertise'])}
DECISION STYLE: {agent_info['decision_style']}

DISCUSSION TOPIC: {topic.title}
DESCRIPTION: {topic.description}
CONTEXT: {json.dumps(serializable_context, indent=2)}

REQUIRED DECISIONS: {', '.join(topic.required_decisions)}

DISCUSSION ROUND: {round_num}

PREVIOUS DISCUSSION:
{discussion_context}

Your task is to contribute to this discussion by providing your expert perspective based on your role and expertise. 

Please respond in the following JSON format:
{{
    "message": "Your main contribution to the discussion (2-3 sentences)",
    "reasoning": "Your reasoning behind this perspective (1-2 sentences)",
    "suggestions": ["Specific suggestion 1", "Specific suggestion 2"],
    "concerns": ["Concern 1 if any", "Concern 2 if any"],
    "vote": "agree/disagree/neutral"
}}

Focus on:
1. Your area of expertise
2. Practical considerations
3. Potential challenges or opportunities
4. Specific actionable recommendations

Be concise but insightful. Consider what other agents have said and build upon or respectfully challenge their ideas.
"""
    
    def _parse_agent_response(self, response_text: str, agent_role: AgentRole) -> Dict[str, Any]:
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
    
    def _format_discussion_for_agent(self, discussion_log: List, current_agent: AgentRole) -> str:
        """Format discussion history for agent context"""
        formatted = []
        
        for entry in discussion_log[-6:]:  # Last 6 entries to keep context manageable
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
    
    def _calculate_consensus(self, round_messages: List[AgentMessage]) -> float:
        """Calculate consensus level from agent votes"""
        if not round_messages:
            return 0.0
        
        votes = [msg.vote for msg in round_messages if msg.vote]
        if not votes:
            return 0.0
        
        agree_count = votes.count('agree')
        total_votes = len(votes)
        
        return agree_count / total_votes if total_votes > 0 else 0.0
    
    def _generate_final_decision(self, topic: DiscussionTopic, discussion_log: List, 
                               participating_agents: List[AgentRole]) -> Dict[str, Any]:
        """Generate final decision based on discussion"""
        # Extract key points from discussion
        key_points = []
        suggestions = []
        concerns = []
        
        for entry in discussion_log:
            if isinstance(entry, dict) and 'reasoning' in entry and entry['reasoning']:
                key_points.append(entry['reasoning'])
            elif hasattr(entry, 'reasoning') and entry.reasoning:
                key_points.append(entry.reasoning)
            if isinstance(entry, dict) and 'suggestions' in entry and entry['suggestions']:
                for suggestion in entry['suggestions']:
                    if isinstance(suggestion, str):
                        suggestions.append(suggestion)
            elif hasattr(entry, 'suggestions') and entry.suggestions:
                for suggestion in entry.suggestions:
                    if isinstance(suggestion, str):
                        suggestions.append(suggestion)
            if isinstance(entry, dict) and 'concerns' in entry and entry['concerns']:
                for concern in entry['concerns']:
                    if isinstance(concern, str):
                        concerns.append(concern)
            elif hasattr(entry, 'concerns') and entry.concerns:
                for concern in entry.concerns:
                    if isinstance(concern, str):
                        concerns.append(concern)
        
        # Create final decision
        decision = {
            "topic": topic.title,
            "final_approach": self._synthesize_approach(key_points, suggestions),
            "key_considerations": list(set(concerns)) if concerns else [],
            "recommended_actions": list(set(suggestions)) if suggestions else [],
            "consensus_points": self._extract_consensus_points(discussion_log),
            "implementation_notes": self._generate_implementation_notes(topic, key_points)
        }
        
        return decision
    
    def _synthesize_approach(self, key_points: List[str], suggestions: List[str]) -> str:
        """Synthesize the final approach from discussion points"""
        # This is a simplified synthesis - in practice, you might use another AI model
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
            if isinstance(entry, dict) and 'reasoning' in entry and entry['reasoning']:
                insights.append(entry['reasoning'])
            elif hasattr(entry, 'reasoning') and entry.reasoning:
                insights.append(entry.reasoning)
        return insights[:5]  # Top 5 insights
    
    def _extract_alternatives(self, discussion_log: List) -> List[str]:
        """Extract alternative approaches mentioned"""
        alternatives = []
        for entry in discussion_log:
            if isinstance(entry, dict) and 'suggestions' in entry and entry['suggestions']:
                # Ensure suggestions is a list and contains only strings
                suggestions = entry.get('suggestions', [])
                if isinstance(suggestions, list):
                    for suggestion in suggestions:
                        if isinstance(suggestion, str):
                            alternatives.append(suggestion)
            elif hasattr(entry, 'suggestions') and entry.suggestions:
                # Ensure suggestions is a list and contains only strings
                if isinstance(entry.suggestions, list):
                    for suggestion in entry.suggestions:
                        if isinstance(suggestion, str):
                            alternatives.append(suggestion)
        
        # Remove duplicates by converting to set, but ensure all items are strings
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
        # This is simplified - you could implement more sophisticated consensus detection
        for entry in discussion_log:
            if isinstance(entry, dict) and entry.get('vote') == 'agree' and entry.get('message'):
                consensus_points.append(entry.get('message', ''))
            elif hasattr(entry, 'vote') and hasattr(entry, 'message') and entry.vote == 'agree':
                consensus_points.append(entry.message)
        return consensus_points[:3]
    
    def _generate_implementation_notes(self, topic: DiscussionTopic, key_points: List[str]) -> List[str]:
        """Generate implementation notes based on discussion"""
        return [
            f"Consider {topic.context.get('platform', 'platform')} specific requirements",
            "Ensure coordination between all agents during implementation",
            "Monitor consensus points during execution"
        ]
    
    def _save_discussion_progress(self, discussion_file: str, topic: DiscussionTopic, 
                                discussion_log: List, round_num: int, consensus_level: float):
        """Save discussion progress to file"""
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
            "timestamp": datetime.now().isoformat()
        }
        
        with open(discussion_file, 'w') as f:
            json.dump(progress_data, f, indent=2, default=str)
    
    def _save_final_result(self, discussion_file: str, result: DiscussionResult):
        """Save final discussion result"""
        result_file = discussion_file.replace('.json', '_final.json')
        
        with open(result_file, 'w') as f:
            json.dump(asdict(result), f, indent=2, default=str)
        
        # Also log to monitoring service
        self.monitoring_service.log(f"🎯 Agent Discussion Complete: {result.topic_id}")
        self.monitoring_service.log(f"   Consensus: {result.consensus_level:.2f}")
        self.monitoring_service.log(f"   Rounds: {result.total_rounds}")
        self.monitoring_service.log(f"   Participants: {', '.join(result.participating_agents)}")

# Predefined discussion topics for common video generation decisions
class VideoGenerationTopics:
    """Predefined discussion topics for video generation"""
    
    @staticmethod
    def script_optimization(context: Dict[str, Any]) -> DiscussionTopic:
        # Get the actual user topic from context
        user_topic = context.get('topic', 'Unknown Topic')
        
        return DiscussionTopic(
            topic_id="script_optimization",
            title=f"Script Content and Structure Optimization for '{user_topic}'",
            description=f"Determine the optimal script structure, content, and style for '{user_topic}' with maximum viral potential",
            context=context,
            required_decisions=[
                "script_length_and_pacing",
                "hook_strategy",
                "content_structure",
                "call_to_action_placement",
                "viral_elements_integration"
            ],
            max_rounds=8,
            min_consensus=0.6
        )
    
    @staticmethod
    def visual_strategy(context: Dict[str, Any]) -> DiscussionTopic:
        return DiscussionTopic(
            topic_id="visual_strategy",
            title="Visual Style and Video Generation Strategy",
            description="Decide on visual style, VEO-2 prompts, and video generation approach",
            context=context,
            required_decisions=[
                "visual_style_direction",
                "veo2_prompt_strategy",
                "scene_composition",
                "continuity_approach",
                "fallback_strategies"
            ],
            max_rounds=7,
            min_consensus=0.7
        )
    
    @staticmethod
    def audio_synchronization(context: Dict[str, Any]) -> DiscussionTopic:
        return DiscussionTopic(
            topic_id="audio_sync",
            title="Audio Generation and Synchronization Strategy",
            description="Determine audio generation approach and synchronization with video",
            context=context,
            required_decisions=[
                "voice_style_selection",
                "audio_timing_strategy",
                "sync_methodology",
                "audio_enhancement",
                "fallback_audio_options"
            ],
            max_rounds=6,
            min_consensus=0.8
        )
    
    @staticmethod
    def platform_optimization(context: Dict[str, Any]) -> DiscussionTopic:
        return DiscussionTopic(
            topic_id="platform_optimization",
            title="Platform-Specific Optimization Strategy",
            description="Optimize content for specific social media platform requirements",
            context=context,
            required_decisions=[
                "platform_specific_adjustments",
                "aspect_ratio_optimization",
                "duration_optimization",
                "engagement_optimization",
                "distribution_strategy"
            ],
            max_rounds=5,
            min_consensus=0.75
        ) 