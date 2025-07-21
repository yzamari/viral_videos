#!/usr/bin/env python3
"""
Test script to verify professional mode fix
Ensures that professional mode uses all 22 agents and integrates their decisions
"""

import os
import sys
import asyncio
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

async def test_professional_mode():
    """Test professional mode with all 22 agents"""
    print("🧪 Testing Professional Mode Fix")
    print("=" * 60)
    
    try:
        # Import the orchestrator
        from src.agents.working_orchestrator import WorkingOrchestrator, OrchestratorMode
        from src.models.video_models import Platform, VideoCategory
        
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("❌ No API key found. Please set GOOGLE_API_KEY environment variable.")
            return False
        
        print("✅ API key found")
        
        # Create professional mode orchestrator
        print("🎯 Creating Professional Mode Orchestrator...")
        orchestrator = WorkingOrchestrator(
            api_key=api_key,
            mission="Test professional mode with all 22 agents",
            platform=Platform.TIKTOK,
            category=VideoCategory.ENTERTAINMENT,
            duration=30,
            mode=OrchestratorMode.PROFESSIONAL,
            cheap_mode=False,  # Ensure no cheap mode
            session_id=f"test_professional_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        print(f"✅ Orchestrator created - Session: {orchestrator.session_id}")
        print(f"🎭 Mode: {orchestrator.mode.value}")
        print(f"💰 Cheap mode: {orchestrator.cheap_mode}")
        
        # Test configuration
        config = {
            'topic': "Test professional mode with all 22 agents",
            'platform': 'tiktok',
            'category': 'entertainment',
            'duration': 30,
            'style': 'viral',
            'tone': 'engaging',
            'target_audience': 'general audience',
            'visual_style': 'dynamic',
            'use_subtitle_overlays': True,
            'frame_continuity': True,
            'cheap_mode': False
        }
        
        print("🎬 Starting professional mode video generation...")
        start_time = datetime.now()
        
        # Generate video
        result = await orchestrator.generate_video(config)
        
        generation_time = (datetime.now() - start_time).total_seconds()
        
        print(f"⏱️ Generation completed in {generation_time:.1f} seconds")
        
        if result and result.get('success'):
            print("✅ Video generation successful!")
            
            # Check professional mode details
            professional_details = result.get('professional_mode_details')
            if professional_details:
                print("\n🎯 PROFESSIONAL MODE DETAILS:")
                print(f"   Total Agents: {professional_details['total_agents']}")
                print(f"   Base Agents: {professional_details['base_agents']}")
                print(f"   Discussion Agents: {professional_details['discussion_agents']}")
                print(f"   Discussions Completed: {professional_details['discussions_completed']}")
                print(f"   All Agents Utilized: {professional_details['all_agents_utilized']}")
                
                # Verify all 22 agents were used
                if professional_details['total_agents'] >= 22:
                    print("✅ SUCCESS: All 22+ agents were utilized!")
                else:
                    print(f"❌ FAILURE: Only {professional_details['total_agents']} agents used, expected 22+")
                    return False
                
                # Verify discussions were conducted
                if professional_details['discussions_completed'] >= 7:
                    print("✅ SUCCESS: All 7 professional discussions were conducted!")
                else:
                    print(f"❌ FAILURE: Only {professional_details['discussions_completed']} discussions completed, expected 7")
                    return False
                
            else:
                print("❌ FAILURE: No professional mode details found")
                return False
            
            print(f"\n📁 Output: {result.get('final_video_path')}")
            print(f"🎭 Mode: {result.get('mode')}")
            print(f"🤖 Agents Used: {result.get('agents_used')}")
            print(f"💬 Discussions: {result.get('discussions_conducted')}")
            
            return True
            
        else:
            print("❌ Video generation failed")
            if result:
                print(f"Error: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Starting Professional Mode Fix Test")
    print("=" * 60)
    
    success = asyncio.run(test_professional_mode())
    
    if success:
        print("\n✅ PROFESSIONAL MODE FIX TEST PASSED!")
        print("🎯 All 22 agents are now properly utilized in professional mode")
    else:
        print("\n❌ PROFESSIONAL MODE FIX TEST FAILED!")
        print("🔧 The fix needs further investigation")
    
    return success

if __name__ == "__main__":
    main() 