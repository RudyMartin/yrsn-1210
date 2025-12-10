"""Retry logic and error handling utilities."""

import asyncio
import time
from typing import Callable, TypeVar, Optional, List, Type
from functools import wraps
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        retryable_exceptions: Optional[List[Type[Exception]]] = None,
        on_retry: Optional[Callable[[Exception, int], None]] = None
    ):
        """
        Initialize retry configuration.
        
        Args:
            max_attempts: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential backoff
            retryable_exceptions: List of exception types to retry on
            on_retry: Callback function called on each retry
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.retryable_exceptions = retryable_exceptions or [Exception]
        self.on_retry = on_retry


def retry_async(
    config: Optional[RetryConfig] = None,
    retryable_exceptions: Optional[List[Type[Exception]]] = None
):
    """
    Decorator for async functions with retry logic.
    
    Args:
        config: Retry configuration
        retryable_exceptions: List of exception types to retry on
    """
    if config is None:
        config = RetryConfig()
    
    if retryable_exceptions:
        config.retryable_exceptions = retryable_exceptions
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            delay = config.initial_delay
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    # Check if exception is retryable
                    if not any(isinstance(e, exc_type) for exc_type in config.retryable_exceptions):
                        raise
                    
                    last_exception = e
                    
                    if attempt < config.max_attempts:
                        if config.on_retry:
                            config.on_retry(e, attempt)
                        else:
                            logger.warning(
                                f"Retry {attempt}/{config.max_attempts} for {func.__name__}: {str(e)}"
                            )
                        
                        await asyncio.sleep(delay)
                        delay = min(delay * config.exponential_base, config.max_delay)
                    else:
                        logger.error(
                            f"Max retries ({config.max_attempts}) exceeded for {func.__name__}"
                        )
                        raise
            
            # Should never reach here, but just in case
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


def retry_sync(
    config: Optional[RetryConfig] = None,
    retryable_exceptions: Optional[List[Type[Exception]]] = None
):
    """
    Decorator for sync functions with retry logic.
    
    Args:
        config: Retry configuration
        retryable_exceptions: List of exception types to retry on
    """
    if config is None:
        config = RetryConfig()
    
    if retryable_exceptions:
        config.retryable_exceptions = retryable_exceptions
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            delay = config.initial_delay
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # Check if exception is retryable
                    if not any(isinstance(e, exc_type) for exc_type in config.retryable_exceptions):
                        raise
                    
                    last_exception = e
                    
                    if attempt < config.max_attempts:
                        if config.on_retry:
                            config.on_retry(e, attempt)
                        else:
                            logger.warning(
                                f"Retry {attempt}/{config.max_attempts} for {func.__name__}: {str(e)}"
                            )
                        
                        time.sleep(delay)
                        delay = min(delay * config.exponential_base, config.max_delay)
                    else:
                        logger.error(
                            f"Max retries ({config.max_attempts}) exceeded for {func.__name__}"
                        )
                        raise
            
            # Should never reach here, but just in case
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


