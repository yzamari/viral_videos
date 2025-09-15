"""
Mission Planning Agent - Strategic Work Plan Generation
Creates comprehensive work plans for mission-oriented content
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json
import re
import asyncio

from ..utils.logging_config import get_logger
from ..ai.manager import AIServiceManager
from ..ai.interfaces.text_generation import TextGenerationRequest
from ..models.video_models import Platform, VideoCategory
from ..frameworks.content_credibility_system import ContentCredibilitySystem, CredibilityScore
from ..frameworks.audience_intelligence_system import AudienceIntelligenceSystem, AudienceIntelligence
from ..frameworks.ethical_optimization_system import EthicalOptimizationSystem, EthicalOptimization

from ..config.ai_model_config import DEFAULT_AI_MODEL
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
    audience_intelligence: Optional[AudienceIntelligence] = None
    ethical_optimization: Optional[EthicalOptimization] = None


class MissionPlanningAgent:
    """
    AI agent responsible for mission analysis and strategic work plan generation
    
    This agent determines whether content is mission-oriented (strategic) or 
    informational (topic-based) and creates comprehensive work plans for 
    mission accomplishment.
    """
    
    def __init__(self, api_key: str = None, model_name: str = None, ai_manager: AIServiceManager = None):
        """Initialize Mission Planning Agent"""
        if ai_manager:
            self.ai_manager = ai_manager
        else:
            if not api_key or not api_key.strip():
                raise ValueError("Either API key or ai_manager must be provided")
            # Create AI configuration with the provided API key
            from ..ai.config import AIConfiguration, AIProvider
            from ..ai.factory import AIServiceType
            config = AIConfiguration()
            config.api_keys[AIProvider.GEMINI] = api_key
            config.default_providers[AIServiceType.TEXT_GENERATION] = AIProvider.GEMINI
            self.ai_manager = AIServiceManager(config)
        
        self.api_key = api_key or "dummy"
        self.model_name = model_name
        
        # Initialize content credibility system
        self.credibility_system = ContentCredibilitySystem(api_key)
        
        # Initialize audience intelligence system
        self.audience_intelligence = AudienceIntelligenceSystem(api_key)
        
        # Initialize ethical optimization system with timeout
        self.ethical_optimization = EthicalOptimizationSystem(api_key, timeout=30)
        
        # Mission types and their descriptions for AI classification
        self.mission_types_descriptions = {
            MissionType.CONVINCE: "Persuade or convince someone to adopt a viewpoint, belief, or take specific action",
            MissionType.PERSUADE: "Influence someone's opinion or decision through reasoning or emotional appeal",
            MissionType.TEACH: "Educate or instruct someone about concepts, skills, or knowledge",
            MissionType.DEMONSTRATE: "Show or prove something through examples, evidence, or practical display",
            MissionType.EXPLAIN: "Clarify, describe, or make something understandable",
            MissionType.HELP: "Assist, support, or provide aid to solve problems or improve situations",
            MissionType.STOP: "Halt, cease, or prevent something from happening or continuing",
            MissionType.PREVENT: "Stop something bad from happening or occurring",
            MissionType.ENCOURAGE: "Motivate, inspire, or support positive action or behavior",
            MissionType.MOTIVATE: "Inspire enthusiasm, drive, or determination to take action",
            MissionType.CHANGE: "Transform, modify, or alter current state or behavior",
            MissionType.TRANSFORM: "Make fundamental changes or complete transformation",
            MissionType.IMPROVE: "Make something better, enhance, or optimize",
            MissionType.SOLVE: "Find solutions to problems or challenges",
            MissionType.FIX: "Repair, correct, or resolve issues",
            MissionType.ACHIEVE: "Accomplish goals, reach objectives, or attain success",
            MissionType.INFORM: "Share information, facts, or knowledge without specific action intent"
        }
        
        logger.info(f"🎯 Enhanced Mission Planning Agent initialized with {model_name}")
        logger.info(f"🔍 Content credibility system enabled")
        logger.info(f"🧠 Audience intelligence system enabled")
        logger.info(f"🎯 Ethical optimization system enabled")
    
    async def analyze_mission(self, 
                       mission_statement: str,
                       duration: int,
                       platform: Platform,
                       category: VideoCategory,
                       target_audience: str = "general audience",
                       min_clips: int = None) -> MissionPlan:
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
            mission_type, is_strategic = await self._detect_mission_type(mission_statement)
            
            if is_strategic:
                # Create strategic mission plan
                plan = await self._create_strategic_mission_plan(
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
    
    async def _detect_mission_type(self, mission_statement: str) -> tuple[MissionType, bool]:
        """AI-powered mission type detection using AI service manager"""
        try:
            # First try AI-powered detection
            if self.ai_manager:
                ai_mission_type, is_strategic = await self._ai_mission_detection(mission_statement)
                if ai_mission_type:
                    return ai_mission_type, is_strategic
            
            # Fallback to heuristic detection
            return self._heuristic_mission_detection(mission_statement)
            
        except Exception as e:
            logger.warning(f"⚠️ Mission type detection failed: {e}")
            return MissionType.INFORM, False
    
    async def _ai_mission_detection(self, mission_statement: str) -> tuple[Optional[MissionType], bool]:
        """AI-powered mission type detection"""
        try:
            # Create mission types list for prompt
            mission_types_list = []
            for mission_type, description in self.mission_types_descriptions.items():
                mission_types_list.append(f"- {mission_type.value}: {description}")
            
            mission_prompt = f"""
            Analyze this statement and determine its mission type and whether it's strategic:
            
            Statement: "{mission_statement}"
            
            Available mission types:
            {chr(10).join(mission_types_list)}
            
            Classification criteria:
            - Strategic missions: Have clear intent to influence, change, teach, or achieve specific outcomes
            - Informational content: Simply shares information without specific action intent
            
            Consider:
            1. Intent: What is the primary purpose?
            2. Action orientation: Does it seek to change behavior, teach, convince, or help?
            3. Outcome focus: Is there a specific desired result?
            
            Return JSON:
            {{
                "mission_type": "convince|persuade|teach|demonstrate|explain|help|stop|prevent|encourage|motivate|change|transform|improve|solve|fix|achieve|inform",
                "is_strategic_mission": true|false,
                "confidence": 0.0-1.0,
                "reasoning": "Brief explanation of classification decision"
            }}
            """
            
            # Use AI service manager for generation
            text_service = self.ai_manager.get_text_service()
            request = TextGenerationRequest(
                prompt=mission_prompt,
                temperature=0.3,
                max_tokens=500
            )
            response = await text_service.generate(request)
            logger.debug(f"AI response text: {response.text[:500]}...")
            
            # Parse response - handle markdown code blocks
            text = response.text
            # Remove markdown code blocks if present
            text = re.sub(r'```json\s*', '', text)
            text = re.sub(r'```\s*', '', text)
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                try:
                    raw_json = json_match.group()
                    result = json.loads(raw_json)
                except json.JSONDecodeError as json_error:
                    logger.error(f"Mission detection JSON parsing error: {json_error}")
                    logger.error(f"Raw AI response: {response.text[:500]}...")
                    # Try to clean up common JSON issues
                    cleaned_json = raw_json.replace('\n', ' ').replace('\r', ' ')
                    cleaned_json = re.sub(r',\s*}', '}', cleaned_json)
                    cleaned_json = re.sub(r',\s*]', ']', cleaned_json)
                    try:
                        result = json.loads(cleaned_json)
                        logger.info("Successfully parsed mission detection JSON after cleanup")
                    except:
                        raise json_error
                
                mission_type_str = result.get('mission_type', 'inform')
                is_strategic = result.get('is_strategic_mission', False)
                confidence = result.get('confidence', 0.5)
                reasoning = result.get('reasoning', 'AI classification')
                
                # Handle multiple mission types (e.g., "encourage|motivate")
                if '|' in mission_type_str:
                    # Take the first one
                    mission_type_str = mission_type_str.split('|')[0].strip()
                
                # Convert string to MissionType enum
                for mission_type in MissionType:
                    if mission_type.value == mission_type_str:
                        logger.info(f"🎯 AI Mission Detection: {mission_type.value} (strategic: {is_strategic})")
                        logger.info(f"   Confidence: {confidence:.2f}")
                        logger.info(f"   Reasoning: {reasoning}")
                        return mission_type, is_strategic
            else:
                logger.warning("⚠️ No JSON found in AI response")
            
        except Exception as e:
            logger.warning(f"⚠️ AI mission detection failed: {e}")
            logger.debug(f"Full error details: {e}", exc_info=True)
        
        return None, False
    
    def _heuristic_mission_detection(self, mission_statement: str) -> tuple[MissionType, bool]:
        """Fallback heuristic mission detection"""
        statement_lower = mission_statement.lower()
        
        # Action-oriented indicators for strategic missions
        strategic_indicators = {
            'convince': MissionType.CONVINCE,
            'persuade': MissionType.PERSUADE,
            'teach': MissionType.TEACH,
            'show': MissionType.DEMONSTRATE,
            'demonstrate': MissionType.DEMONSTRATE,
            'explain why': MissionType.EXPLAIN,
            'help': MissionType.HELP,
            'stop': MissionType.STOP,
            'prevent': MissionType.PREVENT,
            'encourage': MissionType.ENCOURAGE,
            'motivate': MissionType.MOTIVATE,
            'change': MissionType.CHANGE,
            'transform': MissionType.TRANSFORM,
            'improve': MissionType.IMPROVE,
            'solve': MissionType.SOLVE,
            'fix': MissionType.FIX,
            'achieve': MissionType.ACHIEVE
        }
        
        # Check for strategic indicators
        for indicator, mission_type in strategic_indicators.items():
            if indicator in statement_lower:
                logger.info(f"🎯 Heuristic Mission Detection: {mission_type.value} (strategic: True)")
                return mission_type, True
        
        # Default to informational
        logger.info(f"🎯 Mission Detection: inform (strategic: False)")
        return MissionType.INFORM, False
    
    async def _create_strategic_mission_plan(self,
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
            
            # Use AI service manager for generation
            text_service = self.ai_manager.get_text_service()
            request = TextGenerationRequest(
                prompt=prompt,
                temperature=0.4,
                max_tokens=2000
            )
            response = await text_service.generate(request)
            
            # Parse AI response - handle markdown code blocks
            text = response.text
            # Remove markdown code blocks if present
            text = re.sub(r'```json\s*', '', text)
            text = re.sub(r'```\s*', '', text)
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                try:
                    # Log the raw JSON for debugging
                    raw_json = json_match.group()
                    logger.debug(f"Raw JSON from AI: {raw_json[:500]}...")  # Log first 500 chars
                    ai_plan = json.loads(raw_json)
                except json.JSONDecodeError as json_error:
                    logger.error(f"JSON parsing error: {json_error}")
                    logger.error(f"Raw AI response: {response.text[:1000]}...")  # Log first 1000 chars
                    
                    # Enhanced JSON cleanup
                    cleaned_json = raw_json
                    
                    # Remove markdown code blocks
                    cleaned_json = re.sub(r'```json\s*', '', cleaned_json)
                    cleaned_json = re.sub(r'```\s*$', '', cleaned_json)
                    
                    # Clean whitespace and control characters
                    cleaned_json = cleaned_json.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                    
                    # Remove trailing commas before closing braces/brackets
                    cleaned_json = re.sub(r',\s*}', '}', cleaned_json)
                    cleaned_json = re.sub(r',\s*]', ']', cleaned_json)
                    
                    # Fix incomplete strings (add closing quotes)
                    if cleaned_json.count('"') % 2 == 1:
                        cleaned_json += '"'
                    
                    # Fix incomplete objects (add closing braces)
                    open_braces = cleaned_json.count('{')
                    close_braces = cleaned_json.count('}')
                    if open_braces > close_braces:
                        cleaned_json += '}' * (open_braces - close_braces)
                    
                    # Fix incomplete arrays (add closing brackets)
                    open_brackets = cleaned_json.count('[')
                    close_brackets = cleaned_json.count(']')
                    if open_brackets > close_brackets:
                        cleaned_json += ']' * (open_brackets - close_brackets)
                    
                    try:
                        ai_plan = json.loads(cleaned_json)
                        logger.info("Successfully parsed JSON after enhanced cleanup")
                    except Exception as final_error:
                        logger.error(f"Enhanced cleanup also failed: {final_error}")
                        logger.error(f"Cleaned JSON: {cleaned_json[:500]}...")
                        raise json_error
                
                # Perform credibility analysis
                logger.info("🔍 Performing content credibility analysis...")
                credibility_score = self.credibility_system.evaluate_content_credibility(
                    content=mission_statement,
                    topic=mission_statement,
                    platform=platform.value if platform else "general"
                )
                
                # Perform audience intelligence analysis
                logger.info("🧠 Performing audience intelligence analysis...")
                audience_analysis = self.audience_intelligence.analyze_audience(
                    topic=mission_statement,
                    platform=platform.value if platform else "general",
                    target_audience=target_audience
                )
                
                # Perform ethical optimization analysis
                logger.info("🎯 Performing ethical optimization analysis...")
                ethical_analysis = self.ethical_optimization.optimize_for_ethics(
                    content=mission_statement,
                    topic=mission_statement,
                    platform=platform.value if platform else "general",
                    mission_type=mission_type.value
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
                    audience_intelligence=audience_analysis,
                    ethical_optimization=ethical_analysis,
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
                logger.info(f"🧠 Audience Intelligence: {audience_analysis.confidence_score:.2f} confidence")
                logger.info(f"   Primary Age Group: {audience_analysis.demographic_profile.primary_age_group.value}")
                logger.info(f"   Engagement Prediction: {audience_analysis.engagement_prediction.get('overall_engagement_score', 'N/A')}")
                logger.info(f"   Optimization Recommendations: {len(audience_analysis.optimization_recommendations)} provided")
                logger.info(f"🎯 Ethical Optimization: {ethical_analysis.overall_ethical_rating} rating")
                logger.info(f"   Compliance Score: {ethical_analysis.ethical_compliance_score}/10")
                logger.info(f"   Transparency: {ethical_analysis.transparency_assessment.transparency_score:.2f}/10")
                logger.info(f"   Educational Value: {ethical_analysis.educational_value_metrics.educational_effectiveness:.2f}/10")
                logger.info(f"   Positive Engagement: {ethical_analysis.positive_engagement_profile.overall_positive_impact:.2f}/10")
                
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
        
        # Perform audience intelligence analysis for informational content too
        try:
            logger.info("🧠 Performing audience intelligence analysis for informational content...")
            audience_analysis = self.audience_intelligence.analyze_audience(
                topic=topic,
                platform=platform.value if platform else "general",
                target_audience=target_audience
            )
            
            # Also perform credibility analysis for informational content
            logger.info("🔍 Performing content credibility analysis for informational content...")
            credibility_score = self.credibility_system.evaluate_content_credibility(
                content=topic,
                topic=topic,
                platform=platform.value if platform else "general"
            )
            
            content_quality_analysis = {
                "credibility_assessment": self.credibility_system.get_credibility_assessment(credibility_score),
                "improvement_recommendations": credibility_score.improvement_suggestions,
                "risk_factors": credibility_score.issues_detected,
                "evidence_requirements": ["Basic fact verification", "Source credibility check"],
                "fact_check_priority": "MEDIUM"
            }
            
            # Also perform ethical optimization for informational content
            logger.info("🎯 Performing ethical optimization analysis for informational content...")
            ethical_analysis = self.ethical_optimization.optimize_for_ethics(
                content=topic,
                topic=topic,
                platform=platform.value if platform else "general",
                mission_type="inform"
            )
            
        except Exception as e:
            logger.warning(f"⚠️ Audience/credibility/ethical analysis failed for informational content: {e}")
            audience_analysis = None
            credibility_score = None
            content_quality_analysis = None
            ethical_analysis = None
        
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
            reasoning="Standard informational content approach",
            credibility_score=credibility_score,
            content_quality_analysis=content_quality_analysis,
            audience_intelligence=audience_analysis,
            ethical_optimization=ethical_analysis
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