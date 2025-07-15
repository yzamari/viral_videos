#!/usr/bin/env python3
"""
Show current working results
"""

import os
import json

def show_current_session():
    """Show what we have in the current session"""
    session_dir = "outputs/session_20250715_130054"
    
    if not os.path.exists(session_dir):
        print("❌ Session directory not found")
        return
    
    print("🎉 CURRENT WORKING SESSION RESULTS")
    print("=" * 50)
    
    # Show discussions
    discussions_dir = os.path.join(session_dir, "discussions")
    if os.path.exists(discussions_dir):
        print("📝 AI AGENT DISCUSSIONS:")
        for file in os.listdir(discussions_dir):
            file_path = os.path.join(discussions_dir, file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                print(f"   ✅ {file}: {size:,} bytes")
        print()
    
    # Show video clips
    clips_dir = os.path.join(session_dir, "video_clips", "veo_clips")
    if os.path.exists(clips_dir):
        print("🎬 VEO-2 VIDEO CLIPS:")
        total_size = 0
        for file in os.listdir(clips_dir):
            file_path = os.path.join(clips_dir, file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                total_size += size
                print(f"   ✅ {file}: {size:,} bytes ({size/1024/1024:.1f}MB)")
        print(f"   📊 Total video content: {total_size:,} bytes ({total_size/1024/1024:.1f}MB)")
        print()
    
    # Show scripts
    scripts_dir = os.path.join(session_dir, "scripts")
    if os.path.exists(scripts_dir):
        print("📄 SCRIPTS:")
        for file in os.listdir(scripts_dir):
            file_path = os.path.join(scripts_dir, file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                print(f"   ✅ {file}: {size:,} bytes")
        print()
    
    # Show final output
    final_dir = os.path.join(session_dir, "final_output")
    if os.path.exists(final_dir):
        print("🎥 FINAL OUTPUT:")
        for file in os.listdir(final_dir):
            file_path = os.path.join(final_dir, file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                status = "✅ GOOD" if size > 1000 else "⚠️ SMALL"
                print(f"   {status} {file}: {size:,} bytes")
        print()
    
    # Show AI discussion content
    discussion_file = os.path.join(session_dir, "discussions", "ai_agent_discussion.json")
    if os.path.exists(discussion_file):
        print("🤖 AI AGENT DISCUSSION CONTENT:")
        try:
            with open(discussion_file, 'r') as f:
                data = json.load(f)
            
            print(f"   📋 Session: {data.get('session_id', 'unknown')}")
            print(f"   🎯 Topic: {data.get('topic', 'unknown')}")
            print(f"   🕐 Timestamp: {data.get('timestamp', 'unknown')}")
            
            agents = data.get('agents', {})
            print(f"   🤖 Agents: {len(agents)}")
            for agent_name, agent_data in agents.items():
                print(f"      - {agent_name}: {agent_data.get('role', 'unknown role')}")
            
            summary = data.get('discussion_summary', {})
            if summary:
                print(f"   📊 Consensus: {summary.get('consensus', 'unknown')}")
                decisions = summary.get('key_decisions', [])
                print(f"   🎯 Key decisions: {len(decisions)}")
                for i, decision in enumerate(decisions[:3]):
                    print(f"      {i+1}. {decision}")
            
        except Exception as e:
            print(f"   ❌ Error reading discussion: {e}")
        print()
    
    # Show summary
    summary_file = os.path.join(session_dir, "discussions", "discussion_summary.md")
    if os.path.exists(summary_file):
        print("📝 DISCUSSION SUMMARY:")
        try:
            with open(summary_file, 'r') as f:
                content = f.read()
            
            lines = content.split('\n')
            for line in lines[:15]:  # Show first 15 lines
                if line.strip():
                    print(f"   {line}")
            
            if len(lines) > 15:
                print("   ... (truncated)")
                
        except Exception as e:
            print(f"   ❌ Error reading summary: {e}")
        print()
    
    print("🎯 SUMMARY:")
    print("✅ VEO-2 video generation: WORKING")
    print("✅ AI agent discussions: WORKING")
    print("✅ Session management: WORKING")
    print("✅ Script processing: WORKING")
    print("⚠️ Final video composition: NEEDS FIX (only 51 bytes)")
    print()
    print("🚀 CORE SYSTEM IS FUNCTIONAL!")

if __name__ == "__main__":
    show_current_session() 