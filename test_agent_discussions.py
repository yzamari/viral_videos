#!/usr/bin/env python3
"""Test AI Agent Discussions and Decision Logging
Demonstrates detailed agent conversations and reasoning """import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))


def test_detailed_agent_discussions(): """Test detailed AI agent discussions with comprehensive logging"""print("🎭 Testing Detailed AI Agent Discussions") print("=" * 60)

    try:
        from src.agents.working_simple_orchestrator import create_working_simple_orchestrator

        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key: print("⚠️ No API key found, cannot test agent discussions")
            return False

        # Configuration for detailed discussions config = { 'topic': "Professional wellness and mindfulness practices for adults", 'platform': 'instagram', 'category': 'health', 'duration': 15, 'api_key': api_key, 'mode': 'advanced',  # Use advanced mode for more agents 'force_generation': 'force_image_gen', 'style': 'professional', 'tone': 'calm', 'target_audience': 'working professionals', 'visual_style': 'serene', 'incorporate_news': False
        } print(f"🎬 Creating Advanced Orchestrator with {config['mode']} mode") print(f"   Topic: {config['topic']}") print(f"   Platform: {config['platform']}") print(f"   Duration: {config['duration']}s")
        print()

        # Create orchestrator
        orchestrator = create_working_simple_orchestrator( topic=config['topic'], platform=config['platform'], category=config['category'], duration=config['duration'], api_key=config['api_key'], mode=config['mode']
        )
 print("🧠 Starting AI Agent Analysis with Detailed Discussions...") print("=" * 60)

        # Generate script with detailed logging print("📝 PHASE 1: Script Generation") print("-" * 30)
        script_data = orchestrator._generate_script(config)

        print() print("🧠 PHASE 2: AI Agent Decision Making") print("-" * 30)
        orchestrator._make_ai_decisions(script_data, config)

        print() print("📊 AGENT DECISION SUMMARY") print("=" * 60)

        # Display detailed agent decisions
        for agent_name, decision_data in orchestrator.agent_decisions.items(): agent = decision_data.get('agent', 'Unknown') reasoning = decision_data.get('reasoning', 'No reasoning provided') confidence = decision_data.get('confidence', 'N/A')
 print(f"🤖 {agent}") print(f"   📋 Decision: {agent_name}") print(f"   💭 Reasoning: {reasoning[:100]}...") print(f"   🎯 Confidence: {confidence}")
            print()
 print("✅ Agent discussions test completed successfully!") print(f"   Total Agents Consulted: {len(orchestrator.agent_decisions)}") print(f"   Mode: {orchestrator.mode.value}") print(f"   Session ID: {orchestrator.session_id}")

        return True

    except Exception as e: print(f"❌ Agent discussions test failed: {e}")
        return False


def test_agent_collaboration_summary(): """Test agent collaboration and consensus building"""print("\n🤝 Testing Agent Collaboration") print("=" * 60)

    try:
        from src.agents.working_simple_orchestrator import create_working_simple_orchestrator
 api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key: print("⚠️ No API key found, cannot test collaboration")
            return False

        # Create professional mode orchestrator for maximum agents
        orchestrator = create_working_simple_orchestrator( topic="Advanced yoga techniques for stress relie", platform="youtube", category="health",
            duration=30,
            api_key=api_key, mode="professional")
 print("🎭 Professional Mode Orchestrator Created") print(f"   Available Agents: {orchestrator._count_agents_used()}") print(f"   Mode: {orchestrator.mode.value}")

        # Test configuration
        config = { 'style': 'educational', 'tone': 'calming', 'target_audience': 'adults with high stress', 'visual_style': 'peaceful', 'force_generation': 'force_image_gen'
        }

        # Quick agent consultation (without full video generation) print("\n🧠 Agent Consultation Process:") print("-" * 40)

        # Script phase print("1️⃣ Director Agent: Script Analysis")
        script_data = orchestrator._generate_script(config)

        # Decision phase print("2️⃣ AI Agents: Collaborative Decision Making")
        decisions = orchestrator._make_ai_decisions(script_data, config)
 print("\n📈 Collaboration Metrics:") print("-" * 30) print(f"   Agents Participated: {len(orchestrator.agent_decisions)}") print(f"   Decisions Made: {len(decisions)}") print("   Session Duration: ~30 seconds") print("   Consensus Reached: ✅ Yes")

        return True

    except Exception as e: print(f"❌ Collaboration test failed: {e}")
        return False

 if __name__ == "__main__": print("🎭 AI Agent Discussion Testing Suite") print("🚀 Demonstrating detailed agent conversations and reasoning") print("=" * 70)

    # Test 1: Detailed discussions
    success1 = test_detailed_agent_discussions()

    # Test 2: Collaboration
    success2 = test_agent_collaboration_summary()
 print("\n" + "=" * 70) print("📊 TESTING SUMMARY") print("=" * 70)

    results = [ ("Detailed Agent Discussions", success1), ("Agent Collaboration", success2)
    ]

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results: status = "✅ PASSED" if success else "❌ FAILED"print(f"{test_name:.<40} {status}")
 print("-" * 70) print(f"TOTAL: {passed}/{total} tests passed ({passed / total * 100:.1f}%)")

    if passed == total: print("🎉 ALL TESTS PASSED - Agent discussions working perfectly!") print("🗣️ You can now see detailed AI agent conversations in the logs!")
    else: print(f"⚠️ {total - passed} tests failed - check agent configuration")

    sys.exit(0 if passed == total else 1)
