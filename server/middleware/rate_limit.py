import time
import threading
import ipaddress
import sys
from functools import wraps
from collections import defaultdict, deque
from flask import request, jsonify, g

from middleware.error_handler import error_response


# IP 安全配置
MAX_FAILED_ATTEMPTS = 5
BAN_DURATION = 300  # 5分钟

ALLOWED_IP_NETWORKS = [
    '127.0.0.1/32',
    '10.0.0.0/8',
    '172.16.0.0/12',
    '192.168.0.0/16',
]

# 频率限制配置
LOGIN_RATE_LIMIT = 5
LOGIN_RATE_WINDOW = 60
ME_RATE_LIMIT = 30
ME_RATE_WINDOW = 60

# 解析允许的IP网络
_parsed_networks = []
for network in ALLOWED_IP_NETWORKS:
    try:
        _parsed_networks.append(ipaddress.ip_network(network, strict=False))
    except ValueError as e:
        print(f"[WARN] Invalid IP network: {network} - {e}", file=sys.stderr)

# 全局状态
ip_request_history = {}
ip_failed_attempts = {}
ip_banned = {}
ip_lock = threading.Lock()


def get_client_ip():
    """获取客户端真实IP"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or 'unknown'


def is_ip_allowed(ip):
    """检查IP是否在白名单中"""
    try:
        ip_addr = ipaddress.ip_address(ip)
        for network in _parsed_networks:
            if ip_addr in network:
                return True
        return False
    except ValueError:
        return False


def is_ip_banned(ip):
    """检查IP是否被封禁"""
    with ip_lock:
        if ip in ip_banned:
            ban_time = ip_banned[ip]
            if time.time() - ban_time < BAN_DURATION:
                return True
            else:
                # 封禁已过期，清理记录
                del ip_banned[ip]
                if ip in ip_failed_attempts:
                    del ip_failed_attempts[ip]
    return False


def record_failed_attempt(ip):
    """记录失败尝试，达到阈值则封禁IP"""
    with ip_lock:
        if ip not in ip_failed_attempts:
            ip_failed_attempts[ip] = 0
        ip_failed_attempts[ip] += 1
        
        if ip_failed_attempts[ip] >= MAX_FAILED_ATTEMPTS:
            ip_banned[ip] = time.time()
            return True
    return False


def reset_failed_attempts(ip):
    """重置失败尝试记录"""
    with ip_lock:
        if ip in ip_failed_attempts:
            del ip_failed_attempts[ip]
        if ip in ip_banned:
            del ip_banned[ip]


def check_rate_limit(ip, limit, window, endpoint):
    """检查频率限制"""
    with ip_lock:
        key = f"{endpoint}:{ip}"
        now = time.time()
        
        if key not in ip_request_history:
            ip_request_history[key] = []
        
        # 清理过期的请求记录
        ip_request_history[key] = [
            t for t in ip_request_history[key] 
            if now - t < window
        ]
        
        if len(ip_request_history[key]) >= limit:
            return False
        
        ip_request_history[key].append(now)
        return True


class RateLimiter:
    def __init__(self):
        self._requests = defaultdict(lambda: defaultdict(deque))
        self._limits = {
            'default': (100, 60),
            'auth': (5, 60),  # LOGIN_RATE_LIMIT, LOGIN_RATE_WINDOW
            'trading': (60, 60),
            'strict': (30, 60)  # ME_RATE_LIMIT, ME_RATE_WINDOW
        }

    def limit(self, limit_type: str = 'default', by_user: bool = True, check_ban: bool = True):
        """
        频率限制装饰器
        :param limit_type: 限制类型
        :param by_user: 是否按用户限制
        :param check_ban: 是否检查IP封禁
        """
        limit, window = self._limits.get(limit_type, self._limits['default'])

        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                ip = get_client_ip()
                
                # 检查IP是否被封禁
                if check_ban and is_ip_banned(ip):
                    return jsonify({
                        'success': False,
                        'message': f'IP 已被暂时封禁，请 {BAN_DURATION} 秒后再试'
                    }), 429
                
                identifier = self._get_identifier(by_user, ip)
                
                if not self._check_limit(identifier, limit_type, limit, window):
                    return jsonify({
                        'success': False,
                        'message': f'请求过于频繁，请 {window} 秒后再试'
                    }), 429

                return f(*args, **kwargs)
            
            return decorated_function
        return decorator

    def _get_identifier(self, by_user: bool, ip: str = None) -> str:
        if by_user and hasattr(g, 'current_user') and g.current_user:
            return f"user:{g.current_user.id}"
        
        if ip is None:
            ip = get_client_ip()
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


def rate_limit(limit_type: str = 'default', by_user: bool = True, check_ban: bool = True):
    """频率限制装饰器（便捷函数）"""
    return rate_limiter.limit(limit_type, by_user, check_ban)


def ip_ban_required(f):
    """装饰器：检查IP是否被封禁"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip = get_client_ip()
        if is_ip_banned(ip):
            return jsonify({
                'success': False,
                'message': f'IP 已被暂时封禁，请 {BAN_DURATION} 秒后再试'
            }), 429
        return f(*args, **kwargs)
    return decorated_function


def ip_restriction_required(f):
    """装饰器：检查IP是否在白名单中"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip = get_client_ip()
        if not is_ip_allowed(ip):
            return jsonify({
                'success': False,
                'message': 'IP 地址不在允许的网段内'
            }), 403
        return f(*args, **kwargs)
    return decorated_function



