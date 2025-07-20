#!/usr/bin/env python3
"""
Test monitoring script - checks unit test results every minute
"""
import time
import subprocess
import os
from datetime import datetime

def check_test_status():
    """Check the current test status"""
    try:
        # Check if pytest is still running
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        pytest_running = 'pytest' in result.stdout and 'test_results.log' in result.stdout
        
        if pytest_running:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏳ Tests still running...")
            
            # Show last few lines of test output
            if os.path.exists('test_results.log'):
                with open('test_results.log', 'r') as f:
                    lines = f.readlines()
                    if lines:
                        print("   Last output:")
                        for line in lines[-5:]:
                            print(f"   {line.strip()}")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Tests completed!")
            
            # Show final results
            if os.path.exists('test_results.log'):
                with open('test_results.log', 'r') as f:
                    content = f.read()
                    print("\n📊 Final Test Results:")
                    print("=" * 50)
                    
                    # Extract summary
                    lines = content.split('\n')
                    for line in lines:
                        if 'passed' in line or 'failed' in line or 'error' in line:
                            if any(word in line for word in ['===', 'short test summary', 'FAILED', 'ERROR']):
                                print(line)
                    
                    # Show any errors
                    if 'FAILED' in content or 'ERROR' in content:
                        print("\n❌ Issues found:")
                        for line in lines:
                            if 'FAILED' in line or 'ERROR' in line:
                                print(f"   {line}")
            
            return False  # Tests completed
        
        return True  # Tests still running
        
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error checking test status: {e}")
        return False

def main():
    """Main monitoring loop"""
    print("🔍 Starting test monitoring...")
    print("Will check every 60 seconds until tests complete\n")
    
    while True:
        still_running = check_test_status()
        
        if not still_running:
            print("\n🎉 Test monitoring completed!")
            break
            
        time.sleep(60)  # Wait 1 minute

if __name__ == '__main__':
    main() 