"""
File-based video repository implementation
"""

import json
import os
from typing import Optional, List
from pathlib import Path

from ...core.interfaces.repositories import VideoRepository
from ...core.entities.video_entity import VideoEntity

class FileVideoRepository(VideoRepository):
    """
    File-based implementation of VideoRepository

    Stores video entities as JSON files in a directory structure
    """

    def __init__(self, base_path: str = "data/videos"):
        """
        Initialize repository with base path

        Args:
            base_path: Base directory for storing video files
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save(self, video: VideoEntity) -> None:
        """Save a video entity to file"""
        video_file = self.base_path / f"{video.id}.json"

        # Convert entity to dictionary
        video_data = video.to_dict()

        # Save to file
        with open(video_file, 'w', encoding='utf-8') as f:
            json.dump(video_data, f, indent=2, ensure_ascii=False)

    async def get_by_id(self, video_id: str) -> Optional[VideoEntity]:
        """Get video by ID from file"""
        video_file = self.base_path / f"{video_id}.json"

        if not video_file.exists():
            return None

        try:
            with open(video_file, 'r', encoding='utf-8') as f:
                video_data = json.load(f)

            return VideoEntity.from_dict(video_data)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Log error but don't raise - return None for invalid data
            print(f"Error loading video {video_id}: {e}")
            return None

    async def list_by_session(self, session_id: str) -> List[VideoEntity]:
        """List videos by session ID"""
        videos = []

        # Iterate through all video files
        for video_file in self.base_path.glob("*.json"):
            try:
                with open(video_file, 'r', encoding='utf-8') as f:
                    video_data = json.load(f)

                # Check if video belongs to session
                if video_data.get("session_id") == session_id:
                    video = VideoEntity.from_dict(video_data)
                    videos.append(video)
            except (json.JSONDecodeError, KeyError, ValueError):
                # Skip invalid files
                continue

        # Sort by creation date
        videos.sort(key=lambda v: v.created_at)
        return videos

    async def delete(self, video_id: str) -> None:
        """Delete a video file"""
        video_file = self.base_path / f"{video_id}.json"

        if video_file.exists():
            video_file.unlink()

    async def list_all(self) -> List[VideoEntity]:
        """List all videos"""
        videos = []

        # Iterate through all video files
        for video_file in self.base_path.glob("*.json"):
            try:
                with open(video_file, 'r', encoding='utf-8') as f:
                    video_data = json.load(f)

                video = VideoEntity.from_dict(video_data)
                videos.append(video)
            except (json.JSONDecodeError, KeyError, ValueError):
                # Skip invalid files
                continue

        # Sort by creation date
        videos.sort(key=lambda v: v.created_at)
        return videos

    async def list_by_status(self, status: str) -> List[VideoEntity]:
        """List videos by status (additional method)"""
        videos = []

        # Iterate through all video files
        for video_file in self.base_path.glob("*.json"):
            try:
                with open(video_file, 'r', encoding='utf-8') as f:
                    video_data = json.load(f)

                # Check if video has the specified status
                if video_data.get("status") == status:
                    video = VideoEntity.from_dict(video_data)
                    videos.append(video)
            except (json.JSONDecodeError, KeyError, ValueError):
                # Skip invalid files
                continue

        # Sort by creation date
        videos.sort(key=lambda v: v.created_at)
        return videos

    def get_storage_path(self) -> str:
        """Get the storage path for this repository"""
        return str(self.base_path)

    def cleanup_old_files(self, days: int = 30) -> int:
        """
        Clean up old video files

        Args:
            days: Number of days to keep files

        Returns:
            Number of files cleaned up
        """
        import time

        cutoff_time = time.time() - (days * 24 * 60 * 60)
        cleaned_count = 0

        for video_file in self.base_path.glob("*.json"):
            if video_file.stat().st_mtime < cutoff_time:
                video_file.unlink()
                cleaned_count += 1

        return cleaned_count
