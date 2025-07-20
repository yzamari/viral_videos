#!/usr/bin/env python3
"""
🚀 Viral AI Video Generator - Application Launcher
Simplified launcher that avoids dependency conflicts
"""

import os
import sys
import subprocess
import time
import signal
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check if basic dependencies are available"""
    try:
        import fastapi
        import uvicorn
        import websockets
        print("✅ Backend dependencies verified")
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("💡 Install with: pip install fastapi uvicorn websockets")
        return False

def start_backend():
    """Start the FastAPI backend server"""
    print("🔧 Starting backend server...")
    
    try:
        # Start backend server
        backend_process = subprocess.Popen([
            sys.executable, 
            "backend_server.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(3)
        
        # Test if server is running
        try:
            import requests
            response = requests.get("http://localhost:8000/", timeout=5)
            if response.status_code == 200:
                print("✅ Backend server started successfully!")
                print(f"🌐 API available at: http://localhost:8000")
                print(f"📖 API docs at: http://localhost:8000/docs")
                return backend_process
            else:
                print(f"❌ Backend server returned status {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Cannot connect to backend: {e}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the React frontend development server"""
    print("🎨 Starting frontend server...")
    
    frontend_path = Path("frontend")
    if not frontend_path.exists():
        print("❌ Frontend directory not found")
        return None
        
    try:
        # Check if node_modules exists
        if not (frontend_path / "node_modules").exists():
            print("📦 Installing frontend dependencies...")
            subprocess.run(["npm", "install"], cwd=frontend_path, check=True)
        
        # Start frontend dev server
        frontend_process = subprocess.Popen([
            "npm", "run", "dev"
        ], cwd=frontend_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for frontend to start
        time.sleep(5)
        
        print("✅ Frontend server started successfully!")
        print(f"🎨 Frontend available at: http://localhost:5173")
        return frontend_process
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start frontend: {e}")
        return None
    except FileNotFoundError:
        print("❌ npm not found. Please install Node.js and npm")
        return None

def main():
    """Main application launcher"""
    print("🎬 Viral AI Video Generator - Application Launcher")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        print("💡 Please install missing dependencies and try again")
        return
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("❌ Cannot start backend server")
        return
    
    # Start frontend
    frontend_process = start_frontend()
    
    # Print access information
    print("\n" + "🎉 Application is running!")
    print("=" * 60)
    print("🌐 Web Application: http://localhost:8000")
    print("📊 API Documentation: http://localhost:8000/docs")
    
    if frontend_process:
        print("🎨 Frontend Dev Server: http://localhost:5173")
    
    print("\n💡 Tips:")
    print("  - Use the web interface to generate videos")
    print("  - Check API docs for direct API usage")
    print("  - Press Ctrl+C to stop all servers")
    print("=" * 60)
    
    # Open web browser
    try:
        webbrowser.open("http://localhost:8000")
    except:
        pass
    
    # Wait for interrupt
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        
        # Kill processes
        if backend_process:
            backend_process.terminate()
            backend_process.wait()
        
        if frontend_process:
            frontend_process.terminate()
            frontend_process.wait()
        
        print("✅ All servers stopped")

if __name__ == "__main__":
    main()