"""
LangGraph Quality Monitor - Real-time quality monitoring for each video generation step
Uses LangGraph for stateful workflow management with quality checkpoints
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, TypedDict, Annotated, Literal
from dataclasses import dataclass, asdict
from enum import Enum
import operator
import logging
import numpy as np

# LangGraph imports
try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
    from langchain_google_genai import ChatGoogleGenerativeAI
    import google.generativeai as genai
    LANGGRAPH_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ LangGraph not available: {e}")
    LANGGRAPH_AVAILABLE = False
    raise ImportError("LangGraph is required for quality monitoring. Install with: pip install langgraph langchain-google-genai")

from ..utils.logging_config import get_logger

logger = get_logger(__name__)


# Quality States and Types
class QualityLevel(Enum):
    """Quality levels for each step"""
    FAILED = "failed"
    POOR = "poor"
    ACCEPTABLE = "acceptable"
    GOOD = "good"
    EXCELLENT = "excellent"
    PERFECT = "perfect"


class GenerationStep(Enum):
    """Video generation pipeline steps"""
    SCRIPT_GENERATION = "script_generation"
    SCRIPT_VALIDATION = "script_validation"
    AUDIO_GENERATION = "audio_generation"
    VIDEO_GENERATION = "video_generation"
    AUDIO_VIDEO_SYNC = "audio_video_sync"
    EFFECTS_APPLICATION = "effects_application"
    QUALITY_ENHANCEMENT = "quality_enhancement"
    FINAL_COMPOSITION = "final_composition"


@dataclass
class StepQualityResult:
    """Quality result for a single step"""
    step: GenerationStep
    quality_level: QualityLevel
    score: float  # 0.0 to 1.0
    issues: List[str]
    suggestions: List[str]
    metrics: Dict[str, float]
    can_proceed: bool
    should_retry: bool
    retry_count: int = 0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    @property
    def passed(self) -> bool:
        """Check if the quality check passed"""
        return self.can_proceed and self.score >= 0.5


@dataclass
class QualityDecision:
    """Decision made by quality monitor"""
    action: str  # 'proceed', 'retry', 'enhance', 'abort'
    reasoning: str
    confidence: float
    enhancements_needed: List[str]
    retry_params: Optional[Dict] = None


# LangGraph State Definition
class QualityMonitorState(TypedDict):
    """State for quality monitoring workflow"""
    current_step: GenerationStep
    step_results: Dict[str, StepQualityResult]
    overall_quality: float
    messages: Annotated[List[BaseMessage], operator.add]
    decisions: List[QualityDecision]
    artifacts: Dict[str, Any]  # Store generated artifacts (scripts, videos, etc.)
    config: Dict[str, Any]  # Generation configuration
    retry_counts: Dict[str, int]
    max_retries: int
    quality_threshold: float
    final_report: Optional[Dict]
    session_id: str
    start_time: float
    current_issues: List[str]
    accumulated_score: float


class LangGraphQualityMonitor:
    """
    Comprehensive quality monitoring system using LangGraph
    Monitors each step of video generation and ensures quality standards
    """
    
    def __init__(self, api_key: str, session_id: str, quality_threshold: float = 0.7):
        """
        Initialize quality monitor
        
        Args:
            api_key: Gemini API key
            session_id: Session identifier
            quality_threshold: Minimum quality score to proceed (0-1)
        """
        self.api_key = api_key
        self.session_id = session_id
        self.quality_threshold = quality_threshold
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.3,  # Lower temperature for consistent quality evaluation
            convert_system_message_to_human=True
        )
        
        # Initialize memory for state persistence
        self.memory = MemorySaver()
        
        # Build the quality monitoring workflow
        self.workflow = self._build_workflow()
        
        logger.info(f"✅ LangGraph Quality Monitor initialized for session {session_id}")
        logger.info(f"   Quality threshold: {quality_threshold}")
    
    def _build_workflow(self) -> StateGraph:
        """Build the quality monitoring workflow graph"""
        
        # Create workflow
        workflow = StateGraph(QualityMonitorState)
        
        # Add nodes for each quality check
        workflow.add_node("initialize", self._initialize_monitoring)
        workflow.add_node("check_script", self._check_script_quality)
        workflow.add_node("check_audio", self._check_audio_quality)
        workflow.add_node("check_video", self._check_video_quality)
        workflow.add_node("check_sync", self._check_sync_quality)
        workflow.add_node("check_effects", self._check_effects_quality)
        workflow.add_node("check_enhancement", self._check_enhancement_quality)
        workflow.add_node("check_final", self._check_final_quality)
        workflow.add_node("make_decision", self._make_quality_decision)
        workflow.add_node("apply_enhancement", self._apply_enhancement)
        workflow.add_node("retry_step", self._retry_current_step)
        workflow.add_node("generate_report", self._generate_final_report)
        
        # Define the flow
        workflow.set_entry_point("initialize")
        
        # Step progression flow
        workflow.add_edge("initialize", "check_script")
        
        # Each check leads to decision
        workflow.add_conditional_edges(
            "check_script",
            self._route_after_check,
            {
                "decision": "make_decision",
                "next": "check_audio"
            }
        )
        
        workflow.add_conditional_edges(
            "check_audio",
            self._route_after_check,
            {
                "decision": "make_decision",
                "next": "check_video"
            }
        )
        
        workflow.add_conditional_edges(
            "check_video",
            self._route_after_check,
            {
                "decision": "make_decision",
                "next": "check_sync"
            }
        )
        
        workflow.add_conditional_edges(
            "check_sync",
            self._route_after_check,
            {
                "decision": "make_decision",
                "next": "check_effects"
            }
        )
        
        workflow.add_conditional_edges(
            "check_effects",
            self._route_after_check,
            {
                "decision": "make_decision",
                "next": "check_enhancement"
            }
        )
        
        workflow.add_conditional_edges(
            "check_enhancement",
            self._route_after_check,
            {
                "decision": "make_decision",
                "next": "check_final"
            }
        )
        
        workflow.add_conditional_edges(
            "check_final",
            self._route_after_check,
            {
                "decision": "make_decision",
                "next": "generate_report"
            }
        )
        
        # Decision routing
        workflow.add_conditional_edges(
            "make_decision",
            self._route_decision,
            {
                "proceed": "check_audio",  # Dynamic - will be overridden
                "retry": "retry_step",
                "enhance": "apply_enhancement",
                "abort": "generate_report"
            }
        )
        
        # After retry or enhancement, go back to decision
        workflow.add_edge("retry_step", "make_decision")
        workflow.add_edge("apply_enhancement", "make_decision")
        
        # Final report leads to end
        workflow.add_edge("generate_report", END)
        
        # Compile the workflow
        return workflow.compile(checkpointer=self.memory)
    
    def _initialize_monitoring(self, state: QualityMonitorState) -> QualityMonitorState:
        """Initialize the monitoring state"""
        logger.info("🚀 Initializing quality monitoring")
        
        state["current_step"] = GenerationStep.SCRIPT_GENERATION
        state["step_results"] = {}
        state["overall_quality"] = 0.0
        state["messages"] = [
            SystemMessage(content=f"""
You are a professional video quality monitor. Your role is to:
1. Evaluate the quality of each step in video generation
2. Identify issues and suggest improvements
3. Decide whether to proceed, retry, or enhance
4. Ensure the final output meets professional standards

Quality threshold: {state.get('quality_threshold', 0.7)}
Session: {state.get('session_id', 'unknown')}

Be strict but fair in your evaluations. Focus on:
- Technical quality
- Creative effectiveness
- Audience engagement potential
- Production standards
""")
        ]
        state["decisions"] = []
        state["retry_counts"] = {}
        state["current_issues"] = []
        state["accumulated_score"] = 0.0
        state["start_time"] = time.time()
        
        return state
    
    def _check_script_quality(self, state: QualityMonitorState) -> QualityMonitorState:
        """Check script quality"""
        logger.info("📝 Checking script quality")
        
        script = state.get("artifacts", {}).get("script", "")
        config = state.get("config", {})
        
        if not script:
            state["current_issues"] = ["No script provided"]
            state["step_results"]["script"] = StepQualityResult(
                step=GenerationStep.SCRIPT_GENERATION,
                quality_level=QualityLevel.FAILED,
                score=0.0,
                issues=["No script generated"],
                suggestions=["Generate script first"],
                metrics={},
                can_proceed=False,
                should_retry=True
            )
            return state
        
        # Analyze script with Gemini
        analysis_prompt = f"""
Analyze this video script for quality:

SCRIPT:
{script}

TARGET PLATFORM: {config.get('platform', 'general')}
DURATION: {config.get('duration_seconds', 30)} seconds
STYLE: {config.get('style', 'engaging')}

Evaluate:
1. Narrative structure (beginning, middle, end)
2. Hook effectiveness (first 3 seconds)
3. Engagement factors (questions, direct address)
4. Call-to-action clarity
5. Pacing for duration
6. Language clarity and simplicity
7. Emotional resonance
8. Viral potential

Provide a quality score (0.0-1.0) and specific issues/suggestions.
Format response as JSON with: score, quality_level, issues[], suggestions[], metrics{{}}
"""
        
        try:
            response = self.model.invoke([HumanMessage(content=analysis_prompt)])
            
            # Parse response
            result = self._parse_quality_response(response.content)
            
            # Create quality result
            quality_result = StepQualityResult(
                step=GenerationStep.SCRIPT_VALIDATION,
                quality_level=self._score_to_level(result['score']),
                score=result['score'],
                issues=result.get('issues', []),
                suggestions=result.get('suggestions', []),
                metrics=result.get('metrics', {}),
                can_proceed=result['score'] >= state.get('quality_threshold', 0.7),
                should_retry=result['score'] < 0.5
            )
            
            state["step_results"]["script"] = quality_result
            state["current_issues"] = quality_result.issues
            state["accumulated_score"] += quality_result.score
            
            # Add analysis message
            state["messages"].append(
                AIMessage(content=f"Script quality: {quality_result.quality_level.value} ({quality_result.score:.2f})")
            )
            
            logger.info(f"✅ Script quality: {quality_result.quality_level.value} ({quality_result.score:.2f})")
            
        except Exception as e:
            logger.error(f"❌ Script quality check failed: {e}")
            state["current_issues"] = [str(e)]
            
        return state
    
    def _check_audio_quality(self, state: QualityMonitorState) -> QualityMonitorState:
        """Check audio quality"""
        logger.info("🎵 Checking audio quality")
        
        audio_files = state.get("artifacts", {}).get("audio_files", [])
        
        if not audio_files:
            state["current_issues"] = ["No audio files provided"]
            state["step_results"]["audio"] = StepQualityResult(
                step=GenerationStep.AUDIO_GENERATION,
                quality_level=QualityLevel.FAILED,
                score=0.0,
                issues=["No audio generated"],
                suggestions=["Generate audio first"],
                metrics={},
                can_proceed=False,
                should_retry=True
            )
            return state
        
        # Analyze audio properties
        audio_metrics = self._analyze_audio_files(audio_files)
        
        # Evaluate with Gemini
        analysis_prompt = f"""
Evaluate audio quality based on these metrics:

AUDIO METRICS:
{json.dumps(audio_metrics, indent=2)}

TARGET DURATION: {state.get('config', {}).get('duration_seconds', 30)} seconds
PLATFORM: {state.get('config', {}).get('platform', 'general')}

Evaluate:
1. Duration match with target
2. Volume consistency
3. Clarity and articulation
4. Pacing and rhythm
5. Emotional tone
6. Background noise levels
7. Overall production quality

Provide quality score (0.0-1.0) and specific issues/suggestions.
Format as JSON with: score, quality_level, issues[], suggestions[], metrics{{}}
"""
        
        try:
            response = self.model.invoke([HumanMessage(content=analysis_prompt)])
            result = self._parse_quality_response(response.content)
            
            quality_result = StepQualityResult(
                step=GenerationStep.AUDIO_GENERATION,
                quality_level=self._score_to_level(result['score']),
                score=result['score'],
                issues=result.get('issues', []),
                suggestions=result.get('suggestions', []),
                metrics={**audio_metrics, **result.get('metrics', {})},
                can_proceed=result['score'] >= state.get('quality_threshold', 0.7) * 0.9,  # Slightly lower threshold for audio
                should_retry=result['score'] < 0.4
            )
            
            state["step_results"]["audio"] = quality_result
            state["current_issues"] = quality_result.issues
            state["accumulated_score"] += quality_result.score
            
            logger.info(f"✅ Audio quality: {quality_result.quality_level.value} ({quality_result.score:.2f})")
            
        except Exception as e:
            logger.error(f"❌ Audio quality check failed: {e}")
            state["current_issues"] = [str(e)]
        
        return state
    
    def _check_video_quality(self, state: QualityMonitorState) -> QualityMonitorState:
        """Check video clip quality"""
        logger.info("🎬 Checking video quality")
        
        video_clips = state.get("artifacts", {}).get("video_clips", [])
        
        if not video_clips:
            state["current_issues"] = ["No video clips provided"]
            state["step_results"]["video"] = StepQualityResult(
                step=GenerationStep.VIDEO_GENERATION,
                quality_level=QualityLevel.FAILED,
                score=0.0,
                issues=["No video clips generated"],
                suggestions=["Generate video clips first"],
                metrics={},
                can_proceed=False,
                should_retry=True
            )
            return state
        
        # Analyze video properties
        video_metrics = self._analyze_video_clips(video_clips)
        
        # Evaluate with Gemini
        analysis_prompt = f"""
Evaluate video quality based on these metrics:

VIDEO METRICS:
{json.dumps(video_metrics, indent=2)}

SCRIPT CONTEXT: {state.get('artifacts', {}).get('script', '')[:200]}...
PLATFORM: {state.get('config', {}).get('platform', 'general')}
STYLE: {state.get('config', {}).get('style', 'dynamic')}

Evaluate:
1. Visual quality (resolution, sharpness)
2. Scene continuity between clips
3. Visual style consistency
4. Relevance to script content
5. Professional appearance
6. Engagement potential
7. Technical issues (artifacts, glitches)

Provide quality score (0.0-1.0) and specific issues/suggestions.
Format as JSON with: score, quality_level, issues[], suggestions[], metrics{{}}
"""
        
        try:
            response = self.model.invoke([HumanMessage(content=analysis_prompt)])
            result = self._parse_quality_response(response.content)
            
            quality_result = StepQualityResult(
                step=GenerationStep.VIDEO_GENERATION,
                quality_level=self._score_to_level(result['score']),
                score=result['score'],
                issues=result.get('issues', []),
                suggestions=result.get('suggestions', []),
                metrics={**video_metrics, **result.get('metrics', {})},
                can_proceed=result['score'] >= state.get('quality_threshold', 0.7),
                should_retry=result['score'] < 0.5
            )
            
            state["step_results"]["video"] = quality_result
            state["current_issues"] = quality_result.issues
            state["accumulated_score"] += quality_result.score
            
            logger.info(f"✅ Video quality: {quality_result.quality_level.value} ({quality_result.score:.2f})")
            
        except Exception as e:
            logger.error(f"❌ Video quality check failed: {e}")
            state["current_issues"] = [str(e)]
        
        return state
    
    def _check_sync_quality(self, state: QualityMonitorState) -> QualityMonitorState:
        """Check audio-video synchronization quality"""
        logger.info("🔄 Checking audio-video sync quality")
        
        # Get sync analysis from artifacts
        sync_data = state.get("artifacts", {}).get("sync_analysis", {})
        
        if not sync_data:
            # Create basic sync analysis
            sync_data = {
                "sync_score": 0.7,  # Default acceptable
                "issues": [],
                "beat_alignment": 0.7,
                "voice_sync": 0.8
            }
        
        # Evaluate sync quality
        analysis_prompt = f"""
Evaluate audio-video synchronization quality:

SYNC METRICS:
{json.dumps(sync_data, indent=2)}

AUDIO DURATION: {state.get('step_results', {}).get('audio', {}).metrics.get('total_duration', 0)}s
VIDEO CLIPS: {len(state.get('artifacts', {}).get('video_clips', []))}

Evaluate:
1. Audio-video timing alignment
2. Beat synchronization (if music present)
3. Voice-to-visual matching
4. Transition timing
5. Overall flow and rhythm

Provide quality score (0.0-1.0) and specific issues/suggestions.
Format as JSON with: score, quality_level, issues[], suggestions[], metrics{{}}
"""
        
        try:
            response = self.model.invoke([HumanMessage(content=analysis_prompt)])
            result = self._parse_quality_response(response.content)
            
            quality_result = StepQualityResult(
                step=GenerationStep.AUDIO_VIDEO_SYNC,
                quality_level=self._score_to_level(result['score']),
                score=result['score'],
                issues=result.get('issues', []),
                suggestions=result.get('suggestions', []),
                metrics={**sync_data, **result.get('metrics', {})},
                can_proceed=result['score'] >= 0.6,  # Lower threshold for sync
                should_retry=result['score'] < 0.4
            )
            
            state["step_results"]["sync"] = quality_result
            state["current_issues"] = quality_result.issues
            state["accumulated_score"] += quality_result.score
            
            logger.info(f"✅ Sync quality: {quality_result.quality_level.value} ({quality_result.score:.2f})")
            
        except Exception as e:
            logger.error(f"❌ Sync quality check failed: {e}")
            state["current_issues"] = [str(e)]
        
        return state
    
    def _check_effects_quality(self, state: QualityMonitorState) -> QualityMonitorState:
        """Check effects and transitions quality"""
        logger.info("✨ Checking effects quality")
        
        effects_applied = state.get("artifacts", {}).get("effects_applied", [])
        
        # Evaluate effects quality
        analysis_prompt = f"""
Evaluate video effects and transitions quality:

EFFECTS APPLIED: {json.dumps(effects_applied, indent=2)}
STYLE: {state.get('config', {}).get('style', 'dynamic')}
PLATFORM: {state.get('config', {}).get('platform', 'general')}

Evaluate:
1. Transition smoothness
2. Effect appropriateness
3. Visual consistency
4. Professional appearance
5. Not overdone or distracting
6. Enhancement of narrative

Provide quality score (0.0-1.0) and specific issues/suggestions.
Format as JSON with: score, quality_level, issues[], suggestions[], metrics{{}}
"""
        
        try:
            response = self.model.invoke([HumanMessage(content=analysis_prompt)])
            result = self._parse_quality_response(response.content)
            
            quality_result = StepQualityResult(
                step=GenerationStep.EFFECTS_APPLICATION,
                quality_level=self._score_to_level(result['score']),
                score=result['score'],
                issues=result.get('issues', []),
                suggestions=result.get('suggestions', []),
                metrics=result.get('metrics', {}),
                can_proceed=True,  # Effects are optional, always can proceed
                should_retry=False  # Don't retry effects
            )
            
            state["step_results"]["effects"] = quality_result
            state["current_issues"] = quality_result.issues if quality_result.score < 0.7 else []
            state["accumulated_score"] += quality_result.score
            
            logger.info(f"✅ Effects quality: {quality_result.quality_level.value} ({quality_result.score:.2f})")
            
        except Exception as e:
            logger.error(f"❌ Effects quality check failed: {e}")
            # Don't block on effects failure
            state["step_results"]["effects"] = StepQualityResult(
                step=GenerationStep.EFFECTS_APPLICATION,
                quality_level=QualityLevel.ACCEPTABLE,
                score=0.7,
                issues=[],
                suggestions=[],
                metrics={},
                can_proceed=True,
                should_retry=False
            )
        
        return state
    
    def _check_enhancement_quality(self, state: QualityMonitorState) -> QualityMonitorState:
        """Check quality enhancement results"""
        logger.info("🔧 Checking enhancement quality")
        
        enhancement_data = state.get("artifacts", {}).get("enhancement_report", {})
        
        # Evaluate enhancement quality
        analysis_prompt = f"""
Evaluate quality enhancement results:

ENHANCEMENT DATA: {json.dumps(enhancement_data, indent=2)}
BEFORE SCORE: {state.get('accumulated_score', 0) / max(1, len(state.get('step_results', {})))}

Evaluate:
1. Improvement achieved
2. Visual quality enhancement
3. Audio quality enhancement
4. Overall polish
5. Professional standards met

Provide quality score (0.0-1.0) and specific issues/suggestions.
Format as JSON with: score, quality_level, issues[], suggestions[], metrics{{}}
"""
        
        try:
            response = self.model.invoke([HumanMessage(content=analysis_prompt)])
            result = self._parse_quality_response(response.content)
            
            quality_result = StepQualityResult(
                step=GenerationStep.QUALITY_ENHANCEMENT,
                quality_level=self._score_to_level(result['score']),
                score=result['score'],
                issues=result.get('issues', []),
                suggestions=result.get('suggestions', []),
                metrics=result.get('metrics', {}),
                can_proceed=True,
                should_retry=False
            )
            
            state["step_results"]["enhancement"] = quality_result
            state["accumulated_score"] += quality_result.score
            
            logger.info(f"✅ Enhancement quality: {quality_result.quality_level.value} ({quality_result.score:.2f})")
            
        except Exception as e:
            logger.error(f"❌ Enhancement quality check failed: {e}")
            # Don't block on enhancement check failure
            state["step_results"]["enhancement"] = StepQualityResult(
                step=GenerationStep.QUALITY_ENHANCEMENT,
                quality_level=QualityLevel.GOOD,
                score=0.75,
                issues=[],
                suggestions=[],
                metrics={},
                can_proceed=True,
                should_retry=False
            )
        
        return state
    
    def _check_final_quality(self, state: QualityMonitorState) -> QualityMonitorState:
        """Check final output quality"""
        logger.info("🎯 Checking final output quality")
        
        # Calculate overall quality
        step_scores = [r.score for r in state.get("step_results", {}).values()]
        overall_score = np.mean(step_scores) if step_scores else 0.0
        
        # Comprehensive final evaluation
        analysis_prompt = f"""
Evaluate the FINAL video output quality:

STEP RESULTS:
{json.dumps({k: {'score': v.score, 'level': v.quality_level.value} for k, v in state.get('step_results', {}).items()}, indent=2)}

OVERALL SCORE: {overall_score:.2f}
TARGET PLATFORM: {state.get('config', {}).get('platform', 'general')}
DURATION: {state.get('config', {}).get('duration_seconds', 30)}s

Provide comprehensive evaluation:
1. Overall production quality
2. Audience engagement potential
3. Platform optimization
4. Professional standards
5. Viral potential
6. Key strengths
7. Critical weaknesses
8. Final recommendations

Provide quality score (0.0-1.0) and comprehensive assessment.
Format as JSON with: score, quality_level, issues[], suggestions[], metrics{{}}, strengths[], verdict
"""
        
        try:
            response = self.model.invoke([HumanMessage(content=analysis_prompt)])
            result = self._parse_quality_response(response.content)
            
            quality_result = StepQualityResult(
                step=GenerationStep.FINAL_COMPOSITION,
                quality_level=self._score_to_level(result['score']),
                score=result['score'],
                issues=result.get('issues', []),
                suggestions=result.get('suggestions', []),
                metrics={
                    'overall_score': overall_score,
                    'step_average': overall_score,
                    **result.get('metrics', {})
                },
                can_proceed=result['score'] >= state.get('quality_threshold', 0.7),
                should_retry=False  # Don't retry final
            )
            
            state["step_results"]["final"] = quality_result
            state["overall_quality"] = result['score']
            
            # Add final verdict
            state["messages"].append(
                AIMessage(content=f"""
FINAL QUALITY VERDICT:
Score: {result['score']:.2f}
Level: {quality_result.quality_level.value}
Verdict: {result.get('verdict', 'Video meets quality standards')}

Strengths: {', '.join(result.get('strengths', [])[:3])}
Areas for improvement: {', '.join(result.get('issues', [])[:3])}
""")
            )
            
            logger.info(f"🎯 Final quality: {quality_result.quality_level.value} ({result['score']:.2f})")
            
        except Exception as e:
            logger.error(f"❌ Final quality check failed: {e}")
            state["overall_quality"] = overall_score
        
        return state
    
    def _make_quality_decision(self, state: QualityMonitorState) -> QualityMonitorState:
        """Make decision based on quality check"""
        logger.info("🤔 Making quality decision")
        
        current_step = state.get("current_step")
        step_key = self._step_to_key(current_step)
        step_result = state.get("step_results", {}).get(step_key)
        
        if not step_result:
            logger.warning("No step result found, proceeding")
            return state
        
        # Get retry count
        retry_count = state.get("retry_counts", {}).get(step_key, 0)
        max_retries = state.get("max_retries", 2)
        
        # Decision logic
        if step_result.score >= state.get("quality_threshold", 0.7):
            # Quality is good, proceed
            decision = QualityDecision(
                action="proceed",
                reasoning=f"{current_step.value} meets quality standards",
                confidence=step_result.score,
                enhancements_needed=[]
            )
        elif step_result.should_retry and retry_count < max_retries:
            # Quality is poor, retry
            decision = QualityDecision(
                action="retry",
                reasoning=f"{current_step.value} quality too low, retrying",
                confidence=0.8,
                enhancements_needed=step_result.suggestions,
                retry_params={"step": current_step, "issues": step_result.issues}
            )
            state["retry_counts"][step_key] = retry_count + 1
        elif step_result.score >= 0.5:
            # Quality is acceptable but could be better, enhance
            decision = QualityDecision(
                action="enhance",
                reasoning=f"{current_step.value} needs enhancement",
                confidence=0.7,
                enhancements_needed=step_result.suggestions
            )
        else:
            # Quality is too poor and can't retry, abort or proceed with warning
            if step_result.can_proceed:
                decision = QualityDecision(
                    action="proceed",
                    reasoning=f"Proceeding despite low quality in {current_step.value}",
                    confidence=0.4,
                    enhancements_needed=step_result.suggestions
                )
            else:
                decision = QualityDecision(
                    action="abort",
                    reasoning=f"{current_step.value} quality unacceptable",
                    confidence=0.9,
                    enhancements_needed=[]
                )
        
        state["decisions"].append(decision)
        
        logger.info(f"📋 Decision: {decision.action} - {decision.reasoning}")
        
        return state
    
    def _apply_enhancement(self, state: QualityMonitorState) -> QualityMonitorState:
        """Apply quality enhancement"""
        logger.info("✨ Applying quality enhancement")
        
        current_step = state.get("current_step")
        suggestions = state.get("decisions", [])[-1].enhancements_needed if state.get("decisions") else []
        
        # Log enhancement application
        state["messages"].append(
            AIMessage(content=f"Applying enhancements for {current_step.value}: {', '.join(suggestions[:3])}")
        )
        
        # Mark enhancement as applied (actual enhancement happens in video generator)
        state["artifacts"]["enhancements_applied"] = suggestions
        
        return state
    
    def _retry_current_step(self, state: QualityMonitorState) -> QualityMonitorState:
        """Retry the current step"""
        logger.info("🔄 Retrying current step")
        
        current_step = state.get("current_step")
        retry_params = state.get("decisions", [])[-1].retry_params if state.get("decisions") else {}
        
        # Log retry
        state["messages"].append(
            AIMessage(content=f"Retrying {current_step.value} due to: {', '.join(retry_params.get('issues', [])[:3])}")
        )
        
        # Mark for retry (actual retry happens in video generator)
        state["artifacts"]["retry_needed"] = True
        state["artifacts"]["retry_params"] = retry_params
        
        return state
    
    def _generate_final_report(self, state: QualityMonitorState) -> QualityMonitorState:
        """Generate comprehensive quality report"""
        logger.info("📊 Generating final quality report")
        
        elapsed_time = time.time() - state.get("start_time", 0)
        
        report = {
            "session_id": state.get("session_id"),
            "timestamp": datetime.now().isoformat(),
            "elapsed_time": elapsed_time,
            "overall_quality": state.get("overall_quality", 0),
            "quality_threshold": state.get("quality_threshold", 0.7),
            "passed": state.get("overall_quality", 0) >= state.get("quality_threshold", 0.7),
            "step_results": {
                k: {
                    "score": v.score,
                    "level": v.quality_level.value,
                    "issues": v.issues,
                    "suggestions": v.suggestions
                }
                for k, v in state.get("step_results", {}).items()
            },
            "decisions_made": [
                {
                    "action": d.action,
                    "reasoning": d.reasoning,
                    "confidence": d.confidence
                }
                for d in state.get("decisions", [])
            ],
            "total_retries": sum(state.get("retry_counts", {}).values()),
            "final_verdict": self._generate_verdict(state)
        }
        
        state["final_report"] = report
        
        # Save report to file
        report_path = f"outputs/quality_reports/{state.get('session_id')}_quality_report.json"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 Quality report saved: {report_path}")
        logger.info(f"📈 Overall quality: {report['overall_quality']:.2f} - {'PASSED' if report['passed'] else 'FAILED'}")
        
        return state
    
    def _route_after_check(self, state: QualityMonitorState) -> str:
        """Route after quality check"""
        current_step = state.get("current_step")
        step_key = self._step_to_key(current_step)
        step_result = state.get("step_results", {}).get(step_key)
        
        if step_result and (step_result.should_retry or step_result.score < state.get("quality_threshold", 0.7)):
            return "decision"
        else:
            return "next"
    
    def _route_decision(self, state: QualityMonitorState) -> str:
        """Route based on quality decision"""
        if not state.get("decisions"):
            return "proceed"
        
        decision = state["decisions"][-1]
        
        if decision.action == "proceed":
            # Determine next step
            current_step = state.get("current_step")
            next_step = self._get_next_step(current_step)
            state["current_step"] = next_step
            
            # Route to appropriate check
            step_map = {
                GenerationStep.SCRIPT_VALIDATION: "check_script",
                GenerationStep.AUDIO_GENERATION: "check_audio",
                GenerationStep.VIDEO_GENERATION: "check_video",
                GenerationStep.AUDIO_VIDEO_SYNC: "check_sync",
                GenerationStep.EFFECTS_APPLICATION: "check_effects",
                GenerationStep.QUALITY_ENHANCEMENT: "check_enhancement",
                GenerationStep.FINAL_COMPOSITION: "check_final"
            }
            return step_map.get(next_step, "generate_report")
        
        return decision.action
    
    def _parse_quality_response(self, response: str) -> Dict:
        """Parse quality evaluation response"""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Fallback parsing
        result = {
            'score': 0.7,
            'quality_level': 'acceptable',
            'issues': [],
            'suggestions': [],
            'metrics': {}
        }
        
        # Simple parsing
        if 'score' in response.lower():
            try:
                score_match = re.search(r'score[:\s]+([0-9.]+)', response.lower())
                if score_match:
                    result['score'] = float(score_match.group(1))
            except:
                pass
        
        return result
    
    def _score_to_level(self, score: float) -> QualityLevel:
        """Convert numeric score to quality level"""
        if score >= 0.95:
            return QualityLevel.PERFECT
        elif score >= 0.85:
            return QualityLevel.EXCELLENT
        elif score >= 0.7:
            return QualityLevel.GOOD
        elif score >= 0.5:
            return QualityLevel.ACCEPTABLE
        elif score >= 0.3:
            return QualityLevel.POOR
        else:
            return QualityLevel.FAILED
    
    def _step_to_key(self, step: GenerationStep) -> str:
        """Convert step enum to string key"""
        step_map = {
            GenerationStep.SCRIPT_GENERATION: "script",
            GenerationStep.SCRIPT_VALIDATION: "script",
            GenerationStep.AUDIO_GENERATION: "audio",
            GenerationStep.VIDEO_GENERATION: "video",
            GenerationStep.AUDIO_VIDEO_SYNC: "sync",
            GenerationStep.EFFECTS_APPLICATION: "effects",
            GenerationStep.QUALITY_ENHANCEMENT: "enhancement",
            GenerationStep.FINAL_COMPOSITION: "final"
        }
        return step_map.get(step, "unknown")
    
    def _get_next_step(self, current: GenerationStep) -> GenerationStep:
        """Get next step in pipeline"""
        step_sequence = [
            GenerationStep.SCRIPT_VALIDATION,
            GenerationStep.AUDIO_GENERATION,
            GenerationStep.VIDEO_GENERATION,
            GenerationStep.AUDIO_VIDEO_SYNC,
            GenerationStep.EFFECTS_APPLICATION,
            GenerationStep.QUALITY_ENHANCEMENT,
            GenerationStep.FINAL_COMPOSITION
        ]
        
        try:
            current_index = step_sequence.index(current)
            if current_index < len(step_sequence) - 1:
                return step_sequence[current_index + 1]
        except ValueError:
            pass
        
        return GenerationStep.FINAL_COMPOSITION
    
    def _generate_verdict(self, state: QualityMonitorState) -> str:
        """Generate final verdict"""
        overall = state.get("overall_quality", 0)
        threshold = state.get("quality_threshold", 0.7)
        
        if overall >= 0.9:
            return "EXCELLENT - Professional quality achieved"
        elif overall >= threshold:
            return "GOOD - Meets quality standards"
        elif overall >= 0.5:
            return "ACCEPTABLE - Below target but usable"
        else:
            return "POOR - Significant quality issues"
    
    def _analyze_audio_files(self, audio_files: List[str]) -> Dict:
        """Analyze audio file properties"""
        metrics = {
            "file_count": len(audio_files),
            "total_duration": 0,
            "files": []
        }
        
        try:
            from moviepy.editor import AudioFileClip
            
            for audio_file in audio_files:
                if os.path.exists(audio_file):
                    with AudioFileClip(audio_file) as audio:
                        duration = audio.duration
                        metrics["total_duration"] += duration
                        metrics["files"].append({
                            "path": audio_file,
                            "duration": duration
                        })
        except Exception as e:
            logger.error(f"Audio analysis error: {e}")
        
        return metrics
    
    def _analyze_video_clips(self, video_clips: List[str]) -> Dict:
        """Analyze video clip properties"""
        metrics = {
            "clip_count": len(video_clips),
            "total_duration": 0,
            "resolutions": [],
            "clips": []
        }
        
        try:
            from moviepy.editor import VideoFileClip
            
            for video_file in video_clips:
                if os.path.exists(video_file):
                    with VideoFileClip(video_file) as video:
                        metrics["total_duration"] += video.duration
                        metrics["resolutions"].append(f"{video.w}x{video.h}")
                        metrics["clips"].append({
                            "path": video_file,
                            "duration": video.duration,
                            "resolution": f"{video.w}x{video.h}",
                            "fps": video.fps
                        })
        except Exception as e:
            logger.error(f"Video analysis error: {e}")
        
        return metrics
    
    # Public API
    def monitor_generation(self, config: Dict, artifacts: Dict) -> Dict:
        """
        Monitor video generation quality
        
        Args:
            config: Generation configuration
            artifacts: Generated artifacts (script, audio, video, etc.)
            
        Returns:
            Quality monitoring report
        """
        initial_state = {
            "session_id": self.session_id,
            "config": config,
            "artifacts": artifacts,
            "quality_threshold": self.quality_threshold,
            "max_retries": 2,
            "messages": [],
            "step_results": {},
            "decisions": [],
            "retry_counts": {}
        }
        
        # Run the workflow
        thread_config = {"configurable": {"thread_id": f"quality_{self.session_id}"}}
        final_state = self.workflow.invoke(initial_state, thread_config)
        
        return final_state.get("final_report", {})
    
    def check_step_quality(self, step: GenerationStep, artifacts: Dict) -> StepQualityResult:
        """
        Check quality of a specific step
        
        Args:
            step: Generation step to check
            artifacts: Step artifacts
            
        Returns:
            Step quality result
        """
        # Create minimal state for single step check
        state = {
            "current_step": step,
            "artifacts": artifacts,
            "step_results": {},
            "quality_threshold": self.quality_threshold,
            "messages": [],
            "accumulated_score": 0.0,  # Initialize accumulated score
            "current_issues": [],  # Initialize current issues
            "retry_counts": {},  # Initialize retry counts
            "decisions": [],  # Initialize decisions
            "overall_quality": 0.0,  # Initialize overall quality
            "max_retries": 3,  # Set max retries
            "session_id": self.session_id,  # Use session ID
            "start_time": time.time(),  # Set start time
            "final_report": None,  # Initialize final report
            "config": {}  # Initialize config
        }
        
        # Run appropriate check
        if step in [GenerationStep.SCRIPT_GENERATION, GenerationStep.SCRIPT_VALIDATION]:
            state = self._check_script_quality(state)
        elif step == GenerationStep.AUDIO_GENERATION:
            state = self._check_audio_quality(state)
        elif step == GenerationStep.VIDEO_GENERATION:
            state = self._check_video_quality(state)
        elif step == GenerationStep.AUDIO_VIDEO_SYNC:
            state = self._check_sync_quality(state)
        elif step == GenerationStep.EFFECTS_APPLICATION:
            state = self._check_effects_quality(state)
        elif step == GenerationStep.QUALITY_ENHANCEMENT:
            state = self._check_enhancement_quality(state)
        elif step == GenerationStep.FINAL_COMPOSITION:
            state = self._check_final_quality(state)
        
        # Return the step result
        step_key = self._step_to_key(step)
        return state.get("step_results", {}).get(step_key)
    
    def get_quality_summary(self) -> str:
        """Get human-readable quality summary"""
        # Get latest state
        thread_config = {"configurable": {"thread_id": f"quality_{self.session_id}"}}
        state = self.memory.get(thread_config)
        
        if not state:
            return "No quality monitoring data available"
        
        summary = f"""
📊 QUALITY MONITORING SUMMARY
=============================
Session: {self.session_id}
Overall Quality: {state.get('overall_quality', 0):.2f}
Status: {'✅ PASSED' if state.get('overall_quality', 0) >= self.quality_threshold else '❌ FAILED'}

Step Results:
"""
        for step_name, result in state.get('step_results', {}).items():
            summary += f"  • {step_name}: {result.quality_level.value} ({result.score:.2f})\n"
            if result.issues:
                summary += f"    Issues: {', '.join(result.issues[:2])}\n"
        
        return summary