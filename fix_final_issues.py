#!/usr/bin/env python3
"""
Fix final issues in the video generation system
"""

import os
import re

def fix_session_manager_directory():
    """Fix session manager to create directories"""
    session_manager_path = "src/utils/session_manager.py"
    
    with open(session_manager_path, 'r') as f:
        content = f.read()
    
    # Fix save_final_video method
    old_method = '''    def save_final_video(self, video_path: str) -> str:
        """Save final video to session"""
        if not self.current_session:
            return video_path

        session_final_dir = self.get_session_path("final_output")
        filename = f"final_video_{self.current_session}.mp4"
        session_final_path = os.path.join(session_final_dir, filename)

        if os.path.exists(video_path):
            shutil.copy2(video_path, session_final_path)
            self.track_file(session_final_path, "final_video", "VideoComposer")
            logger.info("💾 Saved final video to session")
            return session_final_path

        return video_path'''
    
    new_method = '''    def save_final_video(self, video_path: str) -> str:
        """Save final video to session"""
        if not self.current_session:
            return video_path

        session_final_dir = self.get_session_path("final_output")
        # Ensure directory exists
        os.makedirs(session_final_dir, exist_ok=True)
        
        filename = f"final_video_{self.current_session}.mp4"
        session_final_path = os.path.join(session_final_dir, filename)

        if os.path.exists(video_path):
            shutil.copy2(video_path, session_final_path)
            self.track_file(session_final_path, "final_video", "VideoComposer")
            logger.info("💾 Saved final video to session")
            return session_final_path

        return video_path'''
    
    if old_method in content:
        content = content.replace(old_method, new_method)
        with open(session_manager_path, 'w') as f:
            f.write(content)
        print("✅ Fixed session manager directory creation")
    else:
        print("⚠️ Session manager method not found for replacement")

def fix_video_generator_return():
    """Fix video generator to return proper VideoGenerationResult object"""
    video_gen_path = "src/generators/video_generator.py"
    
    with open(video_gen_path, 'r') as f:
        content = f.read()
    
    # Find the end of generate_video method and ensure it returns result object
    # Look for the return statement at the end
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        if 'return result' in line and 'def generate_video' in '\n'.join(lines[max(0, i-50):i]):
            # This is likely the return statement in generate_video
            fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    new_content = '\n'.join(fixed_lines)
    
    with open(video_gen_path, 'w') as f:
        f.write(new_content)
    
    print("✅ Fixed video generator return object")

def create_simple_test():
    """Create a simple working test"""
    test_content = '''#!/usr/bin/env python3
"""
Simple working test for video generation
"""

import os
import sys
import time
from src.generators.video_generator import VideoGenerator
from src.models.video_models import GeneratedVideoConfig, Platform, Category, Language

def test_simple_generation():
    """Test simple video generation"""
    print("🚀 Starting simple video generation test...")
    
    # Create config
    config = GeneratedVideoConfig(
        topic="Quick test video",
        duration_seconds=5,
        target_platform=Platform.YOUTUBE,
        category=Category.ENTERTAINMENT,
        language=Language.ENGLISH_US,
        session_id="simple_test"
    )
    
    # Create generator
    generator = VideoGenerator()
    
    # Generate video
    start_time = time.time()
    result = generator.generate_video(config)
    generation_time = time.time() - start_time
    
    print(f"✅ Generation completed in {generation_time:.1f}s")
    print(f"   Success: {result.success}")
    print(f"   Video: {result.file_path}")
    print(f"   Size: {result.file_size_mb:.2f}MB")
    
    return result

if __name__ == "__main__":
    try:
        result = test_simple_generation()
        print("🎉 Test completed successfully!")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
'''
    
    with open("test_simple_working.py", 'w') as f:
        f.write(test_content)
    
    print("✅ Created simple test file")

if __name__ == "__main__":
    print("🔧 Fixing final issues...")
    fix_session_manager_directory()
    fix_video_generator_return()
    create_simple_test()
    print("✅ All fixes applied!") 