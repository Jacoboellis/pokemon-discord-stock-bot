"""
Centralized error handling and monitoring utilities
"""
import logging
import functools
import os
from typing import Any, Callable
import asyncio

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Centralized error handler with optional monitoring integration"""
    
    def __init__(self, enable_sentry: bool = False):
        self.enable_sentry = enable_sentry
        self.error_counts = {}
        
        if enable_sentry:
            try:
                import sentry_sdk
                sentry_dsn = os.getenv('SENTRY_DSN')
                if sentry_dsn:
                    sentry_sdk.init(
                        dsn=sentry_dsn,
                        traces_sample_rate=0.1,  # 10% performance monitoring
                        profiles_sample_rate=0.1,  # 10% profiling
                    )
                    logger.info("Sentry error monitoring initialized")
                else:
                    logger.warning("SENTRY_DSN not found, Sentry monitoring disabled")
                    self.enable_sentry = False
            except ImportError:
                logger.warning("Sentry SDK not installed, monitoring disabled")
                self.enable_sentry = False
    
    def log_error(self, error: Exception, context: str = "", extra_data: dict = None):
        """Log error with context and optional extra data"""
        error_type = type(error).__name__
        error_msg = str(error)
        
        # Count errors by type
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Prepare log message
        log_context = f" [{context}]" if context else ""
        logger.error(
            f"{error_type}{log_context}: {error_msg}",
            extra=extra_data or {},
            exc_info=True
        )
        
        # Send to Sentry if enabled
        if self.enable_sentry:
            try:
                import sentry_sdk
                with sentry_sdk.push_scope() as scope:
                    if context:
                        scope.set_tag("context", context)
                    if extra_data:
                        for key, value in extra_data.items():
                            scope.set_extra(key, value)
                    sentry_sdk.capture_exception(error)
            except Exception as e:
                logger.error(f"Failed to send error to Sentry: {e}")
    
    def get_error_summary(self) -> dict:
        """Get summary of error counts"""
        return dict(self.error_counts)


def async_error_handler(context: str = "", reraise: bool = False, default_return: Any = None):
    """Decorator for async functions to handle errors gracefully"""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_handler = getattr(wrapper, '_error_handler', None)
                if error_handler:
                    error_handler.log_error(e, context or func.__name__, {
                        'function': func.__name__,
                        'args': str(args)[:200],  # Truncate long args
                        'kwargs': str(kwargs)[:200]
                    })
                else:
                    logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
                
                if reraise:
                    raise
                return default_return
        
        return wrapper
    return decorator


def sync_error_handler(context: str = "", reraise: bool = False, default_return: Any = None):
    """Decorator for sync functions to handle errors gracefully"""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler = getattr(wrapper, '_error_handler', None)
                if error_handler:
                    error_handler.log_error(e, context or func.__name__, {
                        'function': func.__name__,
                        'args': str(args)[:200],
                        'kwargs': str(kwargs)[:200]
                    })
                else:
                    logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
                
                if reraise:
                    raise
                return default_return
        
        return wrapper
    return decorator


class RetryHandler:
    """Handles retry logic for operations that may fail temporarily"""
    
    @staticmethod
    async def retry_async(
        func: Callable,
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff_factor: float = 2.0,
        exceptions: tuple = (Exception,)
    ):
        """Retry an async function with exponential backoff"""
        last_exception = None
        
        for attempt in range(max_attempts):
            try:
                return await func()
            except exceptions as e:
                last_exception = e
                if attempt == max_attempts - 1:
                    break
                
                wait_time = delay * (backoff_factor ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                await asyncio.sleep(wait_time)
        
        raise last_exception
    
    @staticmethod
    def retry_sync(
        func: Callable,
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff_factor: float = 2.0,
        exceptions: tuple = (Exception,)
    ):
        """Retry a sync function with exponential backoff"""
        import time
        last_exception = None
        
        for attempt in range(max_attempts):
            try:
                return func()
            except exceptions as e:
                last_exception = e
                if attempt == max_attempts - 1:
                    break
                
                wait_time = delay * (backoff_factor ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
        
        raise last_exception


# Global error handler instance
global_error_handler = ErrorHandler()