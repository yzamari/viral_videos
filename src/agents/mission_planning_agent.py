"""
Mission Planning Agent - Strategic Work Plan Generation
Creates comprehensive work plans for mission-oriented content
"""

import google.generativeai as genai
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json
import re

from ..utils.logging_config import get_logger
from ..models.video_models import Platform, VideoCategory
from ..frameworks.content_credibility_system import ContentCredibilitySystem, CredibilityScore

logger = get_logger(__name__)


class MissionType(Enum):
    """Types of missions for strategic planning"""
    CONVINCE = "convince"
    PERSUADE = "persuade"
    TEACH = "teach"
    DEMONSTRATE = "demonstrate"
    EXPLAIN = "explain"
    HELP = "help"
    STOP = "stop"
    PREVENT = "prevent"
    ENCOURAGE = "encourage"
    MOTIVATE = "motivate"
    CHANGE = "change"
    TRANSFORM = "transform"
    IMPROVE = "improve"
    SOLVE = "solve"
    FIX = "fix"
    ACHIEVE = "achieve"
    INFORM = "inform"  # Non-mission, informational content


@dataclass
class MissionPlan:
    """Strategic mission plan with work breakdown"""
    mission_statement: str
    mission_type: MissionType
    is_strategic_mission: bool
    target_outcome: str
    strategic_approach: str
    success_metrics: List[str]
    content_strategy: Dict[str, Any]
    clip_strategy: Dict[str, Any]
    persuasion_tactics: List[str]
    timing_strategy: Dict[str, Any]
    platform_optimization: Dict[str, Any]
    risk_mitigation: List[str]
    confidence_score: float
    reasoning: str
    credibility_score: Optional[CredibilityScore] = None
    content_quality_analysis: Optional[Dict[str, Any]] = None


class MissionPlanningAgent:
    """
    AI agent responsible for mission analysis and strategic work plan generation
    
    This agent determines whether content is mission-oriented (strategic) or 
    informational (topic-based) and creates comprehensive work plans for 
    mission accomplishment.
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        """Initialize Mission Planning Agent"""
        if not api_key or not api_key.strip():
            raise ValueError("API key cannot be empty")
        
        self.api_key = api_key
        self.model_name = model_name
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        
        # Initialize content credibility system
        self.credibility_system = ContentCredibilitySystem(api_key)
        
        # Mission keywords for detection
        self.mission_keywords = [
            'convince', 'persuade', 'teach', 'show', 'prove', 'demonstrate', 
            'explain why', 'help', 'stop', 'prevent', 'encourage', 'motivate',
            'change', 'transform', 'improve', 'solve', 'fix', 'achieve'
        ]
        
        logger.info(f"🎯 Enhanced Mission Planning Agent initialized with {model_name}")
        logger.info(f"🔍 Content credibility system enabled")
    
    def analyze_mission(self, 
                       mission_statement: str,
                       duration: int,
                       platform: Platform,
                       category: VideoCategory,
                       target_audience: str = "general audience") -> MissionPlan:
        """
        Analyze mission and create strategic work plan
        
        Args:
            mission_statement: The mission/topic to analyze
            duration: Video duration in seconds
            platform: Target platform
            category: Content category
            target_audience: Target audience description
            
        Returns:
            MissionPlan with comprehensive strategy
        """
        try:
            logger.info(f"🎯 Analyzing mission: {mission_statement[:50]}...")
            
            # Detect mission type
            mission_type, is_strategic = self._detect_mission_type(mission_statement)
            
            if is_strategic:
                # Create strategic mission plan
                plan = self._create_strategic_mission_plan(
                    mission_statement, mission_type, duration, platform, category, target_audience
                )
                logger.info(f"✅ Strategic mission plan created: {mission_type.value}")
            else:
                # Create informational content plan
                plan = self._create_informational_content_plan(
                    mission_statement, duration, platform, category, target_audience
                )
                logger.info(f"📝 Informational content plan created")
            
            return plan
            
        except Exception as e:
            logger.error(f"❌ Mission analysis failed: {e}")
            # Return fallback plan
            return self._create_fallback_plan(mission_statement, duration, platform, category)
    
    def _detect_mission_type(self, mission_statement: str) -> tuple[MissionType, bool]:
        """Detect if statement is strategic mission or informational topic"""
        statement_lower = mission_statement.lower()
        
        # Check for mission keywords
        for keyword in self.mission_keywords:
            if keyword in statement_lower:
                # Map keyword to mission type
                if keyword in ['convince', 'persuade']:
                    return MissionType.CONVINCE, True
                elif keyword in ['teach', 'show', 'demonstrate']:
                    return MissionType.TEACH, True
                elif keyword in ['prove', 'explain why']:
                    return MissionType.EXPLAIN, True
                elif keyword in ['help', 'improve', 'solve', 'fix']:
                    return MissionType.HELP, True
                elif keyword in ['stop', 'prevent']:
                    return MissionType.PREVENT, True
                elif keyword in ['encourage', 'motivate']:
                    return MissionType.MOTIVATE, True
                elif keyword in ['change', 'transform']:
                    return MissionType.CHANGE, True
                elif keyword in ['achieve']:
                    return MissionType.ACHIEVE, True
        
        # Default to informational
        return MissionType.INFORM, False
    
    def _create_strategic_mission_plan(self,
                                     mission_statement: str,
                                     mission_type: MissionType,
                                     duration: int,
                                     platform: Platform,
                                     category: VideoCategory,
                                     target_audience: str) -> MissionPlan:
        """Create comprehensive strategic mission plan"""
        try:
            # AI-powered mission planning
            prompt = f"""
You are an expert mission strategist and content optimizer. Your task is to create a comprehensive strategic work plan for accomplishing this mission:

MISSION: "{mission_statement}"
MISSION TYPE: {mission_type.value}
DURATION: {duration} seconds
PLATFORM: {platform.value}
CATEGORY: {category.value}
TARGET AUDIENCE: {target_audience}

Your goal is to create a strategic work plan that maximizes the probability of mission success within the given constraints.

STRATEGIC ANALYSIS REQUIREMENTS:
1. Define the specific target outcome (what success looks like)
2. Identify the optimal strategic approach for this mission type
3. Plan clip structure that serves the mission (not just duration)
4. Select persuasion tactics appropriate for the audience and platform
5. Optimize timing for maximum impact
6. Consider platform-specific optimization strategies
7. Identify potential risks and mitigation strategies

CLIP STRATEGY FOCUS:
- Don't just divide duration by arbitrary numbers
- Consider mission complexity and persuasion requirements
- Balance cost efficiency with mission effectiveness
- Recommend optimal number of clips based on strategic needs
- Consider: Does this mission need multiple proof points? Scene changes? Emotional progression?

Provide your strategic analysis in this exact JSON format:
{{
    "target_outcome": "Specific measurable outcome for mission success",
    "strategic_approach": "Overall strategy for accomplishing the mission",
    "success_metrics": ["metric1", "metric2", "metric3"],
    "content_strategy": {{
        "main_argument": "Central argument/message",
        "supporting_points": ["point1", "point2", "point3"],
        "emotional_appeal": "Primary emotional strategy",
        "logical_structure": "Logical flow of arguments"
    }},
    "clip_strategy": {{
        "recommended_clips": 2,
        "strategic_reasoning": "Why this clip count serves the mission best",
        "clip_purposes": ["purpose1", "purpose2"],
        "optimal_durations": [7.5, 7.5],
        "cost_benefit_analysis": "Analysis of clips vs cost vs mission effectiveness"
    }},
    "persuasion_tactics": ["tactic1", "tactic2", "tactic3"],
    "timing_strategy": {{
        "opening_seconds": "Strategy for first 3 seconds",
        "middle_development": "Strategy for middle section",
        "closing_impact": "Strategy for final seconds"
    }},
    "platform_optimization": {{
        "platform_specific_tactics": ["tactic1", "tactic2"],
        "audience_behavior": "How audience behaves on this platform",
        "optimization_techniques": ["technique1", "technique2"]
    }},
    "risk_mitigation": ["risk1_solution", "risk2_solution"],
    "confidence_score": 0.95,
    "reasoning": "Detailed explanation of strategic decisions"
}}

Focus on creating a plan that actually accomplishes the mission, not just creates content about the topic.
"""
            
            response = self.model.generate_content(prompt)
            
            # Parse AI response
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                ai_plan = json.loads(json_match.group())
                
                # Perform credibility analysis
                logger.info("🔍 Performing content credibility analysis...")
                credibility_score = self.credibility_system.evaluate_content_credibility(
                    content=mission_statement,
                    topic=mission_statement,
                    platform=platform.value if platform else "general"
                )
                
                # Create content quality analysis
                content_quality_analysis = {
                    "credibility_assessment": self.credibility_system.get_credibility_assessment(credibility_score),
                    "improvement_recommendations": credibility_score.improvement_suggestions,
                    "risk_factors": credibility_score.issues_detected,
                    "evidence_requirements": self._generate_evidence_requirements(mission_statement, mission_type),
                    "fact_check_priority": "HIGH" if credibility_score.overall_score < 7.0 else "MEDIUM"
                }
                
                # Create mission plan
                plan = MissionPlan(
                    mission_statement=mission_statement,
                    mission_type=mission_type,
                    is_strategic_mission=True,
                    target_outcome=ai_plan.get('target_outcome', 'Mission completion'),
                    strategic_approach=ai_plan.get('strategic_approach', 'Direct approach'),
                    success_metrics=ai_plan.get('success_metrics', []),
                    content_strategy=ai_plan.get('content_strategy', {}),
                    clip_strategy=ai_plan.get('clip_strategy', {}),
                    credibility_score=credibility_score,
                    content_quality_analysis=content_quality_analysis,
                    persuasion_tactics=ai_plan.get('persuasion_tactics', []),
                    timing_strategy=ai_plan.get('timing_strategy', {}),
                    platform_optimization=ai_plan.get('platform_optimization', {}),
                    risk_mitigation=ai_plan.get('risk_mitigation', []),
                    confidence_score=ai_plan.get('confidence_score', 0.8),
                    reasoning=ai_plan.get('reasoning', 'AI-generated strategic plan')
                )
                
                logger.info(f"🎯 Strategic Mission Plan:")
                logger.info(f"   Target Outcome: {plan.target_outcome}")
                logger.info(f"   Strategic Approach: {plan.strategic_approach}")
                logger.info(f"   Recommended Clips: {plan.clip_strategy.get('recommended_clips', 'Not specified')}")
                logger.info(f"   Confidence Score: {plan.confidence_score:.2f}")
                logger.info(f"🔍 Content Credibility: {credibility_score.overall_score}/10 ({content_quality_analysis['credibility_assessment']})")
                
                return plan
                
        except Exception as e:
            logger.warning(f"⚠️ AI strategic planning failed: {e}")
        
        # Fallback to heuristic planning
        return self._create_heuristic_mission_plan(mission_statement, mission_type, duration, platform, category)
    
    def _create_informational_content_plan(self,
                                         topic: str,
                                         duration: int,
                                         platform: Platform,
                                         category: VideoCategory,
                                         target_audience: str) -> MissionPlan:
        """Create plan for informational (non-mission) content"""
        
        # Simple structure for informational content
        plan = MissionPlan(
            mission_statement=topic,
            mission_type=MissionType.INFORM,
            is_strategic_mission=False,
            target_outcome=f"Educate audience about {topic}",
            strategic_approach="Informational presentation",
            success_metrics=["Engagement", "Understanding", "Retention"],
            content_strategy={
                "main_argument": f"Provide comprehensive information about {topic}",
                "supporting_points": ["Key facts", "Important details", "Practical examples"],
                "emotional_appeal": "Curiosity and learning",
                "logical_structure": "Introduction → Details → Conclusion"
            },
            clip_strategy={
                "recommended_clips": max(2, duration // 5),
                "strategic_reasoning": "Standard informational pacing",
                "clip_purposes": ["Introduction", "Main content", "Conclusion"],
                "optimal_durations": [duration / max(2, duration // 5)] * max(2, duration // 5),
                "cost_benefit_analysis": "Balanced approach for informational content"
            },
            persuasion_tactics=["Clear explanation", "Engaging examples", "Logical flow"],
            timing_strategy={
                "opening_seconds": "Hook with interesting fact or question",
                "middle_development": "Systematic information delivery",
                "closing_impact": "Summary and key takeaways"
            },
            platform_optimization={
                "platform_specific_tactics": [f"Optimize for {platform.value} audience"],
                "audience_behavior": "Information-seeking behavior",
                "optimization_techniques": ["Clear structure", "Engaging visuals"]
            },
            risk_mitigation=["Ensure accuracy", "Avoid information overload"],
            confidence_score=0.7,
            reasoning="Standard informational content approach"
        )
        
        logger.info(f"📝 Informational Content Plan: {topic[:50]}...")
        return plan
    
    def _create_heuristic_mission_plan(self,
                                     mission_statement: str,
                                     mission_type: MissionType,
                                     duration: int,
                                     platform: Platform,
                                     category: VideoCategory) -> MissionPlan:
        """Create mission plan using heuristic rules"""
        
        # Heuristic clip strategy based on mission type and duration
        if mission_type in [MissionType.CONVINCE, MissionType.PERSUADE]:
            # Persuasion missions need fewer, longer clips for coherent arguments
            recommended_clips = 2 if duration <= 20 else 3
        elif mission_type in [MissionType.TEACH, MissionType.DEMONSTRATE]:
            # Teaching missions benefit from more clips for step-by-step progression
            recommended_clips = max(2, min(4, duration // 7))
        elif mission_type in [MissionType.PREVENT, MissionType.STOP]:
            # Warning missions need strong impact with fewer clips
            recommended_clips = 2
        else:
            # Default mission approach
            recommended_clips = max(2, duration // 8)
        
        plan = MissionPlan(
            mission_statement=mission_statement,
            mission_type=mission_type,
            is_strategic_mission=True,
            target_outcome=f"Successfully accomplish: {mission_statement}",
            strategic_approach=f"Heuristic approach for {mission_type.value} mission",
            success_metrics=["Mission completion", "Audience action", "Message clarity"],
            content_strategy={
                "main_argument": f"Execute {mission_type.value} strategy",
                "supporting_points": ["Evidence", "Logic", "Emotional appeal"],
                "emotional_appeal": "Mission-appropriate emotional strategy",
                "logical_structure": "Strategic progression toward mission goal"
            },
            clip_strategy={
                "recommended_clips": recommended_clips,
                "strategic_reasoning": f"Optimal for {mission_type.value} missions of {duration}s",
                "clip_purposes": [f"Clip {i+1}" for i in range(recommended_clips)],
                "optimal_durations": [duration / recommended_clips] * recommended_clips,
                "cost_benefit_analysis": "Heuristic-based optimization"
            },
            persuasion_tactics=[f"{mission_type.value} tactics", "Evidence-based arguments", "Emotional connection"],
            timing_strategy={
                "opening_seconds": "Strong mission-focused opening",
                "middle_development": "Mission execution and evidence",
                "closing_impact": "Mission completion and call to action"
            },
            platform_optimization={
                "platform_specific_tactics": [f"{platform.value} optimization"],
                "audience_behavior": f"Platform-specific behavior on {platform.value}",
                "optimization_techniques": ["Platform best practices"]
            },
            risk_mitigation=["Clear messaging", "Appropriate tone", "Audience alignment"],
            confidence_score=0.6,
            reasoning="Heuristic-based mission planning"
        )
        
        logger.info(f"🧠 Heuristic Mission Plan: {mission_type.value} → {recommended_clips} clips")
        return plan
    
    def _create_fallback_plan(self,
                            mission_statement: str,
                            duration: int,
                            platform: Platform,
                            category: VideoCategory) -> MissionPlan:
        """Create minimal fallback plan"""
        
        return MissionPlan(
            mission_statement=mission_statement,
            mission_type=MissionType.INFORM,
            is_strategic_mission=False,
            target_outcome="Create engaging content",
            strategic_approach="Fallback approach",
            success_metrics=["Engagement"],
            content_strategy={},
            clip_strategy={
                "recommended_clips": max(2, duration // 5),
                "strategic_reasoning": "Fallback clip strategy",
                "clip_purposes": ["Content"],
                "optimal_durations": [duration / max(2, duration // 5)] * max(2, duration // 5),
                "cost_benefit_analysis": "Default approach"
            },
            persuasion_tactics=["Engaging content"],
            timing_strategy={},
            platform_optimization={},
            risk_mitigation=[],
            confidence_score=0.3,
            reasoning="Fallback plan due to processing error"
        )
    
    def get_clip_recommendation(self, mission_plan: MissionPlan) -> Dict[str, Any]:
        """Extract clip recommendations from mission plan"""
        clip_strategy = mission_plan.clip_strategy
        
        return {
            'num_clips': clip_strategy.get('recommended_clips', 2),
            'clip_durations': clip_strategy.get('optimal_durations', [5.0, 5.0]),
            'reasoning': clip_strategy.get('strategic_reasoning', 'Mission-based clip strategy'),
            'cost_efficiency_score': 0.8 if mission_plan.is_strategic_mission else 0.6,
            'content_quality_score': mission_plan.confidence_score,
            'optimal_balance_score': (0.8 + mission_plan.confidence_score) / 2,
            'strategic_purposes': clip_strategy.get('clip_purposes', []),
            'cost_benefit_analysis': clip_strategy.get('cost_benefit_analysis', 'Strategic optimization')
        }
    
    def _generate_evidence_requirements(self, mission_statement: str, mission_type: MissionType) -> List[str]:
        """Generate evidence requirements based on mission type and content"""
        requirements = []
        
        # Base requirements for all missions
        if mission_type in [MissionType.CONVINCE, MissionType.PERSUADE]:
            requirements.extend([
                "Statistical data to support claims",
                "Expert opinions or testimonials", 
                "Peer-reviewed research citations",
                "Real-world examples or case studies"
            ])
        elif mission_type in [MissionType.TEACH, MissionType.EXPLAIN]:
            requirements.extend([
                "Authoritative sources for educational content",
                "Step-by-step verification of processes",
                "Multiple perspective validation",
                "Accuracy check with subject matter experts"
            ])
        elif mission_type in [MissionType.DEMONSTRATE, MissionType.HELP]:
            requirements.extend([
                "Verified methodology or best practices",
                "Safety considerations documentation",
                "Success rate or effectiveness data",
                "Alternative approaches comparison"
            ])
        else:
            requirements.extend([
                "Basic fact verification",
                "Source credibility check",
                "Content accuracy validation"
            ])
        
        # Content-specific requirements
        mission_lower = mission_statement.lower()
        if any(word in mission_lower for word in ['health', 'medical', 'safety', 'nutrition']):
            requirements.append("Medical or health authority validation required")
        
        if any(word in mission_lower for word in ['financial', 'investment', 'money', 'economic']):
            requirements.append("Financial expert review and disclaimer required")
        
        if any(word in mission_lower for word in ['legal', 'law', 'rights', 'regulation']):
            requirements.append("Legal expert consultation recommended")
        
        return requirements