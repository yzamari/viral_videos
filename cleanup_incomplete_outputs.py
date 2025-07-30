#!/usr/bin/env python3
"""
Clean up incomplete output folders
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
    print("🧹 Cleaning Up Incomplete Output Folders")
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
            print(f"✅ {episode_dir.name}")
            print(f"   └─ {status}")
        else:
            incomplete_episodes.append((episode_dir, status))
            print(f"❌ {episode_dir.name}")
            print(f"   └─ {status}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")
    print(f"  ✅ Complete: {len(complete_episodes)} episodes")
    print(f"  ❌ Incomplete: {len(incomplete_episodes)} episodes")
    
    if incomplete_episodes:
        print("\n🗑️  FOLDERS TO DELETE:")
        for episode_dir, reason in incomplete_episodes:
            print(f"  • {episode_dir.name} ({reason})")
        
        # Confirm deletion
        print("\n⚠️  This will permanently delete these folders!")
        response = input("Proceed with deletion? (yes/no): ")
        
        if response.lower() == 'yes':
            print("\n🗑️  Deleting incomplete folders...")
            for episode_dir, _ in incomplete_episodes:
                try:
                    shutil.rmtree(episode_dir)
                    print(f"  ✅ Deleted: {episode_dir.name}")
                except Exception as e:
                    print(f"  ❌ Failed to delete {episode_dir.name}: {e}")
            print("\n✅ Cleanup complete!")
        else:
            print("\n❌ Deletion cancelled.")
    else:
        print("\n✅ All episodes have final videos!")

if __name__ == "__main__":
    main()