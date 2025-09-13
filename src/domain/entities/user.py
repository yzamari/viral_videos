"""
User Entity - Core domain entity for user management with proper OOP encapsulation.

This entity follows SOLID principles and encapsulates all user-related business logic.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
import bcrypt
import re


class UserRole(Enum):
    """User role enumeration with explicit permissions"""
    ADMIN = "admin"
    PREMIUM = "premium"
    BASIC = "basic"
    TRIAL = "trial"
    
    def get_max_sessions(self) -> int:
        """Get maximum concurrent sessions allowed for this role"""
        role_limits = {
            UserRole.ADMIN: -1,  # Unlimited
            UserRole.PREMIUM: 10,
            UserRole.BASIC: 3,
            UserRole.TRIAL: 1
        }
        return role_limits.get(self, 1)
    
    def get_max_monthly_videos(self) -> int:
        """Get maximum monthly video generation limit"""
        role_limits = {
            UserRole.ADMIN: -1,  # Unlimited
            UserRole.PREMIUM: 500,
            UserRole.BASIC: 50,
            UserRole.TRIAL: 5
        }
        return role_limits.get(self, 5)
    
    def can_access_premium_features(self) -> bool:
        """Check if role can access premium features"""
        return self in [UserRole.ADMIN, UserRole.PREMIUM]


class UserStatus(Enum):
    """User account status enumeration"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"
    PENDING_VERIFICATION = "pending_verification"
    TRIAL_EXPIRED = "trial_expired"


@dataclass
class User:
    """
    User domain entity with encapsulated business logic.
    
    Follows Single Responsibility Principle by handling only user-related operations.
    Implements proper encapsulation with validation and business rules.
    """
    
    # Core identity
    id: str
    username: str
    email: str
    _hashed_password: str = field(repr=False)  # Private field for security
    
    # User profile
    organization: Optional[str] = None
    role: UserRole = UserRole.BASIC
    status: UserStatus = UserStatus.ACTIVE
    
    # Account lifecycle
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_login_at: Optional[datetime] = None
    email_verified_at: Optional[datetime] = None
    
    # Trial management
    trial_expires_at: Optional[datetime] = None
    trial_videos_used: int = 0
    
    # Usage tracking
    monthly_videos_used: int = 0
    monthly_reset_date: datetime = field(default_factory=lambda: datetime.now().replace(day=1))
    active_sessions: List[str] = field(default_factory=list)
    
    # Preferences and settings
    preferences: Dict[str, Any] = field(default_factory=dict)
    notification_settings: Dict[str, bool] = field(default_factory=lambda: {
        "email_notifications": True,
        "video_completion_alerts": True,
        "weekly_usage_reports": True
    })
    
    def __post_init__(self):
        """Post-initialization validation and setup"""
        self._validate_core_fields()
        self._setup_trial_if_needed()
    
    def _validate_core_fields(self) -> None:
        """Validate core user fields according to business rules"""
        if not self.id or not self.id.strip():
            raise ValueError("User ID cannot be empty")
            
        if not self.username or not self.username.strip():
            raise ValueError("Username cannot be empty")
            
        if len(self.username) < 3 or len(self.username) > 50:
            raise ValueError("Username must be between 3 and 50 characters")
            
        if not self._is_valid_email(self.email):
            raise ValueError("Invalid email format")
            
        if not self._hashed_password:
            raise ValueError("Password hash cannot be empty")
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None
    
    def _setup_trial_if_needed(self) -> None:
        """Setup trial period for new trial users"""
        if self.role == UserRole.TRIAL and not self.trial_expires_at:
            self.trial_expires_at = datetime.now() + timedelta(days=14)  # 14-day trial
    
    @classmethod
    def create_new_user(cls, 
                       user_id: str,
                       username: str, 
                       email: str, 
                       password: str,
                       organization: Optional[str] = None,
                       role: UserRole = UserRole.TRIAL) -> "User":
        """
        Factory method to create a new user with proper password hashing.
        
        Follows Single Responsibility Principle by separating user creation logic.
        """
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
            
        hashed_password = cls._hash_password(password)
        
        user = cls(
            id=user_id,
            username=username,
            email=email,
            _hashed_password=hashed_password,
            organization=organization,
            role=role,
            status=UserStatus.PENDING_VERIFICATION
        )
        
        return user
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str) -> bool:
        """Verify password against stored hash"""
        if not password:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self._hashed_password.encode('utf-8'))
    
    def change_password(self, old_password: str, new_password: str) -> None:
        """Change user password with validation"""
        if not self.verify_password(old_password):
            raise ValueError("Current password is incorrect")
            
        if not new_password or len(new_password) < 8:
            raise ValueError("New password must be at least 8 characters long")
            
        self._hashed_password = self._hash_password(new_password)
        self.updated_at = datetime.now()
    
    def update_last_login(self) -> None:
        """Update last login timestamp"""
        self.last_login_at = datetime.now()
        self.updated_at = datetime.now()
    
    def verify_email(self) -> None:
        """Mark email as verified"""
        self.email_verified_at = datetime.now()
        if self.status == UserStatus.PENDING_VERIFICATION:
            self.status = UserStatus.ACTIVE
        self.updated_at = datetime.now()
    
    def upgrade_to_premium(self) -> None:
        """Upgrade user to premium role"""
        if self.role == UserRole.TRIAL and self.is_trial_expired():
            raise ValueError("Cannot upgrade expired trial. Please contact support.")
            
        self.role = UserRole.PREMIUM
        self.trial_expires_at = None  # Remove trial expiration
        self.updated_at = datetime.now()
    
    def downgrade_to_basic(self) -> None:
        """Downgrade user to basic role"""
        self.role = UserRole.BASIC
        self.trial_expires_at = None
        self.updated_at = datetime.now()
    
    def suspend_account(self, reason: str = "") -> None:
        """Suspend user account"""
        self.status = UserStatus.SUSPENDED
        if reason:
            self.preferences["suspension_reason"] = reason
        self.updated_at = datetime.now()
    
    def reactivate_account(self) -> None:
        """Reactivate suspended account"""
        if self.status == UserStatus.SUSPENDED:
            self.status = UserStatus.ACTIVE
            self.preferences.pop("suspension_reason", None)
            self.updated_at = datetime.now()
    
    def is_active(self) -> bool:
        """Check if user account is active"""
        return self.status == UserStatus.ACTIVE
    
    def is_email_verified(self) -> bool:
        """Check if email is verified"""
        return self.email_verified_at is not None
    
    def is_trial_user(self) -> bool:
        """Check if user is on trial"""
        return self.role == UserRole.TRIAL
    
    def is_trial_expired(self) -> bool:
        """Check if trial period has expired"""
        if not self.is_trial_user() or not self.trial_expires_at:
            return False
        return datetime.now() > self.trial_expires_at
    
    def get_remaining_trial_days(self) -> int:
        """Get remaining trial days"""
        if not self.is_trial_user() or not self.trial_expires_at:
            return 0
        remaining = self.trial_expires_at - datetime.now()
        return max(0, remaining.days)
    
    def can_generate_videos(self) -> bool:
        """Check if user can generate videos based on limits and status"""
        if not self.is_active():
            return False
            
        if self.is_trial_expired():
            return False
            
        if self.has_exceeded_monthly_limit():
            return False
            
        return True
    
    def has_exceeded_monthly_limit(self) -> bool:
        """Check if user has exceeded monthly video limit"""
        max_videos = self.role.get_max_monthly_videos()
        if max_videos == -1:  # Unlimited
            return False
        return self.monthly_videos_used >= max_videos
    
    def can_create_new_session(self) -> bool:
        """Check if user can create a new session"""
        if not self.can_generate_videos():
            return False
            
        max_sessions = self.role.get_max_sessions()
        if max_sessions == -1:  # Unlimited
            return True
            
        return len(self.active_sessions) < max_sessions
    
    def add_session(self, session_id: str) -> None:
        """Add a session to active sessions"""
        if not self.can_create_new_session():
            raise ValueError("Cannot create new session: limit exceeded or account inactive")
            
        if session_id not in self.active_sessions:
            self.active_sessions.append(session_id)
            self.updated_at = datetime.now()
    
    def remove_session(self, session_id: str) -> None:
        """Remove a session from active sessions"""
        if session_id in self.active_sessions:
            self.active_sessions.remove(session_id)
            self.updated_at = datetime.now()
    
    def increment_monthly_usage(self) -> None:
        """Increment monthly video usage"""
        self._reset_monthly_usage_if_needed()
        
        if self.has_exceeded_monthly_limit():
            raise ValueError("Monthly video generation limit exceeded")
            
        self.monthly_videos_used += 1
        if self.is_trial_user():
            self.trial_videos_used += 1
        self.updated_at = datetime.now()
    
    def _reset_monthly_usage_if_needed(self) -> None:
        """Reset monthly usage if new month has started"""
        now = datetime.now()
        if now.month != self.monthly_reset_date.month or now.year != self.monthly_reset_date.year:
            self.monthly_videos_used = 0
            self.monthly_reset_date = now.replace(day=1)
    
    def update_preferences(self, preferences: Dict[str, Any]) -> None:
        """Update user preferences"""
        self.preferences.update(preferences)
        self.updated_at = datetime.now()
    
    def update_notification_settings(self, settings: Dict[str, bool]) -> None:
        """Update notification preferences"""
        self.notification_settings.update(settings)
        self.updated_at = datetime.now()
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get user usage summary"""
        return {
            "role": self.role.value,
            "monthly_videos_used": self.monthly_videos_used,
            "monthly_limit": self.role.get_max_monthly_videos(),
            "active_sessions": len(self.active_sessions),
            "session_limit": self.role.get_max_sessions(),
            "trial_days_remaining": self.get_remaining_trial_days() if self.is_trial_user() else None,
            "can_generate_videos": self.can_generate_videos(),
            "can_create_sessions": self.can_create_new_session()
        }
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """
        Convert user entity to dictionary for serialization.
        
        Args:
            include_sensitive: Whether to include sensitive data (for internal use)
        """
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "organization": self.organization,
            "role": self.role.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "email_verified_at": self.email_verified_at.isoformat() if self.email_verified_at else None,
            "trial_expires_at": self.trial_expires_at.isoformat() if self.trial_expires_at else None,
            "trial_videos_used": self.trial_videos_used,
            "monthly_videos_used": self.monthly_videos_used,
            "monthly_reset_date": self.monthly_reset_date.isoformat(),
            "active_sessions": self.active_sessions.copy(),
            "preferences": self.preferences.copy(),
            "notification_settings": self.notification_settings.copy()
        }
        
        if include_sensitive:
            data["_hashed_password"] = self._hashed_password
            
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """Create user entity from dictionary"""
        return cls(
            id=data["id"],
            username=data["username"],
            email=data["email"],
            _hashed_password=data["_hashed_password"],
            organization=data.get("organization"),
            role=UserRole(data["role"]),
            status=UserStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            last_login_at=datetime.fromisoformat(data["last_login_at"]) if data.get("last_login_at") else None,
            email_verified_at=datetime.fromisoformat(data["email_verified_at"]) if data.get("email_verified_at") else None,
            trial_expires_at=datetime.fromisoformat(data["trial_expires_at"]) if data.get("trial_expires_at") else None,
            trial_videos_used=data.get("trial_videos_used", 0),
            monthly_videos_used=data.get("monthly_videos_used", 0),
            monthly_reset_date=datetime.fromisoformat(data["monthly_reset_date"]),
            active_sessions=data.get("active_sessions", []),
            preferences=data.get("preferences", {}),
            notification_settings=data.get("notification_settings", {
                "email_notifications": True,
                "video_completion_alerts": True,
                "weekly_usage_reports": True
            })
        )