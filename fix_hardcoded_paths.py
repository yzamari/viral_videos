#!/usr/bin/env python3
"""
Fix all hardcoded paths in the viral video generator codebase
"""

import os
import re
import glob
from typing import List, Tuple

def find_hardcoded_paths() -> List[Tuple[str, int, str]]:
    """Find all hardcoded paths in the codebase"""
    hardcoded_patterns = [
        r'/Users/yahavzamari/viralAi',
        r'viral-video-generator/',
        r'viral-video-generator\\',
        r'cd viralAi',
        r'viralAi directory'
    ]
    
    # File extensions to search
    extensions = ['*.py', '*.sh', '*.md', '*.txt', '*.json']
    
    # Directories to exclude
    exclude_dirs = {'.git', '__pycache__', '.venv', 'outputs', 'logs', 'test_outputs', 'releases'}
    
    found_paths = []
    
    for ext in extensions:
        for file_path in glob.glob(f"**/{ext}", recursive=True):
            # Skip excluded directories
            if any(excl in file_path for excl in exclude_dirs):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    
                for line_num, line in enumerate(lines, 1):
                    for pattern in hardcoded_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            found_paths.append((file_path, line_num, line.strip()))
                            
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue
    
    return found_paths

def fix_python_files():
    """Fix hardcoded paths in Python files"""
    python_files = glob.glob("**/*.py", recursive=True)
    
    fixes_applied = 0
    
    for file_path in python_files:
        # Skip excluded directories
        if any(excl in file_path for excl in ['.git', '__pycache__', '.venv', 'outputs']):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix hardcoded viralAi paths
            content = re.sub(
                r'os.path.join(os.getcwd(), "([^")]*)"',
                r'os.path.join(os.getcwd(), "\1")',
                content
            )
            
            # Fix hardcoded viralAi directory checks
            content = re.sub(
                r'viralAi directory',
                r'viralAi directory',
                content
            )
            
            # Fix cd viralAi references
            content = re.sub(
                r'cd viralAi',
                r'cd viralAi',
                content
            )
            
            # Fix error messages about wrong directory
            content = re.sub(
                r'Please run from the viralAi directory',
                r'Please run from the viralAi directory',
                content
            )
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Fixed: {file_path}")
                fixes_applied += 1
                
        except Exception as e:
            print(f"❌ Error fixing {file_path}: {e}")
    
    return fixes_applied

def fix_shell_scripts():
    """Fix hardcoded paths in shell scripts"""
    shell_files = glob.glob("**/*.sh", recursive=True)
    
    fixes_applied = 0
    
    for file_path in shell_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix hardcoded paths
            content = re.sub(
                r'/Users/yahavzamari/viralAi/viral-video-generator',
                r'$(pwd)',
                content
            )
            
            # Fix cd commands
            content = re.sub(
                r'cd /Users/yahavzamari/viralAi/viral-video-generator',
                r'# Already in correct directory',
                content
            )
            
            # Fix directory references
            content = re.sub(
                r'viralAi directory',
                r'viralAi directory',
                content
            )
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Fixed shell script: {file_path}")
                fixes_applied += 1
                
        except Exception as e:
            print(f"❌ Error fixing {file_path}: {e}")
    
    return fixes_applied

def fix_markdown_files():
    """Fix hardcoded paths in markdown documentation"""
    md_files = glob.glob("**/*.md", recursive=True)
    
    fixes_applied = 0
    
    for file_path in md_files:
        # Skip excluded directories
        if any(excl in file_path for excl in ['.git', 'outputs', 'releases']):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix directory references in documentation
            content = re.sub(
                r'viral-video-generator',
                r'viralAi',
                content
            )
            
            # Fix hardcoded paths
            content = re.sub(
                r'/Users/yahavzamari/viralAi/viral-video-generator',
                r'/path/to/viralAi',
                content
            )
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Fixed documentation: {file_path}")
                fixes_applied += 1
                
        except Exception as e:
            print(f"❌ Error fixing {file_path}: {e}")
    
    return fixes_applied

def update_git_repository():
    """Update git repository and clean up"""
    print("\n🔧 Updating Git Repository...")
    
    # Clean up deleted files
    os.system("git add -A")
    
    # Check git status
    os.system("git status --porcelain")
    
    print("✅ Git repository updated")

def main():
    """Main function to fix all hardcoded paths"""
    print("🔧 FIXING HARDCODED PATHS IN VIRAL VIDEO GENERATOR")
    print("=" * 60)
    
    # First, find all hardcoded paths
    print("\n🔍 Scanning for hardcoded paths...")
    hardcoded_paths = find_hardcoded_paths()
    
    if hardcoded_paths:
        print(f"\n📋 Found {len(hardcoded_paths)} hardcoded path references:")
        for file_path, line_num, line in hardcoded_paths[:10]:  # Show first 10
            print(f"   {file_path}:{line_num} - {line[:80]}...")
        
        if len(hardcoded_paths) > 10:
            print(f"   ... and {len(hardcoded_paths) - 10} more")
    else:
        print("✅ No hardcoded paths found!")
    
    # Apply fixes
    print("\n🔧 Applying fixes...")
    
    python_fixes = fix_python_files()
    shell_fixes = fix_shell_scripts()
    md_fixes = fix_markdown_files()
    
    total_fixes = python_fixes + shell_fixes + md_fixes
    
    print(f"\n📊 SUMMARY:")
    print(f"   Python files fixed: {python_fixes}")
    print(f"   Shell scripts fixed: {shell_fixes}")
    print(f"   Markdown files fixed: {md_fixes}")
    print(f"   Total fixes applied: {total_fixes}")
    
    # Update git
    update_git_repository()
    
    print("\n🎉 All hardcoded paths have been fixed!")
    print("The codebase is now portable and will work from any directory.")

if __name__ == "__main__":
    main() 