"""
Campaign Repository implementation for persistent storage.

This implementation provides data access for Campaign entities
with proper indexing and query optimization.
"""

import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from src.domain.entities.campaign import Campaign, CampaignStatus
from src.repositories.interfaces import ICampaignRepository
from src.utils.exceptions import RepositoryError


class CampaignRepository(ICampaignRepository):
    """
    File-based Campaign repository implementation.
    
    Provides persistent storage for Campaign entities using JSON files
    with efficient indexing for complex queries.
    """
    
    def __init__(self, base_path: str = "data/campaigns"):
        """
        Initialize repository with base storage path.
        
        Args:
            base_path: Base directory for campaign data storage
        """
        self.base_path = Path(base_path)
        self._ensure_storage_directory()
    
    def _ensure_storage_directory(self) -> None:
        """Ensure storage directory exists"""
        try:
            self.base_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise RepositoryError(f"Failed to create storage directory: {e}")
    
    def _get_campaign_file_path(self, campaign_id: str) -> Path:
        """Get file path for campaign data"""
        return self.base_path / f"{campaign_id}.json"
    
    def _get_user_index_path(self) -> Path:
        """Get path for user-based campaign index"""
        return self.base_path / "user_campaigns_index.json"
    
    def _get_tag_index_path(self) -> Path:
        """Get path for tag-based campaign index"""
        return self.base_path / "tag_index.json"
    
    def _get_platform_index_path(self) -> Path:
        """Get path for platform-based campaign index"""
        return self.base_path / "platform_index.json"
    
    async def _load_user_index(self) -> Dict[str, List[str]]:
        """Load user campaign index"""
        index_path = self._get_user_index_path()
        if not index_path.exists():
            return {}
        
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise RepositoryError(f"Failed to load user index: {e}")
    
    async def _save_user_index(self, index: Dict[str, List[str]]) -> None:
        """Save user campaign index"""
        index_path = self._get_user_index_path()
        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise RepositoryError(f"Failed to save user index: {e}")
    
    async def _load_tag_index(self) -> Dict[str, List[str]]:
        """Load tag-based campaign index"""
        index_path = self._get_tag_index_path()
        if not index_path.exists():
            return {}
        
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise RepositoryError(f"Failed to load tag index: {e}")
    
    async def _save_tag_index(self, index: Dict[str, List[str]]) -> None:
        """Save tag-based campaign index"""
        index_path = self._get_tag_index_path()
        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise RepositoryError(f"Failed to save tag index: {e}")
    
    async def _load_platform_index(self) -> Dict[str, List[str]]:
        """Load platform-based campaign index"""
        index_path = self._get_platform_index_path()
        if not index_path.exists():
            return {}
        
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise RepositoryError(f"Failed to load platform index: {e}")
    
    async def _save_platform_index(self, index: Dict[str, List[str]]) -> None:
        """Save platform-based campaign index"""
        index_path = self._get_platform_index_path()
        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise RepositoryError(f"Failed to save platform index: {e}")
    
    async def _update_indexes_for_campaign(self, campaign: Campaign) -> None:
        """Update all indexes when campaign is saved"""
        # Update user index
        user_index = await self._load_user_index()
        if campaign.user_id not in user_index:
            user_index[campaign.user_id] = []
        if campaign.id not in user_index[campaign.user_id]:
            user_index[campaign.user_id].append(campaign.id)
        await self._save_user_index(user_index)
        
        # Update tag index
        tag_index = await self._load_tag_index()
        for tag in campaign.tags:
            if tag not in tag_index:
                tag_index[tag] = []
            if campaign.id not in tag_index[tag]:
                tag_index[tag].append(campaign.id)
        await self._save_tag_index(tag_index)
        
        # Update platform index
        platform_index = await self._load_platform_index()
        for platform in campaign.target_platforms:
            if platform not in platform_index:
                platform_index[platform] = []
            if campaign.id not in platform_index[platform]:
                platform_index[platform].append(campaign.id)
        await self._save_platform_index(platform_index)
    
    async def _remove_from_indexes(self, campaign: Campaign) -> None:
        """Remove campaign from all indexes when deleted"""
        # Remove from user index
        user_index = await self._load_user_index()
        if campaign.user_id in user_index:
            user_campaigns = user_index[campaign.user_id]
            if campaign.id in user_campaigns:
                user_campaigns.remove(campaign.id)
            if not user_campaigns:
                del user_index[campaign.user_id]
        await self._save_user_index(user_index)
        
        # Remove from tag index
        tag_index = await self._load_tag_index()
        for tag_campaigns in tag_index.values():
            if campaign.id in tag_campaigns:
                tag_campaigns.remove(campaign.id)
        # Clean empty tag lists
        tag_index = {k: v for k, v in tag_index.items() if v}
        await self._save_tag_index(tag_index)
        
        # Remove from platform index
        platform_index = await self._load_platform_index()
        for platform_campaigns in platform_index.values():
            if campaign.id in platform_campaigns:
                platform_campaigns.remove(campaign.id)
        # Clean empty platform lists
        platform_index = {k: v for k, v in platform_index.items() if v}
        await self._save_platform_index(platform_index)
    
    async def save(self, campaign: Campaign) -> None:
        """
        Save campaign entity to storage.
        
        Args:
            campaign: Campaign entity to save
            
        Raises:
            RepositoryError: If save operation fails
        """
        if not isinstance(campaign, Campaign):
            raise RepositoryError("Entity must be a Campaign instance")
        
        try:
            file_path = self._get_campaign_file_path(campaign.id)
            campaign_data = campaign.to_dict()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(campaign_data, f, indent=2, ensure_ascii=False)
            
            # Update indexes for efficient queries
            await self._update_indexes_for_campaign(campaign)
            
        except Exception as e:
            raise RepositoryError(f"Failed to save campaign {campaign.id}: {e}")
    
    async def get_by_id(self, campaign_id: str) -> Optional[Campaign]:
        """
        Get campaign by ID.
        
        Args:
            campaign_id: Campaign ID to retrieve
            
        Returns:
            Campaign entity if found, None otherwise
        """
        if not campaign_id or not campaign_id.strip():
            return None
        
        try:
            file_path = self._get_campaign_file_path(campaign_id)
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                campaign_data = json.load(f)
            
            return Campaign.from_dict(campaign_data)
            
        except Exception as e:
            raise RepositoryError(f"Failed to get campaign {campaign_id}: {e}")
    
    async def get_by_user_id(self, user_id: str, limit: Optional[int] = None) -> List[Campaign]:
        """
        Get campaigns by user ID.
        
        Args:
            user_id: User ID to filter by
            limit: Maximum number of results
            
        Returns:
            List of user's campaigns
        """
        if not user_id or not user_id.strip():
            return []
        
        try:
            user_index = await self._load_user_index()
            campaign_ids = user_index.get(user_id, [])
            
            if limit is not None:
                campaign_ids = campaign_ids[:limit]
            
            campaigns = []
            for campaign_id in campaign_ids:
                campaign = await self.get_by_id(campaign_id)
                if campaign:
                    campaigns.append(campaign)
            
            # Sort by creation time (most recent first)
            campaigns.sort(key=lambda c: c.created_at, reverse=True)
            
            return campaigns
            
        except Exception as e:
            raise RepositoryError(f"Failed to get campaigns for user {user_id}: {e}")
    
    async def get_active_campaigns(self, user_id: Optional[str] = None) -> List[Campaign]:
        """
        Get active campaigns.
        
        Args:
            user_id: Optional user ID to filter by
            
        Returns:
            List of active campaigns
        """
        try:
            active_campaigns = await self.get_by_status(CampaignStatus.ACTIVE.value)
            
            # Filter by user if specified
            if user_id:
                active_campaigns = [c for c in active_campaigns if c.user_id == user_id]
            
            return active_campaigns
            
        except Exception as e:
            raise RepositoryError(f"Failed to get active campaigns: {e}")
    
    async def get_by_status(self, status: str, limit: Optional[int] = None) -> List[Campaign]:
        """
        Get campaigns by status.
        
        Args:
            status: Campaign status to filter by
            limit: Maximum number of results
            
        Returns:
            List of campaigns with specified status
        """
        try:
            all_campaigns = await self.list_all()
            status_campaigns = [c for c in all_campaigns if c.status.value == status]
            
            if limit is not None:
                status_campaigns = status_campaigns[:limit]
            
            return status_campaigns
            
        except Exception as e:
            raise RepositoryError(f"Failed to get campaigns by status {status}: {e}")
    
    async def find_by_tags(self, tags: List[str], user_id: Optional[str] = None) -> List[Campaign]:
        """
        Find campaigns by tags.
        
        Args:
            tags: List of tags to search for
            user_id: Optional user ID filter
            
        Returns:
            List of campaigns containing any of the specified tags
        """
        try:
            tag_index = await self._load_tag_index()
            matching_campaign_ids = set()
            
            # Find campaigns with any of the specified tags
            for tag in tags:
                tag_lower = tag.lower()
                if tag_lower in tag_index:
                    matching_campaign_ids.update(tag_index[tag_lower])
            
            campaigns = []
            for campaign_id in matching_campaign_ids:
                campaign = await self.get_by_id(campaign_id)
                if campaign:
                    # Filter by user if specified
                    if not user_id or campaign.user_id == user_id:
                        campaigns.append(campaign)
            
            # Sort by creation time
            campaigns.sort(key=lambda c: c.created_at, reverse=True)
            
            return campaigns
            
        except Exception as e:
            raise RepositoryError(f"Failed to find campaigns by tags: {e}")
    
    async def get_campaigns_by_platform(self, platform: str, user_id: Optional[str] = None) -> List[Campaign]:
        """
        Get campaigns targeting specific platform.
        
        Args:
            platform: Platform to filter by
            user_id: Optional user ID filter
            
        Returns:
            List of campaigns targeting the platform
        """
        try:
            platform_index = await self._load_platform_index()
            campaign_ids = platform_index.get(platform, [])
            
            campaigns = []
            for campaign_id in campaign_ids:
                campaign = await self.get_by_id(campaign_id)
                if campaign:
                    # Filter by user if specified
                    if not user_id or campaign.user_id == user_id:
                        campaigns.append(campaign)
            
            # Sort by creation time
            campaigns.sort(key=lambda c: c.created_at, reverse=True)
            
            return campaigns
            
        except Exception as e:
            raise RepositoryError(f"Failed to get campaigns by platform {platform}: {e}")
    
    async def get_campaign_performance_summary(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get campaign performance summary.
        
        Args:
            campaign_id: Campaign ID to get summary for
            
        Returns:
            Dictionary with campaign performance metrics
        """
        try:
            campaign = await self.get_by_id(campaign_id)
            if not campaign:
                raise RepositoryError(f"Campaign {campaign_id} not found")
            
            return campaign.get_campaign_summary()
            
        except Exception as e:
            raise RepositoryError(f"Failed to get campaign performance summary for {campaign_id}: {e}")
    
    async def delete(self, campaign_id: str) -> bool:
        """
        Delete campaign by ID.
        
        Args:
            campaign_id: Campaign ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        if not campaign_id or not campaign_id.strip():
            return False
        
        try:
            # Get campaign first to update indexes
            campaign = await self.get_by_id(campaign_id)
            if not campaign:
                return False
            
            file_path = self._get_campaign_file_path(campaign_id)
            if file_path.exists():
                file_path.unlink()
                await self._remove_from_indexes(campaign)
                return True
            
            return False
            
        except Exception as e:
            raise RepositoryError(f"Failed to delete campaign {campaign_id}: {e}")
    
    async def exists(self, campaign_id: str) -> bool:
        """
        Check if campaign exists.
        
        Args:
            campaign_id: Campaign ID to check
            
        Returns:
            True if exists, False otherwise
        """
        if not campaign_id or not campaign_id.strip():
            return False
        
        try:
            file_path = self._get_campaign_file_path(campaign_id)
            return file_path.exists()
        except Exception as e:
            raise RepositoryError(f"Failed to check campaign existence {campaign_id}: {e}")
    
    async def list_all(self, limit: Optional[int] = None, offset: int = 0) -> List[Campaign]:
        """
        List all campaigns with pagination.
        
        Args:
            limit: Maximum number of campaigns to return
            offset: Number of campaigns to skip
            
        Returns:
            List of campaigns
        """
        try:
            campaigns = []
            campaign_files = list(self.base_path.glob("*.json"))
            
            # Exclude index files
            campaign_files = [f for f in campaign_files if not f.name.endswith("_index.json")]
            
            # Sort by modification time (most recent first)
            campaign_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            # Apply pagination
            if offset > 0:
                campaign_files = campaign_files[offset:]
            if limit is not None:
                campaign_files = campaign_files[:limit]
            
            for file_path in campaign_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        campaign_data = json.load(f)
                    campaign = Campaign.from_dict(campaign_data)
                    campaigns.append(campaign)
                except Exception as e:
                    # Log error but continue with other campaigns
                    print(f"Warning: Failed to load campaign from {file_path}: {e}")
                    continue
            
            return campaigns
            
        except Exception as e:
            raise RepositoryError(f"Failed to list campaigns: {e}")
    
    async def count(self) -> int:
        """
        Count total number of campaigns.
        
        Returns:
            Total campaign count
        """
        try:
            campaign_files = list(self.base_path.glob("*.json"))
            # Exclude index files
            campaign_files = [f for f in campaign_files if not f.name.endswith("_index.json")]
            return len(campaign_files)
        except Exception as e:
            raise RepositoryError(f"Failed to count campaigns: {e}")