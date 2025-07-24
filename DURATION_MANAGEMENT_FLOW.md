# Duration Management Flow in ViralAI

## Overview
The system now has comprehensive duration management with ±5% tolerance across all components.

## Duration Flow

### 1. Initial Duration Decision
```
User Input (--duration 40) 
    ↓
DecisionFramework.make_all_decisions()
    ↓
CoreDecisions.duration_seconds = 40
```

### 2. Script Generation & Control
```
Director.generate_script() 
    ↓
Word Limit Enforcement:
- Target: duration * 2.3-2.5 words/second
- For 40s: 92-100 words MAXIMUM
- Prompt explicitly says "DO NOT EXCEED"
    ↓
EnhancedScriptProcessor.process_script_for_tts()
    ↓
Duration Validation:
- Checks if script fits within ±2 seconds
- If not, triggers _reprocess_for_duration()
- Trims sentences to fit word count
```

### 3. Audio Generation Control
```
VideoGenerator._generate_ai_optimized_audio()
    ↓
Pre-Generation Control:
1. Calculate max words: duration * 2.5
2. If script exceeds, trim to complete sentences that fit
3. Track cumulative duration during generation
4. Stop generating if approaching 105% of target
    ↓
Per-Segment Control:
- Each segment gets duration estimate
- If segment would exceed total, reduce its duration
- Track actual duration after each generation
    ↓
Post-Generation Validation:
- Measure total actual duration
- Log warnings if outside ±5% tolerance
```

### 4. Duration Coordinator
```
DurationCoordinator(target_duration=40)
    ↓
Tracks All Components:
- analyze_script_duration() → script timing
- analyze_audio_files() → actual audio duration  
- analyze_video_clips() → video duration
    ↓
get_optimal_duration():
- Uses maximum duration from all components
- Caps at target * 1.05 (5% tolerance)
```

### 5. Video Assembly
```
_compose_final_video_with_subtitles()
    ↓
Uses DurationCoordinator optimal duration
    ↓
Final Duration Enforcement:
- If > 105% of target: Trim video
- If < 95% of target: Extend video (freeze last frame)
```

### 6. AI Agent Validation
```
All Modes (simple/enhanced/professional):
    ↓
Mandatory "Duration & Timing Validation" discussion
    ↓
AudioMaster (SOUNDMAN) agent enforces:
- Script must fit duration
- Audio segments must sum correctly
- No padding or filler content
```

## Key Improvements

### Before:
- 15% tolerance (too permissive)
- Scripts could expand beyond limits
- Audio segments concatenated without limit checking
- No pre-generation validation
- Duration validation optional in simple mode

### After:
- 5% tolerance (strict)
- Scripts trimmed to fit before audio generation
- Audio generation stops when approaching limit
- Pre-generation word count validation
- Duration validation mandatory in ALL modes
- Final validation after generation

## Example Flow (40s video)

1. **Script Generation**:
   - Max words: 100 (40s * 2.5)
   - Script processor enforces this limit

2. **Audio Pre-Processing**:
   - If script has 120 words → trim to sentences that fit in 100 words
   - Create segments with calculated durations

3. **Audio Generation**:
   - Track total: 0s → 10s → 20s → 30s → 38s
   - At 38s, if next segment is 5s, reduce to 2s (to stay under 42s)

4. **Final Assembly**:
   - DurationCoordinator reports optimal duration
   - If final video is 43s (>42s limit) → trim to 42s
   - If final video is 37s (<38s minimum) → extend to 38s

## Result
Videos now consistently stay within ±5% of target duration through multiple enforcement points.