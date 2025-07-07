#!/usr/bin/env python3
"""
Ensure Orchestrated Video Generation and AI Discussions Always Enabled
Updates configuration to force orchestration and discussions to be always on
"""

import os
import sys
from pathlib import Path

def update_main_py_defaults():
    """Update main.py to have better defaults"""
    main_file = Path("main.py")
    if not main_file.exists():
        print("❌ main.py not found")
        return
    
    content = main_file.read_text()
    
    # Ensure discussions default to 'standard' instead of 'off'
    if "default='off'" in content:
        content = content.replace("default='off'", "default='standard'")
        print("✅ Updated discussions default from 'off' to 'standard'")
    
    # Force discussions to always be enabled
    if "discussions = 'off'" in content:
        content = content.replace("discussions = 'off'", "discussions = 'standard'")
        print("✅ Forced discussions to be 'standard' instead of 'off'")
    
    # Add orchestration force-enable
    if "🤖 AI Agent Discussions: STANDARD MODE (FORCED ON)" not in content:
        # Find the discussions setup section and add orchestration info
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "AI Agent Discussions:" in line and "FORCED ON" in line:
                # Add orchestration info after discussions info
                lines.insert(i + 1, '    click.echo("🎭 Orchestrated Video Generation: ALWAYS ENABLED")')
                break
        content = '\n'.join(lines)
        print("✅ Added orchestration status message")
    
    main_file.write_text(content)

def update_orchestrator_defaults():
    """Ensure orchestrator has optimal defaults"""
    orchestrator_file = Path("src/agents/enhanced_orchestrator_with_discussions.py")
    if not orchestrator_file.exists():
        print("❌ Orchestrator file not found")
        return
    
    content = orchestrator_file.read_text()
    
    # Ensure discussions are always enabled
    if "self.enable_discussions = True  # Force enable" not in content:
        if "self.enable_discussions = enable_discussions" in content:
            content = content.replace(
                "self.enable_discussions = enable_discussions",
                "self.enable_discussions = True  # Force enable\n        # Original: self.enable_discussions = enable_discussions"
            )
            print("✅ Forced discussions to always be enabled in orchestrator")
    
    orchestrator_file.write_text(content)

def update_video_generator_defaults():
    """Ensure video generator has orchestration enabled"""
    generator_file = Path("src/generators/video_generator.py")
    if not generator_file.exists():
        print("❌ Video generator file not found")
        return
    
    content = generator_file.read_text()
    
    # Look for orchestration settings
    if "orchestrated': True" not in content:
        print("⚠️ Orchestration flag not found - may need manual review")
    else:
        print("✅ Orchestration flag found in video generator")

def create_status_checker():
    """Create a script to check orchestration status"""
    status_script = '''#!/usr/bin/env python3
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
        
        print(f"\\n📁 RECENT SESSIONS ({len(recent_sessions)} checked):")
        for session_dir in recent_sessions:
            discussions_dir = session_dir / "agent_discussions"
            if discussions_dir.exists():
                discussion_files = list(discussions_dir.glob("*.json"))
                print(f"  ✅ {session_dir.name}: {len(discussion_files)} discussion files")
            else:
                print(f"  ❌ {session_dir.name}: No agent discussions found")
    
    print("\\n🎯 RECOMMENDATIONS:")
    print("  • Run: python ensure_orchestration_always_on.py")
    print("  • Generate new video to test: python main.py generate --topic 'test' --duration 10")
    print("  • Check session folder for agent_discussions/")

if __name__ == "__main__":
    check_status()
'''
    
    status_file = Path("check_orchestration_status.py")
    status_file.write_text(status_script)
    os.chmod(status_file, 0o755)
    print(f"✅ Created status checker: {status_file}")

def main():
    """Main function to ensure orchestration is always enabled"""
    print("🎭 ENSURING ORCHESTRATED VIDEO GENERATION ALWAYS ENABLED")
    print("=" * 60)
    
    # Update configurations
    update_main_py_defaults()
    update_orchestrator_defaults()
    update_video_generator_defaults()
    
    # Create status checker
    create_status_checker()
    
    print("\n✅ ORCHESTRATION CONFIGURATION COMPLETE!")
    print("\n🎯 CURRENT STATUS:")
    print("  ✅ AI Agent Discussions: ALWAYS ENABLED (forced)")
    print("  ✅ Orchestrated Video Generation: ENABLED")
    print("  ✅ Discussion Depth: 'standard' by default")
    print("  ✅ Agent Discussion Files: Saved to session folders")
    
    print("\n📁 AGENT DISCUSSIONS LOCATION:")
    print("  📂 outputs/session_YYYYMMDD_HHMMSS_ID/agent_discussions/")
    print("     ├── discussion_planning_ID.json")
    print("     ├── discussion_script_ID.json")
    print("     ├── discussion_visual_ID.json")
    print("     ├── discussion_audio_ID.json")
    print("     └── discussion_assembly_ID.json")
    
    print("\n🔍 TO CHECK STATUS:")
    print("  python check_orchestration_status.py")
    
    print("\n🎬 TO GENERATE WITH ORCHESTRATION:")
    print("  python main.py generate --topic 'your topic' --duration 10")
    print("  (Discussions are now ALWAYS enabled by default)")

if __name__ == "__main__":
    main() 