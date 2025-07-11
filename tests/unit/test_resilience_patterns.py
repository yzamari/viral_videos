"""
Unit tests for resilience patterns (Circuit Breaker and Retry Manager)
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# Add src to path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from shared.resilience.circuit_breaker import (
    CircuitBreaker, CircuitBreakerConfig, CircuitBreakerState,
    CircuitBreakerOpenException, CircuitBreakerTimeoutException,
    circuit_breaker, circuit_breaker_registry
)
from shared.resilience.retry_manager import (
    RetryManager, RetryConfig, RetryStrategy,
    RetryExhaustedException, retry, retry_registry,
    CommonRetryConfigs
)


class TestCircuitBreaker:
    """Test suite for Circuit Breaker pattern"""
    
    def setup_method(self):
        """Setup test environment"""
        self.config = CircuitBreakerConfig(
            failure_threshold=3,
            reset_timeout=1,
            success_threshold=2,
            timeout=1.0
        )
        self.cb = CircuitBreaker("test_cb", self.config)
    
    def test_circuit_breaker_initialization(self):
        """Test circuit breaker initialization"""
        assert self.cb.name == "test_cb"
        assert self.cb.state == CircuitBreakerState.CLOSED
        assert self.cb.failure_count == 0
        assert self.cb.success_count == 0
        assert self.cb.total_calls == 0
    
    def test_successful_calls(self):
        """Test successful function calls"""
        def success_func():
            return "success"
        
        # Multiple successful calls
        for i in range(5):
            result = self.cb.call(success_func)
            assert result == "success"
        
        # Verify statistics
        assert self.cb.total_calls == 5
        assert self.cb.total_successes == 5
        assert self.cb.total_failures == 0
        assert self.cb.state == CircuitBreakerState.CLOSED
    
    def test_failure_handling(self):
        """Test failure handling and state transitions"""
        def failure_func():
            raise Exception("Test failure")
        
        # Test failures below threshold
        for i in range(2):
            with pytest.raises(Exception):
                self.cb.call(failure_func)
        
        assert self.cb.state == CircuitBreakerState.CLOSED
        assert self.cb.failure_count == 2
        
        # One more failure should open the circuit
        with pytest.raises(Exception):
            self.cb.call(failure_func)
        
        assert self.cb.state == CircuitBreakerState.OPEN
        assert self.cb.failure_count == 3
    
    def test_circuit_breaker_open_state(self):
        """Test circuit breaker in open state"""
        # Force circuit to open
        self.cb.failure_count = self.config.failure_threshold
        self.cb._transition_to_open()
        
        def any_func():
            return "should not execute"
        
        # Calls should be blocked
        with pytest.raises(CircuitBreakerOpenException):
            self.cb.call(any_func)
        
        # Verify stats
        assert self.cb.total_calls == 1
        assert self.cb.total_successes == 0
        assert self.cb.total_failures == 0  # Not counted as failure, just blocked
    
    def test_half_open_state_transition(self):
        """Test transition from open to half-open state"""
        # Force circuit to open
        self.cb.failure_count = self.config.failure_threshold
        self.cb._transition_to_open()
        
        # Wait for reset timeout
        time.sleep(self.config.reset_timeout + 0.1)
        
        def success_func():
            return "success"
        
        # First call should transition to half-open
        result = self.cb.call(success_func)
        assert result == "success"
        assert self.cb.state == CircuitBreakerState.HALF_OPEN
        assert self.cb.success_count == 1
    
    def test_half_open_to_closed_transition(self):
        """Test transition from half-open to closed state"""
        # Set to half-open state
        self.cb.state = CircuitBreakerState.HALF_OPEN
        self.cb.success_count = 0
        
        def success_func():
            return "success"
        
        # Need success_threshold successes to close
        for i in range(self.config.success_threshold):
            result = self.cb.call(success_func)
            assert result == "success"
        
        assert self.cb.state == CircuitBreakerState.CLOSED
        assert self.cb.failure_count == 0
    
    def test_half_open_to_open_on_failure(self):
        """Test transition from half-open back to open on failure"""
        # Set to half-open state
        self.cb.state = CircuitBreakerState.HALF_OPEN
        self.cb.success_count = 1
        
        def failure_func():
            raise Exception("Test failure")
        
        # Failure should transition back to open
        with pytest.raises(Exception):
            self.cb.call(failure_func)
        
        assert self.cb.state == CircuitBreakerState.OPEN
        assert self.cb.success_count == 0
    
    def test_circuit_breaker_statistics(self):
        """Test circuit breaker statistics"""
        def success_func():
            return "success"
        
        def failure_func():
            raise Exception("Test failure")
        
        # Mix of successes and failures
        self.cb.call(success_func)
        self.cb.call(success_func)
        
        try:
            self.cb.call(failure_func)
        except:
            pass
        
        stats = self.cb.get_stats()
        
        assert stats["name"] == "test_cb"
        assert stats["total_calls"] == 3
        assert stats["total_successes"] == 2
        assert stats["total_failures"] == 1
        assert stats["success_rate_percent"] == 66.67
        assert stats["failure_rate_percent"] == 33.33
    
    def test_circuit_breaker_reset(self):
        """Test manual circuit breaker reset"""
        # Force failures and open state
        self.cb.failure_count = self.config.failure_threshold
        self.cb._transition_to_open()
        
        assert self.cb.state == CircuitBreakerState.OPEN
        
        # Reset circuit breaker
        self.cb.reset()
        
        assert self.cb.state == CircuitBreakerState.CLOSED
        assert self.cb.failure_count == 0
        assert self.cb.success_count == 0
    
    def test_circuit_breaker_decorator(self):
        """Test circuit breaker decorator"""
        @circuit_breaker("test_decorator", self.config)
        def test_function(should_fail=False):
            if should_fail:
                raise Exception("Test failure")
            return "success"
        
        # Test successful calls
        result = test_function()
        assert result == "success"
        
        # Test failure
        with pytest.raises(Exception):
            test_function(should_fail=True)
        
        # Verify decorator preserves function metadata
        assert test_function.__name__ == "test_function"
        assert hasattr(test_function, 'circuit_breaker')


class TestRetryManager:
    """Test suite for Retry Manager"""
    
    def setup_method(self):
        """Setup test environment"""
        self.config = RetryConfig(
            max_retries=3,
            base_delay=0.1,
            max_delay=1.0,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            jitter=False  # Disable jitter for predictable tests
        )
        self.rm = RetryManager("test_rm", self.config)
    
    def test_retry_manager_initialization(self):
        """Test retry manager initialization"""
        assert self.rm.name == "test_rm"
        assert self.rm.config.max_retries == 3
        assert self.rm.total_attempts == 0
        assert self.rm.total_successes == 0
        assert self.rm.total_failures == 0
    
    def test_successful_call_no_retry(self):
        """Test successful call without retries"""
        def success_func():
            return "success"
        
        result = self.rm.retry(success_func)
        
        assert result == "success"
        assert self.rm.total_attempts == 1
        assert self.rm.total_successes == 1
        assert self.rm.total_failures == 0
        assert self.rm.total_retries == 0
    
    def test_retry_on_failure(self):
        """Test retry mechanism on failures"""
        attempt_count = 0
        
        def retry_func():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise Exception("Temporary failure")
            return "success after retry"
        
        result = self.rm.retry(retry_func)
        
        assert result == "success after retry"
        assert attempt_count == 3
        assert self.rm.total_attempts == 3
        assert self.rm.total_successes == 1
        assert self.rm.total_retries == 2
    
    def test_retry_exhaustion(self):
        """Test retry exhaustion"""
        def always_fail():
            raise Exception("Always fails")
        
        with pytest.raises(RetryExhaustedException) as exc_info:
            self.rm.retry(always_fail)
        
        assert exc_info.value.attempts == 4  # max_retries + 1
        assert isinstance(exc_info.value.last_exception, Exception)
        assert self.rm.total_attempts == 4
        assert self.rm.total_failures == 1
    
    def test_non_retryable_exceptions(self):
        """Test non-retryable exceptions"""
        config = RetryConfig(
            max_retries=3,
            non_retryable_exceptions=[ValueError]
        )
        rm = RetryManager("test_non_retryable", config)
        
        def value_error_func():
            raise ValueError("Non-retryable error")
        
        # Should not retry ValueError
        with pytest.raises(ValueError):
            rm.retry(value_error_func)
        
        assert rm.total_attempts == 1
        assert rm.total_retries == 0
    
    def test_retryable_exceptions_only(self):
        """Test retryable exceptions configuration"""
        config = RetryConfig(
            max_retries=2,
            retryable_exceptions=[ConnectionError]
        )
        rm = RetryManager("test_retryable_only", config)
        
        def connection_error_func():
            raise ConnectionError("Connection failed")
        
        def value_error_func():
            raise ValueError("Value error")
        
        # ConnectionError should be retried
        with pytest.raises(RetryExhaustedException):
            rm.retry(connection_error_func)
        
        assert rm.total_attempts == 3  # max_retries + 1
        
        # ValueError should not be retried
        with pytest.raises(ValueError):
            rm.retry(value_error_func)
        
        assert rm.total_attempts == 4  # Previous 3 + 1
    
    def test_exponential_backoff_strategy(self):
        """Test exponential backoff delay calculation"""
        delays = []
        
        for attempt in range(3):
            delay = self.rm._calculate_delay(attempt)
            delays.append(delay)
        
        # Should be exponentially increasing
        assert delays[0] == 0.1  # base_delay
        assert delays[1] == 0.2  # base_delay * 2^1
        assert delays[2] == 0.4  # base_delay * 2^2
    
    def test_linear_backoff_strategy(self):
        """Test linear backoff delay calculation"""
        config = RetryConfig(
            base_delay=0.1,
            strategy=RetryStrategy.LINEAR_BACKOFF,
            jitter=False
        )
        rm = RetryManager("test_linear", config)
        
        delays = []
        for attempt in range(3):
            delay = rm._calculate_delay(attempt)
            delays.append(delay)
        
        # Should be linearly increasing
        assert delays[0] == 0.1  # base_delay * 1
        assert delays[1] == 0.2  # base_delay * 2
        assert delays[2] == 0.3  # base_delay * 3
    
    def test_fixed_delay_strategy(self):
        """Test fixed delay strategy"""
        config = RetryConfig(
            base_delay=0.5,
            strategy=RetryStrategy.FIXED_DELAY,
            jitter=False
        )
        rm = RetryManager("test_fixed", config)
        
        delays = []
        for attempt in range(3):
            delay = rm._calculate_delay(attempt)
            delays.append(delay)
        
        # Should be constant
        assert all(delay == 0.5 for delay in delays)
    
    def test_max_delay_limit(self):
        """Test maximum delay limit"""
        config = RetryConfig(
            base_delay=1.0,
            max_delay=2.0,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            jitter=False
        )
        rm = RetryManager("test_max_delay", config)
        
        # Large attempt number should be capped at max_delay
        delay = rm._calculate_delay(10)
        assert delay == 2.0
    
    def test_retry_statistics(self):
        """Test retry statistics"""
        attempt_count = 0
        
        def sometimes_fail():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count == 1:
                raise Exception("First attempt fails")
            return "success"
        
        # First call with retry
        result = self.rm.retry(sometimes_fail)
        assert result == "success"
        
        # Second call without retry
        attempt_count = 0
        result = self.rm.retry(sometimes_fail)
        assert result == "success"
        
        stats = self.rm.get_stats()
        
        assert stats["name"] == "test_rm"
        assert stats["total_attempts"] == 3  # 2 + 1
        assert stats["total_successes"] == 2
        assert stats["total_retries"] == 1
        assert stats["average_retries_per_success"] == 0.5
    
    def test_retry_decorator(self):
        """Test retry decorator"""
        @retry("test_decorator", self.config)
        def test_function(should_fail=False):
            if should_fail:
                raise Exception("Test failure")
            return "success"
        
        # Test successful call
        result = test_function()
        assert result == "success"
        
        # Test failure with retries
        with pytest.raises(RetryExhaustedException):
            test_function(should_fail=True)
        
        # Verify decorator preserves function metadata
        assert test_function.__name__ == "test_function"
        assert hasattr(test_function, 'retry_manager')
    
    def test_common_retry_configs(self):
        """Test common retry configurations"""
        # Test that common configs are properly defined
        assert CommonRetryConfigs.FAST.max_retries == 2
        assert CommonRetryConfigs.STANDARD.max_retries == 3
        assert CommonRetryConfigs.AGGRESSIVE.max_retries == 5
        assert CommonRetryConfigs.API_RATE_LIMITED.max_retries == 4
        assert CommonRetryConfigs.NETWORK.max_retries == 3
        
        # Test that network config has proper exceptions
        assert ConnectionError in CommonRetryConfigs.NETWORK.retryable_exceptions
        assert TimeoutError in CommonRetryConfigs.NETWORK.retryable_exceptions


class TestResilienceIntegration:
    """Integration tests for resilience patterns"""
    
    def test_circuit_breaker_with_retry(self):
        """Test circuit breaker combined with retry manager"""
        # Create circuit breaker and retry manager
        cb_config = CircuitBreakerConfig(failure_threshold=2, reset_timeout=1)
        cb = CircuitBreaker("integration_cb", cb_config)
        
        retry_config = RetryConfig(max_retries=3, base_delay=0.1)
        rm = RetryManager("integration_rm", retry_config)
        
        failure_count = 0
        
        def flaky_service():
            nonlocal failure_count
            failure_count += 1
            if failure_count <= 5:
                raise Exception("Service temporarily unavailable")
            return "success"
        
        # First, test retry manager alone
        with pytest.raises(RetryExhaustedException):
            rm.retry(flaky_service)
        
        # Reset failure count
        failure_count = 0
        
        # Now test with circuit breaker
        def protected_service():
            return cb.call(flaky_service)
        
        # Should fail and open circuit
        with pytest.raises(Exception):
            rm.retry(protected_service)
        
        # Circuit should be open now
        assert cb.state == CircuitBreakerState.OPEN
        
        # Subsequent calls should be blocked by circuit breaker
        with pytest.raises(CircuitBreakerOpenException):
            rm.retry(protected_service)
    
    def test_registry_functionality(self):
        """Test circuit breaker and retry manager registries"""
        # Test circuit breaker registry
        cb1 = circuit_breaker_registry.get_or_create("test_cb_1")
        cb2 = circuit_breaker_registry.get_or_create("test_cb_1")  # Same name
        cb3 = circuit_breaker_registry.get_or_create("test_cb_2")  # Different name
        
        assert cb1 is cb2  # Should be same instance
        assert cb1 is not cb3  # Should be different instances
        
        # Test retry manager registry
        rm1 = retry_registry.get_or_create("test_rm_1")
        rm2 = retry_registry.get_or_create("test_rm_1")  # Same name
        rm3 = retry_registry.get_or_create("test_rm_2")  # Different name
        
        assert rm1 is rm2  # Should be same instance
        assert rm1 is not rm3  # Should be different instances
        
        # Test statistics
        cb_stats = circuit_breaker_registry.get_all_stats()
        rm_stats = retry_registry.get_all_stats()
        
        assert "test_cb_1" in cb_stats
        assert "test_cb_2" in cb_stats
        assert "test_rm_1" in rm_stats
        assert "test_rm_2" in rm_stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 