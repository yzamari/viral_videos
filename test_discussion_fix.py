#!/usr/bin/env python3
"""Quick test to verify the discussion prompt template fix """from agents.multi_agent_discussion import MultiAgentDiscussionSystem, DiscussionTopic, AgentRole
import os
import sys
sys.path.append('src')


def test_discussion_prompt(): """Test if the discussion prompt is now properly formatted"""print("🧪 Testing Discussion Prompt Template Fix") print("=" * 45)
 api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    if not api_key: print("❌ No API key found")
        return False

    try:
        # Create discussion system discussion_system = MultiAgentDiscussionSystem(api_key, "test_session_123")

        # Create a test topic with the actual mission test_mission = "Create a fun educational video about healthy habits for kids"topic = DiscussionTopic( topic_id="test_prompt_fix", title="Test Mission Discussion", description=f"Test discussion for: {test_mission}",
            context={ 'mission': test_mission, 'platform': 'instagram', 'duration': 30, 'category': 'Education', 'style': 'fun', 'tone': 'engaging'}, required_decisions=["content_approach", "visual_style"]
        )

        # Test prompt creation
        agent_info = discussion_system.agent_personalities[AgentRole.SCRIPT_WRITER]
        prompt = discussion_system._create_agent_prompt( agent_info, topic, "No previous discussion", 1
        ) print("✅ Discussion system created") print(f"✅ Test mission: {test_mission}") print(f"✅ Agent: {agent_info['name']}")

        # Check if the prompt contains the actual mission instead of template placeholders
        if test_mission in prompt: print("✅ Mission found in prompt: ✓")
        else: print("❌ Mission NOT found in prompt")
 if agent_info['name'] in prompt: print("✅ Agent name found in prompt: ✓")
        else: print("❌ Agent name NOT found in prompt")
 if '{agent_info[' in prompt or '{topic.' in prompt: print("❌ Template placeholders still present: ✗") print("First 500 chars of prompt:") print(prompt[:500] + "...")
            return False
        else: print("✅ No template placeholders found: ✓")
 print("\n📝 Prompt Preview (first 200 chars):") print(prompt[:200] + "...")

        return True

    except Exception as e: print(f"❌ Test failed: {e}")
        return False

 if __name__ == "__main__":
    success = test_discussion_prompt()
    if success: print("\n🎉 Discussion prompt template fix SUCCESSFUL!") print("AI agents will now discuss the actual mission instead of generic topics.")
    else: print("\n❌ Discussion prompt template fix FAILED!")
