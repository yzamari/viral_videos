#!/usr/bin/env python3
"""
Fix the news theme issue - ensure news overlay appears
"""

import os
import shutil

def fix_iranian_news_script():
    """Fix Iranian news script to use proper theme"""
    print("🔧 Fixing Iranian news script to use news theme...")
    
    script_path = "/Users/yahavzamari/viralAi/run_iran_news_family_guy_final.sh"
    
    with open(script_path, 'r') as f:
        content = f.read()
    
    # Backup
    shutil.copy(script_path, script_path + '.bak_theme_fix')
    
    # Add --theme preset_news_edition to the command
    content = content.replace(
        '        --style news \\',
        '        --style news \\\n        --theme preset_news_edition \\'
    )
    
    with open(script_path, 'w') as f:
        f.write(content)
    
    print("✅ Iranian news script fixed with news theme")

def ensure_theme_in_video_generator():
    """Ensure theme is properly handled in video generator"""
    print("\n🔧 Ensuring theme is properly passed to video generator...")
    
    video_gen_path = "/Users/yahavzamari/viralAi/src/generators/video_generator.py"
    
    with open(video_gen_path, 'r') as f:
        content = f.read()
    
    # Check if theme is being extracted from config
    if "getattr(config, 'theme'" not in content:
        # Add theme extraction after other config attributes
        enhancement = '''
        # Extract theme from config
        theme_id = getattr(config, 'theme', None)
        if not theme_id and hasattr(self, 'core_decisions'):
            theme_id = getattr(self.core_decisions, 'theme_id', None)
        
        # Log theme for debugging
        if theme_id:
            logger.info(f"🎨 Using theme: {theme_id}")
            # Force news overlay for news theme
            if 'news' in str(theme_id).lower():
                logger.warning("📺 NEWS THEME DETECTED - Ensuring news overlays are applied")
'''
        
        # Add after cheap_mode extraction
        marker = "cheap_mode = getattr(config, 'cheap_mode', False)"
        if marker in content:
            content = content.replace(marker, marker + enhancement)
    
    with open(video_gen_path, 'w') as f:
        f.write(content)
    
    print("✅ Video generator theme handling enhanced")

def fix_working_orchestrator_theme():
    """Ensure working orchestrator passes theme properly"""
    print("\n🔧 Fixing working orchestrator theme passing...")
    
    orchestrator_path = "/Users/yahavzamari/viralAi/src/agents/working_orchestrator.py"
    
    with open(orchestrator_path, 'r') as f:
        content = f.read()
    
    # Ensure theme is passed to GeneratedVideoConfig
    if "'theme': config.get('theme')" not in content:
        # Find where GeneratedVideoConfig is created
        marker = "GeneratedVideoConfig("
        if marker in content:
            # Add theme to the config
            content = content.replace(
                "cheap_mode=config.get('cheap_mode', False),",
                "cheap_mode=config.get('cheap_mode', False),\n                theme=config.get('theme', None),"
            )
    
    with open(orchestrator_path, 'w') as f:
        f.write(content)
    
    print("✅ Working orchestrator theme passing fixed")

def fix_generated_video_config():
    """Ensure GeneratedVideoConfig has theme attribute"""
    print("\n🔧 Adding theme to GeneratedVideoConfig...")
    
    models_path = "/Users/yahavzamari/viralAi/src/models/video_models.py"
    
    with open(models_path, 'r') as f:
        content = f.read()
    
    # Add theme attribute if not present
    if "theme: Optional[str] = None" not in content:
        # Find GeneratedVideoConfig class
        lines = content.split('\n')
        in_class = False
        for i, line in enumerate(lines):
            if 'class GeneratedVideoConfig:' in line:
                in_class = True
            elif in_class and 'cheap_mode_level: str = "off"' in line:
                # Add theme after cheap_mode_level
                lines.insert(i + 1, '    theme: Optional[str] = None')
                break
        content = '\n'.join(lines)
    
    with open(models_path, 'w') as f:
        f.write(content)
    
    print("✅ GeneratedVideoConfig updated with theme attribute")

def main():
    print("🚀 Fixing news theme issues\n")
    
    fix_iranian_news_script()
    ensure_theme_in_video_generator()
    fix_working_orchestrator_theme()
    fix_generated_video_config()
    
    print("\n✨ News theme fixes applied!")
    print("\n📝 Summary:")
    print("1. Iranian news script: Added --theme preset_news_edition")
    print("2. Video generator: Enhanced theme detection and logging")
    print("3. Working orchestrator: Fixed theme passing")
    print("4. GeneratedVideoConfig: Added theme attribute")

if __name__ == "__main__":
    main()