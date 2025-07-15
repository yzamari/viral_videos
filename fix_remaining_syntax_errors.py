#!/usr/bin/env python3
"""Fix all remaining syntax errors in the codebase """import re
import os
from pathlib import Path

def fix_file_syntax_errors(file_path): """Fix syntax errors in a specific file"""try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
         # Fix unterminated string literals content = re.sub(r'"\s*\n\s*([^"]*)"', r'"\1"', content) content = re.sub(r"'\s*\n\s*([^']*)'", r"'\1'", content)
         # Fix broken multiline strings content = re.sub(r'"([^"]*)\n\s*([^"]*)"', r'"\1 \2"', content) content = re.sub(r"'([^']*)\n\s*([^']*)'", r"'\1 \2'", content)
        
        # Fix incomplete assignments content = re.sub(r'=\s*\n\s*([^=\n]+)', r'= \1', content)
         # Fix broken f-strings content = re.sub(r'f"([^"]*)\n\s*([^"]*)"', r'f"\1\2"', content)
        
        # Fix trailing commas in function calls content = re.sub(r',\s*\n\s*\)', ')', content)
        
        # Fix broken parentheses content = re.sub(r'\(\s*\n\s*([^)]+)\)', r'(\1)', content)
        
        if content != original_content: with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content) print(f"Fixed syntax errors in {file_path}")
            return True
        
    except Exception as e: print(f"Error fixing {file_path}: {e}")
    
    return False

def main(): """Fix all syntax errors in Python files"""print("Fixing all remaining syntax errors...")
    
    # Find all Python files
    python_files = [] for root, dirs, files in os.walk('src'):
        for file in files: if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    # Also check main files main_files = ['main.py', 'test_*.py', 'fix_*.py']
    for pattern in main_files: for file in Path('.').glob(pattern): if file.suffix == '.py':
                python_files.append(str(file))
    
    fixed_count = 0
    for file_path in python_files:
        if fix_file_syntax_errors(file_path):
            fixed_count += 1
     print(f"Fixed syntax errors in {fixed_count} files")
    
    # Test compilation of key files
    key_files = [ 'src/agents/director_agent.py', 'src/agents/multi_agent_discussion.py', 'src/agents/image_timing_agent.py', 'src/utils/gcloud_auth_tester.py', 'src/scrapers/news_scraper.py'
    ]
     print("\nTesting compilation of key files:")
    for file_path in key_files:
        if os.path.exists(file_path):
            try:
                import py_compile
                py_compile.compile(file_path, doraise=True) print(f"✅ {file_path} - OK")
            except Exception as e: print(f"❌ {file_path} - {e}")
 if __name__ == "__main__":
    main() 