#!/usr/bin/env python3
"""
Comprehensive Logging System for Viral Video Generator

This system captures and logs all important data:
- Scripts (original, cleaned, TTS-ready)
- Audio generation details and settings
- VEO-2/VEO-3 prompts and responses
- AI agent discussions and decisions
- Generation metrics and performance
- Error handling and debugging info
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict

from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ScriptLogEntry:
    """Log entry for script generation"""
    timestamp: str
    script_type: str  # 'original', 'cleaned', 'tts_ready'
    content: str
    character_count: int
    word_count: int
    estimated_duration: float
    model_used: str
    generation_time: float
    topic: str
    platform: str
    category: str


@dataclass
class AudioLogEntry:
    """Log entry for audio generation"""
    timestamp: str
    audio_type: str  # 'tts', 'google_cloud_tts', 'gtts'
    file_path: str
    file_size_mb: float
    duration: float
    voice_settings: Dict[str, Any]
    script_used: str
    generation_time: float
    success: bool
    error_message: Optional[str] = None


@dataclass
class PromptLogEntry:
    """Log entry for VEO-2/VEO-3 prompts"""
    timestamp: str
    prompt_type: str  # 'veo2', 'veo3', 'image_generation'
    original_prompt: str
    enhanced_prompt: str
    model_used: str
    duration: float
    aspect_ratio: str
    generation_success: bool
    output_path: Optional[str] = None
    file_size_mb: Optional[float] = None
    generation_time: Optional[float] = None
    error_message: Optional[str] = None


@dataclass
class AgentDiscussionLogEntry:
    """Log entry for AI agent discussions"""
    timestamp: str
    discussion_id: str
    topic: str
    participating_agents: List[str]
    total_rounds: int
    consensus_level: float
    duration: float
    key_decisions: Dict[str, Any]
    key_insights: List[str]
    success: bool


@dataclass
class GenerationMetrics:
    """Overall generation metrics"""
    session_id: str
    start_time: str
    end_time: str
    total_duration: float
    topic: str
    platform: str
    category: str
    target_duration: int
    actual_duration: float
    success: bool
    error_message: Optional[str] = None

    # Component metrics
    script_generation_time: float = 0.0
    audio_generation_time: float = 0.0
    video_generation_time: float = 0.0
    discussion_time: float = 0.0

    # File metrics
    final_video_size_mb: float = 0.0
    audio_file_size_mb: float = 0.0
    total_clips_generated: int = 0
    successful_veo_clips: int = 0
    fallback_clips: int = 0


class ComprehensiveLogger:
    """
    Comprehensive logging system for all video generation components
    """

    def __init__(self, session_id: str, session_dir: str):
        self.session_id = session_id
        self.session_dir = session_dir
        self.logs_dir = os.path.join(session_dir, "comprehensive_logs")

        # Create logs directory
        os.makedirs(self.logs_dir, exist_ok=True)

        # Initialize log files
        self.script_log_file = os.path.join(self.logs_dir, "script_generation.json")
        self.audio_log_file = os.path.join(self.logs_dir, "audio_generation.json")
        self.prompt_log_file = os.path.join(self.logs_dir, "prompt_generation.json")
        self.discussion_log_file = os.path.join(self.logs_dir, "agent_discussions.json")
        self.metrics_log_file = os.path.join(self.logs_dir, "generation_metrics.json")
        self.debug_log_file = os.path.join(self.logs_dir, "debug_info.json")

        # Initialize log storage
        self.script_logs: List[ScriptLogEntry] = []
        self.audio_logs: List[AudioLogEntry] = []
        self.prompt_logs: List[PromptLogEntry] = []
        self.discussion_logs: List[AgentDiscussionLogEntry] = []
        self.debug_logs: List[Dict[str, Any]] = []

        # Generation metrics
        self.metrics = GenerationMetrics(
            session_id=session_id,
            start_time=datetime.now().isoformat(),
            end_time="",
            total_duration=0.0,
            topic="",
            platform="",
            category="",
            target_duration=0,
            actual_duration=0.0,
            success=False
        )

        # ENHANCED: Integrate with session manager for file tracking
        try:
            from .session_manager import session_manager
            self.session_manager = session_manager
            
            # Track all log files with session manager
            if self.session_manager.current_session:
                for log_file in [self.script_log_file, self.audio_log_file, self.prompt_log_file,
                               self.discussion_log_file, self.metrics_log_file, self.debug_log_file]:
                    # Pre-track log files (they'll be created later)
                    self.session_manager.track_file(log_file, "comprehensive_log", "ComprehensiveLogger")
                    
                logger.info(f"📊 Comprehensive logging integrated with session manager")
        except Exception as e:
            logger.warning(f"Failed to integrate with session manager: {e}")
            self.session_manager = None

        logger.info(f"📊 Comprehensive logging initialized for session {session_id}")
        logger.info(f"📁 Logs directory: {self.logs_dir}")

    def log_script_generation(self, script_type: str, content: Union[str, dict], model_used: str,
                              generation_time: float, topic: str, platform: str,
                              category: str) -> None:
        """Log script generation details"""
        # Handle both string and dictionary content
        if isinstance(content, dict):
            content_str = json.dumps(content, indent=2)
            word_count = len(content_str.split())
        else:
            content_str = str(content)
            word_count = len(content_str.split())

        entry = ScriptLogEntry(
            timestamp=datetime.now().isoformat(),
            script_type=script_type,
            content=content_str,
            character_count=len(content_str),
            word_count=word_count,
            estimated_duration=word_count * 0.5,  # Rough estimate
            model_used=model_used,
            generation_time=generation_time,
            topic=topic,
            platform=platform,
            category=category
        )

        self.script_logs.append(entry)
        self._save_script_logs()

        logger.info(f"📝 Script logged: {script_type} ({len(content_str)} chars, {generation_time:.2f}s)")

    def log_audio_generation(self, audio_type: str, file_path: str, file_size_mb: float,
                             duration: float, voice_settings: Dict[str, Any],
                             script_used: str, generation_time: float, success: bool,
                             error_message: Optional[str] = None) -> None:
        """Log audio generation details"""
        entry = AudioLogEntry(
            timestamp=datetime.now().isoformat(),
            audio_type=audio_type,
            file_path=file_path,
            file_size_mb=file_size_mb,
            duration=duration,
            voice_settings=voice_settings,
            script_used=script_used[:500] + "..." if len(script_used) > 500 else script_used,
            generation_time=generation_time,
            success=success,
            error_message=error_message
        )

        self.audio_logs.append(entry)
        self._save_audio_logs()

        status = "✅" if success else "❌"
        logger.info(f"🎵 Audio logged: {audio_type} {status} ({file_size_mb:.1f}MB, {duration:.1f}s)")

    def log_prompt_generation(self, prompt_type: str, original_prompt: str,
                              enhanced_prompt: str, model_used: str, duration: float,
                              aspect_ratio: str, generation_success: bool,
                              output_path: Optional[str] = None,
                              file_size_mb: Optional[float] = None,
                              generation_time: Optional[float] = None,
                              error_message: Optional[str] = None) -> None:
        """Log prompt generation and VEO-2/VEO-3 details"""
        entry = PromptLogEntry(
            timestamp=datetime.now().isoformat(),
            prompt_type=prompt_type,
            original_prompt=original_prompt,
            enhanced_prompt=enhanced_prompt,
            model_used=model_used,
            duration=duration,
            aspect_ratio=aspect_ratio,
            generation_success=generation_success,
            output_path=output_path,
            file_size_mb=file_size_mb,
            generation_time=generation_time,
            error_message=error_message
        )

        self.prompt_logs.append(entry)
        self._save_prompt_logs()

        status = "✅" if generation_success else "❌"
        logger.info(f"🎬 Prompt logged: {prompt_type} {status} ({duration:.1f}s)")

    def log_agent_discussion(self, discussion_id: str, topic: str,
                             participating_agents: List[str], total_rounds: int,
                             consensus_level: float, duration: float,
                             key_decisions: Dict[str, Any], key_insights: List[str],
                             success: bool) -> None:
        """Log AI agent discussion details"""
        entry = AgentDiscussionLogEntry(
            timestamp=datetime.now().isoformat(),
            discussion_id=discussion_id,
            topic=topic,
            participating_agents=participating_agents,
            total_rounds=total_rounds,
            consensus_level=consensus_level,
            duration=duration,
            key_decisions=key_decisions,
            key_insights=key_insights,
            success=success
        )

        self.discussion_logs.append(entry)
        self._save_discussion_logs()

        logger.info(f"🤖 Discussion logged: {topic} ({consensus_level:.1%} consensus, {duration:.1f}s)")

    def log_debug_info(self, component: str, level: str, message: str,
                       data: Optional[Dict[str, Any]] = None) -> None:
        """Log debug information"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "level": level,
            "message": message,
            "data": data or {}
        }

        self.debug_logs.append(entry)
        self._save_debug_logs()

        # Keep only last 100 debug entries to prevent huge files
        if len(self.debug_logs) > 100:
            self.debug_logs = self.debug_logs[-100:]

    def update_metrics(self, **kwargs) -> None:
        """Update generation metrics"""
        for key, value in kwargs.items():
            if hasattr(self.metrics, key):
                setattr(self.metrics, key, value)

        self._save_metrics()

    def finalize_session(self, success: bool, error_message: Optional[str] = None) -> None:
        """Finalize the session logging"""
        self.metrics.end_time = datetime.now().isoformat()
        start_time = datetime.fromisoformat(self.metrics.start_time)
        end_time = datetime.fromisoformat(self.metrics.end_time)
        self.metrics.total_duration = (end_time - start_time).total_seconds()
        self.metrics.success = success
        self.metrics.error_message = error_message

        self._save_metrics()
        self._create_session_summary()

        status = "✅ SUCCESS" if success else "❌ FAILED"
        logger.info(f"📊 Session finalized: {status} ({self.metrics.total_duration:.1f}s)")

    def _save_script_logs(self) -> None:
        """Save script logs to file"""
        try:
            with open(self.script_log_file, 'w') as f:
                json.dump([asdict(entry) for entry in self.script_logs], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save script logs: {e}")

    def _save_audio_logs(self) -> None:
        """Save audio logs to file"""
        try:
            with open(self.audio_log_file, 'w') as f:
                json.dump([asdict(entry) for entry in self.audio_logs], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save audio logs: {e}")

    def _save_prompt_logs(self) -> None:
        """Save prompt logs to file"""
        try:
            with open(self.prompt_log_file, 'w') as f:
                json.dump([asdict(entry) for entry in self.prompt_logs], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save prompt logs: {e}")

    def _save_discussion_logs(self) -> None:
        """Save discussion logs to file"""
        try:
            with open(self.discussion_log_file, 'w') as f:
                json.dump([asdict(entry) for entry in self.discussion_logs], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save discussion logs: {e}")

    def _save_debug_logs(self) -> None:
        """Save debug logs to file"""
        try:
            with open(self.debug_log_file, 'w') as f:
                json.dump(self.debug_logs, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save debug logs: {e}")

    def _save_metrics(self) -> None:
        """Save generation metrics to file"""
        try:
            with open(self.metrics_log_file, 'w') as f:
                json.dump(asdict(self.metrics), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")

    def _create_session_summary(self) -> None:
        """Create a comprehensive session summary"""
        summary_file = os.path.join(self.logs_dir, "session_summary.md")

        try:
            with open(summary_file, 'w') as f:
                f.write(f"# Session Summary: {self.session_id}\n\n")
                f.write(f"**Generated:** {self.metrics.start_time}\n")
                f.write(f"**Duration:** {self.metrics.total_duration:.1f} seconds\n")
                f.write(f"**Status:** {'✅ SUCCESS' if self.metrics.success else '❌ FAILED'}\n")
                f.write(f"**Topic:** {self.metrics.topic}\n")
                f.write(f"**Platform:** {self.metrics.platform}\n")
                f.write(f"**Category:** {self.metrics.category}\n\n")

                # Script Generation Summary
                f.write("## 📝 Script Generation\n\n")
                f.write(f"**Scripts Generated:** {len(self.script_logs)}\n")
                if self.script_logs:
                    f.write(f"**Total Generation Time:** {sum(log.generation_time for log in self.script_logs):.1f}s\n")
                    f.write(f"**Models Used:** {', '.join(set(log.model_used for log in self.script_logs))}\n")
                    f.write(f"**Total Characters:** {sum(log.character_count for log in self.script_logs):,}\n")
                f.write("\n")

                # Audio Generation Summary
                f.write("## 🎵 Audio Generation\n\n")
                f.write(f"**Audio Files Generated:** {len(self.audio_logs)}\n")
                if self.audio_logs:
                    successful_audio = [log for log in self.audio_logs if log.success]
                    f.write(f"**Successful:** {len(successful_audio)}/{len(self.audio_logs)}\n")
                    f.write(f"**Total Audio Duration:** {sum(log.duration for log in successful_audio):.1f}s\n")
                    f.write(f"**Total File Size:** {sum(log.file_size_mb for log in successful_audio):.1f}MB\n")
                    f.write(f"**Audio Types:** {', '.join(set(log.audio_type for log in self.audio_logs))}\n")
                f.write("\n")

                # Prompt Generation Summary
                f.write("## 🎬 Video Generation\n\n")
                f.write(f"**Prompts Generated:** {len(self.prompt_logs)}\n")
                if self.prompt_logs:
                    successful_prompts = [log for log in self.prompt_logs if log.generation_success]
                    f.write(f"**Successful:** {len(successful_prompts)}/{len(self.prompt_logs)}\n")
                    f.write(f"**Models Used:** {', '.join(set(log.model_used for log in self.prompt_logs))}\n")
                    f.write(f"**Total Video Duration:** {sum(log.duration for log in successful_prompts):.1f}s\n")
                    if successful_prompts:
                        total_size = sum(log.file_size_mb for log in successful_prompts if log.file_size_mb)
                        f.write(f"**Total Video Size:** {total_size:.1f}MB\n")
                f.write("\n")

                # Agent Discussions Summary
                f.write("## 🤖 AI Agent Discussions\n\n")
                f.write(f"**Discussions Conducted:** {len(self.discussion_logs)}\n")
                if self.discussion_logs:
                    avg_consensus = sum(log.consensus_level for log in self.discussion_logs) / len(self.discussion_logs)
                    total_discussion_time = sum(log.duration for log in self.discussion_logs)
                    f.write(f"**Average Consensus:** {avg_consensus:.1%}\n")
                    f.write(f"**Total Discussion Time:** {total_discussion_time:.1f}s\n")
                    f.write(
                        f"**Total Agents Involved:** {len(set(agent for log in self.discussion_logs for agent in log.participating_agents))}\n")
                f.write("\n")

                # Performance Metrics
                f.write("## 📊 Performance Metrics\n\n")
                f.write(f"**Script Generation Time:** {self.metrics.script_generation_time:.1f}s\n")
                f.write(f"**Audio Generation Time:** {self.metrics.audio_generation_time:.1f}s\n")
                f.write(f"**Video Generation Time:** {self.metrics.video_generation_time:.1f}s\n")
                f.write(f"**Discussion Time:** {self.metrics.discussion_time:.1f}s\n")
                f.write(f"**Final Video Size:** {self.metrics.final_video_size_mb:.1f}MB\n")
                f.write(f"**Successful VEO Clips:** {self.metrics.successful_veo_clips}\n")
                f.write(f"**Fallback Clips:** {self.metrics.fallback_clips}\n")

                if self.metrics.error_message:
                    f.write(f"\n## ❌ Error Information\n\n")
                    f.write(f"**Error:** {self.metrics.error_message}\n")

            logger.info(f"📄 Session summary created: {summary_file}")

        except Exception as e:
            logger.error(f"Failed to create session summary: {e}")

    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics"""
        return {
            "session_id": self.session_id,
            "scripts_generated": len(self.script_logs),
            "audio_files_generated": len(self.audio_logs),
            "prompts_generated": len(self.prompt_logs),
            "discussions_conducted": len(self.discussion_logs),
            "debug_entries": len(self.debug_logs),
            "session_duration": self.metrics.total_duration,
            "success": self.metrics.success
        }

