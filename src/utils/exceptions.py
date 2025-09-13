"""
Custom exceptions for the Viral Video Generator system
"""
from typing import Optional, Dict, Any
import traceback
from datetime import datetime

class VVGException(Exception):
    """Base exception class for Viral Video Generator"""

    def __init__(self, message: str, error_code: Optional[str] = None,
                 context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self.timestamp = datetime.now()
        self.traceback = traceback.format_exc()

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging"""
        return {
            'error_code': self.error_code,
            'message': self.message,
            'context': self.context,
            'timestamp': self.timestamp.isoformat(),
            'traceback': self.traceback
        }

# API Related Exceptions

class APIException(VVGException):
    """Base exception for API-related errors"""
    pass

class RateLimitError(APIException):
    """Raised when API rate limit is exceeded"""

    def __init__(self, platform: str, retry_after: Optional[int] = None):
        super().__init__(
            f"Rate limit exceeded for {platform}",
            context={'platform': platform, 'retry_after': retry_after}
        )
        self.retry_after = retry_after

class AuthenticationError(APIException):
    """Raised when API authentication fails"""

    def __init__(self, platform: str, details: Optional[str] = None):
        super().__init__(
            f"Authentication failed for {platform}",
            context={'platform': platform, 'details': details}
        )

class QuotaExceededError(APIException):
    """Raised when API quota is exceeded"""

    def __init__(self, platform: str, quota_reset: Optional[datetime] = None):
        super().__init__(
            f"API quota exceeded for {platform}",
            context={'platform': platform, 'quota_reset': quota_reset}
        )

class PlatformUnavailableError(APIException):
    """Raised when platform API is unavailable"""

    def __init__(self, platform: str, status_code: Optional[int] = None):
        super().__init__(
            f"Platform {platform} is currently unavailable",
            context={'platform': platform, 'status_code': status_code}
        )

# Processing Exceptions

class ProcessingError(VVGException):
    """Base exception for processing errors"""
    pass

class AnalysisFailedError(ProcessingError):
    """Raised when video analysis fails"""

    def __init__(self, video_id: str, reason: str):
        super().__init__(
            f"Analysis failed for video {video_id}: {reason}",
            context={'video_id': video_id, 'reason': reason}
        )

class GenerationFailedError(ProcessingError):
    """Raised when video generation fails"""

    def __init__(self, stage: str, reason: str):
        super().__init__(
            f"Video generation failed at {stage}: {reason}",
            context={'stage': stage, 'reason': reason}
        )

class RenderingError(ProcessingError):
    """Raised when video rendering fails"""

    def __init__(self, video_id: str, details: str):
        super().__init__(
            f"Rendering failed for video {video_id}: {details}",
            context={'video_id': video_id, 'details': details}
        )

class InvalidDataError(ProcessingError):
    """Raised when data validation fails"""

    def __init__(self, data_type: str, validation_errors: Dict[str, Any]):
        super().__init__(
            f"Invalid {data_type} data",
            context={'data_type': data_type, 'errors': validation_errors}
        )

# System Exceptions

class SystemError(VVGException):
    """Base exception for system errors"""
    pass

class StorageError(SystemError):
    """Raised when storage operations fail"""

    def __init__(self, operation: str, path: str, reason: str):
        super().__init__(
            f"Storage {operation} failed for {path}: {reason}",
            context={'operation': operation, 'path': path, 'reason': reason}
        )

class NetworkError(SystemError):
    """Raised when network operations fail"""

    def __init__(self, operation: str, details: str):
        super().__init__(
            f"Network error during {operation}: {details}",
            context={'operation': operation, 'details': details}
        )

class ConfigurationError(SystemError):
    """Raised when configuration is invalid"""

    def __init__(self, config_key: str, reason: str):
        super().__init__(
            f"Invalid configuration for {config_key}: {reason}",
            context={'config_key': config_key, 'reason': reason}
        )

class DependencyError(SystemError):
    """Raised when external dependency fails"""

    def __init__(self, dependency: str, reason: str):
        super().__init__(
            f"Dependency {dependency} failed: {reason}",
            context={'dependency': dependency, 'reason': reason}
        )

# Content Exceptions

class ContentError(VVGException):
    """Base exception for content-related errors"""
    pass

class ContentPolicyViolation(ContentError):
    """Raised when content violates platform policy"""

    def __init__(self, platform: str, violation_type: str, content: str):
        super().__init__(
            f"Content violates {platform} policy: {violation_type}",
            context={
                'platform': platform,
                'violation_type': violation_type,
                'content_snippet': content[:100]
            }
        )

class CopyrightViolation(ContentError):
    """Raised when copyright content is detected"""

    def __init__(self, content_type: str, source: Optional[str] = None):
        super().__init__(
            f"Copyright violation detected in {content_type}",
            context={'content_type': content_type, 'source': source}
        )

# OOP Architecture Exceptions (New)

class RepositoryError(VVGException):
    """Exception raised for data access errors in repositories"""
    
    def __init__(self, operation: str, entity: str, reason: str):
        super().__init__(
            f"Repository {operation} failed for {entity}: {reason}",
            context={'operation': operation, 'entity': entity, 'reason': reason}
        )


class VideoGenerationError(VVGException):
    """Exception raised for video generation service errors"""
    
    def __init__(self, stage: str, reason: str, session_id: Optional[str] = None):
        super().__init__(
            f"Video generation failed at {stage}: {reason}",
            context={'stage': stage, 'reason': reason, 'session_id': session_id}
        )


class CampaignError(VVGException):
    """Exception raised for campaign management errors"""
    
    def __init__(self, operation: str, reason: str, campaign_id: Optional[str] = None):
        super().__init__(
            f"Campaign {operation} failed: {reason}",
            context={'operation': operation, 'reason': reason, 'campaign_id': campaign_id}
        )


class ValidationError(VVGException):
    """Exception raised for domain entity validation errors"""
    
    def __init__(self, entity_type: str, field: str, reason: str):
        super().__init__(
            f"Validation failed for {entity_type}.{field}: {reason}",
            context={'entity_type': entity_type, 'field': field, 'reason': reason}
        )


# Retry and Recovery

class RetryableError(VVGException):
    """Base class for errors that can be retried"""

    def __init__(self, message: str, max_retries: int = 3, **kwargs):
        super().__init__(message, **kwargs)
        self.max_retries = max_retries
        self.retry_count = 0

    def can_retry(self) -> bool:
        """Check if operation can be retried"""
        return self.retry_count < self.max_retries

    def increment_retry(self):
        """Increment retry counter"""
        self.retry_count += 1
