"""
Dynamic Theme Text Service
Populates theme text fields dynamically based on mission context
"""

from typing import Dict, Any
from ...config.dynamic_content_config import DynamicContentConfig


class DynamicThemeTextService:
    """Service to populate theme text fields dynamically"""
    
    @staticmethod
    def populate_theme_text(theme_data: Dict[str, Any], mission: str, 
                          platform: str, tone: str) -> Dict[str, Any]:
        """Populate theme text fields dynamically based on mission context"""
        
        # Update intro template text if empty
        if hasattr(theme_data, 'intro_template') and theme_data.intro_template:
            if not theme_data.intro_template.title_text:
                theme_data.intro_template.title_text = DynamicContentConfig.generate_theme_text(
                    mission, platform, tone, "title"
                )
            
            if not theme_data.intro_template.subtitle_text:
                theme_data.intro_template.subtitle_text = DynamicContentConfig.generate_theme_text(
                    mission, platform, tone, "subtitle"
                )
        
        # Update outro template text if empty
        if hasattr(theme_data, 'outro_template') and theme_data.outro_template:
            if not theme_data.outro_template.title_text:
                theme_data.outro_template.title_text = DynamicContentConfig.generate_theme_text(
                    mission, platform, tone, "title"
                )
            
            if not theme_data.outro_template.subtitle_text:
                theme_data.outro_template.subtitle_text = DynamicContentConfig.generate_theme_text(
                    mission, platform, tone, "subtitle"
                )
        
        return theme_data
    
    @staticmethod
    def apply_dynamic_text_to_dict(theme_dict: Dict[str, Any], mission: str,
                                 platform: str, tone: str) -> Dict[str, Any]:
        """Apply dynamic text to theme dictionary structure"""
        
        # Update intro template if exists
        if 'intro_template' in theme_dict and theme_dict['intro_template']:
            intro = theme_dict['intro_template']
            if not intro.get('title_text'):
                intro['title_text'] = DynamicContentConfig.generate_theme_text(
                    mission, platform, tone, "title"
                )
            
            if not intro.get('subtitle_text'):
                intro['subtitle_text'] = DynamicContentConfig.generate_theme_text(
                    mission, platform, tone, "subtitle"
                )
        
        # Update outro template if exists
        if 'outro_template' in theme_dict and theme_dict['outro_template']:
            outro = theme_dict['outro_template']
            if not outro.get('title_text'):
                outro['title_text'] = DynamicContentConfig.generate_theme_text(
                    mission, platform, tone, "title"
                )
            
            if not outro.get('subtitle_text'):
                outro['subtitle_text'] = DynamicContentConfig.generate_theme_text(
                    mission, platform, tone, "subtitle"
                )
        
        return theme_dict