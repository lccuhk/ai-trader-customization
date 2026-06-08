import json
import time
from typing import Any, Optional, Callable
from functools import wraps
from flask import request, jsonify

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class RedisCache:
    def __init__(self):
        self._client = None
        self._enabled = False
        self._default_ttl = 300

    def init_app(self, app):
        if not REDIS_AVAILABLE:
            print("[Cache] Redis package not available, caching disabled")
            return

        redis_url = app.config.get('REDIS_URL')
        if not redis_url:
            print("[Cache] REDIS_URL not configured, caching disabled")
            return

        try:
            self._client = redis.from_url(redis_url, decode_responses=True)
            self._client.ping()
            self._enabled = True
            self._default_ttl = app.config.get('CACHE_DEFAULT_TTL', 300)
            print(f"[Cache] Redis cache initialized successfully, default TTL: {self._default_ttl}s")
        except Exception as e:
            print(f"[Cache] Failed to connect to Redis: {e}, caching disabled")
            self._client = None
            self._enabled = False

    def is_enabled(self) -> bool:
        return self._enabled and self._client is not None

    def get(self, key: str) -> Optional[Any]:
        if not self.is_enabled():
            return None
        
        try:
            value = self._client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            print(f"[Cache] Error getting key {key}: {e}")
        
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        if not self.is_enabled():
            return False
        
        try:
            serialized = json.dumps(value)
            self._client.setex(key, ttl or self._default_ttl, serialized)
            return True
        except Exception as e:
            print(f"[Cache] Error setting key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        if not self.is_enabled():
            return False
        
        try:
            self._client.delete(key)
            return True
        except Exception as e:
            print(f"[Cache] Error deleting key {key}: {e}")
            return False

    def delete_pattern(self, pattern: str) -> bool:
        if not self.is_enabled():
            return False
        
        try:
            keys = self._client.keys(pattern)
            if keys:
                self._client.delete(*keys)
            return True
        except Exception as e:
            print(f"[Cache] Error deleting pattern {pattern}: {e}")
            return False

    def clear(self) -> bool:
        if not self.is_enabled():
            return False
        
        try:
            self._client.flushdb()
            return True
        except Exception as e:
            print(f"[Cache] Error clearing cache: {e}")
            return False

    def cached(self, key_prefix: str, ttl: Optional[int] = None, include_user: bool = True):
        def decorator(f: Callable):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not self.is_enabled():
                    return f(*args, **kwargs)

                cache_key = self._build_cache_key(key_prefix, include_user, request.args, kwargs)
                
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    return jsonify(cached_result)

                result = f(*args, **kwargs)
                
                if hasattr(result, 'get_json'):
                    data = result.get_json()
                    self.set(cache_key, data, ttl)
                
                return result
            
            return decorated_function
        return decorator

    def _build_cache_key(self, prefix: str, include_user: bool, args: dict, kwargs: dict) -> str:
        parts = [prefix]
        
        if include_user:
            from middleware.auth import get_current_user_from_token
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                user = get_current_user_from_token(token)
                if user:
                    parts.append(f"user:{user.id}")
        
        if args:
            for key in sorted(args.keys()):
                parts.append(f"{key}:{args[key]}")
        
        if kwargs:
            for key in sorted(kwargs.keys()):
                parts.append(f"{key}:{kwargs[key]}")
        
        return ':'.join(parts)

    def invalidate(self, key_prefix: str, include_user: bool = True) -> None:
        if not self.is_enabled():
            return
        
        pattern = key_prefix + '*'
        self.delete_pattern(pattern)


redis_cache = RedisCache()
