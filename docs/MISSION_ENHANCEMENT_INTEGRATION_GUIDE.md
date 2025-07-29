# Mission Enhancement Integration Guide

## Overview
This guide provides specific code integration points for implementing mission-focused improvements in the ViralAI system.

## Integration Points

### 1. Decision Framework Enhancement

**File**: `/src/core/decision_framework.py`

**Add to imports**:
```python
from ..agents.enhanced_mission_analyzer import EnhancedMissionAnalyzer
from ..agents.mission_coherence_enforcer import MissionCoherenceEnforcer
from ..frameworks.content_credibility_system import ContentCredibilitySystem
from ..frameworks.audience_intelligence_system import AudienceIntelligenceSystem
```

**Enhance `make_all_decisions()` method** (around line 140):
```python
async def make_all_decisions(self, cli_args: Dict[str, Any], 
                           user_config: Optional[Dict[str, Any]] = None) -> CoreDecisions:
    # ... existing code ...
    
    # NEW: Deep mission analysis
    if ai_available and not cheap_mode:
        # Initialize mission analyzer
        mission_analyzer = EnhancedMissionAnalyzer(self.ai_manager)
        
        # Analyze mission depth
        mission_analysis = await mission_analyzer.analyze_mission_depth(
            mission=mission,
            duration=duration,
            target_audience=target_audience,
            platform=platform
        )
        
        # Record mission analysis
        self._record_decision('mission_analysis', mission_analysis, 
                            DecisionSource.AI_AGENT, 0.95,
                            "Deep mission understanding and strategy")
        
        # Generate impact strategies
        impact_strategies = await mission_analyzer.generate_impact_strategies(
            mission_analysis=mission_analysis,
            platform=platform.value
        )
        
        self._record_decision('impact_strategies', impact_strategies,
                            DecisionSource.AI_AGENT, 0.9,
                            "Mission accomplishment strategies")
```

### 2. Working Orchestrator Enhancement

**File**: `/src/agents/working_orchestrator.py`

**Update `generate_comprehensive_script()` method** (around line 380):
```python
async def generate_comprehensive_script(self) -> Dict[str, Any]:
    # ... existing code ...
    
    # NEW: Add mission-focused discussion topics
    from ..agents.mission_discussion_topics import MissionDiscussionTopics
    
    # Replace or enhance existing topics
    mission_topics = [
        MissionDiscussionTopics.mission_strategy(context),
        MissionDiscussionTopics.impact_maximization(context),
        MissionDiscussionTopics.coherence_enforcement(context),
        MissionDiscussionTopics.audience_psychology(context),
        # ... existing topics ...
    ]
    
    # NEW: After script generation, validate coherence
    if self.core_decisions and hasattr(self.core_decisions, 'mission_analysis'):
        coherence_enforcer = MissionCoherenceEnforcer(self.ai_manager)
        
        validation = await coherence_enforcer.validate_script_alignment(
            mission=self.mission,
            core_message=self.core_decisions.mission_analysis['core_message'],
            script_segments=final_script.get('segments', [])
        )
        
        # Enhance weak segments
        if validation['overall_coherence_score'] < 80:
            weak_segments = [s for s in validation['segments'] 
                           if s['alignment_score'] < 70]
            enhanced_segments = await coherence_enforcer.enhance_weak_segments(
                mission=self.mission,
                core_message=self.core_decisions.mission_analysis['core_message'],
                weak_segments=weak_segments
            )
            # Update script with enhanced segments
```

### 3. Script Generator Enhancement

**File**: `/src/generators/separated_script_generator.py`

**Add mission-driven mode** (around line 40):
```python
async def generate_separated_script(self, mission: str, duration: int,
                                  style: str, platform: Platform,
                                  language: Language = Language.ENGLISH_US,
                                  character_description: str = None,
                                  mission_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
    
    # NEW: Use mission-driven generation if analysis available
    if mission_analysis:
        from ..generators.mission_driven_script_generator import MissionDrivenScriptGenerator
        
        mission_generator = MissionDrivenScriptGenerator(self.ai_manager)
        script_data = await mission_generator.generate_mission_script(
            mission=mission,
            mission_analysis=mission_analysis,
            duration=duration,
            platform=platform,
            language=language
        )
        
        # Optimize for platform
        script_data = await mission_generator.optimize_for_impact(
            script_data=script_data,
            platform=platform
        )
        
        return script_data
    
    # ... existing generation code as fallback ...
```

### 4. Director Enhancement

**File**: `/src/generators/director.py`

**Enhance `_create_hook()` method** (around line 141):
```python
def _create_hook(self, mission: str, style: str, platform: Platform,
               patterns: Dict[str, Any], news_context: str,
               mission_analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    
    # NEW: Mission-focused hook generation
    if mission_analysis:
        core_message = mission_analysis.get('core_message', mission)
        impact_type = mission_analysis.get('impact_type', 'awareness_building')
        resistance_points = mission_analysis.get('resistance_points', [])
        
        hook_prompt = f"""
        Create a powerful hook that IMMEDIATELY establishes why viewers must watch.
        
        MISSION: {mission}
        CORE MESSAGE: {core_message}
        IMPACT GOAL: {impact_type}
        PLATFORM: {platform.value}
        
        Address potential objections: {', '.join(resistance_points[:2])}
        
        Hook must:
        1. Create immediate relevance in 3 seconds
        2. Establish the mission importance
        3. Create curiosity about the solution
        4. Use {mission_analysis['persuasion_framework']['primary_approach']} appeal
        
        Return hook text (10-15 words max).
        """
        
        # Generate with mission focus
        # ... implementation ...
```

### 5. Multi-Agent Discussion Enhancement

**File**: `/src/agents/multi_agent_discussion.py`

**Update `_create_agent_prompt()` method** (around line 650):
```python
def _create_agent_prompt(self, agent_role: AgentRole, agent_info: Dict[str, Any],
                       topic: DiscussionTopic, discussion_context: str,
                       round_num: int, mission_or_topic: str,
                       duration: int, platform: str,
                       is_mission: bool = True) -> str:
    
    # NEW: Enhanced mission-focused prompt
    if is_mission:
        # Check if we have mission analysis in context
        mission_analysis = topic.context.get('mission_analysis', {})
        core_message = mission_analysis.get('core_message', mission_or_topic)
        desired_outcome = mission_analysis.get('desired_outcome', 'viewer action')
        
        return f"""
You are {agent_info['name']}, focused on ACCOMPLISHING this mission.

MISSION: {mission_or_topic}
CORE MESSAGE: {core_message}
DESIRED OUTCOME: {desired_outcome}
YOUR EXPERTISE: {', '.join(agent_info['expertise'])}

🎯 YOUR TASK: Contribute strategies to ACCOMPLISH this mission in {duration}s on {platform}.

Consider:
1. How your expertise helps achieve {desired_outcome}
2. Specific techniques from your domain
3. Overcoming resistance: {', '.join(mission_analysis.get('resistance_points', [])[:2])}
4. Evidence to support: {', '.join(mission_analysis.get('key_evidence', [])[:2])}

CRITICAL: Every suggestion must directly advance the mission.

Respond with specific, actionable strategies in JSON format.
"""
```

### 6. Enhanced Overlay Integration

**File**: `/src/generators/ffmpeg_video_composer.py`

**Enhance overlay generation** (around line 60):
```python
# Step 4: Generate AI-powered viral overlays
overlays = await self.overlay_agent.generate_viral_overlays(
    mission=config.get('mission', ''),
    script=config.get('script', ''),
    duration=ffmpeg.get_duration(video_with_audio),
    platform=config.get('platform', 'instagram'),
    style=config.get('style', 'viral'),
    segments=config.get('segments', []),
    # NEW: Mission-focused overlay parameters
    mission_analysis=config.get('mission_analysis', {}),
    core_message=config.get('core_message', ''),
    key_moments=config.get('key_reinforcement_moments', [])
)

# NEW: Add mission reinforcement overlays
if config.get('mission_analysis'):
    reinforcement_plan = config.get('reinforcement_plan', {})
    for reinforcement in reinforcement_plan.get('text_reinforcements', []):
        overlay = self._create_mission_overlay(
            text=reinforcement['text'],
            timing=reinforcement['timing'],
            style=reinforcement['style']
        )
        overlays.append(overlay)
```

### 7. Quick Implementation Helper

**File**: `/src/utils/mission_integration_helper.py` (NEW)
```python
"""
Mission Integration Helper - Utilities for easy mission enhancement integration
"""
from typing import Dict, Any, Optional
from ..agents.quick_mission_enhancement import QuickMissionEnhancer

class MissionIntegrationHelper:
    """Helper class for integrating mission enhancements"""
    
    @staticmethod
    def enhance_any_prompt(prompt: str, mission: str, duration: int) -> str:
        """Add mission focus to any AI prompt"""
        return prompt + QuickMissionEnhancer.enhance_mission_prompt(mission, duration)
    
    @staticmethod
    def validate_mission_focus(content: Dict[str, Any], mission: str) -> Dict[str, Any]:
        """Quick validation of content mission alignment"""
        if 'segments' in content:
            return QuickMissionEnhancer.validate_script_focus(
                content['segments'], mission
            )
        return {"focus_score": 0, "recommendation": "No segments to validate"}
    
    @staticmethod
    def add_reinforcements(content: Dict[str, Any], mission: str) -> Dict[str, Any]:
        """Add mission reinforcement metadata"""
        return QuickMissionEnhancer.add_mission_reinforcement(content, mission)
```

## Testing the Integration

### 1. Unit Tests
```bash
# Test mission analyzer
python -m pytest tests/test_mission_analyzer.py

# Test coherence enforcer  
python -m pytest tests/test_coherence_enforcer.py

# Test integration
python -m pytest tests/test_mission_integration.py
```

### 2. Integration Test Command
```bash
# Test with mission-focused generation
python cli.py \
  --mission "Convince parents to limit kids' screen time to 2 hours daily" \
  --duration 30 \
  --platform tiktok \
  --mode enhanced \
  --debug
```

### 3. Validation Checklist
- [ ] Mission analysis completes successfully
- [ ] Agent discussions focus on mission accomplishment
- [ ] Script segments all advance the mission
- [ ] Coherence score > 80%
- [ ] Overlays reinforce key messages
- [ ] CTA directly relates to mission

## Configuration

### Enable Mission Features
```python
# In config/settings.py or environment
ENABLE_MISSION_ENHANCEMENT = True
MISSION_COHERENCE_THRESHOLD = 0.8
MISSION_REINFORCEMENT_ENABLED = True
```

### Adjust Weights
```python
# In decision_framework.py
MISSION_WEIGHT = 0.9  # How much to prioritize mission (0-1)
COHERENCE_WEIGHT = 0.85  # Minimum acceptable coherence
```

## Monitoring

### Log Analysis
```bash
# Check mission alignment
grep "Mission alignment score" outputs/*/logs/*.log

# Check coherence
grep "Coherence Score" outputs/*/logs/*.log

# Check improvements
grep "enhanced segments" outputs/*/logs/*.log
```

### Metrics to Track
1. Mission alignment scores
2. Coherence scores
3. Segment enhancement rate
4. Generation time impact
5. User engagement metrics

## Troubleshooting

### Common Issues

1. **Slow Generation**
   - Solution: Use `--cheap` mode for testing
   - Disable mission analysis for simple content

2. **Low Coherence Scores**
   - Check mission clarity
   - Ensure sufficient duration for mission
   - Review agent discussion logs

3. **Integration Errors**
   - Verify all imports are correct
   - Check AI manager initialization
   - Ensure API keys are valid

## Next Steps

1. Start with Phase 1 components
2. Test with sample missions
3. Measure improvement metrics
4. Iterate based on results
5. Expand to full implementation

---

*Integration Guide v1.0*
*Last Updated: Current*