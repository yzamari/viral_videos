"""
Session Context Manager - Provides session-aware file operations
Ensures all generated content is properly organized within session directories
"""

import os
import shutil
from typing import Optional
from .session_manager import session_manager
from .logging_config import get_logger

logger = get_logger(__name__)

class SessionContext:
    """Context manager for session-aware file operations"""

    def __init__(self, session_id: str, session_manager_instance=None):
        """
        Initialize session context for a specific session

        Args:
            session_id: The session identifier
            session_manager_instance: Optional specific session manager instance
        """
        self.session_id = session_id
        self.session_manager = session_manager_instance or session_manager

        # Validate session exists
        if not self.session_manager.current_session:
            logger.warning(f"No active session found for {session_id}")
        
        # Set session directory with proper error handling
        try:
            self.session_dir = self._get_session_dir()
            if not self.session_dir:
                raise ValueError("Session directory is None or empty")
            logger.info(f"✅ Session context initialized for {session_id} at {self.session_dir}")
        except Exception as e:
            logger.error(f"Failed to initialize session directory: {e}")
            # Set a fallback directory
            self.session_dir = os.path.join("outputs", session_id)
            os.makedirs(self.session_dir, exist_ok=True)
            logger.info(f"Using fallback session directory: {self.session_dir}")
        
        # Always ensure essential subdirectories exist
        self._ensure_session_directories()

    def _ensure_session_directories(self):
        """Ensure all essential session subdirectories exist"""
        essential_dirs = [
            "metadata",
            "agent_discussions", 
            "audio",
            # "veo2_clips", # VEO2 deprecated
            "comprehensive_logs",
            "scripts",
            "analysis",
            "decisions",
            "hashtags",
            "final_output",
            "temp_files",  # Added for temporary video processing files
            "subtitles",   # Added for subtitle files
            "overlays"     # Added for overlay metadata
        ]
        
        for subdir in essential_dirs:
            dir_path = os.path.join(self.session_dir, subdir)
            os.makedirs(dir_path, exist_ok=True)
            
        # Create session metadata file if it doesn't exist
        metadata_file = os.path.join(self.session_dir, "metadata", "session_metadata.json")
        if not os.path.exists(metadata_file):
            import json
            from datetime import datetime
            metadata = {
                "session_id": self.session_id,
                "created": datetime.now().isoformat(),
                "status": "active",
                "session_dir": self.session_dir
            }
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            logger.info(f"Created session metadata file for {self.session_id}")

    def _get_session_dir(self) -> str:
        """Get the session directory path with proper error handling"""
        try:
            if self.session_manager and hasattr(self.session_manager, 'current_session') and self.session_manager.current_session == self.session_id:
                session_path = self.session_manager.get_session_path()
                if session_path:
                    return session_path
            
            # For non-active sessions or when session_manager is not available, construct path manually
            if hasattr(self.session_manager, 'base_output_dir'):
                return os.path.join(self.session_manager.base_output_dir, self.session_id)
            else:
                # Final fallback to outputs directory
                return os.path.join("outputs", self.session_id)
                
        except Exception as e:
            logger.error(f"Failed to get session directory: {e}")
            # Fallback to outputs directory
            fallback_dir = os.path.join("outputs", self.session_id)
            logger.info(f"Using fallback session directory: {fallback_dir}")
            return fallback_dir

    def get_output_path(self, subdir: str, filename: str = "") -> str:
        """
        Get session-aware output path for a file or directory

        Args:
            subdir: Subdirectory within session (e.g., 'final_output', 'video_clips')
            filename: Optional filename to append

        Returns:
            Full path within session directory
        """
        try:
            # Check if this is the current active session
            if self.session_manager.current_session == self.session_id:
                session_dir = self.session_manager.get_session_path(subdir)
                if filename:
                    return os.path.join(session_dir, filename)
                return session_dir
            else:
                # For non-active sessions, construct path manually
                base_session_dir = os.path.join(
                    self.session_manager.base_output_dir,
                    self.session_id)
                session_dir = os.path.join(base_session_dir, subdir)
                os.makedirs(session_dir, exist_ok=True)
                if filename:
                    return os.path.join(session_dir, filename)
                return session_dir
        except Exception as e:
            logger.error(f"Failed to get session path: '{subdir}' - {e}")
            # Fallback to outputs directory
            fallback_dir = os.path.join(
                self.session_manager.base_output_dir,
                self.session_id,
                subdir)
            os.makedirs(fallback_dir, exist_ok=True)
            if filename:
                return os.path.join(fallback_dir, filename)
            return fallback_dir

    def save_file(
        self,
        source_path: str,
        target_subdir: str,
        filename: str) -> str:
        """
        Save file to session directory with proper organization

        Args:
            source_path: Path to source file
            target_subdir: Target subdirectory within session
            filename: Target filename

        Returns:
            Path to saved file in session directory
        """
        try:
            target_path = self.get_output_path(target_subdir, filename)

            # Ensure target directory exists
            os.makedirs(os.path.dirname(target_path), exist_ok=True)

            if os.path.exists(source_path):
                shutil.copy2(source_path, target_path)
                logger.info(f"💾 Saved {filename} to session {target_subdir}")

                # Register with session manager if it's a final video
                if target_subdir == "final_output" and filename.startswith("final_video"):
                    return self.session_manager.save_final_video(target_path)

                return target_path
            else:
                logger.warning(f"Source file not found: {source_path}")
                return source_path

        except Exception as e:
            logger.error(f"Failed to save file {filename}: {e}")
            return source_path

    def save_final_video(self, video_path: str, suffix: str = "") -> str:
        """Save final video to session directory with optional suffix"""
        try:
            # Ensure final_output directory exists
            final_dir = self.get_output_path("final_output")
            os.makedirs(final_dir, exist_ok=True)
            
            # Generate final video filename with optional suffix
            if suffix:
                final_filename = f"final_video_{self.session_id}_{suffix}.mp4"
            else:
                final_filename = f"final_video_{self.session_id}.mp4"
            final_path = os.path.join(final_dir, final_filename)
            
            # Only copy if source and destination are different
            if os.path.abspath(video_path) != os.path.abspath(final_path):
                import shutil
                shutil.copy2(video_path, final_path)
                logger.info(f"💾 Final video copied to: {final_path}")
            else:
                logger.info(f"💾 Final video already in correct location: {final_path}")
            
            return final_path
            
        except Exception as e:
            logger.error(f"❌ Failed to save final video: {e}")
            return video_path

    def save_video_clip(self, clip_path: str, clip_id: str) -> str:
        """
        Save video clip to session's video_clips directory

        Args:
            clip_path: Path to video clip
            clip_id: Unique identifier for the clip

        Returns:
            Path to saved clip in session directory
        """
        filename = f"video_clip_{clip_id}.mp4"
        return self.save_file(clip_path, "video_clips", filename)

    def save_audio_file(self, audio_path: str, audio_id: str) -> str:
        """
        Save audio file to session's audio directory

        Args:
            audio_path: Path to audio file
            audio_id: Unique identifier for the audio

        Returns:
            Path to saved audio in session directory
        """
        filename = f"audio_{audio_id}.mp3"
        return self.save_file(audio_path, "audio", filename)

    def save_image(self, image_path: str, image_id: str) -> str:
        """
        Save image to session's images directory

        Args:
            image_path: Path to image file
            image_id: Unique identifier for the image

        Returns:
            Path to saved image in session directory
        """
        # Determine file extension
        _, ext = os.path.splitext(image_path)
        if not ext:
            ext = ".jpg"  # Default extension

        filename = f"image_{image_id}{ext}"
        return self.save_file(image_path, "images", filename)

    def get_session_summary(self) -> dict:
        """
        Get summary of session content and organization

        Returns:
            Dictionary with session summary information
        """
        try:
            session_dir = self.session_manager.get_session_path()
            summary = {
                "session_id": self.session_id,
                "session_directory": session_dir,
                "subdirectories": {},
                "file_counts": {},
                "total_size_mb": 0.0
            }

            # Analyze each subdirectory
            subdirs = ["final_output", "video_clips", "audio", "images", "scripts", "logs", "metadata"]

            for subdir in subdirs:
                subdir_path = self.get_output_path(subdir)
                if os.path.exists(subdir_path):
                    files = os.listdir(subdir_path)
                    file_count = len([f for f in files if os.path.isfile(os.path.join(subdir_path, f))])

                    # Calculate directory size
                    dir_size = 0
                    for f in files:
                        file_path = os.path.join(subdir_path, f)
                        if os.path.isfile(file_path):
                            dir_size += os.path.getsize(file_path)

                    summary["subdirectories"][subdir] = subdir_path
                    summary["file_counts"][subdir] = file_count
                    summary["total_size_mb"] += dir_size / (1024 * 1024)

            return summary

        except Exception as e:
            logger.error(f"Failed to generate session summary: {e}")
            return {"session_id": self.session_id, "error": str(e)}

    def cleanup_session(self, keep_final_output: bool = True) -> bool:
        """
        Clean up session temporary files

        Args:
            keep_final_output: Whether to keep the final output directory

        Returns:
            True if cleanup was successful
        """
        try:
            session_dir = self.session_manager.get_session_path()

            # Directories to clean up
            cleanup_dirs = ["video_clips", "audio", "images"]
            if not keep_final_output:
                cleanup_dirs.append("final_output")

            cleaned_files = 0
            for subdir in cleanup_dirs:
                subdir_path = self.get_output_path(subdir)
                if os.path.exists(subdir_path):
                    for file in os.listdir(subdir_path):
                        file_path = os.path.join(subdir_path, file)
                        if os.path.isfile(file_path) and not file.startswith("final_"):
                            os.remove(file_path)
                            cleaned_files += 1

            logger.info(f"🧹 Cleaned up {cleaned_files} temporary files from session {self.session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to cleanup session: {e}")
            return False

def create_session_context(
    session_id: str,
    session_manager_instance=None) -> SessionContext:
    """
    Factory function to create a session context

    Args:
        session_id: The session identifier
        session_manager_instance: Optional specific session manager instance

    Returns:
        SessionContext instance
    """
    return SessionContext(session_id, session_manager_instance)

def get_current_session_context() -> Optional[SessionContext]:
    """
    Get session context for the current active session

    Returns:
        SessionContext for current session or None if no active session
    """
    if session_manager.current_session:
        return SessionContext(session_manager.current_session)
    return None
