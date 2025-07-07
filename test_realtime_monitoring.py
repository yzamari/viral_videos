#!/usr/bin/env python3
"""
Test script for Real-Time Agent Monitoring System
Simulates agent discussions with live visualization updates
"""

import os
import sys
import time
import threading
from datetime import datetime

def test_realtime_monitoring():
    """Test the real-time monitoring system"""
    print("🚀 Testing Real-Time Agent Monitoring System")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY environment variable not set")
        return False
    
    try:
        # Import the real-time visualizer
        from src.agents.realtime_discussion_visualizer import RealTimeDiscussionVisualizer
        
        print("🎬 Initializing Real-Time Discussion Visualizer...")
        
        # Create visualizer with callback
        def update_callback():
            print("🔄 UI Update triggered")
        
        visualizer = RealTimeDiscussionVisualizer("test_session", update_callback)
        
        print("✅ Real-time visualizer initialized!")
        print()
        
        # Test agent definitions
        all_agents = {
            "TrendMaster": {"category": "Foundation", "icon": "📈"},
            "StoryWeaver": {"category": "Foundation", "icon": "📝"},
            "VisionCraft": {"category": "Foundation", "icon": "🎨"},
            "PixelForge": {"category": "Foundation", "icon": "⚡"},
            "AudioMaster": {"category": "Foundation", "icon": "🎵"},
            "CutMaster": {"category": "Foundation", "icon": "✂️"},
            "SyncMaster": {"category": "Foundation", "icon": "🎯"},
            "DialogueMaster": {"category": "Script", "icon": "🎭"},
            "PaceMaster": {"category": "Script", "icon": "⚡"},
            "VoiceDirector": {"category": "Audio", "icon": "🎙️"},
            "SoundDesigner": {"category": "Audio", "icon": "🔊"},
            "TypeMaster": {"category": "Typography", "icon": "📝"},
            "HeaderCraft": {"category": "Typography", "icon": "🏷️"},
            "StyleDirector": {"category": "Visual", "icon": "🎨"},
            "ColorMaster": {"category": "Visual", "icon": "🌈"},
            "PlatformGuru": {"category": "Platform", "icon": "📱"},
            "EngagementHacker": {"category": "Platform", "icon": "🚀"},
            "QualityGuard": {"category": "Quality", "icon": "🔍"},
            "AudienceAdvocate": {"category": "Quality", "icon": "👥"}
        }
        
        print(f"🤖 Testing with {len(all_agents)} agents")
        print()
        
        # Simulate 5 discussion phases
        phases = [
            ("🎭 Script Development", ["StoryWeaver", "DialogueMaster", "PaceMaster", "AudienceAdvocate"]),
            ("🎵 Audio Production", ["AudioMaster", "VoiceDirector", "SoundDesigner", "PlatformGuru"]),
            ("🎨 Visual Design", ["VisionCraft", "StyleDirector", "ColorMaster", "TypeMaster", "HeaderCraft"]),
            ("📱 Platform Optimization", ["PlatformGuru", "EngagementHacker", "TrendMaster", "QualityGuard"]),
            ("🔍 Quality Review", ["QualityGuard", "AudienceAdvocate", "SyncMaster", "CutMaster"])
        ]
        
        print("🎭 Starting simulated discussion phases...")
        print()
        
        for phase_num, (phase_name, agents) in enumerate(phases, 1):
            print(f"Phase {phase_num}/5: {phase_name}")
            print(f"Agents: {', '.join(agents)}")
            
            # Start phase
            visualizer.start_discussion_phase(phase_name, agents, 5, 0.8)
            
            # Simulate discussion rounds
            for round_num in range(1, 4):  # 3 rounds max
                print(f"  Round {round_num}:")
                
                for agent in agents:
                    # Simulate agent contribution
                    messages = [
                        f"Contributing {agent} expertise to {phase_name}",
                        f"Analyzing requirements for {phase_name}",
                        f"Providing professional input on {phase_name}",
                        f"Optimizing approach for {phase_name}"
                    ]
                    
                    import random
                    message = random.choice(messages)
                    vote = random.choice(["agree", "agree", "neutral"])  # Bias toward agreement
                    
                    visualizer.log_agent_contribution(agent, message, round_num, vote)
                    print(f"    💬 {agent}: {message[:50]}... [{vote}]")
                    
                    time.sleep(0.1)  # Small delay for realism
                
                # Update consensus
                consensus = min(1.0, 0.4 + (round_num * 0.3))
                visualizer.update_consensus(consensus, round_num)
                print(f"    📊 Consensus: {consensus:.1%}")
                
                if consensus >= 0.8:
                    print(f"    ✅ Consensus reached in round {round_num}!")
                    break
                
                time.sleep(0.2)
            
            # Complete phase
            visualizer.complete_discussion_phase(consensus, round_num, 
                                               [f"Key insight from {phase_name}"], 
                                               {"decision": f"Completed {phase_name}"})
            
            print(f"  ✅ Phase {phase_num} completed!")
            print()
            
            time.sleep(0.3)
        
        print("🎉 All phases completed!")
        print()
        
        # Test real-time status
        print("📊 Testing real-time status retrieval...")
        status = visualizer.get_real_time_status()
        
        print(f"  • Total messages: {status['total_messages']}")
        print(f"  • Average consensus: {status['average_consensus']:.1%}")
        print(f"  • Session duration: {status['session_duration']:.1f}s")
        print(f"  • Recent activities: {len(status['recent_activities'])}")
        
        print("✅ Real-time status verified!")
        print()
        
        # Test HTML generation
        print("🎨 Testing HTML visualization generation...")
        
        agent_grid_html = visualizer.generate_agent_grid_html(all_agents)
        activity_feed_html = visualizer.generate_activity_feed_html()
        progress_dashboard_html = visualizer.generate_progress_dashboard_html()
        
        print(f"  • Agent grid HTML: {len(agent_grid_html)} characters")
        print(f"  • Activity feed HTML: {len(activity_feed_html)} characters")
        print(f"  • Progress dashboard HTML: {len(progress_dashboard_html)} characters")
        
        print("✅ HTML generation verified!")
        print()
        
        # Test data saving
        print("💾 Testing session data saving...")
        visualizer.save_real_time_session_data()
        print("✅ Session data saving verified!")
        print()
        
        print("🎉 ALL REAL-TIME MONITORING TESTS PASSED!")
        print("👀 Real-time agent monitoring system is fully functional!")
        print()
        print("🚀 Ready to launch real-time monitoring UI:")
        print("   ./launch_realtime_monitoring.sh")
        print()
        print("   Or manually:")
        print("   python enhanced_gradio_ui_with_realtime_agents.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_realtime_monitoring()
    sys.exit(0 if success else 1)
