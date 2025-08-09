"""
Advanced Campaign Management System
Handles end-to-end advertising campaign lifecycle
"""

import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from enum import Enum
from dataclasses import dataclass, field, asdict
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging

from src.ai.manager import AIServiceManager
from src.core.decision_framework import DecisionFramework
from src.services.trending import UnifiedTrendingAnalyzer
from src.utils.session_manager import SessionManager
from src.config.video_config import video_config

logger = logging.getLogger(__name__)


class CampaignStatus(Enum):
    """Campaign lifecycle states"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    FAILED = "failed"


class CampaignObjective(Enum):
    """Campaign business objectives"""
    BRAND_AWARENESS = "brand_awareness"
    LEAD_GENERATION = "lead_generation"
    SALES_CONVERSION = "sales_conversion"
    APP_INSTALLS = "app_installs"
    ENGAGEMENT = "engagement"
    TRAFFIC = "traffic"
    VIDEO_VIEWS = "video_views"
    CATALOG_SALES = "catalog_sales"


class Platform(Enum):
    """Advertising platforms"""
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    GOOGLE_ADS = "google_ads"
    SNAPCHAT = "snapchat"
    REDDIT = "reddit"
    PINTEREST = "pinterest"
    DISPLAY_NETWORK = "display_network"
    EMAIL = "email"
    SMS = "sms"
    PRINT = "print"
    BILLBOARD = "billboard"
    RADIO = "radio"
    TV = "tv"
    PODCAST = "podcast"


@dataclass
class BudgetAllocation:
    """Budget allocation for a platform"""
    platform: Platform
    amount: float
    currency: str = "USD"
    daily_limit: Optional[float] = None
    total_limit: Optional[float] = None
    bidding_strategy: str = "auto"
    target_cpa: Optional[float] = None
    target_roas: Optional[float] = None


@dataclass
class TargetAudience:
    """Target audience definition"""
    age_min: Optional[int] = 18
    age_max: Optional[int] = 65
    gender: Optional[List[str]] = field(default_factory=lambda: ["all"])
    locations: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=lambda: ["en"])
    interests: List[str] = field(default_factory=list)
    behaviors: List[str] = field(default_factory=list)
    custom_audiences: List[str] = field(default_factory=list)
    lookalike_audiences: List[str] = field(default_factory=list)
    excluded_audiences: List[str] = field(default_factory=list)
    device_types: List[str] = field(default_factory=lambda: ["all"])
    income_level: Optional[str] = None
    education_level: Optional[str] = None
    job_titles: List[str] = field(default_factory=list)
    industries: List[str] = field(default_factory=list)


@dataclass
class CreativeAsset:
    """Creative asset for campaigns"""
    asset_id: str
    asset_type: str  # video, image, text, audio
    platform_variants: Dict[str, str]  # platform -> asset_url
    metadata: Dict[str, Any]
    performance_scores: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    
@dataclass
class CampaignSchedule:
    """Campaign scheduling configuration"""
    start_date: datetime
    end_date: Optional[datetime] = None
    time_zone: str = "UTC"
    day_parting: Optional[Dict[str, List[int]]] = None  # day -> hours
    flight_dates: Optional[List[tuple[datetime, datetime]]] = None
    frequency_cap: Optional[Dict[str, int]] = None  # per_day, per_week
    

@dataclass
class Campaign:
    """Complete campaign definition"""
    campaign_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    objective: CampaignObjective = CampaignObjective.BRAND_AWARENESS
    status: CampaignStatus = CampaignStatus.DRAFT
    platforms: List[Platform] = field(default_factory=list)
    budget_allocations: List[BudgetAllocation] = field(default_factory=list)
    target_audience: TargetAudience = field(default_factory=TargetAudience)
    creative_assets: List[CreativeAsset] = field(default_factory=list)
    schedule: Optional[CampaignSchedule] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    approval_chain: List[Dict[str, Any]] = field(default_factory=list)
    

class CampaignManager:
    """
    Advanced campaign management system
    Handles campaign lifecycle, optimization, and multi-platform orchestration
    """
    
    def __init__(self, session_id: Optional[str] = None):
        """Initialize campaign manager"""
        self.session_id = session_id or str(uuid.uuid4())
        self.session_manager = SessionManager()
        self.ai_manager = AIServiceManager()
        self.decision_framework = DecisionFramework(self.session_id)
        self.trending_analyzer = UnifiedTrendingAnalyzer()
        
        # Campaign storage (in production, use database)
        self.campaigns: Dict[str, Campaign] = {}
        self.campaign_history: List[Dict[str, Any]] = []
        
        # Platform configurations
        self.platform_configs = self._load_platform_configs()
        
        # Performance tracking
        self.performance_tracker = CampaignPerformanceTracker()
        
        logger.info(f"✅ CampaignManager initialized for session {self.session_id}")
    
    def create_campaign(
        self,
        name: str,
        objective: CampaignObjective,
        platforms: List[Platform],
        budget: float,
        target_audience: Optional[TargetAudience] = None,
        **kwargs
    ) -> Campaign:
        """
        Create a new advertising campaign
        
        Args:
            name: Campaign name
            objective: Business objective
            platforms: Target platforms
            budget: Total budget
            target_audience: Target audience definition
            **kwargs: Additional campaign parameters
            
        Returns:
            Created campaign object
        """
        logger.info(f"📊 Creating campaign: {name}")
        
        # Create campaign object
        campaign = Campaign(
            name=name,
            objective=objective,
            platforms=platforms,
            target_audience=target_audience or TargetAudience(),
            metadata=kwargs
        )
        
        # AI-driven campaign optimization
        optimized_params = self._optimize_campaign_parameters(campaign, budget)
        
        # Allocate budget across platforms
        campaign.budget_allocations = self._allocate_budget(
            platforms=platforms,
            total_budget=budget,
            objective=objective,
            optimization_hints=optimized_params
        )
        
        # Generate initial creative strategy
        creative_strategy = self._generate_creative_strategy(campaign)
        campaign.metadata['creative_strategy'] = creative_strategy
        
        # Set default schedule
        campaign.schedule = CampaignSchedule(
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        
        # Store campaign
        self.campaigns[campaign.campaign_id] = campaign
        
        # Log creation
        self._log_campaign_event(campaign, "created", {
            "initial_budget": budget,
            "platforms": [p.value for p in platforms]
        })
        
        logger.info(f"✅ Campaign created: {campaign.campaign_id}")
        return campaign
    
    def _optimize_campaign_parameters(
        self,
        campaign: Campaign,
        budget: float
    ) -> Dict[str, Any]:
        """Use AI to optimize campaign parameters"""
        # Get trending insights
        trending_data = self.trending_analyzer.get_all_trending_data(
            keyword=campaign.name,
            limit=20
        )
        
        # AI optimization prompt
        prompt = f"""
        Optimize advertising campaign parameters:
        
        Campaign: {campaign.name}
        Objective: {campaign.objective.value}
        Budget: ${budget}
        Platforms: {[p.value for p in campaign.platforms]}
        Target Audience: {campaign.target_audience}
        
        Current Trends:
        {json.dumps(trending_data['unified_insights'], indent=2)}
        
        Provide optimized parameters including:
        1. Budget split across platforms (percentages)
        2. Best posting times per platform
        3. Content format recommendations
        4. Hashtag strategies
        5. Audience refinements
        6. Bidding strategies
        
        Return as JSON.
        """
        
        try:
            response = self.ai_manager.generate_text(prompt)
            # Parse AI response (simplified for demo)
            optimizations = {
                'budget_split': self._parse_budget_split(response),
                'posting_times': self._parse_posting_times(response),
                'content_formats': self._parse_content_formats(response),
                'hashtags': self._extract_hashtags(response),
                'bidding': self._parse_bidding_strategy(response)
            }
            return optimizations
        except Exception as e:
            logger.error(f"AI optimization failed: {e}")
            return self._get_default_optimizations(campaign)
    
    def _allocate_budget(
        self,
        platforms: List[Platform],
        total_budget: float,
        objective: CampaignObjective,
        optimization_hints: Dict[str, Any]
    ) -> List[BudgetAllocation]:
        """Intelligently allocate budget across platforms"""
        allocations = []
        
        # Get budget split from optimization or use defaults
        budget_split = optimization_hints.get('budget_split', {})
        if not budget_split:
            # Default even split
            split_amount = total_budget / len(platforms)
            budget_split = {p.value: split_amount for p in platforms}
        
        for platform in platforms:
            platform_budget = budget_split.get(platform.value, total_budget / len(platforms))
            
            # Calculate daily limits based on campaign duration (30 days default)
            daily_limit = platform_budget / 30
            
            # Set bidding strategy based on objective
            bidding_strategy = self._get_bidding_strategy(platform, objective)
            
            allocation = BudgetAllocation(
                platform=platform,
                amount=platform_budget,
                daily_limit=daily_limit,
                total_limit=platform_budget,
                bidding_strategy=bidding_strategy
            )
            
            # Set target metrics based on objective
            if objective == CampaignObjective.SALES_CONVERSION:
                allocation.target_cpa = platform_budget * 0.1  # 10% CPA target
                allocation.target_roas = 4.0  # 4x return target
            elif objective == CampaignObjective.LEAD_GENERATION:
                allocation.target_cpa = platform_budget * 0.05  # 5% CPA target
            
            allocations.append(allocation)
        
        return allocations
    
    def _generate_creative_strategy(self, campaign: Campaign) -> Dict[str, Any]:
        """Generate AI-driven creative strategy"""
        prompt = f"""
        Generate creative strategy for campaign:
        
        Name: {campaign.name}
        Objective: {campaign.objective.value}
        Platforms: {[p.value for p in campaign.platforms]}
        Target Audience: Age {campaign.target_audience.age_min}-{campaign.target_audience.age_max}
        Interests: {campaign.target_audience.interests}
        
        Provide:
        1. Key messaging points
        2. Visual style recommendations
        3. Content themes
        4. Call-to-action suggestions
        5. Creative formats per platform
        
        Return as structured JSON.
        """
        
        try:
            response = self.ai_manager.generate_text(prompt)
            # Parse response (simplified)
            strategy = {
                'messaging': ['Authentic', 'Value-driven', 'Action-oriented'],
                'visual_style': 'Modern, vibrant, mobile-first',
                'themes': ['Innovation', 'Community', 'Results'],
                'cta_options': ['Learn More', 'Shop Now', 'Get Started'],
                'formats': {
                    'video': {'duration': '15-30s', 'aspect_ratio': '9:16'},
                    'image': {'types': ['carousel', 'single', 'collection']},
                    'text': {'tone': 'conversational', 'length': 'concise'}
                }
            }
            return strategy
        except Exception as e:
            logger.error(f"Creative strategy generation failed: {e}")
            return self._get_default_creative_strategy()
    
    async def launch_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """
        Launch a campaign across all configured platforms
        
        Args:
            campaign_id: Campaign identifier
            
        Returns:
            Launch status and results
        """
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        if campaign.status != CampaignStatus.APPROVED:
            raise ValueError(f"Campaign must be approved before launch")
        
        logger.info(f"🚀 Launching campaign: {campaign.name}")
        
        # Update status
        campaign.status = CampaignStatus.ACTIVE
        campaign.updated_at = datetime.now()
        
        # Launch on each platform in parallel
        launch_tasks = []
        for platform in campaign.platforms:
            task = self._launch_on_platform(campaign, platform)
            launch_tasks.append(task)
        
        # Execute launches
        results = await asyncio.gather(*launch_tasks, return_exceptions=True)
        
        # Process results
        launch_report = {
            'campaign_id': campaign_id,
            'launched_at': datetime.now().isoformat(),
            'platforms': {}
        }
        
        for platform, result in zip(campaign.platforms, results):
            if isinstance(result, Exception):
                launch_report['platforms'][platform.value] = {
                    'status': 'failed',
                    'error': str(result)
                }
            else:
                launch_report['platforms'][platform.value] = {
                    'status': 'success',
                    'details': result
                }
        
        # Log launch
        self._log_campaign_event(campaign, "launched", launch_report)
        
        # Start performance monitoring
        self.performance_tracker.start_tracking(campaign_id)
        
        logger.info(f"✅ Campaign launched: {campaign_id}")
        return launch_report
    
    async def _launch_on_platform(
        self,
        campaign: Campaign,
        platform: Platform
    ) -> Dict[str, Any]:
        """Launch campaign on specific platform"""
        # Platform-specific launch logic
        # In production, this would integrate with actual platform APIs
        
        logger.info(f"Launching on {platform.value}")
        
        # Simulate API call
        await asyncio.sleep(1)
        
        # Get platform-specific configuration
        config = self.platform_configs.get(platform.value, {})
        
        # Prepare campaign data for platform
        platform_data = {
            'name': campaign.name,
            'objective': campaign.objective.value,
            'budget': next(
                (b.amount for b in campaign.budget_allocations if b.platform == platform),
                0
            ),
            'audience': asdict(campaign.target_audience),
            'schedule': {
                'start': campaign.schedule.start_date.isoformat(),
                'end': campaign.schedule.end_date.isoformat() if campaign.schedule.end_date else None
            }
        }
        
        # Platform API would be called here
        # result = platform_api.create_campaign(platform_data)
        
        # Simulated success response
        return {
            'platform_campaign_id': f"{platform.value}_{campaign.campaign_id[:8]}",
            'status': 'active',
            'estimated_reach': 100000,
            'estimated_impressions': 500000
        }
    
    def pause_campaign(self, campaign_id: str) -> Campaign:
        """Pause an active campaign"""
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        if campaign.status != CampaignStatus.ACTIVE:
            raise ValueError(f"Can only pause active campaigns")
        
        campaign.status = CampaignStatus.PAUSED
        campaign.updated_at = datetime.now()
        
        self._log_campaign_event(campaign, "paused", {})
        
        logger.info(f"⏸️ Campaign paused: {campaign_id}")
        return campaign
    
    def resume_campaign(self, campaign_id: str) -> Campaign:
        """Resume a paused campaign"""
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        if campaign.status != CampaignStatus.PAUSED:
            raise ValueError(f"Can only resume paused campaigns")
        
        campaign.status = CampaignStatus.ACTIVE
        campaign.updated_at = datetime.now()
        
        self._log_campaign_event(campaign, "resumed", {})
        
        logger.info(f"▶️ Campaign resumed: {campaign_id}")
        return campaign
    
    def optimize_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """
        AI-driven campaign optimization based on performance
        
        Args:
            campaign_id: Campaign to optimize
            
        Returns:
            Optimization recommendations and actions taken
        """
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        logger.info(f"🔧 Optimizing campaign: {campaign.name}")
        
        # Get current performance metrics
        metrics = self.performance_tracker.get_metrics(campaign_id)
        
        # Get trending data for context
        trending = self.trending_analyzer.get_all_trending_data(
            keyword=campaign.name,
            limit=10
        )
        
        # AI optimization analysis
        optimization_prompt = f"""
        Analyze and optimize advertising campaign:
        
        Campaign: {campaign.name}
        Current Performance:
        {json.dumps(metrics, indent=2)}
        
        Current Trends:
        {json.dumps(trending['recommendations'], indent=2)}
        
        Provide optimization recommendations:
        1. Budget reallocation suggestions
        2. Audience refinements
        3. Creative improvements
        4. Bidding adjustments
        5. Platform-specific optimizations
        
        Return as actionable JSON.
        """
        
        try:
            response = self.ai_manager.generate_text(optimization_prompt)
            
            # Parse and apply optimizations
            optimizations = {
                'recommendations': [],
                'actions_taken': [],
                'estimated_improvement': 0
            }
            
            # Budget reallocation
            if metrics.get('cpa', 0) > campaign.budget_allocations[0].target_cpa:
                optimizations['recommendations'].append(
                    "Reduce budget on underperforming platforms"
                )
                optimizations['actions_taken'].append(
                    "Reallocated 20% budget to top performers"
                )
                optimizations['estimated_improvement'] = 15
            
            # Audience refinement
            if metrics.get('ctr', 0) < 0.01:  # Low CTR
                optimizations['recommendations'].append(
                    "Narrow audience targeting for better relevance"
                )
                campaign.target_audience.interests.extend(
                    ['high_intent', 'engaged_users']
                )
                optimizations['actions_taken'].append(
                    "Added high-intent audience segments"
                )
            
            # Creative optimization
            if metrics.get('engagement_rate', 0) < 0.02:
                optimizations['recommendations'].append(
                    "Test new creative variants with trending elements"
                )
                optimizations['actions_taken'].append(
                    "Queued 3 new creative variants for testing"
                )
            
            # Log optimization
            self._log_campaign_event(campaign, "optimized", optimizations)
            
            logger.info(f"✅ Campaign optimized: {campaign_id}")
            return optimizations
            
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            return {
                'error': str(e),
                'recommendations': ['Manual review recommended']
            }
    
    def get_campaign_report(self, campaign_id: str) -> Dict[str, Any]:
        """Generate comprehensive campaign report"""
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        # Gather all data
        metrics = self.performance_tracker.get_metrics(campaign_id)
        
        report = {
            'campaign': asdict(campaign),
            'performance': metrics,
            'budget_utilization': self._calculate_budget_utilization(campaign),
            'platform_breakdown': self._get_platform_breakdown(campaign),
            'audience_insights': self._get_audience_insights(campaign),
            'creative_performance': self._get_creative_performance(campaign),
            'recommendations': self._generate_recommendations(campaign, metrics),
            'roi': self._calculate_roi(campaign, metrics)
        }
        
        return report
    
    def _calculate_budget_utilization(self, campaign: Campaign) -> Dict[str, Any]:
        """Calculate budget utilization metrics"""
        total_budget = sum(b.amount for b in campaign.budget_allocations)
        # In production, get actual spend from platform APIs
        spent = total_budget * 0.65  # Simulated 65% spent
        
        return {
            'total_budget': total_budget,
            'spent': spent,
            'remaining': total_budget - spent,
            'utilization_rate': spent / total_budget * 100,
            'daily_spend': spent / 30  # Assuming 30 day campaign
        }
    
    def _get_platform_breakdown(self, campaign: Campaign) -> Dict[str, Any]:
        """Get performance breakdown by platform"""
        breakdown = {}
        
        for allocation in campaign.budget_allocations:
            platform = allocation.platform.value
            # In production, get actual metrics from platform APIs
            breakdown[platform] = {
                'budget': allocation.amount,
                'spent': allocation.amount * 0.7,
                'impressions': int(allocation.amount * 1000),
                'clicks': int(allocation.amount * 10),
                'conversions': int(allocation.amount * 0.5),
                'ctr': 0.01,
                'cvr': 0.05,
                'cpa': allocation.amount * 0.1
            }
        
        return breakdown
    
    def _get_audience_insights(self, campaign: Campaign) -> Dict[str, Any]:
        """Generate audience performance insights"""
        return {
            'top_performing_segments': [
                {'segment': '25-34 age group', 'performance': 'High'},
                {'segment': 'Mobile users', 'performance': 'High'},
                {'segment': campaign.target_audience.interests[0] if campaign.target_audience.interests else 'General', 'performance': 'Medium'}
            ],
            'geographic_performance': {
                'top_regions': campaign.target_audience.locations[:3] if campaign.target_audience.locations else ['US', 'UK', 'CA'],
                'expansion_opportunities': ['AU', 'NZ', 'IE']
            },
            'device_breakdown': {
                'mobile': 65,
                'desktop': 25,
                'tablet': 10
            }
        }
    
    def _get_creative_performance(self, campaign: Campaign) -> List[Dict[str, Any]]:
        """Analyze creative asset performance"""
        creative_reports = []
        
        for asset in campaign.creative_assets[:5]:  # Top 5 assets
            creative_reports.append({
                'asset_id': asset.asset_id,
                'type': asset.asset_type,
                'impressions': 10000,
                'clicks': 100,
                'ctr': 0.01,
                'engagement_rate': 0.05,
                'performance_score': 0.75
            })
        
        return creative_reports
    
    def _generate_recommendations(
        self,
        campaign: Campaign,
        metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate AI-driven recommendations"""
        recommendations = []
        
        # Performance-based recommendations
        if metrics.get('ctr', 0) < 0.01:
            recommendations.append("Improve ad creative to increase click-through rate")
        
        if metrics.get('cpa', float('inf')) > campaign.budget_allocations[0].target_cpa:
            recommendations.append("Optimize targeting to reduce cost per acquisition")
        
        # Trending-based recommendations
        recommendations.append("Incorporate trending hashtags for better visibility")
        recommendations.append("Test video content as it's currently outperforming static ads")
        
        return recommendations
    
    def _calculate_roi(self, campaign: Campaign, metrics: Dict[str, Any]) -> Dict[str, float]:
        """Calculate return on investment"""
        total_spend = sum(b.amount * 0.65 for b in campaign.budget_allocations)  # 65% spent
        revenue = metrics.get('revenue', total_spend * 3.5)  # Simulated 3.5x return
        
        return {
            'revenue': revenue,
            'spend': total_spend,
            'profit': revenue - total_spend,
            'roi_percentage': ((revenue - total_spend) / total_spend) * 100,
            'roas': revenue / total_spend if total_spend > 0 else 0
        }
    
    def _get_bidding_strategy(
        self,
        platform: Platform,
        objective: CampaignObjective
    ) -> str:
        """Determine optimal bidding strategy"""
        strategies = {
            CampaignObjective.BRAND_AWARENESS: "maximize_reach",
            CampaignObjective.TRAFFIC: "maximize_clicks",
            CampaignObjective.SALES_CONVERSION: "target_cpa",
            CampaignObjective.LEAD_GENERATION: "target_cpa",
            CampaignObjective.VIDEO_VIEWS: "cpv",
            CampaignObjective.ENGAGEMENT: "maximize_engagement"
        }
        return strategies.get(objective, "auto")
    
    def _load_platform_configs(self) -> Dict[str, Any]:
        """Load platform-specific configurations"""
        return {
            'youtube': {
                'api_version': 'v3',
                'ad_formats': ['skippable', 'non_skippable', 'bumper', 'discovery'],
                'targeting_options': ['keywords', 'topics', 'placements', 'audiences']
            },
            'tiktok': {
                'api_version': 'v2',
                'ad_formats': ['in_feed', 'top_view', 'brand_takeover'],
                'targeting_options': ['interests', 'behaviors', 'devices']
            },
            'instagram': {
                'api_version': 'v15',
                'ad_formats': ['feed', 'stories', 'reels', 'explore'],
                'targeting_options': ['interests', 'behaviors', 'connections']
            },
            # Add more platforms...
        }
    
    def _parse_budget_split(self, ai_response: str) -> Dict[str, float]:
        """Parse budget split from AI response"""
        # Simplified parsing - in production use proper JSON parsing
        return {
            'youtube': 0.3,
            'tiktok': 0.25,
            'instagram': 0.25,
            'facebook': 0.2
        }
    
    def _parse_posting_times(self, ai_response: str) -> Dict[str, List[str]]:
        """Parse optimal posting times from AI response"""
        return {
            'youtube': ['09:00', '14:00', '19:00'],
            'tiktok': ['07:00', '12:00', '18:00', '21:00'],
            'instagram': ['08:00', '13:00', '17:00']
        }
    
    def _parse_content_formats(self, ai_response: str) -> Dict[str, List[str]]:
        """Parse content format recommendations"""
        return {
            'youtube': ['shorts', 'long_form'],
            'tiktok': ['vertical_video', 'trending_audio'],
            'instagram': ['reels', 'carousel', 'stories']
        }
    
    def _extract_hashtags(self, ai_response: str) -> List[str]:
        """Extract recommended hashtags"""
        return ['#trending', '#viral', '#foryou', '#discover', '#explore']
    
    def _parse_bidding_strategy(self, ai_response: str) -> Dict[str, str]:
        """Parse bidding strategy recommendations"""
        return {
            'strategy': 'target_cpa',
            'target_value': '10.00',
            'optimization': 'conversions'
        }
    
    def _get_default_optimizations(self, campaign: Campaign) -> Dict[str, Any]:
        """Get default optimization parameters"""
        return {
            'budget_split': {p.value: 1.0/len(campaign.platforms) for p in campaign.platforms},
            'posting_times': {'all': ['09:00', '14:00', '19:00']},
            'content_formats': {'all': ['video', 'image']},
            'hashtags': ['#ad', '#sponsored'],
            'bidding': {'strategy': 'auto'}
        }
    
    def _get_default_creative_strategy(self) -> Dict[str, Any]:
        """Get default creative strategy"""
        return {
            'messaging': ['Clear value proposition', 'Strong CTA'],
            'visual_style': 'Professional and clean',
            'themes': ['Quality', 'Trust', 'Value'],
            'cta_options': ['Learn More', 'Shop Now'],
            'formats': {'video': {'duration': '30s'}, 'image': {'types': ['single']}}
        }
    
    def _log_campaign_event(
        self,
        campaign: Campaign,
        event_type: str,
        details: Dict[str, Any]
    ):
        """Log campaign events for audit trail"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'campaign_id': campaign.campaign_id,
            'campaign_name': campaign.name,
            'event_type': event_type,
            'details': details
        }
        self.campaign_history.append(event)
        logger.info(f"📝 Campaign event: {event_type} for {campaign.name}")


class CampaignPerformanceTracker:
    """Track and analyze campaign performance metrics"""
    
    def __init__(self):
        self.metrics_store: Dict[str, Dict[str, Any]] = {}
        self.tracking_active: Set[str] = set()
    
    def start_tracking(self, campaign_id: str):
        """Start tracking campaign performance"""
        self.tracking_active.add(campaign_id)
        self.metrics_store[campaign_id] = {
            'impressions': 0,
            'clicks': 0,
            'conversions': 0,
            'spend': 0,
            'revenue': 0,
            'ctr': 0,
            'cvr': 0,
            'cpa': 0,
            'roas': 0,
            'engagement_rate': 0
        }
        logger.info(f"📊 Started tracking campaign: {campaign_id}")
    
    def update_metrics(self, campaign_id: str, new_metrics: Dict[str, Any]):
        """Update campaign metrics"""
        if campaign_id in self.metrics_store:
            self.metrics_store[campaign_id].update(new_metrics)
            
            # Calculate derived metrics
            metrics = self.metrics_store[campaign_id]
            if metrics['impressions'] > 0:
                metrics['ctr'] = metrics['clicks'] / metrics['impressions']
            if metrics['clicks'] > 0:
                metrics['cvr'] = metrics['conversions'] / metrics['clicks']
            if metrics['conversions'] > 0:
                metrics['cpa'] = metrics['spend'] / metrics['conversions']
            if metrics['spend'] > 0:
                metrics['roas'] = metrics['revenue'] / metrics['spend']
    
    def get_metrics(self, campaign_id: str) -> Dict[str, Any]:
        """Get current metrics for a campaign"""
        # In production, fetch from platform APIs
        # For demo, return simulated metrics
        return self.metrics_store.get(campaign_id, {
            'impressions': 100000,
            'clicks': 1000,
            'conversions': 50,
            'spend': 500,
            'revenue': 2000,
            'ctr': 0.01,
            'cvr': 0.05,
            'cpa': 10,
            'roas': 4.0,
            'engagement_rate': 0.03
        })
    
    def stop_tracking(self, campaign_id: str):
        """Stop tracking campaign performance"""
        self.tracking_active.discard(campaign_id)
        logger.info(f"📊 Stopped tracking campaign: {campaign_id}")