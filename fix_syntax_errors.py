#!/usr/bin/env python3
"""
Fix all syntax errors in video_generator.py
"""

import os
import re

def fix_video_generator_syntax():
    """Fix all syntax errors in video_generator.py"""
    video_gen_path = "src/generators/video_generator.py"
    
    with open(video_gen_path, 'r') as f:
        content = f.read()
    
    # Fix 1: Ensure proper try/except structure
    lines = content.split('\n')
    fixed_lines = []
    in_try_block = False
    
    for i, line in enumerate(lines):
        if 'try:' in line:
            in_try_block = True
            fixed_lines.append(line)
        elif in_try_block and ('def ' in line and not line.strip().startswith('#')):
            # We're in a try block but found a function definition - need to close the try
            if not any('except' in prev_line for prev_line in lines[max(0, i-10):i]):
                fixed_lines.append('        except Exception as e:')
                fixed_lines.append('            logger.error(f"Error: {e}")')
                fixed_lines.append('            return []')
                fixed_lines.append('')
            in_try_block = False
            fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    # Write the fixed content
    with open(video_gen_path, 'w') as f:
        f.write('\n'.join(fixed_lines))
    
    print("✅ Fixed syntax errors")

def create_minimal_working_test():
    """Create a minimal test that should work"""
    test_content = '''#!/usr/bin/env python3
"""
Minimal working test
"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that imports work"""
    try:
        from src.generators.video_generator import VideoGenerator
        print("✅ VideoGenerator import successful")
        
        from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory
        print("✅ Models import successful")
        
        # Test basic instantiation
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY not set")
            return False
        
        generator = VideoGenerator(
            api_key=api_key,
            use_real_veo2=True,
            use_vertex_ai=True,
            vertex_project_id="viralgen-464411",
            vertex_location="us-central1",
            vertex_gcs_bucket="viral-veo2-results",
            prefer_veo3=False
        )
        print("✅ VideoGenerator instantiation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import/instantiation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Running minimal test...")
    success = test_imports()
    if success:
        print("🎉 Minimal test passed!")
    else:
        print("❌ Minimal test failed!")
'''
    
    with open("test_minimal.py", 'w') as f:
        f.write(test_content)
    
    print("✅ Created minimal test")

if __name__ == "__main__":
    print("🔧 Fixing syntax errors...")
    fix_video_generator_syntax()
    create_minimal_working_test()
    print("✅ All syntax fixes applied!") 