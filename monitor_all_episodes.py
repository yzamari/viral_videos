#!/usr/bin/env python3
"""
Monitor all Israeli PM episodes generation
"""
import time
import subprocess
import os
from datetime import datetime

episodes = [9, 7, 8, 10, 11]

def monitor_all_episodes():
    """Monitor all episode generations"""
    print("🔍 Monitoring Israeli PM Episodes: 7, 8, 9, 10, 11")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    while True:
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Check if any process is still running
        try:
            ps_result = subprocess.run(
                ["ps", "aux"], 
                capture_output=True, 
                text=True
            )
            
            running_episodes = []
            for line in ps_result.stdout.split('\n'):
                for ep in episodes:
                    if f"israeli_pm_ghibli_ep{ep}_he" in line and "python" in line:
                        running_episodes.append(ep)
                        break
            
            print(f"\n[{timestamp}] Status Overview:")
            print(f"  Running episodes: {running_episodes if running_episodes else 'None'}")
            
            # Check each episode
            for ep in episodes:
                session_dir = f"outputs/israeli_pm_ghibli_ep{ep}_he"
                log_file = f"israeli_pm_ep{ep}_run.log"
                
                status = "🟢 RUNNING" if ep in running_episodes else "⏸️  STOPPED"
                
                # Check session directory
                files_count = 0
                final_video = None
                if os.path.exists(session_dir):
                    for root, dirs, files in os.walk(session_dir):
                        files_count += len(files)
                    
                    # Check for final video
                    final_output = os.path.join(session_dir, "final_output")
                    if os.path.exists(final_output):
                        for f in os.listdir(final_output):
                            if f.endswith("_final.mp4"):
                                final_video = f
                                break
                
                # Check log file
                last_log = "No log yet"
                if os.path.exists(log_file):
                    try:
                        tail_result = subprocess.run(
                            ["tail", "-1", log_file],
                            capture_output=True,
                            text=True
                        )
                        if tail_result.stdout:
                            last_log = tail_result.stdout.strip()[:80] + "..."
                    except:
                        pass
                
                print(f"\n  Episode {ep}: {status}")
                print(f"    Files: {files_count}")
                print(f"    Final: {'✅ ' + final_video if final_video else '❌ Not generated'}")
                print(f"    Log: {last_log}")
            
            # Check if all are done
            if not running_episodes:
                print(f"\n[{timestamp}] 🏁 All episodes completed!")
                
                # Summary
                print("\n📊 Final Summary:")
                completed = 0
                for ep in episodes:
                    final_output = os.path.join(f"outputs/israeli_pm_ghibli_ep{ep}_he", "final_output")
                    if os.path.exists(final_output):
                        videos = [f for f in os.listdir(final_output) if f.endswith("_final.mp4")]
                        if videos:
                            completed += 1
                            print(f"  Episode {ep}: ✅ {videos[0]}")
                        else:
                            print(f"  Episode {ep}: ❌ No final video")
                    else:
                        print(f"  Episode {ep}: ❌ No output directory")
                
                print(f"\n✅ Completed: {completed}/{len(episodes)}")
                break
            
            # Wait 10 seconds
            time.sleep(10)
            
        except KeyboardInterrupt:
            print(f"\n[{timestamp}] 🛑 Monitoring stopped by user")
            break
        except Exception as e:
            print(f"[{timestamp}] Monitor error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    monitor_all_episodes()