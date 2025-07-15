#!/usr/bin/env python3
"""Comprehensive Linter Error Fix Script
Fixes all types of linter errors in the ViralAI codebase """import os
import re
import ast
import sys
from pathlib import Path
from typing import List, Dict, Set

def fix_line_length_errors(file_path: str) -> int: """Fix E501 line too long errors by intelligent line breaking"""fixes = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        modified = False
        new_lines = []
        
        for i, line in enumerate(lines):
            if len(line.rstrip()) > 79:
                # Try to fix long lines intelligently
                fixed_line = fix_long_line(line, i)
                if fixed_line != line:
                    new_lines.extend(fixed_line if isinstance(fixed_line, list) else [fixed_line])
                    modified = True
                    fixes += 1
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        
        if modified: with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
    
    except Exception as e: print(f"Error fixing line length in {file_path}: {e}")
    
    return fixes

def fix_long_line(line: str, line_num: int) -> str: """Fix a single long line intelligently"""stripped = line.rstrip()
    indent = len(line) - len(line.lstrip()) indent_str = ' ' * indent
     # Don't break very long URLs or strings if 'http' in stripped or '"""' in stripped or "'''" in stripped:
        return line
    
    # Function calls with many parameters if '(' in stripped and ')' in stripped:
        return fix_function_call(line, indent_str)
     # Long string concatenations if '+' in stripped and ('"' in stripped or "'" in stripped):
        return fix_string_concat(line, indent_str)
     # Long f-strings if 'f"' in stripped or "f'" in stripped:
        return fix_fstring(line, indent_str)
    
    # Long dictionary/list definitions if '{' in stripped or '[' in stripped:
        return fix_dict_list(line, indent_str)
    
    # Long import statements if 'import' in stripped:
        return fix_import(line, indent_str)
    
    # Long conditionals if 'if ' in stripped or 'elif ' in stripped:
        return fix_conditional(line, indent_str)
    
    # Generic break at logical points
    return fix_generic_break(line, indent_str)

def fix_function_call(line: str, indent_str: str) -> List[str]: """Fix long function calls by breaking parameters"""stripped = line.strip()
    
    # Find the function call if '(' in stripped and ')' in stripped: func_start = stripped.find('(')
        func_name = stripped[:func_start + 1] params_end = stripped.rfind(')')
        params = stripped[func_start + 1:params_end]
        after_params = stripped[params_end:]
        
        # Break parameters if they contain commas if ',' in params and len(stripped) > 79:
            param_parts = [] current_param = ""paren_level = 0
            
            for char in params: if char == '(':
                    paren_level += 1 elif char == ')':
                    paren_level -= 1 elif char == ',' and paren_level == 0:
                    param_parts.append(current_param.strip()) current_param = ""continue
                current_param += char
            
            if current_param.strip():
                param_parts.append(current_param.strip())
            
            # Reconstruct with line breaks result = [indent_str + func_name + '\n']
            for i, param in enumerate(param_parts):
                if i == len(param_parts) - 1: result.append(indent_str + '    ' + param + after_params + '\n')
                else: result.append(indent_str + '    ' + param + ',\n')
            
            return result
    
    return [line]

def fix_string_concat(line: str, indent_str: str) -> List[str]: """Fix long string concatenations"""stripped = line.strip()
     # Look for string concatenation with + if '+' in stripped and ('"' in stripped or "'" in stripped):
        # Simple approach: break at + operators
        parts = [] current = ""in_string = False
        quote_char = None
        
        i = 0
        while i < len(stripped):
            char = stripped[i] if not in_string and char in ['"', "'"]:
                in_string = True
                quote_char = char
            elif in_string and char == quote_char: # Check if it's escaped
                if i > 0 and stripped[i-1] != '\\':
                    in_string = False
                    quote_char = None elif not in_string and char == '+':
                # Found a concatenation point
                if current.strip():
                    parts.append(current.strip()) current = ""i += 1
                continue
            
            current += char
            i += 1
        
        if current.strip():
            parts.append(current.strip())
        
        if len(parts) > 1:
            result = []
            for i, part in enumerate(parts):
                if i == 0: result.append(indent_str + part + ' +\n')
                elif i == len(parts) - 1: result.append(indent_str + '    ' + part + '\n')
                else: result.append(indent_str + '    ' + part + ' +\n')
            return result
    
    return [line]

def fix_fstring(line: str, indent_str: str) -> str: """Fix long f-strings by breaking them"""stripped = line.strip()
     # For very long f-strings, we'll keep them as is to avoid breaking functionality
    # This is a conservative approach
    return line

def fix_dict_list(line: str, indent_str: str) -> List[str]: """Fix long dictionary or list definitions"""stripped = line.strip()
    
    # Simple approach for dictionaries
    if '{' in stripped and '}' in stripped and ',' in stripped:
        # Break at commas
        parts = [] current = ""brace_level = 0
        
        for char in stripped: if char == '{':
                brace_level += 1 elif char == '}':
                brace_level -= 1 elif char == ',' and brace_level == 1:
                parts.append(current.strip()) current = ""continue
            current += char
        
        if current.strip():
            parts.append(current.strip())
        
        if len(parts) > 1:
            result = []
            for i, part in enumerate(parts):
                if i == 0: result.append(indent_str + part + ',\n')
                elif i == len(parts) - 1: result.append(indent_str + '    ' + part + '\n')
                else: result.append(indent_str + '    ' + part + ',\n')
            return result
    
    return [line]

def fix_import(line: str, indent_str: str) -> List[str]: """Fix long import statements"""stripped = line.strip()
     if 'from' in stripped and 'import' in stripped:
        # Break long from imports parts = stripped.split('import')
        if len(parts) == 2:
            from_part = parts[0].strip()
            import_part = parts[1].strip()
             if ',' in import_part: imports = [imp.strip() for imp in import_part.split(',')]
                if len(imports) > 1: result = [indent_str + from_part + 'import (\n']
                    for i, imp in enumerate(imports):
                        if i == len(imports) - 1: result.append(indent_str + '    ' + imp + '\n')
                        else: result.append(indent_str + '    ' + imp + ',\n') result.append(indent_str + ')\n')
                    return result
    
    return [line]

def fix_conditional(line: str, indent_str: str) -> List[str]: """Fix long conditional statements"""stripped = line.strip()
    
    # Break at logical operators if ' and ' in stripped or ' or ' in stripped:
        # Simple approach: break at logical operators operators = [' and ', ' or ']
        for op in operators:
            if op in stripped:
                parts = stripped.split(op)
                if len(parts) > 1:
                    result = []
                    for i, part in enumerate(parts):
                        if i == 0: result.append(indent_str + part.strip() + op + '\n')
                        elif i == len(parts) - 1: result.append(indent_str + '        ' + part.strip() + ':\n')
                        else: result.append(indent_str + '        ' + part.strip() + op + '\n')
                    return result
                break
    
    return [line]

def fix_generic_break(line: str, indent_str: str) -> str: """Generic line breaking at logical points"""stripped = line.strip()
     # Don't break if it's a comment or docstring if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
        return line
    
    # Break at commas, operators, or other logical points break_points = [', ', ' = ', ' == ', ' != ', ' + ', ' - ', ' * ', ' / ']
    
    for bp in break_points:
        if bp in stripped:
            pos = stripped.find(bp)
            if pos > 0 and pos < 60:  # Break around position 60
                first_part = stripped[:pos + len(bp)]
                second_part = stripped[pos + len(bp):]
                
                if second_part.strip(): return indent_str + first_part + '\n' + indent_str + '    ' + second_part + '\n'return line

def fix_unused_variables(file_path: str) -> int: """Fix F841 unused variable errors"""fixes = 0
    
    try: with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find unused variables and prefix with underscore lines = content.split('\n')
        modified = False
        
        for i, line in enumerate(lines):
            # Look for common unused variable patterns if ' = ' in line and not line.strip().startswith('#'): # Check if it's a simple assignment
                stripped = line.strip()
                if re.match(r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=', stripped):
                    # Extract variable name var_name = stripped.split('=')[0].strip()
                    
                    # Check if variable is used later in the file remaining_content = '\n'.join(lines[i+1:])
                    if var_name not in remaining_content:
                        # Prefix with underscore lines[i] = line.replace(var_name, '_' + var_name, 1)
                        modified = True
                        fixes += 1
        
        if modified: with open(file_path, 'w', encoding='utf-8') as f: f.write('\n'.join(lines))
    
    except Exception as e: print(f"Error fixing unused variables in {file_path}: {e}")
    
    return fixes

def fix_fstring_placeholders(file_path: str) -> int: """Fix F541 f-string missing placeholders"""fixes = 0
    
    try: with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find f-strings without placeholders and convert to regular strings
        modified = False
         # Pattern to match f-strings without {} placeholders pattern = r'f(["\'])((?:(?!\1)[^\\]|\\.)*)(\1)'def replace_fstring(match):
            quote = match.group(1)
            content = match.group(2)
            
            # If no {} placeholders, convert to regular string if '{' not in content:
                return quote + content + quote
            return match.group(0)
        
        new_content = re.sub(pattern, replace_fstring, content)
        
        if new_content != content:
            modified = True fixes += content.count('f"') + content.count("f'") - new_content.count('f"') - new_content.count("f'")
             with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
    
    except Exception as e: print(f"Error fixing f-strings in {file_path}: {e}")
    
    return fixes

def fix_blank_line_whitespace(file_path: str) -> int: """Fix W293 blank line contains whitespace"""fixes = 0
    
    try: with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        modified = False
        new_lines = []
        
        for line in lines: if line.strip() == '' and line != '\n':
                # Blank line with whitespace new_lines.append('\n')
                modified = True
                fixes += 1
            else:
                new_lines.append(line)
        
        if modified: with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
    
    except Exception as e: print(f"Error fixing blank lines in {file_path}: {e}")
    
    return fixes

def fix_bare_except(file_path: str) -> int: """Fix E722 bare except clauses"""fixes = 0
    
    try: with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace bare except with except Exception new_content = re.sub(r'except\s*:', 'except Exception:', content)
        
        if new_content != content: fixes = content.count('except:') - new_content.count('except:')
             with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
    
    except Exception as e: print(f"Error fixing bare except in {file_path}: {e}")
    
    return fixes

def fix_star_imports(file_path: str) -> int: """Fix F403 star imports"""fixes = 0
    
    try: with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        modified = False
        new_lines = []
        
        for line in lines: if 'from moviepy.editor import *' in line:
                # Replace with specific imports
                new_lines.append(line.replace( 'from moviepy.editor import *', 'from moviepy.editor import (AudioFileClip, VideoFileClip, ''concatenate_videoclips, TextClip, CompositeVideoClip)'))
                modified = True
                fixes += 1
            else:
                new_lines.append(line)
        
        if modified: with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
    
    except Exception as e: print(f"Error fixing star imports in {file_path}: {e}")
    
    return fixes

def fix_unused_imports(file_path: str) -> int: """Fix F401 unused imports"""fixes = 0
    
    try: with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
         lines = content.split('\n')
        modified = False
        
        # Simple approach: remove obvious unused imports
        unused_patterns = [ r'import tempfile', r'import re',
        ]
        
        for i, line in enumerate(lines):
            for pattern in unused_patterns:
                if re.match(pattern, line.strip()):
                    # Check if the import is used later
                    module_name = pattern.split()[-1] remaining_content = '\n'.join(lines[i+1:])
                    
                    if module_name not in remaining_content: lines[i] = ''  # Remove the line
                        modified = True
                        fixes += 1
        
        if modified:
            # Clean up empty lines lines = [line for line in lines if line.strip() or line == '']
             with open(file_path, 'w', encoding='utf-8') as f: f.write('\n'.join(lines))
    
    except Exception as e: print(f"Error fixing unused imports in {file_path}: {e}")
    
    return fixes

def process_file(file_path: str) -> Dict[str, int]: """Process a single file and fix all linter errors"""fixes = { 'line_length': 0, 'unused_variables': 0, 'fstring_placeholders': 0, 'blank_line_whitespace': 0, 'bare_except': 0, 'star_imports': 0, 'unused_imports': 0
    }
     print(f"Processing {file_path}...")
     fixes['line_length'] = fix_line_length_errors(file_path) fixes['unused_variables'] = fix_unused_variables(file_path) fixes['fstring_placeholders'] = fix_fstring_placeholders(file_path) fixes['blank_line_whitespace'] = fix_blank_line_whitespace(file_path) fixes['bare_except'] = fix_bare_except(file_path) fixes['star_imports'] = fix_star_imports(file_path) fixes['unused_imports'] = fix_unused_imports(file_path)
    
    total_fixes = sum(fixes.values())
    if total_fixes > 0: print(f"  Fixed {total_fixes} issues in {file_path}")
    
    return fixes

def main(): """Main function to fix all linter errors"""print("🔧 Starting comprehensive linter error fixes...")
    
    # Find all Python files in src directory src_path = Path('src') python_files = list(src_path.rglob('*.py'))
    
    total_fixes = { 'line_length': 0, 'unused_variables': 0, 'fstring_placeholders': 0, 'blank_line_whitespace': 0, 'bare_except': 0, 'star_imports': 0, 'unused_imports': 0
    }
    
    for file_path in python_files:
        file_fixes = process_file(str(file_path))
        for key, value in file_fixes.items():
            total_fixes[key] += value
     print("\n📊 Summary of fixes:")
    for fix_type, count in total_fixes.items():
        if count > 0: print(f"  {fix_type}: {count} fixes")
    
    total_count = sum(total_fixes.values()) print(f"\n✅ Total fixes applied: {total_count}")
    
    if total_count > 0: print("\n🧪 Running flake8 to verify fixes...") os.system("python -m flake8 --count --statistics src/ | head -20")
 if __name__ == "__main__":
    main() 