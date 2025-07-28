"""
AI-Powered Content Analyzer
Replaces hardcoded patterns with intelligent AI analysis
"""
import json
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from ..utils.logging_config import get_logger
from ..config.ai_model_config import DEFAULT_AI_MODEL

logger = get_logger(__name__)

class ContentType(Enum):
    """Types of content detected by AI"""
    CREATIVE = "creative"
    MISSION = "mission"
    INFORMATIONAL = "informational"
    EDUCATIONAL = "educational"
    NEWS = "news"
    ENTERTAINMENT = "entertainment"
    COMMERCIAL = "commercial"
    UNKNOWN = "unknown"

class AIContentAnalyzer:
    """
    AI-driven content analyzer that replaces hardcoded pattern matching
    with intelligent analysis using AI models.
    """
    
    def __init__(self, api_key: str, model_name: str = None):
        """Initialize the AI content analyzer"""
        self.api_key = api_key
        self.model_name = model_name or DEFAULT_AI_MODEL
        
        # Initialize AI model
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"✅ AI Content Analyzer initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI model: {e}")
            self.model = None
    
    def analyze_content_type(self, content: str, context: Dict[str, Any] = None) -> Tuple[ContentType, Dict[str, Any]]:
        """
        Analyze content to determine its type and characteristics using AI
        
        Args:
            content: The content to analyze
            context: Additional context (platform, duration, etc.)
            
        Returns:
            Tuple of (ContentType, analysis_details)
        """
        if not self.model:
            logger.warning("AI model not available, using fallback")
            return ContentType.UNKNOWN, {"reason": "AI model unavailable"}
        
        try:
            analysis_prompt = f"""
Analyze the following content and determine its type and characteristics.

Content: "{content}"

Context:
{json.dumps(context or {}, indent=2)}

Provide a detailed analysis in JSON format:
{{
    "content_type": "creative|mission|informational|educational|news|entertainment|commercial",
    "is_action_oriented": true/false,
    "primary_purpose": "describe the main purpose",
    "target_audience": "describe the target audience",
    "tone": "describe the tone",
    "key_elements": ["list", "key", "elements"],
    "requires_visual_effects": true/false,
    "narrative_style": "first-person|third-person|documentary|etc",
    "persuasion_type": "emotional|logical|ethical|none",
    "call_to_action": "describe if any",
    "content_structure": "linear|episodic|circular|etc"
}}

Focus on understanding the intent and purpose, not just keywords.
"""
            
            response = self.model.generate_content(analysis_prompt)
            
            # Parse the response
            try:
                analysis = self._extract_json(response.text)
                content_type_str = analysis.get('content_type', 'unknown').upper()
                content_type = ContentType[content_type_str] if content_type_str in ContentType.__members__ else ContentType.UNKNOWN
                
                logger.info(f"📊 AI Analysis Complete: {content_type.value}")
                logger.info(f"   Purpose: {analysis.get('primary_purpose', 'Unknown')}")
                logger.info(f"   Action-oriented: {analysis.get('is_action_oriented', False)}")
                
                return content_type, analysis
                
            except Exception as e:
                logger.warning(f"Failed to parse AI response: {e}")
                return ContentType.UNKNOWN, {"error": str(e)}
                
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return ContentType.UNKNOWN, {"error": str(e)}
    
    def analyze_visual_elements(self, script: str) -> Dict[str, List[str]]:
        """
        Analyze script to identify visual vs dialogue elements using AI
        
        Returns:
            Dictionary with 'visual' and 'dialogue' lists
        """
        if not self.model:
            return {"visual": [], "dialogue": [script]}
        
        try:
            prompt = f"""
Analyze this script and separate visual descriptions from spoken dialogue.

Script: "{script}"

Rules:
1. Visual elements include: stage directions, scene descriptions, actions, effects
2. Dialogue includes: anything that should be spoken aloud
3. Use the tagging format: [VISUAL: description] for visual elements
4. Use the tagging format: DIALOGUE: text for spoken content

Return JSON:
{{
    "segments": [
        {{
            "type": "visual|dialogue",
            "content": "the content",
            "duration_estimate": seconds
        }}
    ]
}}
"""
            
            response = self.model.generate_content(prompt)
            result = self._extract_json(response.text)
            
            visual_elements = []
            dialogue_elements = []
            
            for segment in result.get('segments', []):
                if segment['type'] == 'visual':
                    visual_elements.append(segment['content'])
                else:
                    dialogue_elements.append(segment['content'])
            
            return {
                "visual": visual_elements,
                "dialogue": dialogue_elements
            }
            
        except Exception as e:
            logger.error(f"Visual analysis failed: {e}")
            return {"visual": [], "dialogue": [script]}
    
    def detect_language_intent(self, text: str) -> Dict[str, Any]:
        """
        Detect language and writing system using AI instead of character ranges
        """
        if not self.model:
            return {"language": "unknown", "is_rtl": False}
        
        try:
            prompt = f"""
Analyze the language and writing system of this text:

Text: "{text}"

Return JSON:
{{
    "primary_language": "language name",
    "language_code": "ISO code",
    "is_rtl": true/false,
    "script_type": "latin|arabic|hebrew|cyrillic|etc",
    "confidence": 0.0-1.0
}}
"""
            
            response = self.model.generate_content(prompt)
            return self._extract_json(response.text)
            
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return {"language": "unknown", "is_rtl": False}
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from AI response"""
        import re
        
        # Find JSON in response
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        # Fallback
        return {}
    
    def get_content_recommendations(self, content_type: ContentType, 
                                   platform: str = None, 
                                   duration: int = None) -> Dict[str, Any]:
        """
        Get AI recommendations for content based on type and platform
        """
        if not self.model:
            return {}
        
        try:
            prompt = f"""
Provide content creation recommendations for:

Content Type: {content_type.value}
Platform: {platform or 'general'}
Duration: {duration or 'flexible'} seconds

Return JSON with recommendations:
{{
    "pacing": "recommended pacing style",
    "visual_style": "recommended visual approach",
    "audio_style": "recommended audio approach",
    "engagement_techniques": ["list", "of", "techniques"],
    "structure_suggestion": "how to structure the content",
    "platform_optimizations": ["platform", "specific", "tips"]
}}
"""
            
            response = self.model.generate_content(prompt)
            return self._extract_json(response.text)
            
        except Exception as e:
            logger.error(f"Failed to get recommendations: {e}")
            return {}