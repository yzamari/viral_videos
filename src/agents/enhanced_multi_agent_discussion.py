"""
Enhanced Multi-Agent Discussion System for Viral Video Generation
With 12 additional specialized AI agents for professional-grade video production

This system now includes 19 total agents covering:
- Script & Dialogue Specialists
- Advanced Audio Specialists  
- Typography & Visual Text Specialists
- Visual Style & Art Direction
- Platform & Optimization Specialists
- Quality Assurance & Testing
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
from ..services.monitoring_service import MonitoringService
from ..services.file_service import FileService
from .discussion_visualizer import DiscussionVisualizer

logger = get_logger(__name__)

class AgentRole(Enum):
    # Original agents (7)
    TREND_ANALYST = "trend_analyst"
    SCRIPT_WRITER = "script_writer"
    DIRECTOR = "director"
    VIDEO_GENERATOR = "video_generator"
    SOUNDMAN = "soundman"
    EDITOR = "editor"
    ORCHESTRATOR = "orchestrator"
    
    # NEW: Senior Management (1)
    SENIOR_MANAGER = "senior_manager"
    
    # NEW: Script & Dialogue Specialists (2)
    DIALOGUE_MASTER = "dialogue_master"
    PACE_MASTER = "pace_master"
    
    # NEW: Advanced Audio Specialists (2)
    VOICE_DIRECTOR = "voice_director"
    SOUND_DESIGNER = "sound_designer"
    
    # NEW: Typography & Visual Text Specialists (2)
    TYPE_MASTER = "type_master"
    HEADER_CRAFT = "header_craft"
    
    # NEW: Visual Style & Art Direction (2)
    STYLE_DIRECTOR = "style_director"
    COLOR_MASTER = "color_master"
    
    # NEW: Platform & Optimization Specialists (2)
    PLATFORM_GURU = "platform_guru"
    ENGAGEMENT_HACKER = "engagement_hacker"
    
    # NEW: Quality Assurance & Testing (2)
    QUALITY_GUARD = "quality_guard"
    AUDIENCE_ADVOCATE = "audience_advocate"
    
    # NEW: Advanced Specialists (6 additional agents)
    DATA_SCIENTIST = "data_scientist"
    PSYCHOLOGY_EXPERT = "psychology_expert"
    BRAND_STRATEGIST = "brand_strategist"
    ACCESSIBILITY_EXPERT = "accessibility_expert"
    PERFORMANCE_OPTIMIZER = "performance_optimizer"
    INNOVATION_CATALYST = "innovation_catalyst"

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

class EnhancedMultiAgentDiscussionSystem:
    """
    Enhanced system with 19 specialized AI agents for professional video production
    """
    
    def __init__(self, api_key: str, session_id: str):
        self.api_key = api_key
        self.session_id = session_id
        
        # Find existing session directory
        self.session_dir = self._find_existing_session_directory(session_id)
        if not self.session_dir:
            self.session_dir = f"outputs/session_{session_id}"
            os.makedirs(self.session_dir, exist_ok=True)
        
        # Initialize Gemini models
        genai.configure(api_key=api_key)
        self.discussion_model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Initialize services
        self.monitoring_service = MonitoringService(session_id)
        self.file_service = FileService(session_id)
        
        # Discussion storage
        self.discussions_dir = os.path.join(self.session_dir, "agent_discussions")
        os.makedirs(self.discussions_dir, exist_ok=True)
        
        # Initialize discussion visualizer
        self.visualizer = DiscussionVisualizer(self.session_dir)
        
        # ENHANCED: 26+ Total Agent Personalities with Senior Management
        self.agent_personalities = {
            # Senior Management (1 agent)
            AgentRole.SENIOR_MANAGER: {
                "name": "ExecutiveChief",
                "personality": "Senior executive and strategic supervisor, focused on overall project success and quality assurance across all phases",
                "expertise": ["strategic oversight", "quality management", "resource coordination", "risk assessment", "performance optimization", "team leadership"],
                "decision_style": "Executive-focused with strategic oversight and quality assurance priority"
            },
            
            # Original Core Agents (7)
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
                "expertise": ["AI video generation", "VEO-2/VEO-3 capabilities", "technical constraints", "quality optimization"],
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
            },
            
            # Script Development Phase (4 agents total)
            AgentRole.DIALOGUE_MASTER: {
                "name": "DialogueMaster",
                "personality": "Dialogue and conversation expert, focused on natural speech patterns and voice optimization",
                "expertise": ["dialogue writing", "conversation flow", "voice acting", "speech patterns", "character development"],
                "decision_style": "Dialogue-focused with natural speech priority"
            },
            AgentRole.PACE_MASTER: {
                "name": "PaceMaster",
                "personality": "Timing and pacing expert, focused on rhythm and flow optimization",
                "expertise": ["timing optimization", "pacing control", "rhythm analysis", "flow management", "duration targeting"],
                "decision_style": "Timing-focused with flow optimization priority"
            },
            
            # Audio Production Phase (5 agents total)
            AgentRole.VOICE_DIRECTOR: {
                "name": "VoiceDirector",
                "personality": "Voice casting and direction expert, focused on vocal performance optimization",
                "expertise": ["voice casting", "vocal direction", "performance coaching", "emotion delivery", "accent control"],
                "decision_style": "Voice-focused with performance optimization priority"
            },
            AgentRole.SOUND_DESIGNER: {
                "name": "SoundDesigner",
                "personality": "Sound design and audio effects expert, focused on immersive audio experiences",
                "expertise": ["sound effects", "audio design", "ambient sound", "audio atmosphere", "immersive audio"],
                "decision_style": "Sound-focused with immersion priority"
            },
            
            # Visual Design Phase (6 agents total)
            AgentRole.STYLE_DIRECTOR: {
                "name": "StyleDirector",
                "personality": "Art direction and visual style expert, focused on aesthetic consistency and brand alignment",
                "expertise": ["art direction", "visual style", "aesthetic design", "brand consistency", "color theory"],
                "decision_style": "Style-focused with aesthetic priority"
            },
            AgentRole.COLOR_MASTER: {
                "name": "ColorMaster",
                "personality": "Color psychology and palette expert, focused on emotional impact through color",
                "expertise": ["color psychology", "palette design", "emotional color impact", "visual harmony", "brand colors"],
                "decision_style": "Color-focused with psychological impact priority"
            },
            AgentRole.TYPE_MASTER: {
                "name": "TypeMaster",
                "personality": "Typography and text design expert, focused on readable and impactful text elements",
                "expertise": ["typography", "text design", "font selection", "readability optimization", "text hierarchy"],
                "decision_style": "Typography-focused with readability priority"
            },
            AgentRole.HEADER_CRAFT: {
                "name": "HeaderCraft",
                "personality": "Header and title design expert, focused on attention-grabbing visual elements",
                "expertise": ["header design", "title creation", "visual hierarchy", "attention grabbing", "clickbait optimization"],
                "decision_style": "Header-focused with attention priority"
            },
            
            # Platform Optimization Phase (5 agents total)
            AgentRole.PLATFORM_GURU: {
                "name": "PlatformGuru",
                "personality": "Multi-platform expert, focused on platform-specific optimization and best practices",
                "expertise": ["platform optimization", "multi-platform strategy", "platform algorithms", "format requirements", "distribution"],
                "decision_style": "Platform-focused with optimization priority"
            },
            AgentRole.ENGAGEMENT_HACKER: {
                "name": "EngagementHacker",
                "personality": "Viral mechanics and engagement expert, focused on psychological engagement drivers",
                "expertise": ["viral mechanics", "engagement triggers", "psychological drivers", "social sharing optimization", "virality factors"],
                "decision_style": "Engagement-focused with viral optimization priority"
            },
            
            # Quality Assurance & Testing (3 agents total)
            AgentRole.QUALITY_GUARD: {
                "name": "QualityGuard",
                "personality": "Quality assurance and testing expert, focused on technical excellence and error prevention",
                "expertise": ["quality evaluation", "technical assessment", "performance optimization", "error detection", "standards enforcement"],
                "decision_style": "Quality-focused with technical precision priority"
            },
            AgentRole.AUDIENCE_ADVOCATE: {
                "name": "AudienceAdvocate",
                "personality": "User experience and audience psychology expert, focused on viewer satisfaction",
                "expertise": ["audience psychology", "user experience", "accessibility", "demographic preferences", "feedback interpretation"],
                "decision_style": "User-focused with audience satisfaction priority"
            },
            
            # NEW: Advanced Specialists (6 additional agents)
            AgentRole.DATA_SCIENTIST: {
                "name": "DataMaven",
                "personality": "Data science and analytics expert, focused on performance prediction and optimization",
                "expertise": ["data analysis", "performance prediction", "A/B testing", "metrics optimization", "statistical modeling"],
                "decision_style": "Data-driven with predictive analytics priority"
            },
            AgentRole.PSYCHOLOGY_EXPERT: {
                "name": "MindReader",
                "personality": "Psychology and behavioral expert, focused on human psychology and decision-making",
                "expertise": ["behavioral psychology", "cognitive science", "decision psychology", "emotional triggers", "persuasion techniques"],
                "decision_style": "Psychology-focused with behavioral optimization priority"
            },
            AgentRole.BRAND_STRATEGIST: {
                "name": "BrandMaster",
                "personality": "Brand strategy and positioning expert, focused on brand consistency and market positioning",
                "expertise": ["brand strategy", "market positioning", "brand consistency", "competitive analysis", "brand identity"],
                "decision_style": "Brand-focused with strategic positioning priority"
            },
            AgentRole.ACCESSIBILITY_EXPERT: {
                "name": "AccessGuard",
                "personality": "Accessibility and inclusion expert, focused on universal design and compliance",
                "expertise": ["accessibility design", "universal access", "compliance standards", "inclusive design", "assistive technology"],
                "decision_style": "Accessibility-focused with inclusion priority"
            },
            AgentRole.PERFORMANCE_OPTIMIZER: {
                "name": "SpeedDemon",
                "personality": "Performance and optimization expert, focused on technical performance and efficiency",
                "expertise": ["performance optimization", "technical efficiency", "resource management", "speed optimization", "system performance"],
                "decision_style": "Performance-focused with efficiency priority"
            },
            AgentRole.INNOVATION_CATALYST: {
                "name": "InnovateMaster",
                "personality": "Innovation and creativity expert, focused on cutting-edge techniques and breakthrough ideas",
                "expertise": ["innovation strategies", "creative techniques", "breakthrough thinking", "emerging technologies", "disruptive approaches"],
                "decision_style": "Innovation-focused with breakthrough priority"
            }
        }
        
        logger.info(f"🚀 ENHANCED Multi-Agent Discussion System initialized for session {session_id}")
        logger.info(f"🤖 Total agents: {len(self.agent_personalities)} (26+ specialized experts)")
        logger.info(f"💬 Agent phases: Script (4), Audio (5), Visual (6), Platform (5), Quality (3), Advanced (6)")
        logger.info(f"🎯 Discussion modes: light/standard/deep with configurable consensus thresholds")
    
    def _find_existing_session_directory(self, session_id: str) -> str:
        """Find existing session directory that contains the session_id"""
        outputs_dir = "outputs"
        if not os.path.exists(outputs_dir):
            return ""
        
        # Look for session directories that contain the session_id
        for item in os.listdir(outputs_dir):
            item_path = os.path.join(outputs_dir, item)
            if os.path.isdir(item_path) and item.startswith("session_"):
                if session_id in item:
                    logger.info(f"📁 Found existing session directory: {item_path}")
                    return item_path
        
        # If no exact match, look for the most recent session directory
        session_dirs = []
        for item in os.listdir(outputs_dir):
            item_path = os.path.join(outputs_dir, item)
            if os.path.isdir(item_path) and item.startswith("session_"):
                session_dirs.append((item_path, os.path.getctime(item_path)))
        
        if session_dirs:
            session_dirs.sort(key=lambda x: x[1], reverse=True)
            most_recent_session = session_dirs[0][0]
            logger.info(f" Using most recent session directory: {most_recent_session}")
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
        logger.info(f"🎭 Starting ENHANCED agent discussion: {topic.title}")
        logger.info(f"👥 Participating agents ({len(participating_agents)}): {', '.join([self.agent_personalities[agent]['name'] for agent in participating_agents])}")
        
        # Start visualization
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
        discussion_file = os.path.join(self.discussions_dir, f"enhanced_discussion_{topic.topic_id}_{discussion_id}.json")
        
        # Initial context message
        context_message = self._create_context_message(topic)
        discussion_log.append(context_message)
        
        # Discussion rounds
        while current_round < topic.max_rounds and not consensus_reached:
            current_round += 1
            logger.info(f"🔄 Enhanced discussion round {current_round}/{topic.max_rounds}")
            
            round_messages = []
            
            # Each agent contributes to the discussion
            for agent_role in participating_agents:
                agent_message = self._get_agent_response(
                    agent_role, topic, discussion_log, current_round
                )
                round_messages.append(agent_message)
                discussion_log.append(agent_message)
                
                # Log to visualizer
                agent_name = self.agent_personalities[agent_role]['name']
                self.visualizer.log_agent_contribution(
                    agent_name, agent_message.message, current_round, 
                    agent_message.vote, agent_message.reasoning
                )
                
                # Log agent contribution
                logger.info(f"💬 {agent_name}: {agent_message.message[:80]}...")
            
            # Check for consensus
            consensus_level = self._calculate_consensus(round_messages)
            logger.info(f"📊 Enhanced consensus level: {consensus_level:.2f}")
            
            # Update visualizer
            self.visualizer.update_consensus(consensus_level, current_round)
            
            if consensus_level >= topic.min_consensus:
                consensus_reached = True
                logger.info("✅ Enhanced consensus reached!")
            
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
        
        # Complete visualization
        self.visualizer.complete_discussion(
            consensus_level, current_round, key_insights, final_decision
        )
        
        # Save final result
        self._save_final_result(discussion_file, result)
        
        logger.info(f"🎯 Enhanced discussion completed: {result.consensus_level:.2f} consensus in {current_round} rounds")
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
                json.dumps(value)
                serializable_context[key] = value
            except (TypeError, ValueError):
                serializable_context[key] = str(value)
        
        return f"""
You are {agent_info['name']}, a specialized AI agent in the ENHANCED Multi-Agent Discussion System.

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

As a specialized expert, provide your professional perspective based on your unique expertise. 

Please respond in the following JSON format:
{{
    "message": "Your expert contribution to the discussion (2-3 sentences)",
    "reasoning": "Your professional reasoning behind this perspective (1-2 sentences)",
    "suggestions": ["Specific expert suggestion 1", "Specific expert suggestion 2"],
    "concerns": ["Professional concern 1 if any", "Professional concern 2 if any"],
    "vote": "agree/disagree/neutral"
}}

Focus on:
1. Your specialized area of expertise
2. Professional best practices
3. Technical considerations specific to your role
4. Quality standards in your domain
5. Practical implementation insights

Be authoritative but collaborative. Your expertise is valuable to the team's success.
"""
    
    def _parse_agent_response(self, response_text: str, agent_role: AgentRole) -> Dict[str, Any]:
        """Parse agent response from Gemini model"""
        try:
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
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
        
        for entry in discussion_log[-8:]:  # Last 8 entries for more context
            if isinstance(entry, dict):
                if entry.get('type') == 'context':
                    continue
                agent_name = entry.get('agent_name', 'Unknown')
                message = entry.get('message', '')
                if message:
                    formatted.append(f"{agent_name}: {message}")
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
        
        # Create comprehensive final decision
        decision = {
            "topic": topic.title,
            "final_approach": self._synthesize_approach(key_points, suggestions),
            "key_considerations": list(set(concerns)) if concerns else [],
            "recommended_actions": list(set(suggestions)) if suggestions else [],
            "consensus_points": self._extract_consensus_points(discussion_log),
            "implementation_notes": self._generate_implementation_notes(topic, key_points),
            "quality_standards": self._extract_quality_standards(discussion_log),
            "agent_specializations": [self.agent_personalities[agent]['name'] for agent in participating_agents]
        }
        
        return decision
    
    def _synthesize_approach(self, key_points: List[str], suggestions: List[str]) -> str:
        """Synthesize the final approach from discussion points"""
        if suggestions:
            return f"Based on enhanced agent discussion, the professional approach combines: {', '.join(suggestions[:4])}"
        elif key_points:
            return f"The expert discussion centered on: {key_points[0][:120]}..."
        else:
            return "Enhanced consensus approach with professional standards"
    
    def _extract_key_insights(self, discussion_log: List) -> List[str]:
        """Extract key insights from discussion"""
        insights = []
        for entry in discussion_log:
            if isinstance(entry, dict) and 'reasoning' in entry and entry['reasoning']:
                insights.append(entry['reasoning'])
            elif hasattr(entry, 'reasoning') and entry.reasoning:
                insights.append(entry.reasoning)
        return insights[:6]  # Top 6 insights from enhanced discussion
    
    def _extract_alternatives(self, discussion_log: List) -> List[str]:
        """Extract alternative approaches mentioned"""
        alternatives = []
        for entry in discussion_log:
            if isinstance(entry, dict) and 'suggestions' in entry and entry['suggestions']:
                suggestions = entry.get('suggestions', [])
                if isinstance(suggestions, list):
                    for suggestion in suggestions:
                        if isinstance(suggestion, str):
                            alternatives.append(suggestion)
            elif hasattr(entry, 'suggestions') and entry.suggestions:
                if isinstance(entry.suggestions, list):
                    for suggestion in entry.suggestions:
                        if isinstance(suggestion, str):
                            alternatives.append(suggestion)
        
        unique_alternatives = []
        seen = set()
        for alt in alternatives:
            if isinstance(alt, str) and alt not in seen:
                unique_alternatives.append(alt)
                seen.add(alt)
        
        return unique_alternatives[:4]  # Top 4 alternatives
    
    def _extract_consensus_points(self, discussion_log: List) -> List[str]:
        """Extract points where agents agreed"""
        consensus_points = []
        for entry in discussion_log:
            if isinstance(entry, dict) and entry.get('vote') == 'agree' and entry.get('message'):
                consensus_points.append(entry.get('message', ''))
            elif hasattr(entry, 'vote') and hasattr(entry, 'message') and entry.vote == 'agree':
                consensus_points.append(entry.message)
        return consensus_points[:4]
    
    def _extract_quality_standards(self, discussion_log: List) -> List[str]:
        """Extract quality standards mentioned by agents"""
        quality_standards = []
        quality_keywords = ['quality', 'standard', 'professional', 'best practice', 'optimization']
        
        for entry in discussion_log:
            message = ""
            if isinstance(entry, dict) and entry.get('message'):
                message = entry.get('message', '').lower()
            elif hasattr(entry, 'message'):
                message = entry.message.lower()
            
            if any(keyword in message for keyword in quality_keywords):
                if isinstance(entry, dict):
                    quality_standards.append(entry.get('message', ''))
                elif hasattr(entry, 'message'):
                    quality_standards.append(entry.message)
        
        return quality_standards[:3]  # Top 3 quality standards
    
    def _generate_implementation_notes(self, topic: DiscussionTopic, key_points: List[str]) -> List[str]:
        """Generate implementation notes based on discussion"""
        return [
            f"Consider {topic.context.get('platform', 'platform')} specific requirements",
            "Ensure coordination between all specialized agents during implementation",
            "Monitor consensus points and quality standards during execution",
            "Apply professional-grade standards from expert agent input"
        ]
    
    def _save_discussion_progress(self, discussion_file: str, topic: DiscussionTopic, 
                                discussion_log: List, round_num: int, consensus_level: float):
        """Save discussion progress to file"""
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
            "system_type": "enhanced_multi_agent"
        }
        
        try:
            with open(discussion_file, 'w') as f:
                json.dump(progress_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving discussion progress: {e}")
    
    def _save_final_result(self, discussion_file: str, result: DiscussionResult):
        """Save final discussion result"""
        try:
            result_data = asdict(result)
            result_data["timestamp"] = datetime.now().isoformat()
            result_data["system_type"] = "enhanced_multi_agent"
            
            final_file = discussion_file.replace('.json', '_final.json')
            with open(final_file, 'w') as f:
                json.dump(result_data, f, indent=2, default=str)
                
            logger.info(f"📁 Enhanced discussion result saved: {final_file}")
        except Exception as e:
            logger.error(f"Error saving final result: {e}")


class EnhancedVideoGenerationTopics:
    """
    Enhanced discussion topics for professional video generation
    """
    
    @staticmethod
    def script_development(context: Dict[str, Any]) -> DiscussionTopic:
        """Script quality, dialogue, and pacing discussion"""
        user_topic = context.get('topic', 'viral content')
        
        return DiscussionTopic(
            topic_id="script_development",
            title=f"Script Development and Dialogue Optimization for '{user_topic}'",
            description="Comprehensive script development including dialogue naturalness, pacing, and TTS optimization",
            context=context,
            required_decisions=[
                "Script structure and narrative flow",
                "Dialogue naturalness and character voices",
                "Pacing and timing optimization",
                "Hook placement and emotional beats",
                "TTS readability and pronunciation"
            ],
            max_rounds=8,
            min_consensus=0.8
        )
    
    @staticmethod
    def audio_production(context: Dict[str, Any]) -> DiscussionTopic:
        """Audio production and voice optimization discussion"""
        return DiscussionTopic(
            topic_id="audio_production",
            title="Audio Production and Voice Optimization",
            description="Comprehensive audio strategy including voice selection, sound design, and audio branding",
            context=context,
            required_decisions=[
                "Voice casting and character selection",
                "Speaking speed and emotional delivery",
                "Sound effects and ambient audio",
                "Audio branding and consistency",
                "Platform-specific audio optimization"
            ],
            max_rounds=8,
            min_consensus=0.8
        )
    
    @staticmethod
    def visual_design(context: Dict[str, Any]) -> DiscussionTopic:
        """Visual design and typography discussion"""
        return DiscussionTopic(
            topic_id="visual_design",
            title="Visual Design and Typography Strategy",
            description="Comprehensive visual strategy including style direction, typography, and color psychology",
            context=context,
            required_decisions=[
                "Overall visual style and art direction",
                "Typography and font selection",
                "Header design and placement strategy",
                "Color palette and psychology",
                "Visual consistency and branding"
            ],
            max_rounds=8,
            min_consensus=0.8
        )
    
    @staticmethod
    def platform_optimization(context: Dict[str, Any]) -> DiscussionTopic:
        """Platform optimization and viral mechanics discussion"""
        return DiscussionTopic(
            topic_id="platform_optimization",
            title="Platform Optimization and Viral Mechanics",
            description="Platform-specific optimization and engagement enhancement strategies",
            context=context,
            required_decisions=[
                "Platform-specific formatting and features",
                "Algorithm optimization strategies",
                "Engagement trigger placement",
                "Viral mechanics integration",
                "Cross-platform adaptation"
            ],
            max_rounds=8,
            min_consensus=0.8
        )
    
    @staticmethod
    def quality_assurance(context: Dict[str, Any]) -> DiscussionTopic:
        """Quality assurance and user experience discussion"""
        return DiscussionTopic(
            topic_id="quality_assurance",
            title="Quality Assurance and User Experience",
            description="Comprehensive quality review and user experience optimization",
            context=context,
            required_decisions=[
                "Quality standards and technical requirements",
                "User experience optimization",
                "Accessibility considerations",
                "Performance optimization",
                "Final approval criteria"
            ],
            max_rounds=6,
            min_consensus=0.9
        )
