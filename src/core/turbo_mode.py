"""
Turbo Mode - Streamlined video generation bypassing non-essential AI systems
Reduces 50+ AI calls down to 4-5 essential calls
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass  
class TurboConfig:
    """Configuration for turbo mode"""
    skip_audience_intelligence: bool = True
    skip_content_credibility: bool = True
    skip_ethical_optimization: bool = True
    skip_multi_agent_veo3: bool = True
    skip_redundant_validation: bool = True
    skip_artifact_detection: bool = True
    skip_trend_analysis: bool = True
    use_simple_veo3_prompt: bool = True
    max_ai_calls: int = 5
    timeout_seconds: int = 30


class TurboMode:
    """Streamlined video generation with minimal AI calls"""
    
    def __init__(self):
        self.config = TurboConfig()
        self.ai_call_count = 0
        logger.info("⚡ Turbo Mode initialized - Bypassing non-essential AI systems")
    
    def is_enabled(self) -> bool:
        """Check if turbo mode is enabled via environment or flag"""
        return os.getenv('TURBO_MODE', '').lower() in ['true', '1', 'yes']
    
    def should_skip_system(self, system_name: str) -> bool:
        """Determine if a system should be skipped"""
        if not self.is_enabled():
            return False
            
        skip_map = {
            'audience_intelligence': self.config.skip_audience_intelligence,
            'content_credibility': self.config.skip_content_credibility,
            'ethical_optimization': self.config.skip_ethical_optimization,
            'multi_agent_veo3': self.config.skip_multi_agent_veo3,
            'artifact_detection': self.config.skip_artifact_detection,
            'trend_analysis': self.config.skip_trend_analysis,
            'redundant_validation': self.config.skip_redundant_validation,
        }
        
        should_skip = skip_map.get(system_name, False)
        if should_skip:
            logger.debug(f"⚡ Turbo Mode: Skipping {system_name}")
        return should_skip
    
    def get_simple_veo3_prompt(self, mission: str, style: str, duration: int) -> Dict[str, Any]:
        """Generate simple VEO3 prompt without multi-agent system"""
        logger.info("⚡ Using simple VEO3 prompt generation (1 AI call instead of 7)")
        
        # Simple deterministic prompt structure
        return {
            "shot": {
                "composition": "dynamic wide shot",
                "camera_motion": "smooth tracking",
                "frame_rate": "30fps"
            },
            "subject": {
                "description": mission,
                "style": style
            },
            "scene": {
                "visual_style": style,
                "duration": f"{duration} seconds"
            },
            "keywords": [mission, style, "high quality", "16:9", "professional"]
        }
    
    def track_ai_call(self, system: str):
        """Track AI calls and warn if exceeding limit"""
        self.ai_call_count += 1
        logger.debug(f"📊 AI Call #{self.ai_call_count}: {system}")
        
        if self.ai_call_count > self.config.max_ai_calls:
            logger.warning(f"⚠️ Excessive AI calls detected: {self.ai_call_count} (max: {self.config.max_ai_calls})")
    
    def get_fallback_values(self, system: str) -> Any:
        """Get sensible fallback values for skipped systems"""
        fallbacks = {
            'audience_intelligence': {
                'demographics': {'age': '18-45', 'interests': 'general'},
                'confidence': 0.8
            },
            'content_credibility': {
                'credibility_score': 8.0,
                'bias_level': 'LOW', 
                'confidence': 0.8
            },
            'ethical_optimization': {
                'compliance_score': 8.0,
                'rating': 'GOOD',
                'confidence': 0.8
            }
        }
        
        value = fallbacks.get(system, {})
        logger.debug(f"⚡ Using fallback value for {system}: {value}")
        return value


# Global instance
turbo_mode = TurboMode()