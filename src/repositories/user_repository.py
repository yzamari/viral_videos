"""
User Repository implementation providing persistent storage for User entities.

This implementation follows the Repository pattern and provides concrete
data access functionality while maintaining proper error handling.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path

from src.domain.entities.user import User, UserRole
from src.repositories.interfaces import IUserRepository
from src.utils.exceptions import RepositoryError


class UserRepository(IUserRepository):
    """
    File-based User repository implementation.
    
    Provides persistent storage for User entities using JSON files.
    Implements proper error handling and maintains data consistency.
    """
    
    def __init__(self, base_path: str = "data/users"):
        """
        Initialize repository with base storage path.
        
        Args:
            base_path: Base directory for user data storage
        """
        self.base_path = Path(base_path)
        self._ensure_storage_directory()
    
    def _ensure_storage_directory(self) -> None:
        """Ensure storage directory exists"""
        try:
            self.base_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise RepositoryError(f"Failed to create storage directory: {e}")
    
    def _get_user_file_path(self, user_id: str) -> Path:
        """Get file path for user data"""
        return self.base_path / f"{user_id}.json"
    
    def _get_index_file_path(self) -> Path:
        """Get path for user index file"""
        return self.base_path / "user_index.json"
    
    async def _load_user_index(self) -> Dict[str, Dict[str, str]]:
        """
        Load user index for efficient lookups.
        
        Returns:
            Dictionary mapping usernames/emails to user IDs
        """
        index_path = self._get_index_file_path()
        if not index_path.exists():
            return {"by_username": {}, "by_email": {}}
        
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise RepositoryError(f"Failed to load user index: {e}")
    
    async def _save_user_index(self, index: Dict[str, Dict[str, str]]) -> None:
        """
        Save user index for efficient lookups.
        
        Args:
            index: User index to save
        """
        index_path = self._get_index_file_path()
        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise RepositoryError(f"Failed to save user index: {e}")
    
    async def _update_index_for_user(self, user: User) -> None:
        """Update index when user is saved"""
        index = await self._load_user_index()
        index["by_username"][user.username.lower()] = user.id
        index["by_email"][user.email.lower()] = user.id
        await self._save_user_index(index)
    
    async def _remove_from_index(self, user: User) -> None:
        """Remove user from index when deleted"""
        index = await self._load_user_index()
        index["by_username"].pop(user.username.lower(), None)
        index["by_email"].pop(user.email.lower(), None)
        await self._save_user_index(index)
    
    async def save(self, user: User) -> None:
        """
        Save user entity to storage.
        
        Args:
            user: User entity to save
            
        Raises:
            RepositoryError: If save operation fails
        """
        if not isinstance(user, User):
            raise RepositoryError("Entity must be a User instance")
        
        try:
            file_path = self._get_user_file_path(user.id)
            user_data = user.to_dict(include_sensitive=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, indent=2, ensure_ascii=False)
            
            # Update index for efficient lookups
            await self._update_index_for_user(user)
            
        except Exception as e:
            raise RepositoryError(f"Failed to save user {user.id}: {e}")
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID to retrieve
            
        Returns:
            User entity if found, None otherwise
        """
        if not user_id or not user_id.strip():
            return None
        
        try:
            file_path = self._get_user_file_path(user_id)
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            
            return User.from_dict(user_data)
            
        except Exception as e:
            raise RepositoryError(f"Failed to get user {user_id}: {e}")
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            User if found, None otherwise
        """
        if not username or not username.strip():
            return None
        
        try:
            index = await self._load_user_index()
            user_id = index["by_username"].get(username.lower())
            
            if user_id:
                return await self.get_by_id(user_id)
            return None
            
        except Exception as e:
            raise RepositoryError(f"Failed to get user by username {username}: {e}")
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            User if found, None otherwise
        """
        if not email or not email.strip():
            return None
        
        try:
            index = await self._load_user_index()
            user_id = index["by_email"].get(email.lower())
            
            if user_id:
                return await self.get_by_id(user_id)
            return None
            
        except Exception as e:
            raise RepositoryError(f"Failed to get user by email {email}: {e}")
    
    async def delete(self, user_id: str) -> bool:
        """
        Delete user by ID.
        
        Args:
            user_id: User ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        if not user_id or not user_id.strip():
            return False
        
        try:
            # Get user first to update index
            user = await self.get_by_id(user_id)
            if not user:
                return False
            
            file_path = self._get_user_file_path(user_id)
            if file_path.exists():
                file_path.unlink()
                await self._remove_from_index(user)
                return True
            
            return False
            
        except Exception as e:
            raise RepositoryError(f"Failed to delete user {user_id}: {e}")
    
    async def exists(self, user_id: str) -> bool:
        """
        Check if user exists.
        
        Args:
            user_id: User ID to check
            
        Returns:
            True if exists, False otherwise
        """
        if not user_id or not user_id.strip():
            return False
        
        try:
            file_path = self._get_user_file_path(user_id)
            return file_path.exists()
        except Exception as e:
            raise RepositoryError(f"Failed to check user existence {user_id}: {e}")
    
    async def list_all(self, limit: Optional[int] = None, offset: int = 0) -> List[User]:
        """
        List all users with pagination.
        
        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip
            
        Returns:
            List of users
        """
        try:
            users = []
            user_files = list(self.base_path.glob("*.json"))
            
            # Exclude index file
            user_files = [f for f in user_files if f.name != "user_index.json"]
            
            # Sort by modification time (most recent first)
            user_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            # Apply pagination
            if offset > 0:
                user_files = user_files[offset:]
            if limit is not None:
                user_files = user_files[:limit]
            
            for file_path in user_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        user_data = json.load(f)
                    user = User.from_dict(user_data)
                    users.append(user)
                except Exception as e:
                    # Log error but continue with other users
                    print(f"Warning: Failed to load user from {file_path}: {e}")
                    continue
            
            return users
            
        except Exception as e:
            raise RepositoryError(f"Failed to list users: {e}")
    
    async def count(self) -> int:
        """
        Count total number of users.
        
        Returns:
            Total user count
        """
        try:
            user_files = list(self.base_path.glob("*.json"))
            # Exclude index file
            user_files = [f for f in user_files if f.name != "user_index.json"]
            return len(user_files)
        except Exception as e:
            raise RepositoryError(f"Failed to count users: {e}")
    
    async def find_by_role(self, role: str, limit: Optional[int] = None) -> List[User]:
        """
        Find users by role.
        
        Args:
            role: User role to filter by
            limit: Maximum number of results
            
        Returns:
            List of users with the specified role
        """
        try:
            users = await self.list_all()
            filtered_users = [user for user in users if user.role.value == role]
            
            if limit is not None:
                filtered_users = filtered_users[:limit]
            
            return filtered_users
            
        except Exception as e:
            raise RepositoryError(f"Failed to find users by role {role}: {e}")
    
    async def find_trial_users_expiring(self, days: int = 7) -> List[User]:
        """
        Find trial users expiring within specified days.
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            List of users with trials expiring soon
        """
        try:
            users = await self.list_all()
            cutoff_date = datetime.now() + timedelta(days=days)
            
            expiring_users = []
            for user in users:
                if (user.is_trial_user() and 
                    user.trial_expires_at and 
                    user.trial_expires_at <= cutoff_date):
                    expiring_users.append(user)
            
            return expiring_users
            
        except Exception as e:
            raise RepositoryError(f"Failed to find expiring trial users: {e}")
    
    async def find_inactive_users(self, days: int = 30) -> List[User]:
        """
        Find users who haven't logged in for specified days.
        
        Args:
            days: Number of days of inactivity
            
        Returns:
            List of inactive users
        """
        try:
            users = await self.list_all()
            cutoff_date = datetime.now() - timedelta(days=days)
            
            inactive_users = []
            for user in users:
                if (not user.last_login_at or 
                    user.last_login_at < cutoff_date):
                    inactive_users.append(user)
            
            return inactive_users
            
        except Exception as e:
            raise RepositoryError(f"Failed to find inactive users: {e}")
    
    async def update_last_login(self, user_id: str) -> None:
        """
        Update user's last login timestamp.
        
        Args:
            user_id: ID of user to update
        """
        try:
            user = await self.get_by_id(user_id)
            if user:
                user.update_last_login()
                await self.save(user)
        except Exception as e:
            raise RepositoryError(f"Failed to update last login for user {user_id}: {e}")