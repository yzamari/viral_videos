#!/usr/bin/env python3
"""
Test script for Multi-Agent Discussion System
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import settings
from src.agents.multi_agent_discussion import (
    MultiAgentDiscussionSystem, 
    AgentRole, 
    DiscussionTopic,
    VideoGenerationTopics
)

def test_basic_discussion():
    """Test basic multi-agent discussion functionality"""
    
    if not settings.google_api_key:
        print("❌ Error: GOOGLE_API_KEY not found")
        return
    
    print("🤖 Testing Multi-Agent Discussion System")
    print("=" * 50)
    
    # Create discussion system
    session_id = "test_20250106_123456"
    discussion_system = MultiAgentDiscussionSystem(
        api_key=settings.google_api_key,
        session_id=session_id
    )
    
    # Create a simple discussion topic
    topic = DiscussionTopic(
        topic_id="test_script_optimization",
        title="Test Script Optimization",
        description="Determine the best approach for a funny cat video script",
        context={
            'topic': 'funny cats doing silly things',
            'platform': 'youtube',
            'duration': 30,
            'category': 'Comedy'
        },
        required_decisions=[
            "hook_strategy",
            "content_structure", 
            "viral_elements"
        ],
        max_rounds=3,
        min_consensus=0.6
    )
    
    # Participating agents
    participating_agents = [
        AgentRole.SCRIPT_WRITER,
        AgentRole.TREND_ANALYST,
        AgentRole.DIRECTOR
    ]
    
    print(f"💬 Starting discussion: {topic.title}")
    print(f"👥 Participants: {', '.join([agent.value for agent in participating_agents])}")
    
    try:
        # Conduct the discussion
        result = discussion_system.start_discussion(topic, participating_agents)
        
        # Display results
        print("\n🎯 DISCUSSION RESULTS:")
        print(f"   Topic: {result.topic_id}")
        print(f"   Consensus Level: {result.consensus_level:.2f}")
        print(f"   Total Rounds: {result.total_rounds}")
        print(f"   Participants: {', '.join(result.participating_agents)}")
        
        print("\n💡 Key Insights:")
        for insight in result.key_insights:
            print(f"   • {insight}")
        
        print("\n🔄 Alternative Approaches:")
        for alt in result.alternative_approaches:
            print(f"   • {alt}")
        
        print("\n📋 Final Decision:")
        for key, value in result.decision.items():
            print(f"   {key}: {value}")
        
        print("\n✅ Discussion test completed successfully!")
        
    except Exception as e:
        print(f"❌ Discussion test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_basic_discussion() 