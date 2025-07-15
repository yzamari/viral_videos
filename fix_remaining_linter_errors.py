#!/usr/bin/env python3
"""
Fix remaining linter errors after the systematic reduction
"""

import subprocess
import re
import os
from pathlib import Path

def fix_whitespace_errors():
    """Fix W291, W292, W293, W391 whitespace errors"""
    print("🔧 Fixing whitespace errors...")
    
    python_files = list(Path('src').rglob('*.py'))
    fixed_count = 0
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            original_lines = lines[:]
            
            # Fix W291: trailing whitespace
            lines = [line.rstrip() + '\n' if line.strip() else '\n' for line in lines]
            
            # Fix W293: blank line contains whitespace
            lines = ['\n' if line.strip() == '' else line for line in lines]
            
            # Fix W391: blank line at end of file
            while lines and lines[-1].strip() == '':
                lines.pop()
            
            # Ensure file ends with newline (fix W292)
            if lines and not lines[-1].endswith('\n'):
                lines[-1] += '\n'
            
            if lines != original_lines:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                fixed_count += 1
        
        except Exception as e:
            print(f"Error fixing whitespace in {file_path}: {e}")
    
    return fixed_count

def fix_import_errors():
    """Fix F401 unused imports"""
    print("🔧 Fixing unused import errors...")
    
    # Common unused imports to remove
    unused_imports = [
        'import tempfile',
        'import re',
        'import json',
        'import uuid',
        'import time',
        'import random'
    ]
    
    python_files = list(Path('src').rglob('*.py'))
    fixed_count = 0
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Remove obvious unused imports
            for unused_import in unused_imports:
                # Check if the import is actually used
                module_name = unused_import.split()[-1]
                
                # Simple check: if module name appears elsewhere in file
                lines = content.split('\n')
                import_lines = [i for i, line in enumerate(lines) if line.strip() == unused_import]
                
                for import_line_idx in import_lines:
                    # Check if module is used after the import
                    remaining_content = '\n'.join(lines[import_line_idx + 1:])
                    
                    if module_name not in remaining_content:
                        # Remove the import line
                        lines[import_line_idx] = ''
                        fixed_count += 1
                
                content = '\n'.join(lines)
            
            # Clean up multiple empty lines
            content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
        
        except Exception as e:
            print(f"Error fixing imports in {file_path}: {e}")
    
    return fixed_count

def fix_fstring_errors():
    """Fix F541 f-string missing placeholders"""
    print("🔧 Fixing f-string errors...")
    
    python_files = list(Path('src').rglob('*.py'))
    fixed_count = 0
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Find f-strings without placeholders and convert to regular strings
            def replace_fstring(match):
                quote = match.group(1)
                string_content = match.group(2)
                
                # If no {} placeholders, convert to regular string
                if '{' not in string_content:
                    return quote + string_content + quote
                return match.group(0)
            
            # Pattern to match f-strings
            pattern = r'f(["\'])((?:(?!\1)[^\\]|\\.)*)(\1)'
            content = re.sub(pattern, replace_fstring, content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_count += 1
        
        except Exception as e:
            print(f"Error fixing f-strings in {file_path}: {e}")
    
    return fixed_count

def fix_bare_except():
    """Fix E722 bare except clauses"""
    print("🔧 Fixing bare except clauses...")
    
    python_files = list(Path('src').rglob('*.py'))
    fixed_count = 0
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Replace bare except with except Exception
            content = re.sub(r'except\s*:', 'except Exception:', content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_count += 1
        
        except Exception as e:
            print(f"Error fixing bare except in {file_path}: {e}")
    
    return fixed_count

def fix_indentation_errors():
    """Fix E128, E129 indentation errors"""
    print("🔧 Fixing indentation errors...")
    
    python_files = list(Path('src').rglob('*.py'))
    fixed_count = 0
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            original_lines = lines[:]
            
            # Fix common indentation issues
            for i, line in enumerate(lines):
                # Fix continuation line indentation
                if i > 0 and lines[i-1].rstrip().endswith(('(', '[', '{')):
                    # Ensure proper indentation for continuation
                    if line.strip() and not line.startswith('    '):
                        indent = len(line) - len(line.lstrip())
                        if indent % 4 != 0:
                            new_indent = ((indent // 4) + 1) * 4
                            lines[i] = ' ' * new_indent + line.lstrip()
            
            if lines != original_lines:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                fixed_count += 1
        
        except Exception as e:
            print(f"Error fixing indentation in {file_path}: {e}")
    
    return fixed_count

def get_error_count():
    """Get current error count"""
    try:
        result = subprocess.run(
            ['python', '-m', 'flake8', '--count', 'src/'],
            capture_output=True, text=True, timeout=30
        )
        
        # Extract count from output
        for line in result.stdout.split('\n'):
            if line.strip().isdigit():
                return int(line.strip())
        
        return 0
    except Exception:
        return 0

def main():
    """Main function to fix remaining linter errors"""
    print("🔧 Fixing remaining linter errors...")
    
    initial_count = get_error_count()
    print(f"📊 Starting with {initial_count} errors")
    
    total_fixed = 0
    
    # Fix whitespace errors (W291, W292, W293, W391)
    fixed = fix_whitespace_errors()
    total_fixed += fixed
    print(f"   Fixed whitespace in {fixed} files")
    
    # Fix unused imports (F401)
    fixed = fix_import_errors()
    total_fixed += fixed
    print(f"   Fixed {fixed} unused imports")
    
    # Fix f-string errors (F541)
    fixed = fix_fstring_errors()
    total_fixed += fixed
    print(f"   Fixed f-strings in {fixed} files")
    
    # Fix bare except (E722)
    fixed = fix_bare_except()
    total_fixed += fixed
    print(f"   Fixed bare except in {fixed} files")
    
    # Fix indentation errors (E128, E129)
    fixed = fix_indentation_errors()
    total_fixed += fixed
    print(f"   Fixed indentation in {fixed} files")
    
    final_count = get_error_count()
    print(f"\n📊 Results:")
    print(f"   Initial errors: {initial_count}")
    print(f"   Final errors: {final_count}")
    print(f"   Errors fixed: {initial_count - final_count}")
    print(f"   Improvement: {((initial_count - final_count) / initial_count * 100):.1f}%")

if __name__ == "__main__":
    main() 