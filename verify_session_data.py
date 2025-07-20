#!/usr/bin/env python3
"""
Session Data Verification Script
Checks that all session data is properly organized
"""

import os
import json


def verify_session_data():
    """Verify session data structure and content"""
    
    # Check sessions directory
    sessions_dir = "outputs"
    
    if not os.path.exists(sessions_dir):
        print(f"❌ Sessions directory not found: {sessions_dir}")
        return False

    # Find all sessions
    sessions = [d for d in os.listdir(sessions_dir) if d.startswith("session_")]

    if not sessions:
        print("⚠️ No sessions found")
        return True

    print(f"📁 Found {len(sessions)} sessions")

    for session in sorted(sessions):
        session_path = os.path.join(sessions_dir, session)
        print(f"\n📂 Checking session: {session}")

        # Check required directories
        required_dirs = [
            'scripts', 'audio', 'video_clips', 'images', 'final_output',
            'temp_files', 'logs', 'discussions', 'metadata'
        ]

        missing_dirs = []
        for dir_name in required_dirs:
            dir_path = os.path.join(session_path, dir_name)
            if os.path.exists(dir_path):
                # Count files in directory
                files = [
                    f for f in os.listdir(dir_path) if os.path.isfile(
                        os.path.join(
                            dir_path, f))]
                print(f"   ✅ {dir_name}: {len(files)} files")
            else:
                missing_dirs.append(dir_name)
                print(f"   ❌ {dir_name}: missing")

        # Check session metadata
        metadata_file = os.path.join(session_path, "session_metadata.json")
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                print(f"   ✅ metadata: {len(metadata.get('files_tracked', {}))} files tracked")
            except Exception as e:
                print(f"   ⚠️ metadata: error reading ({e})")
        else:
            print("   ❌ metadata: session_metadata.json missing")

        # Check for video outputs
        final_output_dir = os.path.join(session_path, "final_output")
        if os.path.exists(final_output_dir):
            videos = [f for f in os.listdir(final_output_dir) if f.endswith('.mp4')]
            if videos:
                for video in videos:
                    video_path = os.path.join(final_output_dir, video)
                    size_mb = os.path.getsize(video_path) / (1024 * 1024)
                    print(f"   🎬 video: {video} ({size_mb:.1f}MB)")
            else:
                print("   ⚠️ video: no MP4 files in final_output")

    print("\n✅ Session data verification complete")
    return True


if __name__ == "__main__":
    verify_session_data()
