#!/usr/bin/env python3
"""Test the fixed AI agent discussion system """import os
import sys
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')


def test_discussion_system(): """Test if the discussion system is working correctly"""print("🧪 Testing Fixed AI Agent Discussion System") print("=" * 50)

    # Load API key api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    if not api_key: print("❌ No API key found")
        return False
 print(f"✅ API key loaded (length: {len(api_key)})")

    try:
        # Import required modules
        from agents.multi_agent_discussion import MultiAgentDiscussionSystem, DiscussionTopic, AgentRole
 # Test session ID test_session_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"print(f"🔧 Test session: {test_session_id}")

        # Create discussion system
        discussion_system = MultiAgentDiscussionSystem(api_key, test_session_id) print("✅ Discussion system created")

        # Test mission test_mission = "Create an engaging educational video about renewable energy"# Create test topic
        topic = DiscussionTopic( topic_id="test_renewable_energy", title="Renewable Energy Video Strategy", description=f"Develop the best approach for: {test_mission}",
            context={ 'mission': test_mission, 'platform': 'youtube', 'duration': 60, 'category': 'education', 'style': 'engaging', 'target_audience': 'general public'}, required_decisions=["script_approach", "visual_style", "engagement_strategy"]
        )
 print(f"🎯 Testing discussion about: {test_mission}")

        # Test with 2 agents for quick results
        participating_agents = [AgentRole.SCRIPT_WRITER, AgentRole.DIRECTOR]

        # Start discussion print("🎭 Starting AI agent discussion...")
        result = discussion_system.start_discussion(topic, participating_agents) print("✅ Discussion completed!") print(f"   Topic: {result.topic_id}") print(f"   Consensus: {result.consensus_level:.2f}") print(f"   Rounds: {result.total_rounds}") print(f"   Participants: {', '.join(result.participating_agents)}")

        # Check if decision contains actual mission content
        decision_str = json.dumps(result.decision, indent=2) print(f"📋 Decision preview: {decision_str[:200]}...")

        # Test if the discussion is about the actual mission mission_keywords = ['renewable', 'energy', 'educational', 'video']
        decision_text = decision_str.lower()

        relevant_keywords = [kw for kw in mission_keywords if kw in decision_text]

        if len(relevant_keywords) >= 2: print(f"✅ Discussion is RELEVANT to mission (keywords: {relevant_keywords})")
            return True
        else: print(f"❌ Discussion seems OFF-TOPIC (found keywords: {relevant_keywords})") print(f"   Full decision: {decision_str}")
            return False

    except Exception as e: print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

 if __name__ == "__main__":
    success = test_discussion_system()
    if success: print("\n🎉 AI Agent Discussion System is WORKING CORRECTLY!")
    else: print("\n❌ AI Agent Discussion System has ISSUES!")

    exit(0 if success else 1)
