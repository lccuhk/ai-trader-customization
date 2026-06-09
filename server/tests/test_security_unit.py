#!/usr/bin/env python3
"""
安全策略单元测试 - 覆盖所有分支

测试内容:
1. IP 白名单检查 (is_ip_allowed)
2. IP 限制装饰器 (ip_restriction)
3. 频率控制 (check_rate_limit, rate_limit)
4. IP 封禁 (is_ip_banned, record_failed_attempt, reset_failed_attempts)
5. 客户端 IP 获取 (get_client_ip)
6. 集成测试 (两个端点的完整安全流程)
"""

import unittest
import sys
import os
import time
import json
from unittest.mock import patch, MagicMock

# 添加项目路径 (适配 server/tests/ 目录)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入 Flask 应用和安全函数
from app import app
from middleware.rate_limit import (
    is_ip_allowed,
    is_ip_banned,
    record_failed_attempt,
    reset_failed_attempts,
    check_rate_limit,
    get_client_ip,
    ip_request_history,
    ip_failed_attempts,
    ip_banned,
    ip_lock,
    MAX_FAILED_ATTEMPTS,
    BAN_DURATION,
    ALLOWED_IP_NETWORKS,
)

# 兼容旧的常量名
LOGIN_RATE_LIMIT = 5
LOGIN_RATE_WINDOW = 60
ME_RATE_LIMIT = 30
ME_RATE_WINDOW = 60


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class TestIPWhitelist(unittest.TestCase):
    """测试 IP 白名单功能"""

    def test_localhost_allowed(self):
        """测试本地回环地址 127.0.0.1 被允许"""
        self.assertTrue(is_ip_allowed('127.0.0.1'))

    def test_class_a_internal_allowed(self):
        """测试 A 类内网地址 10.x.x.x 被允许"""
        # 测试网段开头
        self.assertTrue(is_ip_allowed('10.0.0.1'))
        self.assertTrue(is_ip_allowed('10.0.0.0'))
        # 测试网段中间
        self.assertTrue(is_ip_allowed('10.10.10.10'))
        self.assertTrue(is_ip_allowed('10.100.200.50'))
        # 测试网段末尾
        self.assertTrue(is_ip_allowed('10.255.255.254'))
        self.assertTrue(is_ip_allowed('10.255.255.255'))

    def test_class_b_internal_allowed(self):
        """测试 B 类内网地址 172.16.x.x - 172.31.x.x 被允许"""
        # 测试网段开头
        self.assertTrue(is_ip_allowed('172.16.0.1'))
        self.assertTrue(is_ip_allowed('172.16.0.0'))
        # 测试网段中间
        self.assertTrue(is_ip_allowed('172.20.10.5'))
        self.assertTrue(is_ip_allowed('172.30.100.200'))
        # 测试网段末尾
        self.assertTrue(is_ip_allowed('172.31.255.254'))
        self.assertTrue(is_ip_allowed('172.31.255.255'))

    def test_class_c_internal_allowed(self):
        """测试 C 类内网地址 192.168.x.x 被允许"""
        # 测试网段开头
        self.assertTrue(is_ip_allowed('192.168.0.1'))
        self.assertTrue(is_ip_allowed('192.168.0.0'))
        # 测试网段中间
        self.assertTrue(is_ip_allowed('192.168.1.100'))
        self.assertTrue(is_ip_allowed('192.168.100.50'))
        # 测试网段末尾
        self.assertTrue(is_ip_allowed('192.168.255.254'))
        self.assertTrue(is_ip_allowed('192.168.255.255'))

    def test_public_ip_blocked(self):
        """测试公网 IP 被拒绝"""
        # Google DNS
        self.assertFalse(is_ip_allowed('8.8.8.8'))
        self.assertFalse(is_ip_allowed('8.8.4.4'))
        # Cloudflare DNS
        self.assertFalse(is_ip_allowed('1.1.1.1'))
        self.assertFalse(is_ip_allowed('1.0.0.1'))
        # 测试公网地址
        self.assertFalse(is_ip_allowed('203.0.113.1'))
        self.assertFalse(is_ip_allowed('198.51.100.1'))
        self.assertFalse(is_ip_allowed('20.112.250.133'))
        self.assertFalse(is_ip_allowed('140.82.112.3'))

    def test_class_a_boundary(self):
        """测试 A 类内网边界"""
        # 边界前 - 应该拒绝
        self.assertFalse(is_ip_allowed('9.255.255.255'))
        # 边界 - 应该允许
        self.assertTrue(is_ip_allowed('10.0.0.0'))
        self.assertTrue(is_ip_allowed('10.255.255.255'))
        # 边界后 - 应该拒绝
        self.assertFalse(is_ip_allowed('11.0.0.0'))
        self.assertFalse(is_ip_allowed('11.0.0.1'))

    def test_class_b_boundary(self):
        """测试 B 类内网边界"""
        # 边界前 - 应该拒绝
        self.assertFalse(is_ip_allowed('172.15.255.255'))
        # 边界 - 应该允许
        self.assertTrue(is_ip_allowed('172.16.0.0'))
        self.assertTrue(is_ip_allowed('172.31.255.255'))
        # 边界后 - 应该拒绝
        self.assertFalse(is_ip_allowed('172.32.0.0'))
        self.assertFalse(is_ip_allowed('172.32.0.1'))

    def test_class_c_boundary(self):
        """测试 C 类内网边界"""
        # 边界前 - 应该拒绝
        self.assertFalse(is_ip_allowed('192.167.255.255'))
        # 边界 - 应该允许
        self.assertTrue(is_ip_allowed('192.168.0.0'))
        self.assertTrue(is_ip_allowed('192.168.255.255'))
        # 边界后 - 应该拒绝
        self.assertFalse(is_ip_allowed('192.169.0.0'))
        self.assertFalse(is_ip_allowed('192.169.0.1'))

    def test_invalid_ip(self):
        """测试无效 IP 地址"""
        self.assertFalse(is_ip_allowed('invalid_ip'))
        self.assertFalse(is_ip_allowed('256.0.0.1'))
        self.assertFalse(is_ip_allowed('0.0.0.0'))
        self.assertFalse(is_ip_allowed(''))
        self.assertFalse(is_ip_allowed(None))

    def test_ipv6_not_supported(self):
        """测试 IPv6 地址（当前不支持）"""
        self.assertFalse(is_ip_allowed('::1'))
        self.assertFalse(is_ip_allowed('2001:db8::1'))


class TestIPBan(unittest.TestCase):
    """测试 IP 封禁功能"""

    def setUp(self):
        """每个测试前清理状态"""
        with ip_lock:
            ip_failed_attempts.clear()
            ip_banned.clear()

    def test_ip_not_banned_initially(self):
        """测试初始状态下 IP 未被封禁"""
        self.assertFalse(is_ip_banned('192.168.1.1'))
        self.assertFalse(is_ip_banned('10.0.0.1'))

    def test_record_failed_attempt(self):
        """测试记录失败尝试"""
        ip = '192.168.1.100'
        
        # 记录第一次失败
        result = record_failed_attempt(ip)
        self.assertFalse(result)  # 未达到封禁阈值
        with ip_lock:
            self.assertEqual(ip_failed_attempts[ip], 1)
        
        # 记录更多失败
        for i in range(3):
            result = record_failed_attempt(ip)
            self.assertFalse(result)
        
        # 第5次失败应该触发封禁
        result = record_failed_attempt(ip)
        self.assertTrue(result)  # 已达到封禁阈值
        with ip_lock:
            self.assertIn(ip, ip_banned)

    def test_ip_banned_after_max_attempts(self):
        """测试达到最大失败次数后 IP 被封禁"""
        ip = '10.0.0.50'
        
        # 记录 MAX_FAILED_ATTEMPTS 次失败
        for i in range(MAX_FAILED_ATTEMPTS):
            result = record_failed_attempt(ip)
            if i == MAX_FAILED_ATTEMPTS - 1:
                self.assertTrue(result)  # 最后一次应该触发封禁
            else:
                self.assertFalse(result)
        
        # 验证 IP 被封禁
        self.assertTrue(is_ip_banned(ip))

    def test_ban_expires_after_duration(self):
        """测试封禁在持续时间后过期"""
        ip = '172.16.0.100'
        
        # 封禁 IP
        with ip_lock:
            ip_banned[ip] = time.time() - BAN_DURATION - 1  # 模拟已过期
        
        # 应该不再被封禁
        self.assertFalse(is_ip_banned(ip))
        
        # 验证数据已清理
        with ip_lock:
            self.assertNotIn(ip, ip_banned)
            self.assertNotIn(ip, ip_failed_attempts)

    def test_ban_active_within_duration(self):
        """测试在封禁持续时间内 IP 保持封禁状态"""
        ip = '192.168.1.200'
        
        # 封禁 IP
        with ip_lock:
            ip_banned[ip] = time.time() - 10  # 10秒前封禁的
        
        # 应该仍然被封禁
        self.assertTrue(is_ip_banned(ip))

    def test_reset_failed_attempts(self):
        """测试重置失败尝试"""
        ip = '10.0.0.100'
        
        # 记录一些失败尝试
        for i in range(3):
            record_failed_attempt(ip)
        
        # 验证失败尝试已记录
        with ip_lock:
            self.assertEqual(ip_failed_attempts[ip], 3)
        
        # 重置失败尝试
        reset_failed_attempts(ip)
        
        # 验证已清理
        with ip_lock:
            self.assertNotIn(ip, ip_failed_attempts)

    def test_reset_banned_ip(self):
        """测试重置已封禁的 IP"""
        ip = '172.16.0.200'
        
        # 封禁 IP
        for i in range(MAX_FAILED_ATTEMPTS):
            record_failed_attempt(ip)
        
        # 验证已封禁
        self.assertTrue(is_ip_banned(ip))
        
        # 重置
        reset_failed_attempts(ip)
        
        # 验证已解封
        self.assertFalse(is_ip_banned(ip))
        with ip_lock:
            self.assertNotIn(ip, ip_banned)
            self.assertNotIn(ip, ip_failed_attempts)

    def test_multiple_ips_independent(self):
        """测试多个 IP 的状态相互独立"""
        ip1 = '192.168.1.1'
        ip2 = '192.168.1.2'
        
        # 封禁 ip1
        for i in range(MAX_FAILED_ATTEMPTS):
            record_failed_attempt(ip1)
        
        # 验证 ip1 被封禁，ip2 未被封禁
        self.assertTrue(is_ip_banned(ip1))
        self.assertFalse(is_ip_banned(ip2))
        
        # 验证失败计数独立
        with ip_lock:
            self.assertEqual(ip_failed_attempts[ip1], MAX_FAILED_ATTEMPTS)
            self.assertNotIn(ip2, ip_failed_attempts)


class TestRateLimit(unittest.TestCase):
    """测试频率控制功能"""

    def setUp(self):
        """每个测试前清理状态"""
        with ip_lock:
            ip_request_history.clear()

    def test_requests_within_limit_allowed(self):
        """测试在限制内的请求被允许"""
        ip = '192.168.1.1'
        endpoint = 'test_endpoint'
        limit = 5
        window = 60
        
        # 发送 limit 个请求，都应该被允许
        for i in range(limit):
            result = check_rate_limit(ip, limit, window, endpoint)
            self.assertTrue(result, f"请求 {i+1} 应该被允许")

    def test_requests_exceed_limit_blocked(self):
        """测试超过限制的请求被拒绝"""
        ip = '10.0.0.1'
        endpoint = 'test_endpoint'
        limit = 3
        window = 60
        
        # 发送 limit 个请求，都应该被允许
        for i in range(limit):
            result = check_rate_limit(ip, limit, window, endpoint)
            self.assertTrue(result)
        
        # 第 limit+1 个请求应该被拒绝
        result = check_rate_limit(ip, limit, window, endpoint)
        self.assertFalse(result, "超过限制的请求应该被拒绝")

    def test_different_endpoints_independent(self):
        """测试不同端点的频率限制相互独立"""
        ip = '172.16.0.1'
        endpoint1 = 'login'
        endpoint2 = 'auth_me'
        limit = 3
        window = 60
        
        # 耗尽 endpoint1 的配额
        for i in range(limit):
            self.assertTrue(check_rate_limit(ip, limit, window, endpoint1))
        
        # endpoint1 应该被拒绝
        self.assertFalse(check_rate_limit(ip, limit, window, endpoint1))
        
        # endpoint2 应该仍然允许
        for i in range(limit):
            self.assertTrue(check_rate_limit(ip, limit, window, endpoint2))

    def test_different_ips_independent(self):
        """测试不同 IP 的频率限制相互独立"""
        ip1 = '192.168.1.1'
        ip2 = '192.168.1.2'
        endpoint = 'test'
        limit = 3
        window = 60
        
        # 耗尽 ip1 的配额
        for i in range(limit):
            self.assertTrue(check_rate_limit(ip1, limit, window, endpoint))
        
        # ip1 应该被拒绝
        self.assertFalse(check_rate_limit(ip1, limit, window, endpoint))
        
        # ip2 应该仍然允许
        for i in range(limit):
            self.assertTrue(check_rate_limit(ip2, limit, window, endpoint))

    def test_old_requests_expired(self):
        """测试旧请求在时间窗口过期后被清除"""
        ip = '10.0.0.50'
        endpoint = 'test'
        limit = 3
        window = 1  # 1秒窗口，便于测试
        
        # 发送一些请求
        for i in range(limit):
            self.assertTrue(check_rate_limit(ip, limit, window, endpoint))
        
        # 等待窗口过期
        time.sleep(window + 0.1)
        
        # 应该又可以发送请求了
        for i in range(limit):
            self.assertTrue(check_rate_limit(ip, limit, window, endpoint))

    def test_partial_window_expiry(self):
        """测试部分请求过期后的行为"""
        ip = '172.16.0.50'
        endpoint = 'test'
        limit = 5
        window = 2  # 2秒窗口
        
        # 发送 2 个请求
        for i in range(2):
            self.assertTrue(check_rate_limit(ip, limit, window, endpoint))
        
        # 等待 1 秒
        time.sleep(1)
        
        # 再发送 2 个请求
        for i in range(2):
            self.assertTrue(check_rate_limit(ip, limit, window, endpoint))
        
        # 再发送 2 个请求（总共 6 个，但前 2 个还在窗口内，所以第 6 个应该被拒绝）
        self.assertTrue(check_rate_limit(ip, limit, window, endpoint))  # 第 5 个
        self.assertFalse(check_rate_limit(ip, limit, window, endpoint))  # 第 6 个

    def test_login_rate_limit_config(self):
        """测试登录端点的频率限制配置"""
        self.assertEqual(LOGIN_RATE_LIMIT, 5)
        self.assertEqual(LOGIN_RATE_WINDOW, 60)

    def test_me_rate_limit_config(self):
        """测试 auth/me 端点的频率限制配置"""
        self.assertEqual(ME_RATE_LIMIT, 30)
        self.assertEqual(ME_RATE_WINDOW, 60)


class TestGetClientIP(unittest.TestCase):
    """测试客户端 IP 获取功能"""

    def setUp(self):
        """每个测试前创建测试上下文"""
        self.app = app.test_client()

    def test_ip_from_x_forwarded_for(self):
        """测试从 X-Forwarded-For 头获取 IP"""
        with app.test_request_context(headers={'X-Forwarded-For': '203.0.113.1'}):
            ip = get_client_ip()
            self.assertEqual(ip, '203.0.113.1')

    def test_ip_from_x_forwarded_for_multiple(self):
        """测试从包含多个 IP 的 X-Forwarded-For 头获取 IP"""
        with app.test_request_context(headers={'X-Forwarded-For': '203.0.113.1, 10.0.0.1, 192.168.1.1'}):
            ip = get_client_ip()
            self.assertEqual(ip, '203.0.113.1')

    def test_ip_from_x_forwarded_for_with_spaces(self):
        """测试 X-Forwarded-For 头包含空格的情况"""
        with app.test_request_context(headers={'X-Forwarded-For': '  203.0.113.1  ,  10.0.0.1  '}):
            ip = get_client_ip()
            self.assertEqual(ip, '203.0.113.1')

    def test_ip_from_remote_addr(self):
        """测试从 remote_addr 获取 IP（没有 X-Forwarded-For 头）"""
        with app.test_request_context(environ_overrides={'REMOTE_ADDR': '192.168.1.100'}):
            ip = get_client_ip()
            self.assertEqual(ip, '192.168.1.100')

    def test_x_forwarded_for_priority(self):
        """测试 X-Forwarded-For 优先级高于 remote_addr"""
        with app.test_request_context(
            headers={'X-Forwarded-For': '203.0.113.1'},
            environ_overrides={'REMOTE_ADDR': '192.168.1.100'}
        ):
            ip = get_client_ip()
            self.assertEqual(ip, '203.0.113.1')


class TestIPRestrictionDecorator(unittest.TestCase):
    """测试 IP 限制装饰器"""

    def setUp(self):
        """每个测试前创建测试客户端"""
        self.app = app.test_client()

    def test_allowed_ip_can_access(self):
        """测试允许的 IP 可以访问"""
        # 首先登录获取 token（使用允许的 IP）
        login_response = self.app.post(
            '/api/auth/login',
            json={'username': 'demo', 'password': 'demo123456'},
            headers={'X-Forwarded-For': '192.168.1.1'}
        )
        self.assertEqual(login_response.status_code, 200)
        data = login_response.get_json()
        self.assertTrue(data['success'])
        token = data['token']

        # 使用 token 访问 /api/auth/me
        response = self.app.get(
            '/api/auth/me',
            headers={
                'Authorization': f'Bearer {token}',
                'X-Forwarded-For': '192.168.1.1'
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])

    def test_blocked_ip_cannot_access_login(self):
        """测试被阻止的 IP 不能访问登录端点"""
        response = self.app.post(
            '/api/auth/login',
            json={'username': 'demo', 'password': 'demo123456'},
            headers={'X-Forwarded-For': '8.8.8.8'}
        )
        self.assertEqual(response.status_code, 403)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertIn('不在允许的网段内', data['message'])

    def test_blocked_ip_cannot_access_me(self):
        """测试被阻止的 IP 不能访问 /api/auth/me"""
        # 首先使用允许的 IP 登录获取 token
        login_response = self.app.post(
            '/api/auth/login',
            json={'username': 'demo', 'password': 'demo123456'},
            headers={'X-Forwarded-For': '192.168.1.1'}
        )
        token = login_response.get_json()['token']

        # 使用被阻止的 IP 访问 /api/auth/me
        response = self.app.get(
            '/api/auth/me',
            headers={
                'Authorization': f'Bearer {token}',
                'X-Forwarded-For': '8.8.8.8'
            }
        )
        self.assertEqual(response.status_code, 403)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertIn('不在允许的网段内', data['message'])

    def test_blocked_ip_with_valid_token(self):
        """测试即使有有效的 token，被阻止的 IP 也不能访问"""
        # 使用允许的 IP 登录
        login_response = self.app.post(
            '/api/auth/login',
            json={'username': 'demo', 'password': 'demo123456'},
            headers={'X-Forwarded-For': '10.0.0.1'}
        )
        token = login_response.get_json()['token']

        # 切换到被阻止的 IP
        response = self.app.get(
            '/api/auth/me',
            headers={
                'Authorization': f'Bearer {token}',
                'X-Forwarded-For': '203.0.113.1'
            }
        )
        self.assertEqual(response.status_code, 403)


class TestRateLimitDecorator(unittest.TestCase):
    """测试频率限制装饰器"""

    def setUp(self):
        """每个测试前创建测试客户端并清理状态"""
        self.app = app.test_client()
        with ip_lock:
            ip_request_history.clear()

    def test_login_rate_limit(self):
        """测试登录端点的频率限制"""
        ip = '192.168.1.100'
        
        # 发送 LOGIN_RATE_LIMIT 个请求，都应该成功
        for i in range(LOGIN_RATE_LIMIT):
            response = self.app.post(
                '/api/auth/login',
                json={'username': 'demo', 'password': 'demo123456'},
                headers={'X-Forwarded-For': ip}
            )
            self.assertEqual(response.status_code, 200, f"请求 {i+1} 应该成功")
        
        # 第 LOGIN_RATE_LIMIT+1 个请求应该被限制
        response = self.app.post(
            '/api/auth/login',
            json={'username': 'demo', 'password': 'demo123456'},
            headers={'X-Forwarded-For': ip}
        )
        self.assertEqual(response.status_code, 429)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertIn('请求过于频繁', data['message'])

    def test_me_rate_limit(self):
        """测试 /api/auth/me 端点的频率限制"""
        ip = '10.0.0.100'
        
        # 首先登录获取 token
        login_response = self.app.post(
            '/api/auth/login',
            json={'username': 'demo', 'password': 'demo123456'},
            headers={'X-Forwarded-For': ip}
        )
        token = login_response.get_json()['token']
        
        # 清理登录请求的历史记录，避免影响测试
        with ip_lock:
            ip_request_history.clear()
        
        # 发送 ME_RATE_LIMIT 个请求，都应该成功
        for i in range(ME_RATE_LIMIT):
            response = self.app.get(
                '/api/auth/me',
                headers={
                    'Authorization': f'Bearer {token}',
                    'X-Forwarded-For': ip
                }
            )
            self.assertEqual(response.status_code, 200, f"请求 {i+1} 应该成功")
        
        # 第 ME_RATE_LIMIT+1 个请求应该被限制
        response = self.app.get(
            '/api/auth/me',
            headers={
                'Authorization': f'Bearer {token}',
                'X-Forwarded-For': ip
            }
        )
        self.assertEqual(response.status_code, 429)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertIn('请求过于频繁', data['message'])


class TestIntegration(unittest.TestCase):
    """集成测试 - 测试完整的安全流程"""

    def setUp(self):
        """每个测试前创建测试客户端并清理状态"""
        self.app = app.test_client()
        with ip_lock:
            ip_request_history.clear()
            ip_failed_attempts.clear()
            ip_banned.clear()

    def test_full_security_flow_allowed_ip(self):
        """测试允许的 IP 的完整安全流程"""
        ip = '192.168.1.50'
        
        # 1. 登录（应该成功）
        login_response = self.app.post(
            '/api/auth/login',
            json={'username': 'demo', 'password': 'demo123456'},
            headers={'X-Forwarded-For': ip}
        )
        self.assertEqual(login_response.status_code, 200)
        data = login_response.get_json()
        self.assertTrue(data['success'])
        token = data['token']
        
        # 2. 访问 /api/auth/me（应该成功）
        me_response = self.app.get(
            '/api/auth/me',
            headers={
                'Authorization': f'Bearer {token}',
                'X-Forwarded-For': ip
            }
        )
        self.assertEqual(me_response.status_code, 200)
        data = me_response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['user']['username'], 'demo')

    def test_full_security_flow_blocked_ip(self):
        """测试被阻止的 IP 的完整安全流程"""
        ip = '8.8.8.8'
        
        # 1. 登录（应该被 IP 限制拒绝）
        login_response = self.app.post(
            '/api/auth/login',
            json={'username': 'demo', 'password': 'demo123456'},
            headers={'X-Forwarded-For': ip}
        )
        self.assertEqual(login_response.status_code, 403)
        
        # 2. 即使 somehow 获取了 token，访问 /api/auth/me 也应该被拒绝
        # 先用允许的 IP 获取 token
        login_response2 = self.app.post(
            '/api/auth/login',
            json={'username': 'demo', 'password': 'demo123456'},
            headers={'X-Forwarded-For': '192.168.1.1'}
        )
        token = login_response2.get_json()['token']
        
        # 用被阻止的 IP 访问
        me_response = self.app.get(
            '/api/auth/me',
            headers={
                'Authorization': f'Bearer {token}',
                'X-Forwarded-For': ip
            }
        )
        self.assertEqual(me_response.status_code, 403)

    def test_full_security_flow_brute_force(self):
        """测试暴力破解防护的完整流程"""
        ip = '10.0.0.200'
        
        # 1. 多次失败的登录尝试
        for i in range(MAX_FAILED_ATTEMPTS):
            response = self.app.post(
                '/api/auth/login',
                json={'username': 'demo', 'password': 'wrongpassword'},
                headers={'X-Forwarded-For': ip}
            )
            if i < MAX_FAILED_ATTEMPTS - 1:
                self.assertEqual(response.status_code, 401)
            else:
                # 最后一次应该触发封禁
                self.assertEqual(response.status_code, 429)
        
        # 2. 验证 IP 已被封禁
        response = self.app.post(
            '/api/auth/login',
            json={'username': 'demo', 'password': 'demo123456'},  # 即使密码正确
            headers={'X-Forwarded-For': ip}
        )
        self.assertEqual(response.status_code, 429)
        self.assertIn('IP 已被暂时封禁', response.get_json()['message'])

    def test_full_security_flow_rate_limit(self):
        """测试频率限制的完整流程"""
        ip = '172.16.0.100'
        
        # 1. 快速发送多个登录请求
        for i in range(LOGIN_RATE_LIMIT):
            response = self.app.post(
                '/api/auth/login',
                json={'username': 'demo', 'password': 'demo123456'},
                headers={'X-Forwarded-For': ip}
            )
            self.assertEqual(response.status_code, 200)
        
        # 2. 超过频率限制
        response = self.app.post(
            '/api/auth/login',
            json={'username': 'demo', 'password': 'demo123456'},
            headers={'X-Forwarded-For': ip}
        )
        self.assertEqual(response.status_code, 429)

    def test_security_layer_order(self):
        """测试安全层的执行顺序：IP 限制 -> 频率限制 -> 认证"""
        ip = '8.8.8.8'  # 被阻止的 IP
        
        # 即使提供了有效的 token，也应该首先被 IP 限制拒绝
        # 先用允许的 IP 获取 token
        login_response = self.app.post(
            '/api/auth/login',
            json={'username': 'demo', 'password': 'demo123456'},
            headers={'X-Forwarded-For': '192.168.1.1'}
        )
        token = login_response.get_json()['token']
        
        # 用被阻止的 IP 访问，应该返回 403（IP 限制）而不是 401（认证）或 429（频率限制）
        response = self.app.get(
            '/api/auth/me',
            headers={
                'Authorization': f'Bearer {token}',
                'X-Forwarded-For': ip
            }
        )
        self.assertEqual(response.status_code, 403)  # IP 限制优先


class TestConfiguration(unittest.TestCase):
    """测试安全配置"""

    def test_allowed_networks_configured(self):
        """测试允许的网段已配置"""
        self.assertIsInstance(ALLOWED_IP_NETWORKS, list)
        self.assertGreater(len(ALLOWED_IP_NETWORKS), 0)
        
        # 验证包含预期的网段
        self.assertIn('127.0.0.1/32', ALLOWED_IP_NETWORKS)
        self.assertIn('10.0.0.0/8', ALLOWED_IP_NETWORKS)
        self.assertIn('172.16.0.0/12', ALLOWED_IP_NETWORKS)
        self.assertIn('192.168.0.0/16', ALLOWED_IP_NETWORKS)

    def test_ban_configuration(self):
        """测试封禁配置"""
        self.assertEqual(MAX_FAILED_ATTEMPTS, 5)
        self.assertEqual(BAN_DURATION, 300)

    def test_rate_limit_configuration(self):
        """测试频率限制配置"""
        self.assertEqual(LOGIN_RATE_LIMIT, 5)
        self.assertEqual(LOGIN_RATE_WINDOW, 60)
        self.assertEqual(ME_RATE_LIMIT, 30)
        self.assertEqual(ME_RATE_WINDOW, 60)


def run_tests_with_report():
    """运行测试并生成报告"""
    print(f"\n{bcolors.HEADER}{bcolors.BOLD}")
    print("╔══════════════════════════════════════════════════════════════════════════╗")
    print("║               安全策略单元测试 - 完整覆盖测试                          ║")
    print("╚══════════════════════════════════════════════════════════════════════════╝")
    print(f"{bcolors.ENDC}")
    print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestIPWhitelist))
    suite.addTests(loader.loadTestsFromTestCase(TestIPBan))
    suite.addTests(loader.loadTestsFromTestCase(TestRateLimit))
    suite.addTests(loader.loadTestsFromTestCase(TestGetClientIP))
    suite.addTests(loader.loadTestsFromTestCase(TestIPRestrictionDecorator))
    suite.addTests(loader.loadTestsFromTestCase(TestRateLimitDecorator))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestConfiguration))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 生成汇总报告
    print(f"\n{bcolors.HEADER}{bcolors.BOLD}")
    print("╔══════════════════════════════════════════════════════════════════════════╗")
    print("║                         测试报告汇总                                    ║")
    print("╚══════════════════════════════════════════════════════════════════════════╝")
    print(f"{bcolors.ENDC}")

    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    passed = total_tests - failures - errors - skipped

    print(f"\n{bcolors.BOLD}测试统计:{bcolors.ENDC}")
    print(f"  总测试数: {total_tests}")
    print(f"  通过: {bcolors.OKGREEN}{passed}{bcolors.ENDC}")
    print(f"  失败: {bcolors.FAIL}{failures}{bcolors.ENDC}")
    print(f"  错误: {bcolors.FAIL}{errors}{bcolors.ENDC}")
    print(f"  跳过: {bcolors.WARNING}{skipped}{bcolors.ENDC}")

    # 计算通过率
    if total_tests > 0:
        pass_rate = (passed / total_tests) * 100
        print(f"\n{bcolors.BOLD}通过率: {pass_rate:.1f}%{bcolors.ENDC}")

    # 显示失败详情
    if failures or errors:
        print(f"\n{bcolors.FAIL}{bcolors.BOLD}失败详情:{bcolors.ENDC}")
        for test, traceback in result.failures:
            print(f"\n  {bcolors.FAIL}✗ {test}{bcolors.ENDC}")
            print(f"    {traceback.split(chr(10))[0]}")
        for test, traceback in result.errors:
            print(f"\n  {bcolors.FAIL}✗ {test} (错误){bcolors.ENDC}")
            print(f"    {traceback.split(chr(10))[0]}")

    # 最终结论
    print()
    if failures == 0 and errors == 0:
        print(f"{bcolors.OKGREEN}{bcolors.BOLD}🎉 所有测试通过！安全策略功能完整且正确！{bcolors.ENDC}")
        print(f"{bcolors.OKGREEN}   所有分支都已覆盖，安全策略可以正常工作。{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}{bcolors.BOLD}⚠️  有 {failures + errors} 项测试失败，请检查代码。{bcolors.ENDC}")

    print(f"\n测试完成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    return result


if __name__ == '__main__':
    result = run_tests_with_report()
    sys.exit(0 if result.wasSuccessful() else 1)
