#!/usr/bin/env python3
"""
Session Regeneration Script
Regenerates a session with all fixes applied
"""

import os
import sys
import subprocess
from pathlib import Path

def regenerate_session(original_topic: str, duration: int = 10, platform: str = "youtube"):
    """Regenerate a session with the correct topic and all fixes"""
    
    print(f"🎬 Regenerating session for topic: '{original_topic}'")
    print(f"⏱️ Duration: {duration}s")
    print(f"📱 Platform: {platform}")
    
    # Clean the topic
    clean_topic = original_topic
    if "Script Content" in clean_topic and "Optimization" in clean_topic:
        import re
        match = re.search(r"'([^']+)'", clean_topic)
        if match:
            clean_topic = match.group(1)
    
    print(f"🧹 Cleaned topic: '{clean_topic}'")
    
    # Run the generation with proper parameters
    cmd = [
        "python", "main.py", "generate",
        "--topic", clean_topic,
        "--duration", str(duration),
        "--platform", platform,
        "--discussions", "standard",
        "--image-only"  # Use image-only mode to avoid Veo quota issues
    ]
    
    print(f"🚀 Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print("✅ Regeneration successful!")
            print("📋 Output:")
            print(result.stdout)
            
            # Find the new session folder
            outputs_dir = Path("outputs")
            if outputs_dir.exists():
                session_folders = sorted([f for f in outputs_dir.iterdir() 
                                        if f.is_dir() and f.name.startswith("session_")])
                if session_folders:
                    latest_session = session_folders[-1]
                    print(f"📁 New session: {latest_session}")
                    return str(latest_session)
        else:
            print("❌ Regeneration failed!")
            print("📋 Error:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("⏰ Regeneration timed out")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    # Regenerate the problematic session
    original_topic = "USA political news test with real images"
    new_session = regenerate_session(original_topic, duration=10, platform="youtube")
    
    if new_session:
        print(f"🎉 Successfully created new session: {new_session}")
    else:
        print("💥 Failed to regenerate session")
