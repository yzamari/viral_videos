"""
Comprehensive Logger for Video Generation
Fixed all f-string syntax errors
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict

from .logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class ScriptLogEntry:
    timestamp: str
    script_type: str
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
    timestamp: str
    audio_type: str
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
    timestamp: str
    prompt_type: str
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
    script_generation_time: float = 0.0
    audio_generation_time: float = 0.0
    video_generation_time: float = 0.0
    discussion_time: float = 0.0
    final_video_size_mb: float = 0.0
    audio_file_size_mb: float = 0.0
    total_clips_generated: int = 0
    successful_veo_clips: int = 0
    fallback_clips: int = 0

class ComprehensiveLogger:
    def __init__(self, session_id: str, session_dir: str):
        self.session_id = session_id
        self.session_dir = session_dir
        self.logs_dir = os.path.join(session_dir, "comprehensive_logs")
        
        os.makedirs(self.logs_dir, exist_ok=True)
        
        self.script_logs: List[ScriptLogEntry] = []
        self.audio_logs: List[AudioLogEntry] = []
        self.prompt_logs: List[PromptLogEntry] = []
        self.discussion_logs: List[AgentDiscussionLogEntry] = []
        self.debug_logs: List[Dict[str, Any]] = []
        
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
        
        logger.info(f"📊 Comprehensive logging initialized for session {session_id}")

    def log_script_generation(self, script_type: str, content: Union[str, dict], 
                             model_used: str, generation_time: float, topic: str, 
                             platform: str, category: str) -> None:
        content_str = json.dumps(content) if isinstance(content, dict) else str(content)
        
        entry = ScriptLogEntry(
            timestamp=datetime.now().isoformat(),
            script_type=script_type,
            content=content_str,
            character_count=len(content_str),
            word_count=len(content_str.split()),
            estimated_duration=len(content_str.split()) / 2.5,
            model_used=model_used,
            generation_time=generation_time,
            topic=topic,
            platform=platform,
            category=category
        )
        
        self.script_logs.append(entry)
        logger.info(f"📝 Script logged: {script_type} ({len(content_str)} chars)")

    def log_audio_generation(self, audio_type: str, file_path: str, file_size_mb: float,
                           duration: float, voice_settings: Dict[str, Any],
                           script_used: str, generation_time: float, success: bool,
                           error_message: Optional[str] = None) -> None:
        entry = AudioLogEntry(
            timestamp=datetime.now().isoformat(),
            audio_type=audio_type,
            file_path=file_path,
            file_size_mb=file_size_mb,
            duration=duration,
            voice_settings=voice_settings,
            script_used=script_used,
            generation_time=generation_time,
            success=success,
            error_message=error_message
        )
        
        self.audio_logs.append(entry)
        status = "✅" if success else "❌"
        logger.info(f"🎵 Audio logged: {audio_type} {status} ({file_size_mb:.1f}MB)")

    def finalize_session(self, success: bool, error_message: Optional[str] = None) -> None:
        self.metrics.end_time = datetime.now().isoformat()
        self.metrics.success = success
        self.metrics.error_message = error_message
        
        # Save all logs
        try:
            with open(os.path.join(self.logs_dir, "script_logs.json"), "w") as f:
                json.dump([asdict(log) for log in self.script_logs], f, indent=2)
            
            with open(os.path.join(self.logs_dir, "audio_logs.json"), "w") as f:
                json.dump([asdict(log) for log in self.audio_logs], f, indent=2)
                
            with open(os.path.join(self.logs_dir, "metrics.json"), "w") as f:
                json.dump(asdict(self.metrics), f, indent=2)
                
            logger.info("📊 Comprehensive logs saved successfully")
        except Exception as e:
            logger.error(f"Failed to save comprehensive logs: {e}")
