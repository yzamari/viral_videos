"""
Frame Continuity Decision Agent
Analyzes video topics and makes intelligent decisions about frame continuity
"""

import google.generativeai as genai
from typing import Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ContinuityDecisionAgent:
    """
    AI Agent specialized in analyzing video content and deciding optimal
    frame continuity strategy
    """

    def __init__(self, api_key: str):
        """Initialize the Continuity Decision Agent"""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

        # Agent personality and expertise
        self.agent_profile = {
            'name': 'VisualFlow',
            'role': 'Frame Continuity Strategist',
            'expertise': [
                'Visual storytelling flow analysis',
                'Scene transition optimization',
                'Continuity vs. jump-cut effectiveness',
                'Platform-specific visual preferences',
                'Content type visual requirements'
            ],
            'decision_factors': [
                'Story narrative flow',
                'Content complexity',
                'Platform requirements',
                'Target audience preferences',
                'Visual style coherence'
            ]
        }

    def analyze_frame_continuity_need(self,
                                      topic: str,
                                      category: str,
                                      platform: str,
                                      duration: int,
                                      style: str = "viral") -> Dict[str, Any]:
        """
        Analyze whether frame continuity would enhance the video

        Args:
            topic: Video topic/content
            category: Video category (Comedy, Educational, etc.)
            platform: Target platform (youtube, tiktok, etc.)
            duration: Video duration in seconds
            style: Video style preference

        Returns:
            Dictionary with continuity decision and reasoning
        """

        logger.info(
            f"🎬 VisualFlow Agent analyzing frame continuity for: {topic}"
        )

        try:
            # Create comprehensive analysis prompt
            analysis_prompt = f"""
You are VisualFlow, an expert AI agent specializing in frame continuity and
visual storytelling flow.

ANALYZE THIS VIDEO CONTENT:
- Topic: {topic}
- Category: {category}
- Platform: {platform}
- Duration: {duration} seconds
- Style: {style}

FRAME CONTINUITY DECISION FACTORS:

1. STORY FLOW ANALYSIS:
   - Does this topic benefit from seamless visual transitions?
   - Would jump cuts be more effective for pacing?
   - Is there a narrative that flows between scenes?

2. CONTENT TYPE ANALYSIS:
   - Educational content: Often benefits from continuity
   - Comedy: May benefit from jump cuts for timing
   - News/Facts: Mixed approach works well
   - Entertainment: Depends on narrative structure

3. PLATFORM OPTIMIZATION:
   - TikTok: Fast cuts often preferred
   - YouTube: Longer form allows more continuity
   - Instagram: Visual consistency important
   - Twitter: Quick, punchy cuts work well

4. DURATION CONSIDERATIONS:
   - Short videos (5-15s): Jump cuts for impact
   - Medium videos (15-30s): Mixed approach
   - Longer videos (30s+): Continuity enhances flow

5. ENGAGEMENT FACTORS:
   - Would continuity help maintain attention?
   - Do jump cuts create better hooks?
   - What creates more viral potential?

PROVIDE YOUR DECISION:
1. Use frame continuity: true/false
2. Confidence level: 0.1-1.0
3. Primary reason (one sentence)
4. Alternative approach suggestion
5. Expected impact on engagement

Respond in JSON format:
{{
    "use_frame_continuity": boolean,
    "confidence": float,
    "primary_reason": "string",
    "alternative_approach": "string",
    "engagement_impact": "string",
    "decision_factors": ["factor1", "factor2", "factor3"],
    "platform_optimization": "string",
    "visual_style_recommendation": "string"
}}
"""

            # Get AI analysis
            response = self.model.generate_content(analysis_prompt)

            # Parse response
            import json
            try:
                # Extract JSON from response
                response_text = response.text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:-3]
                elif response_text.startswith('```'):
                    response_text = response_text[3:-3]

                decision_data = json.loads(response_text)

                # Add metadata
                decision_data.update({
                    'agent_name': 'VisualFlow',
                    'analysis_timestamp': datetime.now().isoformat(),
                    'input_parameters': {
                        'topic': topic,
                        'category': category,
                        'platform': platform,
                        'duration': duration,
                        'style': style
                    }
                })

                # Log decision
                continuity_status = (
                    "✅ ENABLED" if decision_data['use_frame_continuity']
                    else "❌ DISABLED"
                )
                logger.info(
                    f"🎬 VisualFlow Decision: Frame Continuity "
                    f"{continuity_status}"
                )
                logger.info(
                    f"   Confidence: {decision_data['confidence']:.2f}"
                )
                logger.info(
                    f"   Reason: {decision_data['primary_reason']}"
                )

                return decision_data

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse VisualFlow response: {e}")
                # Fallback decision based on heuristics
                return self._make_fallback_decision(
                    topic, category, platform, duration
                )

        except Exception as e:
            logger.error(f"VisualFlow analysis failed: {e}")
            return self._make_fallback_decision(
                topic, category, platform, duration
            )

    def _make_fallback_decision(
        self, topic: str, category: str, platform: str, duration: int
    ) -> Dict[str, Any]:
        """
        Make a fallback decision using heuristics when AI analysis fails
        """

        logger.info(
            "🔄 Using fallback heuristics for frame continuity decision"
        )

        # Heuristic decision logic
        use_continuity = True
        confidence = 0.6
        reason = "Default continuity enabled"

        # Platform-based adjustments
        if platform.lower() == 'tiktok':
            if duration <= 15:
                use_continuity = False
                reason = "TikTok short videos benefit from jump cuts"
                confidence = 0.8

        # Category-based adjustments
        if category.lower() == 'comedy':
            if duration <= 20:
                use_continuity = False
                reason = "Comedy timing benefits from jump cuts"
                confidence = 0.7
        elif category.lower() == 'educational':
            use_continuity = True
            reason = "Educational content benefits from visual flow"
            confidence = 0.8

        # Duration-based adjustments
        if duration <= 10:
            use_continuity = False
            reason = "Very short videos work better with jump cuts"
            confidence = 0.9
        elif duration >= 45:
            use_continuity = True
            reason = "Longer videos benefit from continuity"
            confidence = 0.8

        return {
            'use_frame_continuity': use_continuity,
            'confidence': confidence,
            'primary_reason': reason,
            'alternative_approach': (
                "Could try opposite approach for A/B testing"
            ),
            'engagement_impact': "Moderate impact expected",
            'decision_factors': [
                'platform_optimization',
                'duration_analysis',
                'category_matching'
            ],
            'platform_optimization': f"Optimized for {platform}",
            'visual_style_recommendation': (
                "Standard viral style with optimized continuity"
            ),
            'agent_name': 'VisualFlow (Fallback)',
            'analysis_timestamp': datetime.now().isoformat(),
            'input_parameters': {
                'topic': topic,
                'category': category,
                'platform': platform,
                'duration': duration,
                'style': 'viral'
            }
        }

    def get_agent_summary(self) -> Dict[str, Any]:
        """Get summary of this agent's capabilities"""
        return {
            'agent_name': self.agent_profile['name'],
            'role': self.agent_profile['role'],
            'expertise': self.agent_profile['expertise'],
            'decision_factors': self.agent_profile['decision_factors'],
            'primary_function': (
                'Analyze video content and decide optimal frame '
                'continuity strategy'
            )
        }
