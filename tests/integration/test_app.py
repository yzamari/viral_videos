#!/usr/bin/env python3
"""
Quick test script to verify the full application setup
"""

import sys
import subprocess
import time
import requests
import os

def test_backend():
    """Test if backend server starts correctly"""
    print("🧪 Testing backend server...")
    
    # Start backend server
    process = subprocess.Popen([sys.executable, "backend_server.py"], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
    
    # Wait for server to start
    time.sleep(5)
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running!")
            print(f"✅ Response: {response.json()}")
            
            # Test API docs
            docs_response = requests.get("http://localhost:8000/docs", timeout=5)
            if docs_response.status_code == 200:
                print("✅ API documentation is accessible!")
            else:
                print("⚠️ API docs not accessible")
                
            return True
        else:
            print(f"❌ Backend server returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server")
        return False
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False
    finally:
        # Clean up
        process.terminate()
        process.wait()

def test_frontend():
    """Test if frontend dependencies are installed"""
    print("🧪 Testing frontend setup...")
    
    if not os.path.exists("frontend/package.json"):
        print("❌ Frontend package.json not found")
        return False
        
    try:
        # Check if node_modules exists
        if os.path.exists("frontend/node_modules"):
            print("✅ Frontend dependencies are installed!")
            return True
        else:
            print("⚠️ Frontend dependencies not installed yet")
            print("💡 Run: cd frontend && npm install")
            return False
            
    except Exception as e:
        print(f"❌ Error testing frontend: {e}")
        return False

def main():
    """Main test function"""
    print("🎬 Testing Viral AI Application Setup")
    print("=" * 50)
    
    # Test Python backend
    backend_ok = test_backend()
    
    # Test frontend setup
    frontend_ok = test_frontend()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"🔧 Backend Server: {'✅ PASS' if backend_ok else '❌ FAIL'}")
    print(f"🎨 Frontend Setup: {'✅ PASS' if frontend_ok else '⚠️ NEEDS SETUP'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 Application setup is working correctly!")
        print("💡 You can now run: ./run_app.sh")
    else:
        print("\n⚠️ Some issues found. Please check the errors above.")
        
    return backend_ok and frontend_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)