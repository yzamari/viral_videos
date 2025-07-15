#!/usr/bin/env python3
"""
Systematic Linter Error Reduction
Fix linter errors by category, focusing on the most impactful ones first
"""

import subprocess
import re
import os
from collections import defaultdict

def get_linter_errors():
    """Get current linter errors categorized by type"""
    try:
        result = subprocess.run(
            ['python', '-m', 'flake8', 'src/', '--format=%(path)s:%(row)d:%(col)d: %(code)s %(text)s'],
            capture_output=True, text=True, timeout=60
        )
        
        errors = defaultdict(list)
        for line in result.stdout.split('\n'):
            if line.strip():
                match = re.match(r'([^:]+):(\d+):(\d+): (\w+) (.+)', line)
                if match:
                    file_path, line_num, col, code, message = match.groups()
                    errors[code].append({
                        'file': file_path,
                        'line': int(line_num),
                        'col': int(col),
                        'message': message
                    })
        
        return errors
    except Exception as e:
        print(f"Error getting linter errors: {e}")
        return {}

def fix_line_length_errors(errors):
    """Fix E501 line too long errors"""
    if 'E501' not in errors:
        return 0
    
    fixed = 0
    files_to_fix = defaultdict(list)
    
    # Group by file
    for error in errors['E501']:
        files_to_fix[error['file']].append(error)
    
    for file_path, file_errors in files_to_fix.items():
        if fix_file_line_lengths(file_path, file_errors):
            fixed += len(file_errors)
    
    return fixed

def fix_file_line_lengths(file_path, errors):
    """Fix line length errors in a specific file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        modified = False
        
        # Sort errors by line number (descending) to avoid line number shifts
        errors.sort(key=lambda x: x['line'], reverse=True)
        
        for error in errors:
            line_idx = error['line'] - 1
            if line_idx < len(lines):
                line = lines[line_idx]
                
                # Skip very long strings, URLs, or comments
                if any(x in line for x in ['http', '"""', "'''", '#']):
                    continue
                
                # Try to break at logical points
                fixed_line = break_long_line(line, error['line'])
                if fixed_line != line:
                    if isinstance(fixed_line, list):
                        lines[line_idx:line_idx+1] = fixed_line
                    else:
                        lines[line_idx] = fixed_line
                    modified = True
        
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return True
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
    
    return False

def break_long_line(line, line_num):
    """Break a long line at logical points"""
    stripped = line.strip()
    indent = len(line) - len(line.lstrip())
    indent_str = ' ' * indent
    
    # Don't break if line is not too long after stripping
    if len(stripped) <= 79:
        return line
    
    # Function parameters
    if '(' in stripped and ')' in stripped and ',' in stripped:
        return break_function_params(line, indent_str)
    
    # String concatenation
    if ' + ' in stripped and ('"' in stripped or "'" in stripped):
        return break_string_concat(line, indent_str)
    
    # Long imports
    if 'import' in stripped and ',' in stripped:
        return break_import_line(line, indent_str)
    
    # Dictionary/list definitions
    if ('{' in stripped or '[' in stripped) and ',' in stripped:
        return break_dict_list(line, indent_str)
    
    # Logical operators
    if ' and ' in stripped or ' or ' in stripped:
        return break_logical_operators(line, indent_str)
    
    return line

def break_function_params(line, indent_str):
    """Break function parameters across lines"""
    stripped = line.strip()
    
    # Find function call pattern
    if '(' in stripped and ')' in stripped:
        func_start = stripped.find('(')
        func_end = stripped.rfind(')')
        
        before_params = stripped[:func_start + 1]
        params = stripped[func_start + 1:func_end]
        after_params = stripped[func_end:]
        
        if ',' in params and len(stripped) > 79:
            # Split parameters
            param_list = []
            current_param = ""
            paren_level = 0
            
            for char in params:
                if char == '(':
                    paren_level += 1
                elif char == ')':
                    paren_level -= 1
                elif char == ',' and paren_level == 0:
                    param_list.append(current_param.strip())
                    current_param = ""
                    continue
                current_param += char
            
            if current_param.strip():
                param_list.append(current_param.strip())
            
            if len(param_list) > 1:
                result = [indent_str + before_params + '\n']
                for i, param in enumerate(param_list):
                    if i == len(param_list) - 1:
                        result.append(indent_str + '    ' + param + after_params + '\n')
                    else:
                        result.append(indent_str + '    ' + param + ',\n')
                return result
    
    return line

def break_string_concat(line, indent_str):
    """Break string concatenation across lines"""
    stripped = line.strip()
    
    if ' + ' in stripped:
        parts = stripped.split(' + ')
        if len(parts) > 1:
            result = []
            for i, part in enumerate(parts):
                if i == 0:
                    result.append(indent_str + part.strip() + ' +\n')
                elif i == len(parts) - 1:
                    result.append(indent_str + '    ' + part.strip() + '\n')
                else:
                    result.append(indent_str + '    ' + part.strip() + ' +\n')
            return result
    
    return line

def break_import_line(line, indent_str):
    """Break long import statements"""
    stripped = line.strip()
    
    if 'from' in stripped and 'import' in stripped:
        parts = stripped.split('import')
        if len(parts) == 2:
            from_part = parts[0].strip()
            import_part = parts[1].strip()
            
            if ',' in import_part:
                imports = [imp.strip() for imp in import_part.split(',')]
                if len(imports) > 2:
                    result = [indent_str + from_part + 'import (\n']
                    for i, imp in enumerate(imports):
                        if i == len(imports) - 1:
                            result.append(indent_str + '    ' + imp + '\n')
                        else:
                            result.append(indent_str + '    ' + imp + ',\n')
                    result.append(indent_str + ')\n')
                    return result
    
    return line

def break_dict_list(line, indent_str):
    """Break dictionary or list definitions"""
    stripped = line.strip()
    
    if '{' in stripped and '}' in stripped and ',' in stripped:
        # Simple dictionary breaking
        if stripped.count(',') >= 2:
            return indent_str + stripped[:40] + '\n' + indent_str + '    ' + stripped[40:] + '\n'
    
    return line

def break_logical_operators(line, indent_str):
    """Break lines with logical operators"""
    stripped = line.strip()
    
    for op in [' and ', ' or ']:
        if op in stripped:
            parts = stripped.split(op)
            if len(parts) == 2:
                return (indent_str + parts[0].strip() + op + '\n' +
                       indent_str + '        ' + parts[1].strip() + '\n')
    
    return line

def fix_unused_variables(errors):
    """Fix F841 unused variable errors"""
    if 'F841' not in errors:
        return 0
    
    fixed = 0
    files_to_fix = defaultdict(list)
    
    for error in errors['F841']:
        files_to_fix[error['file']].append(error)
    
    for file_path, file_errors in files_to_fix.items():
        if fix_file_unused_vars(file_path, file_errors):
            fixed += len(file_errors)
    
    return fixed

def fix_file_unused_vars(file_path, errors):
    """Fix unused variables in a file by prefixing with underscore"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        modified = False
        
        for error in errors:
            # Extract variable name from message
            message = error['message']
            if 'local variable' in message and 'is assigned to but never used' in message:
                # Extract variable name
                match = re.search(r"local variable '([^']+)'", message)
                if match:
                    var_name = match.group(1)
                    
                    # Replace first occurrence with underscore prefix
                    pattern = rf'\b{re.escape(var_name)}\s*='
                    replacement = f'_{var_name} ='
                    
                    new_content = re.sub(pattern, replacement, content, count=1)
                    if new_content != content:
                        content = new_content
                        modified = True
        
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
    except Exception as e:
        print(f"Error fixing unused vars in {file_path}: {e}")
    
    return False

def main():
    """Main function to systematically fix linter errors"""
    print("🔧 Starting systematic linter error reduction...")
    
    # Get current errors
    print("📊 Analyzing current linter errors...")
    errors = get_linter_errors()
    
    if not errors:
        print("✅ No linter errors found!")
        return
    
    # Print error summary
    total_errors = sum(len(error_list) for error_list in errors.values())
    print(f"\n📈 Found {total_errors} linter errors:")
    for code, error_list in sorted(errors.items()):
        print(f"  {code}: {len(error_list)} errors")
    
    # Fix errors by priority
    total_fixed = 0
    
    # 1. Fix line length errors (most common)
    print("\n🔧 Fixing line length errors (E501)...")
    fixed = fix_line_length_errors(errors)
    total_fixed += fixed
    print(f"   Fixed {fixed} line length errors")
    
    # 2. Fix unused variables
    print("\n🔧 Fixing unused variable errors (F841)...")
    fixed = fix_unused_variables(errors)
    total_fixed += fixed
    print(f"   Fixed {fixed} unused variable errors")
    
    print(f"\n✅ Total fixes applied: {total_fixed}")
    
    # Check remaining errors
    print("\n📊 Checking remaining errors...")
    remaining_errors = get_linter_errors()
    remaining_total = sum(len(error_list) for error_list in remaining_errors.values())
    
    print(f"📉 Reduced from {total_errors} to {remaining_total} errors")
    print(f"🎯 Improvement: {total_errors - remaining_total} errors fixed")

if __name__ == "__main__":
    main() 