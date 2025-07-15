#!/usr/bin/env python3
"""
Fix final syntax issues by properly handling line breaks
"""

import re
import os

def fix_final_syntax(file_path):
    """Fix final syntax issues in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix missing line breaks after docstrings
        content = re.sub(r'"""([^"]*?)"""([a-zA-Z_])', r'"""\1"""\n\2', content)
        
        # Fix missing line breaks after function/class definitions
        content = re.sub(r':\s*"""([^"]*?)"""([a-zA-Z_])', r': """\1"""\n        \2', content)
        
        # Fix missing line breaks after decorators
        content = re.sub(r'@([a-zA-Z_]+)\s*([a-zA-Z_])', r'@\1\n\2', content)
        
        # Fix missing line breaks in class definitions
        content = re.sub(r'"""([^"]*?)"""([A-Z][a-zA-Z_]*)\s*=', r'"""\1"""\n    \2 =', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed final syntax in {file_path}")
            return True
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
    
    return False

def main():
    """Fix all final syntax errors"""
    print("Fixing final syntax errors...")
    
    # Key files that need fixing
    key_files = [
        'src/agents/director_agent.py',
        'src/agents/multi_agent_discussion.py',
        'src/agents/image_timing_agent.py',
        'src/utils/gcloud_auth_tester.py',
        'src/scrapers/news_scraper.py'
    ]
    
    fixed_count = 0
    for file_path in key_files:
        if os.path.exists(file_path):
            if fix_final_syntax(file_path):
                fixed_count += 1
    
    print(f"Fixed final syntax in {fixed_count} files")
    
    # Test compilation
    print("\nTesting compilation:")
    for file_path in key_files:
        if os.path.exists(file_path):
            try:
                import py_compile
                py_compile.compile(file_path, doraise=True)
                print(f"✅ {file_path} - OK")
            except Exception as e:
                print(f"❌ {file_path} - {str(e)[:100]}...")

if __name__ == "__main__":
    main() 