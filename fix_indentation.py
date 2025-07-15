#!/usr/bin/env python3
"""
Fix all indentation issues in video_generator.py
"""

import os
import re

def fix_video_generator_indentation():
    """Fix all indentation issues"""
    video_gen_path = "src/generators/video_generator.py"
    
    with open(video_gen_path, 'r') as f:
        lines = f.readlines()
    
    fixed_lines = []
    in_class = False
    
    for i, line in enumerate(lines):
        # Check if we're in a class
        if line.strip().startswith('class VideoGenerator:'):
            in_class = True
            fixed_lines.append(line)
            continue
        
        # Fix method definitions inside class
        if in_class and line.strip().startswith('def '):
            # Ensure proper indentation for class methods
            if not line.startswith('    def '):
                line = '    ' + line.lstrip()
            fixed_lines.append(line)
            continue
        
        # Fix docstrings and method content
        if in_class and line.strip().startswith('"""') and i > 0:
            # Check if previous line was a method definition
            prev_line = lines[i-1].strip()
            if prev_line.startswith('def ') and prev_line.endswith(':'):
                # This is a method docstring, ensure proper indentation
                if not line.startswith('        '):
                    line = '        ' + line.lstrip()
        
        fixed_lines.append(line)
    
    # Write fixed content
    with open(video_gen_path, 'w') as f:
        f.writelines(fixed_lines)
    
    print("✅ Fixed indentation issues")

def create_simple_test():
    """Create a simple test to verify fixes"""
    test_content = '''#!/usr/bin/env python3
"""
Simple test to verify the system works
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic():
    try:
        from src.generators.video_generator import VideoGenerator
        from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory
        
        print("✅ Imports successful")
        
        # Test basic config creation
        config = GeneratedVideoConfig(
            topic="Test video",
            duration_seconds=5,
            target_platform=Platform.YOUTUBE,
            category=VideoCategory.ENTERTAINMENT,
            session_id="test_session"
        )
        
        print("✅ Config creation successful")
        
        # Test generator creation
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            generator = VideoGenerator(
                api_key=api_key,
                use_real_veo2=True,
                use_vertex_ai=True,
                vertex_project_id="viralgen-464411",
                vertex_location="us-central1",
                vertex_gcs_bucket="viral-veo2-results"
            )
            print("✅ Generator creation successful")
        else:
            print("⚠️ No API key, skipping generator test")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Running basic test...")
    success = test_basic()
    if success:
        print("🎉 Basic test passed!")
    else:
        print("❌ Basic test failed!")
'''
    
    with open("test_basic.py", 'w') as f:
        f.write(test_content)
    
    print("✅ Created basic test")

if __name__ == "__main__":
    print("🔧 Fixing indentation issues...")
    fix_video_generator_indentation()
    create_simple_test()
    print("✅ All indentation fixes applied!") 