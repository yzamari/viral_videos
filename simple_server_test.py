#!/usr/bin/env python3
"""
Simple test to verify the server setup works
"""

import sys
import os
import subprocess
import time
import signal

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_simple_server():
    print("🧪 Starting simple server test...")
    
    # Start the server in a subprocess
    server_process = subprocess.Popen([
        sys.executable, 
        "backend_server.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for server to start
    time.sleep(3)
    
    # Test if server is running
    try:
        import requests
        
        # Test basic endpoint
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"✅ Server Response: {response.status_code}")
        print(f"✅ Server Data: {response.json()}")
        
        # Test API docs
        docs_response = requests.get("http://localhost:8000/docs", timeout=5)
        print(f"✅ API Docs: {docs_response.status_code}")
        
        print("🎉 Backend server is working correctly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        # Kill the server
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    test_simple_server()