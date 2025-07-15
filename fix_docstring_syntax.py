#!/usr/bin/env python3
"""
Fix broken docstrings that are missing line breaks
"""

import re
import os

def fix_docstring_syntax(file_path):
    """Fix broken docstrings in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix broken docstrings that are missing line breaks
        content = re.sub(r'"""([^"]*) """import', r'"""\1\n"""\nimport', content)
        content = re.sub(r'"""([^"]*) """from', r'"""\1\n"""\nfrom', content)
        content = re.sub(r'"""([^"]*) """class', r'"""\1\n"""\nclass', content)
        content = re.sub(r'"""([^"]*) """def', r'"""\1\n"""\ndef', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed docstring syntax in {file_path}")
            return True
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
    
    return False

def main():
    """Fix all docstring syntax errors"""
    print("Fixing docstring syntax errors...")
    
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
            if fix_docstring_syntax(file_path):
                fixed_count += 1
    
    print(f"Fixed docstring syntax in {fixed_count} files")
    
    # Test compilation
    print("\nTesting compilation:")
    for file_path in key_files:
        if os.path.exists(file_path):
            try:
                import py_compile
                py_compile.compile(file_path, doraise=True)
                print(f"✅ {file_path} - OK")
            except Exception as e:
                print(f"❌ {file_path} - {e}")

if __name__ == "__main__":
    main() 