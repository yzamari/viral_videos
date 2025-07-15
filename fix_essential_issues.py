#!/usr/bin/env python3
"""
Fix only the essential issues to get the system working
"""

import os
import re

def fix_essential_issues():
    """Fix only the critical issues that prevent the system from working"""
    file_path = "src/generators/video_generator.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix 1: Language enum value
    content = content.replace("Language.EN_US", "Language.ENGLISH_US")
    
    # Fix 2: Script result keys
    content = content.replace(
        "result.get('final_script', '')",
        "result.get('optimized_script', '')"
    )
    
    content = content.replace(
        "result.get('word_count', 0)",
        "result.get('total_word_count', 0)"
    )
    
    content = content.replace(
        "result.get('estimated_duration', 0)",
        "result.get('total_estimated_duration', 0)"
    )
    
    # Fix 3: VEO client parameter (if not already fixed)
    content = content.replace(
        "duration_seconds=int(clip_duration),",
        "duration=int(clip_duration),"
    )
    
    # Fix 4: Add fps to write_videofile calls
    content = re.sub(
        r'write_videofile\(([^)]+)\)',
        lambda m: f'write_videofile({m.group(1)}, fps=24)' if 'fps=' not in m.group(1) else m.group(0),
        content
    )
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Applied essential fixes")

if __name__ == '__main__':
    print("🔧 Applying essential fixes...")
    fix_essential_issues()
    print("🎉 Essential fixes applied!") 