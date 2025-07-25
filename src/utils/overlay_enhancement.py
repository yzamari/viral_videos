"""
Overlay Enhancement Module - AI-driven overlay generation with subtitle avoidance
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class OverlayEnhancer:
    """Enhances video overlay generation with AI-driven decisions and subtitle avoidance"""
    
    def __init__(self):
        self.subtitle_area_positions = ['bottom_center', 'bottom_left', 'bottom_right', 'bottom_third', 'center_bottom']
        self.safe_positions = ['top_center', 'top_left', 'top_right', 'center_left', 'center_right']
        
    def enhance_overlay_generation(self, 
                                 positioning_agent,
                                 config: Any,
                                 video_duration: float,
                                 video_width: int,
                                 video_height: int) -> List[Dict[str, Any]]:
        """Generate enhanced overlays with AI-driven colorful hooks"""
        
        all_overlays = []
        
        # First, try to get colorful hooks from AI
        try:
            logger.info("🎨 Generating AI-driven colorful text hooks")
            colorful_hooks = positioning_agent.create_colorful_text_hooks(
                topic=config.mission,
                platform=str(config.platform),
                video_duration=video_duration,
                script_content=getattr(config, 'processed_script', "")
            )
            
            # Filter and reposition hooks to avoid subtitle area
            for i, hook in enumerate(colorful_hooks):
                if hook.get('position', 'center') in self.subtitle_area_positions:
                    # Reassign to a safe position
                    hook['position'] = self.safe_positions[i % len(self.safe_positions)]
                    hook['reasoning'] = hook.get('reasoning', '') + ' (Repositioned to avoid subtitles)'
                
                all_overlays.append(hook)
            
            logger.info(f"✅ Added {len(colorful_hooks)} AI-generated colorful hooks")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not generate colorful hooks: {e}")
        
        return all_overlays
    
    def adjust_positions_for_subtitles(self, positions: Dict[str, str], video_height: int) -> Dict[str, str]:
        """Adjust overlay positions to avoid subtitle area (bottom 30% of screen)"""
        
        return {
            "top_center": f"(w-text_w)/2:20",
            "top_left": "20:20",
            "top_right": "w-text_w-20:20",
            "center": f"(w-text_w)/2:(h-text_h)/2",
            "center_left": f"20:(h-text_h)/2",
            "center_right": f"w-text_w-20:(h-text_h)/2",
            # Bottom positions moved higher to avoid subtitle area
            "bottom_center": f"(w-text_w)/2:h*0.6-text_h",  # 60% down, above subtitles
            "bottom_left": "20:h*0.6-text_h",
            "bottom_right": "w-text_w-20:h*0.6-text_h",
            "bottom_third": f"(w-text_w)/2:h*0.55-text_h",  # 55% down
            "center_bottom": f"(w-text_w)/2:h*0.65-text_h"  # 65% down
        }
    
    def remove_overlapping_overlays(self, overlays: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove overlapping overlays at the same position"""
        
        # Sort by start time
        overlays.sort(key=lambda x: x.get('start_time', 0))
        
        non_overlapping = []
        for overlay in overlays:
            # Check if this overlay overlaps with any existing ones at same position
            overlaps = False
            for existing in non_overlapping:
                if (overlay.get('start_time', 0) < existing.get('end_time', 0) and 
                    overlay.get('end_time', 0) > existing.get('start_time', 0) and
                    overlay.get('position') == existing.get('position')):
                    overlaps = True
                    break
            
            if not overlaps:
                non_overlapping.append(overlay)
        
        return non_overlapping
    
    def calculate_safe_y_position(self, position: str, video_height: int, avoid_subtitles: bool = True) -> int:
        """Calculate Y position for overlays that avoids subtitle area"""
        
        if avoid_subtitles:
            # Subtitle area is typically bottom 30% of screen
            subtitle_top = int(video_height * 0.7)
            
            if position in self.subtitle_area_positions:
                # Move overlay above subtitle area
                return subtitle_top - 100  # 100 pixels above subtitle area
        
        # Default positions
        position_map = {
            'top': 50,
            'center': video_height // 2,
            'bottom': video_height - 100  # If not avoiding subtitles
        }
        
        for key in position_map:
            if key in position:
                return position_map[key]
        
        return 50  # Default to top