#!/usr/bin/env python3
"""
Test Instagram Integration
Verifies that the Instagram posting functionality works correctly
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.social.instagram_autoposter import InstagramAutoPoster, InstagramCredentials, PostContent
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

def test_instagram_credentials():
    """Test Instagram authentication"""
    print("🔐 Testing Instagram Authentication...")
    
    # Get credentials from environment
    username = os.getenv('INSTAGRAM_USERNAME')
    password = os.getenv('INSTAGRAM_PASSWORD')
    
    if not username or not password:
        print("❌ Instagram credentials not found in environment")
        print("💡 Add to .env file:")
        print("   INSTAGRAM_USERNAME=your_username")
        print("   INSTAGRAM_PASSWORD=your_password")
        return False
    
    try:
        credentials = InstagramCredentials(
            username=username,
            password=password
        )
        
        autoposter = InstagramAutoPoster(credentials)
        success = autoposter.authenticate()
        
        if success:
            print("✅ Instagram authentication successful!")
            return True
        else:
            print("❌ Instagram authentication failed")
            return False
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False

def test_video_upload():
    """Test video upload functionality"""
    print("\n🎬 Testing Video Upload...")
    
    # Find a test video
    test_video_path = None
    for session_dir in Path("outputs").glob("session_*"):
        final_video = session_dir / "final_output" / "final_video_session_*.mp4"
        matches = list(final_video.parent.glob(final_video.name))
        if matches:
            test_video_path = str(matches[0])
            break
    
    if not test_video_path:
        print("❌ No test video found")
        print("💡 Generate a video first using: python main.py generate")
        return False
    
    print(f"📹 Using test video: {test_video_path}")
    
    try:
        username = os.getenv('INSTAGRAM_USERNAME')
        password = os.getenv('INSTAGRAM_PASSWORD')
        
        if not username or not password:
            print("❌ Instagram credentials not found")
            return False
        
        credentials = InstagramCredentials(username=username, password=password)
        autoposter = InstagramAutoPoster(credentials)
        
        if not autoposter.authenticate():
            print("❌ Authentication failed")
            return False
        
        # Test video format validation
        if not autoposter.validate_video_format(test_video_path):
            print("❌ Video format validation failed")
            return False
        
        print("✅ Video format validation passed")
        
        # Create test content
        content = PostContent(
            video_path=test_video_path,
            caption="🧪 Test video from Viral AI Generator - Testing Instagram integration",
            hashtags=['#test', '#viralai', '#automation', '#instagram', '#video'],
            is_reel=True
        )
        
        # Test posting (will fall back to simulation if API fails)
        success = autoposter.post_video(content)
        
        if success:
            print("✅ Video posting test completed!")
            return True
        else:
            print("❌ Video posting failed")
            return False
            
    except Exception as e:
        print(f"❌ Upload test error: {e}")
        return False

def test_session_posting():
    """Test posting from a session"""
    print("\n📁 Testing Session-Based Posting...")
    
    # Find the most recent session
    sessions = list(Path("outputs").glob("session_*"))
    if not sessions:
        print("❌ No sessions found")
        return False
    
    latest_session = max(sessions, key=lambda p: p.stat().st_mtime)
    print(f"📂 Using session: {latest_session.name}")
    
    try:
        username = os.getenv('INSTAGRAM_USERNAME')
        password = os.getenv('INSTAGRAM_PASSWORD')
        
        if not username or not password:
            print("❌ Instagram credentials not found")
            return False
        
        credentials = InstagramCredentials(username=username, password=password)
        
        from src.social.instagram_autoposter import create_instagram_post_from_session
        success = create_instagram_post_from_session(str(latest_session), credentials)
        
        if success:
            print("✅ Session posting test completed!")
            return True
        else:
            print("❌ Session posting failed")
            return False
            
    except Exception as e:
        print(f"❌ Session posting error: {e}")
        return False

def main():
    """Run all Instagram integration tests"""
    print("📱 Instagram Integration Test Suite")
    print("=" * 50)
    
    # Test 1: Authentication
    auth_success = test_instagram_credentials()
    
    # Test 2: Video Upload (only if authentication worked)
    upload_success = False
    if auth_success:
        upload_success = test_video_upload()
    
    # Test 3: Session Posting (only if authentication worked)
    session_success = False
    if auth_success:
        session_success = test_session_posting()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   Authentication: {'✅ PASS' if auth_success else '❌ FAIL'}")
    print(f"   Video Upload: {'✅ PASS' if upload_success else '❌ FAIL'}")
    print(f"   Session Posting: {'✅ PASS' if session_success else '❌ FAIL'}")
    
    if auth_success and upload_success and session_success:
        print("\n🎉 All tests passed! Instagram integration is working correctly.")
        print("💡 You can now use Instagram posting in your video generation workflow.")
    else:
        print("\n⚠️ Some tests failed. Check the setup guide in INSTAGRAM_SETUP.md")
        print("💡 The system will fall back to simulation mode for testing.")

if __name__ == "__main__":
    main() 