#!/usr/bin/env python3
"""
Test script for migrated mission planning agent
"""
import asyncio
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.agents.mission_planning_agent import MissionPlanningAgent
from src.models.video_models import Platform, VideoCategory
from src.ai.manager import AIServiceManager

async def test_mission_planning():
    """Test the migrated mission planning agent"""
    try:
        print("🔧 Testing migrated mission planning agent...")
        
        # Create AI service manager
        ai_manager = AIServiceManager()
        
        # Create mission planning agent with AI manager
        agent = MissionPlanningAgent(ai_manager=ai_manager)
        print(f"✅ Created mission planning agent")
        
        # Test mission analysis
        mission = "Choose a character from the Persian history and teach kids about her"
        
        print("🚀 Testing mission analysis...")
        plan = await agent.analyze_mission(
            mission_statement=mission,
            duration=30,
            platform=Platform.TIKTOK,
            category=VideoCategory.ENTERTAINMENT,
            target_audience="kids"
        )
        
        print(f"✅ Mission analysis successful!")
        print(f"   Mission type: {plan.mission_type}")
        print(f"   Strategic: {plan.is_strategic_mission}")
        print(f"   Target outcome: {plan.target_outcome[:100]}...")
        print(f"   Strategic approach: {plan.strategic_approach[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mission_planning())
    sys.exit(0 if success else 1)