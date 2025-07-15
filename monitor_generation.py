#!/usr/bin/env python3
"""
Video Generation Monitor
Runs video generation and monitors for errors/warnings
"""

import subprocess
import time
import os
import re
from datetime import datetime
from typing import List, Dict, Any
import threading
import signal
import sys

class GenerationMonitor:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.logs = []
        self.process = None
        self.monitoring = True
        self.start_time = datetime.now()
        
    def extract_errors_warnings(self, text: str):
        """Extract errors and warnings from log text"""
        lines = text.split('\n')
        
        for line in lines:
            if line.strip():
                # Track all logs
                self.logs.append({
                    'timestamp': datetime.now().isoformat(),
                    'line': line.strip()
                })
                
                # Extract errors
                if any(keyword in line.lower() for keyword in ['error', 'failed', 'exception', 'traceback']):
                    self.errors.append({
                        'timestamp': datetime.now().isoformat(),
                        'message': line.strip(),
                        'type': 'ERROR'
                    })
                
                # Extract warnings
                elif any(keyword in line.lower() for keyword in ['warning', 'warn', '⚠️']):
                    self.warnings.append({
                        'timestamp': datetime.now().isoformat(),
                        'message': line.strip(),
                        'type': 'WARNING'
                    })
    
    def monitor_outputs(self):
        """Monitor output directories for new files"""
        try:
            if os.path.exists('outputs'):
                sessions = [d for d in os.listdir('outputs') if d.startswith('session_')]
                if sessions:
                    latest_session = max(sessions)
                    session_path = f'outputs/{latest_session}'
                    
                    # Check for video files
                    video_files = []
                    for root, dirs, files in os.walk(session_path):
                        for file in files:
                            if file.endswith('.mp4'):
                                filepath = os.path.join(root, file)
                                size = os.path.getsize(filepath)
                                video_files.append({'file': filepath, 'size': size})
                    
                    # Check for audio files
                    audio_files = []
                    for root, dirs, files in os.walk(session_path):
                        for file in files:
                            if file.endswith('.mp3'):
                                filepath = os.path.join(root, file)
                                size = os.path.getsize(filepath)
                                audio_files.append({'file': filepath, 'size': size})
                    
                    return {
                        'session': latest_session,
                        'session_path': session_path,
                        'video_files': video_files,
                        'audio_files': audio_files
                    }
        except Exception as e:
            self.errors.append({
                'timestamp': datetime.now().isoformat(),
                'message': f'Monitor error: {str(e)}',
                'type': 'MONITOR_ERROR'
            })
        
        return None
    
    def print_status(self, file_status=None):
        """Print current status"""
        elapsed = datetime.now() - self.start_time
        print(f"\n{'='*60}")
        print(f"🕐 MONITORING STATUS - {datetime.now().strftime('%H:%M:%S')}")
        print(f"⏱️  Elapsed Time: {elapsed}")
        print(f"❌ Errors: {len(self.errors)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"📝 Total Logs: {len(self.logs)}")
        
        if file_status:
            print(f"📁 Current Session: {file_status['session']}")
            print(f"🎬 Video Files: {len(file_status['video_files'])}")
            print(f"🎵 Audio Files: {len(file_status['audio_files'])}")
            
            if file_status['video_files']:
                for vf in file_status['video_files']:
                    print(f"  📹 {vf['file']}: {vf['size']:,} bytes")
            
            if file_status['audio_files']:
                for af in file_status['audio_files']:
                    print(f"  🎵 {af['file']}: {af['size']:,} bytes")
        
        # Show recent errors/warnings
        if self.errors:
            print(f"\n❌ RECENT ERRORS:")
            for error in self.errors[-3:]:  # Show last 3 errors
                print(f"  {error['timestamp']}: {error['message'][:100]}...")
        
        if self.warnings:
            print(f"\n⚠️  RECENT WARNINGS:")
            for warning in self.warnings[-3:]:  # Show last 3 warnings
                print(f"  {warning['timestamp']}: {warning['message'][:100]}...")
        
        print(f"{'='*60}")
    
    def run_generation(self, command: List[str]):
        """Run the video generation command"""
        print(f"🚀 Starting video generation: {' '.join(command)}")
        print(f"📅 Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Monitor in real-time
            monitor_thread = threading.Thread(target=self.monitor_loop)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # Read output line by line
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    self.extract_errors_warnings(line)
                    print(line.rstrip())  # Print to console
            
            self.process.wait()
            return_code = self.process.returncode
            
            self.monitoring = False
            
            print(f"\n🎯 GENERATION COMPLETED")
            print(f"Return Code: {return_code}")
            
            return return_code
            
        except Exception as e:
            self.errors.append({
                'timestamp': datetime.now().isoformat(),
                'message': f'Process error: {str(e)}',
                'type': 'PROCESS_ERROR'
            })
            print(f"❌ Process error: {e}")
            return 1
    
    def monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            try:
                file_status = self.monitor_outputs()
                self.print_status(file_status)
                time.sleep(60)  # Check every minute
            except Exception as e:
                self.errors.append({
                    'timestamp': datetime.now().isoformat(),
                    'message': f'Monitor loop error: {str(e)}',
                    'type': 'MONITOR_LOOP_ERROR'
                })
                time.sleep(60)
    
    def generate_summary(self):
        """Generate final summary of errors and warnings"""
        end_time = datetime.now()
        total_time = end_time - self.start_time
        
        print(f"\n{'='*80}")
        print(f"📊 FINAL GENERATION SUMMARY")
        print(f"{'='*80}")
        print(f"⏱️  Total Time: {total_time}")
        print(f"📅 Start: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📅 End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"❌ Total Errors: {len(self.errors)}")
        print(f"⚠️  Total Warnings: {len(self.warnings)}")
        print(f"📝 Total Log Lines: {len(self.logs)}")
        
        # Check final output
        file_status = self.monitor_outputs()
        if file_status:
            print(f"\n📁 FINAL OUTPUT:")
            print(f"📂 Session: {file_status['session']}")
            print(f"🎬 Video Files: {len(file_status['video_files'])}")
            print(f"🎵 Audio Files: {len(file_status['audio_files'])}")
            
            total_video_size = sum(vf['size'] for vf in file_status['video_files'])
            total_audio_size = sum(af['size'] for af in file_status['audio_files'])
            
            print(f"📊 Total Video Size: {total_video_size:,} bytes ({total_video_size/1024/1024:.1f} MB)")
            print(f"📊 Total Audio Size: {total_audio_size:,} bytes ({total_audio_size/1024:.1f} KB)")
        
        # Detailed error summary
        if self.errors:
            print(f"\n❌ DETAILED ERROR SUMMARY:")
            print(f"{'='*50}")
            for i, error in enumerate(self.errors, 1):
                print(f"{i}. [{error['timestamp']}] {error['type']}")
                print(f"   {error['message']}")
                print()
        
        # Detailed warning summary
        if self.warnings:
            print(f"\n⚠️  DETAILED WARNING SUMMARY:")
            print(f"{'='*50}")
            for i, warning in enumerate(self.warnings, 1):
                print(f"{i}. [{warning['timestamp']}] {warning['type']}")
                print(f"   {warning['message']}")
                print()
        
        # Success indicators
        success_indicators = []
        if file_status:
            if file_status['video_files']:
                success_indicators.append("✅ Video files generated")
            if file_status['audio_files']:
                success_indicators.append("✅ Audio files generated")
        
        if len(self.errors) == 0:
            success_indicators.append("✅ No errors encountered")
        
        if len(self.warnings) < 5:
            success_indicators.append("✅ Minimal warnings")
        
        print(f"\n🎯 SUCCESS INDICATORS:")
        for indicator in success_indicators:
            print(f"  {indicator}")
        
        if not success_indicators:
            print("  ❌ No clear success indicators")
        
        print(f"{'='*80}")
        
        return {
            'total_time': str(total_time),
            'errors': len(self.errors),
            'warnings': len(self.warnings),
            'logs': len(self.logs),
            'file_status': file_status,
            'success_indicators': success_indicators
        }

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Monitoring interrupted by user")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    
    # Command to run
    command = [
        "python", "main.py", "generate",
        "--mission", "explain to kids why women should stay in the kitchen",
        "--category", "Comedy",
        "--platform", "tiktok", 
        "--duration", "13",
        "--discussions", "enhanced",
        "--target-audience", "kids",
        "--style", "engaging",
        "--tone", "funny",
        "--visual-style", "vibrant"
    ]
    
    monitor = GenerationMonitor()
    
    try:
        return_code = monitor.run_generation(command)
        summary = monitor.generate_summary()
        
        if return_code == 0:
            print("🎉 Generation completed successfully!")
        else:
            print(f"❌ Generation failed with return code: {return_code}")
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"❌ Monitor failed: {e}")
        import traceback
        traceback.print_exc() 