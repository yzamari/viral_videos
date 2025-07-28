#!/usr/bin/env python3
"""
Monitor Israeli PM episode generation
"""
import time
import subprocess
import os
from datetime import datetime

def monitor_generation():
    """Monitor the generation process"""
    print("🔍 Starting Israeli PM Episode 5 Monitor")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    session_dir = "outputs/israeli_pm_ghibli_ep5_he"
    
    while True:
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Check if process is still running
        try:
            ps_result = subprocess.run(
                ["ps", "aux"], 
                capture_output=True, 
                text=True
            )
            
            is_running = False
            for line in ps_result.stdout.split('\n'):
                if "israeli_pm_ghibli_ep5_he" in line and "python" in line:
                    is_running = True
                    break
            
            print(f"\n[{timestamp}] Status: {'🟢 RUNNING' if is_running else '🔴 STOPPED'}")
            
            # Check log file
            log_file = "israeli_pm_test_fixed.log" if os.path.exists("israeli_pm_test_fixed.log") else "israeli_pm_test.log"
            if os.path.exists(log_file):
                with open(log_file, "r") as f:
                    lines = f.readlines()
                    if lines:
                        last_line = lines[-1].strip()
                        print(f"[{timestamp}] Last log: {last_line}")
            
            # Check session directory for progress
            if os.path.exists(session_dir):
                try:
                    # Check logs directory
                    logs_dir = os.path.join(session_dir, "logs")
                    if os.path.exists(logs_dir):
                        log_files = [f for f in os.listdir(logs_dir) if f.endswith('.log')]
                        if log_files:
                            latest_log = max(log_files, key=lambda x: os.path.getctime(os.path.join(logs_dir, x)))
                            log_path = os.path.join(logs_dir, latest_log)
                            
                            # Get last few lines
                            try:
                                tail_result = subprocess.run(
                                    ["tail", "-3", log_path],
                                    capture_output=True,
                                    text=True
                                )
                                if tail_result.stdout:
                                    print(f"[{timestamp}] Session log:")
                                    for line in tail_result.stdout.strip().split('\n'):
                                        if line.strip():
                                            print(f"    {line.strip()}")
                            except Exception as e:
                                print(f"[{timestamp}] Could not read session log: {e}")
                    
                    # Check for generated files
                    file_count = 0
                    for root, dirs, files in os.walk(session_dir):
                        file_count += len(files)
                    
                    print(f"[{timestamp}] Session files: {file_count}")
                    
                except Exception as e:
                    print(f"[{timestamp}] Session check error: {e}")
            else:
                print(f"[{timestamp}] Session directory not found yet")
            
            # Check for completion
            if not is_running:
                print(f"\n[{timestamp}] 🏁 Generation process completed!")
                
                # Check final output
                final_output = os.path.join(session_dir, "final_output")
                if os.path.exists(final_output):
                    final_files = os.listdir(final_output)
                    if final_files:
                        print(f"[{timestamp}] ✅ Final output created: {final_files}")
                    else:
                        print(f"[{timestamp}] ❌ Final output directory is empty")
                else:
                    print(f"[{timestamp}] ❌ No final output directory found")
                
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
    monitor_generation()