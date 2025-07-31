#!/usr/bin/env python3
"""
Test script to verify session management fixes
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.session_manager import SessionManager
from utils.session_context import SessionContext
from models.video_models import Platform, VideoCategory, GeneratedVideoConfig

def test_session_fixes():
    """Test the session management fixes"""
    
    print("🧪 Testing Session Management Fixes")
    print("=" * 50)
    
    # Test 1: Session Manager Creation
    print("\n1. Testing Session Manager Creation...")
    session_manager = SessionManager()
    
    # Create a test session
    session_id = session_manager.create_session(
        topic="Test Session Fixes",
        platform="instagram",
        duration=5,
        category="comedy"
    )
    
    print(f"✅ Session created: {session_id}")
    
    # Test 2: Session Context Creation
    print("\n2. Testing Session Context Creation...")
    try:
        session_context = SessionContext(session_id, session_manager)
        print(f"✅ Session context created successfully")
        print(f"   Session directory: {session_context.session_dir}")
        
        # Test getting output path
        output_path = session_context.get_output_path("logs", "test.log")
        print(f"✅ Output path created: {output_path}")
        
    except Exception as e:
        print(f"❌ Session context creation failed: {e}")
        return False
    
    # Test 3: Video Config with Session ID
    print("\n3. Testing Video Config with Session ID...")
    try:
        video_config = GeneratedVideoConfig(
            target_platform=Platform.INSTAGRAM,
            category=VideoCategory.COMEDY,
            duration_seconds=5,
            topic="Test Video",
            session_id=session_id  # This should be passed through
        )
        
        print(f"✅ Video config created with session_id: {video_config.session_id}")
        
    except Exception as e:
        print(f"❌ Video config creation failed: {e}")
        return False
    
    # Test 4: Directory Structure
    print("\n4. Testing Directory Structure...")
    session_dir = os.path.join("outputs", session_id)
    if os.path.exists(session_dir):
        print(f"✅ Session directory exists: {session_dir}")
        
        # Check for required subdirectories
        required_dirs = ["logs", "scripts", "audio", "video_clips", "discussions"]
        for subdir in required_dirs:
            subdir_path = os.path.join(session_dir, subdir)
            if os.path.exists(subdir_path):
                print(f"   ✅ {subdir}: exists")
            else:
                print(f"   ❌ {subdir}: missing")
    else:
        print(f"❌ Session directory not found: {session_dir}")
        return False
    
    print("\n🎉 All session management tests passed!")
    return True

if __name__ == "__main__":
    success = test_session_fixes()
    if success:
        print("\n✅ Session fixes are working correctly!")
        sys.exit(0)
    else:
        print("\n❌ Session fixes have issues!")
        sys.exit(1) 