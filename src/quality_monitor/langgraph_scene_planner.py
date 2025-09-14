"""
LangGraph Scene Planner - Intelligent scene planning and decision system
Decides on scene composition, transitions, and news-specific requirements
"""

import os
import json
import operator
from typing import Dict, List, Optional, Any, TypedDict, Annotated, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import re

try:
    from langgraph.graph import StateGraph, END
    from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
    from langchain_google_genai import ChatGoogleGenerativeAI
    import google.generativeai as genai
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    raise ImportError("LangGraph required. Install with: pip install langgraph langchain-google-genai")

from ..utils.logging_config import get_logger

logger = get_logger(__name__)


# Scene Types and Structures
class SceneType(Enum):
    """Types of scenes for video generation"""
    INTRO = "intro"
    HOOK = "hook"
    MAIN_CONTENT = "main_content"
    BREAKING_NEWS = "breaking_news"
    ANALYSIS = "analysis"
    INTERVIEW = "interview"
    B_ROLL = "b_roll"
    TRANSITION = "transition"
    DATA_VISUALIZATION = "data_visualization"
    CALL_TO_ACTION = "call_to_action"
    OUTRO = "outro"
    LOWER_THIRD = "lower_third"  # News-style name/title overlay
    TICKER = "ticker"  # News ticker at bottom


class VisualStyle(Enum):
    """Visual styles for scenes"""
    CINEMATIC = "cinematic"
    DOCUMENTARY = "documentary"
    NEWS_BROADCAST = "news_broadcast"
    SOCIAL_MEDIA = "social_media"
    ANIMATED = "animated"
    MINIMAL = "minimal"
    DRAMATIC = "dramatic"
    UPBEAT = "upbeat"
    SERIOUS = "serious"
    TECH = "tech"


@dataclass
class SceneDefinition:
    """Definition of a single scene"""
    scene_id: str
    scene_type: SceneType
    duration: float  # seconds
    content: str  # Script content for this scene
    visual_style: VisualStyle
    visual_prompts: List[str]  # Prompts for video generation
    camera_movement: str  # static, pan, zoom, tracking
    transition_in: str  # cut, fade, dissolve, wipe
    transition_out: str
    overlays: List[Dict[str, Any]]  # Text overlays, graphics, etc.
    audio_cues: List[str]  # Music, sound effects
    importance: float  # 0-1, for prioritization
    can_skip: bool  # If time constrained
    news_elements: Optional[Dict] = None  # News-specific elements
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary"""
        return {
            "scene_id": self.scene_id,
            "scene_type": self.scene_type.value,
            "duration": self.duration,
            "content": self.content,
            "visual_style": self.visual_style.value,
            "visual_prompts": self.visual_prompts,
            "camera_movement": self.camera_movement,
            "transition_in": self.transition_in,
            "transition_out": self.transition_out,
            "overlays": self.overlays,
            "audio_cues": self.audio_cues,
            "importance": self.importance,
            "can_skip": self.can_skip,
            "news_elements": self.news_elements
        }


@dataclass
class ScenePlan:
    """Complete scene plan for video"""
    total_scenes: int
    scenes: List[SceneDefinition]
    total_duration: float
    scene_flow: List[str]  # Order of scene IDs
    style_consistency: Dict[str, Any]
    news_mode: bool
    breaking_news: bool
    multi_segment: bool
    pacing: str  # slow, medium, fast, dynamic
    use_multiple_scenes: bool = False  # Add this property if missing
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary"""
        return {
            "total_scenes": self.total_scenes,
            "scenes": [scene.to_dict() for scene in self.scenes],
            "total_duration": self.total_duration,
            "scene_flow": self.scene_flow,
            "style_consistency": self.style_consistency,
            "news_mode": self.news_mode,
            "breaking_news": self.breaking_news,
            "multi_segment": self.multi_segment,
            "pacing": self.pacing,
            "use_multiple_scenes": getattr(self, 'use_multiple_scenes', self.multi_segment)
        }


# LangGraph State for Scene Planning
class ScenePlannerState(TypedDict):
    """State for scene planning workflow"""
    script: str
    config: Dict[str, Any]
    content_type: str  # news, entertainment, educational, etc.
    duration_target: float
    platform: str
    scene_analysis: Dict[str, Any]
    proposed_scenes: List[SceneDefinition]
    scene_plan: Optional[ScenePlan]
    quality_scores: Dict[str, float]
    decisions: List[str]
    messages: Annotated[List[BaseMessage], operator.add]


class LangGraphScenePlanner:
    """
    Intelligent scene planning using LangGraph
    Decides on scene composition based on content analysis
    """
    
    def __init__(self, api_key: str):
        """Initialize scene planner"""
        self.api_key = api_key
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.7,  # More creative for scene planning
            convert_system_message_to_human=True
        )
        
        # Build workflow
        self.workflow = self._build_workflow()
        
        logger.info("✅ LangGraph Scene Planner initialized")
    
    def _build_workflow(self) -> StateGraph:
        """Build scene planning workflow"""
        
        workflow = StateGraph(ScenePlannerState)
        
        # Add nodes
        workflow.add_node("analyze_content", self._analyze_content)
        workflow.add_node("identify_scenes", self._identify_scene_breaks)
        workflow.add_node("plan_news_scenes", self._plan_news_scenes)
        workflow.add_node("plan_standard_scenes", self._plan_standard_scenes)
        workflow.add_node("optimize_scenes", self._optimize_scene_timing)
        workflow.add_node("add_visual_details", self._add_visual_details)
        workflow.add_node("finalize_plan", self._finalize_scene_plan)
        
        # Define flow
        workflow.set_entry_point("analyze_content")
        workflow.add_edge("analyze_content", "identify_scenes")
        
        # Conditional routing based on content type
        workflow.add_conditional_edges(
            "identify_scenes",
            self._route_by_content_type,
            {
                "news": "plan_news_scenes",
                "standard": "plan_standard_scenes"
            }
        )
        
        workflow.add_edge("plan_news_scenes", "optimize_scenes")
        workflow.add_edge("plan_standard_scenes", "optimize_scenes")
        workflow.add_edge("optimize_scenes", "add_visual_details")
        workflow.add_edge("add_visual_details", "finalize_plan")
        workflow.add_edge("finalize_plan", END)
        
        return workflow.compile()
    
    def _analyze_content(self, state: ScenePlannerState) -> ScenePlannerState:
        """Analyze content to understand structure and requirements"""
        logger.info("📝 Analyzing content for scene planning")
        
        script = state.get("script", "")
        config = state.get("config", {})
        
        analysis_prompt = f"""
Analyze this script for video scene planning:

SCRIPT:
{script}

CONFIG:
Platform: {config.get('platform', 'general')}
Duration: {config.get('duration_seconds', 30)}s
Style: {config.get('style', 'dynamic')}
Category: {config.get('category', 'general')}

Analyze and identify:
1. Content type (news, entertainment, educational, commercial, etc.)
2. Key narrative beats and natural scene breaks
3. Emotional arc and pacing requirements
4. Whether this needs multiple scenes or single scene
5. News elements if applicable (breaking news, interviews, data)
6. Required visual variety for engagement
7. Critical moments that need emphasis

Format response as JSON with:
- content_type: string
- narrative_beats: []
- scene_count_recommendation: number
- is_news: boolean
- is_breaking: boolean
- needs_multiple_scenes: boolean
- pacing: string (slow/medium/fast/dynamic)
- key_moments: []
- visual_requirements: []
"""
        
        try:
            response = self.model.invoke([HumanMessage(content=analysis_prompt)])
            analysis = self._parse_json_response(response.content)
            
            state["scene_analysis"] = analysis
            state["content_type"] = analysis.get("content_type", "general")
            
            # Add analysis message
            state["messages"] = [
                SystemMessage(content="Scene planning analysis complete"),
                AIMessage(content=f"Content type: {analysis.get('content_type')}, Needs {analysis.get('scene_count_recommendation', 1)} scenes")
            ]
            
            logger.info(f"✅ Content analyzed: {analysis.get('content_type')}, {analysis.get('scene_count_recommendation')} scenes recommended")
            
        except Exception as e:
            logger.error(f"❌ Content analysis failed: {e}")
            state["scene_analysis"] = {
                "content_type": "general",
                "scene_count_recommendation": 3,
                "needs_multiple_scenes": True
            }
        
        return state
    
    def _identify_scene_breaks(self, state: ScenePlannerState) -> ScenePlannerState:
        """Identify natural scene break points"""
        logger.info("🎬 Identifying scene breaks")
        
        script = state.get("script", "")
        analysis = state.get("scene_analysis", {})
        duration = state.get("duration_target", 30)
        
        identification_prompt = f"""
Identify optimal scene breaks in this script:

SCRIPT:
{script}

ANALYSIS:
{json.dumps(analysis, indent=2)}

TARGET DURATION: {duration}s

Break the content into distinct scenes. For each scene identify:
1. Scene content (what's being said/shown)
2. Scene purpose (hook, explanation, evidence, CTA, etc.)
3. Suggested duration (in seconds)
4. Emotional tone
5. Visual requirements

Consider:
- Natural narrative breaks
- Attention span (change every 3-5 seconds for social media)
- Platform requirements
- News format if applicable (intro -> story -> analysis -> conclusion)

Format as JSON with:
- scenes: [
    {{
      "content": "text content",
      "purpose": "hook/main/support/cta",
      "duration": seconds,
      "tone": "emotional tone",
      "visual_needs": []
    }}
  ]
- total_scenes: number
- requires_breaking_news_treatment: boolean
"""
        
        try:
            response = self.model.invoke([HumanMessage(content=identification_prompt)])
            scene_breaks = self._parse_json_response(response.content)
            
            # Store identified scenes
            state["proposed_scenes"] = []
            
            for i, scene_data in enumerate(scene_breaks.get("scenes", [])):
                scene = SceneDefinition(
                    scene_id=f"scene_{i+1}",
                    scene_type=self._purpose_to_scene_type(scene_data.get("purpose", "main")),
                    duration=scene_data.get("duration", 5),
                    content=scene_data.get("content", ""),
                    visual_style=VisualStyle.CINEMATIC,  # Will be refined
                    visual_prompts=[],  # Will be added
                    camera_movement="static",  # Will be refined
                    transition_in="cut",
                    transition_out="cut",
                    overlays=[],
                    audio_cues=[],
                    importance=0.8,
                    can_skip=False
                )
                state["proposed_scenes"].append(scene)
            
            logger.info(f"✅ Identified {len(state['proposed_scenes'])} scenes")
            
        except Exception as e:
            logger.error(f"❌ Scene identification failed: {e}")
            # Create default scenes
            self._create_default_scenes(state)
        
        return state
    
    def _plan_news_scenes(self, state: ScenePlannerState) -> ScenePlannerState:
        """Plan scenes specifically for news content"""
        logger.info("📺 Planning news-specific scenes")
        
        scenes = state.get("proposed_scenes", [])
        analysis = state.get("scene_analysis", {})
        
        news_prompt = f"""
Enhance these scenes for NEWS BROADCAST format:

CURRENT SCENES:
{json.dumps([asdict(s) for s in scenes], indent=2)}

IS BREAKING: {analysis.get('is_breaking', False)}

Transform into professional news format:
1. Add news-specific elements (lower thirds, tickers, breaking news graphics)
2. Include B-roll suggestions
3. Add data visualization scenes if statistics mentioned
4. Include correspondent/anchor shots if appropriate
5. Add news-style transitions
6. Include breaking news treatment if needed

For each scene provide:
- news_elements: {{
    "lower_third": {{"text": "", "title": ""}},
    "ticker": {{"text": ""}},
    "breaking_banner": boolean,
    "graphics": []
  }}
- b_roll_suggestions: []
- camera_style: "news_static/news_pan/news_zoom"

Format as JSON with enhanced_scenes: []
"""
        
        try:
            response = self.model.invoke([HumanMessage(content=news_prompt)])
            news_enhancements = self._parse_json_response(response.content)
            
            # Enhance scenes with news elements
            for i, scene in enumerate(scenes):
                if i < len(news_enhancements.get("enhanced_scenes", [])):
                    enhancement = news_enhancements["enhanced_scenes"][i]
                    
                    # Add news elements
                    scene.news_elements = enhancement.get("news_elements", {})
                    
                    # Add lower third overlay if specified
                    if "lower_third" in enhancement.get("news_elements", {}):
                        scene.overlays.append({
                            "type": "lower_third",
                            "text": enhancement["news_elements"]["lower_third"].get("text", ""),
                            "title": enhancement["news_elements"]["lower_third"].get("title", ""),
                            "position": "bottom",
                            "style": "news"
                        })
                    
                    # Add ticker if specified
                    if "ticker" in enhancement.get("news_elements", {}):
                        scene.overlays.append({
                            "type": "ticker",
                            "text": enhancement["news_elements"]["ticker"].get("text", ""),
                            "position": "bottom",
                            "style": "scrolling"
                        })
                    
                    # Update visual style for news
                    scene.visual_style = VisualStyle.NEWS_BROADCAST
                    scene.camera_movement = enhancement.get("camera_style", "news_static")
            
            state["proposed_scenes"] = scenes
            logger.info(f"✅ Enhanced {len(scenes)} scenes with news elements")
            
        except Exception as e:
            logger.error(f"❌ News scene planning failed: {e}")
        
        return state
    
    def _plan_standard_scenes(self, state: ScenePlannerState) -> ScenePlannerState:
        """Plan scenes for non-news content"""
        logger.info("🎬 Planning standard scenes")
        
        scenes = state.get("proposed_scenes", [])
        config = state.get("config", {})
        platform = config.get("platform", "general")
        
        standard_prompt = f"""
Optimize these scenes for {platform} platform:

SCENES:
{json.dumps([asdict(s) for s in scenes], indent=2)}

Enhance for maximum engagement:
1. Add dynamic visual suggestions
2. Optimize pacing for platform
3. Add engagement elements (text overlays, animations)
4. Suggest camera movements
5. Plan smooth transitions

For each scene provide:
- visual_enhancements: []
- engagement_elements: []
- optimal_camera: string
- transition_style: string

Format as JSON with enhanced_scenes: []
"""
        
        try:
            response = self.model.invoke([HumanMessage(content=standard_prompt)])
            enhancements = self._parse_json_response(response.content)
            
            # Apply enhancements
            for i, scene in enumerate(scenes):
                if i < len(enhancements.get("enhanced_scenes", [])):
                    enhancement = enhancements["enhanced_scenes"][i]
                    
                    scene.camera_movement = enhancement.get("optimal_camera", "pan")
                    scene.transition_in = enhancement.get("transition_style", "fade")
                    
                    # Add engagement overlays
                    for element in enhancement.get("engagement_elements", []):
                        scene.overlays.append({
                            "type": "text",
                            "content": element,
                            "style": "animated"
                        })
            
            state["proposed_scenes"] = scenes
            logger.info(f"✅ Enhanced {len(scenes)} standard scenes")
            
        except Exception as e:
            logger.error(f"❌ Standard scene planning failed: {e}")
        
        return state
    
    def _optimize_scene_timing(self, state: ScenePlannerState) -> ScenePlannerState:
        """Optimize scene timing and pacing"""
        logger.info("⏱️ Optimizing scene timing")
        
        scenes = state.get("proposed_scenes", [])
        target_duration = state.get("duration_target", 30)
        
        # Calculate current total
        current_total = sum(s.duration for s in scenes)
        
        if current_total != target_duration:
            # Adjust proportionally
            scale_factor = target_duration / current_total
            
            for scene in scenes:
                scene.duration = round(scene.duration * scale_factor, 1)
                
                # Ensure minimum scene duration
                if scene.duration < 2.0 and not scene.can_skip:
                    scene.duration = 2.0
        
        # Recalculate total
        new_total = sum(s.duration for s in scenes)
        
        # If still off, adjust the main content scene
        if new_total != target_duration:
            diff = target_duration - new_total
            main_scenes = [s for s in scenes if s.scene_type == SceneType.MAIN_CONTENT]
            if main_scenes:
                main_scenes[0].duration += diff
        
        state["proposed_scenes"] = scenes
        logger.info(f"✅ Optimized timing: {len(scenes)} scenes, {sum(s.duration for s in scenes)}s total")
        
        return state
    
    def _add_visual_details(self, state: ScenePlannerState) -> ScenePlannerState:
        """Add detailed visual prompts for each scene"""
        logger.info("🎨 Adding visual details")
        
        scenes = state.get("proposed_scenes", [])
        config = state.get("config", {})
        
        for scene in scenes:
            # Generate visual prompts based on scene type and content
            if scene.scene_type == SceneType.INTRO:
                scene.visual_prompts = [
                    f"Professional opening shot, {scene.visual_style.value} style",
                    f"Establishing shot with title overlay",
                    f"Smooth {scene.camera_movement} camera movement"
                ]
            elif scene.scene_type == SceneType.BREAKING_NEWS:
                scene.visual_prompts = [
                    "Breaking news broadcast studio",
                    "Red breaking news banner",
                    "Urgent news graphics",
                    "Professional news anchor desk"
                ]
            elif scene.scene_type == SceneType.MAIN_CONTENT:
                # Parse content for visual cues
                visual_elements = self._extract_visual_elements(scene.content)
                scene.visual_prompts = visual_elements
            elif scene.scene_type == SceneType.DATA_VISUALIZATION:
                scene.visual_prompts = [
                    "Modern data visualization",
                    "Animated charts and graphs",
                    "Clean infographic style"
                ]
            else:
                # Generic visual prompts
                scene.visual_prompts = [
                    f"{scene.visual_style.value} visual style",
                    f"Scene showing: {scene.content[:50]}..."
                ]
            
            # Add platform-specific optimizations
            if "tiktok" in config.get("platform", "").lower():
                scene.visual_prompts.append("Vertical format optimized for mobile")
                scene.visual_prompts.append("High energy, fast-paced visuals")
            elif "youtube" in config.get("platform", "").lower():
                scene.visual_prompts.append("High quality cinematic visuals")
                scene.visual_prompts.append("Professional production value")
        
        state["proposed_scenes"] = scenes
        logger.info(f"✅ Added visual details to {len(scenes)} scenes")
        
        return state
    
    def _finalize_scene_plan(self, state: ScenePlannerState) -> ScenePlannerState:
        """Finalize and validate scene plan"""
        logger.info("✅ Finalizing scene plan")
        
        scenes = state.get("proposed_scenes", [])
        analysis = state.get("scene_analysis", {})
        
        # Create scene plan
        scene_plan = ScenePlan(
            total_scenes=len(scenes),
            scenes=scenes,
            total_duration=sum(s.duration for s in scenes),
            scene_flow=[s.scene_id for s in scenes],
            style_consistency={
                "primary_style": scenes[0].visual_style.value if scenes else "cinematic",
                "transitions": list(set(s.transition_in for s in scenes))
            },
            news_mode=analysis.get("is_news", False),
            breaking_news=analysis.get("is_breaking", False),
            multi_segment=len(scenes) > 3,
            pacing=analysis.get("pacing", "medium")
        )
        
        state["scene_plan"] = scene_plan
        
        # Log scene plan summary
        logger.info(f"""
📋 SCENE PLAN SUMMARY:
- Total Scenes: {scene_plan.total_scenes}
- Duration: {scene_plan.total_duration}s
- News Mode: {scene_plan.news_mode}
- Multi-Segment: {scene_plan.multi_segment}
- Pacing: {scene_plan.pacing}
""")
        
        for i, scene in enumerate(scenes):
            logger.info(f"  Scene {i+1}: {scene.scene_type.value} ({scene.duration}s)")
        
        return state
    
    def _route_by_content_type(self, state: ScenePlannerState) -> str:
        """Route based on content type"""
        analysis = state.get("scene_analysis", {})
        
        if analysis.get("is_news") or analysis.get("content_type") == "news":
            return "news"
        else:
            return "standard"
    
    def _purpose_to_scene_type(self, purpose: str) -> SceneType:
        """Convert purpose string to SceneType"""
        purpose_map = {
            "hook": SceneType.HOOK,
            "intro": SceneType.INTRO,
            "main": SceneType.MAIN_CONTENT,
            "support": SceneType.MAIN_CONTENT,
            "evidence": SceneType.ANALYSIS,
            "data": SceneType.DATA_VISUALIZATION,
            "cta": SceneType.CALL_TO_ACTION,
            "outro": SceneType.OUTRO,
            "breaking": SceneType.BREAKING_NEWS
        }
        
        purpose_lower = purpose.lower()
        for key, scene_type in purpose_map.items():
            if key in purpose_lower:
                return scene_type
        
        return SceneType.MAIN_CONTENT
    
    def _create_default_scenes(self, state: ScenePlannerState):
        """Create default scene structure"""
        duration = state.get("duration_target", 30)
        
        # Simple 3-scene structure
        scenes = [
            SceneDefinition(
                scene_id="scene_1",
                scene_type=SceneType.HOOK,
                duration=duration * 0.2,
                content=state.get("script", "")[:100],
                visual_style=VisualStyle.CINEMATIC,
                visual_prompts=["Opening scene"],
                camera_movement="zoom",
                transition_in="fade",
                transition_out="cut",
                overlays=[],
                audio_cues=[],
                importance=1.0,
                can_skip=False
            ),
            SceneDefinition(
                scene_id="scene_2",
                scene_type=SceneType.MAIN_CONTENT,
                duration=duration * 0.6,
                content=state.get("script", "")[100:300],
                visual_style=VisualStyle.CINEMATIC,
                visual_prompts=["Main content"],
                camera_movement="pan",
                transition_in="cut",
                transition_out="cut",
                overlays=[],
                audio_cues=[],
                importance=0.9,
                can_skip=False
            ),
            SceneDefinition(
                scene_id="scene_3",
                scene_type=SceneType.CALL_TO_ACTION,
                duration=duration * 0.2,
                content=state.get("script", "")[300:],
                visual_style=VisualStyle.CINEMATIC,
                visual_prompts=["Call to action"],
                camera_movement="static",
                transition_in="cut",
                transition_out="fade",
                overlays=[],
                audio_cues=[],
                importance=0.8,
                can_skip=False
            )
        ]
        
        state["proposed_scenes"] = scenes
    
    def _extract_visual_elements(self, content: str) -> List[str]:
        """Extract visual elements from content"""
        prompts = []
        
        # Look for visual cues in content
        if "people" in content.lower() or "person" in content.lower():
            prompts.append("People in professional setting")
        if "data" in content.lower() or "number" in content.lower():
            prompts.append("Data visualization and statistics")
        if "city" in content.lower() or "building" in content.lower():
            prompts.append("Urban cityscape")
        if "technology" in content.lower() or "computer" in content.lower():
            prompts.append("Modern technology and devices")
        
        # Default if no specific elements found
        if not prompts:
            prompts.append(f"Visual representation of: {content[:50]}")
        
        return prompts
    
    def _parse_json_response(self, response: str) -> Dict:
        """Parse JSON from model response"""
        try:
            # Try to extract JSON
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Return default
        return {}
    
    # Public API
    def plan_scenes(self, script: str, config: Dict) -> ScenePlan:
        """
        Plan scenes for video generation
        
        Args:
            script: Video script
            config: Generation configuration
            
        Returns:
            Complete scene plan
        """
        initial_state = {
            "script": script,
            "config": config,
            "duration_target": config.get("duration_seconds", 30),
            "platform": config.get("platform", "general"),
            "messages": []
        }
        
        # Run workflow
        final_state = self.workflow.invoke(initial_state)
        
        return final_state.get("scene_plan")
    
    def should_use_multiple_scenes(self, script: str, duration: float) -> bool:
        """
        Quick check if content needs multiple scenes
        
        Args:
            script: Video script
            duration: Target duration
            
        Returns:
            True if multiple scenes recommended
        """
        # Quick heuristics
        word_count = len(script.split())
        
        # Check for scene indicators
        has_multiple_parts = any(
            indicator in script.lower() 
            for indicator in ["first", "second", "next", "then", "finally", "but", "however"]
        )
        
        # Duration check
        needs_multiple = duration > 15  # More than 15 seconds usually needs scenes
        
        # Content complexity
        is_complex = word_count > 100
        
        return has_multiple_parts or needs_multiple or is_complex
    
    def get_scene_summary(self, scene_plan: ScenePlan) -> str:
        """Get human-readable scene summary"""
        if not scene_plan:
            return "No scene plan available"
        
        summary = f"""
🎬 SCENE PLAN
=============
Total Scenes: {scene_plan.total_scenes}
Duration: {scene_plan.total_duration}s
Style: {scene_plan.news_mode and 'News Broadcast' or 'Standard'}
Pacing: {scene_plan.pacing}

Scene Breakdown:
"""
        
        for i, scene in enumerate(scene_plan.scenes):
            summary += f"""
Scene {i+1}: {scene.scene_type.value.upper()}
- Duration: {scene.duration}s
- Style: {scene.visual_style.value}
- Camera: {scene.camera_movement}
- Content: {scene.content[:50]}...
"""
            if scene.news_elements:
                summary += f"- News Elements: Lower third, ticker\n"
        
        return summary