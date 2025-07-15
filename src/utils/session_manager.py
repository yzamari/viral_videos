"""
Session Manager - Comprehensive session organization system
Creates dedicated folders for each session with all logs, data, AI agent outputs, and
        generated content
Enhanced to ensure 100% file capture and organization
"""

import os
import json
import shutil
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import glob
import re

from .logging_config import get_logger

logger = get_logger(__name__)

class SessionManager:
    """Manages session organization and data storage with comprehensive file tracking"""

    def __init__(self, base_output_dir: str = "outputs"):
        self.base_output_dir = base_output_dir
        self.current_session = None
        self.session_data = {}
        self.tracked_files = {}  # Track all files created during session

    def create_session(
        self,
        topic: str,
        platform: str,
        duration: int,
        category: str) -> str:
        """Create a new session with organized folder structure"""

        # Generate session ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"session_{timestamp}"

        # Create session directory structure
        session_dir = os.path.join(self.base_output_dir, session_id)

        # Create all subdirectories - COMPREHENSIVE LIST
        subdirs = [
            "logs",                    # All log files
            "scripts",                 # Generated scripts and text
            "audio",                   # TTS audio files
            "video_clips",             # Individual video clips
            "images",                  # Generated images
            "ai_agents",               # AI agent decisions and logs
            "discussions",             # Agent discussions
            "final_output",            # Final composed video
            "metadata",                # Session metadata and configs
            "comprehensive_logs",      # Comprehensive logging data
            "temp_files",              # Temporary files during generation
            "fallback_content",        # Fallback generation content
            "debug_info",              # Debug information
            "performance_metrics",     # Performance and timing data
            "user_configs",            # User configuration snapshots
            "error_logs",              # Error-specific logs
            "success_metrics"          # Success tracking metrics
        ]

        for subdir in subdirs:
            os.makedirs(os.path.join(session_dir, subdir), exist_ok=True)

        # Initialize session data
        self.current_session = session_id
        self.session_data = {
            "session_id": session_id,
            "timestamp": timestamp,
            "topic": topic,
            "platform": platform,
            "duration": duration,
            "category": category,
            "session_dir": session_dir,
            "subdirs": {subdir: os.path.join(session_dir, subdir) for subdir in subdirs},
            "ai_decisions": {},
            "generation_log": [],
            "errors": [],
            "warnings": [],
            "tracked_files": {},
            "file_counts": {subdir: 0 for subdir in subdirs},
            "total_files_created": 0,
            "comprehensive_logger": None
        }

        # Initialize comprehensive logger for this session
        self._initialize_comprehensive_logger()

        # Save session metadata
        self._save_session_metadata()

        logger.info(f"📁 Created session: {session_id}")
        logger.info(f"📂 Session directory: {session_dir}")
        logger.info(f"📊 Subdirectories created: {len(subdirs)}")

        return session_id

    def _initialize_comprehensive_logger(self):
        """Initialize comprehensive logger for this session"""
        try:
            from .comprehensive_logger import ComprehensiveLogger
            self.session_data["comprehensive_logger"] = ComprehensiveLogger(
                session_id=self.current_session,
                session_dir=self.session_data["session_dir"]
            )
            logger.info("📊 Comprehensive logger initialized for session")
        except Exception as e:
            logger.warning(f"Failed to initialize comprehensive logger: {e}")

    @staticmethod
    def get_static_session_path(session_id: str, subdir: str = None) -> str:
        """Get path for session or specific subdirectory (static method)"""
        base_session_dir = os.path.join("outputs", "sessions", session_id)
        
        if subdir:
            return os.path.join(base_session_dir, subdir)
        else:
            return base_session_dir

    def get_session_path(self, subdir: str = None) -> str:
        """Get path for session or specific subdirectory"""
        if not self.current_session:
            raise ValueError("No active session")

        if subdir:
            return self.session_data["subdirs"][subdir]
        return self.session_data["session_dir"]

    def track_file(
        self,
        file_path: str,
        file_type: str,
        source: str = "system") -> str:
        """Track a file created during session and ensure it is in the session directory"""
        if not self.current_session:
            return file_path

        try:
            # Determine target subdirectory based on file type
            subdir_mapping = {
                "script": "scripts",
                "audio": "audio",
                "video_clip": "video_clips",
                "image": "images",
                "log": "logs",
                "discussion": "discussions",
                "ai_decision": "ai_agents",
                "final_video": "final_output",
                "metadata": "metadata",
                "comprehensive_log": "comprehensive_logs",
                "temp": "temp_files",
                "fallback": "fallback_content",
                "debug": "debug_info",
                "performance": "performance_metrics",
                "config": "user_configs",
                "error": "error_logs"
            }

            target_subdir = subdir_mapping.get(file_type, "temp_files")

            # If file is already in session directory, just track it
            session_dir = self.session_data["session_dir"]
            if file_path.startswith(session_dir):
                self.tracked_files[file_path] = {
                    "type": file_type,
                    "source": source,
                    "timestamp": datetime.now().isoformat(),
                    "subdir": target_subdir
                }
                self.session_data["file_counts"][target_subdir] += 1
                self.session_data["total_files_created"] += 1
                return file_path

            # Move file to session directory
            target_dir = self.get_session_path(target_subdir)
            filename = os.path.basename(file_path)

            # Handle duplicate filenames
            counter = 1
            base_name, ext = os.path.splitext(filename)
            while os.path.exists(os.path.join(target_dir, filename)):
                filename = f"{base_name}_{counter}{ext}"
                counter += 1

            target_path = os.path.join(target_dir, filename)

            # Copy/move file
            if os.path.exists(file_path):
                shutil.copy2(file_path, target_path)

                # Track the file
                self.tracked_files[target_path] = {
                    "type": file_type,
                    "source": source,
                    "timestamp": datetime.now().isoformat(),
                    "original_path": file_path,
                    "subdir": target_subdir
                }

                self.session_data["file_counts"][target_subdir] += 1
                self.session_data["total_files_created"] += 1

                logger.info(f"📁 Tracked {file_type} file: {filename} -> {target_subdir}/")

                return target_path
            else:
                logger.warning(f"⚠️ File not found for tracking: {file_path}")
                return file_path

        except Exception as e:
            logger.error(f"❌ Failed to track file {file_path}: {e}")
            return file_path

    def log_ai_decision(self, agent_name: str, decision_data: Dict[str, Any]):
        """Log AI agent decision to session"""
        if not self.current_session:
            return

        decision_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "decision": decision_data
        }

        self.session_data["ai_decisions"][agent_name] = decision_entry

        # Save to AI agents directory
        agent_file = os.path.join(
            self.get_session_path("ai_agents"),
            f"{agent_name}_decision.json")
        with open(agent_file, 'w') as f:
            json.dump(decision_entry, f, indent=2)

        # Track the file
        self.track_file(agent_file, "ai_decision", agent_name)

        logger.info(f"💾 Logged {agent_name} decision to session")

    def save_discussion(
        self,
        discussion_data: Dict[str,
        Any],
        discussion_id: str) -> str:
        """Save AI agent discussion to session"""
        if not self.current_session:
            return ""

        discussion_file = os.path.join(
            self.get_session_path("discussions"),
            f"discussion_{discussion_id}.json"
        )

        with open(discussion_file, 'w') as f:
            json.dump(discussion_data, f, indent=2, default=str)

        # Track the file
        self.track_file(discussion_file, "discussion", "MultiAgentDiscussion")

        logger.info(f"💾 Saved discussion to session: {discussion_id}")
        return discussion_file

    def save_script(self, script_content: str, script_type: str = "main") -> str:
        """Save script to session"""
        if not self.current_session:
            return ""

        # Handle different script formats
        if isinstance(script_content, dict):
            script_file = os.path.join(
                self.get_session_path("scripts"),
                f"{script_type}_script.json")
            with open(script_file, 'w') as f:
                json.dump(script_content, f, indent=2)
        else:
            script_file = os.path.join(
                self.get_session_path("scripts"),
                f"{script_type}_script.txt")
            with open(script_file, 'w') as f:
                f.write(str(script_content))

        # Track the file
        self.track_file(script_file, "script", "ScriptProcessor")

        logger.info(f"💾 Saved {script_type} script to session")
        return script_file

    def save_audio(self, audio_path: str, clip_id: str) -> str:
        """Save audio file to session"""
        if not self.current_session:
            return audio_path

        session_audio_dir = self.get_session_path("audio")
        filename = f"audio_clip_{clip_id}.mp3"
        session_audio_path = os.path.join(session_audio_dir, filename)

        if os.path.exists(audio_path):
            shutil.copy2(audio_path, session_audio_path)
            self.track_file(session_audio_path, "audio", "TTS")
            logger.info(f"💾 Saved audio clip {clip_id} to session")
            return session_audio_path

        return audio_path

    def save_video_clip(self, video_path: str, clip_id: str) -> str:
        """Save video clip to session"""
        if not self.current_session:
            return video_path

        session_video_dir = self.get_session_path("video_clips")
        filename = f"video_clip_{clip_id}.mp4"
        session_video_path = os.path.join(session_video_dir, filename)

        if os.path.exists(video_path):
            shutil.copy2(video_path, session_video_path)
            self.track_file(session_video_path, "video_clip", "VEO/Gemini")
            logger.info(f"💾 Saved video clip {clip_id} to session")
            return session_video_path

        return video_path

    def save_image(self, image_path: str, image_id: str) -> str:
        """Save image to session"""
        if not self.current_session:
            return image_path

        session_images_dir = self.get_session_path("images")

        # Determine file extension
        _, ext = os.path.splitext(image_path)
        if not ext:
            ext = ".jpg"

        filename = f"image_{image_id}{ext}"
        session_image_path = os.path.join(session_images_dir, filename)

        if os.path.exists(image_path):
            shutil.copy2(image_path, session_image_path)
            self.track_file(session_image_path, "image", "Gemini")
            logger.info(f"💾 Saved image {image_id} to session")
            return session_image_path

        return image_path

    def save_final_video(self, video_path: str) -> str:
        """Save final video to session"""
        if not self.current_session:
            return video_path

        session_final_dir = self.get_session_path("final_output")
        # Ensure directory exists
        os.makedirs(session_final_dir, exist_ok=True)
        
        filename = f"final_video_{self.current_session}.mp4"
        session_final_path = os.path.join(session_final_dir, filename)

        if os.path.exists(video_path):
            shutil.copy2(video_path, session_final_path)
            self.track_file(session_final_path, "final_video", "VideoComposer")
            logger.info("💾 Saved final video to session")
            return session_final_path

        return video_path

    def copy_logs_to_session(self):
        """Copy current log files to session"""
        if not self.current_session:
            return

        session_logs_dir = self.get_session_path("logs")

        # Copy main log files
        log_patterns = [
            "logs/*.log",
            "logs/*.txt",
            "*.log",
            "generation.log",
            "error.log",
            "debug.log"
        ]

        copied_count = 0
        for pattern in log_patterns:
            for log_file in glob.glob(pattern):
                if os.path.exists(log_file):
                    filename = os.path.basename(log_file)
                    session_log_path = os.path.join(session_logs_dir, filename)
                    shutil.copy2(log_file, session_log_path)
                    self.track_file(session_log_path, "log", "System")
                    copied_count += 1

        logger.info(f"💾 Copied {copied_count} log files to session")

    def collect_temp_files(self):
        """Collect temporary files that might have been created outside session"""
        if not self.current_session:
            return

        temp_patterns = [
            "/tmp/viral_*",
            "/tmp/veo_*",
            "/tmp/gemini_*",
            "/tmp/tts_*",
            "/var/folders/*/viral_*",
            "temp_*",
            "*.tmp"
        ]

        collected_count = 0
        for pattern in temp_patterns:
            for temp_file in glob.glob(pattern):
                if os.path.exists(temp_file) and os.path.isfile(temp_file):
                    try:
                        # Determine file type from name
                        filename = os.path.basename(temp_file)
                        if any(x in filename for x in ['video', 'mp4', 'veo']):
                            file_type = "video_clip"
                        elif any(x in filename for x in ['audio', 'mp3', 'wav', 'tts']):
                            file_type = "audio"
                        elif any(x in filename for x in ['image', 'jpg', 'png', 'gemini']):
                            file_type = "image"
                        else:
                            file_type = "temp"

                        self.track_file(temp_file, file_type, "TempCollector")
                        collected_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to collect temp file {temp_file}: {e}")

        if collected_count > 0:
            logger.info(f"🧹 Collected {collected_count} temporary files to session")

    def finalize_session(self) -> str:
        """Finalize session and return summary"""
        if not self.current_session:
            return "No active session"

        # Collect any remaining temp files
        self.collect_temp_files()

        # Copy final logs
        self.copy_logs_to_session()

        # Finalize comprehensive logger if available
        if self.session_data.get("comprehensive_logger"):
            try:
                self.session_data["comprehensive_logger"].finalize_session(
                    success=True,
                    error_message=None
                )
            except Exception as e:
                logger.warning(f"Failed to finalize comprehensive logger: {e}")

        # Create comprehensive session summary
        summary = {
            "session_id": self.current_session,
            "topic": self.session_data["topic"],
            "platform": self.session_data["platform"],
            "duration": self.session_data["duration"],
            "total_ai_decisions": len(self.session_data["ai_decisions"]),
            "total_generation_steps": len(self.session_data["generation_log"]),
            "total_errors": len(self.session_data["errors"]),
            "total_warnings": len(self.session_data["warnings"]),
            "total_files_created": self.session_data["total_files_created"],
            "files_by_type": self.session_data["file_counts"],
            "session_directory": self.session_data["session_dir"],
            "tracked_files": len(self.tracked_files)
        }

        # Save final summary
        summary_file = os.path.join(
            self.get_session_path("metadata"),
            "session_summary.json")
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        # Save detailed file tracking
        tracking_file = os.path.join(
            self.get_session_path("metadata"),
            "file_tracking.json")
        with open(tracking_file, 'w') as f:
            json.dump(self.tracked_files, f, indent=2, default=str)

        logger.info(f"✅ Finalized session: {self.current_session}")
        logger.info(
            f"📊 Summary: {summary['total_ai_decisions']} AI decisions,"
            f"{summary['total_generation_steps']} steps, "
            f"{summary['total_errors']} errors")
        logger.info(
            f"📁 Files created: {summary['total_files_created']} total,"
            f"{summary['tracked_files']} tracked")

        session_dir = self.session_data["session_dir"]
        self.current_session = None
        self.session_data = {}
        self.tracked_files = {}

        return session_dir

    def _save_session_metadata(self):
        """Save session metadata to file"""
        if not self.current_session:
            return

        metadata_file = os.path.join(
            self.get_session_path("metadata"),
            "session_metadata.json")

        # Create serializable session data
        serializable_data = {
            key: value for key, value in self.session_data.items()
            if key != "comprehensive_logger"  # Skip non-serializable objects
        }

        with open(metadata_file, 'w') as f:
            json.dump(serializable_data, f, indent=2, default=str)

    def log_generation_step(
        self,
        step: str,
        status: str,
        details: Dict[str,
        Any] = None):
        """Log generation step to session"""
        if not self.current_session:
            return

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "step": step,
            "status": status,
            "details": details or {}
        }

        self.session_data["generation_log"].append(log_entry)
        self._save_session_metadata()

        logger.info(f"📝 Logged generation step: {step} - {status}")

    def log_error(
        self,
        error_type: str,
        error_message: str,
        details: Dict[str,
        Any] = None):
        """Log error to session"""
        if not self.current_session:
            return

        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "message": error_message,
            "details": details or {}
        }

        self.session_data["errors"].append(error_entry)
        self._save_session_metadata()

        logger.error(f"❌ Logged session error: {error_type} - {error_message}")

    def log_warning(
        self,
        warning_type: str,
        warning_message: str,
        details: Dict[str,
        Any] = None):
        """Log warning to session"""
        if not self.current_session:
            return

        warning_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": warning_type,
            "message": warning_message,
            "details": details or {}
        }

        self.session_data["warnings"].append(warning_entry)
        self._save_session_metadata()

        logger.warning(f"⚠️ Logged session warning: {warning_type} - {warning_message}")

    def get_session_info(self, session_id: str = None) -> Dict[str, Any]:
        """Get information about a session"""
        if session_id is None:
            session_id = self.current_session

        if not session_id:
            raise ValueError("No session ID provided and no active session")

        # If this is the current session, return stored data
        if session_id == self.current_session and self.session_data:
            session_info = {
                "session_id": session_id,
                "topic": self.session_data.get("topic", ""),
                "platform": self.session_data.get("platform", ""),
                "duration": self.session_data.get("duration", 0),
                "category": self.session_data.get("category", ""),
                "session_dir": self.session_data.get("session_dir", ""),
                "total_files": self.session_data.get("total_files_created", 0),
                "generation_steps": self.session_data.get("generation_log", []),
                "ai_decisions": self.session_data.get("ai_decisions", {}),
                "errors": self.session_data.get("errors", []),
                "warnings": self.session_data.get("warnings", []),
                "is_active": True
            }

            # Count files in session
            session_dir = self.session_data.get("session_dir", "")
            if os.path.exists(session_dir):
                total_files = 0
                for root, dirs, files in os.walk(session_dir):
                    total_files += len(files)
                session_info["total_files"] = total_files

            return session_info

        # For non-current sessions, construct from directory
        session_dir = os.path.join(self.base_output_dir, session_id)
        if not os.path.exists(session_dir):
            raise ValueError(f"Session {session_id} not found")

        # Count files in session
        total_files = 0
        for root, dirs, files in os.walk(session_dir):
            total_files += len(files)

        return {
            "session_id": session_id,
            "session_dir": session_dir,
            "total_files": total_files,
            "created_at": session_id.split("_")[-1] if "_" in session_id else "unknown",
            "is_active": False,
            "topic": "Unknown",
            "platform": "Unknown",
            "duration": 0,
            "category": "Unknown",
            "generation_steps": [],
            "ai_decisions": {},
            "errors": [],
            "warnings": []
        }

    def cleanup_session(
        self,
        session_id: str,
        keep_final_output: bool = True) -> bool:
        """Clean up session files"""
        try:
            session_dir = os.path.join(self.base_output_dir, session_id)
            if not os.path.exists(session_dir):
                return False

            if keep_final_output:
                # Keep final_output directory, clean everything else
                final_output_dir = os.path.join(session_dir, "final_output")
                if os.path.exists(final_output_dir):
                    # Move final output to temp location
                    temp_final = os.path.join(self.base_output_dir, f"temp_final_{session_id}")
                    shutil.move(final_output_dir, temp_final)

                    # Remove session directory
                    shutil.rmtree(session_dir)

                    # Recreate session directory with just final output
                    os.makedirs(session_dir, exist_ok=True)
                    shutil.move(temp_final, final_output_dir)
                else:
                    # No final output to keep, just remove everything
                    shutil.rmtree(session_dir)
            else:
                # Remove everything
                shutil.rmtree(session_dir)

            return True
        except Exception as e:
            logger.error(f"Failed to cleanup session {session_id}: {e}")
            return False

# Global session manager instance
session_manager = SessionManager()
