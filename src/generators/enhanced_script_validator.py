"""
Enhanced Script Validator - Validates script quality for narrative coherence and engagement
Ensures professional-grade storytelling with proper pacing and emotional arcs
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from ..utils.logging_config import get_logger
from ..config import video_config

logger = get_logger(__name__)


class NarrativeArc(Enum):
    """Standard narrative arc types"""
    FREYTAG = "freytag"  # Exposition -> Rising Action -> Climax -> Falling Action -> Resolution
    THREE_ACT = "three_act"  # Setup -> Confrontation -> Resolution
    HERO_JOURNEY = "hero_journey"  # Call to Adventure -> Trials -> Return
    PROBLEM_SOLUTION = "problem_solution"  # Problem -> Analysis -> Solution
    VIRAL_HOOK = "viral_hook"  # Hook -> Build -> Payoff -> CTA


class EmotionalTone(Enum):
    """Emotional tones for content"""
    EXCITEMENT = "excitement"
    CURIOSITY = "curiosity"
    SURPRISE = "surprise"
    HUMOR = "humor"
    INSPIRATION = "inspiration"
    URGENCY = "urgency"
    EMPATHY = "empathy"
    FEAR = "fear"  # FOMO


@dataclass
class ScriptQualityMetrics:
    """Comprehensive script quality metrics"""
    overall_score: float
    narrative_score: float
    pacing_score: float
    engagement_score: float
    emotional_score: float
    clarity_score: float
    cta_strength: float
    hook_effectiveness: float
    issues: List[str]
    suggestions: List[str]
    narrative_arc: NarrativeArc
    emotional_journey: List[EmotionalTone]
    key_moments: Dict[str, float]  # moment_name -> timestamp


class ScriptQualityValidator:
    """Validates and enhances script quality for professional video production"""
    
    def __init__(self):
        """Initialize the script validator with quality thresholds"""
        self.min_quality_score = 0.7  # Minimum acceptable quality
        self.hook_word_limit = 15  # First sentence should be under 15 words
        self.optimal_wpm = 150  # Words per minute for clear speech
        
        # Engagement triggers (viral elements)
        self.engagement_triggers = [
            "you won't believe", "secret", "revealed", "shocking", "amazing",
            "unbelievable", "mind-blowing", "game-changer", "breakthrough",
            "exclusive", "limited time", "proven", "guaranteed", "transform"
        ]
        
        # Power words for emotional impact
        self.power_words = {
            EmotionalTone.EXCITEMENT: ["incredible", "amazing", "thrilling", "spectacular"],
            EmotionalTone.CURIOSITY: ["discover", "uncover", "reveal", "mystery"],
            EmotionalTone.SURPRISE: ["shocking", "unexpected", "stunning", "astonishing"],
            EmotionalTone.HUMOR: ["hilarious", "funny", "laugh", "ridiculous"],
            EmotionalTone.INSPIRATION: ["inspire", "motivate", "achieve", "success"],
            EmotionalTone.URGENCY: ["now", "today", "limited", "hurry", "last chance"],
            EmotionalTone.EMPATHY: ["understand", "feel", "relate", "together"],
            EmotionalTone.FEAR: ["miss out", "lose", "risk", "danger", "warning"]
        }
        
        logger.info("✅ Script Quality Validator initialized")
    
    def validate_script_quality(self, script: str, config: Any) -> ScriptQualityMetrics:
        """
        Comprehensive script quality validation
        
        Args:
            script: The script text to validate
            config: Video configuration with target duration, platform, etc.
            
        Returns:
            ScriptQualityMetrics with detailed analysis
        """
        logger.info("🔍 Validating script quality...")
        
        # Analyze different aspects
        narrative_analysis = self._check_narrative_arc(script)
        pacing_analysis = self._analyze_pacing(script, config.duration_seconds)
        engagement_analysis = self._analyze_engagement(script)
        emotional_analysis = self._map_emotional_arc(script)
        clarity_analysis = self._check_clarity(script)
        hook_analysis = self._analyze_hook(script)
        cta_analysis = self._evaluate_cta(script)
        
        # Identify key moments
        key_moments = self._identify_key_moments(script, config.duration_seconds)
        
        # Compile issues and suggestions
        issues = []
        suggestions = []
        
        # Check narrative issues
        if narrative_analysis['score'] < 0.6:
            issues.append("Weak narrative structure - lacks clear progression")
            suggestions.append("Add clear beginning, middle, and end sections")
        
        # Check pacing issues
        if pacing_analysis['wpm'] > 180:
            issues.append(f"Script too fast ({pacing_analysis['wpm']} WPM) - may be hard to follow")
            suggestions.append("Reduce content or increase video duration")
        elif pacing_analysis['wpm'] < 120:
            issues.append(f"Script too slow ({pacing_analysis['wpm']} WPM) - may lose engagement")
            suggestions.append("Add more content or reduce video duration")
        
        # Check hook effectiveness
        if hook_analysis['score'] < 0.7:
            issues.append("Weak opening hook - may not capture attention")
            suggestions.append("Start with a question, surprising fact, or bold statement")
        
        # Check CTA strength
        if cta_analysis['score'] < 0.6:
            issues.append("Weak or missing call-to-action")
            suggestions.append("Add clear, specific action for viewers to take")
        
        # Calculate overall score
        overall_score = (
            narrative_analysis['score'] * 0.2 +
            pacing_analysis['score'] * 0.15 +
            engagement_analysis['score'] * 0.25 +
            emotional_analysis['score'] * 0.15 +
            clarity_analysis['score'] * 0.1 +
            hook_analysis['score'] * 0.1 +
            cta_analysis['score'] * 0.05
        )
        
        metrics = ScriptQualityMetrics(
            overall_score=overall_score,
            narrative_score=narrative_analysis['score'],
            pacing_score=pacing_analysis['score'],
            engagement_score=engagement_analysis['score'],
            emotional_score=emotional_analysis['score'],
            clarity_score=clarity_analysis['score'],
            cta_strength=cta_analysis['score'],
            hook_effectiveness=hook_analysis['score'],
            issues=issues,
            suggestions=suggestions,
            narrative_arc=narrative_analysis['arc_type'],
            emotional_journey=emotional_analysis['journey'],
            key_moments=key_moments
        )
        
        # Log summary
        logger.info(f"📊 Script Quality Score: {overall_score:.2f}/1.0")
        if issues:
            logger.warning(f"⚠️ Issues found: {', '.join(issues[:2])}")
        if suggestions:
            logger.info(f"💡 Suggestions: {suggestions[0]}")
        
        return metrics
    
    def _check_narrative_arc(self, script: str) -> Dict[str, Any]:
        """Analyze narrative structure and arc"""
        sentences = self._split_into_sentences(script)
        total_sentences = len(sentences)
        
        if total_sentences < 3:
            return {'score': 0.3, 'arc_type': NarrativeArc.VIRAL_HOOK}
        
        # Divide script into sections
        first_third = sentences[:total_sentences//3]
        middle_third = sentences[total_sentences//3:2*total_sentences//3]
        last_third = sentences[2*total_sentences//3:]
        
        # Check for narrative elements
        has_setup = any(word in ' '.join(first_third).lower() 
                       for word in ['today', 'discover', 'learn', 'imagine', 'what if'])
        has_development = any(word in ' '.join(middle_third).lower() 
                            for word in ['because', 'however', 'but', 'therefore', 'this means'])
        has_conclusion = any(word in ' '.join(last_third).lower() 
                           for word in ['finally', 'now', 'so', 'remember', 'don\'t forget'])
        
        # Detect arc type
        if has_setup and has_development and has_conclusion:
            arc_type = NarrativeArc.THREE_ACT
            score = 0.9
        elif any(word in script.lower() for word in ['problem', 'solution', 'solve', 'fix']):
            arc_type = NarrativeArc.PROBLEM_SOLUTION
            score = 0.8
        elif any(word in script.lower() for word in ['shocking', 'revealed', 'secret']):
            arc_type = NarrativeArc.VIRAL_HOOK
            score = 0.85
        else:
            arc_type = NarrativeArc.VIRAL_HOOK
            score = 0.6
        
        return {
            'score': score,
            'arc_type': arc_type,
            'has_setup': has_setup,
            'has_development': has_development,
            'has_conclusion': has_conclusion
        }
    
    def _analyze_pacing(self, script: str, duration_seconds: float) -> Dict[str, Any]:
        """Analyze script pacing and timing"""
        word_count = len(script.split())
        duration_minutes = duration_seconds / 60
        wpm = word_count / duration_minutes if duration_minutes > 0 else 0
        
        # Score based on optimal WPM
        if 140 <= wpm <= 160:
            score = 1.0
        elif 120 <= wpm < 140 or 160 < wpm <= 180:
            score = 0.8
        elif 100 <= wpm < 120 or 180 < wpm <= 200:
            score = 0.6
        else:
            score = 0.4
        
        # Check for pacing variation
        sentences = self._split_into_sentences(script)
        sentence_lengths = [len(s.split()) for s in sentences]
        
        # Good pacing has varied sentence lengths
        if sentence_lengths:
            length_variance = max(sentence_lengths) - min(sentence_lengths)
            if length_variance > 10:
                score = min(1.0, score + 0.1)
        
        return {
            'score': score,
            'wpm': round(wpm),
            'word_count': word_count,
            'optimal_word_count': int(self.optimal_wpm * duration_minutes),
            'sentence_variety': length_variance if sentence_lengths else 0
        }
    
    def _analyze_engagement(self, script: str) -> Dict[str, Any]:
        """Analyze engagement factors in the script"""
        script_lower = script.lower()
        
        # Check for engagement triggers
        trigger_count = sum(1 for trigger in self.engagement_triggers 
                          if trigger in script_lower)
        
        # Check for questions (engage viewer)
        question_count = script.count('?')
        
        # Check for direct address (you, your)
        direct_address = script_lower.count('you') + script_lower.count('your')
        
        # Check for action words
        action_words = ['click', 'watch', 'subscribe', 'follow', 'share', 'comment', 'try', 'get']
        action_count = sum(1 for word in action_words if word in script_lower)
        
        # Calculate engagement score
        score = min(1.0, 
                   (trigger_count * 0.15 + 
                    question_count * 0.1 + 
                    min(direct_address, 10) * 0.05 + 
                    action_count * 0.1))
        
        return {
            'score': score,
            'trigger_count': trigger_count,
            'question_count': question_count,
            'direct_address_count': direct_address,
            'action_words': action_count
        }
    
    def _map_emotional_arc(self, script: str) -> Dict[str, Any]:
        """Map the emotional journey throughout the script"""
        sentences = self._split_into_sentences(script)
        emotional_journey = []
        total_emotional_words = 0
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            sentence_emotions = []
            
            for tone, words in self.power_words.items():
                if any(word in sentence_lower for word in words):
                    sentence_emotions.append(tone)
                    total_emotional_words += 1
            
            if sentence_emotions:
                # Take the dominant emotion for this sentence
                emotional_journey.append(sentence_emotions[0])
        
        # Calculate emotional score based on presence and variety
        emotion_variety = len(set(emotional_journey))
        score = min(1.0, (total_emotional_words * 0.1 + emotion_variety * 0.15))
        
        return {
            'score': score,
            'journey': emotional_journey,
            'variety': emotion_variety,
            'emotional_density': total_emotional_words / len(sentences) if sentences else 0
        }
    
    def _check_clarity(self, script: str) -> Dict[str, Any]:
        """Check script clarity and readability"""
        sentences = self._split_into_sentences(script)
        
        if not sentences:
            return {'score': 0, 'issues': ['Empty script']}
        
        issues = []
        
        # Check average sentence length
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        if avg_sentence_length > 20:
            issues.append("Sentences too long")
        
        # Check for complex words (approximation)
        complex_word_count = sum(1 for word in script.split() 
                                if len(word) > 10)
        if complex_word_count > len(script.split()) * 0.1:
            issues.append("Too many complex words")
        
        # Check for passive voice indicators
        passive_indicators = ['was', 'were', 'been', 'being', 'be']
        passive_count = sum(1 for word in passive_indicators 
                          if word in script.lower().split())
        if passive_count > len(sentences) * 0.3:
            issues.append("Too much passive voice")
        
        # Calculate clarity score
        score = 1.0
        score -= len(issues) * 0.2
        score -= (avg_sentence_length - 15) * 0.02 if avg_sentence_length > 15 else 0
        score = max(0, min(1.0, score))
        
        return {
            'score': score,
            'issues': issues,
            'avg_sentence_length': avg_sentence_length,
            'complex_words_ratio': complex_word_count / len(script.split())
        }
    
    def _analyze_hook(self, script: str) -> Dict[str, Any]:
        """Analyze the effectiveness of the opening hook"""
        sentences = self._split_into_sentences(script)
        
        if not sentences:
            return {'score': 0, 'issues': ['No content']}
        
        first_sentence = sentences[0]
        first_words = first_sentence.split()[:self.hook_word_limit]
        hook_text = ' '.join(first_words)
        
        score = 0.5  # Base score
        
        # Check for question hook
        if '?' in first_sentence:
            score += 0.2
        
        # Check for surprising statement
        if any(word in hook_text.lower() for word in ['never', 'always', 'secret', 'shocking']):
            score += 0.2
        
        # Check for direct address
        if 'you' in hook_text.lower():
            score += 0.1
        
        # Check for number/statistic
        if any(char.isdigit() for char in hook_text):
            score += 0.15
        
        # Check length (shorter is often better for hooks)
        if len(first_words) <= 10:
            score += 0.1
        
        return {
            'score': min(1.0, score),
            'hook_text': hook_text,
            'hook_type': self._identify_hook_type(first_sentence)
        }
    
    def _evaluate_cta(self, script: str) -> Dict[str, Any]:
        """Evaluate the call-to-action strength"""
        script_lower = script.lower()
        sentences = self._split_into_sentences(script)
        last_sentences = ' '.join(sentences[-2:]) if len(sentences) >= 2 else script
        
        cta_keywords = [
            'subscribe', 'follow', 'like', 'comment', 'share', 'click',
            'visit', 'check out', 'learn more', 'get', 'download', 'join'
        ]
        
        score = 0.3  # Base score if CTA exists
        
        # Check for CTA keywords
        cta_found = False
        for keyword in cta_keywords:
            if keyword in script_lower:
                cta_found = True
                score += 0.2
                break
        
        # Check if CTA is in the last part
        if cta_found and any(keyword in last_sentences.lower() for keyword in cta_keywords):
            score += 0.2
        
        # Check for urgency in CTA
        urgency_words = ['now', 'today', 'limited', 'exclusive', 'before']
        if any(word in script_lower for word in urgency_words):
            score += 0.15
        
        # Check for benefit statement
        benefit_words = ['free', 'save', 'improve', 'transform', 'discover']
        if any(word in script_lower for word in benefit_words):
            score += 0.15
        
        return {
            'score': min(1.0, score) if cta_found else 0,
            'has_cta': cta_found,
            'cta_position': 'end' if cta_found and any(kw in last_sentences.lower() for kw in cta_keywords) else 'middle'
        }
    
    def _identify_key_moments(self, script: str, duration_seconds: float) -> Dict[str, float]:
        """Identify key moments and their timestamps"""
        sentences = self._split_into_sentences(script)
        if not sentences:
            return {}
        
        total_words = len(script.split())
        seconds_per_word = duration_seconds / total_words if total_words > 0 else 0
        
        key_moments = {}
        current_time = 0
        
        for i, sentence in enumerate(sentences):
            sentence_words = len(sentence.split())
            sentence_duration = sentence_words * seconds_per_word
            
            # Check for hook (first sentence)
            if i == 0:
                key_moments['hook'] = 0
            
            # Check for reveal/climax keywords
            if any(word in sentence.lower() for word in ['reveal', 'secret', 'truth', 'answer']):
                key_moments['reveal'] = current_time
            
            # Check for CTA
            if any(word in sentence.lower() for word in ['subscribe', 'follow', 'click']):
                key_moments['cta'] = current_time
            
            current_time += sentence_duration
        
        # Add climax point (usually 60-70% through)
        if 'reveal' not in key_moments:
            key_moments['climax'] = duration_seconds * 0.65
        
        return key_moments
    
    def _identify_hook_type(self, first_sentence: str) -> str:
        """Identify the type of hook used"""
        first_sentence_lower = first_sentence.lower()
        
        if '?' in first_sentence:
            return "question"
        elif any(word in first_sentence_lower for word in ['you', 'your']):
            return "direct_address"
        elif any(char.isdigit() for char in first_sentence):
            return "statistic"
        elif any(word in first_sentence_lower for word in ['imagine', 'what if', 'picture']):
            return "scenario"
        elif any(word in first_sentence_lower for word in ['secret', 'revealed', 'truth']):
            return "revelation"
        else:
            return "statement"
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting (could be enhanced with NLP)
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def enhance_script(self, script: str, metrics: ScriptQualityMetrics) -> str:
        """
        Enhance script based on quality metrics
        
        Args:
            script: Original script
            metrics: Quality metrics from validation
            
        Returns:
            Enhanced script with improvements
        """
        enhanced = script
        
        # Add hook if weak
        if metrics.hook_effectiveness < 0.7:
            hook_suggestions = [
                "Did you know that ",
                "What if I told you ",
                "The shocking truth about ",
                "You won't believe what "
            ]
            # Prepend a hook if not starting with a question
            if not script.startswith(tuple(hook_suggestions)) and '?' not in script[:50]:
                enhanced = f"What if I told you {enhanced[0].lower()}{enhanced[1:]}"
        
        # Add CTA if missing or weak
        if metrics.cta_strength < 0.6:
            cta_templates = [
                "\n\nDon't forget to subscribe for more amazing content!",
                "\n\nHit that follow button to never miss an update!",
                "\n\nShare this with someone who needs to see it!",
                "\n\nComment below with your thoughts!"
            ]
            # Add CTA if not present
            if not any(word in enhanced.lower() for word in ['subscribe', 'follow', 'share', 'comment']):
                enhanced += cta_templates[0]
        
        # Add emotional triggers if lacking
        if metrics.emotional_score < 0.5:
            # Insert power words at key positions
            sentences = self._split_into_sentences(enhanced)
            if len(sentences) > 2:
                # Add emphasis to middle sentence
                middle_idx = len(sentences) // 2
                sentences[middle_idx] = f"This is absolutely incredible - {sentences[middle_idx]}"
                enhanced = '. '.join(sentences) + '.'
        
        return enhanced
    
    def get_quality_report(self, metrics: ScriptQualityMetrics) -> str:
        """Generate a detailed quality report"""
        report = f"""
📊 SCRIPT QUALITY REPORT
========================

Overall Score: {metrics.overall_score:.2f}/1.0 {'✅' if metrics.overall_score >= 0.7 else '⚠️'}

Detailed Metrics:
• Narrative Structure: {metrics.narrative_score:.2f}/1.0
• Pacing: {metrics.pacing_score:.2f}/1.0
• Engagement: {metrics.engagement_score:.2f}/1.0
• Emotional Impact: {metrics.emotional_score:.2f}/1.0
• Clarity: {metrics.clarity_score:.2f}/1.0
• Hook Effectiveness: {metrics.hook_effectiveness:.2f}/1.0
• CTA Strength: {metrics.cta_strength:.2f}/1.0

Narrative Arc: {metrics.narrative_arc.value}
Emotional Journey: {' → '.join([e.value for e in metrics.emotional_journey[:5]])}

Key Moments:
{chr(10).join([f'• {moment}: {time:.1f}s' for moment, time in metrics.key_moments.items()])}

Issues Found:
{chr(10).join([f'❌ {issue}' for issue in metrics.issues]) if metrics.issues else '✅ No major issues'}

Recommendations:
{chr(10).join([f'💡 {suggestion}' for suggestion in metrics.suggestions]) if metrics.suggestions else '✅ Script is well-optimized'}
"""
        return report