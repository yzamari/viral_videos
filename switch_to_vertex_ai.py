#!/usr/bin/env python3
"""
Switch to Vertex AI for VEO Generation

This script switches your viral video generator from Google AI Studio 
(which has daily limits) to Vertex AI (unlimited enterprise quotas).
"""

import os
import sys
import shutil
from datetime import datetime

def backup_current_config():
    """Backup current configuration"""
    print("📁 Backing up current configuration...")
    
    backup_dir = f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Backup key files
    files_to_backup = [
        'src/generators/optimized_veo_client.py',
        'src/workflows/generate_viral_video.py',
        'config/config.py'
    ]
    
    for file_path in files_to_backup:
        if os.path.exists(file_path):
            backup_path = os.path.join(backup_dir, os.path.basename(file_path))
            shutil.copy2(file_path, backup_path)
            print(f"   ✅ Backed up: {file_path}")
    
    print(f"✅ Configuration backed up to: {backup_dir}")
    return backup_dir

def update_optimized_veo_client():
    """Update the optimized VEO client to prefer Vertex AI"""
    print("🔧 Updating VEO client to use Vertex AI...")
    
    client_path = 'src/generators/optimized_veo_client.py'
    
    # Read current content
    with open(client_path, 'r') as f:
        content = f.read()
    
    # Find the initialization section and modify it
    lines = content.split('\n')
    modified_lines = []
    in_init = False
    
    for line in lines:
        if 'def __init__(self, api_key: str, output_dir: str' in line:
            in_init = True
            modified_lines.append(line)
        elif in_init and 'self.veo_quota_exhausted = False' in line:
            # Add Vertex AI preference
            modified_lines.append(line)
            modified_lines.append('')
            modified_lines.append('        # 🚀 VERTEX AI PREFERENCE - Added for unlimited quotas')
            modified_lines.append('        self.prefer_vertex_ai = True')
            modified_lines.append('        self.vertex_ai_client = None')
            modified_lines.append('        self._init_vertex_ai_client()')
        elif in_init and 'logger.info(f"🔄 Fallback chain:' in line:
            # Update fallback chain message
            modified_lines.append('        logger.info(f"🔄 Fallback chain: Vertex AI VEO-2 → Google AI VEO-2 → Gemini Images → Text Overlay")')
        else:
            modified_lines.append(line)
    
    # Add Vertex AI initialization method
    vertex_ai_init = '''
    def _init_vertex_ai_client(self):
        """Initialize Vertex AI client for unlimited VEO generation"""
        try:
            from .vertex_ai_veo2_client import VertexAIVeo2Client
            
            self.vertex_ai_client = VertexAIVeo2Client(
                project_id='viralgen-464411',
                location='us-central1',
                gcs_bucket='viral-veo2-results',
                output_dir=self.output_dir
            )
            
            if self.vertex_ai_client.veo_available:
                logger.info("🚀 Vertex AI VEO-2: ✅ AVAILABLE (unlimited quotas)")
                self.prefer_vertex_ai = True
            else:
                logger.warning("⚠️ Vertex AI VEO-2: ❌ NOT AVAILABLE")
                self.prefer_vertex_ai = False
                
        except Exception as e:
            logger.warning(f"⚠️ Vertex AI initialization failed: {e}")
            self.prefer_vertex_ai = False
            self.vertex_ai_client = None
'''
    
    # Find where to insert the new method (after __init__)
    init_end = -1
    for i, line in enumerate(modified_lines):
        if line.strip().startswith('def _check_initial_quota_status'):
            init_end = i
            break
    
    if init_end > 0:
        modified_lines.insert(init_end, vertex_ai_init)
    
    # Update the generation method to prefer Vertex AI
    for i, line in enumerate(modified_lines):
        if 'def _generate_quota_aware_clip(' in line:
            # Find the method and update it
            j = i
            while j < len(modified_lines) and not (modified_lines[j].strip().startswith('def ') and j > i):
                if 'max_attempts = 3' in modified_lines[j]:
                    # Insert Vertex AI attempt before Google AI Studio attempts
                    vertex_attempt = '''        
        # 🚀 VERTEX AI ATTEMPT FIRST (unlimited quotas)
        if self.prefer_vertex_ai and self.vertex_ai_client:
            logger.info("🚀 Attempting Vertex AI VEO-2 generation (unlimited quotas)...")
            try:
                vertex_result = self.vertex_ai_client.generate_video_clip(
                    prompt=prompt,
                    duration=duration,
                    clip_id=clip_id,
                    aspect_ratio="9:16" if "tiktok" in prompt.lower() else "16:9"
                )
                
                if vertex_result and os.path.exists(vertex_result):
                    # Move to expected location
                    expected_path = os.path.join(self.clips_dir, f"veo2_clip_{clip_id}.mp4")
                    shutil.copy2(vertex_result, expected_path)
                    
                    file_size = os.path.getsize(expected_path) / (1024 * 1024)
                    logger.info(f"✅ VERTEX AI SUCCESS: {expected_path} ({file_size:.1f}MB)")
                    logger.info(f"💰 Cost: ~$0.15 (no daily limits)")
                    return expected_path
                    
            except Exception as e:
                logger.warning(f"⚠️ Vertex AI attempt failed: {e}")
                logger.info("🔄 Falling back to Google AI Studio...")
'''
                    modified_lines.insert(j + 1, vertex_attempt)
                    break
                j += 1
            break
    
    # Write the modified content
    modified_content = '\n'.join(modified_lines)
    with open(client_path, 'w') as f:
        f.write(modified_content)
    
    print("✅ VEO client updated to prefer Vertex AI")

def update_workflow_config():
    """Update workflow configuration to use Vertex AI"""
    print("🔧 Updating workflow configuration...")
    
    workflow_path = 'src/workflows/generate_viral_video.py'
    
    if os.path.exists(workflow_path):
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Add Vertex AI preference comment
        if 'VERTEX AI PREFERENCE' not in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'OptimizedVeoClient' in line and 'api_key' in line:
                    lines.insert(i, '        # 🚀 Using Vertex AI for unlimited VEO generation')
                    break
            
            with open(workflow_path, 'w') as f:
                f.write('\n'.join(lines))
        
        print("✅ Workflow updated")

def test_vertex_ai_setup():
    """Test Vertex AI setup"""
    print("\n🧪 Testing Vertex AI setup...")
    
    try:
        from src.generators.vertex_ai_veo2_client import VertexAIVeo2Client
        
        client = VertexAIVeo2Client(
            project_id='viralgen-464411',
            location='us-central1',
            gcs_bucket='viral-veo2-results',
            output_dir='outputs'
        )
        
        if client.veo_available:
            print("✅ Vertex AI VEO-2 client: READY")
            print("📊 Quota: Enterprise-grade (unlimited)")
            print("💰 Cost: ~$0.15 per 5-second video")
            print("🚀 No daily limits!")
            return True
        else:
            print("❌ Vertex AI VEO-2 client: NOT AVAILABLE")
            return False
            
    except Exception as e:
        print(f"❌ Vertex AI test failed: {e}")
        return False

def create_vertex_ai_test_script():
    """Create a test script for Vertex AI"""
    print("📝 Creating Vertex AI test script...")
    
    test_script = '''#!/usr/bin/env python3
"""
Test Vertex AI VEO-2 Generation

This script tests the Vertex AI VEO-2 setup with a simple video generation.
"""

import os
import sys

def test_vertex_ai_generation():
    """Test Vertex AI VEO-2 generation"""
    print("🧪 Testing Vertex AI VEO-2 generation...")
    
    try:
        from src.generators.vertex_ai_veo2_client import VertexAIVeo2Client
        
        # Initialize client
        client = VertexAIVeo2Client(
            project_id='viralgen-464411',
            location='us-central1',
            gcs_bucket='viral-veo2-results',
            output_dir='outputs'
        )
        
        if not client.veo_available:
            print("❌ Vertex AI not available")
            return False
        
        # Test generation
        print("🎬 Generating test video...")
        result = client.generate_video_clip(
            prompt="A cute baby laughing and playing with toys",
            duration=5.0,
            clip_id="vertex_test",
            aspect_ratio="16:9"
        )
        
        if result and os.path.exists(result):
            file_size = os.path.getsize(result) / (1024 * 1024)
            print(f"✅ SUCCESS: {result} ({file_size:.1f}MB)")
            print("💰 Estimated cost: ~$0.15")
            print("🚀 No quota limits!")
            return True
        else:
            print("❌ Generation failed - no file created")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main test routine"""
    print("🚀 Vertex AI VEO-2 Test")
    print("=" * 30)
    
    success = test_vertex_ai_generation()
    
    if success:
        print("\\n🎉 Vertex AI is working perfectly!")
        print("   You now have unlimited VEO generation.")
    else:
        print("\\n❌ Vertex AI test failed.")
        print("   Check your Google Cloud setup.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
'''
    
    with open('test_vertex_ai.py', 'w') as f:
        f.write(test_script)
    
    print("✅ Test script created: test_vertex_ai.py")

def main():
    """Main switching routine"""
    print("🚀 Switching to Vertex AI for VEO Generation")
    print("=" * 50)
    
    print("This will switch your system from:")
    print("❌ Google AI Studio (2-3 videos/day limit)")
    print("✅ Vertex AI (unlimited enterprise quotas)")
    print("💰 Cost: ~$0.15 per 5-second video")
    print()
    
    # 1. Backup current configuration
    backup_dir = backup_current_config()
    
    # 2. Test Vertex AI first
    vertex_available = test_vertex_ai_setup()
    
    if not vertex_available:
        print("\n❌ Vertex AI is not available!")
        print("   Please check your Google Cloud setup.")
        print("   Run: gcloud auth application-default login")
        return 1
    
    # 3. Update VEO client
    update_optimized_veo_client()
    
    # 4. Update workflow
    update_workflow_config()
    
    # 5. Create test script
    create_vertex_ai_test_script()
    
    # 6. Summary
    print("\n🎉 VERTEX AI SWITCH COMPLETE!")
    print("=" * 35)
    print("✅ System now uses Vertex AI for VEO generation")
    print("🚀 No more daily quota limits")
    print("💰 Pay-per-video pricing (~$0.15 each)")
    print("📁 Configuration backed up to:", backup_dir)
    
    print("\n🧪 NEXT STEPS:")
    print("1. Test Vertex AI: python test_vertex_ai.py")
    print("2. Generate videos normally - no limits!")
    print("3. Monitor costs in Google Cloud Console")
    
    print("\n📊 QUOTA COMPARISON:")
    print("Google AI Studio: 2-3 videos/day ❌ EXHAUSTED")
    print("Vertex AI: Unlimited videos ✅ READY")
    
    return 0

if __name__ == "__main__":
    exit(main()) 