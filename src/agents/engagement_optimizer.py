"""
Advanced Engagement Optimization System
Optimizes content for maximum user engagement (likes, follows, reactions)
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

class EngagementOptimizer:
    """
    Analyzes and optimizes content for maximum engagement and user interaction
    Focuses on likes, follows, reactions, and message understanding
    """
    
    def __init__(self, ai_manager: AIServiceManager):
        self.ai_manager = ai_manager
        logger.info("✅ Engagement Optimizer initialized")
    
    async def analyze_engagement_potential(
        self,
        mission: str,
        script_segments: List[Dict],
        platform: Platform,
        target_audience: str = None
    ) -> Dict[str, Any]:
        """
        Analyze content's engagement potential and identify improvement opportunities
        
        Returns:
            Comprehensive engagement analysis with specific recommendations
        """
        logger.info(f"🎯 Analyzing engagement potential for '{mission}' on {platform.value}")
        
        # Build analysis prompt focusing on engagement factors
        prompt = f"""
Analyze this content for maximum engagement potential on {platform.value}:

MISSION: {mission}
TARGET AUDIENCE: {target_audience or "General audience"}

SCRIPT SEGMENTS:
{self._format_segments_for_analysis(script_segments)}

🎯 ENGAGEMENT ANALYSIS REQUIRED:

1. MESSAGE CLARITY ASSESSMENT:
   - Is the core message immediately understandable?
   - Does each segment reinforce the main point?
   - Are there confusing or unclear elements?
   - Rate message clarity: 1-100

2. EMOTIONAL ENGAGEMENT ANALYSIS:
   - What emotions does this content trigger?
   - Are there emotional peaks and valleys?
   - Does it create personal connection?
   - Identify emotional engagement score: 1-100

3. PLATFORM OPTIMIZATION ASSESSMENT:
   - How well is this optimized for {platform.value}?
   - Does it follow platform-specific engagement patterns?
   - Are there platform-native elements missing?
   - Platform optimization score: 1-100

4. VIRAL POTENTIAL EVALUATION:
   - What makes people want to share this?
   - Are there quotable/memorable moments?
   - Does it spark conversation/debate?
   - Viral potential score: 1-100

5. ACTION TRIGGER IDENTIFICATION:
   - What specific actions will viewers take?
   - Are CTAs clear and compelling?
   - Does it inspire likes, follows, comments?
   - Action likelihood score: 1-100

6. ENGAGEMENT KILLERS DETECTION:
   - What elements reduce engagement?
   - Are there boring or off-topic segments?
   - What causes viewers to scroll away?
   - List specific problems

7. PSYCHOLOGICAL TRIGGERS ANALYSIS:
   - What psychological principles are used?
   - Are there curiosity gaps, social proof, urgency?
   - How can psychology be enhanced?
   - Psychology utilization score: 1-100

Return JSON:
{{
    "overall_engagement_score": 85,
    "message_clarity": {{
        "score": 75,
        "strengths": ["Clear opening", "Simple language"],
        "weaknesses": ["Confusing middle section", "Unclear conclusion"],
        "improvements": ["Simplify technical terms", "Stronger ending"]
    }},
    "emotional_engagement": {{
        "score": 80,
        "primary_emotions": ["curiosity", "excitement"],
        "emotional_journey": ["intrigue → build → payoff"],
        "missing_emotions": ["urgency", "social connection"],
        "enhancement_opportunities": ["Add personal stories", "Create urgency"]
    }},
    "platform_optimization": {{
        "score": 70,
        "platform_strengths": ["Good length", "Visual potential"],
        "platform_gaps": ["Missing trending elements", "No engagement hooks"],
        "platform_specific_tips": ["Add hashtag moments", "Include trending references"]
    }},
    "viral_potential": {{
        "score": 65,
        "shareable_elements": ["Surprising fact", "Useful tip"],
        "viral_gaps": ["No debate trigger", "Not quotable enough"],
        "viral_enhancements": ["Add controversial angle", "Create quotable moments"]
    }},
    "action_triggers": {{
        "score": 60,
        "current_actions": ["watch", "maybe like"],
        "missing_actions": ["follow", "comment", "share"],
        "action_improvements": ["Stronger CTA", "Follow incentive", "Comment question"]
    }},
    "engagement_killers": [
        "Segment 3 is too technical",
        "No clear benefit stated",
        "Ending feels abrupt"
    ],
    "psychological_triggers": {{
        "score": 55,
        "used_triggers": ["curiosity", "novelty"],
        "missing_triggers": ["social proof", "scarcity", "authority"],
        "trigger_opportunities": ["Add testimonials", "Create urgency", "Establish credibility"]
    }},
    "top_recommendations": [
        "Simplify technical language in segment 3",
        "Add compelling follow CTA at end",
        "Include social proof elements",
        "Create stronger emotional hook in opening"
    ]
}}
"""
        
        try:
            text_service = self.ai_manager.get_service(AIServiceType.TEXT_GENERATION)
            request = TextGenerationRequest(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.7
            )
            
            response = await text_service.generate(request)
            analysis = self._parse_json_response(response.text)
            
            logger.info(f"📊 Engagement analysis complete - Overall score: {analysis.get('overall_engagement_score', 0)}")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Engagement analysis failed: {e}")
            return self._create_fallback_analysis()
    
    async def optimize_for_engagement(
        self,
        mission: str,
        script_segments: List[Dict],
        platform: Platform,
        engagement_analysis: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate optimized version of content for maximum engagement
        """
        logger.info(f"🚀 Optimizing content for engagement on {platform.value}")
        
        # Get analysis if not provided
        if not engagement_analysis:
            engagement_analysis = await self.analyze_engagement_potential(
                mission, script_segments, platform
            )
        
        # Build optimization prompt
        prompt = f"""
Optimize this content for MAXIMUM ENGAGEMENT on {platform.value}:

ORIGINAL MISSION: {mission}
CURRENT ENGAGEMENT SCORE: {engagement_analysis.get('overall_engagement_score', 50)}

CURRENT SCRIPT:
{self._format_segments_for_analysis(script_segments)}

ENGAGEMENT ANALYSIS FINDINGS:
- Message Clarity Issues: {engagement_analysis.get('message_clarity', {}).get('weaknesses', [])}
- Emotional Gaps: {engagement_analysis.get('emotional_engagement', {}).get('missing_emotions', [])}
- Platform Gaps: {engagement_analysis.get('platform_optimization', {}).get('platform_gaps', [])}
- Viral Gaps: {engagement_analysis.get('viral_potential', {}).get('viral_gaps', [])}
- Action Gaps: {engagement_analysis.get('action_triggers', {}).get('missing_actions', [])}

🎯 OPTIMIZATION REQUIREMENTS:

1. MAXIMIZE MESSAGE CLARITY:
   - Make core message instantly clear
   - Remove confusing elements
   - Use simple, powerful language
   - Ensure every word serves engagement

2. EMOTIONAL OPTIMIZATION:
   - Create strong emotional hooks
   - Build emotional journey with peaks
   - Add personal connection elements
   - Trigger desired emotional responses

3. PLATFORM-NATIVE OPTIMIZATION:
   - Follow {platform.value} best practices
   - Include platform-specific elements
   - Use platform psychology
   - Optimize for platform algorithms

4. VIRAL MECHANICS:
   - Add shareable moments
   - Create quotable content
   - Include conversation starters
   - Build debate/discussion triggers

5. ACTION OPTIMIZATION:
   - Clear, compelling CTAs
   - Multiple engagement opportunities
   - Follow incentives
   - Comment triggers

6. PSYCHOLOGICAL ENHANCEMENT:
   - Add curiosity gaps
   - Include social proof
   - Create urgency/scarcity
   - Use authority/credibility

Generate OPTIMIZED script maintaining the mission but dramatically improving engagement:

Return JSON:
{{
    "optimized_script": {{
        "segments": [
            {{
                "segment_id": 1,
                "optimized_text": "Compelling opening with hook...",
                "engagement_elements": ["curiosity gap", "emotional hook"],
                "platform_optimizations": ["trending reference", "visual cue"],
                "psychological_triggers": ["novelty", "social proof"]
            }}
        ]
    }},
    "engagement_improvements": {{
        "clarity_enhancements": ["Simplified technical terms", "Clearer benefit"],
        "emotional_upgrades": ["Added personal story", "Created urgency"],
        "platform_additions": ["Trending hashtag moment", "Platform-native phrase"],
        "viral_elements": ["Quotable moment", "Debate trigger"],
        "action_triggers": ["Follow CTA", "Comment question"]
    }},
    "expected_results": {{
        "engagement_score_improvement": "+35 points",
        "like_increase": "+150%",
        "follow_increase": "+200%",
        "comment_increase": "+300%",
        "share_increase": "+250%"
    }}
}}
"""
        
        try:
            text_service = self.ai_manager.get_service(AIServiceType.TEXT_GENERATION)
            request = TextGenerationRequest(
                prompt=prompt,
                max_tokens=2500,
                temperature=0.8
            )
            
            response = await text_service.generate(request)
            optimization = self._parse_json_response(response.text)
            
            logger.info("✅ Content optimization complete")
            return optimization
            
        except Exception as e:
            logger.error(f"❌ Content optimization failed: {e}")
            return self._create_fallback_optimization(script_segments)
    
    async def create_engagement_variants(
        self,
        mission: str,
        original_script: str,
        platform: Platform,
        num_variants: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Create multiple engagement-optimized variants for A/B testing
        """
        logger.info(f"🎭 Creating {num_variants} engagement variants")
        
        # Define different engagement strategies
        strategies = [
            "emotional_storytelling",
            "controversial_angle", 
            "educational_authority",
            "entertainment_first",
            "community_building"
        ]
        
        variants = []
        
        for i in range(min(num_variants, len(strategies))):
            strategy = strategies[i]
            
            prompt = f"""
Create an engagement-optimized variant using the "{strategy}" strategy:

ORIGINAL MISSION: {mission}
PLATFORM: {platform.value}
STRATEGY: {strategy}

ORIGINAL SCRIPT: {original_script}

STRATEGY DEFINITIONS:
- emotional_storytelling: Focus on personal stories, emotions, relatability
- controversial_angle: Add debate elements, contrarian views, discussion triggers  
- educational_authority: Emphasize expertise, credibility, learning value
- entertainment_first: Prioritize fun, humor, entertainment value
- community_building: Focus on shared identity, belonging, group participation

Create a variant that maximizes engagement using this strategy while maintaining the core mission.

Return JSON:
{{
    "variant_id": {i+1},
    "strategy": "{strategy}",
    "optimized_script": "Full optimized script here...",
    "key_changes": ["Added personal story", "Included controversial question"],
    "engagement_focus": ["likes", "comments", "shares"],
    "expected_performance": "Higher emotional engagement, more comments"
}}
"""
            
            try:
                text_service = self.ai_manager.get_service(AIServiceType.TEXT_GENERATION)
                request = TextGenerationRequest(
                    prompt=prompt,
                    max_tokens=1500,
                    temperature=0.9
                )
                
                response = await text_service.generate(request)
                variant = self._parse_json_response(response.text)
                variants.append(variant)
                
            except Exception as e:
                logger.error(f"❌ Variant {i+1} creation failed: {e}")
                continue
        
        logger.info(f"✅ Created {len(variants)} engagement variants")
        return variants
    
    def analyze_engagement_metrics(
        self,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze engagement metrics and provide optimization insights
        """
        logger.info("📈 Analyzing engagement metrics")
        
        # Calculate engagement rates
        total_views = metrics.get('views', 1)
        likes = metrics.get('likes', 0)
        comments = metrics.get('comments', 0)
        shares = metrics.get('shares', 0)
        follows = metrics.get('follows', 0)
        
        # Calculate rates
        like_rate = (likes / total_views) * 100
        comment_rate = (comments / total_views) * 100
        share_rate = (shares / total_views) * 100
        follow_rate = (follows / total_views) * 100
        
        # Overall engagement score
        engagement_score = (like_rate * 1) + (comment_rate * 3) + (share_rate * 5) + (follow_rate * 10)
        
        # Determine performance level
        if engagement_score >= 15:
            performance = "excellent"
        elif engagement_score >= 10:
            performance = "good"
        elif engagement_score >= 5:
            performance = "average"
        else:
            performance = "poor"
        
        # Generate insights
        insights = []
        if like_rate < 2:
            insights.append("Low like rate - improve emotional hooks and relatability")
        if comment_rate < 0.5:
            insights.append("Low comment rate - add questions and controversial elements")
        if share_rate < 0.1:
            insights.append("Low share rate - create more quotable and shareable moments")
        if follow_rate < 0.05:
            insights.append("Low follow rate - strengthen follow CTAs and value proposition")
        
        return {
            "engagement_score": round(engagement_score, 2),
            "performance_level": performance,
            "rates": {
                "like_rate": round(like_rate, 2),
                "comment_rate": round(comment_rate, 2),
                "share_rate": round(share_rate, 2),
                "follow_rate": round(follow_rate, 2)
            },
            "insights": insights,
            "recommendations": self._generate_metric_recommendations(
                like_rate, comment_rate, share_rate, follow_rate
            )
        }
    
    def _format_segments_for_analysis(self, segments: List[Dict]) -> str:
        """Format script segments for AI analysis"""
        formatted = []
        for i, segment in enumerate(segments, 1):
            text = segment.get('text', '') or segment.get('dialogue', '') or segment.get('audio', {}).get('dialogue', '')
            formatted.append(f"Segment {i}: {text}")
        return "\n".join(formatted)
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from AI response with error handling"""
        try:
            # Clean response
            response_text = response_text.strip()
            
            # Extract JSON
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
    
    def _create_fallback_analysis(self) -> Dict[str, Any]:
        """Create fallback analysis when AI fails"""
        return {
            "overall_engagement_score": 50,
            "message_clarity": {"score": 50, "improvements": ["Simplify language"]},
            "emotional_engagement": {"score": 50, "enhancement_opportunities": ["Add emotional hooks"]},
            "platform_optimization": {"score": 50, "platform_specific_tips": ["Follow platform best practices"]},
            "viral_potential": {"score": 50, "viral_enhancements": ["Add shareable elements"]},
            "action_triggers": {"score": 50, "action_improvements": ["Stronger CTAs"]},
            "engagement_killers": ["Generic fallback analysis"],
            "psychological_triggers": {"score": 50, "trigger_opportunities": ["Add psychological elements"]},
            "top_recommendations": ["Improve emotional engagement", "Add clear CTAs", "Optimize for platform"]
        }
    
    def _create_fallback_optimization(self, segments: List[Dict]) -> Dict[str, Any]:
        """Create fallback optimization when AI fails"""
        return {
            "optimized_script": {"segments": segments},
            "engagement_improvements": {
                "clarity_enhancements": ["Simplified language"],
                "emotional_upgrades": ["Added engagement elements"],
                "platform_additions": ["Platform optimizations"],
                "viral_elements": ["Shareable content"],
                "action_triggers": ["Clear CTAs"]
            },
            "expected_results": {
                "engagement_score_improvement": "+20 points",
                "like_increase": "+50%",
                "follow_increase": "+75%",
                "comment_increase": "+100%",
                "share_increase": "+100%"
            }
        }
    
    def _generate_metric_recommendations(
        self,
        like_rate: float,
        comment_rate: float, 
        share_rate: float,
        follow_rate: float
    ) -> List[str]:
        """Generate specific recommendations based on metric performance"""
        recommendations = []
        
        if like_rate < 2:
            recommendations.extend([
                "Add more relatable content and emotional hooks",
                "Use more engaging visuals and animations",
                "Include trending topics and current events"
            ])
        
        if comment_rate < 0.5:
            recommendations.extend([
                "Ask specific questions to encourage responses",
                "Create controversial or debate-worthy content",
                "Include interactive elements and polls"
            ])
        
        if share_rate < 0.1:
            recommendations.extend([
                "Create more quotable and memorable moments", 
                "Add surprising facts or insights",
                "Build content worth sharing with friends"
            ])
        
        if follow_rate < 0.05:
            recommendations.extend([
                "Strengthen your unique value proposition",
                "Add clear follow CTAs with benefits",
                "Build stronger personal brand elements"
            ])
        
        return recommendations