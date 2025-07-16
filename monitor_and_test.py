#!/usr/bin/env python3
"""
Comprehensive monitoring and testing script for AI agent discussions
"""

import os
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def monitor_session_files(session_id):
    """Monitor session files in real-time"""
    # Fix to avoid double session_ prefix
    session_dir = f"outputs/{session_id}" if session_id.startswith("session_") else f"outputs/session_{session_id}"
    
    # Create session directory if it doesn't exist
    os.makedirs(session_dir, exist_ok=True)
    
    # Create metadata file
    metadata_file = os.path.join(session_dir, "session_metadata.json")

    print(f"\n📁 MONITORING SESSION: {session_id}")
    print("=" * 50)

    if not os.path.exists(session_dir):
        print(f"❌ Session directory not found: {session_dir}")
        return

    # Check session metadata
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
            print("✅ Session Metadata:")
            print(f"   Mission: {metadata.get('mission', 'MISSING')}")
            print(f"   Platform: {metadata.get('platform', 'MISSING')}")
            print(f"   Category: {metadata.get('category', 'MISSING')}")
            print(f"   Status: {metadata.get('status', 'MISSING')}")

    # Monitor subdirectories
    subdirs = ['scripts', 'audio', 'video_clips', 'discussions', 'final_output', 'logs']

    for subdir in subdirs:
        subdir_path = os.path.join(session_dir, subdir)
        if os.path.exists(subdir_path):
            files = os.listdir(subdir_path)
            if files:
                print(f"📂 {subdir}/: {len(files)} files")
                for file in files[:3]:  # Show first 3 files
                    file_path = os.path.join(subdir_path, file)
                    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                    print(f"   - {file} ({file_size} bytes)")
                if len(files) > 3:
                    print(f"   ... and {len(files) - 3} more files")
            else:
                print(f"📂 {subdir}/: empty")
        else:
            print(f"📂 {subdir}/: not created")


def check_discussion_content(session_id):
    """Check if discussions contain the correct mission content"""
    # Fix to avoid double session_ prefix
    discussions_dir = f"outputs/{session_id}/discussions" if session_id.startswith("session_") else f"outputs/session_{session_id}/discussions"

    print("\n🤖 CHECKING AI DISCUSSIONS")
    print("=" * 50)

    if not os.path.exists(discussions_dir):
        print("❌ Discussions directory not found")
        return False

    discussion_files = [f for f in os.listdir(discussions_dir) if f.endswith('.json')]

    if not discussion_files:
        print("⚠️ No discussion files found")
        return False

    mission_keywords = ['iran', 'nuclear', 'diplomatic', 'weapons', 'peace', 'dialogue']
    wrong_keywords = ['cold shower', 'ai technology', 'supply chain', 'healthcare']

    for file in discussion_files:
        file_path = os.path.join(discussions_dir, file)
        try:
            with open(file_path, 'r') as f:
                content = json.load(f)
                content_str = json.dumps(content).lower()

                print(f"📄 {file}:")

                # Check for mission keywords
                mission_found = any(keyword in content_str for keyword in mission_keywords)
                wrong_found = any(keyword in content_str for keyword in wrong_keywords)

                if mission_found:
                    print("   ✅ Contains mission-related content")
                    found_keywords = [kw for kw in mission_keywords if kw in content_str]
                    print(f"   Keywords found: {found_keywords}")
                else:
                    print("   ❌ No mission-related content found")

                if wrong_found:
                    print("   🚨 Contains wrong topic content!")
                    wrong_keywords_found = [kw for kw in wrong_keywords if kw in content_str]
                    print(f"   Wrong keywords: {wrong_keywords_found}")

                # Show a snippet of the content
                if 'discussion_log' in content and content['discussion_log']:
                    first_message = content['discussion_log'][0]
                    if 'message' in first_message:
                        snippet = first_message['message'][:100]
                        print(f"   Preview: {snippet}...")

        except Exception as e:
            print(f"   ❌ Error reading {file}: {e}")

    return True


def check_logs_for_issues():
    """Check logs for common issues"""
    print("\n📋 CHECKING LOGS FOR ISSUES")
    print("=" * 50)

    log_file = "logs/viral_video_20250713.log"
    if not os.path.exists(log_file):
        print(f"❌ Log file not found: {log_file}")
        return

    # Read last 50 lines
    with open(log_file, 'r') as f:
        lines = f.readlines()
        recent_lines = lines[-50:] if len(lines) > 50 else lines

    issues_found = []

    for line in recent_lines:
        line_lower = line.lower()

        # Check for template issues
        if '{agent_info[' in line or '{topic}' in line:
            issues_found.append(f"🚨 Template formatting issue: {line.strip()}")

        # Check for wrong topic discussions
        if any(word in line_lower for word in ['cold shower', 'supply chain', 'healthcare ai']):
            issues_found.append(f"🚨 Wrong topic discussion: {line.strip()}")

        # Check for session issues
        if 'no active session' in line_lower or 'session not found' in line_lower:
            issues_found.append(f"⚠️ Session issue: {line.strip()}")

        # Check for import errors
        if 'importerror' in line_lower or 'modulenotfounderror' in line_lower:
            issues_found.append(f"❌ Import error: {line.strip()}")

    if issues_found:
        print("🚨 ISSUES FOUND:")
        for issue in issues_found[-10:]:  # Show last 10 issues
            print(f"   {issue}")
    else:
        print("✅ No major issues found in recent logs")


def main():
    """Main monitoring function"""
    print("🔍 COMPREHENSIVE SESSION MONITORING")
    print("=" * 60)

    # Monitor existing sessions
    sessions_dir = "outputs"
    
    if not os.path.exists(sessions_dir):
        print(f"Sessions directory {sessions_dir} not found")
        return
    
    # Get all session directories
    session_dirs = [d for d in os.listdir(sessions_dir) 
                   if d.startswith("session_") and 
                   os.path.isdir(os.path.join(sessions_dir, d))]

    if session_dirs:
        latest_session = sorted(session_dirs)[-1]
        print(f"📊 Latest session: {latest_session}")

        # Monitor session files
        monitor_session_files(latest_session)

        # Check discussion content
        check_discussion_content(latest_session)

    else:
        print(f"⚠️ No sessions found in {sessions_dir}")

    # Check logs
    check_logs_for_issues()

    print("\n🎯 MONITORING COMPLETE")


if __name__ == "__main__":
    main()
