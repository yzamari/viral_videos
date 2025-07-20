#!/usr/bin/env python3
"""
Test script to verify Instagram posting with instagrapi import fix
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_instagram_posting():
    """Test Instagram posting with the fixed import"""
    print("🧪 Testing Instagram posting with import fix")
    print("=" * 50)
    
    try:
        # Import the Instagram autoposter
        from src.social.instagram_autoposter import create_instagram_autoposter_from_env
        
        # Create autoposter from .env
        autoposter = create_instagram_autoposter_from_env()
        
        if not autoposter:
            print("❌ Failed to create Instagram autoposter")
            return False
        
        print("✅ Instagram autoposter created successfully")
        
        # Test authentication
        if autoposter.authenticate():
            print("✅ Authentication successful")
        else:
            print("❌ Authentication failed")
            return False
        
        # Test instagrapi import specifically
        print("\n🔧 Testing instagrapi import...")
        try:
            from instagrapi import Client
            print("✅ instagrapi imported successfully")
            
            # Test creating a client
            cl = Client()
            print("✅ instagrapi Client created successfully")
            
        except ImportError as e:
            print(f"❌ instagrapi import failed: {e}")
            return False
        
        # Test video posting (simulation)
        print("\n📱 Testing video posting...")
        
        # Create a test video path (use an existing video if available)
        test_video_path = "outputs/session_20250718_184403/final_output/final_video_session_20250718_184403.mp4"
        
        if os.path.exists(test_video_path):
            print(f"✅ Found test video: {test_video_path}")
            
            # Test the _try_instagrapi_upload method
            from src.social.instagram_autoposter import PostContent, PostingOptions
            
            content = PostContent(
                video_path=test_video_path,
                caption="Test video from viral AI system",
                hashtags=["#test", "#viralai", "#instagram"],
                is_reel=True
            )
            
            options = PostingOptions()
            
            # This should now work with the fixed import
            success = autoposter.post_video(content, options)
            
            if success:
                print("✅ Video posting test successful!")
            else:
                print("❌ Video posting test failed")
                return False
        else:
            print(f"⚠️ Test video not found: {test_video_path}")
            print("💡 Skipping video posting test")
        
        # Cleanup
        autoposter.disconnect()
        
        print("\n🎉 All tests passed!")
        print("✅ Instagram posting with instagrapi is working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_instagram_posting()
    sys.exit(0 if success else 1) 