"""
Advanced Workflow Automation Engine
Orchestrates end-to-end advertising workflows with AI-driven automation
"""

import uuid
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import defaultdict
import schedule
import threading

from src.services.trending import UnifiedTrendingAnalyzer
from src.advertising.campaign_management.campaign_manager import CampaignManager, CampaignObjective, Platform
from src.advertising.platforms.platform_integrations import UnifiedAdPlatformManager
from src.advertising.analytics.analytics_dashboard import AnalyticsDashboard, MetricType
from src.ai.manager import AIServiceManager
from src.core.decision_framework import DecisionFramework

logger = logging.getLogger(__name__)


class TriggerType(Enum):
    """Types of workflow triggers"""
    SCHEDULED = "scheduled"
    EVENT_BASED = "event_based"
    PERFORMANCE_BASED = "performance_based"
    MANUAL = "manual"
    API_WEBHOOK = "api_webhook"
    TRENDING = "trending"
    BUDGET_THRESHOLD = "budget_threshold"
    CONVERSION_GOAL = "conversion_goal"


class ActionType(Enum):
    """Types of workflow actions"""
    CREATE_CAMPAIGN = "create_campaign"
    UPDATE_CAMPAIGN = "update_campaign"
    PAUSE_CAMPAIGN = "pause_campaign"
    RESUME_CAMPAIGN = "resume_campaign"
    ADJUST_BUDGET = "adjust_budget"
    GENERATE_CREATIVE = "generate_creative"
    A_B_TEST = "a_b_test"
    OPTIMIZE_TARGETING = "optimize_targeting"
    SEND_NOTIFICATION = "send_notification"
    EXPORT_REPORT = "export_report"
    SCALE_CAMPAIGN = "scale_campaign"
    CLONE_CAMPAIGN = "clone_campaign"


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


@dataclass
class WorkflowTrigger:
    """Workflow trigger configuration"""
    trigger_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trigger_type: TriggerType = TriggerType.MANUAL
    conditions: Dict[str, Any] = field(default_factory=dict)
    schedule: Optional[str] = None  # Cron expression
    enabled: bool = True
    last_triggered: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowAction:
    """Workflow action configuration"""
    action_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    action_type: ActionType = ActionType.CREATE_CAMPAIGN
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)  # Action IDs that must complete first
    retry_config: Dict[str, int] = field(default_factory=lambda: {"max_retries": 3, "retry_delay": 60})
    timeout: int = 300  # seconds
    on_success: Optional[str] = None  # Next action ID
    on_failure: Optional[str] = None  # Fallback action ID


@dataclass
class WorkflowTemplate:
    """Reusable workflow template"""
    template_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    triggers: List[WorkflowTrigger] = field(default_factory=list)
    actions: List[WorkflowAction] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class WorkflowExecution:
    """Workflow execution instance"""
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str = ""
    status: WorkflowStatus = WorkflowStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    trigger_data: Dict[str, Any] = field(default_factory=dict)
    action_results: Dict[str, Any] = field(default_factory=dict)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


class WorkflowAutomationEngine:
    """
    Comprehensive workflow automation engine for advertising operations
    Handles triggers, actions, and complex workflow orchestration
    """
    
    def __init__(self):
        """Initialize workflow automation engine"""
        self.workflows: Dict[str, WorkflowTemplate] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.active_schedules: Dict[str, Any] = {}
        
        # Initialize services
        self.campaign_manager = CampaignManager()
        self.platform_manager = UnifiedAdPlatformManager()
        self.analytics = AnalyticsDashboard()
        self.trending_analyzer = UnifiedTrendingAnalyzer()
        self.ai_manager = AIServiceManager()
        self.decision_framework = DecisionFramework(str(uuid.uuid4()))
        
        # Action handlers
        self.action_handlers = self._register_action_handlers()
        
        # Trigger monitors
        self.trigger_monitors = {}
        self.monitoring_active = False
        
        # Event bus for inter-workflow communication
        self.event_bus = defaultdict(list)
        
        # Start background monitoring
        self.monitoring_thread = None
        
        # Initialize pre-built workflows
        self._init_prebuilt_workflows()
        
        logger.info("✅ WorkflowAutomationEngine initialized")
    
    def _register_action_handlers(self) -> Dict[ActionType, Callable]:
        """Register action handlers"""
        return {
            ActionType.CREATE_CAMPAIGN: self._action_create_campaign,
            ActionType.UPDATE_CAMPAIGN: self._action_update_campaign,
            ActionType.PAUSE_CAMPAIGN: self._action_pause_campaign,
            ActionType.RESUME_CAMPAIGN: self._action_resume_campaign,
            ActionType.ADJUST_BUDGET: self._action_adjust_budget,
            ActionType.GENERATE_CREATIVE: self._action_generate_creative,
            ActionType.A_B_TEST: self._action_ab_test,
            ActionType.OPTIMIZE_TARGETING: self._action_optimize_targeting,
            ActionType.SEND_NOTIFICATION: self._action_send_notification,
            ActionType.EXPORT_REPORT: self._action_export_report,
            ActionType.SCALE_CAMPAIGN: self._action_scale_campaign,
            ActionType.CLONE_CAMPAIGN: self._action_clone_campaign
        }
    
    def _init_prebuilt_workflows(self):
        """Initialize pre-built workflow templates"""
        # Viral Content Workflow
        self.create_workflow(WorkflowTemplate(
            name="Viral Content Hunter",
            description="Automatically creates campaigns when trending topics are detected",
            triggers=[
                WorkflowTrigger(
                    trigger_type=TriggerType.TRENDING,
                    conditions={
                        "viral_score_threshold": 0.8,
                        "platforms": ["tiktok", "instagram"],
                        "check_interval": 3600  # Check every hour
                    }
                )
            ],
            actions=[
                WorkflowAction(
                    action_type=ActionType.GENERATE_CREATIVE,
                    parameters={"use_trending": True, "format": "video"}
                ),
                WorkflowAction(
                    action_type=ActionType.CREATE_CAMPAIGN,
                    parameters={
                        "objective": "video_views",
                        "budget": 500,
                        "duration": 3
                    },
                    dependencies=["0"]  # Depends on creative generation
                )
            ]
        ))
        
        # Performance Optimization Workflow
        self.create_workflow(WorkflowTemplate(
            name="Performance Auto-Optimizer",
            description="Continuously optimizes campaigns based on performance",
            triggers=[
                WorkflowTrigger(
                    trigger_type=TriggerType.SCHEDULED,
                    schedule="0 */6 * * *",  # Every 6 hours
                    conditions={"min_campaign_age_hours": 24}
                )
            ],
            actions=[
                WorkflowAction(
                    action_type=ActionType.OPTIMIZE_TARGETING,
                    parameters={"optimization_goal": "cpa"}
                ),
                WorkflowAction(
                    action_type=ActionType.ADJUST_BUDGET,
                    parameters={"strategy": "performance_based"},
                    dependencies=["0"]
                )
            ]
        ))
        
        # A/B Testing Workflow
        self.create_workflow(WorkflowTemplate(
            name="Creative A/B Tester",
            description="Automatically runs A/B tests on new creatives",
            triggers=[
                WorkflowTrigger(
                    trigger_type=TriggerType.EVENT_BASED,
                    conditions={"event": "new_creative_uploaded"}
                )
            ],
            actions=[
                WorkflowAction(
                    action_type=ActionType.A_B_TEST,
                    parameters={
                        "test_duration_hours": 48,
                        "traffic_split": [50, 50],
                        "success_metric": "ctr"
                    }
                )
            ]
        ))
    
    def create_workflow(self, template: WorkflowTemplate) -> str:
        """
        Create a new workflow template
        
        Args:
            template: Workflow template configuration
            
        Returns:
            Workflow ID
        """
        workflow_id = template.template_id
        self.workflows[workflow_id] = template
        
        # Setup triggers
        for trigger in template.triggers:
            self._setup_trigger(workflow_id, trigger)
        
        logger.info(f"📋 Workflow created: {template.name} ({workflow_id})")
        return workflow_id
    
    def _setup_trigger(self, workflow_id: str, trigger: WorkflowTrigger):
        """Setup workflow trigger"""
        if trigger.trigger_type == TriggerType.SCHEDULED:
            self._setup_scheduled_trigger(workflow_id, trigger)
        elif trigger.trigger_type == TriggerType.TRENDING:
            self._setup_trending_trigger(workflow_id, trigger)
        elif trigger.trigger_type == TriggerType.PERFORMANCE_BASED:
            self._setup_performance_trigger(workflow_id, trigger)
        elif trigger.trigger_type == TriggerType.EVENT_BASED:
            self._setup_event_trigger(workflow_id, trigger)
    
    def _setup_scheduled_trigger(self, workflow_id: str, trigger: WorkflowTrigger):
        """Setup scheduled trigger using cron expression"""
        if trigger.schedule:
            # Parse cron expression and schedule
            schedule_job = schedule.every().day.at("09:00").do(
                lambda: asyncio.run(self.execute_workflow(workflow_id, trigger_data={"trigger": "scheduled"}))
            )
            self.active_schedules[trigger.trigger_id] = schedule_job
            logger.info(f"⏰ Scheduled trigger set for workflow {workflow_id}")
    
    def _setup_trending_trigger(self, workflow_id: str, trigger: WorkflowTrigger):
        """Setup trending detection trigger"""
        async def monitor_trends():
            while trigger.enabled:
                try:
                    # Get trending data
                    trending_data = self.trending_analyzer.get_all_trending_data(limit=10)
                    
                    # Check viral score threshold
                    for platform, data in trending_data.get('platforms', {}).items():
                        if platform in trigger.conditions.get('platforms', []):
                            # Calculate viral score
                            viral_score = self._calculate_viral_score(data)
                            
                            if viral_score >= trigger.conditions.get('viral_score_threshold', 0.8):
                                # Trigger workflow
                                await self.execute_workflow(workflow_id, trigger_data={
                                    "trigger": "trending",
                                    "platform": platform,
                                    "viral_score": viral_score,
                                    "trending_data": data
                                })
                                trigger.last_triggered = datetime.now()
                    
                    # Wait for next check
                    await asyncio.sleep(trigger.conditions.get('check_interval', 3600))
                    
                except Exception as e:
                    logger.error(f"Trending monitor error: {e}")
                    await asyncio.sleep(60)
        
        # Start monitoring in background
        self.trigger_monitors[trigger.trigger_id] = asyncio.create_task(monitor_trends())
        logger.info(f"📈 Trending trigger set for workflow {workflow_id}")
    
    def _setup_performance_trigger(self, workflow_id: str, trigger: WorkflowTrigger):
        """Setup performance-based trigger"""
        async def monitor_performance():
            while trigger.enabled:
                try:
                    # Get performance metrics
                    metrics = self.analytics.get_metrics(
                        metric_types=[MetricType.CPA, MetricType.ROAS],
                        time_range=(datetime.now() - timedelta(hours=24), datetime.now())
                    )
                    
                    # Check performance conditions
                    if self._check_performance_conditions(metrics, trigger.conditions):
                        await self.execute_workflow(workflow_id, trigger_data={
                            "trigger": "performance",
                            "metrics": metrics.to_dict()
                        })
                        trigger.last_triggered = datetime.now()
                    
                    await asyncio.sleep(trigger.conditions.get('check_interval', 1800))
                    
                except Exception as e:
                    logger.error(f"Performance monitor error: {e}")
                    await asyncio.sleep(60)
        
        self.trigger_monitors[trigger.trigger_id] = asyncio.create_task(monitor_performance())
        logger.info(f"📊 Performance trigger set for workflow {workflow_id}")
    
    def _setup_event_trigger(self, workflow_id: str, trigger: WorkflowTrigger):
        """Setup event-based trigger"""
        event_name = trigger.conditions.get('event', 'default')
        self.event_bus[event_name].append((workflow_id, trigger))
        logger.info(f"🎯 Event trigger set for workflow {workflow_id} on event: {event_name}")
    
    async def execute_workflow(
        self,
        workflow_id: str,
        trigger_data: Optional[Dict[str, Any]] = None,
        variables: Optional[Dict[str, Any]] = None
    ) -> WorkflowExecution:
        """
        Execute a workflow
        
        Args:
            workflow_id: Workflow to execute
            trigger_data: Data from trigger
            variables: Variable overrides
            
        Returns:
            Workflow execution record
        """
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        logger.info(f"🚀 Executing workflow: {workflow.name}")
        
        # Create execution record
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            status=WorkflowStatus.RUNNING,
            started_at=datetime.now(),
            trigger_data=trigger_data or {}
        )
        
        self.executions[execution.execution_id] = execution
        
        # Merge variables
        workflow_variables = {**workflow.variables, **(variables or {})}
        
        # Execute actions in dependency order
        action_queue = self._build_action_queue(workflow.actions)
        completed_actions = set()
        
        for action in action_queue:
            # Check dependencies
            if all(dep in completed_actions for dep in action.dependencies):
                try:
                    # Execute action
                    result = await self._execute_action(
                        action,
                        workflow_variables,
                        execution
                    )
                    
                    execution.action_results[action.action_id] = result
                    completed_actions.add(action.action_id)
                    
                    # Handle success path
                    if action.on_success:
                        # Queue next action
                        pass
                    
                except Exception as e:
                    logger.error(f"Action {action.action_id} failed: {e}")
                    execution.errors.append({
                        "action_id": action.action_id,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Handle failure path
                    if action.on_failure:
                        # Execute fallback action
                        pass
                    
                    # Retry logic
                    if action.retry_config['max_retries'] > 0:
                        await self._retry_action(action, workflow_variables, execution)
        
        # Update execution status
        execution.completed_at = datetime.now()
        execution.status = WorkflowStatus.COMPLETED if not execution.errors else WorkflowStatus.FAILED
        
        # Calculate execution metrics
        execution.metrics = {
            "duration_seconds": (execution.completed_at - execution.started_at).total_seconds(),
            "actions_executed": len(completed_actions),
            "actions_failed": len(execution.errors)
        }
        
        logger.info(f"✅ Workflow completed: {workflow.name} ({execution.status.value})")
        return execution
    
    def _build_action_queue(self, actions: List[WorkflowAction]) -> List[WorkflowAction]:
        """Build action execution queue respecting dependencies"""
        # Simple topological sort for dependency resolution
        queue = []
        visited = set()
        
        def visit(action: WorkflowAction):
            if action.action_id in visited:
                return
            
            visited.add(action.action_id)
            
            # Visit dependencies first
            for dep_id in action.dependencies:
                dep_action = next((a for a in actions if a.action_id == dep_id), None)
                if dep_action:
                    visit(dep_action)
            
            queue.append(action)
        
        for action in actions:
            visit(action)
        
        return queue
    
    async def _execute_action(
        self,
        action: WorkflowAction,
        variables: Dict[str, Any],
        execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Execute a single workflow action"""
        logger.info(f"⚡ Executing action: {action.action_type.value}")
        
        # Get handler
        handler = self.action_handlers.get(action.action_type)
        if not handler:
            raise ValueError(f"No handler for action type: {action.action_type}")
        
        # Substitute variables in parameters
        parameters = self._substitute_variables(action.parameters, variables)
        
        # Execute with timeout
        try:
            result = await asyncio.wait_for(
                handler(parameters, execution),
                timeout=action.timeout
            )
            return result
        except asyncio.TimeoutError:
            raise Exception(f"Action timed out after {action.timeout} seconds")
    
    async def _retry_action(
        self,
        action: WorkflowAction,
        variables: Dict[str, Any],
        execution: WorkflowExecution,
        attempt: int = 1
    ):
        """Retry failed action"""
        max_retries = action.retry_config['max_retries']
        retry_delay = action.retry_config['retry_delay']
        
        if attempt <= max_retries:
            logger.info(f"🔄 Retrying action {action.action_id} (attempt {attempt}/{max_retries})")
            await asyncio.sleep(retry_delay)
            
            try:
                result = await self._execute_action(action, variables, execution)
                execution.action_results[f"{action.action_id}_retry_{attempt}"] = result
            except Exception as e:
                logger.error(f"Retry {attempt} failed: {e}")
                await self._retry_action(action, variables, execution, attempt + 1)
    
    # Action Handlers
    
    async def _action_create_campaign(
        self,
        parameters: Dict[str, Any],
        execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Create campaign action"""
        # Extract parameters
        name = parameters.get('name', f"Auto Campaign {datetime.now().strftime('%Y%m%d')}")
        objective = CampaignObjective[parameters.get('objective', 'BRAND_AWARENESS').upper()]
        platforms = [Platform[p.upper()] for p in parameters.get('platforms', ['youtube'])]
        budget = parameters.get('budget', 1000)
        
        # Create campaign
        campaign = self.campaign_manager.create_campaign(
            name=name,
            objective=objective,
            platforms=platforms,
            budget=budget
        )
        
        # Launch on platforms
        launch_results = await self.campaign_manager.launch_campaign(campaign.campaign_id)
        
        return {
            'campaign_id': campaign.campaign_id,
            'launch_results': launch_results,
            'status': 'created'
        }
    
    async def _action_update_campaign(
        self,
        parameters: Dict[str, Any],
        execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Update campaign action"""
        campaign_id = parameters.get('campaign_id')
        updates = parameters.get('updates', {})
        
        # Update via platform manager
        results = {}
        for platform, platform_campaign_id in self.campaign_manager.campaign_mappings.get(campaign_id, {}).items():
            if platform in self.platform_manager.adapters:
                result = await self.platform_manager.adapters[platform].update_campaign(
                    platform_campaign_id,
                    updates
                )
                results[platform] = result
        
        return {'campaign_id': campaign_id, 'updates': updates, 'results': results}
    
    async def _action_pause_campaign(
        self,
        parameters: Dict[str, Any],
        execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Pause campaign action"""
        campaign_id = parameters.get('campaign_id')
        campaign = self.campaign_manager.pause_campaign(campaign_id)
        
        # Pause on all platforms
        results = await self.platform_manager.pause_all_campaigns(campaign.name)
        
        return {'campaign_id': campaign_id, 'status': 'paused', 'platform_results': results}
    
    async def _action_resume_campaign(
        self,
        parameters: Dict[str, Any],
        execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Resume campaign action"""
        campaign_id = parameters.get('campaign_id')
        campaign = self.campaign_manager.resume_campaign(campaign_id)
        
        return {'campaign_id': campaign_id, 'status': 'resumed'}
    
    async def _action_adjust_budget(
        self,
        parameters: Dict[str, Any],
        execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Adjust budget action"""
        campaign_id = parameters.get('campaign_id')
        strategy = parameters.get('strategy', 'fixed')
        
        if strategy == 'performance_based':
            # Get performance data
            performance = await self.platform_manager.get_unified_performance(
                campaign_id,
                (datetime.now() - timedelta(days=7), datetime.now())
            )
            
            # Optimize allocation
            new_allocation = await self.platform_manager.optimize_budget_allocation(
                campaign_id,
                parameters.get('total_budget', 1000)
            )
            
            return {'campaign_id': campaign_id, 'new_allocation': new_allocation}
        else:
            # Fixed adjustment
            adjustment = parameters.get('adjustment', 0)
            return {'campaign_id': campaign_id, 'adjustment': adjustment}
    
    async def _action_generate_creative(
        self,
        parameters: Dict[str, Any],
        execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Generate creative content action"""
        use_trending = parameters.get('use_trending', False)
        format_type = parameters.get('format', 'video')
        
        creative_brief = {
            'format': format_type,
            'duration': parameters.get('duration', 30),
            'style': parameters.get('style', 'modern')
        }
        
        if use_trending:
            # Get trending elements
            trending = self.trending_analyzer.get_all_trending_data(limit=5)
            creative_brief['trending_elements'] = trending['unified_insights']
        
        # Generate with AI
        prompt = f"Generate creative brief for {format_type}: {json.dumps(creative_brief)}"
        creative_content = self.ai_manager.generate_text(prompt)
        
        return {
            'creative_id': str(uuid.uuid4()),
            'brief': creative_brief,
            'content': creative_content,
            'status': 'generated'
        }
    
    async def _action_ab_test(
        self,
        parameters: Dict[str, Any],
        execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Run A/B test action"""
        variants = parameters.get('variants', 2)
        duration = parameters.get('test_duration_hours', 48)
        success_metric = parameters.get('success_metric', 'ctr')
        
        # Create test variants
        test_id = str(uuid.uuid4())
        variants_created = []
        
        for i in range(variants):
            variant = {
                'variant_id': f"{test_id}_variant_{i}",
                'traffic_allocation': 100 / variants,
                'status': 'active'
            }
            variants_created.append(variant)
        
        # Schedule test completion
        completion_time = datetime.now() + timedelta(hours=duration)
        
        return {
            'test_id': test_id,
            'variants': variants_created,
            'success_metric': success_metric,
            'completion_time': completion_time.isoformat(),
            'status': 'running'
        }
    
    async def _action_optimize_targeting(
        self,
        parameters: Dict[str, Any],
        execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Optimize audience targeting action"""
        campaign_id = parameters.get('campaign_id')
        optimization_goal = parameters.get('optimization_goal', 'cpa')
        
        # Get current performance by audience
        audience_performance = self.analytics._audience_insights(
            self.analytics.get_metrics(
                dimensions={'campaign': campaign_id},
                time_range=(datetime.now() - timedelta(days=7), datetime.now())
            )
        )
        
        # AI optimization
        prompt = f"""
        Optimize audience targeting for {optimization_goal}:
        Current performance: {json.dumps(audience_performance)}
        
        Suggest targeting improvements.
        """
        
        optimizations = self.ai_manager.generate_text(prompt)
        
        return {
            'campaign_id': campaign_id,
            'optimizations': optimizations,
            'current_performance': audience_performance
        }
    
    async def _action_send_notification(
        self,
        parameters: Dict[str, Any],
        execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Send notification action"""
        recipients = parameters.get('recipients', [])
        message = parameters.get('message', '')
        channel = parameters.get('channel', 'email')
        
        # In production, integrate with notification service
        logger.info(f"📧 Sending notification via {channel}: {message[:50]}...")
        
        return {
            'notification_id': str(uuid.uuid4()),
            'recipients': recipients,
            'channel': channel,
            'status': 'sent'
        }
    
    async def _action_export_report(
        self,
        parameters: Dict[str, Any],
        execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Export analytics report action"""
        format_type = parameters.get('format', 'pdf')
        time_range = parameters.get('time_range')
        
        if time_range:
            start = datetime.fromisoformat(time_range['start'])
            end = datetime.fromisoformat(time_range['end'])
            time_range = (start, end)
        else:
            time_range = (datetime.now() - timedelta(days=30), datetime.now())
        
        # Generate report
        report_data = self.analytics.export_report(format_type, time_range)
        
        # Save report
        report_id = str(uuid.uuid4())
        report_path = f"/tmp/report_{report_id}.{format_type}"
        
        with open(report_path, 'wb') as f:
            f.write(report_data)
        
        return {
            'report_id': report_id,
            'path': report_path,
            'format': format_type,
            'size_bytes': len(report_data)
        }
    
    async def _action_scale_campaign(
        self,
        parameters: Dict[str, Any],
        execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Scale successful campaign action"""
        campaign_id = parameters.get('campaign_id')
        scale_factor = parameters.get('scale_factor', 2)
        new_markets = parameters.get('new_markets', [])
        
        # Get current campaign
        campaign = self.campaign_manager.campaigns.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        # Scale budget
        new_budget = sum(b.amount for b in campaign.budget_allocations) * scale_factor
        
        # Add new markets
        if new_markets:
            campaign.target_audience.locations.extend(new_markets)
        
        return {
            'campaign_id': campaign_id,
            'new_budget': new_budget,
            'new_markets': new_markets,
            'scale_factor': scale_factor
        }
    
    async def _action_clone_campaign(
        self,
        parameters: Dict[str, Any],
        execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Clone existing campaign action"""
        source_campaign_id = parameters.get('source_campaign_id')
        modifications = parameters.get('modifications', {})
        
        # Get source campaign
        source = self.campaign_manager.campaigns.get(source_campaign_id)
        if not source:
            raise ValueError(f"Source campaign {source_campaign_id} not found")
        
        # Create clone with modifications
        clone = self.campaign_manager.create_campaign(
            name=modifications.get('name', f"{source.name} - Clone"),
            objective=source.objective,
            platforms=source.platforms,
            budget=modifications.get('budget', sum(b.amount for b in source.budget_allocations))
        )
        
        return {
            'source_campaign_id': source_campaign_id,
            'cloned_campaign_id': clone.campaign_id,
            'modifications': modifications
        }
    
    def _substitute_variables(
        self,
        parameters: Dict[str, Any],
        variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Substitute variables in parameters"""
        result = {}
        
        for key, value in parameters.items():
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                # Variable reference
                var_name = value[2:-1]
                result[key] = variables.get(var_name, value)
            elif isinstance(value, dict):
                # Recursive substitution
                result[key] = self._substitute_variables(value, variables)
            else:
                result[key] = value
        
        return result
    
    def _calculate_viral_score(self, trending_data: Dict[str, Any]) -> float:
        """Calculate viral potential score from trending data"""
        score = 0.0
        
        # Factor in various metrics
        if 'trending_videos' in trending_data:
            avg_views = sum(v.get('view_count', 0) for v in trending_data['trending_videos']) / len(trending_data['trending_videos'])
            if avg_views > 1000000:
                score += 0.3
            elif avg_views > 100000:
                score += 0.2
        
        if 'trending_hashtags' in trending_data:
            top_hashtag_score = max((h.get('trend_score', 0) for h in trending_data['trending_hashtags']), default=0)
            score += top_hashtag_score * 0.5
        
        if 'analysis' in trending_data:
            engagement_rate = trending_data['analysis'].get('average_metrics', {}).get('engagement_rate', 0)
            score += min(engagement_rate * 10, 0.2)
        
        return min(score, 1.0)
    
    def _check_performance_conditions(
        self,
        metrics: Any,
        conditions: Dict[str, Any]
    ) -> bool:
        """Check if performance conditions are met"""
        if metrics.empty:
            return False
        
        # Check various conditions
        if 'min_cpa' in conditions:
            if 'cpa' in metrics.columns:
                if metrics['cpa'].mean() < conditions['min_cpa']:
                    return True
        
        if 'max_cpa' in conditions:
            if 'cpa' in metrics.columns:
                if metrics['cpa'].mean() > conditions['max_cpa']:
                    return True
        
        if 'min_roas' in conditions:
            if 'roas' in metrics.columns:
                if metrics['roas'].mean() < conditions['min_roas']:
                    return True
        
        return False
    
    def emit_event(self, event_name: str, event_data: Dict[str, Any]):
        """
        Emit an event to trigger workflows
        
        Args:
            event_name: Name of event
            event_data: Event payload
        """
        logger.info(f"📢 Event emitted: {event_name}")
        
        # Find workflows listening to this event
        for workflow_id, trigger in self.event_bus.get(event_name, []):
            # Execute workflow
            asyncio.create_task(
                self.execute_workflow(workflow_id, trigger_data={
                    "trigger": "event",
                    "event_name": event_name,
                    "event_data": event_data
                })
            )
    
    def start_monitoring(self):
        """Start background monitoring for triggers"""
        if not self.monitoring_active:
            self.monitoring_active = True
            
            # Start scheduler thread
            def run_scheduler():
                while self.monitoring_active:
                    schedule.run_pending()
                    threading.Event().wait(1)
            
            self.monitoring_thread = threading.Thread(target=run_scheduler, daemon=True)
            self.monitoring_thread.start()
            
            logger.info("🔍 Workflow monitoring started")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring_active = False
        
        # Cancel all trigger monitors
        for task in self.trigger_monitors.values():
            task.cancel()
        
        logger.info("🛑 Workflow monitoring stopped")
    
    def get_workflow_status(self, execution_id: str) -> Dict[str, Any]:
        """Get status of workflow execution"""
        execution = self.executions.get(execution_id)
        if not execution:
            return {'error': 'Execution not found'}
        
        return {
            'execution_id': execution_id,
            'workflow_id': execution.workflow_id,
            'status': execution.status.value,
            'started_at': execution.started_at.isoformat() if execution.started_at else None,
            'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
            'metrics': execution.metrics,
            'errors': execution.errors
        }