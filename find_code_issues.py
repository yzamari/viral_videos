#!/usr/bin/env python3
"""
Find potential code issues including undefined variables, dangerous patterns, etc.
"""
import os
import re
from pathlib import Path

def check_file(filepath):
    issues = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # Check for eval/exec usage
            if re.search(r'\beval\s*\(|exec\s*\(', line) and not line.strip().startswith('#'):
                issues.append((line_num, "DANGER", f"Use of eval/exec: {line.strip()}"))
            
            # Check for bare except
            if re.search(r'except\s*:', line):
                issues.append((line_num, "WARNING", f"Bare except clause: {line.strip()}"))
                
            # Check for undefined 'response' pattern
            if 'response.text' in line or 'response.json' in line:
                # Check if response is defined in previous 10 lines
                start = max(0, i - 10)
                if not any('response =' in lines[j] or 'response=' in lines[j] for j in range(start, i)):
                    issues.append((line_num, "POSSIBLE", f"'response' may be undefined: {line.strip()}"))
                    
            # Check for common undefined variables
            undefined_patterns = [
                (r'(?<!\.)result(?!s)', 'result'),
                (r'(?<!\.)data\b', 'data'),
                (r'(?<!\.)content\b', 'content'),
                (r'(?<!\.)config\b', 'config'),
            ]
            
            for pattern, var_name in undefined_patterns:
                if re.search(pattern, line) and '=' not in line:
                    # Check if defined in previous lines
                    start = max(0, i - 20)
                    context = ''.join(lines[start:i])
                    if f'{var_name} =' not in context and f'{var_name}=' not in context:
                        # Check if it's a parameter
                        func_start = max(0, i - 30)
                        func_context = ''.join(lines[func_start:i])
                        if not re.search(rf'def\s+\w+\s*\([^)]*{var_name}[^)]*\)', func_context):
                            issues.append((line_num, "POSSIBLE", f"'{var_name}' may be undefined: {line.strip()}"))
            
    except Exception as e:
        issues.append((0, "ERROR", f"Failed to parse file: {e}"))
        
    return filepath, issues

def main():
    src_dir = Path('src')
    all_issues = []
    
    for py_file in src_dir.rglob('*.py'):
        if '__pycache__' in str(py_file):
            continue
            
        filepath, issues = check_file(py_file)
        if issues:
            all_issues.append((filepath, issues))
    
    if all_issues:
        print("🔍 Potential code issues found:\n")
        
        # Group by severity
        danger_issues = []
        warning_issues = []
        possible_issues = []
        
        for filepath, issues in all_issues:
            for line_num, severity, message in issues:
                issue = (filepath, line_num, message)
                if severity == "DANGER":
                    danger_issues.append(issue)
                elif severity == "WARNING":
                    warning_issues.append(issue)
                else:
                    possible_issues.append(issue)
        
        if danger_issues:
            print("🚨 DANGEROUS PATTERNS:")
            for filepath, line_num, message in danger_issues:
                print(f"   {filepath}:{line_num} - {message}")
            print()
            
        if warning_issues:
            print("⚠️  WARNINGS:")
            for filepath, line_num, message in warning_issues[:10]:  # Limit output
                print(f"   {filepath}:{line_num} - {message}")
            if len(warning_issues) > 10:
                print(f"   ... and {len(warning_issues) - 10} more warnings")
            print()
            
        if possible_issues and len(danger_issues) + len(warning_issues) < 20:
            print("❓ POSSIBLE ISSUES:")
            for filepath, line_num, message in possible_issues[:10]:
                print(f"   {filepath}:{line_num} - {message}")
            if len(possible_issues) > 10:
                print(f"   ... and {len(possible_issues) - 10} more possible issues")
    else:
        print("✅ No obvious code issues found!")

if __name__ == '__main__':
    main()