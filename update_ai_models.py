#!/usr/bin/env python3
"""
Script to update all AI model references to use centralized configuration
"""
import os
import re
from pathlib import Path

# Define the import statement to add
IMPORT_STATEMENT = "from src.config.ai_model_config import DEFAULT_AI_MODEL"
RELATIVE_IMPORTS = {
    "src/agents/": "from ..config.ai_model_config import DEFAULT_AI_MODEL",
    "src/generators/": "from ..config.ai_model_config import DEFAULT_AI_MODEL",
    "src/frameworks/": "from ..config.ai_model_config import DEFAULT_AI_MODEL",
    "src/utils/": "from ..config.ai_model_config import DEFAULT_AI_MODEL",
    "src/core/": "from ..config.ai_model_config import DEFAULT_AI_MODEL",
    "src/analyzers/": "from ..config.ai_model_config import DEFAULT_AI_MODEL",
    "src/features/": "from ..config.ai_model_config import DEFAULT_AI_MODEL",
}

# Patterns to replace
PATTERNS = [
    # Direct GenerativeModel calls
    (r"GenerativeModel\(['\"]gemini-[^'\"]+['\"]\)", "GenerativeModel(DEFAULT_AI_MODEL)"),
    (r"genai\.GenerativeModel\(['\"]gemini-[^'\"]+['\"]\)", "genai.GenerativeModel(DEFAULT_AI_MODEL)"),
    
    # get_configured_model calls with explicit model
    (r"get_configured_model\(([^,]+),\s*['\"]gemini-[^'\"]+['\"]\)", r"get_configured_model(\1)"),
    
    # Default parameters in function definitions
    (r"model_name:\s*str\s*=\s*['\"]gemini-[^'\"]+['\"]", "model_name: str = None"),
]

# Files to skip
SKIP_FILES = {
    "ai_model_config.py",
    "gemini_helper.py",
    "update_ai_models.py",
    "__pycache__",
}

def should_skip_file(filepath):
    """Check if file should be skipped"""
    path_str = str(filepath)
    return any(skip in path_str for skip in SKIP_FILES)

def get_import_statement(filepath):
    """Get the appropriate import statement based on file location"""
    path_str = str(filepath).replace(os.sep, "/")
    for prefix, import_stmt in RELATIVE_IMPORTS.items():
        if prefix in path_str:
            return import_stmt
    return IMPORT_STATEMENT

def update_file(filepath):
    """Update a single file with new model references"""
    if should_skip_file(filepath):
        return False
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False
    
    original_content = content
    modified = False
    
    # Check if file uses any Gemini models
    if re.search(r"gemini-[\d\.]+-(flash|pro|lite)", content):
        # Apply all patterns
        for pattern, replacement in PATTERNS:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                modified = True
                content = new_content
        
        # Add import if modified and not already present
        if modified and "DEFAULT_AI_MODEL" not in content:
            import_stmt = get_import_statement(filepath)
            
            # Find the right place to add import
            lines = content.split('\n')
            import_added = False
            
            # Look for existing imports
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    # Add after the last import
                    for j in range(i, len(lines)):
                        if not (lines[j].startswith('import ') or 
                               lines[j].startswith('from ') or 
                               lines[j].strip() == ''):
                            lines.insert(j, import_stmt)
                            import_added = True
                            break
                    if import_added:
                        break
            
            # If no imports found, add after docstring
            if not import_added:
                for i, line in enumerate(lines):
                    if line.strip() and not line.startswith('"""') and not line.startswith('#'):
                        lines.insert(i, import_stmt)
                        lines.insert(i + 1, '')
                        break
            
            content = '\n'.join(lines)
    
    # Write back if modified
    if content != original_content:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated: {filepath}")
            return True
        except Exception as e:
            print(f"❌ Error writing {filepath}: {e}")
            return False
    
    return False

def main():
    """Main function to update all files"""
    src_dir = Path("src")
    
    updated_count = 0
    total_count = 0
    
    # Find all Python files
    for py_file in src_dir.rglob("*.py"):
        total_count += 1
        if update_file(py_file):
            updated_count += 1
    
    print(f"\n📊 Summary: Updated {updated_count}/{total_count} files")

if __name__ == "__main__":
    main()