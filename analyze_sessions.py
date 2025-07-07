#!/usr/bin/env python3
"""
Session Analyzer
Analyzes session completeness and identifies missing components
"""

import os
import json
from pathlib import Path
from datetime import datetime

def analyze_session(session_path: str):
    """Analyze a session folder for completeness"""
    session_dir = Path(session_path)
    if not session_dir.exists():
        print(f"❌ Session not found: {session_path}")
        return
    
    print(f"🔍 Analyzing session: {session_dir.name}")
    print("=" * 60)
    
    # Check required files
    required_files = {
        "video": ["*.mp4"],
        "audio": ["*.mp3"],
        "scripts": ["script_*.txt", "tts_script_*.txt", "veo2_prompts_*.txt"],
        "analysis": ["video_analysis.txt"]
    }
    
    # Check optional directories
    optional_dirs = ["clips", "images", "agent_discussions"]
    
    # Analyze file structure
    all_files = list(session_dir.rglob("*"))
    file_count = len([f for f in all_files if f.is_file()])
    dir_count = len([f for f in all_files if f.is_dir()])
    
    print(f"📊 Total files: {file_count}")
    print(f"📁 Total directories: {dir_count}")
    print()
    
    # Check each category
    for category, patterns in required_files.items():
        print(f"📋 {category.upper()}:")
        found_files = []
        for pattern in patterns:
            matches = list(session_dir.glob(pattern)) + list(session_dir.glob(f"**/{pattern}"))
            found_files.extend(matches)
        
        if found_files:
            for file in found_files:
                size = file.stat().st_size / 1024  # KB
                print(f"  ✅ {file.name} ({size:.1f} KB)")
        else:
            print(f"  ❌ Missing {category} files")
        print()
    
    # Check optional directories
    print("📁 OPTIONAL DIRECTORIES:")
    for dir_name in optional_dirs:
        dir_path = session_dir / dir_name
        if dir_path.exists():
            files_in_dir = len(list(dir_path.iterdir()))
            print(f"  ✅ {dir_name}/ ({files_in_dir} items)")
        else:
            print(f"  ⚠️  {dir_name}/ (missing)")
    print()
    
    # Analyze video analysis file
    analysis_file = session_dir / "video_analysis.txt"
    if analysis_file.exists():
        print("📊 VIDEO ANALYSIS:")
        content = analysis_file.read_text()
        
        # Extract key metrics
        lines = content.split('\n')
        for line in lines:
            if any(keyword in line for keyword in ["Duration:", "Generation Time:", "Total Clips:", "File Size:"]):
                print(f"  {line.strip()}")
        print()
    
    # Check for issues
    issues = []
    
    # Check for empty clips directory
    clips_dir = session_dir / "clips"
    if clips_dir.exists() and not any(clips_dir.iterdir()):
        issues.append("Empty clips directory")
    
    # Check for very small audio files
    audio_files = list(session_dir.glob("*.mp3")) + list(session_dir.glob("**/*.mp3"))
    for audio_file in audio_files:
        if audio_file.stat().st_size < 50000:  # Less than 50KB
            issues.append(f"Very small audio file: {audio_file.name}")
    
    # Check for missing agent discussions
    if not (session_dir / "agent_discussions").exists():
        issues.append("Missing agent discussions")
    
    if issues:
        print("🚨 ISSUES FOUND:")
        for issue in issues:
            print(f"  ❌ {issue}")
    else:
        print("✅ No critical issues found")
    
    print()
    print("🎯 RECOMMENDATIONS:")
    if issues:
        print("  • Regenerate session with fixes applied")
        print("  • Use --image-only mode to avoid Veo quota issues")
        print("  • Check topic interpretation")
    else:
        print("  • Session appears complete")

def analyze_all_sessions():
    """Analyze all sessions"""
    outputs_dir = Path("outputs")
    if not outputs_dir.exists():
        print("❌ No outputs directory found")
        return
    
    session_dirs = [d for d in outputs_dir.iterdir() if d.is_dir() and d.name.startswith("session_")]
    
    if not session_dirs:
        print("❌ No session directories found")
        return
    
    print(f"🔍 Found {len(session_dirs)} sessions")
    print()
    
    for session_dir in sorted(session_dirs):
        analyze_session(str(session_dir))
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        analyze_session(sys.argv[1])
    else:
        analyze_all_sessions()
