#!/usr/bin/env python3
"""
Instagram Posting Unit Test
Tests the Instagram posting functionality with real credentials
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

def test_instagram_posting():
    """Test Instagram posting with real credentials"""
    print("📱 Instagram Posting Unit Test")
    print("=" * 50)
    
    # Test credentials
    username = "yzamari@gmail.com"
    password = "Nvnnh@123"
    
    # Find a test video
    test_video_path = "outputs/session_20250718_173213/final_output/final_video_session_20250718_173213.mp4"
    
    if not os.path.exists(test_video_path):
        print(f"❌ Test video not found: {test_video_path}")
        return False
    
    print(f"📹 Using test video: {test_video_path}")
    print(f"👤 Username: {username}")
    
    try:
        # Step 1: Create credentials and autoposter
        print("\n🔐 Step 1: Creating Instagram autoposter...")
        credentials = InstagramCredentials(
            username=username,
            password=password
        )
        
        autoposter = InstagramAutoPoster(credentials)
        print("✅ Instagram autoposter created")
        
        # Step 2: Authenticate
        print("\n🔐 Step 2: Authenticating with Instagram...")
        auth_success = autoposter.authenticate()
        
        if not auth_success:
            print("❌ Authentication failed")
            return False
        
        print("✅ Authentication successful!")
        
        # Step 3: Validate video format
        print("\n🎬 Step 3: Validating video format...")
        if not autoposter.validate_video_format(test_video_path):
            print("❌ Video format validation failed")
            return False
        
        print("✅ Video format validation passed")
        
        # Step 4: Create post content
        print("\n📝 Step 4: Creating post content...")
        content = PostContent(
            video_path=test_video_path,
            caption="🧪 Unit Test: Viral AI Video Generator - Testing Instagram posting functionality with real credentials. This video was automatically generated and posted using our AI system! 🚀",
            hashtags=[
                '#viralai', '#automation', '#instagram', '#video', '#test', 
                '#ai', '#content', '#socialmedia', '#automation', '#technology'
            ],
            is_reel=True
        )
        print("✅ Post content created")
        
        # Step 5: Post the video
        print("\n📤 Step 5: Posting video to Instagram...")
        print("📝 Caption preview:", content.caption[:100] + "...")
        print("🏷️ Hashtags:", " ".join(content.hashtags[:5]) + "...")
        
        post_success = autoposter.post_video(content)
        
        if post_success:
            print("✅ Video posted successfully!")
            print("🎉 Instagram posting unit test PASSED!")
            return True
        else:
            print("❌ Video posting failed")
            print("💡 This might be due to:")
            print("   - Instagram API restrictions")
            print("   - Rate limiting")
            print("   - Account verification requirements")
            print("   - The system falling back to simulation mode")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_session_posting():
    """Test posting from a session directory"""
    print("\n📁 Session-Based Posting Test")
    print("=" * 50)
    
    session_path = "outputs/session_20250718_173213"
    
    if not os.path.exists(session_path):
        print(f"❌ Session not found: {session_path}")
        return False
    
    try:
        username = "yzamari@gmail.com"
        password = "Nvnnh@123"
        
        credentials = InstagramCredentials(username=username, password=password)
        
        from src.social.instagram_autoposter import create_instagram_post_from_session
        success = create_instagram_post_from_session(session_path, credentials)
        
        if success:
            print("✅ Session posting successful!")
            return True
        else:
            print("❌ Session posting failed")
            return False
            
    except Exception as e:
        print(f"❌ Session posting error: {e}")
        return False

def main():
    """Run the Instagram posting unit tests"""
    print("🧪 Instagram Posting Unit Test Suite")
    print("=" * 60)
    
    # Test 1: Direct posting
    print("\n🎯 Test 1: Direct Video Posting")
    posting_success = test_instagram_posting()
    
    # Test 2: Session-based posting
    print("\n🎯 Test 2: Session-Based Posting")
    session_success = test_session_posting()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Unit Test Results:")
    print(f"   Direct Posting: {'✅ PASS' if posting_success else '❌ FAIL'}")
    print(f"   Session Posting: {'✅ PASS' if session_success else '❌ FAIL'}")
    
    if posting_success or session_success:
        print("\n🎉 At least one posting method worked!")
        print("💡 The Instagram integration is functional.")
        if not posting_success and not session_success:
            print("⚠️ Both methods failed, but this might be due to Instagram API restrictions.")
            print("💡 The system will fall back to simulation mode for testing.")
    else:
        print("\n⚠️ Both posting methods failed.")
        print("💡 Check Instagram account status and API restrictions.")

if __name__ == "__main__":
    main() 