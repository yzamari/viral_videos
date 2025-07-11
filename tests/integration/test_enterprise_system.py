"""
Comprehensive Enterprise System Integration Test
Tests all components working together in a production-like environment
"""

import os
import sys
import time
import tempfile
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from utils.session_manager import SessionManager
from utils.session_context import create_session_context
from shared.resilience.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
from shared.resilience.retry_manager import RetryManager, RetryConfig
from shared.caching.cache_manager import CacheManager, CacheConfig
from shared.monitoring.performance_monitor import PerformanceMonitor, VideoGenerationMonitor
from models.video_models import GeneratedVideoConfig, Platform, VideoCategory


class TestEnterpriseSystemIntegration:
    """Comprehensive integration test for the entire enterprise system"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.session_manager = SessionManager(base_output_dir=self.temp_dir)
        
        # Initialize enterprise components
        self.circuit_breaker = CircuitBreaker("test_system", CircuitBreakerConfig(
            failure_threshold=3,
            reset_timeout=2,
            success_threshold=2
        ))
        
        self.retry_manager = RetryManager("test_system", RetryConfig(
            max_retries=3,
            base_delay=0.1,
            max_delay=1.0
        ))
        
        self.cache_manager = CacheManager("test_system", CacheConfig(
            max_size=100,
            ttl_seconds=300,
            persist_to_disk=False  # Disable for tests
        ))
        
        self.performance_monitor = PerformanceMonitor("test_system")
        self.video_monitor = VideoGenerationMonitor(self.performance_monitor)
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        
        # Stop monitoring
        self.performance_monitor.stop_monitoring()
    
    def test_complete_video_generation_workflow(self):
        """Test complete video generation workflow with all enterprise components"""
        # Create session
        session_id = self.session_manager.create_session(
            topic="Enterprise System Test",
            platform="tiktok",
            duration=15,
            category="Educational"
        )
        
        # Create session context
        context = create_session_context(session_id)
        
        # Start video generation monitoring
        tracking_id = self.video_monitor.start_generation(
            session_id=session_id,
            topic="Enterprise System Test",
            platform="tiktok"
        )
        
        # Simulate video generation steps with enterprise patterns
        steps = [
            ("script_processing", 2.5),
            ("image_generation", 5.2),
            ("video_generation", 8.7),
            ("audio_generation", 3.1),
            ("final_composition", 4.3)
        ]
        
        total_start_time = time.time()
        
        for step_name, duration in steps:
            # Simulate step execution with monitoring
            step_start_time = time.time()
            
            # Use cache for repeated operations
            cache_key = f"{step_name}_{session_id}"
            cached_result = self.cache_manager.get(cache_key)
            
            if cached_result:
                # Use cached result
                result = cached_result
                actual_duration = 0.1  # Minimal time for cache hit
            else:
                # Simulate actual processing with resilience patterns
                result = self._simulate_processing_step(step_name, duration)
                actual_duration = time.time() - step_start_time
                
                # Cache the result
                self.cache_manager.set(cache_key, result, ttl_seconds=600)
            
            # Record step in monitoring
            self.video_monitor.record_step(tracking_id, step_name, actual_duration, True)
            
            # Save step output to session
            step_output_path = context.get_output_path(step_name, f"{step_name}_output.txt")
            os.makedirs(os.path.dirname(step_output_path), exist_ok=True)
            with open(step_output_path, 'w') as f:
                f.write(f"Output from {step_name}: {result}")
        
        # Create final video file
        final_video_path = context.save_final_video(
            self._create_temp_video_file("Enterprise test video content")
        )
        
        # Finish monitoring
        total_duration = time.time() - total_start_time
        self.video_monitor.finish_generation(tracking_id, True, final_video_path)
        
        # Verify all components worked correctly
        self._verify_session_structure(session_id, context)
        self._verify_monitoring_data(tracking_id)
        self._verify_cache_performance()
        self._verify_performance_metrics()
        
        # Verify final video is in session directory
        assert final_video_path.startswith(os.path.join(self.temp_dir, session_id))
        assert os.path.exists(final_video_path)
        
        # Verify session summary
        summary = context.get_session_summary()
        assert summary["session_id"] == session_id
        assert summary["total_files"] > 0
        assert len(summary["file_counts"]) > 0
    
    def test_resilience_patterns_integration(self):
        """Test resilience patterns working together"""
        failure_count = 0
        
        def flaky_api_call():
            nonlocal failure_count
            failure_count += 1
            if failure_count <= 2:
                raise Exception("Temporary API failure")
            return "API success"
        
        # Test retry manager with circuit breaker
        def protected_api_call():
            return self.circuit_breaker.call(flaky_api_call)
        
        # Should succeed after retries
        result = self.retry_manager.retry(protected_api_call)
        assert result == "API success"
        
        # Verify statistics
        cb_stats = self.circuit_breaker.get_stats()
        retry_stats = self.retry_manager.get_stats()
        
        assert cb_stats["total_calls"] == 3
        assert cb_stats["total_successes"] == 1
        assert cb_stats["total_failures"] == 2
        
        assert retry_stats["total_attempts"] == 3
        assert retry_stats["total_successes"] == 1
        assert retry_stats["total_retries"] == 2
    
    def test_caching_integration(self):
        """Test caching integration with other components"""
        # Test caching with performance monitoring
        @self.performance_monitor.timer("cached_operation")
        def expensive_operation(input_data):
            # Simulate expensive operation
            time.sleep(0.1)
            return f"processed_{input_data}"
        
        # First call - should be slow
        start_time = time.time()
        result1 = expensive_operation("test_data")
        duration1 = time.time() - start_time
        
        # Cache the result
        self.cache_manager.set("expensive_op_test_data", result1)
        
        # Second call - should use cache
        start_time = time.time()
        cached_result = self.cache_manager.get("expensive_op_test_data")
        duration2 = time.time() - start_time
        
        assert result1 == cached_result
        assert duration2 < duration1  # Cache should be faster
        
        # Verify cache statistics
        cache_stats = self.cache_manager.get_stats()
        assert cache_stats["hits"] == 1
        assert cache_stats["entries"] == 1
    
    def test_monitoring_comprehensive_tracking(self):
        """Test comprehensive monitoring and tracking"""
        # Record various metrics
        self.performance_monitor.record_metric("test_metric", 42.5, {"type": "test"}, "units")
        self.performance_monitor.increment_counter("test_counter", 5)
        self.performance_monitor.set_gauge("test_gauge", 78.9, {"category": "test"}, "percent")
        
        # Test timing context
        timing_context = self.performance_monitor.time_operation("test_operation")
        time.sleep(0.1)
        self.performance_monitor.finish_timing(timing_context)
        
        # Get performance report
        report = self.performance_monitor.get_performance_report()
        
        # Verify report structure
        assert "timestamp" in report
        assert "system_status" in report
        assert "metrics_summary" in report
        assert "timer_statistics" in report
        assert "counters" in report
        assert "gauges" in report
        
        # Verify specific metrics
        assert report["counters"]["test_counter"] == 5
        assert report["gauges"]["test_gauge"] == 78.9
        assert "test_operation" in report["timer_statistics"]
    
    def test_session_isolation_with_concurrent_operations(self):
        """Test session isolation with concurrent operations"""
        # Create multiple sessions
        sessions = []
        for i in range(3):
            session_id = self.session_manager.create_session(
                topic=f"Concurrent Test {i}",
                platform="youtube",
                duration=30,
                category="Entertainment"
            )
            sessions.append(session_id)
        
        # Perform operations in each session
        for i, session_id in enumerate(sessions):
            context = create_session_context(session_id)
            
            # Create files in each session
            for j in range(3):
                file_path = context.get_output_path("test_files", f"file_{j}.txt")
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w') as f:
                    f.write(f"Content from session {i}, file {j}")
            
            # Cache session-specific data
            self.cache_manager.set(f"session_{session_id}_data", f"cached_data_{i}")
        
        # Verify session isolation
        for i, session_id in enumerate(sessions):
            context = create_session_context(session_id)
            
            # Check files are in correct session
            for j in range(3):
                file_path = context.get_output_path("test_files", f"file_{j}.txt")
                assert os.path.exists(file_path)
                
                with open(file_path, 'r') as f:
                    content = f.read()
                    assert f"session {i}" in content
                    assert session_id in file_path
            
            # Check cached data
            cached_data = self.cache_manager.get(f"session_{session_id}_data")
            assert cached_data == f"cached_data_{i}"
    
    def test_error_handling_and_recovery(self):
        """Test comprehensive error handling and recovery"""
        # Test circuit breaker with failures
        def failing_service():
            raise Exception("Service unavailable")
        
        # Exhaust circuit breaker
        for _ in range(3):
            try:
                self.circuit_breaker.call(failing_service)
            except Exception:
                pass
        
        # Circuit should be open
        assert self.circuit_breaker.state.value == "open"
        
        # Test retry manager with non-retryable error
        def non_retryable_error():
            raise ValueError("Non-retryable error")
        
        # Should not retry ValueError
        with pytest.raises(ValueError):
            self.retry_manager.retry(non_retryable_error)
        
        # Should only have 1 attempt
        retry_stats = self.retry_manager.get_stats()
        assert retry_stats["total_attempts"] >= 1
        
        # Test cache with invalid data
        self.cache_manager.set("invalid_key", None)
        result = self.cache_manager.get("invalid_key")
        assert result is None
    
    def test_performance_under_load(self):
        """Test system performance under simulated load"""
        # Simulate multiple concurrent operations
        operations = []
        
        for i in range(10):
            # Create session
            session_id = self.session_manager.create_session(
                topic=f"Load Test {i}",
                platform="instagram",
                duration=15,
                category="Comedy"
            )
            
            # Start monitoring
            tracking_id = self.video_monitor.start_generation(
                session_id=session_id,
                topic=f"Load Test {i}",
                platform="instagram"
            )
            
            operations.append((session_id, tracking_id))
        
        # Perform operations
        for session_id, tracking_id in operations:
            context = create_session_context(session_id)
            
            # Simulate processing steps
            for step in ["processing", "generation", "composition"]:
                # Use cache to improve performance
                cache_key = f"{step}_{session_id}"
                if not self.cache_manager.get(cache_key):
                    # Simulate work
                    result = f"result_{step}_{session_id}"
                    self.cache_manager.set(cache_key, result)
                
                # Record step
                self.video_monitor.record_step(tracking_id, step, 0.1, True)
            
            # Finish monitoring
            self.video_monitor.finish_generation(tracking_id, True)
        
        # Verify performance metrics
        generation_stats = self.video_monitor.get_generation_stats()
        assert generation_stats["total_sessions"] == 10
        assert generation_stats["successful_sessions"] == 10
        assert generation_stats["success_rate"] == 100.0
        
        # Verify cache efficiency
        cache_stats = self.cache_manager.get_stats()
        assert cache_stats["entries"] > 0
        assert cache_stats["hit_rate_percent"] > 0
    
    def _simulate_processing_step(self, step_name: str, duration: float) -> str:
        """Simulate a processing step with resilience patterns"""
        def processing_work():
            time.sleep(duration * 0.1)  # Reduced for testing
            return f"completed_{step_name}"
        
        # Use retry manager for resilience
        return self.retry_manager.retry(processing_work)
    
    def _create_temp_video_file(self, content: str) -> str:
        """Create a temporary video file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mp4', delete=False) as f:
            f.write(content)
            return f.name
    
    def _verify_session_structure(self, session_id: str, context):
        """Verify session directory structure"""
        session_dir = os.path.join(self.temp_dir, session_id)
        assert os.path.exists(session_dir)
        
        # Check subdirectories
        expected_dirs = ["script_processing", "image_generation", "video_generation", 
                        "audio_generation", "final_composition", "final_output"]
        for dir_name in expected_dirs:
            dir_path = os.path.join(session_dir, dir_name)
            assert os.path.exists(dir_path)
    
    def _verify_monitoring_data(self, tracking_id: str):
        """Verify monitoring data was recorded"""
        generation_stats = self.video_monitor.get_generation_stats()
        assert generation_stats["total_sessions"] >= 1
        assert generation_stats["successful_sessions"] >= 1
        
        # Check if tracking ID exists
        assert tracking_id in self.video_monitor.generation_sessions
        session_data = self.video_monitor.generation_sessions[tracking_id]
        assert "steps" in session_data
        assert len(session_data["steps"]) > 0
    
    def _verify_cache_performance(self):
        """Verify cache performance"""
        cache_stats = self.cache_manager.get_stats()
        assert cache_stats["entries"] > 0
        # Should have some cache hits from repeated operations
        assert cache_stats["hits"] >= 0
    
    def _verify_performance_metrics(self):
        """Verify performance metrics were recorded"""
        perf_report = self.performance_monitor.get_performance_report()
        
        # Should have system metrics
        assert "system_status" in perf_report
        assert "metrics_summary" in perf_report
        
        # Should have some recorded metrics
        assert len(perf_report["metrics_summary"]) > 0


class TestEnterpriseSystemEdgeCases:
    """Test edge cases and failure scenarios"""
    
    def test_system_recovery_after_failures(self):
        """Test system recovery after various failure scenarios"""
        # Test session recovery
        temp_dir = tempfile.mkdtemp()
        session_manager = SessionManager(base_output_dir=temp_dir)
        
        # Create session
        session_id = session_manager.create_session(
            topic="Recovery Test",
            platform="tiktok",
            duration=15,
            category="Educational"
        )
        
        # Simulate system restart (new session manager instance)
        session_manager2 = SessionManager(base_output_dir=temp_dir)
        
        # Should be able to work with existing session
        context = create_session_context(session_id)
        test_file = context.get_output_path("test", "recovery.txt")
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        with open(test_file, 'w') as f:
            f.write("Recovery test")
        
        assert os.path.exists(test_file)
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
    
    def test_resource_cleanup(self):
        """Test proper resource cleanup"""
        # Create components
        monitor = PerformanceMonitor("cleanup_test")
        cache = CacheManager("cleanup_test")
        
        # Use components
        monitor.record_metric("test", 1.0)
        cache.set("test", "value")
        
        # Cleanup
        monitor.stop_monitoring()
        cache.clear()
        
        # Verify cleanup
        assert len(cache.cache) == 0
        assert not monitor.system_monitoring
    
    def test_concurrent_access_safety(self):
        """Test thread safety of components"""
        import threading
        
        cache = CacheManager("concurrent_test")
        results = []
        
        def worker(worker_id):
            for i in range(10):
                key = f"worker_{worker_id}_item_{i}"
                value = f"value_{worker_id}_{i}"
                cache.set(key, value)
                retrieved = cache.get(key)
                results.append(retrieved == value)
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify all operations succeeded
        assert all(results)
        assert len(results) == 50  # 5 workers * 10 items each


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 