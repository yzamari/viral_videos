"""
Centralized Session Manager
Ensures all sessions follow consistent naming: session_TIMESTAMP_UID
"""

import os
import uuid
from datetime import datetime
from typing import Optional
from .logging_config import get_logger

logger = get_logger(__name__)

class SessionManager:
    """Centralized session management with consistent naming"""
    
    OUTPUTS_DIR = "outputs"
    SESSION_PREFIX = "session_"
    
    @staticmethod
    def create_session_id() -> str:
        """Create a standardized session ID: TIMESTAMP_UID"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        uid = str(uuid.uuid4())[:8]
        return f"{timestamp}_{uid}"
    
    @staticmethod
    def create_session_folder(session_id: Optional[str] = None) -> str:
        """
        Create a session folder with standardized naming
        
        Args:
            session_id: Optional session ID, if None will generate new one
            
        Returns:
            Full session folder path
        """
        if session_id is None:
            session_id = SessionManager.create_session_id()
        
        # Ensure session_id follows the correct format
        if not session_id.startswith(SessionManager.SESSION_PREFIX):
            session_folder_name = f"{SessionManager.SESSION_PREFIX}{session_id}"
        else:
            session_folder_name = session_id
        
        session_path = os.path.join(SessionManager.OUTPUTS_DIR, session_folder_name)
        os.makedirs(session_path, exist_ok=True)
        
        logger.info(f"📁 Created session folder: {session_folder_name}")
        return session_path
    
    @staticmethod
    def get_session_path(session_id: str) -> str:
        """Get the full path for a session folder"""
        if not session_id.startswith(SessionManager.SESSION_PREFIX):
            session_folder_name = f"{SessionManager.SESSION_PREFIX}{session_id}"
        else:
            session_folder_name = session_id
        
        return os.path.join(SessionManager.OUTPUTS_DIR, session_folder_name)
    
    @staticmethod
    def find_most_recent_session() -> Optional[str]:
        """Find the most recent session folder"""
        if not os.path.exists(SessionManager.OUTPUTS_DIR):
            return None
        
        session_folders = []
        for item in os.listdir(SessionManager.OUTPUTS_DIR):
            if item.startswith(SessionManager.SESSION_PREFIX):
                item_path = os.path.join(SessionManager.OUTPUTS_DIR, item)
                if os.path.isdir(item_path):
                    session_folders.append((item_path, os.path.getctime(item_path)))
        
        if session_folders:
            session_folders.sort(key=lambda x: x[1], reverse=True)
            return session_folders[0][0]
        
        return None
    
    @staticmethod
    def list_all_sessions() -> list:
        """List all session folders"""
        if not os.path.exists(SessionManager.OUTPUTS_DIR):
            return []
        
        sessions = []
        for item in os.listdir(SessionManager.OUTPUTS_DIR):
            if item.startswith(SessionManager.SESSION_PREFIX):
                item_path = os.path.join(SessionManager.OUTPUTS_DIR, item)
                if os.path.isdir(item_path):
                    sessions.append({
                        'name': item,
                        'path': item_path,
                        'created': os.path.getctime(item_path)
                    })
        
        # Sort by creation time (newest first)
        sessions.sort(key=lambda x: x['created'], reverse=True)
        return sessions
    
    @staticmethod
    def cleanup_inconsistent_folders():
        """Clean up folders that don't follow the naming convention"""
        if not os.path.exists(SessionManager.OUTPUTS_DIR):
            return
        
        inconsistent_folders = []
        for item in os.listdir(SessionManager.OUTPUTS_DIR):
            item_path = os.path.join(SessionManager.OUTPUTS_DIR, item)
            if os.path.isdir(item_path):
                # Check if it's an inconsistent session folder
                if (not item.startswith(SessionManager.SESSION_PREFIX) and 
                    ('session' in item.lower() or len(item) == 8 or '_' in item)):
                    inconsistent_folders.append((item, item_path))
        
        logger.info(f"🧹 Found {len(inconsistent_folders)} inconsistent folders to clean up")
        
        for folder_name, folder_path in inconsistent_folders:
            # Try to determine if this is a session folder and rename it
            if len(folder_name) == 8:  # Probably a UID-only folder
                # Check if there's a corresponding session_ folder
                session_folder = f"{SessionManager.SESSION_PREFIX}{folder_name}"
                session_path = os.path.join(SessionManager.OUTPUTS_DIR, session_folder)
                
                if not os.path.exists(session_path):
                    # Rename the folder
                    try:
                        os.rename(folder_path, session_path)
                        logger.info(f"📝 Renamed: {folder_name} → {session_folder}")
                    except Exception as e:
                        logger.warning(f"⚠️ Could not rename {folder_name}: {e}")
                else:
                    logger.warning(f"⚠️ Duplicate found, manual cleanup needed: {folder_name}")
            
            elif folder_name.startswith('orchestrated_session_'):
                # Rename orchestrated sessions to standard format
                timestamp_uid = folder_name.replace('orchestrated_session_', '')
                new_name = f"{SessionManager.SESSION_PREFIX}{timestamp_uid}"
                new_path = os.path.join(SessionManager.OUTPUTS_DIR, new_name)
                
                if not os.path.exists(new_path):
                    try:
                        os.rename(folder_path, new_path)
                        logger.info(f"📝 Renamed: {folder_name} → {new_name}")
                    except Exception as e:
                        logger.warning(f"⚠️ Could not rename {folder_name}: {e}")
            
            elif folder_name.startswith('topic_session_'):
                # Rename topic sessions to standard format
                timestamp_uid = folder_name.replace('topic_session_', '')
                new_name = f"{SessionManager.SESSION_PREFIX}{timestamp_uid}"
                new_path = os.path.join(SessionManager.OUTPUTS_DIR, new_name)
                
                if not os.path.exists(new_path):
                    try:
                        os.rename(folder_path, new_path)
                        logger.info(f"📝 Renamed: {folder_name} → {new_name}")
                    except Exception as e:
                        logger.warning(f"⚠️ Could not rename {folder_name}: {e}") 