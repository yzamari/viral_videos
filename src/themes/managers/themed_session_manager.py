"""
Themed Session Manager
Manages video generation sessions with consistent themes
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import json

from ..models.theme import Theme
from ..managers.theme_manager import ThemeManager
from ...utils.session_manager import SessionManager
from ...utils.session_context import SessionContext
from ...core.decision_framework import DecisionFramework, CoreDecisions
from ...utils.logging_config import get_logger

logger = get_logger(__name__)


class ThemedSessionManager:
    """Manages themed video generation sessions"""
    
    def __init__(self, theme_manager: ThemeManager):
        """
        Initialize themed session manager
        
        Args:
            theme_manager: Theme manager instance
        """
        self.theme_manager = theme_manager
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
    
    def create_themed_session(
        self,
        theme_id: str,
        session_name: Optional[str] = None,
        override_settings: Optional[Dict[str, Any]] = None
    ) -> SessionContext:
        """
        Create a new session with a specific theme
        
        Args:
            theme_id: Theme to use for the session
            session_name: Optional session name
            override_settings: Optional settings to override theme defaults
            
        Returns:
            Session context with theme applied
        """
        # Load theme
        theme = self.theme_manager.load_theme(theme_id)
        if not theme:
            raise ValueError(f"Theme not found: {theme_id}")
        
        # Create session using the singleton session manager
        from ...utils.session_manager import session_manager
        session_name = session_name or f"{theme.name} Session"
        session_id = session_manager.create_session(
            topic=session_name,
            platform="youtube",  # Default, can be overridden
            duration=theme.default_duration or 64,
            category="Entertainment"  # Default, can be overridden
        )
        
        # Create session context
        from ...utils.session_context import create_session_context
        session_context = create_session_context(session_id)
        
        # Apply theme to session
        self._apply_theme_to_session(session_context, theme, override_settings)
        
        # Track active session
        self.active_sessions[session_context.session_id] = {
            "theme_id": theme_id,
            "theme_name": theme.name,
            "created_at": datetime.now(),
            "override_settings": override_settings
        }
        
        logger.info(f"Created themed session: {session_context.session_id} with theme {theme.name}")
        return session_context
    
    def _apply_theme_to_session(
        self,
        session_context: SessionContext,
        theme: Theme,
        override_settings: Optional[Dict[str, Any]] = None
    ):
        """Apply theme settings to session"""
        # Save theme info to session
        theme_info_path = session_context.get_path("theme_info.json", "metadata")
        with open(theme_info_path, 'w') as f:
            json.dump({
                "theme_id": theme.theme_id,
                "theme_name": theme.name,
                "theme_category": theme.category.value,
                "applied_at": datetime.now().isoformat(),
                "override_settings": override_settings
            }, f, indent=2)
        
        # Apply theme to decision framework
        if hasattr(session_context, 'decision_framework'):
            self._apply_theme_to_decisions(
                session_context.decision_framework,
                theme,
                override_settings
            )
    
    def _apply_theme_to_decisions(
        self,
        decision_framework: DecisionFramework,
        theme: Theme,
        override_settings: Optional[Dict[str, Any]] = None
    ):
        """Apply theme settings to decision framework"""
        settings = {}
        
        # Apply theme defaults
        if theme.default_duration:
            settings["duration"] = theme.default_duration
        
        if theme.content_tone:
            settings["tone"] = theme.content_tone
        
        if theme.content_style:
            settings["style"] = theme.content_style
        
        if theme.target_audience:
            settings["target_audience"] = theme.target_audience
        
        if theme.default_aspect_ratio:
            settings["aspect_ratio"] = theme.default_aspect_ratio
        
        # Apply visual style from theme
        if theme.style_reference:
            settings["style_reference_id"] = theme.style_reference.reference_id
        
        # Apply overrides
        if override_settings:
            settings.update(override_settings)
        
        # TODO: Update decision framework with theme settings
        # This would need to be integrated into the decision-making process
        # For now, theme settings are stored in session metadata
    
    def generate_with_theme(
        self,
        theme_id: str,
        mission: str,
        additional_params: Optional[Dict[str, Any]] = None
    ) -> SessionContext:
        """
        Generate video with a specific theme
        
        Args:
            theme_id: Theme to use
            mission: Mission/prompt for the video
            additional_params: Additional generation parameters
            
        Returns:
            Session context with generation results
        """
        # Create themed session
        session_context = self.create_themed_session(theme_id)
        
        # Load theme for access to its properties
        theme = self.theme_manager.load_theme(theme_id)
        
        # Prepare generation parameters
        params = {
            "mission": mission,
            "duration": theme.default_duration or 64,
            "style": theme.content_style,
            "tone": theme.content_tone,
            "target_audience": theme.target_audience
        }
        
        # Add theme-specific elements
        if theme.intro_template:
            params["use_intro"] = True
            params["intro_duration"] = theme.intro_template.duration
        
        if theme.outro_template:
            params["use_outro"] = True
            params["outro_duration"] = theme.outro_template.duration
        
        if theme.logo_config:
            params["show_logo"] = True
            params["logo_path"] = theme.logo_config.logo_path
        
        if theme.lower_thirds_style and theme.lower_thirds_style.enabled:
            params["use_lower_thirds"] = True
        
        # Apply additional parameters
        if additional_params:
            params.update(additional_params)
        
        # TODO: Integrate with actual video generation pipeline
        # This would call the working orchestrator with theme-aware parameters
        
        logger.info(f"Generating video with theme {theme.name} for mission: {mission}")
        
        return session_context
    
    def create_series_session(
        self,
        theme_id: str,
        series_name: str,
        episode_count: int
    ) -> List[SessionContext]:
        """
        Create a series of sessions with consistent theme
        
        Args:
            theme_id: Theme to use for all episodes
            series_name: Name of the series
            episode_count: Number of episodes to create
            
        Returns:
            List of session contexts for each episode
        """
        sessions = []
        
        for i in range(1, episode_count + 1):
            session_name = f"{series_name} - Episode {i}"
            session_context = self.create_themed_session(
                theme_id,
                session_name=session_name
            )
            
            # Save series metadata
            series_info_path = session_context.get_path("series_info.json", "metadata")
            with open(series_info_path, 'w') as f:
                json.dump({
                    "series_name": series_name,
                    "episode_number": i,
                    "total_episodes": episode_count,
                    "theme_id": theme_id
                }, f, indent=2)
            
            sessions.append(session_context)
        
        logger.info(f"Created series '{series_name}' with {episode_count} episodes using theme {theme_id}")
        return sessions
    
    def get_session_theme(self, session_id: str) -> Optional[Theme]:
        """
        Get the theme used in a session
        
        Args:
            session_id: Session ID
            
        Returns:
            Theme object or None
        """
        if session_id in self.active_sessions:
            theme_id = self.active_sessions[session_id]["theme_id"]
            return self.theme_manager.load_theme(theme_id)
        
        # Try to load from session metadata
        from ...utils.session_context import create_session_context
        try:
            session_context = create_session_context(session_id)
            theme_info_path = session_context.get_path("theme_info.json", "metadata")
            if Path(theme_info_path).exists():
                with open(theme_info_path, 'r') as f:
                    theme_info = json.load(f)
                    return self.theme_manager.load_theme(theme_info["theme_id"])
        except Exception as e:
            logger.warning(f"Could not load theme for session {session_id}: {e}")
        
        return None
    
    def apply_theme_to_existing_session(
        self,
        session_id: str,
        theme_id: str,
        preserve_content: bool = True
    ) -> bool:
        """
        Apply a theme to an existing session
        
        Args:
            session_id: Session to update
            theme_id: Theme to apply
            preserve_content: Whether to preserve existing content
            
        Returns:
            True if successful
        """
        # Get session
        from ...utils.session_context import create_session_context
        try:
            session_context = create_session_context(session_id)
        except Exception as e:
            logger.error(f"Session not found: {session_id} - {e}")
            return False
        
        # Load theme
        theme = self.theme_manager.load_theme(theme_id)
        if not theme:
            logger.error(f"Theme not found: {theme_id}")
            return False
        
        # Apply theme
        override_settings = {"preserve_content": preserve_content} if preserve_content else None
        self._apply_theme_to_session(session_context, theme, override_settings)
        
        # Update tracking
        self.active_sessions[session_id] = {
            "theme_id": theme_id,
            "theme_name": theme.name,
            "updated_at": datetime.now(),
            "preserve_content": preserve_content
        }
        
        logger.info(f"Applied theme {theme.name} to session {session_id}")
        return True
    
    def list_themed_sessions(
        self,
        theme_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        List sessions using themes
        
        Args:
            theme_id: Filter by specific theme
            limit: Maximum number of results
            
        Returns:
            List of session information
        """
        sessions = []
        
        # Get all sessions from outputs directory
        # Since the session manager doesn't have a list_sessions method,
        # we'll scan the outputs directory
        from pathlib import Path
        outputs_dir = Path("outputs")
        all_sessions = []
        
        if outputs_dir.exists():
            for session_dir in outputs_dir.glob("session_*"):
                if session_dir.is_dir():
                    session_id = session_dir.name
                    all_sessions.append({
                        "session_id": session_id,
                        "name": session_id,
                        "created_at": datetime.fromtimestamp(session_dir.stat().st_ctime).isoformat()
                    })
        
        # Apply limit
        if limit:
            all_sessions = all_sessions[:limit]
        
        for session_info in all_sessions:
            session_id = session_info["session_id"]
            
            # Check if session has theme
            session_theme = self.get_session_theme(session_id)
            if session_theme:
                if theme_id and session_theme.theme_id != theme_id:
                    continue
                
                sessions.append({
                    "session_id": session_id,
                    "session_name": session_info["name"],
                    "theme_id": session_theme.theme_id,
                    "theme_name": session_theme.name,
                    "created_at": session_info["created_at"],
                    "status": session_info.get("status", "unknown")
                })
        
        return sessions
    
    def get_theme_usage_stats(self) -> Dict[str, Any]:
        """Get statistics on theme usage"""
        stats = {
            "total_themed_sessions": 0,
            "theme_usage": {},
            "most_popular_theme": None,
            "category_distribution": {}
        }
        
        # Count theme usage
        themed_sessions = self.list_themed_sessions()
        stats["total_themed_sessions"] = len(themed_sessions)
        
        for session in themed_sessions:
            theme_id = session["theme_id"]
            theme_name = session["theme_name"]
            
            if theme_id not in stats["theme_usage"]:
                stats["theme_usage"][theme_id] = {
                    "name": theme_name,
                    "count": 0
                }
            stats["theme_usage"][theme_id]["count"] += 1
        
        # Find most popular
        if stats["theme_usage"]:
            most_popular = max(
                stats["theme_usage"].items(),
                key=lambda x: x[1]["count"]
            )
            stats["most_popular_theme"] = {
                "theme_id": most_popular[0],
                "name": most_popular[1]["name"],
                "usage_count": most_popular[1]["count"]
            }
        
        # Category distribution
        for theme_id in stats["theme_usage"]:
            theme = self.theme_manager.load_theme(theme_id)
            if theme:
                category = theme.category.value
                stats["category_distribution"][category] = \
                    stats["category_distribution"].get(category, 0) + \
                    stats["theme_usage"][theme_id]["count"]
        
        return stats