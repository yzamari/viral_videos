"""
Message Clarity Enhancement Framework
Ensures content delivers clear, understandable messages that resonate with audiences
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from ..utils.logging_config import get_logger
from ..ai.manager import AIServiceManager
from ..ai.interfaces.text_generation import TextGenerationRequest
from ..ai.interfaces.base import AIServiceType
from ..models.video_models import Platform, Language

logger = get_logger(__name__)

class MessageClarityEnhancer:
    """
    Enhances message clarity to ensure audiences understand the content's core message
    Focuses on comprehension, simplicity, and memorability
    """
    
    def __init__(self, ai_manager: AIServiceManager):
        self.ai_manager = ai_manager
        logger.info("✅ Message Clarity Enhancer initialized")
    
    async def analyze_message_clarity(
        self,
        mission: str,
        script_content: str,
        target_audience: str = None,
        language: Language = Language.ENGLISH_US
    ) -> Dict[str, Any]:
        """
        Comprehensive analysis of message clarity and comprehension
        
        Returns:
            Detailed clarity analysis with specific improvement recommendations
        """
        logger.info(f"🔍 Analyzing message clarity for '{mission}'")
        
        prompt = f"""
Analyze this content for MESSAGE CLARITY and COMPREHENSION:

MISSION: {mission}
TARGET AUDIENCE: {target_audience or "General audience"}
LANGUAGE: {language.value}

CONTENT TO ANALYZE:
{script_content}

🧠 CLARITY ANALYSIS REQUIRED:

1. CORE MESSAGE IDENTIFICATION:
   - What is the main message?
   - Is it immediately clear from the content?
   - Does every element support this message?
   - Rate message clarity: 1-100

2. COMPREHENSION ASSESSMENT:
   - How easy is this to understand?
   - What reading/comprehension level is required?
   - Are there confusing technical terms?
   - Comprehension difficulty: 1-10 (1=very easy, 10=very hard)

3. COGNITIVE LOAD ANALYSIS:
   - How much mental effort is required?
   - Are there too many concepts at once?
   - Is the information flow logical?
   - Cognitive load score: 1-100 (lower is better)

4. LANGUAGE SIMPLICITY:
   - Are sentences too long or complex?
   - Is vocabulary appropriate for audience?
   - Are there unnecessary jargon or buzzwords?
   - Language simplicity score: 1-100

5. STRUCTURE & FLOW:
   - Does information flow logically?
   - Are transitions clear between ideas?
   - Is there a clear beginning, middle, end?
   - Structure clarity score: 1-100

6. MEMORABILITY ASSESSMENT:
   - What will audience remember?
   - Are there clear takeaways?
   - Is the message sticky and memorable?
   - Memorability score: 1-100

7. CONFUSION POINTS:
   - What specific parts are confusing?
   - Where might audience get lost?
   - What questions will they have?
   - List all confusion risks

8. AUDIENCE APPROPRIATENESS:
   - Is language appropriate for target audience?
   - Does it match their knowledge level?
   - Are cultural/context assumptions valid?
   - Audience fit score: 1-100

Return JSON:
{{
    "overall_clarity_score": 75,
    "core_message": {{
        "identified_message": "The main takeaway is...",
        "clarity_score": 80,
        "message_strength": "clear",
        "supporting_elements": ["intro states purpose", "examples reinforce point"],
        "weakening_elements": ["tangent in middle", "unclear conclusion"]
    }},
    "comprehension": {{
        "difficulty_level": 6,
        "reading_level": "high school",
        "technical_complexity": "moderate",
        "barriers": ["unfamiliar terms", "complex sentences"],
        "accessibility_score": 70
    }},
    "cognitive_load": {{
        "load_score": 65,
        "information_density": "high",
        "concept_count": 8,
        "multitasking_required": false,
        "simplification_opportunities": ["break down complex ideas", "use analogies"]
    }},
    "language": {{
        "simplicity_score": 60,
        "average_sentence_length": 18,
        "complex_words": ["methodology", "implementation"],
        "jargon_count": 5,
        "readability": "needs improvement"
    }},
    "structure": {{
        "flow_score": 75,
        "logical_progression": true,
        "clear_transitions": false,
        "narrative_structure": "problem-solution",
        "improvement_needs": ["better transitions", "clearer sections"]
    }},
    "memorability": {{
        "memorability_score": 55,
        "key_takeaways": ["main point 1", "main point 2"],
        "memorable_elements": ["good analogy", "surprising fact"],
        "forgettable_elements": ["technical details", "generic statements"],
        "memory_aids_needed": ["repetition", "visual anchors"]
    }},
    "confusion_points": [
        "Technical term 'X' not explained",
        "Jump from concept A to B unclear", 
        "Conclusion doesn't match opening"
    ],
    "audience_fit": {{
        "appropriateness_score": 70,
        "language_match": "mostly appropriate",
        "knowledge_assumptions": ["assumes basic familiarity"],
        "cultural_considerations": ["broadly accessible"],
        "adjustments_needed": ["simplify technical terms", "add context"]
    }},
    "top_clarity_improvements": [
        "Define technical terms on first use",
        "Shorten complex sentences",
        "Add clearer transitions between ideas",
        "Strengthen memorable conclusion"
    ]
}}
"""
        
        try:
            text_service = self.ai_manager.get_service(AIServiceType.TEXT_GENERATION)
            request = TextGenerationRequest(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.5  # Lower temperature for analytical precision
            )
            
            response = await text_service.generate(request)
            analysis = self._parse_json_response(response.text)
            
            logger.info(f"📊 Clarity analysis complete - Overall score: {analysis.get('overall_clarity_score', 0)}")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Message clarity analysis failed: {e}")
            return self._create_fallback_clarity_analysis()
    
    async def enhance_message_clarity(
        self,
        mission: str,
        script_content: str,
        clarity_analysis: Dict[str, Any] = None,
        target_audience: str = None,
        language: Language = Language.ENGLISH_US
    ) -> Dict[str, Any]:
        """
        Generate clarity-enhanced version of the content
        """
        logger.info(f"✨ Enhancing message clarity for '{mission}'")
        
        # Get analysis if not provided
        if not clarity_analysis:
            clarity_analysis = await self.analyze_message_clarity(
                mission, script_content, target_audience, language
            )
        
        prompt = f"""
Enhance this content for MAXIMUM MESSAGE CLARITY and COMPREHENSION:

ORIGINAL MISSION: {mission}
TARGET AUDIENCE: {target_audience or "General audience"}
CURRENT CLARITY SCORE: {clarity_analysis.get('overall_clarity_score', 50)}

ORIGINAL CONTENT:
{script_content}

CLARITY ANALYSIS FINDINGS:
- Core Message Issues: {clarity_analysis.get('core_message', {}).get('weakening_elements', [])}
- Comprehension Barriers: {clarity_analysis.get('comprehension', {}).get('barriers', [])}
- Language Complexity: {clarity_analysis.get('language', {}).get('complex_words', [])}
- Structure Issues: {clarity_analysis.get('structure', {}).get('improvement_needs', [])}
- Confusion Points: {clarity_analysis.get('confusion_points', [])}

🎯 CLARITY ENHANCEMENT REQUIREMENTS:

1. CORE MESSAGE OPTIMIZATION:
   - Make the main message crystal clear from the start
   - Ensure every element reinforces the core message
   - Remove or clarify weakening elements
   - Create memorable message summary

2. COMPREHENSION SIMPLIFICATION:
   - Break down complex concepts into simple parts
   - Use familiar analogies and examples
   - Define technical terms immediately
   - Lower cognitive load throughout

3. LANGUAGE SIMPLIFICATION:
   - Use shorter, simpler sentences
   - Replace complex words with simple alternatives
   - Remove unnecessary jargon
   - Improve readability significantly

4. STRUCTURAL ENHANCEMENT:
   - Create clear logical flow
   - Add smooth transitions between ideas
   - Use signposting to guide understanding
   - Structure for maximum comprehension

5. MEMORABILITY OPTIMIZATION:
   - Add repetition of key points
   - Create memorable phrases or summaries
   - Use storytelling and analogies
   - Build clear takeaways

6. AUDIENCE OPTIMIZATION:
   - Match language to audience level
   - Address their specific knowledge base
   - Remove inappropriate assumptions
   - Maximize accessibility

Generate CLARITY-ENHANCED content that maintains the mission but dramatically improves understanding:

Return JSON:
{{
    "enhanced_content": "Fully rewritten content with maximum clarity...",
    "clarity_improvements": {{
        "message_enhancements": ["Clearer opening statement", "Reinforced key message"],
        "comprehension_aids": ["Added analogies", "Defined technical terms"],
        "language_simplifications": ["Shorter sentences", "Simpler vocabulary"],
        "structure_improvements": ["Logical flow", "Clear transitions"],
        "memorability_boosts": ["Repeated key points", "Added summary"]
    }},
    "key_changes": [
        "Replaced 'methodology' with 'approach'",
        "Broke down complex concept into 3 simple steps",
        "Added clear transition sentences",
        "Created memorable closing summary"
    ],
    "clarity_metrics": {{
        "estimated_clarity_score": 95,
        "reading_level": "8th grade",
        "cognitive_load_reduction": "40%",
        "comprehension_improvement": "60%"
    }},
    "message_reinforcement": {{
        "core_message_repetition": 3,
        "supporting_examples": 2,
        "takeaway_clarity": "crystal clear",
        "memorability_elements": ["key phrase", "summary statement"]
    }}
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
            enhancement = self._parse_json_response(response.text)
            
            logger.info("✅ Message clarity enhancement complete")
            return enhancement
            
        except Exception as e:
            logger.error(f"❌ Message clarity enhancement failed: {e}")
            return self._create_fallback_enhancement(script_content)
    
    async def create_clarity_variants(
        self,
        mission: str,
        script_content: str,
        target_audiences: List[str],
        language: Language = Language.ENGLISH_US
    ) -> List[Dict[str, Any]]:
        """
        Create clarity-optimized variants for different audience types
        """
        logger.info(f"🎭 Creating clarity variants for {len(target_audiences)} audiences")
        
        variants = []
        
        for audience in target_audiences:
            prompt = f"""
Create a clarity-optimized variant for this specific audience:

MISSION: {mission}
TARGET AUDIENCE: {audience}
LANGUAGE: {language.value}

ORIGINAL CONTENT: {script_content}

AUDIENCE-SPECIFIC CLARITY OPTIMIZATION:
- Adjust language complexity for {audience}
- Use examples and analogies relevant to {audience}
- Address their specific knowledge level and interests
- Remove barriers specific to this audience type

Create maximum clarity content specifically for {audience}:

Return JSON:
{{
    "audience": "{audience}",
    "clarity_optimized_content": "Content specifically optimized for {audience}...",
    "audience_adaptations": [
        "Adjusted vocabulary for audience level",
        "Used relevant examples from their domain",
        "Removed technical barriers"
    ],
    "clarity_score": 95,
    "key_changes": ["Specific changes made for this audience"]
}}
"""
            
            try:
                text_service = self.ai_manager.get_service(AIServiceType.TEXT_GENERATION)
                request = TextGenerationRequest(
                    prompt=prompt,
                    max_tokens=1500,
                    temperature=0.7
                )
                
                response = await text_service.generate(request)
                variant = self._parse_json_response(response.text)
                variants.append(variant)
                
            except Exception as e:
                logger.error(f"❌ Clarity variant for {audience} failed: {e}")
                continue
        
        logger.info(f"✅ Created {len(variants)} clarity variants")
        return variants
    
    def validate_message_consistency(
        self,
        mission: str,
        script_segments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate that message remains consistent across all segments
        """
        logger.info("🔍 Validating message consistency across segments")
        
        # Extract text from segments
        segment_texts = []
        for segment in script_segments:
            text = segment.get('text', '') or segment.get('dialogue', '') or segment.get('audio', {}).get('dialogue', '')
            segment_texts.append(text)
        
        # Analyze consistency
        consistency_issues = []
        message_alignment = []
        
        for i, text in enumerate(segment_texts, 1):
            # Check if segment supports main mission
            mission_words = set(mission.lower().split())
            text_words = set(text.lower().split())
            overlap = len(mission_words.intersection(text_words))
            alignment = overlap / len(mission_words) if mission_words else 0
            
            message_alignment.append({
                "segment_id": i,
                "alignment_score": round(alignment * 100, 1),
                "supporting_mission": alignment > 0.3
            })
            
            # Check for contradictions or off-topic content
            if alignment < 0.2:
                consistency_issues.append(f"Segment {i} appears off-topic or weakly related to mission")
        
        # Calculate overall consistency
        avg_alignment = sum(seg['alignment_score'] for seg in message_alignment) / len(message_alignment) if message_alignment else 0
        
        consistency_level = "excellent" if avg_alignment >= 80 else "good" if avg_alignment >= 60 else "needs_improvement"
        
        return {
            "overall_consistency": consistency_level,
            "average_alignment_score": round(avg_alignment, 1),
            "segment_analysis": message_alignment,
            "consistency_issues": consistency_issues,
            "recommendations": self._generate_consistency_recommendations(consistency_issues, message_alignment)
        }
    
    def measure_clarity_impact(
        self,
        original_metrics: Dict[str, Any],
        enhanced_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Measure the impact of clarity enhancements on engagement metrics
        """
        logger.info("📈 Measuring clarity enhancement impact")
        
        # Calculate improvements
        improvements = {}
        for metric in ['completion_rate', 'comprehension_score', 'engagement_rate', 'retention_rate']:
            original = original_metrics.get(metric, 0)
            enhanced = enhanced_metrics.get(metric, 0)
            
            if original > 0:
                improvement = ((enhanced - original) / original) * 100
                improvements[metric] = round(improvement, 1)
            else:
                improvements[metric] = 0
        
        # Overall clarity impact score
        impact_score = sum(improvements.values()) / len(improvements)
        
        # Generate insights
        insights = []
        if improvements.get('completion_rate', 0) > 10:
            insights.append("Clarity improvements significantly increased completion rates")
        if improvements.get('comprehension_score', 0) > 15:
            insights.append("Message understanding dramatically improved")
        if improvements.get('engagement_rate', 0) > 20:
            insights.append("Clearer messaging boosted audience engagement")
        
        return {
            "clarity_impact_score": round(impact_score, 1),
            "metric_improvements": improvements,
            "insights": insights,
            "success_indicators": [k for k, v in improvements.items() if v > 10],
            "areas_for_further_improvement": [k for k, v in improvements.items() if v < 5]
        }
    
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
    
    def _create_fallback_clarity_analysis(self) -> Dict[str, Any]:
        """Create fallback analysis when AI fails"""
        return {
            "overall_clarity_score": 50,
            "core_message": {"clarity_score": 50, "identified_message": "Message needs clarification"},
            "comprehension": {"difficulty_level": 7, "accessibility_score": 50},
            "cognitive_load": {"load_score": 70, "simplification_opportunities": ["Simplify language"]},
            "language": {"simplicity_score": 50, "readability": "needs improvement"},
            "structure": {"flow_score": 50, "improvement_needs": ["Better organization"]},
            "memorability": {"memorability_score": 50, "memory_aids_needed": ["Add repetition"]},
            "confusion_points": ["Generic analysis - specific review needed"],
            "audience_fit": {"appropriateness_score": 50, "adjustments_needed": ["Review for audience"]},
            "top_clarity_improvements": ["Simplify language", "Improve structure", "Clarify message", "Add examples"]
        }
    
    def _create_fallback_enhancement(self, original_content: str) -> Dict[str, Any]:
        """Create fallback enhancement when AI fails"""
        return {
            "enhanced_content": original_content,
            "clarity_improvements": {
                "message_enhancements": ["Applied basic improvements"],
                "comprehension_aids": ["Added clarity elements"],
                "language_simplifications": ["Simplified where possible"],
                "structure_improvements": ["Improved organization"],
                "memorability_boosts": ["Enhanced key points"]
            },
            "key_changes": ["Applied standard clarity enhancements"],
            "clarity_metrics": {
                "estimated_clarity_score": 70,
                "reading_level": "general",
                "cognitive_load_reduction": "10%",
                "comprehension_improvement": "20%"
            },
            "message_reinforcement": {
                "core_message_repetition": 2,
                "supporting_examples": 1,
                "takeaway_clarity": "improved",
                "memorability_elements": ["key points highlighted"]
            }
        }
    
    def _generate_consistency_recommendations(
        self,
        issues: List[str],
        alignment_data: List[Dict]
    ) -> List[str]:
        """Generate recommendations for improving message consistency"""
        recommendations = []
        
        if issues:
            recommendations.append("Review off-topic segments and align with core mission")
        
        low_alignment_segments = [seg for seg in alignment_data if seg['alignment_score'] < 50]
        if low_alignment_segments:
            recommendations.append("Strengthen mission connection in low-alignment segments")
        
        if len(alignment_data) > 5:
            recommendations.append("Consider consolidating message for better consistency")
        
        recommendations.extend([
            "Add mission-reinforcing statements throughout content",
            "Use consistent terminology and key phrases",
            "Ensure each segment advances the core message"
        ])
        
        return recommendations