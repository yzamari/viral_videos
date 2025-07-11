"""
Retry Manager with Exponential Backoff
Provides intelligent retry mechanisms for transient failures
"""

import time
import random
import logging
from typing import Callable, Any, Optional, Type, Union, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class RetryStrategy(Enum):
    """Retry strategies"""
    FIXED_DELAY = "fixed_delay"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIBONACCI_BACKOFF = "fibonacci_backoff"


@dataclass
class RetryConfig:
    """Configuration for retry manager"""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    jitter: bool = True
    backoff_multiplier: float = 2.0
    retryable_exceptions: Optional[List[Type[Exception]]] = None
    non_retryable_exceptions: Optional[List[Type[Exception]]] = None


class RetryExhaustedException(Exception):
    """Exception raised when all retry attempts are exhausted"""
    
    def __init__(self, message: str, attempts: int, last_exception: Exception):
        super().__init__(message)
        self.attempts = attempts
        self.last_exception = last_exception


class RetryManager:
    """
    Retry manager with configurable strategies and exponential backoff
    
    Provides intelligent retry mechanisms for handling transient failures
    with various backoff strategies and jitter to avoid thundering herd.
    """
    
    def __init__(self, name: str, config: Optional[RetryConfig] = None):
        """
        Initialize retry manager
        
        Args:
            name: Name of the retry manager for logging
            config: Configuration for retry behavior
        """
        self.name = name
        self.config = config or RetryConfig()
        
        # Statistics
        self.total_attempts = 0
        self.total_retries = 0
        self.total_successes = 0
        self.total_failures = 0
        
        logger.info(f"🔄 Retry manager '{name}' initialized with config: {self.config}")
    
    def retry(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with retry logic
        
        Args:
            func: Function to execute with retries
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function
            
        Returns:
            Result of successful function call
            
        Raises:
            RetryExhaustedException: When all retry attempts are exhausted
            Any non-retryable exception from the function
        """
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            self.total_attempts += 1
            
            try:
                start_time = time.time()
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                if attempt > 0:
                    logger.info(f"✅ Retry manager '{self.name}' succeeded on attempt {attempt + 1}")
                    self.total_retries += attempt
                
                self.total_successes += 1
                logger.debug(f"✅ Retry manager '{self.name}' call succeeded in {execution_time:.2f}s")
                
                return result
                
            except Exception as e:
                last_exception = e
                
                # Check if exception is retryable
                if not self._is_retryable_exception(e):
                    logger.error(f"❌ Retry manager '{self.name}' non-retryable exception: {e}")
                    raise e
                
                # If this was the last attempt, raise RetryExhaustedException
                if attempt >= self.config.max_retries:
                    self.total_failures += 1
                    error_msg = f"Retry manager '{self.name}' exhausted all {self.config.max_retries + 1} attempts"
                    logger.error(f"❌ {error_msg}, last exception: {e}")
                    raise RetryExhaustedException(error_msg, attempt + 1, e)
                
                # Calculate delay for next attempt
                delay = self._calculate_delay(attempt)
                
                logger.warning(f"⚠️ Retry manager '{self.name}' attempt {attempt + 1} failed: {e}")
                logger.info(f"🔄 Retrying in {delay:.2f}s (attempt {attempt + 2}/{self.config.max_retries + 1})")
                
                time.sleep(delay)
        
        # This should never be reached, but just in case
        self.total_failures += 1
        final_exception = last_exception or Exception(f"Unexpected retry exhaustion for '{self.name}'")
        raise RetryExhaustedException(f"Unexpected retry exhaustion for '{self.name}'", 
                                    self.config.max_retries + 1, final_exception)
    
    def _is_retryable_exception(self, exception: Exception) -> bool:
        """
        Check if an exception is retryable based on configuration
        
        Args:
            exception: Exception to check
            
        Returns:
            True if exception is retryable, False otherwise
        """
        # Check non-retryable exceptions first (takes precedence)
        if self.config.non_retryable_exceptions:
            for exc_type in self.config.non_retryable_exceptions:
                if isinstance(exception, exc_type):
                    return False
        
        # Check retryable exceptions
        if self.config.retryable_exceptions:
            for exc_type in self.config.retryable_exceptions:
                if isinstance(exception, exc_type):
                    return True
            # If retryable_exceptions is specified, only those are retryable
            return False
        
        # Default: most exceptions are retryable except certain types
        non_retryable_defaults = [
            ValueError,
            TypeError,
            AttributeError,
            ImportError,
            SyntaxError,
            KeyboardInterrupt,
        ]
        
        for exc_type in non_retryable_defaults:
            if isinstance(exception, exc_type):
                return False
        
        return True
    
    def _calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for next retry attempt based on strategy
        
        Args:
            attempt: Current attempt number (0-based)
            
        Returns:
            Delay in seconds
        """
        if self.config.strategy == RetryStrategy.FIXED_DELAY:
            delay = self.config.base_delay
            
        elif self.config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = self.config.base_delay * (self.config.backoff_multiplier ** attempt)
            
        elif self.config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = self.config.base_delay * (attempt + 1)
            
        elif self.config.strategy == RetryStrategy.FIBONACCI_BACKOFF:
            delay = self.config.base_delay * self._fibonacci(attempt + 1)
            
        else:
            # Default to exponential backoff
            delay = self.config.base_delay * (self.config.backoff_multiplier ** attempt)
        
        # Apply maximum delay limit
        delay = min(delay, self.config.max_delay)
        
        # Apply jitter to avoid thundering herd
        if self.config.jitter:
            jitter_range = delay * 0.1  # 10% jitter
            jitter = random.uniform(-jitter_range, jitter_range)
            delay = max(0.1, delay + jitter)  # Ensure minimum delay
        
        return delay
    
    def _fibonacci(self, n: int) -> int:
        """Calculate nth Fibonacci number for Fibonacci backoff"""
        if n <= 1:
            return n
        
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        
        return b
    
    def get_stats(self) -> dict:
        """
        Get retry manager statistics
        
        Returns:
            Dictionary with retry statistics
        """
        success_rate = (self.total_successes / self.total_attempts * 100) if self.total_attempts > 0 else 0
        failure_rate = (self.total_failures / self.total_attempts * 100) if self.total_attempts > 0 else 0
        avg_retries = (self.total_retries / self.total_successes) if self.total_successes > 0 else 0
        
        return {
            "name": self.name,
            "total_attempts": self.total_attempts,
            "total_retries": self.total_retries,
            "total_successes": self.total_successes,
            "total_failures": self.total_failures,
            "success_rate_percent": round(success_rate, 2),
            "failure_rate_percent": round(failure_rate, 2),
            "average_retries_per_success": round(avg_retries, 2),
            "config": {
                "max_retries": self.config.max_retries,
                "base_delay": self.config.base_delay,
                "max_delay": self.config.max_delay,
                "strategy": self.config.strategy.value,
                "jitter": self.config.jitter,
                "backoff_multiplier": self.config.backoff_multiplier
            }
        }
    
    def reset_stats(self):
        """Reset retry statistics"""
        self.total_attempts = 0
        self.total_retries = 0
        self.total_successes = 0
        self.total_failures = 0
        logger.info(f"📊 Reset statistics for retry manager '{self.name}'")


class RetryRegistry:
    """Registry for managing multiple retry managers"""
    
    def __init__(self):
        self.retry_managers: dict[str, RetryManager] = {}
    
    def get_or_create(self, name: str, config: Optional[RetryConfig] = None) -> RetryManager:
        """
        Get existing retry manager or create new one
        
        Args:
            name: Name of the retry manager
            config: Configuration for new retry manager
            
        Returns:
            RetryManager instance
        """
        if name not in self.retry_managers:
            self.retry_managers[name] = RetryManager(name, config)
        
        return self.retry_managers[name]
    
    def get_all_stats(self) -> dict:
        """
        Get statistics for all retry managers
        
        Returns:
            Dictionary with all retry manager statistics
        """
        return {
            name: rm.get_stats() 
            for name, rm in self.retry_managers.items()
        }
    
    def reset_all_stats(self):
        """Reset statistics for all retry managers"""
        for rm in self.retry_managers.values():
            rm.reset_stats()
        logger.info(f"📊 Reset statistics for {len(self.retry_managers)} retry managers")


# Global registry instance
retry_registry = RetryRegistry()


def retry(name: str, config: Optional[RetryConfig] = None):
    """
    Decorator for applying retry logic to functions
    
    Args:
        name: Name of the retry manager
        config: Configuration for retry behavior
        
    Returns:
        Decorated function with retry protection
    """
    def decorator(func: Callable):
        rm = retry_registry.get_or_create(name, config)
        
        def wrapper(*args, **kwargs):
            return rm.retry(func, *args, **kwargs)
        
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.retry_manager = rm
        
        return wrapper
    
    return decorator


# Convenience configurations for common scenarios
class CommonRetryConfigs:
    """Common retry configurations for different scenarios"""
    
    # Quick retries for fast operations
    FAST = RetryConfig(
        max_retries=2,
        base_delay=0.5,
        max_delay=5.0,
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF
    )
    
    # Standard retries for most operations
    STANDARD = RetryConfig(
        max_retries=3,
        base_delay=1.0,
        max_delay=30.0,
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF
    )
    
    # Aggressive retries for critical operations
    AGGRESSIVE = RetryConfig(
        max_retries=5,
        base_delay=1.0,
        max_delay=60.0,
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF
    )
    
    # API calls with rate limiting
    API_RATE_LIMITED = RetryConfig(
        max_retries=4,
        base_delay=2.0,
        max_delay=120.0,
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        jitter=True
    )
    
    # Network operations
    NETWORK = RetryConfig(
        max_retries=3,
        base_delay=1.0,
        max_delay=30.0,
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        retryable_exceptions=[
            ConnectionError,
            TimeoutError,
            OSError
        ]
    ) 