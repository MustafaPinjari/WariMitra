"""
Core utility functions and decorators
Used across the entire WariMitra backend
"""
import functools
import logging
import time
from typing import Any, Callable, Dict, Optional
from django.core.cache import cache
from django.utils.decorators import wraps
from django.http import JsonResponse
import json

logger = logging.getLogger(__name__)


# ============================================================================
# Caching Decorators
# ============================================================================

def cache_result(timeout: int = 300, key_prefix: str = None):
    """
    Cache function result in Redis.
    
    Args:
        timeout: Cache timeout in seconds (default: 5 min)
        key_prefix: Prefix for cache key (default: function name)
    
    Usage:
        @cache_result(timeout=600)
        def expensive_calculation():
            return sum(range(1000000))
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key
            prefix = key_prefix or func.__name__
            args_str = str(args) + str(kwargs)
            cache_key = f"{prefix}:{hash(args_str)}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            logger.debug(f"Cache set: {cache_key} ({timeout}s)")
            
            return result
        
        return wrapper
    return decorator


def cache_by_user(timeout: int = 300):
    """
    Cache function result per user.
    Requires first argument to be request object with user.
    
    Usage:
        @cache_by_user(timeout=600)
        def get_user_data(request):
            return request.user.profile.get_data()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not hasattr(request, 'user'):
                return func(request, *args, **kwargs)
            
            cache_key = f"{func.__name__}:user:{request.user.id}"
            result = cache.get(cache_key)
            
            if result is not None:
                return result
            
            result = func(request, *args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        
        return wrapper
    return decorator


# ============================================================================
# Performance/Timing Decorators
# ============================================================================

def measure_time(func: Callable) -> Callable:
    """
    Measure function execution time and log it.
    
    Usage:
        @measure_time
        def slow_function():
            time.sleep(1)
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        
        logger.info(f"{func.__name__} took {elapsed:.3f}s")
        
        if elapsed > 1.0:
            logger.warning(f"SLOW: {func.__name__} took {elapsed:.3f}s")
        
        return result
    
    return wrapper


def log_execution(level: str = "info"):
    """
    Log function execution with arguments and result.
    
    Usage:
        @log_execution(level="debug")
        def my_function(x, y):
            return x + y
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            log_func = getattr(logger, level.lower())
            
            # Log call
            log_func(f"→ {func.__name__} called")
            
            try:
                result = func(*args, **kwargs)
                log_func(f"← {func.__name__} returned")
                return result
            except Exception as e:
                logger.error(f"✗ {func.__name__} failed: {str(e)}")
                raise
        
        return wrapper
    return decorator


# ============================================================================
# Error Handling Utilities
# ============================================================================

class AppException(Exception):
    """Base exception for WariMitra app"""
    def __init__(self, message: str, code: str = "ERROR", status_code: int = 400, details: Dict = None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict:
        """Convert exception to API response dict"""
        return {
            'error': self.message,
            'code': self.code,
            'details': self.details
        }


class ValidationError(AppException):
    """Validation error"""
    def __init__(self, message: str, details: Dict = None):
        super().__init__(message, "VALIDATION_ERROR", 400, details)


class NotFoundError(AppException):
    """Resource not found"""
    def __init__(self, message: str, details: Dict = None):
        super().__init__(message, "NOT_FOUND", 404, details)


class PermissionError(AppException):
    """Permission denied"""
    def __init__(self, message: str, details: Dict = None):
        super().__init__(message, "PERMISSION_DENIED", 403, details)


class RateLimitError(AppException):
    """Rate limit exceeded"""
    def __init__(self, message: str = "Rate limit exceeded", details: Dict = None):
        super().__init__(message, "RATE_LIMIT_EXCEEDED", 429, details)


# ============================================================================
# Response Utilities
# ============================================================================

def success_response(data: Any = None, message: str = "Success", status_code: int = 200) -> Dict:
    """Create standardized success response"""
    return {
        'success': True,
        'message': message,
        'data': data,
        'status_code': status_code
    }


def error_response(message: str, code: str = "ERROR", status_code: int = 400, details: Dict = None) -> Dict:
    """Create standardized error response"""
    return {
        'success': False,
        'error': message,
        'code': code,
        'status_code': status_code,
        'details': details or {}
    }


def paginated_response(data: list, count: int, page: int, page_size: int) -> Dict:
    """Create paginated response"""
    total_pages = (count + page_size - 1) // page_size
    
    return {
        'success': True,
        'data': data,
        'pagination': {
            'total': count,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_previous': page > 1
        }
    }


# ============================================================================
# Validation Utilities
# ============================================================================

def validate_required_fields(data: Dict, required: list) -> Optional[Dict]:
    """
    Validate that required fields are present.
    
    Returns:
        None if valid, error dict if not
    
    Usage:
        error = validate_required_fields(request.data, ['name', 'email'])
        if error:
            return Response(error, status=400)
    """
    missing = []
    for field in required:
        if field not in data or data[field] is None or data[field] == '':
            missing.append(field)
    
    if missing:
        return error_response(
            f"Missing required fields: {', '.join(missing)}",
            "VALIDATION_ERROR",
            400,
            {'missing_fields': missing}
        )
    
    return None


def validate_email_format(email: str) -> bool:
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone_format(phone: str) -> bool:
    """Validate phone number format"""
    import re
    # Accepts various formats: +1234567890, 123-456-7890, (123) 456-7890, etc.
    pattern = r'^[\d\-\(\)\s\+]{7,}$'
    return re.match(pattern, phone) is not None


# ============================================================================
# Query Utilities
# ============================================================================

def get_object_or_404(model, **kwargs):
    """
    Get object or raise NotFoundError.
    
    Usage:
        user = get_object_or_404(User, id=user_id)
    """
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        raise NotFoundError(f"{model.__name__} not found")


def get_list_or_empty(model, **kwargs):
    """
    Get queryset or return empty list.
    
    Usage:
        users = get_list_or_empty(User, is_active=True)
    """
    return model.objects.filter(**kwargs, is_active=True)


# ============================================================================
# Serialization Utilities
# ============================================================================

def model_to_dict(instance, fields: list = None, exclude: list = None) -> Dict:
    """
    Convert model instance to dictionary.
    
    Usage:
        data = model_to_dict(user, fields=['id', 'username', 'email'])
    """
    if fields is None:
        fields = []
    if exclude is None:
        exclude = []
    
    result = {}
    
    # If fields specified, only include those
    if fields:
        for field in fields:
            if hasattr(instance, field):
                value = getattr(instance, field)
                result[field] = value
    else:
        # Include all fields except excluded ones
        for field in instance._meta.fields:
            if field.name not in exclude:
                value = getattr(instance, field.name)
                result[field.name] = value
    
    return result


# ============================================================================
# Audit Utilities
# ============================================================================

def log_audit_event(user_id: int, action: str, model_name: str, object_id: str, 
                    changes: Dict = None, details: str = ""):
    """
    Log an audit event.
    
    Usage:
        log_audit_event(
            user_id=request.user.id,
            action='create',
            model_name='Patient',
            object_id='123',
            changes={'name': 'John Doe'}
        )
    """
    from apps.audit.models import AuditLog
    
    try:
        AuditLog.objects.create(
            action=action,
            actor_id=user_id,
            model_name=model_name,
            object_id=object_id,
            changes=changes or {},
            details=details
        )
    except Exception as e:
        logger.error(f"Failed to log audit event: {str(e)}")


# ============================================================================
# Data Processing Utilities
# ============================================================================

def chunk_list(lst: list, chunk_size: int) -> list:
    """Split list into chunks"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """Flatten nested dictionary"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def merge_dicts(*dicts: Dict) -> Dict:
    """Merge multiple dictionaries"""
    result = {}
    for d in dicts:
        result.update(d)
    return result


# ============================================================================
# Type Conversion Utilities
# ============================================================================

def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert to int"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert to float"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_bool(value: Any) -> bool:
    """Safely convert to bool"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on')
    return bool(value)
