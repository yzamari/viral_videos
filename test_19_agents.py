#!/usr/bin/env python3
"""
Test script for the Enhanced 19 AI Agents System
Verifies all agents are properly configured and functional
"""

import os
import sys
from src.agents.enhanced_multi_agent_discussion import EnhancedMultiAgentDiscussionSystem, AgentRole
from src.models.video_models import VideoCategory, Platform

def test_19_agents():
    """Test all 19 AI agents"""
    print("🚀 Testing Enhanced 19 AI Agents System")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY environment variable not set")
        return False
    
    try:
        # Initialize the enhanced system
        print("🤖 Initializing Enhanced Multi-Agent Discussion System...")
        system = EnhancedMultiAgentDiscussionSystem(api_key, "test_session")
        
        # Verify all 19 agents are loaded
        expected_agents = 19
        actual_agents = len(system.agent_personalities)
        
        print(f"📊 Expected agents: {expected_agents}")
        print(f"📊 Actual agents: {actual_agents}")
        
        if actual_agents != expected_agents:
            print(f"❌ Error: Expected {expected_agents} agents, found {actual_agents}")
            return False
        
        print("✅ All 19 agents successfully loaded!")
        print()
        
        # List all agents by category
        print("🤖 AGENT ROSTER:")
        print("-" * 30)
        
        # Original agents
        original_agents = [
            AgentRole.TREND_ANALYST, AgentRole.SCRIPT_WRITER, AgentRole.DIRECTOR,
            AgentRole.VIDEO_GENERATOR, AgentRole.SOUNDMAN, AgentRole.EDITOR, AgentRole.ORCHESTRATOR
        ]
        print("📚 Original Foundation Agents (7):")
        for agent in original_agents:
            name = system.agent_personalities[agent]['name']
            expertise = system.agent_personalities[agent]['expertise'][0]
            print(f"  • {name} - {expertise}")
        print()
        
        # Script & Dialogue specialists
        script_agents = [AgentRole.DIALOGUE_MASTER, AgentRole.PACE_MASTER]
        print("🎭 Script & Dialogue Specialists (2):")
        for agent in script_agents:
            name = system.agent_personalities[agent]['name']
            expertise = system.agent_personalities[agent]['expertise'][0]
            print(f"  • {name} - {expertise}")
        print()
        
        # Audio specialists
        audio_agents = [AgentRole.VOICE_DIRECTOR, AgentRole.SOUND_DESIGNER]
        print("🎵 Advanced Audio Specialists (2):")
        for agent in audio_agents:
            name = system.agent_personalities[agent]['name']
            expertise = system.agent_personalities[agent]['expertise'][0]
            print(f"  • {name} - {expertise}")
        print()
        
        # Typography specialists
        type_agents = [AgentRole.TYPE_MASTER, AgentRole.HEADER_CRAFT]
        print("📝 Typography & Visual Text Specialists (2):")
        for agent in type_agents:
            name = system.agent_personalities[agent]['name']
            expertise = system.agent_personalities[agent]['expertise'][0]
            print(f"  • {name} - {expertise}")
        print()
        
        # Visual style specialists
        visual_agents = [AgentRole.STYLE_DIRECTOR, AgentRole.COLOR_MASTER]
        print("🎨 Visual Style & Art Direction (2):")
        for agent in visual_agents:
            name = system.agent_personalities[agent]['name']
            expertise = system.agent_personalities[agent]['expertise'][0]
            print(f"  • {name} - {expertise}")
        print()
        
        # Platform specialists
        platform_agents = [AgentRole.PLATFORM_GURU, AgentRole.ENGAGEMENT_HACKER]
        print("📱 Platform & Optimization Specialists (2):")
        for agent in platform_agents:
            name = system.agent_personalities[agent]['name']
            expertise = system.agent_personalities[agent]['expertise'][0]
            print(f"  • {name} - {expertise}")
        print()
        
        # Quality specialists
        quality_agents = [AgentRole.QUALITY_GUARD, AgentRole.AUDIENCE_ADVOCATE]
        print("🔍 Quality Assurance & Testing (2):")
        for agent in quality_agents:
            name = system.agent_personalities[agent]['name']
            expertise = system.agent_personalities[agent]['expertise'][0]
            print(f"  • {name} - {expertise}")
        print()
        
        print("✅ All agent categories verified!")
        print()
        
        # Test agent role enum
        print("🔧 Testing AgentRole enum...")
        all_roles = list(AgentRole)
        print(f"📊 Total roles defined: {len(all_roles)}")
        
        if len(all_roles) != 19:
            print(f"❌ Error: Expected 19 roles, found {len(all_roles)}")
            return False
        
        print("✅ AgentRole enum verified!")
        print()
        
        # Test a quick discussion (without API calls)
        print("🎭 Testing discussion topic creation...")
        from src.agents.enhanced_multi_agent_discussion import EnhancedVideoGenerationTopics
        
        context = {
            'topic': 'Test AI Video Generation',
            'category': 'EDUCATIONAL',
            'platform': 'YOUTUBE_SHORTS',
            'duration': 30
        }
        
        # Test all discussion topics
        topics = [
            EnhancedVideoGenerationTopics.script_development(context),
            EnhancedVideoGenerationTopics.audio_production(context),
            EnhancedVideoGenerationTopics.visual_design(context),
            EnhancedVideoGenerationTopics.platform_optimization(context),
            EnhancedVideoGenerationTopics.quality_assurance(context)
        ]
        
        print(f"📊 Discussion topics created: {len(topics)}")
        for i, topic in enumerate(topics, 1):
            print(f"  {i}. {topic.title}")
        
        print("✅ Discussion topics verified!")
        print()
        
        print("🎉 ALL TESTS PASSED!")
        print("🚀 Enhanced 19 AI Agents System is ready for professional video generation!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_19_agents()
    sys.exit(0 if success else 1)
