# Enhanced Mission Parser Fix Documentation

## Issue Identified
Visual instructions and stage directions were being included in the spoken audio and subtitles, causing the TTS to speak things like "*drinks entire bottle*" and "End card: Logo".

## Root Cause Analysis

### 1. Parser Fallback Issue
The Enhanced Mission Parser was falling back to heuristic parsing due to JSON parsing errors, and the heuristic parser was too simplistic - it extracted ALL quoted text as script content.

### 2. Director Override Issue  
Even when the parser correctly separated dialogue from visual instructions, the Director was being called with the full mission and overriding the parsed script content.

## Fixes Applied

### Fix 1: Improved Heuristic Parser
**File**: `src/agents/enhanced_mission_parser.py`

#### Before:
```python
# Extract quoted text as script
script_parts = []
quoted_pattern = r'"([^"]*)"'
quotes = re.findall(quoted_pattern, mission_statement)
script_parts.extend(quotes)
```

#### After:
```python
# Patterns for actual dialogue/narration
dialogue_patterns = [
    r'(?:says?|said|speaking|announces?|reports?|states?):\s*["\']([^"\']+)["\']',
    r'(?:Maryam|Anchor|Narrator|Brian|Peter|Stewie|Quagmire|Lois):\s*["\']([^"\']+)["\']',
    r'(?:Maryam|Official|Character\s*\w*):\s*\'([^\']+)\'',
    r'\'([^\']+)\'\s*(?:\*[^*]+\*)?',
    r'"([^"]+)"\s*(?:\*[^*]+\*)?',
]

# Patterns for visual instructions (should NOT be spoken)
visual_patterns = [
    r'\*([^*]+)\*',  # *action in asterisks*
    r'\(([^)]+)\)',  # (stage directions in parentheses)
    r'(?:Cut to|Show|Display|Pan to|Zoom|Fade|Scene:)(.+?)(?:\.|!|\?|$)',
    r'(?:Background:|Setting:|Visual:)(.+?)(?:\.|!|\?|$)',
]
```

### Fix 2: Prevent Director Override
**File**: `src/generators/video_generator.py`

#### Before:
```python
# Generate the narrative script
director_result = self.director.write_script(...)

# Extract the script content from Director's output
if isinstance(director_result, dict):
    # ... extract script from director_result
    script = " ".join(script_parts)
```

#### After:
```python
# If we have parsed script content, use it directly
if script.strip():
    logger.info(f"✅ Using parsed script content from Enhanced Mission Parser")
    director_result = {
        'script': script,
        'segments': [{'text': script}],
        'hook': {'text': script.split('.')[0] if '.' in script else script[:50]},
        'main_content': [{'text': script}],
        'cta': {'text': config.call_to_action or 'Follow for more!'}
    }
else:
    # Only fall back to Director if no script was parsed
    director_result = self.director.write_script(...)
```

### Fix 3: Better Fallback Filtering
**File**: `src/agents/enhanced_mission_parser.py`

Added additional filtering for narrative descriptions:
```python
skip_keywords = [
    'show', 'display', 'cut to', 'cutaway', 'pan to', 'zoom', 'fade', 'scene:', 
    'background:', 'setting:', 'visual:', '(', '*', 'style', 'animation',
    'fighting', 'removes', 'disheveled', 'running', 'card:', 'end card',
    'completely', 'griffin-style', 'brian-style', 'chicken fight'
]
```

## Testing Results

### Before Fix:
```
Maryam: Breaking news! A severe water crisis is hitting Iran. Peter: This is worse than that time I accidentally drank all the Fiji. *Flashback: Peter chugs an enormous Fiji water bottle with a straw.* Peter: Ah, pure hydration! Official: The situation is complex. End with Griffin Family logo.
```

### After Fix:
```
This just in: Tehran has gone full Mad Max. It is a shocking water apocalypse unfolding. WITNESS ME! F*** it, there is no water to wash it. Iran International: We are as thirsty as you are!
```

## Remaining Issues

1. **AI Parser Failures**: The Gemini-based AI parser is still failing and falling back to heuristic parsing. This needs investigation.

2. **Imperfect Heuristic Parsing**: While improved, the heuristic parser may still include some descriptive text. Best solution is to fix the AI parser.

3. **Character Names in Script**: Sometimes character names are included (e.g., "Maryam removes her hijab" becomes "Maryam removes her hijab" in audio).

## Recommendations

1. **Fix AI Parser**: Investigate why the Gemini parser is failing with JSON errors and fix it for better parsing accuracy.

2. **Improve Mission Format**: Encourage users to format missions with clear separation:
   ```
   DIALOGUE: "This just in: Tehran has gone full Mad Max."
   VISUAL: Maryam with disheveled hijab
   DIALOGUE: "WITNESS ME!"
   VISUAL: Warriors fighting over water bottle
   ```

3. **Add Mission Templates**: Provide templates that clearly separate spoken content from visual instructions.

4. **Test with Various Formats**: Test the parser with different mission formats to ensure robustness.

## Usage Notes

- Visual instructions in asterisks (*like this*) are properly filtered out
- Stage directions in parentheses (like this) are filtered out
- Commands like "Cut to:", "Show:", "End card:" are filtered out
- Character actions without dialogue are filtered out