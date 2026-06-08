import time
from functools import wraps
from collections import defaultdict, deque
from flask import request, jsonify, g

from middleware.error_handler import error_response


class RateLimiter:
    def __init__(self):
        self._requests = defaultdict(lambda: defaultdict(deque))
        self._limits = {
            'default': (100, 60),
            'auth': (10, 60),
            'trading': (60, 60),
            'strict': (5, 60)
        }

    def limit(self, limit_type: str = 'default', by_user: bool = True):
        limit, window = self._limits.get(limit_type, self._limits['default'])

        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                identifier = self._get_identifier(by_user)
                
                if not self._check_limit(identifier, limit_type, limit, window):
                    return jsonify(error_response('请求过于频繁，请稍后再试', 429)), 429

                return f(*args, **kwargs)
            
            return decorated_function
        return decorator

    def _get_identifier(self, by_user: bool) -> str:
        if by_user and hasattr(g, 'current_user') and g.current_user:
            return f"user:{g.current_user.id}"
        
        ip = request.remote_addr or 'unknown'
        return f"ip:{ip}"

    def _check_limit(self, identifier: str, limit_type: str, limit: int, window: int) -> bool:
        now = time.time()
        timestamps = self._requests[identifier][limit_type]

        while timestamps and timestamps[0] < now - window:
            timestamps.popleft()

        if len(timestamps) >= limit:
            return False

        timestamps.append(now)
        return True

    def get_remaining(self, identifier: str, limit_type: str) -> dict:
        limit, window = self._limits.get(limit_type, self._limits['default'])
        now = time.time()
        timestamps = self._requests[identifier][limit_type]

        while timestamps and timestamps[0] < now - window:
            timestamps.popleft()

        return {
            'limit': limit,
            'remaining': limit - len(timestamps),
            'reset': int(timestamps[0] + window) if timestamps else int(now)
        }


rate_limiter = RateLimiter()


def rate_limit(limit_type: str = 'default', by_user: bool = True):
    return rate_limiter.limit(limit_type, by_user)
