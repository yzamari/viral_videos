"""
Session Manager - Comprehensive session organization system
Creates dedicated folders for each session with all logs, data, AI agent outputs, and generated content
"""

import os
import json
import shutil
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from .logging_config import get_logger

logger = get_logger(__name__)


class SessionManager:
    """Manages session organization and data storage"""
    
    def __init__(self, base_output_dir: str = "outputs"):
        self.base_output_dir = base_output_dir
        self.current_session = None
        self.session_data = {}
        
    def create_session(self, topic: str, platform: str, duration: int, category: str) -> str:
        """Create a new session with organized folder structure"""
        
        # Generate session ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"session_{timestamp}"
        
        # Create session directory structure
        session_dir = os.path.join(self.base_output_dir, session_id)
        
        # Create all subdirectories
        subdirs = [
            "logs",           # All log files
            "scripts",        # Generated scripts and text
            "audio",          # TTS audio files
            "video_clips",    # Individual video clips
            "images",         # Generated images
            "ai_agents",      # AI agent decisions and logs
            "discussions",    # Agent discussions
            "final_output",   # Final composed video
            "metadata"        # Session metadata and configs
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
            "warnings": []
        }
        
        # Save session metadata
        self._save_session_metadata()
        
        logger.info(f"📁 Created session: {session_id}")
        logger.info(f"📂 Session directory: {session_dir}")
        
        return session_id
    
    def get_session_path(self, subdir: str = None) -> str:
        """Get path for session or specific subdirectory"""
        if not self.current_session:
            raise ValueError("No active session")
        
        if subdir:
            return self.session_data["subdirs"][subdir]
        return self.session_data["session_dir"]
    
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
        agent_file = os.path.join(self.get_session_path("ai_agents"), f"{agent_name}_decision.json")
        with open(agent_file, 'w') as f:
            json.dump(decision_entry, f, indent=2)
        
        logger.info(f"💾 Logged {agent_name} decision to session")
    
    def log_generation_step(self, step: str, status: str, details: Dict[str, Any] = None):
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
    
    def log_error(self, error_type: str, error_message: str, details: Dict[str, Any] = None):
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
    
    def log_warning(self, warning_type: str, warning_message: str, details: Dict[str, Any] = None):
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
    
    def save_script(self, script_content: str, script_type: str = "main") -> str:
        """Save script to session"""
        if not self.current_session:
            return None
        
        script_file = os.path.join(self.get_session_path("scripts"), f"{script_type}_script.json")
        
        script_data = {
            "timestamp": datetime.now().isoformat(),
            "type": script_type,
            "content": script_content
        }
        
        with open(script_file, 'w') as f:
            json.dump(script_data, f, indent=2)
        
        logger.info(f"💾 Saved {script_type} script to session")
        return script_file
    
    def save_audio(self, audio_path: str, clip_id: str) -> str:
        """Save audio file to session"""
        if not self.current_session:
            return audio_path
        
        session_audio_dir = self.get_session_path("audio")
        filename = f"audio_clip_{clip_id}.wav"
        session_audio_path = os.path.join(session_audio_dir, filename)
        
        if os.path.exists(audio_path):
            shutil.copy2(audio_path, session_audio_path)
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
            logger.info(f"💾 Saved video clip {clip_id} to session")
            return session_video_path
        
        return video_path
    
    def save_final_video(self, video_path: str) -> str:
        """Save final video to session"""
        if not self.current_session:
            return video_path
        
        session_final_dir = self.get_session_path("final_output")
        filename = f"final_video_{self.current_session}.mp4"
        session_final_path = os.path.join(session_final_dir, filename)
        
        if os.path.exists(video_path):
            shutil.copy2(video_path, session_final_path)
            logger.info(f"💾 Saved final video to session")
            return session_final_path
        
        return video_path
    
    def copy_logs_to_session(self):
        """Copy current log files to session"""
        if not self.current_session:
            return
        
        session_logs_dir = self.get_session_path("logs")
        
        # Copy main log files
        log_files = ["logs/app.log", "logs/generation.log", "logs/errors.log"]
        
        for log_file in log_files:
            if os.path.exists(log_file):
                filename = os.path.basename(log_file)
                session_log_path = os.path.join(session_logs_dir, filename)
                shutil.copy2(log_file, session_log_path)
        
        logger.info("💾 Copied logs to session")
    
    def _save_session_metadata(self):
        """Save session metadata to file"""
        if not self.current_session:
            return
        
        metadata_file = os.path.join(self.get_session_path("metadata"), "session_metadata.json")
        
        with open(metadata_file, 'w') as f:
            json.dump(self.session_data, f, indent=2)
    
    def finalize_session(self) -> str:
        """Finalize session and return summary"""
        if not self.current_session:
            return "No active session"
        
        # Copy final logs
        self.copy_logs_to_session()
        
        # Create session summary
        summary = {
            "session_id": self.current_session,
            "topic": self.session_data["topic"],
            "platform": self.session_data["platform"],
            "duration": self.session_data["duration"],
            "total_ai_decisions": len(self.session_data["ai_decisions"]),
            "total_generation_steps": len(self.session_data["generation_log"]),
            "total_errors": len(self.session_data["errors"]),
            "total_warnings": len(self.session_data["warnings"]),
            "session_directory": self.session_data["session_dir"]
        }
        
        # Save final summary
        summary_file = os.path.join(self.get_session_path("metadata"), "session_summary.json")
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"✅ Finalized session: {self.current_session}")
        logger.info(f"📊 Summary: {summary['total_ai_decisions']} AI decisions, {summary['total_generation_steps']} steps, {summary['total_errors']} errors")
        
        session_dir = self.session_data["session_dir"]
        self.current_session = None
        self.session_data = {}
        
        return session_dir


# Global session manager instance
session_manager = SessionManager()

