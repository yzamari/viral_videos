#!/usr/bin/env python3
"""
Fix critical syntax errors preventing code compilation
"""

import os
import re

def fix_critical_file(file_path, expected_issues):
    """Fix critical syntax errors in a specific file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply specific fixes for each file
        for pattern, replacement in expected_issues:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed critical syntax in {file_path}")
            return True
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
    
    return False

def main():
    """Fix critical syntax errors in key files"""
    print("Fixing critical syntax errors...")
    
    # Define specific fixes for each problematic file
    fixes = {
        'src/core/__init__.py': [
            (r'following clean architecture principles\. """\s*___version__', 
             'following clean architecture principles.\n"""\n\n__version__')
        ],
        'src/agents/working_orchestrator.py': [
            (r'Comprehensive mission-driven system with ALL features and proper OOP design """\s*from',
             'Comprehensive mission-driven system with ALL features and proper OOP design\n"""\n\nfrom'),
            (r'"""Available orchestrator modes for different use cases"""\s*([A-Z_]+\s*=)',
             '"""Available orchestrator modes for different use cases"""\n    \\1'),
            (r'"""Comprehensive mission-driven orchestrator with ALL features and proper OOP design\s*-([^"]*?)"""\s*def',
             '"""Comprehensive mission-driven orchestrator with ALL features and proper OOP design\\1"""\n\n    def'),
            (r'"""Initialize agents based on orchestrator mode"""\s*if',
             '"""Initialize agents based on orchestrator mode"""\n        if')
        ],
        'src/agents/director_agent.py': [
            (r'Ensures hooks are prominently featured in both script and final video """\s*import',
             'Ensures hooks are prominently featured in both script and final video\n"""\n\nimport')
        ],
        'src/agents/multi_agent_discussion.py': [
            (r'Collaborative decision-making with specialized AI agents """\s*import',
             'Collaborative decision-making with specialized AI agents\n"""\n\nimport')
        ],
        'src/agents/image_timing_agent.py': [
            (r'Enhanced for fallback generation with 5-10 second intelligent timing """\s*import',
             'Enhanced for fallback generation with 5-10 second intelligent timing\n"""\n\nimport')
        ],
        'src/utils/gcloud_auth_tester.py': [
            (r'Tests all authentication methods and services required by the app """\s*import',
             'Tests all authentication methods and services required by the app\n"""\n\nimport')
        ],
        'src/scrapers/news_scraper.py': [
            (r'"""Enhanced news scraper for hot trending topics """\s*import',
             '"""Enhanced news scraper for hot trending topics\n"""\n\nimport')
        ]
    }
    
    fixed_count = 0
    for file_path, file_fixes in fixes.items():
        if os.path.exists(file_path):
            if fix_critical_file(file_path, file_fixes):
                fixed_count += 1
    
    print(f"Fixed critical syntax in {fixed_count} files")
    
    # Test compilation of fixed files
    print("\nTesting compilation:")
    for file_path in fixes.keys():
        if os.path.exists(file_path):
            try:
                import py_compile
                py_compile.compile(file_path, doraise=True)
                print(f"✅ {file_path} - OK")
            except Exception as e:
                print(f"❌ {file_path} - {str(e)[:100]}...")

if __name__ == "__main__":
    main() 