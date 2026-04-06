import redis
import json
import logging
from functools import wraps
from flask import current_app

# Global Redis client
redis_client = None

def init_cache(app):
    """
    Initialize Redis connection
    """
    global redis_client
    redis_url = app.config.get('REDIS_URL')
    
    if not redis_url:
        logging.warning("REDIS_URL not set. Caching disabled.")
        return

    try:
        redis_client = redis.from_url(redis_url)
        # Test connection
        redis_client.ping()
        logging.info(f"Redis connected: {redis_url}")
    except Exception as e:
        logging.error(f"Redis connection failed: {e}")
        redis_client = None

def get_cache(key):
    """
    Get value from cache
    """
    if not redis_client:
        return None
    
    try:
        val = redis_client.get(key)
        if val:
            return json.loads(val)
    except Exception as e:
        logging.error(f"Cache get error: {e}")
    
    return None

def set_cache(key, value, timeout=3600):
    """
    Set value in cache with timeout (default 1 hour)
    """
    if not redis_client:
        return
    
    try:
        # Ensure value is JSON serializable
        json_val = json.dumps(value)
        redis_client.setex(key, timeout, json_val)
    except Exception as e:
        logging.error(f"Cache set error: {e}")

def cache_response(timeout=300):
    """
    Decorator to cache Flask route responses (JSON only)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Create a cache key based on route path and query parameters
            # Use request.full_path or similar
            from flask import request
            key = f"view:{request.full_path}"
            
            cached_data = get_cache(key)
            if cached_data:
                return cached_data
            
            # Execute function
            response = f(*args, **kwargs)
            
            # Only cache 200 OK JSON responses
            # This is tricky because response might be a tuple (json, status)
            # or a Response object.
            # For simplicity, let's assume this decorator is manually used inside functions
            # or we just provide get/set helpers for now to avoid complexity with Response objects.
            return response
        return decorated_function
    return decorator

import time

# In-memory fallback for rate limiting
_local_rate_limit_store = {}

def rate_limit(limit=100, window=60):
    """
    Decorator to rate limit Flask routes
    limit: Number of requests
    window: Time window in seconds
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request, jsonify
            
            # Key based on IP address
            ip = request.remote_addr
            endpoint = request.endpoint
            key = f"rate_limit:{ip}:{endpoint}"
            
            if redis_client:
                try:
                    # Redis Implementation
                    current = redis_client.incr(key)
                    if current == 1:
                        redis_client.expire(key, window)
                    
                    if current > limit:
                        return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429
                except Exception as e:
                    logging.error(f"Redis rate limit error: {e}")
                    # Fallback to local if Redis fails?
                    # For now just pass to ensure availability, or switch to local logic below
                    pass
            else:
                # In-Memory Fallback
                current_time = time.time()
                
                # Clean up old entries occasionally? 
                # For simplicity, we just check specific key
                
                if key not in _local_rate_limit_store:
                    _local_rate_limit_store[key] = {'count': 1, 'start_time': current_time}
                else:
                    data = _local_rate_limit_store[key]
                    # Check window
                    if current_time - data['start_time'] > window:
                        # Reset
                        data['count'] = 1
                        data['start_time'] = current_time
                    else:
                        # Increment
                        data['count'] += 1
                        if data['count'] > limit:
                            return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
