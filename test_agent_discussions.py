#!/usr/bin/env python3
"""
Test Agent Discussions - Simulate agent discussions for UI testing
"""

import time
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(__file__))

from unified_realtime_ui import global_visualizer

def simulate_agent_discussions():
    """Simulate realistic agent discussions"""
    
    # Start monitoring
    global_visualizer.start_monitoring()
    
    # Phase 1: Script Development
    print("🎭 Starting Phase 1: Script Development")
    global_visualizer.add_agent_message("System", "🎭 Starting discussion: Script Development and Dialogue Optimization", phase="Script Development")
    
    time.sleep(1)
    global_visualizer.add_agent_message("StoryWeaver", "Analyzing mission requirements and target audience demographics for optimal engagement", phase="Script Development", round_num=1, consensus=0.2)
    
    time.sleep(1)
    global_visualizer.add_agent_message("DialogueMaster", "Crafting compelling dialogue that leverages the narrative for maximum comedic impact", phase="Script Development", round_num=1, consensus=0.4)
    
    time.sleep(1)
    global_visualizer.add_agent_message("PaceMaster", "Optimizing script pacing for 35-second TikTok format with strong hooks", phase="Script Development", round_num=1, consensus=0.6)
    
    time.sleep(1)
    global_visualizer.add_agent_message("AudienceAdvocate", "Ensuring content resonates with target audience while maintaining ethical boundaries", phase="Script Development", round_num=1, consensus=0.8)
    
    time.sleep(1)
    global_visualizer.add_agent_message("System", "✅ Consensus reached!", phase="Script Development", consensus=1.0)
    
    # Phase 2: Audio Production
    print("🎭 Starting Phase 2: Audio Production")
    global_visualizer.add_agent_message("System", "🎭 Starting discussion: Audio Production and Voice Optimization", phase="Audio Production")
    
    time.sleep(1)
    global_visualizer.add_agent_message("AudioMaster", "Configuring audio levels and clarity for optimal TikTok playback", phase="Audio Production", round_num=1, consensus=0.3)
    
    time.sleep(1)
    global_visualizer.add_agent_message("VoiceMaster", "Selecting voice characteristics that match the comedic tone", phase="Audio Production", round_num=1, consensus=0.7)
    
    time.sleep(1)
    global_visualizer.add_agent_message("SoundMaster", "Adding subtle background elements to enhance engagement", phase="Audio Production", round_num=1, consensus=0.9)
    
    time.sleep(1)
    global_visualizer.add_agent_message("System", "✅ Consensus reached!", phase="Audio Production", consensus=1.0)
    
    # Phase 3: Visual Design
    print("🎭 Starting Phase 3: Visual Design")
    global_visualizer.add_agent_message("System", "🎭 Starting discussion: Visual Design and Typography Strategy", phase="Visual Design")
    
    time.sleep(1)
    global_visualizer.add_agent_message("VisualDirector", "Creating visual composition that supports the comedic narrative", phase="Visual Design", round_num=1, consensus=0.4)
    
    time.sleep(1)
    global_visualizer.add_agent_message("ColorMaster", "Implementing color palette that enhances mood and readability", phase="Visual Design", round_num=1, consensus=0.6)
    
    time.sleep(1)
    global_visualizer.add_agent_message("LayoutMaster", "Optimizing layout for mobile viewing and engagement", phase="Visual Design", round_num=1, consensus=0.8)
    
    time.sleep(1)
    global_visualizer.add_agent_message("System", "✅ Consensus reached!", phase="Visual Design", consensus=1.0)
    
    # Phase 4: Platform Optimization
    print("🎭 Starting Phase 4: Platform Optimization")
    global_visualizer.add_agent_message("System", "🎭 Starting discussion: Platform Optimization and Viral Mechanics", phase="Platform Optimization")
    
    time.sleep(1)
    global_visualizer.add_agent_message("PlatformExpert", "Optimizing for TikTok algorithm preferences and engagement patterns", phase="Platform Optimization", round_num=1, consensus=0.5)
    
    time.sleep(1)
    global_visualizer.add_agent_message("EngagementMaster", "Implementing hooks and engagement triggers for maximum viral potential", phase="Platform Optimization", round_num=1, consensus=0.7)
    
    time.sleep(1)
    global_visualizer.add_agent_message("TrendMaster", "Analyzing current trends and incorporating viral elements", phase="Platform Optimization", round_num=1, consensus=0.9)
    
    time.sleep(1)
    global_visualizer.add_agent_message("System", "✅ Consensus reached!", phase="Platform Optimization", consensus=1.0)
    
    # Phase 5: Quality Assurance
    print("🎭 Starting Phase 5: Quality Assurance")
    global_visualizer.add_agent_message("System", "🎭 Starting discussion: Quality Assurance and Final Review", phase="Quality Assurance")
    
    time.sleep(1)
    global_visualizer.add_agent_message("QualityGuard", "Performing comprehensive quality checks on all components", phase="Quality Assurance", round_num=1, consensus=0.4)
    
    time.sleep(1)
    global_visualizer.add_agent_message("CutMaster", "Finalizing cuts and transitions for optimal flow", phase="Quality Assurance", round_num=1, consensus=0.7)
    
    time.sleep(1)
    global_visualizer.add_agent_message("SyncMaster", "Ensuring perfect audio-visual synchronization", phase="Quality Assurance", round_num=1, consensus=0.9)
    
    time.sleep(1)
    global_visualizer.add_agent_message("System", "🎯 Discussion completed: 100% consensus in 1 rounds (45.2s)", phase="Quality Assurance", consensus=1.0)
    
    # Final completion
    time.sleep(1)
    global_visualizer.add_agent_message("System", "🎉 All agent discussions completed successfully!", phase="Completion")
    
    print("\n✅ Agent discussion simulation completed!")
    print("🌐 Check the UI at http://localhost:7860 to see the discussions")
    print("📊 Final HTML:")
    print(global_visualizer.generate_discussion_html())

if __name__ == "__main__":
    simulate_agent_discussions() 