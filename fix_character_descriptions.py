#!/usr/bin/env python3
"""
Fix character descriptions to ensure historical accuracy
"""

import os
import shutil

def enhance_character_extraction():
    """Enhance character extraction to be more specific for historical figures"""
    print("🔧 Enhancing character descriptions for historical accuracy...")
    
    # Fix in decision_framework.py
    decision_path = "/Users/yahavzamari/viralAi/src/core/decision_framework.py"
    
    with open(decision_path, 'r') as f:
        content = f.read()
    
    # Backup
    shutil.copy(decision_path, decision_path + '.bak_character_fix')
    
    # Find the _extract_character_description method and enhance it
    enhanced_method = '''    def _extract_character_description(self, mission_text: str) -> str:
        """Extract character description from mission text"""
        # Historical figure database for accurate representation
        historical_figures = {
            'david ben-gurion': 'Elderly man with distinctive wild white hair flowing outward, round face, strong jawline, wearing simple khaki shirt, Israeli founding father appearance',
            'ben-gurion': 'Elderly man with distinctive wild white hair flowing outward, round face, strong jawline, wearing simple khaki shirt, Israeli founding father appearance',
            'moshe sharett': 'Middle-aged man with completely bald head, round wire-rimmed glasses, formal suit, diplomatic appearance, thoughtful expression',
            'sharett': 'Middle-aged man with completely bald head, round wire-rimmed glasses, formal suit, diplomatic appearance, thoughtful expression',
            'yitzhak shamir': 'Short elderly man with thick eyebrows, balding with side hair, stern expression, penetrating eyes, formal suit',
            'shamir': 'Short elderly man with thick eyebrows, balding with side hair, stern expression, penetrating eyes, formal suit',
            'benjamin netanyahu': 'Middle-aged man with gray hair, strong features, business suit, confident expression, Israeli political leader appearance',
            'netanyahu': 'Middle-aged man with gray hair, strong features, business suit, confident expression, Israeli political leader appearance',
            'golda meir': 'Elderly woman with gray hair in a bun, strong facial features, modest dress, grandmotherly but powerful presence',
            'meir': 'Elderly woman with gray hair in a bun, strong facial features, modest dress, grandmotherly but powerful presence'
        }
        
        # Check for historical figures first
        mission_lower = mission_text.lower()
        for name, description in historical_figures.items():
            if name in mission_lower:
                self.logger.info(f"🎭 Found historical figure: {name}")
                return description
        
        # Extract character ethnicity if mentioned
        ethnicity = self._extract_character_ethnicity(mission_text)
        
        # Original extraction logic
        patterns = [
            r"character[:\s]+([^.]+)",
            r"protagonist[:\s]+([^.]+)",
            r"main character[:\s]+([^.]+)",
            r"featuring[:\s]+([^.]+)",
            r"stars[:\s]+([^.]+)",
            r"follows?[:\s]+([^.]+)",
        ]
        
        import re
        for pattern in patterns:
            match = re.search(pattern, mission_text, re.IGNORECASE)
            if match:
                character_desc = match.group(1).strip()
                if ethnicity and ethnicity not in character_desc:
                    character_desc = f"{character_desc}, {ethnicity}"
                return character_desc
        
        # Fallback with ethnicity
        if ethnicity:
            return f"A person with {ethnicity}"
        
        return ""'''
    
    # Replace the existing method
    lines = content.split('\n')
    in_method = False
    method_start = -1
    method_indent = 0
    
    for i, line in enumerate(lines):
        if 'def _extract_character_description' in line:
            in_method = True
            method_start = i
            method_indent = len(line) - len(line.lstrip())
        elif in_method and line.strip() and len(line) - len(line.lstrip()) <= method_indent:
            # End of method found
            # Replace the entire method
            lines[method_start:i] = enhanced_method.split('\n')
            break
    
    content = '\n'.join(lines)
    
    with open(decision_path, 'w') as f:
        f.write(content)
    
    print("✅ Enhanced character extraction with historical figure database")

def fix_director_prompts():
    """Ensure Director uses accurate character descriptions"""
    print("\n🔧 Fixing Director to emphasize character accuracy...")
    
    director_path = "/Users/yahavzamari/viralAi/src/generators/director.py"
    
    with open(director_path, 'r') as f:
        content = f.read()
    
    # Add character accuracy emphasis
    enhancement = '''
        # Ensure historical accuracy for real people
        if character_description and any(name in character_description.lower() for name in ['ben-gurion', 'sharett', 'shamir', 'netanyahu', 'meir']):
            prompt = f"IMPORTANT: Character must look exactly like the real historical figure. {prompt}"
'''
    
    # Find where to add this in _create_scene_prompt
    if "# Ensure historical accuracy" not in content:
        marker = "enhanced_prompt = prompt"
        if marker in content:
            content = content.replace(marker, enhancement + "\n        " + marker)
            print("  ✅ Added historical accuracy emphasis")
    
    with open(director_path, 'w') as f:
        f.write(content)
    
    print("✅ Director fixes applied")

def main():
    print("🚀 Fixing character representation for historical accuracy\n")
    
    enhance_character_extraction()
    fix_director_prompts()
    
    print("\n✨ Character description fixes applied!")
    print("\n📝 Key improvements:")
    print("1. Added historical figure database with accurate descriptions")
    print("2. Ben-Gurion: Wild white hair, khaki shirt")
    print("3. Sharett: Completely bald, wire-rimmed glasses")
    print("4. Enhanced Director to emphasize historical accuracy")

if __name__ == "__main__":
    main()