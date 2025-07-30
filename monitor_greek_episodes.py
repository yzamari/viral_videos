#!/usr/bin/env python3
"""
Greek Mythology Episodes Monitor
Monitors the progress of Episodes 6, 7, and 8 generation
"""

import time
import os
import sys
from datetime import datetime

def get_latest_log_line(log_file):
    """Get the latest line from a log file"""
    if not os.path.exists(log_file):
        return "Log file not found"
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            if lines:
                return lines[-1].strip()
            else:
                return "Log file is empty"
    except Exception as e:
        return f"Error reading log: {e}"

def check_completion_status(episode_name):
    """Check if episode is completed by looking for final output"""
    final_output_dir = f"/Users/yahavzamari/viralAi/outputs/{episode_name}/final_output"
    if os.path.exists(final_output_dir):
        files = os.listdir(final_output_dir)
        final_files = [f for f in files if f.endswith('__final.mp4')]
        return len(final_files) > 0, len(files)
    return False, 0

def main():
    episodes = {
        "greek_medusa_ep6": "medusa_ep6.log",
        "greek_prometheus_ep7": "prometheus_ep7.log", 
        "greek_aphrodite_ep8": "aphrodite_ep8.log"
    }
    
    print("🏛️ Greek Mythology Episodes Monitor")
    print("=" * 50)
    print("Monitoring Episodes 6, 7, and 8 generation...")
    print("Press Ctrl+C to stop monitoring")
    print()
    
    try:
        while True:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"⏰ {timestamp}")
            print("-" * 30)
            
            all_completed = True
            
            for episode_name, log_file in episodes.items():
                is_completed, file_count = check_completion_status(episode_name)
                latest_line = get_latest_log_line(log_file)
                
                episode_num = episode_name.split('_')[-1]
                
                if is_completed:
                    print(f"✅ {episode_num.upper()}: COMPLETED ({file_count} files)")
                else:
                    all_completed = False
                    print(f"🔄 {episode_num.upper()}: IN PROGRESS")
                
                # Show latest log activity (truncated for readability)
                if len(latest_line) > 80:
                    display_line = latest_line[:77] + "..."
                else:
                    display_line = latest_line
                    
                print(f"   📝 {display_line}")
                print()
            
            if all_completed:
                print("🎬 ALL EPISODES COMPLETED! 🎉")
                print("✨ Greek Mythology Series is now complete!")
                break
                
            print("=" * 50)
            time.sleep(5)  # Check every 5 seconds
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Monitoring stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main()