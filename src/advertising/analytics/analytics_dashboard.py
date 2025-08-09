"""
Advanced Analytics Dashboard System
Real-time performance tracking and insights for advertising campaigns
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
import numpy as np
from collections import defaultdict
import logging
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics tracked"""
    IMPRESSIONS = "impressions"
    CLICKS = "clicks"
    CONVERSIONS = "conversions"
    COST = "cost"
    REVENUE = "revenue"
    CTR = "ctr"
    CVR = "cvr"
    CPA = "cpa"
    ROAS = "roas"
    ENGAGEMENT_RATE = "engagement_rate"
    VIEW_RATE = "view_rate"
    BOUNCE_RATE = "bounce_rate"
    
    
class TimeGranularity(Enum):
    """Time granularity for analytics"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class DimensionType(Enum):
    """Dimensions for data analysis"""
    PLATFORM = "platform"
    CAMPAIGN = "campaign"
    AD_SET = "ad_set"
    CREATIVE = "creative"
    AUDIENCE = "audience"
    DEVICE = "device"
    LOCATION = "location"
    TIME = "time"
    KEYWORD = "keyword"
    PLACEMENT = "placement"


@dataclass
class MetricSnapshot:
    """Single metric measurement"""
    metric_type: MetricType
    value: float
    timestamp: datetime
    dimensions: Dict[str, str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceAlert:
    """Performance alert configuration"""
    alert_id: str
    name: str
    metric: MetricType
    condition: str  # >, <, =, !=
    threshold: float
    severity: str  # low, medium, high, critical
    action: str  # notify, pause_campaign, adjust_budget
    triggered: bool = False
    last_triggered: Optional[datetime] = None


@dataclass
class DashboardWidget:
    """Dashboard widget configuration"""
    widget_id: str
    title: str
    widget_type: str  # chart, metric, table, heatmap
    metrics: List[MetricType]
    dimensions: List[DimensionType]
    time_range: str  # last_24h, last_7d, last_30d, custom
    refresh_interval: int  # seconds
    position: Dict[str, int]  # x, y, width, height
    config: Dict[str, Any] = field(default_factory=dict)


class AnalyticsDashboard:
    """
    Comprehensive analytics dashboard for advertising campaigns
    Provides real-time insights, predictions, and recommendations
    """
    
    def __init__(self):
        """Initialize analytics dashboard"""
        self.metrics_store: List[MetricSnapshot] = []
        self.alerts: Dict[str, PerformanceAlert] = {}
        self.widgets: Dict[str, DashboardWidget] = {}
        self.predictions_cache: Dict[str, Any] = {}
        
        # Initialize default widgets
        self._init_default_widgets()
        
        # Start background tasks
        self.monitoring_task = None
        
        logger.info("✅ AnalyticsDashboard initialized")
    
    def _init_default_widgets(self):
        """Initialize default dashboard widgets"""
        # Overview metrics
        self.add_widget(DashboardWidget(
            widget_id="overview_metrics",
            title="Campaign Overview",
            widget_type="metric",
            metrics=[MetricType.IMPRESSIONS, MetricType.CLICKS, MetricType.CONVERSIONS, MetricType.COST],
            dimensions=[DimensionType.CAMPAIGN],
            time_range="last_24h",
            refresh_interval=60,
            position={"x": 0, "y": 0, "width": 12, "height": 2}
        ))
        
        # Performance chart
        self.add_widget(DashboardWidget(
            widget_id="performance_chart",
            title="Performance Trends",
            widget_type="chart",
            metrics=[MetricType.CTR, MetricType.CVR, MetricType.ROAS],
            dimensions=[DimensionType.TIME],
            time_range="last_7d",
            refresh_interval=300,
            position={"x": 0, "y": 2, "width": 8, "height": 4}
        ))
        
        # Platform breakdown
        self.add_widget(DashboardWidget(
            widget_id="platform_breakdown",
            title="Platform Performance",
            widget_type="table",
            metrics=[MetricType.IMPRESSIONS, MetricType.CLICKS, MetricType.COST, MetricType.ROAS],
            dimensions=[DimensionType.PLATFORM],
            time_range="last_30d",
            refresh_interval=600,
            position={"x": 8, "y": 2, "width": 4, "height": 4}
        ))
    
    def record_metric(
        self,
        metric_type: MetricType,
        value: float,
        dimensions: Dict[str, str],
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Record a metric measurement
        
        Args:
            metric_type: Type of metric
            value: Metric value
            dimensions: Dimensional breakdown
            timestamp: Measurement time (default: now)
            metadata: Additional metadata
        """
        snapshot = MetricSnapshot(
            metric_type=metric_type,
            value=value,
            timestamp=timestamp or datetime.now(),
            dimensions=dimensions,
            metadata=metadata or {}
        )
        
        self.metrics_store.append(snapshot)
        
        # Check alerts
        self._check_alerts(snapshot)
        
        # Update predictions if needed
        if len(self.metrics_store) % 100 == 0:
            self._update_predictions()
    
    def get_metrics(
        self,
        metric_types: Optional[List[MetricType]] = None,
        dimensions: Optional[Dict[str, str]] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None,
        granularity: TimeGranularity = TimeGranularity.DAILY
    ) -> pd.DataFrame:
        """
        Query metrics with filters
        
        Args:
            metric_types: Filter by metric types
            dimensions: Filter by dimensions
            time_range: Time range filter
            granularity: Time aggregation level
            
        Returns:
            DataFrame with metrics
        """
        # Filter metrics
        filtered = self.metrics_store.copy()
        
        if metric_types:
            filtered = [m for m in filtered if m.metric_type in metric_types]
        
        if dimensions:
            filtered = [
                m for m in filtered
                if all(m.dimensions.get(k) == v for k, v in dimensions.items())
            ]
        
        if time_range:
            start, end = time_range
            filtered = [
                m for m in filtered
                if start <= m.timestamp <= end
            ]
        
        # Convert to DataFrame
        if not filtered:
            return pd.DataFrame()
        
        data = []
        for metric in filtered:
            row = {
                'timestamp': metric.timestamp,
                'metric_type': metric.metric_type.value,
                'value': metric.value,
                **metric.dimensions
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # Aggregate by granularity
        df = self._aggregate_by_granularity(df, granularity)
        
        return df
    
    def _aggregate_by_granularity(
        self,
        df: pd.DataFrame,
        granularity: TimeGranularity
    ) -> pd.DataFrame:
        """Aggregate data by time granularity"""
        if df.empty:
            return df
        
        # Set timestamp as index
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # Determine resampling rule
        rules = {
            TimeGranularity.HOURLY: 'H',
            TimeGranularity.DAILY: 'D',
            TimeGranularity.WEEKLY: 'W',
            TimeGranularity.MONTHLY: 'M',
            TimeGranularity.QUARTERLY: 'Q',
            TimeGranularity.YEARLY: 'Y'
        }
        
        rule = rules.get(granularity, 'D')
        
        # Group by dimensions and resample
        groupby_cols = [col for col in df.columns if col not in ['value', 'metric_type']]
        
        if groupby_cols:
            aggregated = df.groupby(groupby_cols).resample(rule).agg({
                'value': ['sum', 'mean', 'min', 'max', 'count']
            }).reset_index()
        else:
            aggregated = df.resample(rule).agg({
                'value': ['sum', 'mean', 'min', 'max', 'count']
            }).reset_index()
        
        return aggregated
    
    def calculate_derived_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate derived metrics (CTR, CVR, CPA, ROAS)
        
        Args:
            df: DataFrame with base metrics
            
        Returns:
            DataFrame with derived metrics added
        """
        if df.empty:
            return df
        
        # Calculate CTR
        if 'impressions' in df.columns and 'clicks' in df.columns:
            df['ctr'] = df['clicks'] / df['impressions'].replace(0, 1)
        
        # Calculate CVR
        if 'clicks' in df.columns and 'conversions' in df.columns:
            df['cvr'] = df['conversions'] / df['clicks'].replace(0, 1)
        
        # Calculate CPA
        if 'cost' in df.columns and 'conversions' in df.columns:
            df['cpa'] = df['cost'] / df['conversions'].replace(0, 1)
        
        # Calculate ROAS
        if 'revenue' in df.columns and 'cost' in df.columns:
            df['roas'] = df['revenue'] / df['cost'].replace(0, 1)
        
        return df
    
    def generate_performance_report(
        self,
        campaign_ids: Optional[List[str]] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive performance report
        
        Args:
            campaign_ids: Filter by campaigns
            time_range: Time range for report
            
        Returns:
            Performance report dictionary
        """
        if not time_range:
            time_range = (datetime.now() - timedelta(days=30), datetime.now())
        
        # Get metrics
        dimensions = {'campaign': campaign_ids[0]} if campaign_ids else {}
        df = self.get_metrics(
            dimensions=dimensions,
            time_range=time_range,
            granularity=TimeGranularity.DAILY
        )
        
        if df.empty:
            return {'error': 'No data available for the specified period'}
        
        # Calculate derived metrics
        df = self.calculate_derived_metrics(df)
        
        # Generate report sections
        report = {
            'summary': self._generate_summary(df),
            'trends': self._analyze_trends(df),
            'platform_breakdown': self._platform_breakdown(df),
            'audience_insights': self._audience_insights(df),
            'creative_performance': self._creative_performance(df),
            'recommendations': self._generate_recommendations(df),
            'predictions': self._generate_predictions(df)
        }
        
        return report
    
    def _generate_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary statistics"""
        summary = {
            'total_impressions': df['value'].sum() if 'impressions' in str(df.get('metric_type', [])) else 0,
            'total_clicks': df['value'].sum() if 'clicks' in str(df.get('metric_type', [])) else 0,
            'total_conversions': df['value'].sum() if 'conversions' in str(df.get('metric_type', [])) else 0,
            'total_cost': df['value'].sum() if 'cost' in str(df.get('metric_type', [])) else 0,
            'total_revenue': df['value'].sum() if 'revenue' in str(df.get('metric_type', [])) else 0,
            'avg_ctr': df['ctr'].mean() if 'ctr' in df.columns else 0,
            'avg_cvr': df['cvr'].mean() if 'cvr' in df.columns else 0,
            'avg_cpa': df['cpa'].mean() if 'cpa' in df.columns else 0,
            'avg_roas': df['roas'].mean() if 'roas' in df.columns else 0
        }
        
        # Calculate period-over-period change
        if len(df) > 7:
            recent = df.tail(7)
            previous = df.iloc[-14:-7] if len(df) > 14 else df.head(7)
            
            summary['weekly_change'] = {
                'impressions': self._calculate_change(
                    recent['value'].sum() if 'impressions' in str(recent.get('metric_type', [])) else 0,
                    previous['value'].sum() if 'impressions' in str(previous.get('metric_type', [])) else 0
                ),
                'conversions': self._calculate_change(
                    recent['value'].sum() if 'conversions' in str(recent.get('metric_type', [])) else 0,
                    previous['value'].sum() if 'conversions' in str(previous.get('metric_type', [])) else 0
                )
            }
        
        return summary
    
    def _analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze performance trends"""
        trends = {
            'direction': 'stable',
            'momentum': 0,
            'key_changes': []
        }
        
        if len(df) < 2:
            return trends
        
        # Calculate trend direction
        if 'value' in df.columns:
            values = df['value'].values
            if len(values) > 1:
                # Simple linear regression for trend
                x = np.arange(len(values))
                z = np.polyfit(x, values, 1)
                slope = z[0]
                
                if slope > 0.1:
                    trends['direction'] = 'improving'
                    trends['momentum'] = min(slope / values.mean(), 1.0)
                elif slope < -0.1:
                    trends['direction'] = 'declining'
                    trends['momentum'] = max(slope / values.mean(), -1.0)
        
        # Identify key changes
        if 'ctr' in df.columns:
            ctr_change = self._calculate_change(
                df['ctr'].iloc[-1] if len(df) > 0 else 0,
                df['ctr'].iloc[0] if len(df) > 0 else 0
            )
            if abs(ctr_change) > 10:
                trends['key_changes'].append(f"CTR changed by {ctr_change:.1f}%")
        
        return trends
    
    def _platform_breakdown(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze performance by platform"""
        breakdown = {}
        
        if 'platform' in df.columns:
            for platform in df['platform'].unique():
                platform_df = df[df['platform'] == platform]
                breakdown[platform] = {
                    'impressions': platform_df['value'].sum() if 'impressions' in str(platform_df.get('metric_type', [])) else 0,
                    'clicks': platform_df['value'].sum() if 'clicks' in str(platform_df.get('metric_type', [])) else 0,
                    'cost': platform_df['value'].sum() if 'cost' in str(platform_df.get('metric_type', [])) else 0,
                    'performance_score': self._calculate_performance_score(platform_df)
                }
        
        return breakdown
    
    def _audience_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate audience insights"""
        insights = {
            'top_performing_segments': [],
            'engagement_by_age': {},
            'device_breakdown': {},
            'geographic_performance': {}
        }
        
        # Analyze by audience dimensions if available
        if 'audience_segment' in df.columns:
            segment_performance = df.groupby('audience_segment').agg({
                'value': 'sum'
            }).sort_values('value', ascending=False)
            
            insights['top_performing_segments'] = segment_performance.head(5).to_dict()
        
        # Device breakdown
        if 'device' in df.columns:
            device_stats = df.groupby('device').agg({
                'value': 'sum'
            })
            insights['device_breakdown'] = device_stats.to_dict()
        
        return insights
    
    def _creative_performance(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Analyze creative performance"""
        creative_data = []
        
        if 'creative_id' in df.columns:
            for creative_id in df['creative_id'].unique():
                creative_df = df[df['creative_id'] == creative_id]
                
                performance = {
                    'creative_id': creative_id,
                    'impressions': creative_df['value'].sum() if 'impressions' in str(creative_df.get('metric_type', [])) else 0,
                    'engagement_rate': creative_df['engagement_rate'].mean() if 'engagement_rate' in creative_df.columns else 0,
                    'performance_score': self._calculate_performance_score(creative_df)
                }
                creative_data.append(performance)
        
        # Sort by performance
        creative_data.sort(key=lambda x: x['performance_score'], reverse=True)
        
        return creative_data[:10]  # Top 10 creatives
    
    def _generate_recommendations(self, df: pd.DataFrame) -> List[str]:
        """Generate actionable recommendations based on data"""
        recommendations = []
        
        # CTR recommendations
        if 'ctr' in df.columns:
            avg_ctr = df['ctr'].mean()
            if avg_ctr < 0.01:
                recommendations.append("CTR is below 1% - Consider improving ad creative and targeting")
            elif avg_ctr > 0.05:
                recommendations.append("Excellent CTR! Consider increasing budget to scale")
        
        # CPA recommendations
        if 'cpa' in df.columns:
            avg_cpa = df['cpa'].mean()
            if 'target_cpa' in df.columns:
                target = df['target_cpa'].iloc[0] if len(df) > 0 else avg_cpa
                if avg_cpa > target * 1.2:
                    recommendations.append(f"CPA is 20% above target - Optimize targeting and bidding")
        
        # ROAS recommendations
        if 'roas' in df.columns:
            avg_roas = df['roas'].mean()
            if avg_roas < 2:
                recommendations.append("ROAS below 2x - Review product pricing or reduce acquisition costs")
            elif avg_roas > 4:
                recommendations.append("Strong ROAS! Consider expanding to new markets")
        
        # Platform-specific recommendations
        if 'platform' in df.columns:
            platform_performance = df.groupby('platform')['value'].sum()
            best_platform = platform_performance.idxmax()
            worst_platform = platform_performance.idxmin()
            
            recommendations.append(f"Shift budget from {worst_platform} to {best_platform} for better ROI")
        
        # Time-based recommendations
        if 'hour' in df.columns:
            hourly_performance = df.groupby('hour')['value'].sum()
            peak_hours = hourly_performance.nlargest(3).index.tolist()
            recommendations.append(f"Focus ad delivery during peak hours: {peak_hours}")
        
        return recommendations
    
    def _generate_predictions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate predictive insights"""
        predictions = {
            'next_7_days': {},
            'next_30_days': {},
            'trend_forecast': 'stable',
            'budget_recommendation': 0
        }
        
        if len(df) < 7:
            return predictions
        
        # Simple moving average prediction
        if 'value' in df.columns:
            recent_avg = df['value'].tail(7).mean()
            recent_growth = self._calculate_change(
                df['value'].iloc[-1] if len(df) > 0 else 0,
                df['value'].iloc[-7] if len(df) > 7 else 0
            ) / 100
            
            # Project forward
            predictions['next_7_days'] = {
                'expected_conversions': recent_avg * 7 * (1 + recent_growth),
                'confidence': 0.7 if len(df) > 14 else 0.5
            }
            
            predictions['next_30_days'] = {
                'expected_conversions': recent_avg * 30 * (1 + recent_growth * 0.5),
                'confidence': 0.6 if len(df) > 30 else 0.4
            }
            
            # Trend forecast
            if recent_growth > 0.1:
                predictions['trend_forecast'] = 'growth'
            elif recent_growth < -0.1:
                predictions['trend_forecast'] = 'decline'
        
        # Budget recommendation
        if 'roas' in df.columns and 'cost' in df.columns:
            current_roas = df['roas'].tail(7).mean()
            current_spend = df['cost'].tail(7).sum() if 'cost' in df.columns else 0
            
            if current_roas > 3:
                predictions['budget_recommendation'] = current_spend * 1.5
            elif current_roas > 2:
                predictions['budget_recommendation'] = current_spend * 1.1
            else:
                predictions['budget_recommendation'] = current_spend * 0.9
        
        return predictions
    
    def create_visualization(
        self,
        widget: DashboardWidget,
        data: pd.DataFrame
    ) -> go.Figure:
        """
        Create plotly visualization for widget
        
        Args:
            widget: Widget configuration
            data: Data to visualize
            
        Returns:
            Plotly figure
        """
        if widget.widget_type == 'chart':
            return self._create_line_chart(widget, data)
        elif widget.widget_type == 'metric':
            return self._create_metric_cards(widget, data)
        elif widget.widget_type == 'table':
            return self._create_data_table(widget, data)
        elif widget.widget_type == 'heatmap':
            return self._create_heatmap(widget, data)
        else:
            return go.Figure()
    
    def _create_line_chart(self, widget: DashboardWidget, data: pd.DataFrame) -> go.Figure:
        """Create line chart visualization"""
        fig = go.Figure()
        
        for metric in widget.metrics:
            metric_data = data[data['metric_type'] == metric.value] if 'metric_type' in data.columns else data
            
            if not metric_data.empty:
                fig.add_trace(go.Scatter(
                    x=metric_data.index if isinstance(metric_data.index, pd.DatetimeIndex) else metric_data['timestamp'],
                    y=metric_data['value'] if 'value' in metric_data.columns else metric_data[metric.value],
                    mode='lines+markers',
                    name=metric.value.upper(),
                    line=dict(width=2),
                    marker=dict(size=6)
                ))
        
        fig.update_layout(
            title=widget.title,
            xaxis_title="Time",
            yaxis_title="Value",
            hovermode='x unified',
            showlegend=True,
            height=widget.position['height'] * 100
        )
        
        return fig
    
    def _create_metric_cards(self, widget: DashboardWidget, data: pd.DataFrame) -> go.Figure:
        """Create metric cards visualization"""
        fig = make_subplots(
            rows=1,
            cols=len(widget.metrics),
            subplot_titles=[m.value.upper() for m in widget.metrics],
            specs=[[{'type': 'indicator'} for _ in widget.metrics]]
        )
        
        for i, metric in enumerate(widget.metrics, 1):
            metric_data = data[data['metric_type'] == metric.value] if 'metric_type' in data.columns else data
            
            if not metric_data.empty:
                current_value = metric_data['value'].iloc[-1] if 'value' in metric_data.columns else 0
                previous_value = metric_data['value'].iloc[-2] if len(metric_data) > 1 and 'value' in metric_data.columns else current_value
                
                fig.add_trace(
                    go.Indicator(
                        mode="number+delta",
                        value=current_value,
                        delta={'reference': previous_value, 'relative': True},
                        domain={'x': [0, 1], 'y': [0, 1]}
                    ),
                    row=1, col=i
                )
        
        fig.update_layout(
            title=widget.title,
            height=widget.position['height'] * 100
        )
        
        return fig
    
    def _create_data_table(self, widget: DashboardWidget, data: pd.DataFrame) -> go.Figure:
        """Create data table visualization"""
        # Prepare data for table
        table_data = data.head(20)  # Limit to 20 rows for display
        
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=list(table_data.columns),
                fill_color='paleturquoise',
                align='left',
                font=dict(size=12)
            ),
            cells=dict(
                values=[table_data[col] for col in table_data.columns],
                fill_color='lavender',
                align='left',
                font=dict(size=11)
            )
        )])
        
        fig.update_layout(
            title=widget.title,
            height=widget.position['height'] * 100
        )
        
        return fig
    
    def _create_heatmap(self, widget: DashboardWidget, data: pd.DataFrame) -> go.Figure:
        """Create heatmap visualization"""
        # Create pivot table for heatmap
        if len(widget.dimensions) >= 2 and not data.empty:
            dim1 = widget.dimensions[0].value
            dim2 = widget.dimensions[1].value
            
            if dim1 in data.columns and dim2 in data.columns:
                pivot = data.pivot_table(
                    values='value' if 'value' in data.columns else data.columns[0],
                    index=dim1,
                    columns=dim2,
                    aggfunc='mean'
                )
                
                fig = go.Figure(data=go.Heatmap(
                    z=pivot.values,
                    x=pivot.columns,
                    y=pivot.index,
                    colorscale='Viridis'
                ))
                
                fig.update_layout(
                    title=widget.title,
                    xaxis_title=dim2,
                    yaxis_title=dim1,
                    height=widget.position['height'] * 100
                )
                
                return fig
        
        return go.Figure()
    
    def add_alert(self, alert: PerformanceAlert):
        """Add performance alert"""
        self.alerts[alert.alert_id] = alert
        logger.info(f"📢 Alert added: {alert.name}")
    
    def _check_alerts(self, snapshot: MetricSnapshot):
        """Check if any alerts should be triggered"""
        for alert in self.alerts.values():
            if alert.metric == snapshot.metric_type:
                should_trigger = False
                
                if alert.condition == '>' and snapshot.value > alert.threshold:
                    should_trigger = True
                elif alert.condition == '<' and snapshot.value < alert.threshold:
                    should_trigger = True
                elif alert.condition == '=' and snapshot.value == alert.threshold:
                    should_trigger = True
                elif alert.condition == '!=' and snapshot.value != alert.threshold:
                    should_trigger = True
                
                if should_trigger and not alert.triggered:
                    self._trigger_alert(alert, snapshot)
                elif not should_trigger and alert.triggered:
                    alert.triggered = False
    
    def _trigger_alert(self, alert: PerformanceAlert, snapshot: MetricSnapshot):
        """Trigger an alert"""
        alert.triggered = True
        alert.last_triggered = datetime.now()
        
        logger.warning(f"⚠️ Alert triggered: {alert.name} - {snapshot.metric_type.value} = {snapshot.value}")
        
        # Take action based on alert configuration
        if alert.action == 'notify':
            self._send_notification(alert, snapshot)
        elif alert.action == 'pause_campaign':
            self._pause_campaign_action(snapshot.dimensions.get('campaign_id'))
        elif alert.action == 'adjust_budget':
            self._adjust_budget_action(snapshot.dimensions.get('campaign_id'), alert)
    
    def _send_notification(self, alert: PerformanceAlert, snapshot: MetricSnapshot):
        """Send alert notification"""
        # In production, integrate with notification service
        logger.info(f"📧 Notification sent for alert: {alert.name}")
    
    def _pause_campaign_action(self, campaign_id: Optional[str]):
        """Pause campaign action"""
        if campaign_id:
            logger.info(f"⏸️ Pausing campaign: {campaign_id}")
            # In production, call campaign manager to pause
    
    def _adjust_budget_action(self, campaign_id: Optional[str], alert: PerformanceAlert):
        """Adjust budget action"""
        if campaign_id:
            logger.info(f"💰 Adjusting budget for campaign: {campaign_id}")
            # In production, call campaign manager to adjust budget
    
    def add_widget(self, widget: DashboardWidget):
        """Add widget to dashboard"""
        self.widgets[widget.widget_id] = widget
        logger.info(f"📊 Widget added: {widget.title}")
    
    def _calculate_change(self, current: float, previous: float) -> float:
        """Calculate percentage change"""
        if previous == 0:
            return 100 if current > 0 else 0
        return ((current - previous) / previous) * 100
    
    def _calculate_performance_score(self, df: pd.DataFrame) -> float:
        """Calculate overall performance score"""
        score = 0.5  # Base score
        
        # Factor in CTR
        if 'ctr' in df.columns:
            avg_ctr = df['ctr'].mean()
            if avg_ctr > 0.02:
                score += 0.2
            elif avg_ctr > 0.01:
                score += 0.1
        
        # Factor in ROAS
        if 'roas' in df.columns:
            avg_roas = df['roas'].mean()
            if avg_roas > 4:
                score += 0.3
            elif avg_roas > 2:
                score += 0.2
            elif avg_roas > 1:
                score += 0.1
        
        return min(score, 1.0)
    
    def _update_predictions(self):
        """Update predictive models"""
        # In production, use ML models for predictions
        logger.info("🔮 Updating predictions cache")
    
    async def start_real_time_monitoring(self):
        """Start real-time monitoring"""
        logger.info("🚀 Starting real-time monitoring")
        
        while True:
            try:
                # Fetch latest metrics from platforms
                # Update visualizations
                # Check alerts
                
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(60)
    
    def export_report(
        self,
        format: str = 'pdf',
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> bytes:
        """
        Export analytics report
        
        Args:
            format: Export format (pdf, csv, json)
            time_range: Time range for report
            
        Returns:
            Report data as bytes
        """
        report = self.generate_performance_report(time_range=time_range)
        
        if format == 'json':
            return json.dumps(report, indent=2, default=str).encode()
        elif format == 'csv':
            # Convert to CSV
            df = self.get_metrics(time_range=time_range)
            return df.to_csv().encode()
        elif format == 'pdf':
            # In production, use PDF generation library
            return json.dumps(report, indent=2, default=str).encode()
        
        return b''