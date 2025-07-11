import os
import json
from datetime import datetime
from ..utils.session_manager import SessionManager
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class FileService:
    def __init__(self, session_id):
        self.session_id = session_id
        self.session_path = SessionManager.get_session_path(session_id)
        os.makedirs(self.session_path, exist_ok=True)

    @staticmethod
    def create_session_folder():
        """Create session folder using centralized session manager"""
        session_id = SessionManager.create_session_id()
        return f"session_{session_id}"  # Return with prefix for backward compatibility

    def setup_session_directories(self, session_id: str) -> Dict[str, str]:
        """Setup session directories and ensure they contain data"""
        session_dir = SessionManager.get_session_path(session_id)

        # Create main session directory
        os.makedirs(session_dir, exist_ok=True)

        # Define all required subdirectories
        directories = {
            'session_dir': session_dir,
            'audio': os.path.join(session_dir, 'audio'),
            'veo2_clips': os.path.join(session_dir, 'veo2_clips'),
            'comprehensive_logs': os.path.join(session_dir, 'comprehensive_logs'),
            'agent_discussions': os.path.join(session_dir, 'agent_discussions'),
            'scripts': os.path.join(session_dir, 'scripts'),
            'analysis': os.path.join(session_dir, 'analysis')
        }

        # Only create directories that will actually be used
        essential_dirs = ['audio', 'veo2_clips', 'comprehensive_logs', 'agent_discussions', 'scripts']
        for dir_name in essential_dirs:
            os.makedirs(directories[dir_name], exist_ok=True)

            # Create placeholder files to prevent empty directories
            placeholder_file = os.path.join(directories[dir_name], '.gitkeep')
            if not os.path.exists(placeholder_file):
                with open(placeholder_file, 'w') as f:
                    f.write(f"# {dir_name.title()} directory for session {session_id}\n")

        logger.info(f"📁 Session directories setup: session_{session_id}")
        return directories

    def save_session_metadata(self, session_id: str, config: Dict, start_time: datetime) -> str:
        """Save comprehensive session metadata"""
        session_dir = SessionManager.get_session_path(session_id)
        metadata_file = os.path.join(session_dir, 'session_metadata.json')

        metadata = {
            'session_id': session_id,
            'start_time': start_time.isoformat(),
            'config': {
                'topic': config.get('topic', ''),
                'platform': config.get('target_platform', ''),
                'category': config.get('category', ''),
                'duration_seconds': config.get('duration_seconds', 0),
                'style': config.get('style', ''),
                'tone': config.get('tone', '')
            },
            'directories_created': [
                'audio', 'veo2_clips', 'comprehensive_logs',
                'agent_discussions', 'scripts', 'analysis'
            ],
            'expected_outputs': [
                'final_video_*.mp4',
                'tts_script.json',
                'audio/*.mp3',
                'veo2_clips/*.mp4',
                'comprehensive_logs/*.json',
                'agent_discussions/*.md',
                'scripts/*.txt'
            ]
        }

        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        logger.info(f"📄 Session metadata saved: {metadata_file}")
        return metadata_file

    def cleanup_empty_directories(self, session_id: str) -> int:
        """Remove empty directories and log what was cleaned up"""
        session_dir = SessionManager.get_session_path(session_id)
        cleaned_count = 0

        # Walk through all subdirectories
        for root, dirs, files in os.walk(session_dir, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    # Check if directory is empty (only .gitkeep files are okay)
                    contents = os.listdir(dir_path)
                    if not contents or (len(contents) == 1 and contents[0] == '.gitkeep'):
                        # Don't remove essential directories, just log them
                        if dir_name in ['audio', 'veo2_clips', 'comprehensive_logs', 'agent_discussions', 'scripts']:
                            logger.info(f"📁 Keeping essential empty directory: {dir_name}")
                        else:
                            os.rmdir(dir_path)
                            cleaned_count += 1
                            logger.info(f"🗑️ Removed empty directory: {dir_path}")
                except OSError:
                    pass  # Directory not empty or permission issue

        if cleaned_count > 0:
            logger.info(f"🧹 Cleaned up {cleaned_count} empty directories from session {session_id}")

        return cleaned_count

    def save_json(self, filename, data):
        with open(os.path.join(self.session_path, filename), "w") as f:
            json.dump(data, f, indent=4)

    def create_final_video(self, clips: List[str], audio_path: str, 
                          session_id: str, output_dir: str = "outputs") -> str:
        """Create final video from clips and audio"""
        logger.info("🎞️ Creating final video from clips and audio")
        
        try:
            # Create session directory
            session_path = os.path.join(output_dir, f"session_{session_id}")
            os.makedirs(session_path, exist_ok=True)
            
            # For now, create a placeholder video file
            video_path = os.path.join(session_path, "final_video.mp4")
            with open(video_path, "w") as f:
                f.write("video data")
            return video_path
        except Exception as e:
            logger.error(f"Error creating final video: {e}")
            return ""

