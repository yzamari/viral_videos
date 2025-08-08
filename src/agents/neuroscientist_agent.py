"""
Neuroscientist Agent
Analyzes content for neurological triggers and dopamine-inducing elements
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from ..utils.logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class NeurologicalInsight:
    """Represents a neurological insight about content"""
    trigger_type: str  # dopamine, serotonin, adrenaline, oxytocin, endorphins
    mechanism: str  # The neurological mechanism being activated
    intensity: float  # 0.0 to 1.0 intensity of the trigger
    explanation: str  # Scientific explanation
    implementation: str  # How to implement this in the content
    timing: Optional[str] = None  # When in the content this should occur

class NeuroscientistAgent:
    """
    AI agent specializing in neuroscience and psychological triggers
    Analyzes content for brain engagement and dopamine release patterns
    """
    
    # Core neurological triggers for viral content
    DOPAMINE_TRIGGERS = {
        "anticipation": {
            "mechanism": "Reward prediction error - brain releases dopamine when anticipating rewards",
            "implementation": "Create cliffhangers, tease upcoming reveals, use countdown timers",
            "intensity": 0.9
        },
        "pattern_interruption": {
            "mechanism": "Unexpected events trigger dopamine release through novelty detection",
            "implementation": "Break patterns with surprising twists, unexpected cuts, or plot reversals",
            "intensity": 0.85
        },
        "achievement_moments": {
            "mechanism": "Completion and success trigger reward pathways",
            "implementation": "Show progression, milestones, 'before/after' transformations",
            "intensity": 0.8
        },
        "social_validation": {
            "mechanism": "Social approval activates dopaminergic reward circuits",
            "implementation": "Include social proof, community reactions, viral moments",
            "intensity": 0.75
        },
        "curiosity_gaps": {
            "mechanism": "Information gaps create cognitive tension that dopamine helps resolve",
            "implementation": "Pose questions, create mysteries, withhold key information initially",
            "intensity": 0.85
        },
        "variable_rewards": {
            "mechanism": "Unpredictable rewards create strongest dopamine response (like gambling)",
            "implementation": "Mix predictable and unpredictable elements, vary pacing",
            "intensity": 0.95
        }
    }
    
    ENGAGEMENT_TRIGGERS = {
        "mirror_neurons": {
            "mechanism": "Mirror neurons fire when observing actions, creating empathy and engagement",
            "implementation": "Show human faces, emotional reactions, relatable behaviors",
            "neurotransmitter": "oxytocin",
            "intensity": 0.8
        },
        "fear_of_missing_out": {
            "mechanism": "FOMO activates amygdala and creates urgency through stress hormones",
            "implementation": "Limited time offers, exclusive content, trending topics",
            "neurotransmitter": "cortisol/adrenaline",
            "intensity": 0.7
        },
        "cognitive_ease": {
            "mechanism": "Brain prefers easily processed information, reducing cognitive load",
            "implementation": "Simple language, clear visuals, familiar patterns with twists",
            "neurotransmitter": "serotonin",
            "intensity": 0.6
        },
        "emotional_contagion": {
            "mechanism": "Emotions spread through automatic mimicry and feedback",
            "implementation": "Strong emotional displays, laughter, excitement, surprise",
            "neurotransmitter": "multiple",
            "intensity": 0.85
        },
        "storytelling_arc": {
            "mechanism": "Narrative structure engages multiple brain regions simultaneously",
            "implementation": "Clear beginning, tension building, climax, resolution",
            "neurotransmitter": "dopamine/oxytocin",
            "intensity": 0.9
        }
    }
    
    RETENTION_PATTERNS = {
        "primacy_recency": {
            "principle": "First and last moments are most memorable",
            "implementation": "Strong hooks at start, powerful endings"
        },
        "peak_end_rule": {
            "principle": "People judge experiences by peak moment and ending",
            "implementation": "Create one intense peak moment, ensure satisfying conclusion"
        },
        "chunking": {
            "principle": "Brain processes information better in chunks",
            "implementation": "Break content into digestible segments with micro-rewards"
        },
        "repetition_variation": {
            "principle": "Repetition with variation enhances memory encoding",
            "implementation": "Repeat key messages with different presentations"
        }
    }
    
    def __init__(self):
        """Initialize the neuroscientist agent"""
        self.logger = logger
        
    def analyze_content_for_triggers(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze content and suggest neurological optimization
        
        Args:
            content: Content details including script, visuals, timing
            
        Returns:
            Dictionary with neurological insights and recommendations
        """
        insights = []
        
        # Analyze for dopamine triggers
        dopamine_suggestions = self._analyze_dopamine_potential(content)
        insights.extend(dopamine_suggestions)
        
        # Analyze for engagement triggers
        engagement_suggestions = self._analyze_engagement_potential(content)
        insights.extend(engagement_suggestions)
        
        # Analyze retention patterns
        retention_suggestions = self._analyze_retention_patterns(content)
        insights.extend(retention_suggestions)
        
        # Generate implementation timeline
        timeline = self._create_neurological_timeline(insights, content)
        
        return {
            "neurological_insights": insights,
            "implementation_timeline": timeline,
            "predicted_engagement_score": self._calculate_engagement_score(insights),
            "key_recommendations": self._prioritize_recommendations(insights),
            "scientific_rationale": self._generate_scientific_explanation(insights)
        }
    
    def _analyze_dopamine_potential(self, content: Dict[str, Any]) -> List[NeurologicalInsight]:
        """Analyze content for dopamine trigger opportunities"""
        insights = []
        
        # Check for anticipation building
        if "script" in content:
            script = content.get("script", "")
            if "reveal" in script.lower() or "discover" in script.lower():
                insights.append(NeurologicalInsight(
                    trigger_type="dopamine",
                    mechanism=self.DOPAMINE_TRIGGERS["anticipation"]["mechanism"],
                    intensity=self.DOPAMINE_TRIGGERS["anticipation"]["intensity"],
                    explanation="Content contains reveal moments that can trigger anticipatory dopamine",
                    implementation="Delay the reveal by 2-3 seconds with visual or audio cues building anticipation",
                    timing="Before each major reveal"
                ))
        
        # Check for pattern interruption opportunities
        if content.get("style") != "predictable":
            insights.append(NeurologicalInsight(
                trigger_type="dopamine",
                mechanism=self.DOPAMINE_TRIGGERS["pattern_interruption"]["mechanism"],
                intensity=self.DOPAMINE_TRIGGERS["pattern_interruption"]["intensity"],
                explanation="Unexpected elements can create novelty-driven dopamine spikes",
                implementation="Add unexpected visual transitions or audio stings at 30% and 70% marks",
                timing="30% and 70% through content"
            ))
        
        # Variable reward scheduling
        insights.append(NeurologicalInsight(
            trigger_type="dopamine",
            mechanism=self.DOPAMINE_TRIGGERS["variable_rewards"]["mechanism"],
            intensity=self.DOPAMINE_TRIGGERS["variable_rewards"]["intensity"],
            explanation="Variable reward schedules create the strongest dopamine response",
            implementation="Vary the pacing - mix fast cuts with slower moments unpredictably",
            timing="Throughout, with emphasis on middle section"
        ))
        
        return insights
    
    def _analyze_engagement_potential(self, content: Dict[str, Any]) -> List[NeurologicalInsight]:
        """Analyze content for general engagement triggers"""
        insights = []
        
        # Mirror neuron activation
        if content.get("includes_people", True):
            insights.append(NeurologicalInsight(
                trigger_type="oxytocin",
                mechanism=self.ENGAGEMENT_TRIGGERS["mirror_neurons"]["mechanism"],
                intensity=self.ENGAGEMENT_TRIGGERS["mirror_neurons"]["intensity"],
                explanation="Human faces and emotions activate mirror neurons for deep engagement",
                implementation="Include close-ups of facial expressions, especially during emotional peaks",
                timing="During emotional or reaction moments"
            ))
        
        # Emotional contagion
        insights.append(NeurologicalInsight(
            trigger_type="multiple",
            mechanism=self.ENGAGEMENT_TRIGGERS["emotional_contagion"]["mechanism"],
            intensity=self.ENGAGEMENT_TRIGGERS["emotional_contagion"]["intensity"],
            explanation="Strong emotions are contagious and increase viewer engagement",
            implementation="Amplify emotional moments with music, pacing, and visual intensity",
            timing="Peak emotional moments"
        ))
        
        return insights
    
    def _analyze_retention_patterns(self, content: Dict[str, Any]) -> List[NeurologicalInsight]:
        """Analyze how to optimize memory retention"""
        insights = []
        
        # Primacy-recency effect
        insights.append(NeurologicalInsight(
            trigger_type="memory",
            mechanism="Primacy-recency effect enhances memory encoding",
            intensity=0.9,
            explanation="First 3 seconds and last 3 seconds are most memorable",
            implementation="Place key message/branding in first 3 and last 3 seconds",
            timing="0-3 seconds and final 3 seconds"
        ))
        
        # Peak-end rule
        insights.append(NeurologicalInsight(
            trigger_type="memory",
            mechanism="Peak-end rule determines overall experience memory",
            intensity=0.85,
            explanation="Viewers judge entire experience by peak moment and ending",
            implementation="Create one spectacular peak moment at 60-70% mark, ensure satisfying ending",
            timing="60-70% for peak, 95-100% for ending"
        ))
        
        return insights
    
    def _create_neurological_timeline(self, insights: List[NeurologicalInsight], 
                                     content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create a timeline of when to deploy each neurological trigger"""
        duration = content.get("duration", 60)
        timeline = []
        
        # Opening hook (0-3 seconds)
        timeline.append({
            "time": "0-3s",
            "triggers": ["curiosity_gap", "pattern_interruption"],
            "goal": "Capture attention and create anticipation",
            "intensity": "high"
        })
        
        # Build phase (3-30% of content)
        timeline.append({
            "time": f"3s-{int(duration*0.3)}s",
            "triggers": ["anticipation", "mirror_neurons"],
            "goal": "Build emotional investment and curiosity",
            "intensity": "medium-building"
        })
        
        # First peak (30% mark)
        timeline.append({
            "time": f"{int(duration*0.3)}s",
            "triggers": ["pattern_interruption", "dopamine_spike"],
            "goal": "First reward to maintain engagement",
            "intensity": "high"
        })
        
        # Development (30-60%)
        timeline.append({
            "time": f"{int(duration*0.3)}s-{int(duration*0.6)}s",
            "triggers": ["variable_rewards", "emotional_contagion"],
            "goal": "Maintain engagement with varied stimulation",
            "intensity": "variable"
        })
        
        # Main peak (60-70%)
        timeline.append({
            "time": f"{int(duration*0.6)}s-{int(duration*0.7)}s",
            "triggers": ["peak_experience", "maximum_dopamine"],
            "goal": "Create memorable peak moment",
            "intensity": "maximum"
        })
        
        # Resolution (70-95%)
        timeline.append({
            "time": f"{int(duration*0.7)}s-{int(duration*0.95)}s",
            "triggers": ["achievement", "satisfaction"],
            "goal": "Provide closure and satisfaction",
            "intensity": "medium-high"
        })
        
        # Ending hook (95-100%)
        timeline.append({
            "time": f"{int(duration*0.95)}s-{duration}s",
            "triggers": ["social_validation", "call_to_action"],
            "goal": "Encourage sharing and engagement",
            "intensity": "high"
        })
        
        return timeline
    
    def _calculate_engagement_score(self, insights: List[NeurologicalInsight]) -> float:
        """Calculate predicted engagement score based on neurological triggers"""
        if not insights:
            return 0.5
        
        total_intensity = sum(insight.intensity for insight in insights)
        average_intensity = total_intensity / len(insights)
        
        # Weight by trigger diversity
        unique_triggers = len(set(insight.trigger_type for insight in insights))
        diversity_bonus = min(unique_triggers * 0.05, 0.2)
        
        return min(average_intensity + diversity_bonus, 1.0)
    
    def _prioritize_recommendations(self, insights: List[NeurologicalInsight]) -> List[str]:
        """Prioritize top recommendations based on impact"""
        # Sort by intensity
        sorted_insights = sorted(insights, key=lambda x: x.intensity, reverse=True)
        
        # Get top 5 recommendations
        top_recommendations = []
        for insight in sorted_insights[:5]:
            top_recommendations.append(f"• {insight.implementation} (Impact: {insight.intensity:.0%})")
        
        return top_recommendations
    
    def _generate_scientific_explanation(self, insights: List[NeurologicalInsight]) -> str:
        """Generate scientific explanation of the neurological approach"""
        explanation = "NEUROLOGICAL OPTIMIZATION STRATEGY:\n\n"
        
        # Group by neurotransmitter
        dopamine_insights = [i for i in insights if i.trigger_type == "dopamine"]
        other_insights = [i for i in insights if i.trigger_type != "dopamine"]
        
        if dopamine_insights:
            explanation += "DOPAMINE ACTIVATION (Reward & Motivation):\n"
            explanation += "The content leverages dopaminergic pathways through:\n"
            for insight in dopamine_insights[:3]:
                explanation += f"- {insight.mechanism}\n"
            explanation += "\n"
        
        if other_insights:
            explanation += "MULTI-SYSTEM ENGAGEMENT:\n"
            explanation += "Additional neurological systems activated:\n"
            for insight in other_insights[:3]:
                explanation += f"- {insight.trigger_type.upper()}: {insight.mechanism}\n"
            explanation += "\n"
        
        explanation += "EXPECTED OUTCOME:\n"
        explanation += "This neurological approach should increase:\n"
        explanation += "- Initial attention capture by 40-60%\n"
        explanation += "- Sustained engagement by 25-35%\n"
        explanation += "- Memory retention by 30-45%\n"
        explanation += "- Sharing likelihood by 20-30%"
        
        return explanation
    
    def suggest_optimizations(self, current_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggest specific optimizations for existing content
        
        Args:
            current_content: Current content structure
            
        Returns:
            Optimization suggestions with neurological backing
        """
        analysis = self.analyze_content_for_triggers(current_content)
        
        optimizations = {
            "immediate_changes": [],
            "structural_changes": [],
            "timing_adjustments": []
        }
        
        # Immediate changes (easy wins)
        optimizations["immediate_changes"] = [
            "Add 2-second anticipation pause before reveals",
            "Include human reaction shots for mirror neuron activation",
            "Use ascending audio cue before key moments",
            "Add progress indicators for achievement sensing"
        ]
        
        # Structural changes
        optimizations["structural_changes"] = [
            "Restructure content with clear 3-act structure for storytelling engagement",
            "Add pattern interruption at 30% and 70% marks",
            "Create curiosity gap in first 3 seconds",
            "Ensure peak moment occurs at 60-70% point"
        ]
        
        # Timing adjustments
        optimizations["timing_adjustments"] = [
            "Quicken pace in first 3 seconds (1-second cuts maximum)",
            "Slow down at peak moment for emphasis (2-3 second holds)",
            "Variable pacing throughout (mix 0.5-3 second cuts)",
            "Strong pause before final call-to-action"
        ]
        
        return {
            "optimizations": optimizations,
            "neurological_analysis": analysis,
            "implementation_priority": self._rank_by_roi(optimizations),
            "expected_improvement": self._estimate_improvement(analysis)
        }
    
    def _rank_by_roi(self, optimizations: Dict[str, List[str]]) -> List[str]:
        """Rank optimizations by return on investment"""
        ranked = []
        
        # Immediate changes have highest ROI (easy to implement, good impact)
        for opt in optimizations["immediate_changes"]:
            ranked.append(f"HIGH ROI: {opt}")
        
        # Timing adjustments are medium ROI
        for opt in optimizations["timing_adjustments"]:
            ranked.append(f"MEDIUM ROI: {opt}")
        
        # Structural changes are lower ROI (harder to implement)
        for opt in optimizations["structural_changes"]:
            ranked.append(f"LONG-TERM: {opt}")
        
        return ranked
    
    def _estimate_improvement(self, analysis: Dict[str, Any]) -> Dict[str, str]:
        """Estimate improvement metrics from neurological optimization"""
        score = analysis["predicted_engagement_score"]
        
        return {
            "attention_capture": f"+{int(score * 50)}% in first 3 seconds",
            "watch_time": f"+{int(score * 30)}% average view duration",
            "engagement_rate": f"+{int(score * 40)}% likes/comments",
            "share_rate": f"+{int(score * 25)}% sharing probability",
            "memory_retention": f"+{int(score * 35)}% brand recall after 24 hours"
        }