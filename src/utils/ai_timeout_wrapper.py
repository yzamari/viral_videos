"""
AI Timeout Wrapper
Ensures all AI calls have timeouts to prevent indefinite hanging
"""
import asyncio
import functools
import time
from typing import Any, Callable, Optional, TypeVar, Union
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

class AITimeoutError(Exception):
    """Raised when an AI call times out"""
    pass

def with_timeout(timeout_seconds: float = 30.0, default_value: Any = None):
    """
    Decorator that adds timeout to any function call.
    Works with both sync and async functions.
    
    Args:
        timeout_seconds: Maximum time to wait for the function to complete
        default_value: Value to return if the function times out
    """
    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):
            # Async function
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    logger.debug(f"⏱️ Starting {func.__name__} with {timeout_seconds}s timeout")
                    start_time = time.time()
                    
                    result = await asyncio.wait_for(
                        func(*args, **kwargs),
                        timeout=timeout_seconds
                    )
                    
                    elapsed = time.time() - start_time
                    logger.debug(f"✅ {func.__name__} completed in {elapsed:.1f}s")
                    return result
                    
                except asyncio.TimeoutError:
                    elapsed = time.time() - start_time
                    logger.warning(f"⚠️ {func.__name__} timed out after {elapsed:.1f}s - using fallback")
                    if default_value is not None:
                        return default_value
                    raise AITimeoutError(f"{func.__name__} timed out after {timeout_seconds}s")
                    
            return async_wrapper
        else:
            # Sync function
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                try:
                    logger.debug(f"⏱️ Starting {func.__name__} with {timeout_seconds}s timeout")
                    start_time = time.time()
                    
                    # Run in thread pool to enable timeout
                    with ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(func, *args, **kwargs)
                        result = future.result(timeout=timeout_seconds)
                    
                    elapsed = time.time() - start_time
                    logger.debug(f"✅ {func.__name__} completed in {elapsed:.1f}s")
                    return result
                    
                except (FutureTimeoutError, TimeoutError):
                    elapsed = time.time() - start_time
                    logger.warning(f"⚠️ {func.__name__} timed out after {elapsed:.1f}s - using fallback")
                    if default_value is not None:
                        return default_value
                    raise AITimeoutError(f"{func.__name__} timed out after {timeout_seconds}s")
                    
            return sync_wrapper
    return decorator

def run_with_timeout(
    func: Callable,
    args: tuple = (),
    kwargs: dict = None,
    timeout_seconds: float = 30.0,
    default_value: Any = None
) -> Any:
    """
    Run a function with a timeout.
    
    Args:
        func: The function to run
        args: Positional arguments for the function
        kwargs: Keyword arguments for the function
        timeout_seconds: Maximum time to wait
        default_value: Value to return on timeout
        
    Returns:
        The function result or default_value on timeout
    """
    if kwargs is None:
        kwargs = {}
    
    try:
        logger.debug(f"⏱️ Running {func.__name__} with {timeout_seconds}s timeout")
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(func, *args, **kwargs)
            result = future.result(timeout=timeout_seconds)
        
        elapsed = time.time() - start_time
        logger.debug(f"✅ {func.__name__} completed in {elapsed:.1f}s")
        return result
        
    except (FutureTimeoutError, TimeoutError):
        elapsed = time.time() - start_time
        logger.warning(f"⚠️ {func.__name__} timed out after {elapsed:.1f}s")
        if default_value is not None:
            logger.info(f"📌 Using default value for {func.__name__}")
            return default_value
        raise AITimeoutError(f"{func.__name__} timed out after {timeout_seconds}s")

class AICallWrapper:
    """
    Wrapper for AI service calls with automatic timeout handling.
    """
    
    def __init__(self, timeout_seconds: float = 30.0):
        self.timeout_seconds = timeout_seconds
        logger.info(f"🛡️ AI Call Wrapper initialized with {timeout_seconds}s timeout")
    
    def wrap_method(self, method: Callable, default_value: Any = None) -> Callable:
        """
        Wrap a method with timeout protection.
        
        Args:
            method: The method to wrap
            default_value: Default value to return on timeout
            
        Returns:
            Wrapped method with timeout protection
        """
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            return run_with_timeout(
                method,
                args,
                kwargs,
                timeout_seconds=self.timeout_seconds,
                default_value=default_value
            )
        return wrapper
    
    def safe_ai_call(
        self,
        func: Callable,
        *args,
        fallback_value: Any = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Any:
        """
        Make a safe AI call with timeout and fallback.
        
        Args:
            func: The function to call
            *args: Positional arguments
            fallback_value: Value to return on timeout
            timeout: Custom timeout (uses default if None)
            **kwargs: Keyword arguments
            
        Returns:
            Function result or fallback value
        """
        timeout_seconds = timeout or self.timeout_seconds
        
        try:
            return run_with_timeout(
                func,
                args,
                kwargs,
                timeout_seconds=timeout_seconds,
                default_value=fallback_value
            )
        except AITimeoutError as e:
            logger.error(f"❌ AI call failed: {e}")
            if fallback_value is not None:
                logger.info(f"📌 Using fallback value")
                return fallback_value
            raise

# Global instance for easy access - increased timeout for complex AI operations
ai_wrapper = AICallWrapper(timeout_seconds=90.0)