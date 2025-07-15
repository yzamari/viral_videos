"""
Performance Monitor for AI Video Generator
Tracks system metrics, API calls, and generation performance
"""

import time
import psutil
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses  import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    unit: str = ""

@dataclass
class TimingContext:
    """Context for timing operations"""
    name: str
    start_time: float
    tags: Dict[str, str] = field(default_factory=dict)

class PerformanceMonitor:
    """
    Comprehensive performance monitoring system

    Tracks system metrics, API performance, and generation statistics
    with real-time monitoring and historical analysis.
    """

    def __init(self, name: str = "ai_video_generator"):
        """
        Initialize performance monitor

        Args:
            name: Name of the monitoring instance
        """
        self.name = name
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.timers: Dict[str, List[float]] = defaultdict(list)

        # System monitoring
        self.system_monitoring = True
        self.monitoring_thread = None
        self.monitoring_interval = 30  # seconds

        # Performance thresholds
        self.thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'api_response_time': 10.0,
            'generation_time': 300.0
        }

        # Start system monitoring
        self._start_system_monitoring()

        logger.info(f"📊 Performance monitor '{name}' initialized")

    def record_metric(
        self,
        name: str,
        value: float,
        tags: Optional[Dict[str,
        str]] = None,
        unit: str = ""):
        """
        Record a performance metric

        Args:
            name: Metric name
            value: Metric value
            tags: Optional tags for the metric
            unit: Unit of measurement
        """
        metric = PerformanceMetric(
            name=name,
            value=value,
            timestamp=datetime.now(),
            tags=tags or {},
            unit=unit
        )

        self.metrics[name].append(metric)
        logger.debug(f"📈 Recorded metric: {name} = {value} {unit}")

    def increment_counter(
        self,
        name: str,
        value: int = 1,
        tags: Optional[Dict[str,
        str]] = None):
        """
        Increment a counter metric

        Args:
            name: Counter name
            value: Increment value
            tags: Optional tags
        """
        self.counters[name] += value
        self.record_metric(f"{name}_total", self.counters[name], tags, "count")

    def set_gauge(
        self,
        name: str,
        value: float,
        tags: Optional[Dict[str,
        str]] = None,
        unit: str = ""):
        """
        Set a gauge metric

        Args:
            name: Gauge name
            value: Gauge value
            tags: Optional tags
            unit: Unit of measurement
        """
        self.gauges[name] = value
        self.record_metric(name, value, tags, unit)

    def time_operation(
        self,
        name: str,
        tags: Optional[Dict[str,
        str]] = None) -> TimingContext:
        """
        Create a timing context for an operation

        Args:
            name: Operation name
            tags: Optional tags

        Returns:
            TimingContext for the operation
        """
        return TimingContext(
            name=name,
            start_time=time.time(),
            tags=tags or {)

    def finish_timing(self, context: TimingContext):
        """
        Finish timing an operation

        Args:
            context: TimingContext from time_operation
        """
        duration = time.time() - context.start_time
        self.timers[context.name].append(duration)
        self.record_metric(
            f"{context.name}_duration",
            duration,
            context.tags,
            "seconds")

        # Check thresholds
        threshold_key = f"{context.name}_time"
        if threshold_key in self.thresholds and
                duration > self.thresholds[threshold_key]:
            logger.warning(f"⚠️ Operation '{context.name}' took {duration:.2f}s (threshold: {self.thresholds[threshold_key]}s)")

    def timer(self, name: str, tags: Optional[Dict[str, str]] = None):
        """
        Decorator for timing functions

        Args:
            name: Timer name
            tags: Optional tags

        Returns:
            Decorator function
        """
        def decorator(func: Callable):
            def wrapper(*args, **kwargs):
                context = self.time_operation(name, tags)
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    self.finish_timing(context)

            wrapper.__name__ = func.__name__
            wrapper.__doc__ = func.__doc__
            return wrapper

        return decorator

    def _start_system_monitoring(self):
        """Start system monitoring thread"""
        if self.monitoring_thread is None or not self.monitoring_thread.is_alive():
            self.monitoring_thread = threading.Thread(
                target=self._monitor_system_metrics,
                daemon=True
            )
            self.monitoring_thread.start()
            logger.info("🔍 Started system monitoring thread")

    def _monitor_system_metrics(self):
        """Monitor system metrics continuously"""
        while self.system_monitoring:
            try:
                # CPU metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                self.set_gauge("system_cpu_usage", cpu_percent, unit="percent")

                # Memory metrics
                memory = psutil.virtual_memory()
                self.set_gauge("system_memory_usage", memory.percent, unit="percent")
                self.set_gauge(
                    "system_memory_available",
                    memory.available / (1024**3),
                    unit="GB")

                # Disk metrics
                disk = psutil.disk_usage('/')
                self.set_gauge("system_disk_usage", disk.percent, unit="percent")
                self.set_gauge("system_disk_free", disk.free / (1024**3), unit="GB")

                # Network metrics (if available)
                try:
                    net_io = psutil.net_io_counters()
                    self.set_gauge("system_bytes_sent", net_io.bytes_sent / (1024**2), unit="MB")
                    self.set_gauge("system_bytes_recv", net_io.bytes_recv / (1024**2), unit="MB")
                except Exception:
                    pass

                # Process metrics
                process = psutil.Process()
                self.set_gauge("process_cpu_usage", process.cpu_percent(), unit="percent")
                self.set_gauge(
                    "process_memory_usage",
                    process.memory_info().rss / (1024**2),
                    unit="MB")

                # Check thresholds
                self._check_thresholds()

                time.sleep(self.monitoring_interval)

            except Exception as e:
                logger.error(f"❌ Error in system monitoring: {e}")
                time.sleep(self.monitoring_interval)

    def _check_thresholds(self):
        """Check performance thresholds and log warnings"""
        # CPU threshold
        if "system_cpu_usage" in self.gauges:
            cpu_usage = self.gauges["system_cpu_usage"]
            if cpu_usage > self.thresholds["cpu_usage"]:
                logger.warning(f"⚠️ High CPU usage: {cpu_usage:.1f}% (threshold: {self.thresholds['cpu_usage']}%)")

        # Memory threshold
        if "system_memory_usage" in self.gauges:
            memory_usage = self.gauges["system_memory_usage"]
            if memory_usage > self.thresholds["memory_usage"]:
                logger.warning(f"⚠️ High memory usage: {memory_usage:.1f}% (threshold: {self.thresholds['memory_usage']}%)")

    def get_metrics_summary(
        self,
        time_window: Optional[timedelta] = None) -> Dict[str, Any]:
        """
        Get summary of metrics within a time window

        Args:
            time_window: Time window for metrics (default: last hour)

        Returns:
            Dictionary with metrics summary
        """
        if time_window is None:
            time_window = timedelta(hours=1)

        cutoff_time = datetime.now() - time_window
        summary = {}

        for metric_name, metric_deque in self.metrics.items():
            # Filter metrics within time window
            recent_metrics = [
                m for m in metric_deque
                if m.timestamp >= cutoff_time
            ]

            if recent_metrics:
                values = [m.value for m in recent_metrics]
                summary[metric_name] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                    "latest": values[-1],
                    "unit": recent_metrics[-1].unit
                }

        return summary

    def get_performance_report(self) -> Dict[str, Any]:
        """
        Get comprehensive performance report

        Returns:
            Dictionary with performance report
        """
        # Get metrics summary
        metrics_summary = self.get_metrics_summary()

        # Calculate timer statistics
        timer_stats = {}
        for timer_name, durations in self.timers.items():
            if durations:
                timer_stats[timer_name] = {
                    "count": len(durations),
                    "min": min(durations),
                    "max": max(durations),
                    "avg": sum(durations) / len(durations),
                    "total": sum(durations),
                    "unit": "seconds"
                }

        # Current system status
        system_status = {
            "cpu_usage": self.gauges.get("system_cpu_usage", 0),
            "memory_usage": self.gauges.get("system_memory_usage", 0),
            "disk_usage": self.gauges.get("system_disk_usage", 0),
            "process_memory": self.gauges.get("process_memory_usage", 0)
        }

        return {
            "timestamp": datetime.now().isoformat(),
            "monitor_name": self.name,
            "system_status": system_status,
            "metrics_summary": metrics_summary,
            "timer_statistics": timer_stats,
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "thresholds": self.thresholds
        }

    def save_report(self, filepath: str):
        """
        Save performance report to file

        Args:
            filepath: Path to save the report
        """
        report = self.get_performance_report()

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"📄 Performance report saved to: {filepath}")

    def reset_metrics(self):
        """Reset all metrics and statistics"""
        self.metrics.clear()
        self.counters.clear()
        self.gauges.clear()
        self.timers.clear()
        logger.info(f"🔄 Reset all metrics for monitor '{self.name}'")

    def stop_monitoring(self):
        """Stop system monitoring"""
        self.system_monitoring = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        logger.info("🛑 Stopped system monitoring")

    def set_threshold(self, metric_name: str, threshold_value: float):
        """
        Set performance threshold for a metric

        Args:
            metric_name: Name of the metric
            threshold_value: Threshold value
        """
        self.thresholds[metric_name] = threshold_value
        logger.info(f"⚖️ Set threshold for '{metric_name}': {threshold_value}")

class VideoGenerationMonitor:
    """Specialized monitor for video generation operations"""

    def __init(self, base_monitor: PerformanceMonitor):
        """
        Initialize video generation monitor

        Args:
            base_monitor: Base performance monitor
        """
        self.monitor = base_monitor
        self.generation_sessions = {}

    def start_generation(self, session_id: str, topic: str, platform: str) -> str:
        """
        Start monitoring a video generation session

        Args:
            session_id: Session identifier
            topic: Video topic
            platform: Target platform

        Returns:
            Generation tracking ID
        """
        tracking_id = f"gen_{session_id}_{int(time.time())}"

        self.generation_sessions[tracking_id] = {
            "session_id": session_id,
            "topic": topic,
            "platform": platform,
            "start_time": time.time(),
            "steps": []
        }

        self.monitor.increment_counter("video_generations_started")
        self.monitor.record_metric("generation_started", 1, {
            "session_id": session_id,
            "platform": platform
        )

        logger.info(f"📹 Started monitoring generation: {tracking_id}")
        return tracking_id

    def record_step(
        self,
        tracking_id: str,
        step_name: str,
        duration: float,
        success: bool = True):
        """
        Record a generation step

        Args:
            tracking_id: Generation tracking ID
            step_name: Name of the step
            duration: Step duration in seconds
            success: Whether the step succeeded
        """
        if tracking_id not in self.generation_sessions:
            logger.warning(f"⚠️ Unknown tracking ID: {tracking_id}")
            return

        step_data = {
            "name": step_name,
            "duration": duration,
            "success": success,
            "timestamp": time.time()
        }

        self.generation_sessions[tracking_id]["steps"].append(step_data)

        # Record metrics
        self.monitor.record_metric(f"step_{step_name}_duration", duration, {
            "tracking_id": tracking_id,
            "success": str(success)
        }, "seconds")

        if success:
            self.monitor.increment_counter(f"step_{step_name}_success")
        else:
            self.monitor.increment_counter(f"step_{step_name}_failure")

    def finish_generation(
        self,
        tracking_id: str,
        success: bool = True,
        final_video_path: Optional[str] = None):
        """
        Finish monitoring a generation session

        Args:
            tracking_id: Generation tracking ID
            success: Whether generation succeeded
            final_video_path: Path to final video if successful
        """
        if tracking_id not in self.generation_sessions:
            logger.warning(f"⚠️ Unknown tracking ID: {tracking_id}")
            return

        session = self.generation_sessions[tracking_id]
        total_duration = time.time() - session["start_time"]

        # Update session
        session["end_time"] = time.time()
        session["total_duration"] = total_duration
        session["success"] = success
        session["final_video_path"] = final_video_path

        # Record metrics
        self.monitor.record_metric("generation_total_duration", total_duration, {
            "session_id": session["session_id"],
            "platform": session["platform"],
            "success": str(success)
        }, "seconds")

        if success:
            self.monitor.increment_counter("video_generations_completed")
        else:
            self.monitor.increment_counter("video_generations_failed")

        logger.info(f"📹 Finished monitoring generation: {tracking_id} ('success' if success else 'failure'}, {total_duration:.2f}s)")

    def get_generation_stats(self) -> Dict[str, Any]:
        """
        Get generation statistics

        Returns:
            Dictionary with generation statistics
        """
        active_sessions = len([s for s in self.generation_sessions.values() if "end_time" not in s])
        completed_sessions = len([s for s in self.generation_sessions.values() if "end_time" in s])
        successful_sessions = len([s for s in self.generation_sessions.values() if s.get("success", False)])

        # Calculate average durations
        completed_durations = [s["total_duration"] for s in self.generation_sessions.values() if "total_duration" in s]
        avg_duration = sum(completed_durations) / len(completed_durations) if completed_durations else 0

        return {
            "active_sessions": active_sessions,
            "completed_sessions": completed_sessions,
            "successful_sessions": successful_sessions,
            "success_rate": (successful_sessions / completed_sessions * 100) if completed_sessions > 0 else 0,
            "average_duration": avg_duration,
            "total_sessions": len(self.generation_sessions)
        }

# Global performance monitor instance
performance_monitor = PerformanceMonitor()
video_generation_monitor = VideoGenerationMonitor(performance_monitor)

def monitor_performance(
    operation_name: str,
    tags: Optional[Dict[str,
    str]] = None):
    """
    Decorator for monitoring function performance

    Args:
        operation_name: Name of the operation
        tags: Optional tags for the operation

    Returns:
        Decorator function
    """
    return performance_monitor.timer(operation_name, tags)

def track_api_call(api_name: str):
    """
    Decorator for tracking API calls

    Args:
        api_name: Name of the API

    Returns:
        Decorator function
    """
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            # Start timing
            context = performance_monitor.time_operation(f"api_{api_name}")

            try:
                result = func(*args, **kwargs)
                performance_monitor.increment_counter(f"api_{api_name}_success")
                return result

            except Exception as e:
                performance_monitor.increment_counter(f"api_{api_name}_failure")
                raise e

            finally:
                performance_monitor.finish_timing(context)

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper

    return decorator
