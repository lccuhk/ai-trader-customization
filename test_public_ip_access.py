#!/usr/bin/env python3
"""
公网 IP 访问测试脚本 - 验证 /api/auth/me 端点的 IP 限制是否生效

这个脚本会模拟从不同的公网 IP 地址访问 /api/auth/me，
验证 IP 白名单限制是否正确工作。
"""

import requests
import time
from datetime import datetime

BASE_URL = "http://localhost:8001"
TEST_USERNAME = "demo"
TEST_PASSWORD = "demo123456"

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(title):
    print(f"\n{bcolors.HEADER}{bcolors.BOLD}{'='*70}{bcolors.ENDC}")
    print(f"{bcolors.HEADER}{bcolors.BOLD}  {title}{bcolors.ENDC}")
    print(f"{bcolors.HEADER}{bcolors.BOLD}{'='*70}{bcolors.ENDC}\n")

def print_ip_test(ip, description, expected_allowed):
    """测试指定 IP 访问 /api/auth/me"""
    headers = {
        'Authorization': f'Bearer {token}',
        'X-Forwarded-For': ip
    }
    
    try:
        response = requests.get(f'{BASE_URL}/api/auth/me', headers=headers, timeout=5)
        result = response.json()
        status_code = response.status_code
        
        is_allowed = status_code == 200 and result.get('success')
        is_blocked = status_code == 403 and '不在允许的网段内' in result.get('message', '')
        
        test_passed = (is_allowed and expected_allowed) or (is_blocked and not expected_allowed)
        
        status_icon = f"{bcolors.OKGREEN}✅{bcolors.ENDC}" if test_passed else f"{bcolors.FAIL}❌{bcolors.ENDC}"
        access_status = f"{bcolors.OKGREEN}允许访问{bcolors.ENDC}" if is_allowed else f"{bcolors.FAIL}拒绝访问{bcolors.ENDC}"
        expected_status = f"{bcolors.OKGREEN}允许{bcolors.ENDC}" if expected_allowed else f"{bcolors.FAIL}拒绝{bcolors.ENDC}"
        
        print(f"{status_icon} {ip:<18} {description:<30} 预期: {expected_status} 实际: {access_status}")
        
        if not test_passed:
            print(f"     {bcolors.WARNING}状态码: {status_code}, 消息: {result.get('message', '')}{bcolors.ENDC}")
        
        return test_passed
        
    except Exception as e:
        print(f"{bcolors.FAIL}❌ {ip:<18} {description:<30} 异常: {str(e)}{bcolors.ENDC}")
        return False

# 测试用例定义
TEST_CASES = [
    # (IP 地址, 描述, 预期是否允许访问)
    # 允许的 IP
    ('127.0.0.1', '本地回环地址', True),
    ('10.0.0.1', 'A类内网地址', True),
    ('10.255.255.254', 'A类内网地址 (末尾)', True),
    ('172.16.0.1', 'B类内网地址', True),
    ('172.31.255.254', 'B类内网地址 (末尾)', True),
    ('192.168.0.1', 'C类内网地址', True),
    ('192.168.255.254', 'C类内网地址 (末尾)', True),
    ('192.168.1.100', '常见路由器地址', True),
    ('192.168.10.50', '常见内网地址', True),
    
    # 拒绝的公网 IP
    ('8.8.8.8', 'Google DNS', False),
    ('8.8.4.4', 'Google DNS 2', False),
    ('1.1.1.1', 'Cloudflare DNS', False),
    ('203.0.113.1', '测试公网地址 1', False),
    ('198.51.100.1', '测试公网地址 2', False),
    ('20.112.250.133', '微软公网地址', False),
    ('140.82.112.3', 'GitHub 公网地址', False),
    ('151.101.1.69', 'Fastly CDN', False),
    ('104.16.132.229', 'Cloudflare CDN', False),
    ('172.217.160.78', 'Google 公网地址', False),
    ('157.240.1.35', 'Facebook 公网地址', False),
    ('104.244.42.1', 'Twitter 公网地址', False),
    
    # 边界测试
    ('9.255.255.255', 'A类边界 (10.0.0.0 之前)', False),
    ('11.0.0.1', 'A类边界 (10.255.255.255 之后)', False),
    ('172.15.255.255', 'B类边界 (172.16.0.0 之前)', False),
    ('172.32.0.1', 'B类边界 (172.31.255.255 之后)', False),
    ('192.167.255.255', 'C类边界 (192.168.0.0 之前)', False),
    ('192.169.0.1', 'C类边界 (192.168.255.255 之后)', False),
]

def main():
    global token
    
    print(f"\n{bcolors.BOLD}{bcolors.HEADER}")
    print("╔══════════════════════════════════════════════════════════════════════════╗")
    print("║            公网 IP 访问测试 - /api/auth/me IP 限制验证                  ║")
    print("╚══════════════════════════════════════════════════════════════════════════╝")
    print(f"{bcolors.ENDC}")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"目标服务器: {BASE_URL}")
    print(f"测试端点: /api/auth/me")
    print()
    
    # 步骤1: 登录获取 token
    print_header("步骤1: 登录获取访问 Token")
    
    login_data = {'username': TEST_USERNAME, 'password': TEST_PASSWORD}
    
    try:
        response = requests.post(f'{BASE_URL}/api/auth/login', json=login_data, timeout=5)
        result = response.json()
        
        if response.status_code != 200 or not result.get('success'):
            print(f"{bcolors.FAIL}❌ 登录失败！{bcolors.ENDC}")
            print(f"   状态码: {response.status_code}")
            print(f"   消息: {result.get('message', '')}")
            return
        
        token = result['token']
        print(f"{bcolors.OKGREEN}✅ 登录成功！{bcolors.ENDC}")
        print(f"   Token: {token[:20]}...{token[-20:]}")
        print(f"   用户: {result['user']['username']}")
        
    except Exception as e:
        print(f"{bcolors.FAIL}❌ 登录异常: {e}{bcolors.ENDC}")
        return
    
    # 步骤2: 测试不同 IP 访问
    print_header("步骤2: 测试不同 IP 地址访问 /api/auth/me")
    
    print(f"{bcolors.BOLD}{'IP 地址':<20} {'描述':<32} {'预期':<10} {'实际':<10}{bcolors.ENDC}")
    print("-" * 75)
    
    passed = 0
    failed = 0
    allowed_count = 0
    blocked_count = 0
    
    for ip, description, expected_allowed in TEST_CASES:
        result = print_ip_test(ip, description, expected_allowed)
        if result:
            passed += 1
        else:
            failed += 1
        
        if expected_allowed:
            allowed_count += 1
        else:
            blocked_count += 1
        
        # 稍微延迟，避免触发频率限制
        time.sleep(0.1)
    
    # 步骤3: 输出汇总报告
    print_header("测试报告汇总")
    
    print(f"{bcolors.BOLD}测试统计:{bcolors.ENDC}")
    print(f"  总测试用例: {len(TEST_CASES)}")
    print(f"  允许访问的 IP: {bcolors.OKGREEN}{allowed_count}{bcolors.ENDC} 个")
    print(f"  拒绝访问的 IP: {bcolors.FAIL}{blocked_count}{bcolors.ENDC} 个")
    print()
    print(f"  通过测试: {bcolors.OKGREEN}{passed}{bcolors.ENDC}")
    print(f"  失败测试: {bcolors.FAIL}{failed}{bcolors.ENDC}")
    print()
    
    # 计算通过率
    pass_rate = (passed / len(TEST_CASES)) * 100
    print(f"{bcolors.BOLD}通过率: {pass_rate:.1f}%{bcolors.ENDC}")
    print()
    
    if failed == 0:
        print(f"{bcolors.OKGREEN}{bcolors.BOLD}🎉 所有测试通过！IP 白名单限制功能完美生效！{bcolors.ENDC}")
        print(f"{bcolors.OKGREEN}   所有公网 IP 都被正确拒绝，所有内网 IP 都被正确允许。{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}{bcolors.BOLD}⚠️  有 {failed} 项测试失败，请检查配置。{bcolors.ENDC}")
    
    # 显示当前的白名单配置
    print_header("当前 IP 白名单配置")
    
    print(f"{bcolors.BOLD}允许的网段:{bcolors.ENDC}")
    print(f"  127.0.0.1/32      - 本地回环地址")
    print(f"  10.0.0.0/8         - A类私有网络 (10.0.0.0 - 10.255.255.255)")
    print(f"  172.16.0.0/12      - B类私有网络 (172.16.0.0 - 172.31.255.255)")
    print(f"  192.168.0.0/16     - C类私有网络 (192.168.0.0 - 192.168.255.255)")
    print()
    print(f"{bcolors.WARNING}提示: 所有不在上述网段内的 IP 地址都将被拒绝访问。{bcolors.ENDC}")
    
    print(f"\n测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
