"""
Enhanced Mission Parser - Properly separates script from visual instructions
Uses Gemini 2.5 Pro to intelligently parse missions
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import json
import re
import asyncio

from ..utils.logging_config import get_logger
from ..ai.manager import AIServiceManager
from ..ai.interfaces.text_generation import TextGenerationRequest
from ..models.video_models import Platform, VideoCategory

logger = get_logger(__name__)


@dataclass
class ParsedMission:
    """Parsed mission with separated components"""
    original_mission: str
    script_content: str  # What should be spoken/narrated
    visual_instructions: List[str]  # Visual elements to show
    character_descriptions: Dict[str, str]  # Character name -> description
    scene_descriptions: List[str]  # Scene/setting descriptions
    style_notes: str  # Animation/visual style notes
    special_effects: List[str]  # Special effects, overlays, etc.
    is_satirical: bool  # Whether this is comedy/satire
    mission_type: str  # The actual type of content
    parsing_confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "original_mission": self.original_mission,
            "script_content": self.script_content,
            "visual_instructions": self.visual_instructions,
            "character_descriptions": self.character_descriptions,
            "scene_descriptions": self.scene_descriptions,
            "style_notes": self.style_notes,
            "special_effects": self.special_effects,
            "is_satirical": self.is_satirical,
            "mission_type": self.mission_type,
            "parsing_confidence": self.parsing_confidence
        }


class EnhancedMissionParser:
    """
    Enhanced mission parser that properly separates script from visual instructions
    Uses Gemini 2.5 Pro for intelligent parsing
    """
    
    def __init__(self, ai_manager: AIServiceManager = None, model_name: str = "gemini-2.5-pro", api_key: str = None):
        """Initialize Enhanced Mission Parser"""
        self.ai_manager = ai_manager
        self.model_name = model_name
        self.api_key = api_key
        
        # Initialize Gemini client if no AI manager
        if not self.ai_manager and self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.gemini_model = genai.GenerativeModel(model_name)
                logger.info(f"🎯 Enhanced Mission Parser initialized with direct Gemini client ({model_name})")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize Gemini client: {e}")
                self.gemini_model = None
        else:
            self.gemini_model = None
            
        logger.info(f"🎯 Enhanced Mission Parser initialized with {model_name}")
    
    async def parse_mission(self, 
                          mission_statement: str,
                          platform: Optional[Platform] = None,
                          flags: Dict[str, Any] = None) -> ParsedMission:
        """
        Parse mission statement into components
        
        Args:
            mission_statement: The full mission text
            platform: Target platform
            flags: CLI flags (character, scene, style, etc.)
            
        Returns:
            ParsedMission with separated components
        """
        try:
            logger.info(f"🎯 Parsing mission with Enhanced Parser: {mission_statement[:100]}...")
            
            # Build context from flags
            flag_context = self._build_flag_context(flags) if flags else ""
            
            # Create comprehensive parsing prompt
            prompt = f"""
You are an expert video content parser. Your task is to analyze this mission statement and separate it into distinct components.

MISSION STATEMENT:
"{mission_statement}"

ADDITIONAL CONTEXT FROM FLAGS:
{flag_context}

Your goal is to intelligently separate:
1. SCRIPT CONTENT: What should actually be spoken/narrated (the dialogue, narration)
2. VISUAL INSTRUCTIONS: What should be shown visually (not spoken)
3. CHARACTER DESCRIPTIONS: Descriptions of characters and their appearance
4. SCENE DESCRIPTIONS: Settings, backgrounds, environments
5. STYLE NOTES: Animation style, visual style (e.g., "Family Guy style")
6. SPECIAL EFFECTS: Overlays, tickers, logos, special visual effects

IMPORTANT PARSING RULES:
- Script content should ONLY include what is meant to be spoken/narrated
- Do NOT include visual descriptions in the script (e.g., "Show cartoon map" should be in visual_instructions, not script)
- Character descriptions should be extracted (e.g., "Maryam with big eyes, hijab")
- Recognize satirical/comedy content (e.g., Family Guy style = satirical)
- If something is in quotes, it's likely dialogue for the script
- Visual actions like "show", "display", "cut to" belong in visual_instructions

Analyze the mission and return a JSON response:
{{
    "script_content": "The actual dialogue/narration to be spoken",
    "visual_instructions": [
        "Visual instruction 1",
        "Visual instruction 2"
    ],
    "character_descriptions": {{
        "character_name": "description"
    }},
    "scene_descriptions": [
        "Scene description 1",
        "Scene description 2"
    ],
    "style_notes": "Overall visual/animation style",
    "special_effects": [
        "Special effect 1 (logos, tickers, overlays)",
        "Special effect 2"
    ],
    "is_satirical": true/false,
    "mission_type": "news_parody|educational|informational|etc",
    "parsing_confidence": 0.0-1.0,
    "parsing_notes": "Brief explanation of parsing decisions"
}}

Example parsing:
Input: "Family Guy style animated news. Nuclear News logo. Anchor says: 'Breaking news!' Show map with fleeing water."
Output:
{{
    "script_content": "Breaking news!",
    "visual_instructions": ["Show map with fleeing water"],
    "character_descriptions": {{"Anchor": "News anchor"}},
    "scene_descriptions": ["Animated news studio"],
    "style_notes": "Family Guy style animation",
    "special_effects": ["Nuclear News logo"],
    "is_satirical": true,
    "mission_type": "news_parody",
    "parsing_confidence": 0.95
}}
"""
            
            # Use AI service manager or direct Gemini for generation
            response_text = None
            
            if self.ai_manager:
                text_service = self.ai_manager.get_text_service()
                request = TextGenerationRequest(
                    prompt=prompt,
                    temperature=0.3,
                    max_tokens=2000,
                    model=self.model_name  # Use Gemini 2.5 Pro
                )
                response = await text_service.generate(request)
                response_text = response.text
            elif self.gemini_model:
                # Use direct Gemini client
                try:
                    logger.info("🤖 Using direct Gemini client for parsing")
                    response = await asyncio.to_thread(
                        self.gemini_model.generate_content,
                        prompt,
                        generation_config={
                            "temperature": 0.3,
                            "max_output_tokens": 2000,
                        }
                    )
                    response_text = response.text
                    logger.info(f"✅ Gemini response received: {len(response_text)} chars")
                except Exception as e:
                    logger.warning(f"⚠️ Gemini generation failed: {e}")
                    import traceback
                    logger.debug(f"Traceback: {traceback.format_exc()}")
            
            if response_text:
                # Parse response
                parsed = self._parse_ai_response(response_text)
                if parsed:
                    # Create ParsedMission object
                    return ParsedMission(
                        original_mission=mission_statement,
                        script_content=parsed.get('script_content', ''),
                        visual_instructions=parsed.get('visual_instructions', []),
                        character_descriptions=parsed.get('character_descriptions', {}),
                        scene_descriptions=parsed.get('scene_descriptions', []),
                        style_notes=parsed.get('style_notes', ''),
                        special_effects=parsed.get('special_effects', []),
                        is_satirical=parsed.get('is_satirical', False),
                        mission_type=parsed.get('mission_type', 'general'),
                        parsing_confidence=parsed.get('parsing_confidence', 0.8)
                    )
            
            # Fallback to heuristic parsing
            return self._heuristic_parse(mission_statement, flags)
            
        except Exception as e:
            logger.error(f"❌ Enhanced mission parsing failed: {e}")
            return self._create_fallback_parse(mission_statement)
    
    def _parse_ai_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Parse AI response into structured data"""
        try:
            logger.debug(f"🔍 Parsing AI response: {response_text[:200]}...")
            
            # Remove markdown code blocks if present
            text = response_text
            text = re.sub(r'```json\s*', '', text)
            text = re.sub(r'```\s*', '', text)
            
            # Find JSON in response
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                raw_json = json_match.group()
                logger.debug(f"📋 Found JSON: {raw_json[:200]}...")
                result = json.loads(raw_json)
                
                logger.info(f"✅ Successfully parsed mission:")
                logger.info(f"   Script length: {len(result.get('script_content', ''))} chars")
                logger.info(f"   Visual instructions: {len(result.get('visual_instructions', []))} items")
                logger.info(f"   Characters: {len(result.get('character_descriptions', {}))} defined")
                logger.info(f"   Is satirical: {result.get('is_satirical', False)}")
                logger.info(f"   Mission type: {result.get('mission_type', 'unknown')}")
                
                return result
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to parse AI response: {e}")
        
        return None
    
    def _heuristic_parse(self, mission_statement: str, flags: Optional[Dict[str, Any]] = None) -> ParsedMission:
        """Fallback heuristic parsing with better separation of dialogue vs instructions"""
        logger.info("📝 Using heuristic parsing as fallback")
        
        # Patterns for actual dialogue/narration
        dialogue_patterns = [
            r'(?:says?|said|speaking|announces?|reports?|states?):\s*["\']([^"\']+)["\']',  # Character says: "..."
            r'(?:Maryam|Anchor|Narrator|Brian|Peter|Stewie|Quagmire|Lois):\s*["\']([^"\']+)["\']',  # Character: "..."
            r'(?:Maryam|Official|Character\s*\w*):\s*\'([^\']+)\'',  # Character: 'dialogue'
            r'\'([^\']+)\'\s*(?:\*[^*]+\*)?',  # 'Dialogue' with optional action
            r'"([^"]+)"\s*(?:\*[^*]+\*)?',  # "Dialogue" with optional action
        ]
        
        # Patterns for visual instructions (should NOT be spoken)
        visual_patterns = [
            r'\*([^*]+)\*',  # *action in asterisks*
            r'\(([^)]+)\)',  # (stage directions in parentheses)
            r'(?:Cut to|Show|Display|Pan to|Zoom|Fade|Scene:)(.+?)(?:\.|!|\?|$)',  # Visual commands
            r'(?:Background:|Setting:|Visual:)(.+?)(?:\.|!|\?|$)',  # Visual descriptions
        ]
        
        script_parts = []
        visual_instructions = []
        
        # First, extract clear dialogue patterns
        for pattern in dialogue_patterns:
            matches = re.findall(pattern, mission_statement, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                clean_text = match.strip()
                if clean_text and len(clean_text) > 3:  # Avoid tiny fragments
                    script_parts.append(clean_text)
        
        # Extract visual instructions
        for pattern in visual_patterns:
            matches = re.findall(pattern, mission_statement, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                clean_text = match.strip()
                if clean_text:
                    visual_instructions.append(clean_text)
        
        # Detect style
        style_notes = ""
        if "family guy" in mission_statement.lower():
            style_notes = "Family Guy animation style"
        elif "marvel" in mission_statement.lower():
            style_notes = "Marvel Comics style"
        elif "anime" in mission_statement.lower():
            style_notes = "Anime style"
        
        # Detect if satirical
        is_satirical = any(word in mission_statement.lower() for word in 
                          ['family guy', 'parody', 'satire', 'comedy', 'funny'])
        
        # If no clear script parts found, try to extract narrative content more carefully
        if not script_parts:
            # Split by sentences and look for narrative content
            sentences = re.split(r'[.!?]+', mission_statement)
            for sentence in sentences:
                sentence = sentence.strip()
                # Skip sentences that are clearly visual instructions or descriptions
                skip_keywords = [
                    'show', 'display', 'cut to', 'cutaway', 'pan to', 'zoom', 'fade', 'scene:', 
                    'background:', 'setting:', 'visual:', '(', '*', 'style', 'animation',
                    'fighting', 'removes', 'disheveled', 'running', 'card:', 'end card',
                    'completely', 'griffin-style', 'brian-style', 'chicken fight'
                ]
                if not any(keyword in sentence.lower() for keyword in skip_keywords):
                    # Check if it contains actual narrative content
                    if len(sentence) > 10 and not sentence.endswith(':'):
                        # Additional check - skip if it's describing an action without dialogue
                        if not re.match(r'^[A-Z]\w+\s+(is|are|does|fights|removes|shows)', sentence):
                            script_parts.append(sentence)
        
        # Clean up script parts - remove duplicates and character names
        unique_script_parts = []
        for part in script_parts:
            # Remove character names from dialogue
            # Pattern: "Character: dialogue" -> "dialogue"
            cleaned_part = re.sub(r'^[A-Z][a-zA-Z\s]*:\s*', '', part)
            if cleaned_part and cleaned_part not in unique_script_parts:
                unique_script_parts.append(cleaned_part)
        
        final_script = '. '.join(unique_script_parts) if unique_script_parts else ""
        
        # Log what we extracted
        logger.info(f"📝 Heuristic parsing results:")
        logger.info(f"   Script parts found: {len(unique_script_parts)}")
        logger.info(f"   Visual instructions: {len(visual_instructions)}")
        logger.info(f"   Script preview: {final_script[:100]}..." if final_script else "   No script content extracted")
        
        return ParsedMission(
            original_mission=mission_statement,
            script_content=final_script,
            visual_instructions=visual_instructions,
            character_descriptions=flags.get('character', {}) if flags else {},
            scene_descriptions=[flags.get('scene', '')] if flags and flags.get('scene') else [],
            style_notes=style_notes or (flags.get('visual_style', '') if flags else ''),
            special_effects=[],
            is_satirical=is_satirical,
            mission_type='news_parody' if is_satirical else 'general',
            parsing_confidence=0.6
        )
    
    def _build_flag_context(self, flags: Dict[str, Any]) -> str:
        """Build context from CLI flags"""
        context_parts = []
        
        if flags.get('character'):
            context_parts.append(f"Character: {flags['character']}")
        if flags.get('scene'):
            context_parts.append(f"Scene: {flags['scene']}")
        if flags.get('visual_style'):
            context_parts.append(f"Visual Style: {flags['visual_style']}")
        if flags.get('theme'):
            context_parts.append(f"Theme: {flags['theme']}")
        if flags.get('style'):
            context_parts.append(f"Style: {flags['style']}")
        
        return '\n'.join(context_parts) if context_parts else "No additional context provided"
    
    def _create_fallback_parse(self, mission_statement: str) -> ParsedMission:
        """Create minimal fallback parse"""
        return ParsedMission(
            original_mission=mission_statement,
            script_content=mission_statement,  # Use full mission as script
            visual_instructions=[],
            character_descriptions={},
            scene_descriptions=[],
            style_notes="",
            special_effects=[],
            is_satirical=False,
            mission_type='general',
            parsing_confidence=0.3
        )