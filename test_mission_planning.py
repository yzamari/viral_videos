#!/usr/bin/env python3
"""
Test script for Mission Planning Agent and AI-driven clip structure optimization
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.mission_planning_agent import MissionPlanningAgent, MissionType
from src.models.video_models import Platform, VideoCategory
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

def test_mission_planning_agent():
    """Test the Mission Planning Agent with different mission types"""
    
    print("🎯 Testing Mission Planning Agent...")
    
    # Get API key
    api_key = os.getenv("GOOGLE_AI_API_KEY")
    if not api_key:
        print("❌ No API key found. Please set GOOGLE_AI_API_KEY environment variable.")
        return
    
    # Initialize Mission Planning Agent
    agent = MissionPlanningAgent(api_key)
    
    # Test different mission types
    test_cases = [
        {
            "mission": "Convince people to stop smoking",
            "duration": 15,
            "platform": Platform.INSTAGRAM,
            "category": VideoCategory.HEALTH,
            "expected_type": MissionType.CONVINCE
        },
        {
            "mission": "Teach kids about recycling",
            "duration": 20,
            "platform": Platform.YOUTUBE,
            "category": VideoCategory.EDUCATIONAL,
            "expected_type": MissionType.TEACH
        },
        {
            "mission": "Explain why renewable energy is important",
            "duration": 30,
            "platform": Platform.TIKTOK,
            "category": VideoCategory.SCIENCE,
            "expected_type": MissionType.EXPLAIN
        },
        {
            "mission": "The history of artificial intelligence",
            "duration": 25,
            "platform": Platform.YOUTUBE,
            "category": VideoCategory.EDUCATIONAL,
            "expected_type": MissionType.INFORM
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['mission']}")
        print(f"   Duration: {test_case['duration']}s")
        print(f"   Platform: {test_case['platform'].value}")
        print(f"   Expected Type: {test_case['expected_type'].value}")
        
        try:
            # Analyze mission
            mission_plan = agent.analyze_mission(
                mission_statement=test_case['mission'],
                duration=test_case['duration'],
                platform=test_case['platform'],
                category=test_case['category']
            )
            
            # Get clip recommendations
            clip_recommendation = agent.get_clip_recommendation(mission_plan)
            
            print(f"   ✅ Mission Analysis Complete:")
            print(f"      Mission Type: {mission_plan.mission_type.value}")
            print(f"      Strategic Mission: {mission_plan.is_strategic_mission}")
            print(f"      Target Outcome: {mission_plan.target_outcome}")
            print(f"      Confidence: {mission_plan.confidence_score:.2f}")
            print(f"      Recommended Clips: {clip_recommendation['num_clips']}")
            print(f"      Clip Durations: {[f'{d:.1f}s' for d in clip_recommendation['clip_durations']]}")
            print(f"      Cost Efficiency: {clip_recommendation['cost_efficiency_score']:.2f}")
            print(f"      Content Quality: {clip_recommendation['content_quality_score']:.2f}")
            print(f"      Balance Score: {clip_recommendation['optimal_balance_score']:.2f}")
            print(f"      Reasoning: {clip_recommendation['reasoning'][:100]}...")
            
            # Verify mission type detection
            if mission_plan.mission_type == test_case['expected_type']:
                print(f"   ✅ Mission type correctly detected!")
            else:
                print(f"   ⚠️  Mission type mismatch: expected {test_case['expected_type'].value}, got {mission_plan.mission_type.value}")
                
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
    
    print("\n🎯 Mission Planning Agent testing complete!")

def test_clip_structure_logic():
    """Test the clip structure logic specifically"""
    
    print("\n🎬 Testing Clip Structure Logic...")
    
    # Test different duration scenarios
    test_durations = [10, 15, 20, 30, 45]
    
    for duration in test_durations:
        print(f"\n⏱️  Testing {duration}s duration:")
        
        # Compare old vs new logic
        old_logic = max(2, min(5, duration // 3))
        print(f"   Old Logic (duration // 3): {old_logic} clips")
        
        # Test with different mission types
        missions = [
            ("Convince people to vote", MissionType.CONVINCE),
            ("Teach guitar basics", MissionType.TEACH),
            ("Climate change facts", MissionType.INFORM)
        ]
        
        for mission, expected_type in missions:
            print(f"   Mission: {mission}")
            print(f"   Expected optimization based on mission type: {expected_type.value}")
            
            # Heuristic-based logic
            if expected_type in [MissionType.CONVINCE, MissionType.PERSUADE]:
                # Persuasion missions need fewer, longer clips for coherent arguments
                recommended_clips = 2 if duration <= 20 else 3
            elif expected_type in [MissionType.TEACH, MissionType.DEMONSTRATE]:
                # Teaching missions benefit from more clips for step-by-step progression
                recommended_clips = max(2, min(4, duration // 7))
            elif expected_type == MissionType.INFORM:
                # Informational content uses standard approach
                recommended_clips = max(2, duration // 5)
            else:
                # Default approach
                recommended_clips = max(2, duration // 8)
            
            print(f"   New Logic (mission-based): {recommended_clips} clips")
            
            # Cost efficiency analysis
            cost_score = max(0, 1 - (recommended_clips - 2) * 0.2)
            quality_score = min(1, recommended_clips * 0.25)
            balance_score = (cost_score + quality_score) / 2
            
            print(f"   Cost Efficiency: {cost_score:.2f}")
            print(f"   Content Quality: {quality_score:.2f}")
            print(f"   Balance Score: {balance_score:.2f}")
            print()

if __name__ == "__main__":
    test_mission_planning_agent()
    test_clip_structure_logic()