#!/usr/bin/env python3
"""
Real Instagram Posting Test with instagrapi
Posts a video to Instagram and returns the actual post link
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.logging_config import get_logger

logger = get_logger(__name__)

def test_real_instagram_posting():
    """Test real Instagram posting with instagrapi and return the post link"""
    print("🚀 Real Instagram Posting Test with instagrapi")
    print("=" * 60)
    
    # Test credentials
    username = "Veo.calculus"
    password = "Nvnnh@123"
    
    # Find a test video
    test_video_path = "outputs/session_20250718_173213/final_output/final_video_session_20250718_173213.mp4"
    
    if not os.path.exists(test_video_path):
        print(f"❌ Test video not found: {test_video_path}")
        return None
    
    print(f"📹 Using test video: {test_video_path}")
    print(f"👤 Username: {username}")
    
    try:
        # Import instagrapi
        try:
            from instagrapi import Client
            print("✅ instagrapi imported successfully")
        except ImportError as e:
            print(f"❌ instagrapi import failed: {e}")
            return None
        
        # Step 1: Initialize instagrapi client
        print("\n🔧 Step 1: Initializing instagrapi client...")
        cl = Client()
        print("✅ instagrapi client initialized")
        
        # Step 2: Login with credentials
        print("\n🔐 Step 2: Logging in to Instagram...")
        login_success = cl.login(
            username=username,
            password=password
        )
        
        if not login_success:
            print("❌ Instagram login failed")
            return None
        
        print("✅ Instagram login successful!")
        
        # Step 3: Validate video file
        print("\n🎬 Step 3: Validating video file...")
        video_path_obj = Path(test_video_path)
        if not video_path_obj.exists():
            print("❌ Video file not found")
            return None
        
        print(f"✅ Video file found: {video_path_obj}")
        
        # Step 4: Create caption
        print("\n📝 Step 4: Creating post caption...")
        caption = """🧪 Real Instagram Post Test!

This video was automatically generated and posted using our Viral AI Video Generator with instagrapi integration! 

🚀 Features tested:
✅ AI-generated content
✅ Automated video creation
✅ Real Instagram posting
✅ Line-by-line text overlays

#viralai #automation #instagram #video #test #ai #content #socialmedia #technology #innovation #viral #trending #reels #automation #future"""
        
        print(f"📝 Caption length: {len(caption)} characters")
        
        # Step 5: Upload as Reel
        print("\n📤 Step 5: Uploading video as Instagram Reel...")
        print("⏳ This may take a few minutes...")
        
        try:
            media = cl.clip_upload(
                path=video_path_obj,
                caption=caption
            )
            
            if media:
                post_url = f"https://www.instagram.com/p/{media.code}/"
                print("✅ Video uploaded successfully!")
                print(f"📊 Media ID: {media.id}")
                print(f"🔗 Post URL: {post_url}")
                return post_url
            else:
                print("❌ Upload returned no media object")
                return None
                
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            print("💡 This might be due to:")
            print("   - Instagram rate limiting")
            print("   - Account restrictions")
            print("   - Video format issues")
            print("   - Network connectivity")
            return None
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Run the real Instagram posting test"""
    print("🧪 Real Instagram Posting Test Suite")
    print("=" * 60)
    
    # Run the real posting test
    post_url = test_real_instagram_posting()
    
    # Results
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    
    if post_url:
        print("✅ SUCCESS: Real Instagram posting worked!")
        print(f"🔗 Your Instagram post: {post_url}")
        print("\n🎉 The video has been posted to your Instagram account!")
        print("💡 You can view it by clicking the link above.")
    else:
        print("❌ FAILED: Real Instagram posting did not work")
        print("💡 The system will fall back to simulation mode for testing.")
        print("🔧 Check Instagram account status and try again later.")

if __name__ == "__main__":
    main() 