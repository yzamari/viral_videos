#!/usr/bin/env python3
"""
Retry Manager - Intelligent retry mechanism with multiple strategies
"""

import time
import random
import logging
from typing import Any, Callable, Optional, Dict, List, Type
from dataclasses import dataclass
from enum import Enum
from functools import wraps

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
    Intelligent retry manager with multiple strategies and comprehensive monitoring
    """
    
    def __init__(self, name: str, config: Optional[RetryConfig] = None):
        """
        Initialize retry manager
        
        Args:
            name: Name of the retry manager
            config: Retry configuration
        """
        self.name = name
        self.config = config or RetryConfig()
        
        # Statistics
        self.total_attempts = 0
        self.total_successes = 0
        self.total_failures = 0
        self.total_retries = 0
        
        # Fibonacci sequence for fibonacci backoff
        self.fibonacci_sequence = [1, 1]
        
        logger.info(f"🔄 Retry manager '{name}' initialized with {self.config.strategy.value} strategy")
    
    def retry(self, func: Callable, *args, **kwargs) -> Any:
        """Alias for execute method for backwards compatibility"""
        return self.execute(func, *args, **kwargs)

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with retry logic
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            RetryExhaustedException: If all retries are exhausted
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
                logger.debug(f"Function executed successfully in {execution_time:.2f}s")
                return result
                
            except Exception as e:
                last_exception = e
                
                # Check if exception is retryable
                if not self._is_retryable(e):
                    logger.error(f"❌ Non-retryable exception in '{self.name}': {e}")
                    self.total_failures += 1
                    raise
                
                # If this was the last attempt, raise
                if attempt == self.config.max_retries:
                    logger.error(f"❌ Retry manager '{self.name}' exhausted all {self.config.max_retries + 1} attempts")
                    self.total_failures += 1
                    raise RetryExhaustedException(
                        f"Failed after {self.config.max_retries + 1} attempts",
                        attempt + 1,
                        e
                    )
                
                # Calculate delay and wait
                delay = self._calculate_delay(attempt)
                logger.warning(f"⚠️ Attempt {attempt + 1} failed for '{self.name}': {e}. Retrying in {delay:.2f}s...")
                time.sleep(delay)
    
    def _is_retryable(self, exception: Exception) -> bool:
        """
        Check if exception is retryable
        
        Args:
            exception: Exception to check
            
        Returns:
            True if retryable, False otherwise
        """
        # Check non-retryable exceptions first
        if self.config.non_retryable_exceptions:
            for exc_type in self.config.non_retryable_exceptions:
                if isinstance(exception, exc_type):
                    return False
        
        # Check retryable exceptions
        if self.config.retryable_exceptions:
            for exc_type in self.config.retryable_exceptions:
                if isinstance(exception, exc_type):
                    return True
            return False  # If specific retryable exceptions are defined, only those are retryable
        
        # Default: most exceptions are retryable except for specific ones
        non_retryable_defaults = [
            ValueError,
            TypeError,
            AttributeError,
            KeyError,
            IndexError,
            NotImplementedError
        ]
        
        for exc_type in non_retryable_defaults:
            if isinstance(exception, exc_type):
                return False
        
        return True
    
    def _calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay based on retry strategy
        
        Args:
            attempt: Current attempt number (0-indexed)
            
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
            # Extend fibonacci sequence if needed
            while len(self.fibonacci_sequence) <= attempt + 1:
                next_fib = self.fibonacci_sequence[-1] + self.fibonacci_sequence[-2]
                self.fibonacci_sequence.append(next_fib)
            
            delay = self.config.base_delay * self.fibonacci_sequence[attempt + 1]
        
        else:
            delay = self.config.base_delay
        
        # Apply max delay limit
        delay = min(delay, self.config.max_delay)
        
        # Add jitter if enabled
        if self.config.jitter:
            jitter_amount = delay * 0.1 * random.random()
            delay += jitter_amount
        
        return delay
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get retry statistics
        
        Returns:
            Dictionary with statistics
        """
        success_rate = (self.total_successes / self.total_attempts * 100) if self.total_attempts > 0 else 0
        avg_retries = (self.total_retries / self.total_successes) if self.total_successes > 0 else 0
        
        return {
            "name": self.name,
            "total_attempts": self.total_attempts,
            "total_successes": self.total_successes,
            "total_failures": self.total_failures,
            "total_retries": self.total_retries,
            "success_rate": success_rate,
            "average_retries_per_success": avg_retries,
            "strategy": self.config.strategy.value,
            "max_retries": self.config.max_retries
        }
    
    def reset_statistics(self) -> None:
        """Reset retry statistics"""
        self.total_attempts = 0
        self.total_successes = 0
        self.total_failures = 0
        self.total_retries = 0
        logger.info(f"🔄 Reset statistics for retry manager '{self.name}'")

def retry_on_failure(
    max_retries: int = 3,
    base_delay: float = 1.0,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
    retryable_exceptions: Optional[List[Type[Exception]]] = None,
    non_retryable_exceptions: Optional[List[Type[Exception]]] = None
):
    """
    Decorator for automatic retry on failure
    
    Args:
        max_retries: Maximum number of retries
        base_delay: Base delay between retries
        strategy: Retry strategy
        retryable_exceptions: List of exceptions that should trigger retry
        non_retryable_exceptions: List of exceptions that should not trigger retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            config = RetryConfig(
                max_retries=max_retries,
                base_delay=base_delay,
                strategy=strategy,
                retryable_exceptions=retryable_exceptions,
                non_retryable_exceptions=non_retryable_exceptions
            )
            
            retry_manager = RetryManager(func.__name__, config)
            return retry_manager.execute(func, *args, **kwargs)
        
        return wrapper
    return decorator

# Global retry managers for common use cases
api_retry_manager = RetryManager(
    "api_calls",
    RetryConfig(
        max_retries=3,
        base_delay=1.0,
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        retryable_exceptions=[ConnectionError, TimeoutError],
        non_retryable_exceptions=[ValueError, TypeError]
    )
)

file_retry_manager = RetryManager(
    "file_operations",
    RetryConfig(
        max_retries=5,
        base_delay=0.5,
        strategy=RetryStrategy.LINEAR_BACKOFF,
        retryable_exceptions=[OSError, IOError],
        non_retryable_exceptions=[FileNotFoundError, PermissionError]
    )
)

network_retry_manager = RetryManager(
    "network_operations",
    RetryConfig(
        max_retries=5,
        base_delay=2.0,
        strategy=RetryStrategy.FIBONACCI_BACKOFF,
        jitter=True
    )
)

def get_retry_manager(name: str) -> Optional[RetryManager]:
    """
    Get a predefined retry manager by name
    
    Args:
        name: Name of the retry manager
        
    Returns:
        Retry manager if found, None otherwise
    """
    managers = {
        "api": api_retry_manager,
        "file": file_retry_manager,
        "network": network_retry_manager
    }
    
    return managers.get(name)

def create_custom_retry_manager(name: str, **config_kwargs) -> RetryManager:
    """
    Create a custom retry manager with specific configuration
    
    Args:
        name: Name of the retry manager
        **config_kwargs: Configuration parameters
        
    Returns:
        Configured retry manager
    """
    config = RetryConfig(**config_kwargs)
    return RetryManager(name, config)

# Example usage and testing
if __name__ == "__main__":
    import requests
    
    # Example 1: Using retry manager directly
    def unreliable_api_call():
        response = requests.get("https://httpbin.org/status/500")
        response.raise_for_status()
        return response.json()
    
    try:
        result = api_retry_manager.execute(unreliable_api_call)
        print("API call succeeded:", result)
    except RetryExhaustedException as e:
        print(f"API call failed after {e.attempts} attempts: {e.last_exception}")
    
    # Example 2: Using decorator
    @retry_on_failure(max_retries=3, base_delay=0.5)
    def flaky_function():
        if random.random() < 0.7:  # 70% chance of failure
            raise ConnectionError("Network error")
        return "Success!"
    
    try:
        result = flaky_function()
        print("Function succeeded:", result)
    except RetryExhaustedException as e:
        print(f"Function failed: {e}")
    
    # Print statistics
    print("\nRetry Statistics:")
    print(api_retry_manager.get_statistics())
