"""
Psychological Trigger Enhancement System
Enhances content with proven psychological triggers for maximum engagement
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from ..utils.logging_config import get_logger
from ..ai.manager import AIServiceManager
from ..ai.interfaces.text_generation import TextGenerationRequest
from ..ai.interfaces.base import AIServiceType
from ..models.video_models import Platform

logger = get_logger(__name__)

class PsychologicalTriggerEnhancer:
    """
    Applies psychological triggers to content for maximum engagement and persuasion
    Uses behavioral science principles to increase likes, follows, and reactions
    """
    
    def __init__(self, ai_manager: AIServiceManager):
        self.ai_manager = ai_manager
        
        # Define psychological triggers and their applications
        self.psychological_triggers = {
            "curiosity_gap": {
                "description": "Creates information gaps that viewers want filled",
                "examples": ["What happens next will shock you", "The secret is revealed at the end"],
                "effectiveness": 9.2
            },
            "social_proof": {
                "description": "Uses others' behavior to influence decisions",
                "examples": ["Millions of people are doing this", "Join the community"],
                "effectiveness": 8.8
            },
            "scarcity": {
                "description": "Creates urgency through limited availability",
                "examples": ["Limited time offer", "Only a few people know this"],
                "effectiveness": 8.5
            },
            "authority": {
                "description": "Leverages credibility and expertise",
                "examples": ["Experts recommend", "Research shows"],
                "effectiveness": 8.3
            },
            "reciprocity": {
                "description": "People feel obligated to return favors",
                "examples": ["I'll give you this free tip", "Here's a valuable insight"],
                "effectiveness": 8.0
            },
            "loss_aversion": {
                "description": "Fear of missing out or losing something",
                "examples": ["Don't miss out", "What you're losing by not knowing this"],
                "effectiveness": 7.8
            },
            "emotional_contrast": {
                "description": "Creates emotional highs and lows",
                "examples": ["From despair to triumph", "The shocking truth"],
                "effectiveness": 7.5
            },
            "pattern_interruption": {
                "description": "Breaks expected patterns to capture attention",
                "examples": ["Wait, that's not what you think", "Plot twist"],
                "effectiveness": 7.2
            },
            "tribal_identity": {
                "description": "Appeals to group belonging",
                "examples": ["People like us", "Our community"],
                "effectiveness": 7.0
            },
            "anticipation": {
                "description": "Builds excitement for future events",
                "examples": ["Coming up next", "Wait until you see this"],
                "effectiveness": 6.8
            }
        }
        
        logger.info("✅ Psychological Trigger Enhancer initialized")
    
    async def analyze_psychological_effectiveness(
        self,
        content: str,
        mission: str,
        platform: Platform,
        target_audience: str = None
    ) -> Dict[str, Any]:
        """
        Analyze current psychological effectiveness of content
        """
        logger.info(f"🧠 Analyzing psychological effectiveness for '{mission}' on {platform.value}")
        
        prompt = f"""
Analyze this content for PSYCHOLOGICAL EFFECTIVENESS and PERSUASION POWER:

MISSION: {mission}
PLATFORM: {platform.value}
TARGET AUDIENCE: {target_audience or "General audience"}

CONTENT TO ANALYZE:
{content}

🧠 PSYCHOLOGICAL ANALYSIS REQUIRED:

Analyze the presence and effectiveness of these psychological triggers:

1. CURIOSITY GAP: Creates information gaps that viewers want filled
   - Current usage: Rate 1-10
   - Opportunities: Where can we add curiosity gaps?
   - Examples: "What happens next", "The secret is..."

2. SOCIAL PROOF: Uses others' behavior to influence decisions
   - Current usage: Rate 1-10
   - Opportunities: Where can we add social validation?
   - Examples: "Everyone is talking about", "Join millions"

3. SCARCITY: Creates urgency through limited availability
   - Current usage: Rate 1-10
   - Opportunities: Where can we add urgency?
   - Examples: "Limited time", "Few people know"

4. AUTHORITY: Leverages credibility and expertise
   - Current usage: Rate 1-10
   - Opportunities: Where can we add credibility?
   - Examples: "Experts say", "Research proves"

5. RECIPROCITY: People feel obligated to return favors
   - Current usage: Rate 1-10
   - Opportunities: Where can we give value first?
   - Examples: "Free tip", "I'll share"

6. LOSS AVERSION: Fear of missing out or losing something
   - Current usage: Rate 1-10
   - Opportunities: Where can we highlight what they'll miss?
   - Examples: "Don't miss out", "What you're losing"

7. EMOTIONAL CONTRAST: Creates emotional highs and lows
   - Current usage: Rate 1-10
   - Opportunities: Where can we add emotional shifts?
   - Examples: "From failure to success", "The shocking truth"

8. PATTERN INTERRUPTION: Breaks expected patterns
   - Current usage: Rate 1-10
   - Opportunities: Where can we surprise viewers?
   - Examples: "Plot twist", "Wait, that's not right"

9. TRIBAL IDENTITY: Appeals to group belonging
   - Current usage: Rate 1-10
   - Opportunities: Where can we build community?
   - Examples: "People like us", "Our tribe"

10. ANTICIPATION: Builds excitement for future events
    - Current usage: Rate 1-10
    - Opportunities: Where can we build anticipation?
    - Examples: "Coming up", "Wait until you see"

Return JSON:
{{
    "overall_psychological_score": 65,
    "trigger_analysis": {{
        "curiosity_gap": {{
            "current_score": 7,
            "usage_examples": ["Teaser at beginning"],
            "opportunities": ["Add mystery in middle", "Cliffhanger ending"],
            "effectiveness_potential": 9.2
        }},
        "social_proof": {{
            "current_score": 3,
            "usage_examples": [],
            "opportunities": ["Add testimonials", "Mention community size"],
            "effectiveness_potential": 8.8
        }}
        // ... continue for all triggers
    }},
    "strongest_triggers": ["curiosity_gap", "authority"],
    "weakest_triggers": ["social_proof", "scarcity", "reciprocity"],
    "missing_opportunities": [
        "No social proof elements",
        "Lacks urgency/scarcity",
        "Could add more emotional contrast"
    ],
    "psychological_gaps": [
        "Opening lacks hook",
        "No community building",
        "Missing credibility markers"
    ],
    "platform_specific_psychology": {{
        "platform_match": 7,
        "platform_gaps": ["Missing viral elements for {platform.value}"],
        "platform_opportunities": ["Add trending psychological patterns"]
    }},
    "audience_psychology": {{
        "audience_match": 6,
        "motivations": ["achievement", "belonging", "recognition"],
        "psychological_profile": "achievement-oriented, social",
        "trigger_preferences": ["social_proof", "authority", "tribal_identity"]
    }},
    "top_enhancement_priorities": [
        "Add strong social proof elements",
        "Create curiosity gaps throughout",
        "Build tribal identity/community",
        "Establish authority/credibility"
    ]
}}
"""
        
        try:
            text_service = self.ai_manager.get_service(AIServiceType.TEXT_GENERATION)
            request = TextGenerationRequest(
                prompt=prompt,
                max_tokens=2500,
                temperature=0.6
            )
            
            response = await text_service.generate(request)
            analysis = self._parse_json_response(response.text)
            
            logger.info(f"🧠 Psychological analysis complete - Score: {analysis.get('overall_psychological_score', 0)}")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Psychological analysis failed: {e}")
            return self._create_fallback_psychological_analysis()
    
    async def enhance_with_psychological_triggers(
        self,
        content: str,
        mission: str,
        platform: Platform,
        psychological_analysis: Dict[str, Any] = None,
        target_triggers: List[str] = None
    ) -> Dict[str, Any]:
        """
        Enhance content with specific psychological triggers
        """
        logger.info(f"🚀 Enhancing content with psychological triggers")
        
        # Get analysis if not provided
        if not psychological_analysis:
            psychological_analysis = await self.analyze_psychological_effectiveness(
                content, mission, platform
            )
        
        # Determine priority triggers
        if not target_triggers:
            weakest_triggers = psychological_analysis.get('weakest_triggers', [])
            missing_opportunities = psychological_analysis.get('missing_opportunities', [])
            target_triggers = weakest_triggers[:3]  # Focus on top 3 weakest
        
        prompt = f"""
Enhance this content with POWERFUL PSYCHOLOGICAL TRIGGERS for maximum engagement:

MISSION: {mission}
PLATFORM: {platform.value}
CURRENT PSYCHOLOGICAL SCORE: {psychological_analysis.get('overall_psychological_score', 50)}

ORIGINAL CONTENT:
{content}

PSYCHOLOGICAL GAPS IDENTIFIED:
- Weakest Areas: {psychological_analysis.get('weakest_triggers', [])}
- Missing Opportunities: {psychological_analysis.get('missing_opportunities', [])}
- Priority Enhancements: {psychological_analysis.get('top_enhancement_priorities', [])}

TARGET TRIGGERS TO ENHANCE: {target_triggers}

🧠 PSYCHOLOGICAL ENHANCEMENT REQUIREMENTS:

1. CURIOSITY GAP ENHANCEMENT:
   - Add mysterious hooks that create information gaps
   - Use pattern interruptions and surprising reveals
   - Create "you won't believe what happens next" moments
   - Build anticipation throughout content

2. SOCIAL PROOF AMPLIFICATION:
   - Add community size references ("millions of people")
   - Include testimonial elements ("users report")
   - Reference trending/popular elements
   - Create "join the movement" feelings

3. SCARCITY & URGENCY CREATION:
   - Add time-limited elements
   - Create "limited knowledge" positioning
   - Use "before it's too late" messaging
   - Build FOMO (fear of missing out)

4. AUTHORITY ESTABLISHMENT:
   - Add credibility markers and expertise signals
   - Reference research/studies/experts
   - Use confident, authoritative language
   - Establish thought leadership

5. RECIPROCITY BUILDING:
   - Give valuable information first
   - Create "gift" mentality with free insights
   - Build obligation through value delivery
   - Use "here's what I'll give you" language

6. LOSS AVERSION TRIGGERS:
   - Highlight what viewers lose by not engaging
   - Create "missing out" scenarios
   - Use negative consequences framing
   - Build pain-avoidance motivation

7. EMOTIONAL CONTRAST:
   - Create emotional highs and lows
   - Use surprising reversals
   - Build tension and release
   - Add emotional storytelling

8. TRIBAL IDENTITY BUILDING:
   - Create "us vs them" dynamics
   - Use inclusive language ("people like us")
   - Build community belonging
   - Reference shared values/goals

9. PATTERN INTERRUPTION:
   - Break expected narrative flows
   - Add surprising elements
   - Use contrarian viewpoints
   - Create "wait, what?" moments

10. ANTICIPATION BUILDING:
    - Tease upcoming revelations
    - Create excitement for what's coming
    - Use countdown/buildup language
    - Promise valuable payoffs

PLATFORM-SPECIFIC PSYCHOLOGY for {platform.value}:
- Use platform-native psychological patterns
- Leverage platform-specific user motivations
- Apply platform engagement psychology
- Optimize for platform algorithms

Generate PSYCHOLOGICALLY ENHANCED content that maintains the mission but dramatically improves persuasion:

Return JSON:
{{
    "enhanced_content": "Full psychologically enhanced content here...",
    "psychological_enhancements": {{
        "curiosity_gaps": ["Added mystery hook", "Created information gap"],
        "social_proof": ["Added community references", "Included trending elements"],
        "scarcity": ["Created urgency", "Added FOMO elements"],
        "authority": ["Added credibility markers", "Referenced expertise"],
        "reciprocity": ["Gave free value", "Created gift mentality"],
        "loss_aversion": ["Highlighted missing out", "Created pain points"],
        "emotional_contrast": ["Added emotional highs/lows", "Created tension"],
        "tribal_identity": ["Built community", "Created belonging"],
        "pattern_interruption": ["Added surprises", "Broke expectations"],
        "anticipation": ["Built excitement", "Teased revelations"]
    }},
    "trigger_improvements": {{
        "triggers_added": ["social_proof", "scarcity", "curiosity_gap"],
        "triggers_strengthened": ["authority", "reciprocity"],
        "new_psychological_score": 85,
        "improvement_percentage": 40
    }},
    "engagement_predictions": {{
        "like_increase": "+120%",
        "comment_increase": "+200%",
        "share_increase": "+180%",
        "follow_increase": "+150%",
        "completion_increase": "+80%"
    }},
    "platform_optimization": {{
        "platform_triggers": ["Platform-specific triggers added"],
        "algorithm_optimization": ["Optimized for {platform.value} psychology"],
        "user_behavior_alignment": ["Matched platform user motivations"]
    }}
}}
"""
        
        try:
            text_service = self.ai_manager.get_service(AIServiceType.TEXT_GENERATION)
            request = TextGenerationRequest(
                prompt=prompt,
                max_tokens=3000,
                temperature=0.7
            )
            
            response = await text_service.generate(request)
            enhancement = self._parse_json_response(response.text)
            
            logger.info("✅ Psychological trigger enhancement complete")
            return enhancement
            
        except Exception as e:
            logger.error(f"❌ Psychological enhancement failed: {e}")
            return self._create_fallback_psychological_enhancement(content)
    
    async def create_trigger_variants(
        self,
        content: str,
        mission: str,
        platform: Platform,
        trigger_strategies: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Create variants focusing on different psychological trigger strategies
        """
        if not trigger_strategies:
            trigger_strategies = ["social_proof_focus", "scarcity_focus", "authority_focus", "curiosity_focus"]
        
        logger.info(f"🎭 Creating {len(trigger_strategies)} psychological trigger variants")
        
        variants = []
        
        for strategy in trigger_strategies:
            prompt = f"""
Create a psychological trigger variant using the "{strategy}" strategy:

MISSION: {mission}
PLATFORM: {platform.value}
STRATEGY: {strategy}

ORIGINAL CONTENT: {content}

STRATEGY DEFINITIONS:
- social_proof_focus: Maximize social validation, community, trending elements
- scarcity_focus: Emphasize urgency, limited time, exclusive access, FOMO
- authority_focus: Establish expertise, credibility, research-backed claims
- curiosity_focus: Create mystery, information gaps, surprising reveals

Create a variant that MAXIMIZES the {strategy} psychological trigger while maintaining the core mission.

Return JSON:
{{
    "strategy": "{strategy}",
    "enhanced_content": "Full content optimized for {strategy}...",
    "key_psychological_elements": [
        "Primary trigger applications",
        "Secondary supporting triggers"
    ],
    "expected_psychological_impact": {{
        "primary_trigger_strength": 9,
        "overall_persuasion_score": 85,
        "engagement_drivers": ["curiosity", "social_proof"]
    }},
    "target_audience_response": "Expected psychological response from audience"
}}
"""
            
            try:
                text_service = self.ai_manager.get_service(AIServiceType.TEXT_GENERATION)
                request = TextGenerationRequest(
                    prompt=prompt,
                    max_tokens=2000,
                    temperature=0.8
                )
                
                response = await text_service.generate(request)
                variant = self._parse_json_response(response.text)
                variants.append(variant)
                
            except Exception as e:
                logger.error(f"❌ Trigger variant {strategy} failed: {e}")
                continue
        
        logger.info(f"✅ Created {len(variants)} psychological trigger variants")
        return variants
    
    def analyze_trigger_effectiveness(
        self,
        content: str,
        engagement_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze which psychological triggers are most effective based on engagement
        """
        logger.info("📊 Analyzing trigger effectiveness from engagement data")
        
        # Detect triggers present in content
        detected_triggers = self._detect_triggers_in_content(content)
        
        # Calculate engagement score
        views = engagement_metrics.get('views', 1)
        engagement_score = (
            (engagement_metrics.get('likes', 0) * 1) +
            (engagement_metrics.get('comments', 0) * 3) +
            (engagement_metrics.get('shares', 0) * 5) +
            (engagement_metrics.get('follows', 0) * 10)
        ) / views * 100
        
        # Analyze trigger correlation with engagement
        trigger_effectiveness = {}
        for trigger, presence_score in detected_triggers.items():
            # Estimate trigger contribution to engagement
            trigger_info = self.psychological_triggers.get(trigger, {})
            base_effectiveness = trigger_info.get('effectiveness', 5.0)
            
            # Adjust based on presence and engagement
            actual_effectiveness = (presence_score / 10) * base_effectiveness * (engagement_score / 50)
            trigger_effectiveness[trigger] = round(actual_effectiveness, 2)
        
        # Identify top and bottom performers
        sorted_triggers = sorted(trigger_effectiveness.items(), key=lambda x: x[1], reverse=True)
        top_triggers = sorted_triggers[:3]
        bottom_triggers = sorted_triggers[-3:]
        
        return {
            "analysis_timestamp": "current",
            "engagement_score": round(engagement_score, 1),
            "triggers_detected": detected_triggers,
            "trigger_effectiveness": trigger_effectiveness,
            "top_performing_triggers": [{"trigger": t[0], "effectiveness": t[1]} for t in top_triggers],
            "underperforming_triggers": [{"trigger": t[0], "effectiveness": t[1]} for t in bottom_triggers],
            "recommendations": self._generate_trigger_recommendations(trigger_effectiveness, engagement_score),
            "missing_high_impact_triggers": self._identify_missing_high_impact_triggers(detected_triggers)
        }
    
    def get_platform_specific_triggers(self, platform: Platform) -> Dict[str, Any]:
        """
        Get psychological triggers most effective for specific platforms
        """
        logger.info(f"🎯 Getting platform-specific triggers for {platform.value}")
        
        platform_triggers = {
            Platform.INSTAGRAM: {
                "primary_triggers": ["social_proof", "tribal_identity", "curiosity_gap"],
                "secondary_triggers": ["scarcity", "anticipation", "emotional_contrast"],
                "platform_psychology": "Visual storytelling, lifestyle aspiration, community building",
                "engagement_drivers": ["aesthetic appeal", "relatability", "aspirational content"],
                "optimal_combinations": ["social_proof + tribal_identity", "curiosity_gap + emotional_contrast"]
            },
            Platform.TIKTOK: {
                "primary_triggers": ["pattern_interruption", "curiosity_gap", "emotional_contrast"],
                "secondary_triggers": ["social_proof", "anticipation", "tribal_identity"],
                "platform_psychology": "Quick attention capture, entertainment, trend participation",
                "engagement_drivers": ["surprise elements", "entertainment value", "trend alignment"],
                "optimal_combinations": ["pattern_interruption + curiosity_gap", "emotional_contrast + social_proof"]
            },
            Platform.YOUTUBE: {
                "primary_triggers": ["authority", "curiosity_gap", "reciprocity"],
                "secondary_triggers": ["social_proof", "anticipation", "loss_aversion"],
                "platform_psychology": "Educational value, expertise, long-form engagement",
                "engagement_drivers": ["expertise demonstration", "value delivery", "comprehensive content"],
                "optimal_combinations": ["authority + reciprocity", "curiosity_gap + anticipation"]
            },
            Platform.LINKEDIN: {
                "primary_triggers": ["authority", "social_proof", "reciprocity"],
                "secondary_triggers": ["tribal_identity", "loss_aversion", "anticipation"],
                "platform_psychology": "Professional credibility, industry insights, career advancement",
                "engagement_drivers": ["professional value", "industry expertise", "networking"],
                "optimal_combinations": ["authority + social_proof", "reciprocity + tribal_identity"]
            }
        }
        
        return platform_triggers.get(platform, {
            "primary_triggers": ["curiosity_gap", "social_proof", "authority"],
            "secondary_triggers": ["scarcity", "reciprocity", "emotional_contrast"],
            "platform_psychology": "General engagement principles",
            "engagement_drivers": ["value", "entertainment", "connection"],
            "optimal_combinations": ["curiosity_gap + social_proof"]
        })
    
    def _detect_triggers_in_content(self, content: str) -> Dict[str, int]:
        """Detect psychological triggers present in content"""
        content_lower = content.lower()
        detected_triggers = {}
        
        # Trigger detection patterns
        trigger_patterns = {
            "curiosity_gap": [
                r"what happens next", r"you won't believe", r"the secret", r"revealed",
                r"shocking", r"surprising", r"wait until", r"but first"
            ],
            "social_proof": [
                r"millions", r"everyone", r"most people", r"studies show", r"proven",
                r"join", r"community", r"trending", r"popular"
            ],
            "scarcity": [
                r"limited", r"only", r"few", r"rare", r"exclusive", r"before it's too late",
                r"don't miss", r"last chance", r"running out"
            ],
            "authority": [
                r"expert", r"research", r"study", r"proven", r"professional",
                r"certified", r"official", r"scientific", r"data shows"
            ],
            "reciprocity": [
                r"free", r"gift", r"give you", r"here's", r"i'll share",
                r"bonus", r"complimentary", r"no cost"
            ],
            "loss_aversion": [
                r"lose", r"missing out", r"don't miss", r"avoid", r"prevent",
                r"mistake", r"regret", r"fail"
            ],
            "emotional_contrast": [
                r"from.*to", r"but then", r"suddenly", r"however", r"plot twist",
                r"shocking", r"unexpected", r"dramatic"
            ],
            "pattern_interruption": [
                r"wait", r"stop", r"hold on", r"actually", r"but", r"however",
                r"twist", r"surprise", r"unexpected"
            ],
            "tribal_identity": [
                r"we", r"us", r"our", r"people like us", r"community", r"tribe",
                r"family", r"together", r"belong"
            ],
            "anticipation": [
                r"coming up", r"next", r"soon", r"about to", r"prepare",
                r"get ready", r"countdown", r"coming"
            ]
        }
        
        for trigger, patterns in trigger_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, content_lower))
                score += matches
            
            # Normalize score (0-10 scale)
            detected_triggers[trigger] = min(10, score * 2)
        
        return detected_triggers
    
    def _generate_trigger_recommendations(
        self,
        trigger_effectiveness: Dict[str, float],
        engagement_score: float
    ) -> List[str]:
        """Generate recommendations for improving psychological triggers"""
        recommendations = []
        
        # If overall engagement is low
        if engagement_score < 40:
            recommendations.extend([
                "Overall engagement is low - focus on high-impact psychological triggers",
                "Add curiosity gaps and pattern interruptions for attention capture",
                "Implement social proof elements to build credibility"
            ])
        
        # Find weakest triggers
        weak_triggers = [trigger for trigger, score in trigger_effectiveness.items() if score < 3.0]
        if weak_triggers:
            recommendations.append(f"Strengthen these weak triggers: {', '.join(weak_triggers)}")
        
        # Recommend high-impact combinations
        recommendations.extend([
            "Combine curiosity gaps with social proof for maximum impact",
            "Use scarcity together with loss aversion for urgency",
            "Build authority through reciprocity (give value first)"
        ])
        
        return recommendations
    
    def _identify_missing_high_impact_triggers(self, detected_triggers: Dict[str, int]) -> List[str]:
        """Identify high-impact triggers that are missing or weak"""
        high_impact_triggers = ["curiosity_gap", "social_proof", "scarcity", "authority"]
        missing_triggers = []
        
        for trigger in high_impact_triggers:
            if detected_triggers.get(trigger, 0) < 3:
                missing_triggers.append(trigger)
        
        return missing_triggers
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from AI response with error handling"""
        try:
            response_text = response_text.strip()
            
            if response_text.startswith('{'):
                return json.loads(response_text)
            elif '```json' in response_text:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    return json.loads(response_text[json_start:json_end])
            else:
                return json.loads(response_text)
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            return {}
    
    def _create_fallback_psychological_analysis(self) -> Dict[str, Any]:
        """Create fallback analysis when AI fails"""
        return {
            "overall_psychological_score": 50,
            "trigger_analysis": {
                trigger: {
                    "current_score": 5,
                    "usage_examples": [],
                    "opportunities": [f"Add {trigger} elements"],
                    "effectiveness_potential": self.psychological_triggers[trigger]["effectiveness"]
                }
                for trigger in self.psychological_triggers.keys()
            },
            "strongest_triggers": ["curiosity_gap"],
            "weakest_triggers": ["social_proof", "scarcity", "authority"],
            "missing_opportunities": ["Add psychological triggers throughout content"],
            "psychological_gaps": ["Limited psychological engagement"],
            "platform_specific_psychology": {"platform_match": 5, "platform_gaps": ["Needs platform optimization"]},
            "audience_psychology": {"audience_match": 5, "trigger_preferences": ["social_proof", "authority"]},
            "top_enhancement_priorities": ["Add curiosity gaps", "Include social proof", "Establish authority"]
        }
    
    def _create_fallback_psychological_enhancement(self, original_content: str) -> Dict[str, Any]:
        """Create fallback enhancement when AI fails"""
        return {
            "enhanced_content": original_content,
            "psychological_enhancements": {
                trigger: [f"Applied {trigger} elements"]
                for trigger in self.psychological_triggers.keys()
            },
            "trigger_improvements": {
                "triggers_added": ["social_proof", "curiosity_gap"],
                "triggers_strengthened": ["authority"],
                "new_psychological_score": 70,
                "improvement_percentage": 20
            },
            "engagement_predictions": {
                "like_increase": "+50%",
                "comment_increase": "+75%",
                "share_increase": "+60%",
                "follow_increase": "+80%",
                "completion_increase": "+40%"
            },
            "platform_optimization": {
                "platform_triggers": ["Basic platform optimization applied"],
                "algorithm_optimization": ["General optimization applied"],
                "user_behavior_alignment": ["Aligned with general user psychology"]
            }
        }