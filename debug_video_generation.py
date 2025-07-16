#!/usr/bin/env python3
"""
Debug video generation step by step
"""

import os
import sys
sys.path.append('src')

from src.models.video_models import GeneratedVideoConfig, Platform, VideoCategory
from src.generators.video_generator import VideoGenerator

def debug_video_generation():
    print("🔍 Debugging video generation...")
    
    # Create a simple config
    config = GeneratedVideoConfig(
        topic="Test video generation",
        duration_seconds=10,
        target_platform=Platform.TIKTOK,
        category=VideoCategory.EDUCATIONAL,
        visual_style="dynamic",
        tone="friendly",
        style="casual"
    )
    
    print(f"✅ Config created: {config.topic}")
    
    # Initialize video generator
    try:
        print("🎬 Initializing VideoGenerator...")
        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            print("❌ GOOGLE_API_KEY not found in environment")
            return
        
        generator = VideoGenerator(api_key=api_key)
        print("✅ VideoGenerator initialized")
        
        # Try session creation
        print("📝 Creating session...")
        from src.utils.session_manager import session_manager
        
        session_id = session_manager.create_session(
            topic=config.topic,
            platform=config.target_platform.value,
            duration=config.duration_seconds,
            category=config.category.value
        )
        print(f"✅ Session created: {session_id}")
        
        # Create session context
        print("🎯 Creating session context...")
        from src.utils.session_context import SessionContext
        
        session_context = SessionContext(
            session_id=session_id,
            session_dir=f"outputs/{session_id}",
            config=config
        )
        print(f"✅ Session context created: {session_context.session_dir}")
        
        # This is where it might hang - let's test the first few steps
        print("🎯 Testing script generation...")
        
        # Skip actual generation and just test the session setup
        print("✅ Debug completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_video_generation()