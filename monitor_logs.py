#!/usr/bin/env python3
"""
Real-time log monitoring script
Monitors video generation progress and reports status every second
"""

import os
import time
import subprocess
import json
from datetime import datetime

def get_active_sessions():
    """Get list of active generation sessions"""
    sessions = []
    outputs_dir = "outputs"
    
    if not os.path.exists(outputs_dir):
        return sessions
    
    for session_dir in os.listdir(outputs_dir):
        session_path = os.path.join(outputs_dir, session_dir)
        if os.path.isdir(session_path):
            # Check if session has recent activity (modified in last 5 minutes)
            try:
                modified_time = os.path.getmtime(session_path)
                if time.time() - modified_time < 300:  # 5 minutes
                    sessions.append({
                        "name": session_dir,
                        "path": session_path,
                        "modified": datetime.fromtimestamp(modified_time).strftime("%H:%M:%S")
                    })
            except:
                pass
    
    return sessions

def get_session_status(session_path):
    """Get detailed status of a session"""
    status = {
        "stage": "unknown",
        "progress": 0,
        "clips_generated": 0,
        "final_videos": 0,
        "errors": []
    }
    
    # Check generation log
    log_file = os.path.join(session_path, "logs", "generation_log.json")
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                logs = json.load(f)
                if "current_stage" in logs:
                    status["stage"] = logs["current_stage"]
                if "progress_percentage" in logs:
                    status["progress"] = logs["progress_percentage"]
        except:
            pass
    
    # Check for VEO clips
    veo_clips_dir = os.path.join(session_path, "video_clips", "veo_clips")
    if os.path.exists(veo_clips_dir):
        status["clips_generated"] = len([f for f in os.listdir(veo_clips_dir) if f.endswith('.mp4')])
    
    # Check for final videos
    final_output_dir = os.path.join(session_path, "final_output")
    if os.path.exists(final_output_dir):
        status["final_videos"] = len([f for f in os.listdir(final_output_dir) if f.endswith('.mp4')])
    
    return status

def check_running_processes():
    """Check for active generation processes"""
    try:
        result = subprocess.run("ps aux | grep 'python3 main.py' | grep -v grep", 
                               shell=True, capture_output=True, text=True)
        processes = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                parts = line.split()
                if len(parts) > 10:
                    processes.append({
                        "pid": parts[1],
                        "cpu": parts[2],
                        "mem": parts[3],
                        "time": parts[9],
                        "command": " ".join(parts[10:])
                    })
        return processes
    except:
        return []

def monitor_loop():
    """Main monitoring loop"""
    print("🖥️ Starting real-time log monitoring...")
    print("📊 Monitoring every second. Press Ctrl+C to stop.")
    print("=" * 100)
    
    try:
        while True:
            # Clear screen (optional)
            # os.system('clear')
            
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"\n⏰ {current_time} - System Status Check")
            print("-" * 50)
            
            # Check running processes
            processes = check_running_processes()
            if processes:
                print(f"🚀 Active Processes: {len(processes)}")
                for proc in processes:
                    cmd_short = proc["command"][:60] + "..." if len(proc["command"]) > 60 else proc["command"]
                    print(f"   PID {proc['pid']}: CPU {proc['cpu']}% | {cmd_short}")
            else:
                print("💤 No active generation processes")
            
            # Check active sessions
            sessions = get_active_sessions()
            if sessions:
                print(f"\n📁 Active Sessions: {len(sessions)}")
                for session in sessions:
                    status = get_session_status(session["path"])
                    print(f"   📂 {session['name']} (modified: {session['modified']})")
                    print(f"      Stage: {status['stage']} | Clips: {status['clips_generated']} | Videos: {status['final_videos']}")
            else:
                print("\n📁 No recently active sessions")
            
            # Check system resources
            try:
                result = subprocess.run("df -h .", shell=True, capture_output=True, text=True)
                disk_line = result.stdout.split('\n')[1]
                disk_usage = disk_line.split()[4]
                print(f"\n💾 Disk Usage: {disk_usage}")
            except:
                pass
            
            print("-" * 50)
            
            # Wait 1 second
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoring stopped by user")

if __name__ == "__main__":
    monitor_loop()