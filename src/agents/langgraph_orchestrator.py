"""
LangGraph-based Multi-Agent Discussion Orchestrator
Uses LangGraph for improved state management and agent coordination
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, TypedDict, Annotated, Sequence
from dataclasses import dataclass
import operator

# Import logger first
from ..utils.logging_config import get_logger
logger = get_logger(__name__)

try:
    from langgraph.graph import StateGraph, MessageGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
    from langchain_core.prompts import ChatPromptTemplate
    LANGGRAPH_AVAILABLE = True
    logger.info("✅ LangGraph successfully imported and available")
except ImportError as e:
    logger.warning(f"LangGraph import error: {e}")
    StateGraph = None
    MessageGraph = None
    END = None
    MemorySaver = None
    BaseMessage = dict
    HumanMessage = dict
    AIMessage = dict
    SystemMessage = dict
    ChatPromptTemplate = None
    LANGGRAPH_AVAILABLE = False

from .multi_agent_discussion import (
    AgentRole,
    DiscussionTopic,
    DiscussionResult
)
from .gemini_helper import GeminiModelHelper, ensure_api_key

# Define the state structure for discussions
if LANGGRAPH_AVAILABLE:
    class DiscussionState(TypedDict):
        """State for agent discussions using TypedDict for LangGraph"""
        messages: Annotated[Sequence[BaseMessage], operator.add]
        topic: DiscussionTopic
        participants: List[AgentRole]
        round: int
        max_rounds: int
        consensus_level: float
        decisions: Dict[str, Any]
        key_insights: List[str]
        alternative_approaches: List[str]
        current_speaker: Optional[AgentRole]
        voting_results: Dict[str, Any]
        final_decision: Optional[Dict[str, Any]]
else:
    # Fallback when LangGraph is not available
    class DiscussionState(TypedDict):
        """State for agent discussions using TypedDict"""
        messages: List[Dict]
        topic: DiscussionTopic
        participants: List[AgentRole]
        round: int
        max_rounds: int
        consensus_level: float
        decisions: Dict[str, Any]
        key_insights: List[str]
        alternative_approaches: List[str]
        current_speaker: Optional[AgentRole]
        voting_results: Dict[str, Any]
        final_decision: Optional[Dict[str, Any]]
    
@dataclass
class AgentNode:
    """Represents an agent node in the discussion graph"""
    role: AgentRole
    name: str
    personality: str
    expertise: List[str]
    decision_style: str
    
class LangGraphDiscussionOrchestrator:
    """
    Advanced discussion orchestrator using LangGraph for state management
    and sophisticated agent coordination
    """
    
    def __init__(self, api_key: str, session_id: str):
        self.api_key = ensure_api_key(api_key)
        self.session_id = session_id
        # Get configured Gemini model using the helper
        self.model = GeminiModelHelper.get_configured_model(self.api_key)
        
        # Initialize memory for state persistence
        self.memory = MemorySaver() if LANGGRAPH_AVAILABLE else None
        
        # Agent configurations
        self.agent_configs = self._initialize_agent_configs()
        
        # Initialize dynamic agent systems
        self.meta_agent = None
        self.dynamic_agents = {}
        self._initialize_dynamic_agent_system()
        
        # Build the discussion graph
        self.graph = self._build_discussion_graph()
        
        logger.info(f"🚀 LangGraph Discussion Orchestrator initialized for session {session_id}")
        
    def _generate_content_safe(self, prompt: str) -> str:
        """Generate content using the Gemini model with error handling"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            # Return a fallback response if generation fails
            return "Error generating response. Please try again."
        
    def _initialize_agent_configs(self) -> Dict[AgentRole, AgentNode]:
        """Initialize agent configurations with enhanced capabilities"""
        return {
            AgentRole.NEUROSCIENTIST: AgentNode(
                role=AgentRole.NEUROSCIENTIST,
                name="NeuroBoost",
                personality="Scientific, analytical, brain-engagement focused",
                expertise=["neuroscience", "dopamine triggers", "attention mechanisms", "memory encoding"],
                decision_style="Evidence-based with neurological optimization"
            ),
            AgentRole.DIRECTOR: AgentNode(
                role=AgentRole.DIRECTOR,
                name="VisionMaster",
                personality="Creative visionary with strong aesthetic sense",
                expertise=["visual storytelling", "creative direction", "aesthetic choices"],
                decision_style="Creative with audience impact focus"
            ),
            AgentRole.SCRIPT_WRITER: AgentNode(
                role=AgentRole.SCRIPT_WRITER,
                name="WordSmith",
                personality="Creative storyteller with viral content expertise",
                expertise=["narrative structure", "viral hooks", "dialogue", "pacing"],
                decision_style="Story-driven with engagement priority"
            ),
            AgentRole.VIDEO_GENERATOR: AgentNode(
                role=AgentRole.VIDEO_GENERATOR,
                name="PixelForge",
                personality="Technical expert focused on AI video generation",
                expertise=["AI video generation", "VEO capabilities", "technical constraints"],
                decision_style="Technical feasibility with quality focus"
            ),
            AgentRole.SOUNDMAN: AgentNode(
                role=AgentRole.SOUNDMAN,
                name="AudioMaster",
                personality="Audio specialist focused on sound design",
                expertise=["audio production", "voice synthesis", "sound design"],
                decision_style="Audio-centric with synchronization priority"
            ),
            AgentRole.EDITOR: AgentNode(
                role=AgentRole.EDITOR,
                name="CutMaster",
                personality="Post-production expert focused on final polish",
                expertise=["video editing", "post-production", "quality control"],
                decision_style="Quality-focused with practical execution"
            ),
            AgentRole.ORCHESTRATOR: AgentNode(
                role=AgentRole.ORCHESTRATOR,
                name="SyncMaster",
                personality="Coordination expert focused on workflow",
                expertise=["workflow coordination", "agent synchronization", "resource management"],
                decision_style="Holistic with coordination priority"
            ),
            AgentRole.ENGAGEMENT_OPTIMIZER: AgentNode(
                role=AgentRole.ENGAGEMENT_OPTIMIZER,
                name="EngagePro",
                personality="Metrics-driven, interaction-focused",
                expertise=["engagement rates", "user behavior", "retention strategies"],
                decision_style="Engagement-maximizing with data support"
            ),
            AgentRole.VIRAL_SPECIALIST: AgentNode(
                role=AgentRole.VIRAL_SPECIALIST,
                name="ViralVault",
                personality="Trend-obsessed, shareability expert",
                expertise=["viral mechanics", "trend analysis", "viral triggers"],
                decision_style="Virality-maximizing with trend awareness"
            )
        }
        
    def _initialize_dynamic_agent_system(self):
        """Initialize the dynamic agent creation and management system"""
        try:
            # Import dynamic agent modules
            from src.agents.meta_agent_orchestrator import MetaAgentOrchestrator
            from src.agents.agent_discovery_system import AgentDiscoverySystem
            from src.agents.dynamic_agent_factory import DynamicAgentFactory
            
            # Initialize Meta-Agent with auto-spawn threshold
            self.meta_agent = MetaAgentOrchestrator(auto_spawn_threshold=0.85)
            
            # Initialize discovery system
            self.discovery_system = AgentDiscoverySystem()
            
            # Initialize agent factory
            self.agent_factory = DynamicAgentFactory()
            
            logger.info("🚀 Dynamic Agent System initialized successfully")
            logger.info(f"   Auto-spawn threshold: {self.meta_agent.auto_spawn_threshold}")
            logger.info("   Ready to spawn specialized agents as needed")
            
        except ImportError as e:
            logger.warning(f"⚠️ Dynamic Agent System not available: {e}")
            logger.warning("   Continuing without dynamic agent capabilities")
            self.meta_agent = None
            self.discovery_system = None
            self.agent_factory = None
        except Exception as e:
            logger.error(f"❌ Failed to initialize Dynamic Agent System: {e}")
            self.meta_agent = None
            self.discovery_system = None
            self.agent_factory = None
        
    def _build_discussion_graph(self) -> StateGraph:
        """Build the LangGraph discussion workflow"""
        if not StateGraph:
            logger.warning("LangGraph not available, using fallback")
            return None
            
        # Create the state graph
        workflow = StateGraph(DiscussionState)
        
        # Add nodes for each phase of discussion
        workflow.add_node("initialize", self._initialize_discussion)
        workflow.add_node("propose", self._agent_propose)
        workflow.add_node("critique", self._agent_critique)
        workflow.add_node("synthesize", self._synthesize_insights)
        workflow.add_node("vote", self._conduct_voting)
        workflow.add_node("consensus_check", self._check_consensus)
        workflow.add_node("finalize", self._finalize_decision)
        
        # Define the flow
        workflow.set_entry_point("initialize")
        
        workflow.add_edge("initialize", "propose")
        workflow.add_edge("propose", "critique")
        workflow.add_edge("critique", "synthesize")
        workflow.add_edge("synthesize", "vote")
        workflow.add_edge("vote", "consensus_check")
        
        # Conditional edges
        workflow.add_conditional_edges(
            "consensus_check",
            self._should_continue_discussion,
            {
                "continue": "propose",
                "finalize": "finalize"
            }
        )
        
        workflow.add_edge("finalize", END)
        
        # Compile the graph
        return workflow.compile(checkpointer=self.memory)
        
    def _initialize_discussion(self, state: DiscussionState) -> DiscussionState:
        """Initialize the discussion state"""
        logger.info(f"🎭 Initializing LangGraph discussion: {state['topic'].title}")
        
        # Add system message to set the context
        system_msg = SystemMessage(content=f"""
You are participating in a multi-agent discussion about: {state['topic'].title}

Context: {json.dumps(state['topic'].context, indent=2)}

Your goal is to collaboratively reach a decision on: {', '.join(state['topic'].required_decisions)}

Guidelines:
- Build on each other's ideas
- Consider neurological and psychological factors
- Focus on practical implementation
- Aim for consensus while maintaining critical thinking
""")
        
        state["messages"] = [system_msg]
        state["round"] = 1
        state["consensus_level"] = 0.0
        state["key_insights"] = []
        state["alternative_approaches"] = []
        
        return state
        
    def _agent_propose(self, state: DiscussionState) -> DiscussionState:
        """Agents propose solutions"""
        round_messages = []
        
        for participant in state["participants"]:
            if participant not in self.agent_configs:
                continue
                
            agent = self.agent_configs[participant]
            
            # Generate proposal from this agent
            prompt = f"""
As {agent.name} ({agent.role.value}), with expertise in {', '.join(agent.expertise)}, 
propose your solution for: {state['topic'].title}

Consider:
- Your personality: {agent.personality}
- Your decision style: {agent.decision_style}
- Previous messages in the discussion
- The need to reach consensus

Provide a clear, actionable proposal.
"""
            
            try:
                response = self._generate_content_safe(prompt)
                
                message = AIMessage(
                    content=response,
                    name=agent.name,
                    additional_kwargs={"role": agent.role.value}
                )
                round_messages.append(message)
                
                logger.info(f"💬 {agent.name} proposed: {response[:100]}...")
                
            except Exception as e:
                logger.error(f"Error generating proposal from {agent.name}: {e}")
                
        state["messages"].extend(round_messages)
        return state
        
    def _agent_critique(self, state: DiscussionState) -> DiscussionState:
        """Agents critique and refine proposals"""
        critique_messages = []
        
        # Get recent proposals to critique
        recent_proposals = [msg for msg in state["messages"][-len(state["participants"]):] 
                          if isinstance(msg, AIMessage)]
        
        for participant in state["participants"]:
            if participant not in self.agent_configs:
                continue
                
            agent = self.agent_configs[participant]
            
            # Special critique from neuroscientist
            if agent.role == AgentRole.NEUROSCIENTIST:
                critique_prompt = f"""
As {agent.name}, analyze the proposals from a neuroscience perspective:

Proposals to analyze:
{chr(10).join([f"- {msg.name}: {msg.content[:200]}" for msg in recent_proposals])}

Provide:
1. Neurological impact assessment (dopamine, attention, memory)
2. Suggested improvements for brain engagement
3. Specific triggers to incorporate
4. Expected cognitive response

Be constructive and specific.
"""
            else:
                critique_prompt = f"""
As {agent.name} ({agent.role.value}), critique and refine the proposals:

Proposals to analyze:
{chr(10).join([f"- {msg.name}: {msg.content[:200]}" for msg in recent_proposals])}

From your expertise in {', '.join(agent.expertise)}, provide:
1. Strengths of each proposal
2. Potential weaknesses or challenges
3. Suggested improvements
4. How proposals could be combined

Be constructive and collaborative.
"""
            
            try:
                response = self._generate_content_safe(critique_prompt)
                
                message = AIMessage(
                    content=response,
                    name=f"{agent.name}_critique",
                    additional_kwargs={"role": agent.role.value, "type": "critique"}
                )
                critique_messages.append(message)
                
                logger.info(f"🔍 {agent.name} critiqued: {response[:100]}...")
                
            except Exception as e:
                logger.error(f"Error generating critique from {agent.name}: {e}")
                
        state["messages"].extend(critique_messages)
        return state
        
    def _synthesize_insights(self, state: DiscussionState) -> DiscussionState:
        """Synthesize insights from the discussion"""
        
        # Extract key insights using AI
        synthesis_prompt = f"""
Analyze the discussion so far and extract:

1. Key insights that have emerged
2. Points of agreement
3. Points of disagreement
4. Alternative approaches suggested
5. Neurological/psychological factors identified

Discussion context: {state['topic'].title}

Recent messages:
{chr(10).join([f"- {msg.name if hasattr(msg, 'name') else 'System'}: {msg.content[:300]}" 
               for msg in state["messages"][-10:]])}

Provide a structured synthesis.
"""
        
        try:
            synthesis = self._generate_content_safe(synthesis_prompt)
            
            # Parse synthesis to extract insights
            if "key insights" in synthesis.lower():
                # Simple extraction - could be improved with structured output
                insights = [line.strip() for line in synthesis.split('\n') 
                          if line.strip() and not line.startswith('#')]
                state["key_insights"].extend(insights[:5])
            
            state["messages"].append(
                SystemMessage(content=f"Synthesis Round {state['round']}: {synthesis}")
            )
            
            logger.info(f"✨ Synthesized {len(state['key_insights'])} key insights")
            
        except Exception as e:
            logger.error(f"Error synthesizing insights: {e}")
            
        return state
        
    def _conduct_voting(self, state: DiscussionState) -> DiscussionState:
        """Conduct voting on proposals"""
        voting_results = {}
        
        # Collect votes from each agent
        for participant in state["participants"]:
            if participant not in self.agent_configs:
                continue
                
            agent = self.agent_configs[participant]
            
            # Use JSON mode for structured voting
            vote_prompt = f"""
As {agent.name}, vote on the best approach based on the discussion.

Consider:
- Your expertise in {', '.join(agent.expertise)}
- The neurological insights provided
- Practical feasibility
- Expected impact

Respond with a JSON object containing:
{{
    "vote": <integer 1-10>,
    "reasoning": "<brief explanation>",
    "concerns": "<any critical concerns or null>"
}}

Where vote is your score from 1 (strongly disagree) to 10 (strongly agree).
"""
            
            try:
                # Try to use JSON mode if available
                import google.generativeai as genai
                
                # Configure the API with v1beta for JSON mode support
                genai.configure(api_key=self.api_key)
                
                # Configure model with JSON mode using gemini-2.5-flash (not lite)
                generation_config = genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema={
                        "type": "object",
                        "properties": {
                            "vote": {"type": "integer", "minimum": 1, "maximum": 10},
                            "reasoning": {"type": "string"}
                        },
                        "required": ["vote", "reasoning"]
                    }
                )
                
                # Create model with JSON configuration using gemini-2.5-flash
                json_model = genai.GenerativeModel(
                    model_name="gemini-2.5-flash",
                    generation_config=generation_config
                )
                
                # Generate structured response
                json_response = json_model.generate_content(vote_prompt)
                
                # Parse JSON response
                import json
                vote_data = json.loads(json_response.text)
                
                score = vote_data.get("vote", 7)
                reasoning = vote_data.get("reasoning", "Agreement with proposal")
                
                # Validate score
                if not (1 <= score <= 10):
                    logger.warning(f"Invalid vote {score} from {agent.name}, using 7")
                    score = 7
                
                voting_results[agent.role.value] = {
                    "score": score,
                    "reasoning": reasoning[:200]
                }
                
                logger.info(f"🗳️ {agent.name} voted: {score}/10 (JSON mode)")
                
            except Exception as json_error:
                # Fallback to regex extraction if JSON mode fails
                logger.debug(f"JSON mode failed: {json_error}, using fallback")
                
                try:
                    response = self._generate_content_safe(vote_prompt)
                    
                    # Try to parse as JSON first
                    try:
                        import json
                        vote_data = json.loads(response)
                        score = vote_data.get("vote", 7)
                        reasoning = vote_data.get("reasoning", response[:200])
                    except:
                        # Extract vote score with regex
                        import re
                        patterns = [
                            r'"vote":\s*(\d+)',  # JSON format
                            r'(?:vote|score|rating)[\s:]+(\d+)(?:/10)?',
                            r'(\d+)(?:/10|out of 10)',
                            r'\b(10|[1-9])\b(?!/)',
                        ]
                        
                        score = 7  # More positive default
                        for pattern in patterns:
                            match = re.search(pattern, response, re.IGNORECASE)
                            if match:
                                potential_score = int(match.group(1))
                                if 1 <= potential_score <= 10:
                                    score = potential_score
                                    break
                        
                        # Infer from content if still default
                        if score == 7:
                            if any(word in response.lower() for word in ['excellent', 'perfect', 'strongly agree']):
                                score = 9
                            elif any(word in response.lower() for word in ['agree', 'good', 'support']):
                                score = 8
                            elif any(word in response.lower() for word in ['disagree', 'concern', 'issue']):
                                score = 4
                        
                        reasoning = response[:200]
                    
                    voting_results[agent.role.value] = {
                        "score": score,
                        "reasoning": reasoning
                    }
                    
                    logger.info(f"🗳️ {agent.name} voted: {score}/10 (fallback)")
                    
                except Exception as e:
                    logger.error(f"Error getting vote from {agent.name}: {e}")
                    voting_results[agent.role.value] = {"score": 7, "reasoning": "Default agreement"}
                
        state["voting_results"] = voting_results
        
        # Calculate consensus level
        if voting_results:
            scores = [v["score"] for v in voting_results.values()]
            state["consensus_level"] = sum(scores) / (len(scores) * 10)
        
        return state
        
    def _check_consensus(self, state: DiscussionState) -> DiscussionState:
        """Check if consensus has been reached"""
        logger.info(f"📊 Consensus level: {state['consensus_level']:.2f} (Round {state['round']}/{state['max_rounds']})")
        
        state["round"] += 1
        return state
        
    def _should_continue_discussion(self, state: DiscussionState) -> str:
        """Determine if discussion should continue"""
        min_consensus = state["topic"].min_consensus
        
        if state["consensus_level"] >= min_consensus:
            return "finalize"
        elif state["round"] >= state["max_rounds"]:
            logger.info("⏰ Max rounds reached, finalizing with current consensus")
            return "finalize"
        else:
            logger.info(f"🔄 Continuing discussion (consensus: {state['consensus_level']:.2f} < {min_consensus})")
            return "continue"
            
    def _finalize_decision(self, state: DiscussionState) -> DiscussionState:
        """Finalize the decision based on discussion"""
        
        # Create final decision summary
        final_prompt = f"""
Based on the entire discussion about {state['topic'].title}, create a final decision.

Key insights identified:
{chr(10).join(state['key_insights'][:10])}

Voting results:
{json.dumps(state['voting_results'], indent=2)}

Consensus level: {state['consensus_level']:.2f}

Provide a structured final decision covering:
{chr(10).join(state['topic'].required_decisions)}

Include specific neurological optimizations identified.
"""
        
        try:
            final_decision = self._generate_content_safe(final_prompt)
            
            state["final_decision"] = {
                "decision": final_decision,
                "consensus_level": state["consensus_level"],
                "rounds_taken": state["round"],
                "key_insights": state["key_insights"][:5],
                "neurological_optimizations": self._extract_neuro_optimizations(state)
            }
            
            logger.info(f"✅ Final decision reached with {state['consensus_level']:.2f} consensus")
            
        except Exception as e:
            logger.error(f"Error finalizing decision: {e}")
            state["final_decision"] = {
                "decision": "Error in finalization",
                "consensus_level": state["consensus_level"]
            }
            
        return state
        
    def _extract_neuro_optimizations(self, state: DiscussionState) -> List[str]:
        """Extract neurological optimizations from the discussion"""
        neuro_optimizations = []
        
        for msg in state["messages"]:
            if isinstance(msg, AIMessage) and "neuro" in msg.content.lower():
                # Extract optimization points (simple extraction)
                lines = msg.content.split('\n')
                for line in lines:
                    if any(word in line.lower() for word in ['dopamine', 'attention', 'memory', 'trigger']):
                        neuro_optimizations.append(line.strip())
                        
        return neuro_optimizations[:5]
        
    def run_discussion(self, topic: DiscussionTopic, participants: List[AgentRole]) -> DiscussionResult:
        """
        Run a discussion using the LangGraph workflow
        
        Args:
            topic: The discussion topic
            participants: List of participating agents
            
        Returns:
            DiscussionResult with the final decision
        """
        if not self.graph:
            logger.warning("LangGraph not available, falling back to simple discussion")
            return self._fallback_discussion(topic, participants)
            
        logger.info(f"🚀 Starting LangGraph discussion: {topic.title}")
        logger.info(f"👥 Participants: {[p.value for p in participants]}")
        
        # Initialize state
        initial_state = {
            "messages": [],
            "topic": topic,
            "participants": participants,
            "round": 0,
            "max_rounds": topic.max_rounds,
            "consensus_level": 0.0,
            "decisions": {},
            "key_insights": [],
            "alternative_approaches": [],
            "current_speaker": None,
            "voting_results": {},
            "final_decision": None
        }
        
        # Run the graph
        try:
            # Execute the workflow
            config = {"configurable": {"thread_id": f"{self.session_id}_{topic.topic_id}"}}
            final_state = self.graph.invoke(initial_state, config)
            
            # Convert to DiscussionResult
            result = DiscussionResult(
                topic_id=topic.topic_id,
                decision=final_state.get("final_decision", {}),
                consensus_level=final_state["consensus_level"],
                total_rounds=final_state["round"],
                participating_agents=[p.value for p in participants],
                key_insights=final_state["key_insights"],
                alternative_approaches=final_state.get("alternative_approaches", [])
            )
            
            logger.info(f"✅ LangGraph discussion completed: {result.consensus_level:.2f} consensus in {result.total_rounds} rounds")
            
            # Save discussion to session output folder
            self._save_discussion_to_session(topic, result, final_state)
            
            return result
            
        except Exception as e:
            logger.error(f"Error running LangGraph discussion: {e}")
            return self._fallback_discussion(topic, participants)
            
    def _fallback_discussion(self, topic: DiscussionTopic, participants: List[AgentRole]) -> DiscussionResult:
        """Fallback discussion method if LangGraph fails"""
        logger.info("Using fallback discussion method")
        
        # Simple discussion simulation
        decision = {
            "approach": "Simplified decision due to LangGraph unavailability",
            "neurological_factors": ["Basic dopamine triggers", "Attention hooks"],
            "implementation": "Standard implementation approach"
        }
        
        return DiscussionResult(
            topic_id=topic.topic_id,
            decision=decision,
            consensus_level=0.7,
            total_rounds=1,
            participating_agents=[p.value for p in participants],
            key_insights=["Fallback mode - limited insights"],
            alternative_approaches=[]
        )
        
    def _save_discussion_to_session(self, topic: DiscussionTopic, result: DiscussionResult, final_state: Dict):
        """Save LangGraph discussion results to session output folder"""
        try:
            # Import here to avoid circular dependency
            from ..utils.session_context import SessionContext
            
            # Get current session context
            session_context = SessionContext.get_instance() if hasattr(SessionContext, 'get_instance') else None
            if not session_context:
                # Try to get from session_id
                if self.session_id:
                    from ..utils.session_context import create_session_context
                    session_context = create_session_context(self.session_id)
                else:
                    logger.warning("No session context available to save LangGraph discussion")
                    return
            
            # Create langgraph discussions folder
            langgraph_dir = session_context.get_output_path("langgraph_discussions")
            os.makedirs(langgraph_dir, exist_ok=True)
            
            # Save full discussion state
            state_file = os.path.join(langgraph_dir, f"discussion_{topic.topic_id}_state.json")
            with open(state_file, 'w', encoding='utf-8') as f:
                # Convert messages to serializable format
                serializable_state = {
                    "topic": topic.topic_id,
                    "round": final_state.get("round", 0),
                    "consensus_level": final_state.get("consensus_level", 0),
                    "key_insights": final_state.get("key_insights", []),
                    "messages": [
                        {
                            "type": msg.__class__.__name__,
                            "content": msg.content,
                            "agent": getattr(msg, 'agent', 'unknown')
                        }
                        for msg in final_state.get("messages", [])
                    ],
                    "final_decision": final_state.get("final_decision", {}),
                    "alternative_approaches": final_state.get("alternative_approaches", [])
                }
                json.dump(serializable_state, f, indent=2, ensure_ascii=False)
            
            # Save result summary
            result_file = os.path.join(langgraph_dir, f"discussion_{topic.topic_id}_result.json")
            with open(result_file, 'w', encoding='utf-8') as f:
                result_data = {
                    "topic_id": result.topic_id,
                    "decision": result.decision,
                    "consensus_level": result.consensus_level,
                    "total_rounds": result.total_rounds,
                    "participating_agents": result.participating_agents,
                    "key_insights": result.key_insights,
                    "alternative_approaches": result.alternative_approaches,
                    "timestamp": datetime.now().isoformat()
                }
                json.dump(result_data, f, indent=2, ensure_ascii=False)
            
            # Save visualization
            viz_file = os.path.join(langgraph_dir, f"discussion_{topic.topic_id}_visualization.md")
            with open(viz_file, 'w', encoding='utf-8') as f:
                f.write(f"# LangGraph Discussion: {topic.topic_id}\n\n")
                f.write(f"**Consensus Level:** {result.consensus_level:.2f}\n")
                f.write(f"**Total Rounds:** {result.total_rounds}\n")
                f.write(f"**Participants:** {', '.join(result.participating_agents)}\n\n")
                
                f.write("## Key Insights\n")
                for i, insight in enumerate(result.key_insights, 1):
                    f.write(f"{i}. {insight}\n")
                
                f.write("\n## Decision\n")
                f.write(f"```json\n{json.dumps(result.decision, indent=2, ensure_ascii=False)}\n```\n")
                
                if result.alternative_approaches:
                    f.write("\n## Alternative Approaches\n")
                    for i, approach in enumerate(result.alternative_approaches, 1):
                        f.write(f"{i}. {approach}\n")
            
            logger.info(f"💾 LangGraph discussion saved to: {langgraph_dir}")
            
        except Exception as e:
            logger.warning(f"Could not save LangGraph discussion: {e}")
    
    def visualize_discussion_graph(self) -> str:
        """Generate a visual representation of the discussion flow"""
        if not self.graph:
            return "Graph visualization not available"
            
        try:
            # Get the graph structure
            graph_repr = """
LangGraph Discussion Flow:
========================

[Initialize] 
     ↓
[Propose] ← ─ ─ ─ ─ ─ ┐
     ↓                 │
[Critique]             │
     ↓                 │
[Synthesize]           │ (if no consensus)
     ↓                 │
[Vote]                 │
     ↓                 │
[Consensus Check] ─ ─ ┘
     ↓ (if consensus reached)
[Finalize]
     ↓
[END]

Features:
- State persistence with MemorySaver
- Neurological optimization integration
- Multi-round consensus building
- Parallel agent proposals
- Structured critique and synthesis
"""
            return graph_repr
            
        except Exception as e:
            logger.error(f"Error visualizing graph: {e}")
            return "Error generating visualization"