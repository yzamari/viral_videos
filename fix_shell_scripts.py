#!/usr/bin/env python3
"""
Fix Shell Scripts Issues
========================
Fixes common issues in shell scripts:
1. Replace python main.py with python3 main.py generate
2. Add bash 4+ compatibility check for associative arrays
3. Ensure proper CLI command format
"""

import os
import re
import glob
from pathlib import Path

def fix_bash_version_check(content):
    """Add bash version check if script uses associative arrays"""
    if 'declare -A' in content and 'BASH_VERSION' not in content:
        # Add bash version check after shebang
        lines = content.split('\n')
        shebang_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('#!'):
                shebang_idx = i
                break
        
        version_check = """# Force use of modern bash for associative arrays
if [[ ${BASH_VERSION%%.*} -lt 4 ]]; then
    echo "⚠️  This script requires bash 4.0+. macOS default is bash 3.x"
    echo "Installing modern bash via homebrew..."
    if command -v brew >/dev/null 2>&1; then
        brew install bash
        exec /usr/local/bin/bash "$0" "$@"
    else
        echo "❌ Please install bash 4+ or run: brew install bash"
        exit 1
    fi
fi"""
        
        lines.insert(shebang_idx + 1, version_check)
        return '\n'.join(lines)
    return content

def fix_python_commands(content):
    """Fix python main.py commands to python3 main.py generate"""
    # Pattern 1: python main.py --mission (missing generate)
    content = re.sub(
        r'python(\d?)(\s+)main\.py(\s+)--mission',
        r'python3\2main.py\3generate --mission',
        content
    )
    
    # Pattern 2: python main.py \ followed by --mission on next line
    content = re.sub(
        r'python(\d?)(\s+)main\.py(\s+)\\(\s*\n\s*)--mission',
        r'python3\2main.py\3generate \\\4--mission',
        content
    )
    
    # Pattern 3: Ensure python3 is used instead of python
    content = re.sub(r'\bpython\b(?!\d)', 'python3', content)
    
    return content

def fix_shell_script(file_path):
    """Fix a single shell script"""
    print(f"🔧 Fixing {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply fixes
        content = fix_bash_version_check(content)
        content = fix_python_commands(content)
        
        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Fixed {file_path}")
            return True
        else:
            print(f"  ✨ No changes needed for {file_path}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error fixing {file_path}: {e}")
        return False

def main():
    """Fix all shell scripts in the directory"""
    print("🛠️  Shell Script Fixer")
    print("=" * 50)
    
    # Find all shell scripts
    script_patterns = [
        '*.sh',
        'run_*.sh',
        '*_series.sh'
    ]
    
    all_scripts = set()
    base_dir = Path('/Users/yahavzamari/viralAi')
    
    for pattern in script_patterns:
        scripts = glob.glob(str(base_dir / pattern))
        all_scripts.update(scripts)
    
    print(f"Found {len(all_scripts)} shell scripts to check")
    print()
    
    fixed_count = 0
    skipped_count = 0
    
    for script_path in sorted(all_scripts):
        if fix_shell_script(script_path):
            fixed_count += 1
        else:
            skipped_count += 1
    
    print()
    print("📊 Summary:")
    print(f"  ✅ Fixed: {fixed_count} scripts")
    print(f"  ✨ No changes needed: {skipped_count} scripts")
    print(f"  📁 Total processed: {len(all_scripts)} scripts")
    
    # Test the dragon calculus script specifically
    print()
    print("🧪 Testing dragon calculus script...")
    test_script = base_dir / 'run_all_dragon_calculus_episodes.sh'
    if test_script.exists():
        print(f"✅ Script exists: {test_script}")
        
        # Check for bash 4+ compatibility
        with open(test_script, 'r') as f:
            content = f.read()
            if 'BASH_VERSION' in content:
                print("✅ Bash version check present")
            if 'python3 main.py generate' in content:
                print("✅ Correct CLI command format")
            if 'declare -A' in content:
                print("✅ Uses associative arrays (requires bash 4+)")
    
    print()
    print("🎉 Shell script fixes complete!")
    print("You can now run: ./run_all_dragon_calculus_episodes.sh")

if __name__ == "__main__":
    main()