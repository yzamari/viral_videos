#!/usr/bin/env python3
"""
Clean up incomplete output folders - Automatic version
"""

import os
import shutil
from pathlib import Path
from typing import List, Tuple

def check_episode_completeness(episode_dir: Path) -> Tuple[bool, str]:
    """Check if an episode has a final video"""
    final_output_dir = episode_dir / 'final_output'
    
    if not final_output_dir.exists():
        return False, "No final_output directory"
    
    # Look for final videos
    final_videos = list(final_output_dir.glob('*__final.mp4'))
    
    # Filter out backup/temp files
    final_videos = [v for v in final_videos if not any(x in v.name for x in ['backup', 'original', 'temp', 'fixed', 'complete'])]
    
    if not final_videos:
        return False, "No final video found"
    
    # Check if the final video is valid
    for video in final_videos:
        if video.stat().st_size > 1000000:  # At least 1MB
            return True, f"Found: {video.name}"
    
    return False, "Final video too small or corrupted"

def main():
    """Clean up incomplete output folders"""
    print("🧹 Cleaning Up Incomplete Output Folders (Auto Mode)")
    print("=" * 50)
    
    outputs_dir = Path('/Users/yahavzamari/viralAi/outputs')
    
    if not outputs_dir.exists():
        print("❌ Outputs directory not found!")
        return
    
    # Get all directories in outputs
    all_dirs = [d for d in outputs_dir.iterdir() if d.is_dir()]
    
    complete_episodes = []
    incomplete_episodes = []
    
    print(f"\n📊 Found {len(all_dirs)} directories in outputs/\n")
    
    # Check each directory
    for episode_dir in sorted(all_dirs):
        is_complete, status = check_episode_completeness(episode_dir)
        
        if is_complete:
            complete_episodes.append(episode_dir.name)
            print(f"✅ {episode_dir.name} - KEEPING")
            print(f"   └─ {status}")
        else:
            incomplete_episodes.append((episode_dir, status))
            print(f"❌ {episode_dir.name} - TO DELETE")
            print(f"   └─ {status}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")
    print(f"  ✅ Complete: {len(complete_episodes)} episodes (keeping)")
    print(f"  ❌ Incomplete: {len(incomplete_episodes)} episodes (deleting)")
    
    if incomplete_episodes:
        print("\n🗑️  DELETING INCOMPLETE FOLDERS...")
        deleted_count = 0
        failed_count = 0
        
        for episode_dir, reason in incomplete_episodes:
            try:
                shutil.rmtree(episode_dir)
                print(f"  ✅ Deleted: {episode_dir.name}")
                deleted_count += 1
            except Exception as e:
                print(f"  ❌ Failed to delete {episode_dir.name}: {e}")
                failed_count += 1
        
        print(f"\n✅ Cleanup complete!")
        print(f"   • Deleted: {deleted_count} folders")
        if failed_count > 0:
            print(f"   • Failed: {failed_count} folders")
    else:
        print("\n✅ All episodes have final videos!")
    
    # List remaining folders
    print("\n📁 REMAINING FOLDERS:")
    remaining = [d.name for d in outputs_dir.iterdir() if d.is_dir()]
    for folder in sorted(remaining):
        print(f"  • {folder}")

if __name__ == "__main__":
    main()