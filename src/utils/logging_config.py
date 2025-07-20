"""
Logging configuration for the viral video generator
Enhanced with session-aware logging and comprehensive file tracking
"""
import logging
import colorlog
from datetime import datetime
import os

def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance with session-aware logging

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Configure colorlog for console output
    console_handler = colorlog.StreamHandler()
    console_handler.setFormatter(
        colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
    )

    # Configure file handler with session-aware filename
    session_aware_filename = f"viral_video_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(
        os.path.join(log_dir, session_aware_filename)
    )
    file_handler.setFormatter(
        logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    )

    # Create and configure logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Add handlers if not already added
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    # ENHANCED: Track log files with session manager if available
    try:
        from .session_manager import session_manager
        if session_manager.current_session:
            log_file_path = os.path.join(log_dir, session_aware_filename)
            session_manager.track_file(log_file_path, "log", "SystemLogging")
    except (ImportError, AttributeError):
        # Session manager not available or no active session
        pass

    return logger

def setup_session_logging(session_id: str, session_dir: str):
    """
    Set up session-specific logging handlers

    Args:
        session_id: Session identifier
        session_dir: Session directory path
    """
    try:
        # Create session-specific log file
        session_log_dir = os.path.join(session_dir, "logs")
        os.makedirs(session_log_dir, exist_ok=True)

        session_log_file = os.path.join(session_log_dir, f"session_{session_id}.log")

        # Create session-specific handler
        session_handler = logging.FileHandler(session_log_file)
        session_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        )

        # Add to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(session_handler)

        # Track with session manager
        from .session_manager import session_manager
        if session_manager.current_session:
            session_manager.track_file(session_log_file, "log", "SessionLogging")

        return session_log_file

    except Exception as e:
        print(f"Failed to set up session logging: {e}")
        return None
