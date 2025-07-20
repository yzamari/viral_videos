#!/usr/bin/env python3
"""
Monitor the complete system test progress
"""

import os
import time
import json
from datetime import datetime

def monitor_test_progress():
    """Monitor the complete system test progress"""
    
    print("🔍 MONITORING COMPLETE SYSTEM TEST")
    print("=" * 50)
    
    # Find the latest test session
    outputs_dir = "outputs"
    if not os.path.exists(outputs_dir):
        print("❌ No outputs directory found")
        return
    
    # Find the most recent session
    sessions = [d for d in os.listdir(outputs_dir) if d.startswith('complete_test_')]
    if not sessions:
        print("❌ No complete test sessions found")
        return
    
    latest_session = max(sessions)
    session_dir = os.path.join(outputs_dir, latest_session)
    
    print(f"📁 Monitoring session: {latest_session}")
    print(f"📂 Session directory: {session_dir}")
    print()
    
    # Monitor files being created
    monitored_files = []
    start_time = time.time()
    
    while time.time() - start_time < 300:  # Monitor for 5 minutes max
        try:
            if os.path.exists(session_dir):
                current_files = []
                for root, dirs, files in os.walk(session_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, session_dir)
                        size = os.path.getsize(file_path)
                        current_files.append((rel_path, size))
                
                # Check for new files
                for file_path, size in current_files:
                    if file_path not in [f[0] for f in monitored_files]:
                        print(f"📄 NEW FILE: {file_path} ({size:,} bytes)")
                        monitored_files.append((file_path, size))
                
                # Check for updated files
                for i, (file_path, old_size) in enumerate(monitored_files):
                    for new_path, new_size in current_files:
                        if new_path == file_path and new_size != old_size:
                            print(f"📝 UPDATED: {file_path} ({old_size:,} -> {new_size:,} bytes)")
                            monitored_files[i] = (file_path, new_size)
                
                # Check for completion markers
                session_data_path = os.path.join(session_dir, "session_data.json")
                if os.path.exists(session_data_path):
                    try:
                        with open(session_data_path, 'r') as f:
                            session_data = json.load(f)
                        
                        if session_data.get('success'):
                            print("🎉 GENERATION COMPLETED SUCCESSFULLY!")
                            print_final_summary(session_dir, session_data)
                            return
                    except:
                        pass
                
            time.sleep(2)  # Check every 2 seconds
            
        except KeyboardInterrupt:
            print("\n⚠️ Monitoring interrupted by user")
            break
        except Exception as e:
            print(f"⚠️ Monitoring error: {e}")
            time.sleep(5)
    
    print("⏰ Monitoring timeout reached")
    print_current_status(session_dir)

def print_final_summary(session_dir, session_data):
    """Print final summary of the generation"""
    print("\n🎯 FINAL SUMMARY")
    print("=" * 50)
    
    print(f"✅ Success: {session_data.get('success', False)}")
    print(f"📋 Topic: {session_data.get('topic', 'N/A')}")
    print(f"⏱️ Duration: {session_data.get('duration_seconds', 0)} seconds")
    print(f"🎬 Platform: {session_data.get('platform', 'N/A')}")
    print(f"⚡ Generation time: {session_data.get('generation_time', 0):.1f} seconds")
    print(f"📊 File size: {session_data.get('file_size_mb', 0):.2f} MB")
    print(f"🎞️ Clips generated: {session_data.get('clips_generated', 0)}")
    print()
    
    files_generated = session_data.get('files_generated', {})
    print("📁 FILES GENERATED:")
    for file_type, file_path in files_generated.items():
        if file_path and os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   ✅ {file_type}: {os.path.basename(file_path)} ({size:,} bytes)")
        else:
            print(f"   ❌ {file_type}: Missing")
    print()
    
    # Check for AI discussions
    discussion_path = os.path.join(session_dir, "ai_agent_discussion.json")
    if os.path.exists(discussion_path):
        try:
            with open(discussion_path, 'r') as f:
                discussion = json.load(f)
            
            print("🤖 AI AGENT DISCUSSIONS:")
            agents = discussion.get('agents', {})
            for agent_name, agent_data in agents.items():
                print(f"   🔹 {agent_data.get('agent_name', agent_name)}")
                print(f"      Role: {agent_data.get('role', 'N/A')}")
                print(f"      Performance: {agent_data.get('performance', 'N/A')}")
            
            summary = discussion.get('discussion_summary', {})
            print(f"   📊 Consensus: {summary.get('consensus', 'N/A')}")
            print(f"   🎯 Decisions made: {summary.get('performance_metrics', {}).get('decisions_made', 0)}")
            print()
        except:
            print("🤖 AI AGENT DISCUSSIONS: Error reading file")
    
    print("🎉 COMPLETE SYSTEM TEST SUCCESSFUL!")

def print_current_status(session_dir):
    """Print current status of the generation"""
    print("\n📊 CURRENT STATUS")
    print("=" * 50)
    
    if os.path.exists(session_dir):
        files = []
        for root, dirs, file_list in os.walk(session_dir):
            for file in file_list:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, session_dir)
                size = os.path.getsize(file_path)
                files.append((rel_path, size))
        
        print(f"📁 Session directory: {session_dir}")
        print(f"📄 Files found: {len(files)}")
        
        for file_path, size in sorted(files):
            print(f"   📄 {file_path}: {size:,} bytes")
    else:
        print("❌ Session directory not found")

if __name__ == '__main__':
    monitor_test_progress() 