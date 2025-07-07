#!/usr/bin/env python3
"""
Fix VideoGenerator class to accept use_real_veo2 parameter
"""
import os
import re

def fix_video_generator():
    """Fix VideoGenerator __init__ method"""
    file_path = "src/generators/video_generator.py"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find and replace the __init__ method
    old_init = r'def __init__\(self, api_key: str, output_dir: str = "outputs"\):'
    new_init = 'def __init__(self, api_key: str, output_dir: str = "outputs", use_real_veo2: bool = True, use_vertex_ai: bool = False, project_id: str = None, location: str = "us-central1"):'
    
    if old_init in content:
        content = re.sub(old_init, new_init, content)
        
        # Also update the initialization part
        old_vars = """        self.api_key = api_key
        self.output_dir = output_dir
        self.session_id = str(uuid.uuid4())[:8]"""
        
        new_vars = """        self.api_key = api_key
        self.output_dir = output_dir
        self.session_id = str(uuid.uuid4())[:8]
        self.use_real_veo2 = use_real_veo2
        self.use_vertex_ai = use_vertex_ai
        self.project_id = project_id
        self.location = location"""
        
        content = content.replace(old_vars, new_vars)
        
        # Update the log message
        old_log = 'logger.info(f"🎬 VideoGenerator initialized with session {self.session_id}")'
        new_log = 'logger.info(f"🎬 VideoGenerator initialized with session {self.session_id}, use_real_veo2={use_real_veo2}, use_vertex_ai={use_vertex_ai}")'
        
        content = content.replace(old_log, new_log)
        
        # Write back
        with open(file_path, 'w') as f:
            f.write(content)
        
        print("✅ VideoGenerator fixed successfully!")
        return True
    else:
        print("❌ Could not find __init__ method to fix")
        return False

if __name__ == "__main__":
    fix_video_generator() 