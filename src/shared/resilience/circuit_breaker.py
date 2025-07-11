"""
Circuit Breaker Pattern Implementation
Provides resilience for external API calls with automatic failure detection and recovery
"""

import time
import logging
from enum import Enum
from typing import Callable, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, blocking calls
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5          # Number of failures before opening
    reset_timeout: int = 60             # Seconds before trying to close again
    success_threshold: int = 3          # Successes needed in half-open to close
    timeout: float = 30.0               # Timeout for individual calls


class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open"""
    
    def __init__(self, message: str, last_failure_time: Optional[datetime] = None):
        super().__init__(message)
        self.last_failure_time = last_failure_time


class CircuitBreakerTimeoutException(Exception):
    """Exception raised when call times out"""
    pass


class CircuitBreaker:
    """
    Circuit breaker for external API calls
    
    Implements the circuit breaker pattern to provide resilience against
    failing external services by monitoring failures and temporarily
    blocking calls when failure rate is too high.
    """
    
    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        """
        Initialize circuit breaker
        
        Args:
            name: Name of the circuit breaker for logging
            config: Configuration for the circuit breaker
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        
        # State management
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_success_time: Optional[datetime] = None
        
        # Statistics
        self.total_calls = 0
        self.total_failures = 0
        self.total_successes = 0
        self.total_timeouts = 0
        
        logger.info(f"🔧 Circuit breaker '{name}' initialized with config: {self.config}")
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection
        
        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function
            
        Returns:
            Result of function call
            
        Raises:
            CircuitBreakerOpenException: When circuit breaker is open
            CircuitBreakerTimeoutException: When call times out
            Any exception raised by the function
        """
        self.total_calls += 1
        
        # Check if circuit breaker should transition states
        self._check_state_transition()
        
        # Block calls if circuit breaker is open
        if self.state == CircuitBreakerState.OPEN:
            error_msg = f"Circuit breaker '{self.name}' is OPEN - blocking call"
            logger.warning(error_msg)
            raise CircuitBreakerOpenException(error_msg, self.last_failure_time)
        
        # Execute the function call
        start_time = time.time()
        try:
            # Set timeout for the call
            import signal
            
            def timeout_handler(signum, frame):
                raise CircuitBreakerTimeoutException(f"Call to '{self.name}' timed out after {self.config.timeout}s")
            
            # Set timeout (Unix-like systems only)
            try:
                old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(int(self.config.timeout))
                
                result = func(*args, **kwargs)
                
                signal.alarm(0)  # Cancel alarm
                signal.signal(signal.SIGALRM, old_handler)
                
            except AttributeError:
                # Windows doesn't support SIGALRM, execute without timeout
                result = func(*args, **kwargs)
            
            # Record success
            self._on_success()
            
            execution_time = time.time() - start_time
            logger.debug(f"✅ Circuit breaker '{self.name}' call succeeded in {execution_time:.2f}s")
            
            return result
            
        except CircuitBreakerTimeoutException as e:
            self.total_timeouts += 1
            self._on_failure()
            logger.error(f"⏰ Circuit breaker '{self.name}' call timed out: {e}")
            raise e
            
        except Exception as e:
            self._on_failure()
            execution_time = time.time() - start_time
            logger.error(f"❌ Circuit breaker '{self.name}' call failed after {execution_time:.2f}s: {e}")
            raise e
        
        finally:
            # Ensure alarm is cancelled (Unix-like systems)
            try:
                signal.alarm(0)
            except AttributeError:
                pass
    
    def _check_state_transition(self):
        """Check if circuit breaker should transition to a different state"""
        current_time = datetime.now()
        
        if self.state == CircuitBreakerState.OPEN:
            # Check if we should transition to half-open
            if (self.last_failure_time and 
                current_time - self.last_failure_time >= timedelta(seconds=self.config.reset_timeout)):
                self._transition_to_half_open()
        
        elif self.state == CircuitBreakerState.HALF_OPEN:
            # Check if we should transition to closed (enough successes)
            if self.success_count >= self.config.success_threshold:
                self._transition_to_closed()
    
    def _on_success(self):
        """Handle successful call"""
        self.total_successes += 1
        self.last_success_time = datetime.now()
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            logger.info(f"🟡 Circuit breaker '{self.name}' half-open success {self.success_count}/{self.config.success_threshold}")
        
        elif self.state == CircuitBreakerState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed call"""
        self.total_failures += 1
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        # Reset success count if we were in half-open state
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count = 0
            self._transition_to_open()
        
        # Check if we should open the circuit breaker
        elif (self.state == CircuitBreakerState.CLOSED and 
              self.failure_count >= self.config.failure_threshold):
            self._transition_to_open()
    
    def _transition_to_open(self):
        """Transition circuit breaker to open state"""
        old_state = self.state
        self.state = CircuitBreakerState.OPEN
        self.success_count = 0
        logger.warning(f"🔴 Circuit breaker '{self.name}' transitioned from {old_state.value} to OPEN")
        logger.warning(f"   Failure count: {self.failure_count}/{self.config.failure_threshold}")
        logger.warning(f"   Will retry in {self.config.reset_timeout} seconds")
    
    def _transition_to_half_open(self):
        """Transition circuit breaker to half-open state"""
        old_state = self.state
        self.state = CircuitBreakerState.HALF_OPEN
        self.success_count = 0
        logger.info(f"🟡 Circuit breaker '{self.name}' transitioned from {old_state.value} to HALF_OPEN")
        logger.info(f"   Testing service recovery, need {self.config.success_threshold} successes to close")
    
    def _transition_to_closed(self):
        """Transition circuit breaker to closed state"""
        old_state = self.state
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        logger.info(f"🟢 Circuit breaker '{self.name}' transitioned from {old_state.value} to CLOSED")
        logger.info(f"   Service recovered, normal operation resumed")
    
    def get_stats(self) -> dict:
        """
        Get circuit breaker statistics
        
        Returns:
            Dictionary with circuit breaker statistics
        """
        success_rate = (self.total_successes / self.total_calls * 100) if self.total_calls > 0 else 0
        failure_rate = (self.total_failures / self.total_calls * 100) if self.total_calls > 0 else 0
        timeout_rate = (self.total_timeouts / self.total_calls * 100) if self.total_calls > 0 else 0
        
        return {
            "name": self.name,
            "state": self.state.value,
            "total_calls": self.total_calls,
            "total_successes": self.total_successes,
            "total_failures": self.total_failures,
            "total_timeouts": self.total_timeouts,
            "success_rate_percent": round(success_rate, 2),
            "failure_rate_percent": round(failure_rate, 2),
            "timeout_rate_percent": round(timeout_rate, 2),
            "current_failure_count": self.failure_count,
            "current_success_count": self.success_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "last_success_time": self.last_success_time.isoformat() if self.last_success_time else None,
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "reset_timeout": self.config.reset_timeout,
                "success_threshold": self.config.success_threshold,
                "timeout": self.config.timeout
            }
        }
    
    def reset(self):
        """
        Manually reset circuit breaker to closed state
        
        Use this for administrative override or testing
        """
        old_state = self.state
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        logger.info(f"🔄 Circuit breaker '{self.name}' manually reset from {old_state.value} to CLOSED")
    
    def force_open(self):
        """
        Manually force circuit breaker to open state
        
        Use this for maintenance or testing
        """
        old_state = self.state
        self.state = CircuitBreakerState.OPEN
        self.last_failure_time = datetime.now()
        logger.warning(f"⚠️ Circuit breaker '{self.name}' manually forced from {old_state.value} to OPEN")


class CircuitBreakerRegistry:
    """Registry for managing multiple circuit breakers"""
    
    def __init__(self):
        self.circuit_breakers: dict[str, CircuitBreaker] = {}
    
    def get_or_create(self, name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
        """
        Get existing circuit breaker or create new one
        
        Args:
            name: Name of the circuit breaker
            config: Configuration for new circuit breaker
            
        Returns:
            CircuitBreaker instance
        """
        if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker(name, config)
        
        return self.circuit_breakers[name]
    
    def get_all_stats(self) -> dict:
        """
        Get statistics for all circuit breakers
        
        Returns:
            Dictionary with all circuit breaker statistics
        """
        return {
            name: cb.get_stats() 
            for name, cb in self.circuit_breakers.items()
        }
    
    def reset_all(self):
        """Reset all circuit breakers to closed state"""
        for cb in self.circuit_breakers.values():
            cb.reset()
        logger.info(f"🔄 Reset {len(self.circuit_breakers)} circuit breakers")


# Global registry instance
circuit_breaker_registry = CircuitBreakerRegistry()


def circuit_breaker(name: str, config: Optional[CircuitBreakerConfig] = None):
    """
    Decorator for applying circuit breaker to functions
    
    Args:
        name: Name of the circuit breaker
        config: Configuration for the circuit breaker
        
    Returns:
        Decorated function with circuit breaker protection
    """
    def decorator(func: Callable):
        cb = circuit_breaker_registry.get_or_create(name, config)
        
        def wrapper(*args, **kwargs):
            return cb.call(func, *args, **kwargs)
        
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.circuit_breaker = cb
        
        return wrapper
    
    return decorator 