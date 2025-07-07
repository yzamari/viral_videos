#!/usr/bin/env python3
"""
Check Orchestration and Discussion Status
Verifies that orchestrated video generation and AI discussions are properly enabled
"""

import os
import sys
from pathlib import Path

def check_status():
    """Check the current status of orchestration and discussions"""
    print("🔍 ORCHESTRATION & DISCUSSIONS STATUS CHECK")
    print("=" * 60)
    
    # Check main.py defaults
    main_file = Path("main.py")
    if main_file.exists():
        content = main_file.read_text()
        if "default='standard'" in content:
            print("✅ main.py: Discussions default to 'standard'")
        else:
            print("❌ main.py: Discussions may not default to 'standard'")
    
    # Check orchestrator
    orchestrator_file = Path("src/agents/enhanced_orchestrator_with_discussions.py")
    if orchestrator_file.exists():
        content = orchestrator_file.read_text()
        if "Force enable" in content or "FORCED ENABLED" in content:
            print("✅ Orchestrator: Discussions forced to be enabled")
        else:
            print("❌ Orchestrator: Discussions may not be forced")
    
    # Check current sessions
    outputs_dir = Path("outputs")
    if outputs_dir.exists():
        session_dirs = [d for d in outputs_dir.iterdir() if d.is_dir() and d.name.startswith("session_")]
        recent_sessions = sorted(session_dirs, key=lambda x: x.stat().st_mtime)[-3:]
        
        print(f"\n📁 RECENT SESSIONS ({len(recent_sessions)} checked):")
        for session_dir in recent_sessions:
            discussions_dir = session_dir / "agent_discussions"
            if discussions_dir.exists():
                discussion_files = list(discussions_dir.glob("*.json"))
                print(f"  ✅ {session_dir.name}: {len(discussion_files)} discussion files")
            else:
                print(f"  ❌ {session_dir.name}: No agent discussions found")
    
    print("\n🎯 RECOMMENDATIONS:")
    print("  • Run: python ensure_orchestration_always_on.py")
    print("  • Generate new video to test: python main.py generate --topic 'test' --duration 10")
    print("  • Check session folder for agent_discussions/")

if __name__ == "__main__":
    check_status()
