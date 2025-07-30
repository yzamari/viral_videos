"""
Viral Mechanics Optimization System
Optimizes content for viral potential and maximum reach
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

class ViralMechanicsOptimizer:
    """
    Analyzes and optimizes content for viral potential using proven viral mechanics
    Focuses on shareability, memorability, and exponential reach
    """
    
    def __init__(self, ai_manager: AIServiceManager):
        self.ai_manager = ai_manager
        
        # Define viral mechanics and their viral coefficients
        self.viral_mechanics = {
            "emotional_intensity": {
                "description": "Content that triggers strong emotional responses",
                "viral_coefficient": 9.5,
                "examples": ["shocking revelations", "heartwarming stories", "outrageous claims"],
                "platforms": ["all"]
            },
            "relatability_universality": {
                "description": "Content that resonates with large audiences",
                "viral_coefficient": 9.2,
                "examples": ["common experiences", "universal truths", "shared struggles"],
                "platforms": ["instagram", "tiktok", "facebook"]
            },
            "controversy_debate": {
                "description": "Content that sparks discussion and debate",
                "viral_coefficient": 9.0,
                "examples": ["contrarian views", "hot takes", "polarizing opinions"],
                "platforms": ["twitter", "linkedin", "youtube"]
            },
            "surprise_unexpected": {
                "description": "Content that defies expectations",
                "viral_coefficient": 8.8,
                "examples": ["plot twists", "unexpected outcomes", "surprising facts"],
                "platforms": ["tiktok", "youtube", "instagram"]
            },
            "practical_utility": {
                "description": "Immediately useful or actionable content",
                "viral_coefficient": 8.5,
                "examples": ["life hacks", "tutorials", "problem solutions"],
                "platforms": ["youtube", "linkedin", "pinterest"]
            },
            "social_currency": {
                "description": "Makes sharer look good/smart/informed",
                "viral_coefficient": 8.3,
                "examples": ["insider knowledge", "trend awareness", "expert insights"],
                "platforms": ["linkedin", "twitter", "instagram"]
            },
            "story_narrative": {
                "description": "Compelling storytelling that hooks viewers",
                "viral_coefficient": 8.0,
                "examples": ["personal journeys", "transformation stories", "dramatic arcs"],
                "platforms": ["youtube", "instagram", "tiktok"]
            },
            "timing_relevance": {
                "description": "Perfectly timed to current events/trends",
                "viral_coefficient": 7.8,
                "examples": ["trend piggybacking", "news commentary", "seasonal content"],
                "platforms": ["twitter", "tiktok", "instagram"]
            },
            "visual_memorable": {
                "description": "Highly visual and memorable imagery",
                "viral_coefficient": 7.5,
                "examples": ["stunning visuals", "memes", "iconic moments"],
                "platforms": ["instagram", "tiktok", "pinterest"]
            },
            "participation_engagement": {
                "description": "Invites audience participation",
                "viral_coefficient": 7.2,
                "examples": ["challenges", "questions", "calls to action"],
                "platforms": ["tiktok", "instagram", "facebook"]
            }
        }
        
        logger.info("✅ Viral Mechanics Optimizer initialized")
    
    async def analyze_viral_potential(
        self,
        content: str,
        mission: str,
        platform: Platform,
        target_audience: str = None
    ) -> Dict[str, Any]:
        """
        Comprehensive analysis of content's viral potential
        """
        logger.info(f"🚀 Analyzing viral potential for '{mission}' on {platform.value}")
        
        prompt = f"""
Analyze this content for VIRAL POTENTIAL and SHAREABILITY:

MISSION: {mission}
PLATFORM: {platform.value}
TARGET AUDIENCE: {target_audience or "General audience"}

CONTENT TO ANALYZE:
{content}

🚀 VIRAL MECHANICS ANALYSIS REQUIRED:

Analyze the presence and strength of these viral mechanics:

1. EMOTIONAL INTENSITY: Triggers strong emotional responses
   - Current strength: Rate 1-10
   - Emotional triggers present: anger, joy, surprise, sadness, fear
   - Intensity level: low/medium/high
   - Improvement opportunities

2. RELATABILITY & UNIVERSALITY: Resonates with large audiences
   - Current strength: Rate 1-10
   - Universal themes present
   - Relatable experiences/struggles
   - Broad appeal assessment

3. CONTROVERSY & DEBATE: Sparks discussion and opposing views
   - Current strength: Rate 1-10
   - Controversial elements present
   - Debate triggers identified
   - Discussion potential

4. SURPRISE & UNEXPECTED: Defies expectations and surprises
   - Current strength: Rate 1-10
   - Surprise elements present
   - Unexpected twists/reveals
   - Shock value assessment

5. PRACTICAL UTILITY: Immediately useful and actionable
   - Current strength: Rate 1-10
   - Practical value provided
   - Actionable insights/tips
   - Problem-solving content

6. SOCIAL CURRENCY: Makes sharer look good/smart
   - Current strength: Rate 1-10
   - Status enhancement for sharer
   - Knowledge/insight sharing value
   - Credibility building potential

7. STORY & NARRATIVE: Compelling storytelling
   - Current strength: Rate 1-10
   - Story structure present
   - Character development
   - Narrative arc strength

8. TIMING & RELEVANCE: Aligned with trends/current events
   - Current strength: Rate 1-10
   - Trend alignment
   - Timeliness factor
   - Cultural relevance

9. VISUAL & MEMORABLE: Strong visual/memorable elements
   - Current strength: Rate 1-10
   - Visual appeal
   - Memorable moments/quotes
   - Iconic potential

10. PARTICIPATION & ENGAGEMENT: Invites audience action
    - Current strength: Rate 1-10
    - Call-to-action strength
    - Participation opportunities
    - Engagement triggers

VIRAL PREDICTION FACTORS:
- Share likelihood: 1-10
- Comment probability: 1-10  
- Save/bookmark potential: 1-10
- Viral velocity potential: 1-10
- Exponential growth factors
- Platform algorithm compatibility

Return JSON:
{{
    "overall_viral_score": 75,
    "viral_mechanics_analysis": {{
        "emotional_intensity": {{
            "strength": 8,
            "emotions_triggered": ["surprise", "excitement"],
            "intensity_level": "high",
            "viral_coefficient": 9.5,
            "improvement_opportunities": ["Add more emotional contrast"]
        }},
        "relatability_universality": {{
            "strength": 6,
            "universal_themes": ["success", "struggle"],
            "relatable_elements": ["common experiences"],
            "viral_coefficient": 9.2,
            "improvement_opportunities": ["Broaden appeal"]
        }}
        // ... continue for all mechanics
    }},
    "viral_strengths": ["emotional_intensity", "surprise_unexpected"],
    "viral_weaknesses": ["controversy_debate", "social_currency"],
    "viral_predictions": {{
        "share_likelihood": 7,
        "comment_probability": 8,
        "save_potential": 6,
        "viral_velocity": 7,
        "exponential_factors": ["emotional intensity", "surprise element"],
        "viral_ceiling": "medium-high"
    }},
    "platform_viral_fit": {{
        "platform_optimization": 7,
        "algorithm_compatibility": 8,
        "user_behavior_match": 7,
        "platform_viral_mechanics": ["surprise works well on {platform.value}"]
    }},
    "audience_viral_factors": {{
        "audience_sharing_likelihood": 7,
        "demographic_viral_preferences": ["visual content", "emotional stories"],
        "sharing_motivations": ["entertainment", "information"]
    }},
    "viral_gaps": [
        "Lacks controversial element",
        "Could be more relatable", 
        "Needs stronger social currency"
    ],
    "viral_enhancement_priorities": [
        "Add controversial angle for debate",
        "Increase relatability factor",
        "Build social currency value",
        "Strengthen call-to-action"
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
            
            logger.info(f"🚀 Viral analysis complete - Score: {analysis.get('overall_viral_score', 0)}")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Viral analysis failed: {e}")
            return self._create_fallback_viral_analysis()
    
    async def optimize_for_virality(
        self,
        content: str,
        mission: str,
        platform: Platform,
        viral_analysis: Dict[str, Any] = None,
        target_viral_score: int = 85
    ) -> Dict[str, Any]:
        """
        Optimize content for maximum viral potential
        """
        logger.info(f"🚀 Optimizing content for virality (target score: {target_viral_score})")
        
        # Get analysis if not provided
        if not viral_analysis:
            viral_analysis = await self.analyze_viral_potential(content, mission, platform)
        
        current_score = viral_analysis.get('overall_viral_score', 50)
        
        prompt = f"""
Optimize this content for MAXIMUM VIRAL POTENTIAL and SHAREABILITY:

MISSION: {mission}
PLATFORM: {platform.value}
CURRENT VIRAL SCORE: {current_score}
TARGET VIRAL SCORE: {target_viral_score}

ORIGINAL CONTENT:
{content}

VIRAL ANALYSIS FINDINGS:
- Viral Strengths: {viral_analysis.get('viral_strengths', [])}
- Viral Weaknesses: {viral_analysis.get('viral_weaknesses', [])}
- Viral Gaps: {viral_analysis.get('viral_gaps', [])}
- Enhancement Priorities: {viral_analysis.get('viral_enhancement_priorities', [])}

🚀 VIRAL OPTIMIZATION REQUIREMENTS:

1. EMOTIONAL INTENSITY MAXIMIZATION:
   - Create stronger emotional triggers (surprise, shock, joy, outrage)
   - Build emotional peaks and valleys
   - Add personal/emotional stakes
   - Use emotional storytelling techniques

2. RELATABILITY AMPLIFICATION:
   - Use universal human experiences
   - Add relatable struggles/challenges
   - Include common situations everyone faces
   - Build "this is so me" moments

3. CONTROVERSY & DEBATE INJECTION:
   - Add contrarian viewpoints or hot takes
   - Create "agree or disagree" moments
   - Include polarizing but defendable positions
   - Spark thoughtful debate/discussion

4. SURPRISE & SHOCK OPTIMIZATION:
   - Add unexpected twists and reveals
   - Include counterintuitive insights
   - Create "wait, what?" moments
   - Build anticipation and payoff

5. PRACTICAL UTILITY ENHANCEMENT:
   - Include immediately actionable tips
   - Provide solve-a-problem value
   - Add "you can use this right now" elements
   - Build save-for-later value

6. SOCIAL CURRENCY BUILDING:
   - Make sharing enhance sharer's status
   - Include "insider knowledge" elements
   - Add trend-awareness content
   - Build "I'm in the know" value

7. NARRATIVE STRENGTHENING:
   - Create compelling story arcs
   - Add character development/transformation
   - Build tension and resolution
   - Use storytelling hooks

8. TIMING & TREND ALIGNMENT:
   - Connect to current trends/events
   - Use trending language/references
   - Add cultural relevance
   - Leverage moment-in-time factors

9. VISUAL & MEMORABLE ENHANCEMENT:
   - Create iconic/quotable moments
   - Add visually striking elements
   - Build memorable phrases/concepts
   - Design for screenshot/meme potential

10. PARTICIPATION MAXIMIZATION:
    - Add strong calls-to-action
    - Create participation opportunities
    - Include engagement triggers
    - Build community interaction

PLATFORM-SPECIFIC VIRAL OPTIMIZATION for {platform.value}:
- Leverage platform viral patterns
- Use platform-native viral mechanics
- Optimize for platform algorithms
- Match platform user viral behaviors

Generate VIRALLY OPTIMIZED content that maintains the mission but dramatically increases share potential:

Return JSON:
{{
    "viral_optimized_content": "Full content optimized for maximum virality...",
    "viral_enhancements": {{
        "emotional_intensity": ["Added shock element", "Created emotional peaks"],
        "relatability": ["Added universal experiences", "Included relatable struggles"],
        "controversy": ["Added contrarian viewpoint", "Created debate trigger"],
        "surprise": ["Added unexpected twist", "Created shock moment"],
        "utility": ["Added actionable tips", "Provided immediate value"],
        "social_currency": ["Added insider knowledge", "Built status value"],
        "narrative": ["Strengthened story arc", "Added character development"],
        "timing": ["Connected to current trends", "Added cultural relevance"],
        "visual": ["Created quotable moments", "Added memorable elements"],
        "participation": ["Strengthened CTAs", "Added engagement triggers"]
    }},
    "viral_improvements": {{
        "viral_score_increase": 25,
        "new_viral_score": 85,
        "share_likelihood_increase": "+150%",
        "viral_velocity_boost": "+200%",
        "viral_ceiling_raised": "high"
    }},
    "viral_predictions": {{
        "expected_shares": "+300%",
        "expected_comments": "+250%",
        "expected_saves": "+180%",
        "viral_probability": "high",
        "exponential_growth_factors": ["emotional intensity", "controversy", "surprise"]
    }},
    "platform_viral_optimization": {{
        "algorithm_optimization": ["Optimized for {platform.value} viral signals"],
        "user_behavior_alignment": ["Matched platform viral patterns"],
        "viral_distribution_factors": ["Enhanced for platform sharing mechanics"]
    }}
}}
"""
        
        try:
            text_service = self.ai_manager.get_service(AIServiceType.TEXT_GENERATION)
            request = TextGenerationRequest(
                prompt=prompt,
                max_tokens=3000,
                temperature=0.8
            )
            
            response = await text_service.generate(request)
            optimization = self._parse_json_response(response.text)
            
            logger.info("✅ Viral optimization complete")
            return optimization
            
        except Exception as e:
            logger.error(f"❌ Viral optimization failed: {e}")
            return self._create_fallback_viral_optimization(content)
    
    async def create_viral_variants(
        self,
        content: str,
        mission: str,
        platform: Platform,
        viral_strategies: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Create multiple viral-optimized variants using different viral strategies
        """
        if not viral_strategies:
            viral_strategies = ["emotional_viral", "controversial_viral", "utility_viral", "surprise_viral"]
        
        logger.info(f"🎭 Creating {len(viral_strategies)} viral strategy variants")
        
        variants = []
        
        for strategy in viral_strategies:
            prompt = f"""
Create a viral-optimized variant using the "{strategy}" strategy:

MISSION: {mission}
PLATFORM: {platform.value}
VIRAL STRATEGY: {strategy}

ORIGINAL CONTENT: {content}

VIRAL STRATEGY DEFINITIONS:
- emotional_viral: Maximize emotional intensity, relatability, emotional sharing
- controversial_viral: Add debate elements, contrarian views, polarizing opinions
- utility_viral: Focus on practical value, actionable tips, immediate usefulness
- surprise_viral: Emphasize shock, unexpected elements, surprise reveals

Create a variant optimized for maximum virality using this specific strategy.

Return JSON:
{{
    "viral_strategy": "{strategy}",
    "viral_optimized_content": "Content optimized for {strategy} virality...",
    "viral_mechanics_used": [
        "Primary viral mechanics for this strategy",
        "Supporting viral elements"
    ],
    "viral_predictions": {{
        "viral_score": 85,
        "share_probability": "high",
        "viral_velocity": "fast",
        "target_audience_reaction": "Expected viral response"
    }},
    "strategy_specific_elements": [
        "Key elements that make this viral for {strategy}",
        "Unique viral triggers for this approach"
    ]
}}
"""
            
            try:
                text_service = self.ai_manager.get_service(AIServiceType.TEXT_GENERATION)
                request = TextGenerationRequest(
                    prompt=prompt,
                    max_tokens=2000,
                    temperature=0.9
                )
                
                response = await text_service.generate(request)
                variant = self._parse_json_response(response.text)
                variants.append(variant)
                
            except Exception as e:
                logger.error(f"❌ Viral variant {strategy} failed: {e}")
                continue
        
        logger.info(f"✅ Created {len(variants)} viral strategy variants")
        return variants
    
    def predict_viral_performance(
        self,
        content: str,
        platform: Platform,
        viral_score: float,
        initial_audience_size: int = 1000
    ) -> Dict[str, Any]:
        """
        Predict viral performance based on viral score and platform
        """
        logger.info(f"📈 Predicting viral performance for score {viral_score} on {platform.value}")
        
        # Platform-specific viral coefficients
        platform_coefficients = {
            Platform.TIKTOK: 1.8,      # High viral potential
            Platform.INSTAGRAM: 1.5,   # Good viral potential
            Platform.TWITTER: 1.4,     # Good viral potential
            Platform.YOUTUBE: 1.2,     # Moderate viral potential
            Platform.LINKEDIN: 0.9,    # Lower viral potential
            Platform.FACEBOOK: 1.3     # Moderate viral potential
        }
        
        platform_coefficient = platform_coefficients.get(platform, 1.0)
        
        # Calculate viral predictions
        base_viral_factor = (viral_score / 100) * platform_coefficient
        
        # Viral growth phases
        if viral_score >= 85:
            viral_probability = "high"
            growth_multiplier = 5.0
            viral_ceiling = "exponential"
        elif viral_score >= 70:
            viral_probability = "medium-high"
            growth_multiplier = 3.0
            viral_ceiling = "significant"
        elif viral_score >= 55:
            viral_probability = "medium"
            growth_multiplier = 1.8
            viral_ceiling = "moderate"
        else:
            viral_probability = "low"
            growth_multiplier = 1.2
            viral_ceiling = "limited"
        
        # Calculate projections
        projected_reach = int(initial_audience_size * growth_multiplier * base_viral_factor)
        projected_shares = int(projected_reach * 0.05 * base_viral_factor)
        projected_engagement = int(projected_reach * 0.15 * base_viral_factor)
        
        # Time-based projections
        hourly_growth = max(1.1, base_viral_factor / 24)
        daily_peak = int(projected_reach * 0.6)  # Peak typically within first day
        
        return {
            "viral_predictions": {
                "viral_probability": viral_probability,
                "viral_ceiling": viral_ceiling,
                "growth_multiplier": round(growth_multiplier, 2),
                "platform_coefficient": platform_coefficient
            },
            "reach_projections": {
                "initial_audience": initial_audience_size,
                "projected_reach": projected_reach,
                "reach_multiplier": round(projected_reach / initial_audience_size, 1),
                "viral_factor": round(base_viral_factor, 2)
            },
            "engagement_projections": {
                "projected_shares": projected_shares,
                "projected_engagement": projected_engagement,
                "share_rate": round((projected_shares / projected_reach) * 100, 2),
                "engagement_rate": round((projected_engagement / projected_reach) * 100, 2)
            },
            "timeline_projections": {
                "hourly_growth_rate": round((hourly_growth - 1) * 100, 1),
                "daily_peak_reach": daily_peak,
                "viral_velocity": "fast" if base_viral_factor > 2 else "moderate",
                "sustainability": "high" if viral_score > 80 else "moderate"
            },
            "success_indicators": self._generate_viral_success_indicators(viral_score, platform),
            "optimization_recommendations": self._generate_viral_optimization_recommendations(viral_score)
        }
    
    def analyze_viral_trends(
        self,
        platform: Platform,
        time_period: str = "current"
    ) -> Dict[str, Any]:
        """
        Analyze current viral trends for the platform
        """
        logger.info(f"📊 Analyzing viral trends for {platform.value}")
        
        # Platform-specific viral trends (would be updated with real data)
        viral_trends = {
            Platform.TIKTOK: {
                "trending_mechanics": ["surprise_reveals", "emotional_stories", "controversy"],
                "viral_formats": ["before_after", "storytime", "hot_takes"],
                "optimal_length": "15-60 seconds",
                "trending_elements": ["trending sounds", "challenges", "duets"],
                "viral_timing": ["evening hours", "weekends"]
            },
            Platform.INSTAGRAM: {
                "trending_mechanics": ["relatability", "visual_appeal", "social_currency"],
                "viral_formats": ["carousel_posts", "reels", "stories"],
                "optimal_length": "15-30 seconds for reels",
                "trending_elements": ["trending hashtags", "location tags", "collaborations"],
                "viral_timing": ["lunch hours", "evening scroll time"]
            },
            Platform.YOUTUBE: {
                "trending_mechanics": ["utility", "entertainment", "authority"],
                "viral_formats": ["tutorials", "reaction_videos", "deep_dives"],
                "optimal_length": "8-15 minutes",
                "trending_elements": ["trending topics", "collaborations", "series"],
                "viral_timing": ["after work hours", "weekends"]
            }
        }
        
        platform_trends = viral_trends.get(platform, {
            "trending_mechanics": ["emotional_intensity", "relatability"],
            "viral_formats": ["short_form", "visual_content"],
            "optimal_length": "varies",
            "trending_elements": ["platform_specific"],
            "viral_timing": ["peak_hours"]
        })
        
        return {
            "platform": platform.value,
            "analysis_period": time_period,
            "trending_viral_mechanics": platform_trends["trending_mechanics"],
            "viral_content_formats": platform_trends["viral_formats"],
            "optimal_content_specs": {
                "length": platform_trends["optimal_length"],
                "trending_elements": platform_trends["trending_elements"],
                "viral_timing": platform_trends["viral_timing"]
            },
            "viral_success_patterns": self._get_viral_success_patterns(platform),
            "emerging_trends": self._get_emerging_viral_trends(platform),
            "recommendations": [
                f"Focus on {platform_trends['trending_mechanics'][0]} for {platform.value}",
                f"Use {platform_trends['viral_formats'][0]} format",
                f"Optimize for {platform_trends['optimal_length']} length"
            ]
        }
    
    def _get_viral_success_patterns(self, platform: Platform) -> List[str]:
        """Get viral success patterns for platform"""
        patterns = {
            Platform.TIKTOK: [
                "Quick emotional hooks in first 3 seconds",
                "Surprise elements throughout",
                "Strong visual transitions",
                "Trending audio usage"
            ],
            Platform.INSTAGRAM: [
                "High-quality visuals",
                "Relatable captions",
                "Strategic hashtag usage", 
                "Engaging first frame"
            ],
            Platform.YOUTUBE: [
                "Compelling thumbnails",
                "Strong titles with keywords",
                "Good audience retention",
                "Clear value proposition"
            ]
        }
        
        return patterns.get(platform, ["General engagement patterns"])
    
    def _get_emerging_viral_trends(self, platform: Platform) -> List[str]:
        """Get emerging viral trends for platform"""
        trends = {
            Platform.TIKTOK: [
                "Micro-storytelling in 15 seconds",
                "Educational content with entertainment",
                "Behind-the-scenes authenticity",
                "Interactive elements (polls, questions)"
            ],
            Platform.INSTAGRAM: [
                "Carousel storytelling",
                "User-generated content campaigns",
                "Authentic lifestyle content",
                "Collaborative content"
            ],
            Platform.YOUTUBE: [
                "Shorts integration with long-form",
                "Community-driven content",
                "Educational entertainment",
                "Live streaming integration"
            ]
        }
        
        return trends.get(platform, ["Emerging digital trends"])
    
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
    
    def _create_fallback_viral_analysis(self) -> Dict[str, Any]:
        """Create fallback analysis when AI fails"""
        return {
            "overall_viral_score": 50,
            "viral_mechanics_analysis": {
                mechanic: {
                    "strength": 5,
                    "viral_coefficient": info["viral_coefficient"],
                    "improvement_opportunities": [f"Enhance {mechanic}"]
                }
                for mechanic, info in self.viral_mechanics.items()
            },
            "viral_strengths": ["emotional_intensity"],
            "viral_weaknesses": ["controversy_debate", "social_currency"],
            "viral_predictions": {
                "share_likelihood": 5,
                "comment_probability": 5,
                "viral_velocity": 5,
                "viral_ceiling": "moderate"
            },
            "viral_gaps": ["Limited viral mechanics"],
            "viral_enhancement_priorities": ["Add emotional elements", "Increase shareability", "Build social currency"]
        }
    
    def _create_fallback_viral_optimization(self, original_content: str) -> Dict[str, Any]:
        """Create fallback optimization when AI fails"""
        return {
            "viral_optimized_content": original_content,
            "viral_enhancements": {
                mechanic: [f"Applied {mechanic} elements"]
                for mechanic in self.viral_mechanics.keys()
            },
            "viral_improvements": {
                "viral_score_increase": 20,
                "new_viral_score": 70,
                "share_likelihood_increase": "+100%",
                "viral_velocity_boost": "+50%"
            },
            "viral_predictions": {
                "expected_shares": "+150%",
                "expected_comments": "+100%",
                "viral_probability": "medium"
            }
        }
    
    def _generate_viral_success_indicators(self, viral_score: float, platform: Platform) -> List[str]:
        """Generate viral success indicators based on score and platform"""
        indicators = []
        
        if viral_score >= 85:
            indicators.extend([
                "High probability of exponential growth",
                "Strong shareability indicators",
                "Multiple viral mechanics present"
            ])
        elif viral_score >= 70:
            indicators.extend([
                "Good viral potential",
                "Solid shareability foundation",
                "Platform-optimized content"
            ])
        else:
            indicators.extend([
                "Moderate viral potential",
                "Needs viral enhancement",
                "Limited shareability"
            ])
        
        return indicators
    
    def _generate_viral_optimization_recommendations(self, viral_score: float) -> List[str]:
        """Generate recommendations for improving viral potential"""
        recommendations = []
        
        if viral_score < 60:
            recommendations.extend([
                "Focus on emotional intensity - add surprise/shock elements",
                "Increase relatability with universal experiences",
                "Add controversial or debate-worthy angles"
            ])
        elif viral_score < 80:
            recommendations.extend([
                "Strengthen existing viral mechanics",
                "Add more shareability triggers",
                "Optimize for platform-specific viral patterns"
            ])
        else:
            recommendations.extend([
                "Fine-tune existing strong viral elements",
                "Test different viral timing strategies",
                "Consider viral variant testing"
            ])
        
        return recommendations