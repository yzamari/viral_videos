"""
Multi-Platform Advertising Integration System
Unified interface for all major advertising platforms
"""

import os
import json
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
import requests
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign as FBCampaign
import tweepy
from linkedin_ads import LinkedInAds
from tiktok_ads import TikTokAds
import stripe  # For payment processing

logger = logging.getLogger(__name__)


@dataclass
class AdCreative:
    """Universal ad creative format"""
    headline: str
    description: str
    media_url: str
    media_type: str  # image, video
    cta_text: str
    landing_url: str
    metadata: Dict[str, Any]


@dataclass 
class AdSet:
    """Universal ad set/ad group format"""
    name: str
    budget: float
    schedule: Dict[str, Any]
    targeting: Dict[str, Any]
    creatives: List[AdCreative]
    bidding: Dict[str, Any]


@dataclass
class PlatformCampaign:
    """Universal campaign format for platform APIs"""
    name: str
    objective: str
    budget: float
    ad_sets: List[AdSet]
    settings: Dict[str, Any]


class PlatformAdapter(ABC):
    """Abstract base class for platform adapters"""
    
    @abstractmethod
    async def create_campaign(self, campaign: PlatformCampaign) -> Dict[str, Any]:
        """Create campaign on platform"""
        pass
    
    @abstractmethod
    async def update_campaign(self, campaign_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing campaign"""
        pass
    
    @abstractmethod
    async def pause_campaign(self, campaign_id: str) -> bool:
        """Pause campaign"""
        pass
    
    @abstractmethod
    async def resume_campaign(self, campaign_id: str) -> bool:
        """Resume campaign"""
        pass
    
    @abstractmethod
    async def get_performance(self, campaign_id: str, date_range: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """Get campaign performance metrics"""
        pass
    
    @abstractmethod
    async def get_spend(self, campaign_id: str) -> float:
        """Get current spend"""
        pass


class GoogleAdsAdapter(PlatformAdapter):
    """Google Ads platform adapter"""
    
    def __init__(self):
        """Initialize Google Ads client"""
        self.client = None
        self.customer_id = os.getenv('GOOGLE_ADS_CUSTOMER_ID')
        
        try:
            # Initialize with credentials
            self.client = GoogleAdsClient.load_from_storage()
            logger.info("✅ Google Ads client initialized")
        except Exception as e:
            logger.error(f"❌ Google Ads initialization failed: {e}")
    
    async def create_campaign(self, campaign: PlatformCampaign) -> Dict[str, Any]:
        """Create Google Ads campaign"""
        if not self.client:
            return {'error': 'Google Ads client not initialized'}
        
        try:
            campaign_service = self.client.get_service("CampaignService")
            campaign_operation = self.client.get_type("CampaignOperation")
            
            # Create campaign
            new_campaign = campaign_operation.create
            new_campaign.name = campaign.name
            new_campaign.advertising_channel_type = self._map_objective(campaign.objective)
            
            # Set budget
            campaign_budget_service = self.client.get_service("CampaignBudgetService")
            budget_operation = self.client.get_type("CampaignBudgetOperation")
            budget = budget_operation.create
            budget.name = f"{campaign.name} Budget"
            budget.amount_micros = int(campaign.budget * 1_000_000)
            budget.delivery_method = "STANDARD"
            
            # Create budget first
            budget_response = campaign_budget_service.mutate_campaign_budgets(
                customer_id=self.customer_id,
                operations=[budget_operation]
            )
            
            new_campaign.campaign_budget = budget_response.results[0].resource_name
            new_campaign.status = "ENABLED"
            
            # Set bidding strategy
            new_campaign.bidding_strategy_type = "MAXIMIZE_CONVERSIONS"
            
            # Create campaign
            response = campaign_service.mutate_campaigns(
                customer_id=self.customer_id,
                operations=[campaign_operation]
            )
            
            campaign_id = response.results[0].resource_name
            
            # Create ad groups and ads
            for ad_set in campaign.ad_sets:
                await self._create_ad_group(campaign_id, ad_set)
            
            return {
                'platform': 'google_ads',
                'campaign_id': campaign_id,
                'status': 'created',
                'estimated_reach': self._estimate_reach(campaign)
            }
            
        except GoogleAdsException as e:
            logger.error(f"Google Ads error: {e}")
            return {'error': str(e)}
    
    async def _create_ad_group(self, campaign_id: str, ad_set: AdSet) -> str:
        """Create ad group within campaign"""
        ad_group_service = self.client.get_service("AdGroupService")
        ad_group_operation = self.client.get_type("AdGroupOperation")
        
        ad_group = ad_group_operation.create
        ad_group.name = ad_set.name
        ad_group.campaign = campaign_id
        ad_group.status = "ENABLED"
        
        # Set bidding
        ad_group.cpc_bid_micros = int(ad_set.bidding.get('max_cpc', 1.0) * 1_000_000)
        
        response = ad_group_service.mutate_ad_groups(
            customer_id=self.customer_id,
            operations=[ad_group_operation]
        )
        
        ad_group_id = response.results[0].resource_name
        
        # Create ads
        for creative in ad_set.creatives:
            await self._create_ad(ad_group_id, creative)
        
        return ad_group_id
    
    async def _create_ad(self, ad_group_id: str, creative: AdCreative) -> str:
        """Create individual ad"""
        ad_service = self.client.get_service("AdService")
        ad_operation = self.client.get_type("AdOperation")
        
        ad = ad_operation.create
        ad.ad_group = ad_group_id
        
        # Create responsive display ad
        if creative.media_type == 'image':
            ad.responsive_display_ad.headlines.append(creative.headline)
            ad.responsive_display_ad.descriptions.append(creative.description)
            ad.responsive_display_ad.marketing_images.append(creative.media_url)
            ad.responsive_display_ad.business_name = "Business"
        
        ad.final_urls.append(creative.landing_url)
        
        response = ad_service.mutate_ads(
            customer_id=self.customer_id,
            operations=[ad_operation]
        )
        
        return response.results[0].resource_name
    
    async def update_campaign(self, campaign_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update Google Ads campaign"""
        try:
            campaign_service = self.client.get_service("CampaignService")
            campaign_operation = self.client.get_type("CampaignOperation")
            
            campaign = campaign_operation.update
            campaign.resource_name = campaign_id
            
            # Update fields
            if 'budget' in updates:
                # Update budget
                pass
            
            if 'status' in updates:
                campaign.status = updates['status']
            
            response = campaign_service.mutate_campaigns(
                customer_id=self.customer_id,
                operations=[campaign_operation]
            )
            
            return {'status': 'updated', 'campaign_id': campaign_id}
            
        except GoogleAdsException as e:
            return {'error': str(e)}
    
    async def pause_campaign(self, campaign_id: str) -> bool:
        """Pause Google Ads campaign"""
        result = await self.update_campaign(campaign_id, {'status': 'PAUSED'})
        return 'error' not in result
    
    async def resume_campaign(self, campaign_id: str) -> bool:
        """Resume Google Ads campaign"""
        result = await self.update_campaign(campaign_id, {'status': 'ENABLED'})
        return 'error' not in result
    
    async def get_performance(self, campaign_id: str, date_range: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """Get Google Ads performance metrics"""
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            query = f"""
                SELECT
                    campaign.id,
                    campaign.name,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.conversions,
                    metrics.cost_micros,
                    metrics.average_cpc,
                    metrics.ctr,
                    metrics.conversion_rate
                FROM campaign
                WHERE campaign.resource_name = '{campaign_id}'
                    AND segments.date BETWEEN '{date_range[0].strftime('%Y-%m-%d')}'
                    AND '{date_range[1].strftime('%Y-%m-%d')}'
            """
            
            response = ga_service.search_stream(
                customer_id=self.customer_id,
                query=query
            )
            
            metrics = {
                'impressions': 0,
                'clicks': 0,
                'conversions': 0,
                'cost': 0,
                'ctr': 0,
                'conversion_rate': 0
            }
            
            for batch in response:
                for row in batch.results:
                    metrics['impressions'] += row.metrics.impressions
                    metrics['clicks'] += row.metrics.clicks
                    metrics['conversions'] += row.metrics.conversions
                    metrics['cost'] += row.metrics.cost_micros / 1_000_000
                    metrics['ctr'] = row.metrics.ctr
                    metrics['conversion_rate'] = row.metrics.conversion_rate
            
            return metrics
            
        except GoogleAdsException as e:
            logger.error(f"Error getting performance: {e}")
            return {}
    
    async def get_spend(self, campaign_id: str) -> float:
        """Get current Google Ads spend"""
        metrics = await self.get_performance(
            campaign_id,
            (datetime.now() - timedelta(days=30), datetime.now())
        )
        return metrics.get('cost', 0)
    
    def _map_objective(self, objective: str) -> str:
        """Map universal objective to Google Ads objective"""
        mapping = {
            'brand_awareness': 'DISPLAY',
            'traffic': 'SEARCH',
            'sales_conversion': 'SHOPPING',
            'lead_generation': 'SEARCH',
            'app_installs': 'APP',
            'video_views': 'VIDEO'
        }
        return mapping.get(objective, 'SEARCH')
    
    def _estimate_reach(self, campaign: PlatformCampaign) -> int:
        """Estimate campaign reach"""
        # Simplified estimation
        return int(campaign.budget * 1000)


class MetaAdsAdapter(PlatformAdapter):
    """Meta (Facebook/Instagram) Ads adapter"""
    
    def __init__(self):
        """Initialize Meta Ads API"""
        self.api = None
        self.ad_account_id = os.getenv('META_AD_ACCOUNT_ID')
        
        try:
            app_id = os.getenv('META_APP_ID')
            app_secret = os.getenv('META_APP_SECRET')
            access_token = os.getenv('META_ACCESS_TOKEN')
            
            FacebookAdsApi.init(app_id, app_secret, access_token)
            self.api = FacebookAdsApi.get_default_api()
            self.ad_account = AdAccount(f'act_{self.ad_account_id}')
            logger.info("✅ Meta Ads API initialized")
        except Exception as e:
            logger.error(f"❌ Meta Ads initialization failed: {e}")
    
    async def create_campaign(self, campaign: PlatformCampaign) -> Dict[str, Any]:
        """Create Meta Ads campaign"""
        if not self.api:
            return {'error': 'Meta Ads API not initialized'}
        
        try:
            # Create campaign
            fb_campaign = self.ad_account.create_campaign(
                params={
                    'name': campaign.name,
                    'objective': self._map_objective(campaign.objective),
                    'status': 'ACTIVE',
                    'special_ad_categories': []
                }
            )
            
            campaign_id = fb_campaign['id']
            
            # Create ad sets
            for ad_set in campaign.ad_sets:
                await self._create_ad_set(campaign_id, ad_set)
            
            return {
                'platform': 'meta_ads',
                'campaign_id': campaign_id,
                'status': 'created',
                'platforms': ['facebook', 'instagram']
            }
            
        except Exception as e:
            logger.error(f"Meta Ads error: {e}")
            return {'error': str(e)}
    
    async def _create_ad_set(self, campaign_id: str, ad_set: AdSet) -> str:
        """Create Meta ad set"""
        targeting = {
            'geo_locations': {
                'countries': ad_set.targeting.get('locations', ['US'])
            },
            'age_min': ad_set.targeting.get('age_min', 18),
            'age_max': ad_set.targeting.get('age_max', 65),
            'interests': self._map_interests(ad_set.targeting.get('interests', []))
        }
        
        fb_ad_set = self.ad_account.create_ad_set(
            params={
                'name': ad_set.name,
                'campaign_id': campaign_id,
                'daily_budget': int(ad_set.budget * 100),  # In cents
                'billing_event': 'IMPRESSIONS',
                'optimization_goal': 'REACH',
                'targeting': targeting,
                'status': 'ACTIVE',
                'start_time': ad_set.schedule.get('start', datetime.now().isoformat()),
                'end_time': ad_set.schedule.get('end')
            }
        )
        
        ad_set_id = fb_ad_set['id']
        
        # Create ads
        for creative in ad_set.creatives:
            await self._create_ad(ad_set_id, creative)
        
        return ad_set_id
    
    async def _create_ad(self, ad_set_id: str, creative: AdCreative) -> str:
        """Create Meta ad"""
        # Create creative
        ad_creative = self.ad_account.create_ad_creative(
            params={
                'name': f'Creative for {creative.headline}',
                'object_story_spec': {
                    'page_id': os.getenv('META_PAGE_ID'),
                    'link_data': {
                        'message': creative.description,
                        'link': creative.landing_url,
                        'name': creative.headline,
                        'call_to_action': {
                            'type': self._map_cta(creative.cta_text)
                        }
                    }
                }
            }
        )
        
        # Create ad
        ad = self.ad_account.create_ad(
            params={
                'name': creative.headline,
                'adset_id': ad_set_id,
                'creative': {'creative_id': ad_creative['id']},
                'status': 'ACTIVE'
            }
        )
        
        return ad['id']
    
    async def update_campaign(self, campaign_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update Meta Ads campaign"""
        try:
            campaign = FBCampaign(campaign_id)
            campaign.api_update(params=updates)
            return {'status': 'updated', 'campaign_id': campaign_id}
        except Exception as e:
            return {'error': str(e)}
    
    async def pause_campaign(self, campaign_id: str) -> bool:
        """Pause Meta Ads campaign"""
        result = await self.update_campaign(campaign_id, {'status': 'PAUSED'})
        return 'error' not in result
    
    async def resume_campaign(self, campaign_id: str) -> bool:
        """Resume Meta Ads campaign"""
        result = await self.update_campaign(campaign_id, {'status': 'ACTIVE'})
        return 'error' not in result
    
    async def get_performance(self, campaign_id: str, date_range: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """Get Meta Ads performance metrics"""
        try:
            campaign = FBCampaign(campaign_id)
            insights = campaign.get_insights(
                params={
                    'time_range': {
                        'since': date_range[0].strftime('%Y-%m-%d'),
                        'until': date_range[1].strftime('%Y-%m-%d')
                    },
                    'fields': [
                        'impressions',
                        'clicks',
                        'spend',
                        'ctr',
                        'conversions',
                        'conversion_rate'
                    ]
                }
            )
            
            if insights:
                data = insights[0]
                return {
                    'impressions': int(data.get('impressions', 0)),
                    'clicks': int(data.get('clicks', 0)),
                    'cost': float(data.get('spend', 0)),
                    'ctr': float(data.get('ctr', 0)),
                    'conversions': int(data.get('conversions', 0))
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting Meta performance: {e}")
            return {}
    
    async def get_spend(self, campaign_id: str) -> float:
        """Get current Meta Ads spend"""
        metrics = await self.get_performance(
            campaign_id,
            (datetime.now() - timedelta(days=30), datetime.now())
        )
        return metrics.get('cost', 0)
    
    def _map_objective(self, objective: str) -> str:
        """Map universal objective to Meta objective"""
        mapping = {
            'brand_awareness': 'BRAND_AWARENESS',
            'traffic': 'LINK_CLICKS',
            'sales_conversion': 'CONVERSIONS',
            'lead_generation': 'LEAD_GENERATION',
            'app_installs': 'APP_INSTALLS',
            'video_views': 'VIDEO_VIEWS',
            'engagement': 'POST_ENGAGEMENT'
        }
        return mapping.get(objective, 'LINK_CLICKS')
    
    def _map_interests(self, interests: List[str]) -> List[Dict[str, Any]]:
        """Map interests to Meta format"""
        # In production, use Meta's interest targeting API
        return [{'id': interest, 'name': interest} for interest in interests]
    
    def _map_cta(self, cta_text: str) -> str:
        """Map CTA text to Meta CTA type"""
        mapping = {
            'Learn More': 'LEARN_MORE',
            'Shop Now': 'SHOP_NOW',
            'Sign Up': 'SIGN_UP',
            'Download': 'DOWNLOAD',
            'Get Started': 'GET_STARTED'
        }
        return mapping.get(cta_text, 'LEARN_MORE')


class TikTokAdsAdapter(PlatformAdapter):
    """TikTok Ads adapter"""
    
    def __init__(self):
        """Initialize TikTok Ads API"""
        self.api_key = os.getenv('TIKTOK_ADS_API_KEY')
        self.advertiser_id = os.getenv('TIKTOK_ADVERTISER_ID')
        self.base_url = "https://business-api.tiktok.com/open_api/v1.3"
        logger.info("✅ TikTok Ads adapter initialized")
    
    async def create_campaign(self, campaign: PlatformCampaign) -> Dict[str, Any]:
        """Create TikTok Ads campaign"""
        try:
            headers = {
                'Access-Token': self.api_key,
                'Content-Type': 'application/json'
            }
            
            # Create campaign
            campaign_data = {
                'advertiser_id': self.advertiser_id,
                'campaign_name': campaign.name,
                'objective_type': self._map_objective(campaign.objective),
                'budget_mode': 'BUDGET_MODE_DAY',
                'budget': campaign.budget
            }
            
            response = requests.post(
                f"{self.base_url}/campaign/create/",
                headers=headers,
                json=campaign_data
            )
            
            if response.status_code == 200:
                result = response.json()
                campaign_id = result['data']['campaign_id']
                
                # Create ad groups
                for ad_set in campaign.ad_sets:
                    await self._create_ad_group(campaign_id, ad_set)
                
                return {
                    'platform': 'tiktok_ads',
                    'campaign_id': campaign_id,
                    'status': 'created'
                }
            else:
                return {'error': f"TikTok API error: {response.text}"}
                
        except Exception as e:
            logger.error(f"TikTok Ads error: {e}")
            return {'error': str(e)}
    
    async def _create_ad_group(self, campaign_id: str, ad_set: AdSet) -> str:
        """Create TikTok ad group"""
        headers = {
            'Access-Token': self.api_key,
            'Content-Type': 'application/json'
        }
        
        ad_group_data = {
            'advertiser_id': self.advertiser_id,
            'campaign_id': campaign_id,
            'adgroup_name': ad_set.name,
            'placement_type': 'PLACEMENT_TYPE_AUTOMATIC',
            'budget_mode': 'BUDGET_MODE_DAY',
            'budget': ad_set.budget,
            'schedule_type': 'SCHEDULE_START_END',
            'start_time': ad_set.schedule.get('start', datetime.now().isoformat()),
            'location_ids': self._map_locations(ad_set.targeting.get('locations', [])),
            'age_groups': self._map_age_groups(ad_set.targeting),
            'gender': ad_set.targeting.get('gender', 'GENDER_UNLIMITED')
        }
        
        response = requests.post(
            f"{self.base_url}/adgroup/create/",
            headers=headers,
            json=ad_group_data
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['data']['adgroup_id']
        else:
            raise Exception(f"Failed to create ad group: {response.text}")
    
    async def update_campaign(self, campaign_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update TikTok Ads campaign"""
        headers = {
            'Access-Token': self.api_key,
            'Content-Type': 'application/json'
        }
        
        update_data = {
            'advertiser_id': self.advertiser_id,
            'campaign_id': campaign_id,
            **updates
        }
        
        response = requests.post(
            f"{self.base_url}/campaign/update/",
            headers=headers,
            json=update_data
        )
        
        if response.status_code == 200:
            return {'status': 'updated', 'campaign_id': campaign_id}
        else:
            return {'error': f"Update failed: {response.text}"}
    
    async def pause_campaign(self, campaign_id: str) -> bool:
        """Pause TikTok Ads campaign"""
        result = await self.update_campaign(campaign_id, {'operation_status': 'DISABLE'})
        return 'error' not in result
    
    async def resume_campaign(self, campaign_id: str) -> bool:
        """Resume TikTok Ads campaign"""
        result = await self.update_campaign(campaign_id, {'operation_status': 'ENABLE'})
        return 'error' not in result
    
    async def get_performance(self, campaign_id: str, date_range: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """Get TikTok Ads performance metrics"""
        headers = {'Access-Token': self.api_key}
        
        params = {
            'advertiser_id': self.advertiser_id,
            'filtering': json.dumps({'campaign_ids': [campaign_id]}),
            'start_date': date_range[0].strftime('%Y-%m-%d'),
            'end_date': date_range[1].strftime('%Y-%m-%d'),
            'metrics': json.dumps([
                'impressions', 'clicks', 'spend', 'conversions', 'ctr', 'cvr'
            ])
        }
        
        response = requests.get(
            f"{self.base_url}/reports/integrated/get/",
            headers=headers,
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()['data']['list'][0] if response.json()['data']['list'] else {}
            return {
                'impressions': data.get('impressions', 0),
                'clicks': data.get('clicks', 0),
                'cost': data.get('spend', 0),
                'conversions': data.get('conversions', 0),
                'ctr': data.get('ctr', 0),
                'cvr': data.get('cvr', 0)
            }
        
        return {}
    
    async def get_spend(self, campaign_id: str) -> float:
        """Get current TikTok Ads spend"""
        metrics = await self.get_performance(
            campaign_id,
            (datetime.now() - timedelta(days=30), datetime.now())
        )
        return metrics.get('cost', 0)
    
    def _map_objective(self, objective: str) -> str:
        """Map universal objective to TikTok objective"""
        mapping = {
            'brand_awareness': 'REACH',
            'traffic': 'TRAFFIC',
            'sales_conversion': 'CONVERSIONS',
            'lead_generation': 'LEAD_GENERATION',
            'app_installs': 'APP_PROMOTION',
            'video_views': 'VIDEO_VIEWS'
        }
        return mapping.get(objective, 'TRAFFIC')
    
    def _map_locations(self, locations: List[str]) -> List[int]:
        """Map location names to TikTok location IDs"""
        # Simplified mapping - in production use TikTok's location API
        location_map = {
            'US': 6252001,
            'UK': 2635167,
            'CA': 6251999,
            'AU': 2077456
        }
        return [location_map.get(loc, 6252001) for loc in locations]
    
    def _map_age_groups(self, targeting: Dict[str, Any]) -> List[str]:
        """Map age range to TikTok age groups"""
        age_min = targeting.get('age_min', 18)
        age_max = targeting.get('age_max', 65)
        
        age_groups = []
        if age_min <= 17:
            age_groups.append('AGE_13_17')
        if age_min <= 24 and age_max >= 18:
            age_groups.append('AGE_18_24')
        if age_min <= 34 and age_max >= 25:
            age_groups.append('AGE_25_34')
        if age_min <= 44 and age_max >= 35:
            age_groups.append('AGE_35_44')
        if age_min <= 54 and age_max >= 45:
            age_groups.append('AGE_45_54')
        if age_max >= 55:
            age_groups.append('AGE_55_100')
        
        return age_groups if age_groups else ['AGE_18_24', 'AGE_25_34']


class UnifiedAdPlatformManager:
    """
    Unified manager for all advertising platforms
    Provides single interface for multi-platform campaigns
    """
    
    def __init__(self):
        """Initialize all platform adapters"""
        self.adapters = {
            'google_ads': GoogleAdsAdapter(),
            'meta_ads': MetaAdsAdapter(),
            'tiktok_ads': TikTokAdsAdapter(),
            # Add more adapters as needed
        }
        
        self.campaign_mappings = {}  # Maps internal IDs to platform IDs
        logger.info("✅ UnifiedAdPlatformManager initialized")
    
    async def create_multi_platform_campaign(
        self,
        campaign: PlatformCampaign,
        platforms: List[str]
    ) -> Dict[str, Any]:
        """
        Create campaign across multiple platforms
        
        Args:
            campaign: Universal campaign format
            platforms: List of platform names
            
        Returns:
            Results from each platform
        """
        results = {}
        tasks = []
        
        for platform in platforms:
            if platform in self.adapters:
                task = self.adapters[platform].create_campaign(campaign)
                tasks.append((platform, task))
        
        # Execute in parallel
        for platform, task in tasks:
            try:
                result = await task
                results[platform] = result
                
                # Store mapping
                if 'campaign_id' in result:
                    if campaign.name not in self.campaign_mappings:
                        self.campaign_mappings[campaign.name] = {}
                    self.campaign_mappings[campaign.name][platform] = result['campaign_id']
                    
            except Exception as e:
                results[platform] = {'error': str(e)}
                logger.error(f"Failed to create campaign on {platform}: {e}")
        
        return results
    
    async def pause_all_campaigns(self, campaign_name: str) -> Dict[str, bool]:
        """Pause campaign across all platforms"""
        results = {}
        
        if campaign_name in self.campaign_mappings:
            for platform, campaign_id in self.campaign_mappings[campaign_name].items():
                if platform in self.adapters:
                    success = await self.adapters[platform].pause_campaign(campaign_id)
                    results[platform] = success
        
        return results
    
    async def get_unified_performance(
        self,
        campaign_name: str,
        date_range: Tuple[datetime, datetime]
    ) -> Dict[str, Any]:
        """Get performance metrics across all platforms"""
        unified_metrics = {
            'total_impressions': 0,
            'total_clicks': 0,
            'total_conversions': 0,
            'total_spend': 0,
            'platform_breakdown': {}
        }
        
        if campaign_name in self.campaign_mappings:
            for platform, campaign_id in self.campaign_mappings[campaign_name].items():
                if platform in self.adapters:
                    metrics = await self.adapters[platform].get_performance(
                        campaign_id,
                        date_range
                    )
                    
                    unified_metrics['platform_breakdown'][platform] = metrics
                    unified_metrics['total_impressions'] += metrics.get('impressions', 0)
                    unified_metrics['total_clicks'] += metrics.get('clicks', 0)
                    unified_metrics['total_conversions'] += metrics.get('conversions', 0)
                    unified_metrics['total_spend'] += metrics.get('cost', 0)
        
        # Calculate aggregated metrics
        if unified_metrics['total_impressions'] > 0:
            unified_metrics['overall_ctr'] = (
                unified_metrics['total_clicks'] / unified_metrics['total_impressions']
            )
        
        if unified_metrics['total_clicks'] > 0:
            unified_metrics['overall_cvr'] = (
                unified_metrics['total_conversions'] / unified_metrics['total_clicks']
            )
        
        if unified_metrics['total_conversions'] > 0:
            unified_metrics['overall_cpa'] = (
                unified_metrics['total_spend'] / unified_metrics['total_conversions']
            )
        
        return unified_metrics
    
    async def optimize_budget_allocation(
        self,
        campaign_name: str,
        total_budget: float
    ) -> Dict[str, float]:
        """
        Optimize budget allocation based on performance
        
        Args:
            campaign_name: Campaign to optimize
            total_budget: Total budget to allocate
            
        Returns:
            Optimized budget per platform
        """
        # Get recent performance
        date_range = (datetime.now() - timedelta(days=7), datetime.now())
        performance = await self.get_unified_performance(campaign_name, date_range)
        
        platform_scores = {}
        
        # Calculate performance scores for each platform
        for platform, metrics in performance['platform_breakdown'].items():
            if metrics.get('cost', 0) > 0:
                # Calculate ROAS-like score
                conversions = metrics.get('conversions', 0)
                cost = metrics.get('cost', 1)
                score = conversions / cost
                platform_scores[platform] = score
        
        # Allocate budget proportionally to performance
        total_score = sum(platform_scores.values())
        
        if total_score > 0:
            optimized_allocation = {
                platform: (score / total_score) * total_budget
                for platform, score in platform_scores.items()
            }
        else:
            # Equal allocation if no performance data
            num_platforms = len(performance['platform_breakdown'])
            optimized_allocation = {
                platform: total_budget / num_platforms
                for platform in performance['platform_breakdown']
            }
        
        return optimized_allocation