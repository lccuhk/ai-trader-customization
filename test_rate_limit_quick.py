#!/usr/bin/env python3
"""
快速高频请求测试脚本 - 验证频率限制是否真的生效

这个脚本会快速发送并发请求，验证频率限制功能。
"""

import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import sys

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
    print(f"\n{bcolors.HEADER}{bcolors.BOLD}{'='*60}{bcolors.ENDC}")
    print(f"{bcolors.HEADER}{bcolors.BOLD}  {title}{bcolors.ENDC}")
    print(f"{bcolors.HEADER}{bcolors.BOLD}{'='*60}{bcolors.ENDC}\n")

def test_login_concurrent():
    """测试 /api/auth/login 并发请求的频率限制"""
    print_header("测试1: /api/auth/login 并发请求 (限制: 5次/60秒)")
    
    url = f"{BASE_URL}/api/auth/login"
    data = {"username": TEST_USERNAME, "password": TEST_PASSWORD}
    
    total_requests = 10
    results = {"success": 0, "rate_limited": 0, "other_errors": 0}
    response_times = []
    
    print(f"发送 {total_requests} 个并发登录请求...\n")
    
    def make_request(i):
        start_time = time.time()
        try:
            response = requests.post(url, json=data, timeout=5)
            elapsed = time.time() - start_time
            response_times.append(elapsed)
            
            result = response.json()
            status_code = response.status_code
            
            if status_code == 200 and result.get("success"):
                return ("success", i, elapsed, status_code, "")
            elif status_code == 429:
                return ("rate_limited", i, elapsed, status_code, result.get("message", ""))
            else:
                return ("other", i, elapsed, status_code, result.get("message", ""))
        except Exception as e:
            elapsed = time.time() - start_time
            return ("error", i, elapsed, 0, str(e))
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request, i) for i in range(total_requests)]
        
        for future in as_completed(futures):
            result_type, req_num, elapsed, status_code, message = future.result()
            
            if result_type == "success":
                results["success"] += 1
                print(f"{bcolors.OKGREEN}[请求{req_num:2d}] ✅ 成功 - {status_code} - {elapsed:.3f}s{bcolors.ENDC}")
            elif result_type == "rate_limited":
                results["rate_limited"] += 1
                print(f"{bcolors.WARNING}[请求{req_num:2d}] ⚠️  被限制 - {status_code} - {elapsed:.3f}s - {message}{bcolors.ENDC}")
            elif result_type == "other":
                results["other_errors"] += 1
                print(f"{bcolors.FAIL}[请求{req_num:2d}] ❌ 其他错误 - {status_code} - {elapsed:.3f}s - {message}{bcolors.ENDC}")
            else:
                results["other_errors"] += 1
                print(f"{bcolors.FAIL}[请求{req_num:2d}] ❌ 异常 - {elapsed:.3f}s - {message}{bcolors.ENDC}")
    
    print(f"\n{bcolors.BOLD}结果统计:{bcolors.ENDC}")
    print(f"  成功请求: {bcolors.OKGREEN}{results['success']}{bcolors.ENDC}")
    print(f"  被限制请求: {bcolors.WARNING}{results['rate_limited']}{bcolors.ENDC}")
    print(f"  其他错误: {bcolors.FAIL}{results['other_errors']}{bcolors.ENDC}")
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        print(f"  平均响应时间: {avg_time:.3f}s")
    
    # 验证频率限制是否生效
    rate_limit_working = results["success"] <= 5 and results["rate_limited"] >= 4
    
    if rate_limit_working:
        print(f"\n{bcolors.OKGREEN}{bcolors.BOLD}✅ 登录频率限制验证通过！{bcolors.ENDC}")
        print(f"   成功请求 {results['success']} 次（限制5次），被限制 {results['rate_limited']} 次")
    else:
        print(f"\n{bcolors.FAIL}{bcolors.BOLD}❌ 登录频率限制验证失败！{bcolors.ENDC}")
    
    return rate_limit_working

def test_auth_me_concurrent():
    """测试 /api/auth/me 并发请求的频率限制"""
    print_header("测试2: /api/auth/me 并发请求 (限制: 30次/60秒)")
    
    # 首先登录获取 token
    login_url = f"{BASE_URL}/api/auth/login"
    login_data = {"username": TEST_USERNAME, "password": TEST_PASSWORD}
    
    print("首先登录获取 token...")
    response = requests.post(login_url, json=login_data)
    if response.status_code != 200 or not response.json().get("success"):
        print(f"{bcolors.FAIL}❌ 登录失败，无法继续测试{bcolors.ENDC}")
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.text}")
        return False
    
    token = response.json()["token"]
    print(f"{bcolors.OKGREEN}✅ 登录成功，获取到 token{bcolors.ENDC}\n")
    
    url = f"{BASE_URL}/api/auth/me"
    headers = {"Authorization": f"Bearer {token}"}
    
    total_requests = 40
    results = {"success": 0, "rate_limited": 0, "other_errors": 0}
    response_times = []
    
    print(f"发送 {total_requests} 个并发请求到 /api/auth/me...\n")
    
    def make_request(i):
        start_time = time.time()
        try:
            response = requests.get(url, headers=headers, timeout=5)
            elapsed = time.time() - start_time
            response_times.append(elapsed)
            
            result = response.json()
            status_code = response.status_code
            
            if status_code == 200 and result.get("success"):
                return ("success", i, elapsed, status_code, "")
            elif status_code == 429:
                return ("rate_limited", i, elapsed, status_code, result.get("message", ""))
            else:
                return ("other", i, elapsed, status_code, result.get("message", ""))
        except Exception as e:
            elapsed = time.time() - start_time
            return ("error", i, elapsed, 0, str(e))
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(make_request, i) for i in range(total_requests)]
        
        success_count = 0
        limited_count = 0
        
        for future in as_completed(futures):
            result_type, req_num, elapsed, status_code, message = future.result()
            
            if result_type == "success":
                results["success"] += 1
                success_count += 1
                if success_count <= 5 or success_count > 28:
                    print(f"{bcolors.OKGREEN}[请求{req_num:2d}] ✅ 成功 - {status_code} - {elapsed:.3f}s{bcolors.ENDC}")
                elif success_count == 6:
                    print(f"{bcolors.OKCYAN}... (省略中间 {total_requests - 12} 个请求) ...{bcolors.ENDC}")
            elif result_type == "rate_limited":
                results["rate_limited"] += 1
                limited_count += 1
                print(f"{bcolors.WARNING}[请求{req_num:2d}] ⚠️  被限制 - {status_code} - {elapsed:.3f}s - {message}{bcolors.ENDC}")
            elif result_type == "other":
                results["other_errors"] += 1
                print(f"{bcolors.FAIL}[请求{req_num:2d}] ❌ 其他错误 - {status_code} - {elapsed:.3f}s - {message}{bcolors.ENDC}")
            else:
                results["other_errors"] += 1
                print(f"{bcolors.FAIL}[请求{req_num:2d}] ❌ 异常 - {elapsed:.3f}s - {message}{bcolors.ENDC}")
    
    print(f"\n{bcolors.BOLD}结果统计:{bcolors.ENDC}")
    print(f"  成功请求: {bcolors.OKGREEN}{results['success']}{bcolors.ENDC}")
    print(f"  被限制请求: {bcolors.WARNING}{results['rate_limited']}{bcolors.ENDC}")
    print(f"  其他错误: {bcolors.FAIL}{results['other_errors']}{bcolors.ENDC}")
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        print(f"  平均响应时间: {avg_time:.3f}s")
    
    # 验证频率限制是否生效
    rate_limit_working = results["success"] <= 32 and results["rate_limited"] >= 6
    
    if rate_limit_working:
        print(f"\n{bcolors.OKGREEN}{bcolors.BOLD}✅ auth/me 频率限制验证通过！{bcolors.ENDC}")
        print(f"   成功请求 {results['success']} 次（限制30次），被限制 {results['rate_limited']} 次")
    else:
        print(f"\n{bcolors.FAIL}{bcolors.BOLD}❌ auth/me 频率限制验证失败！{bcolors.ENDC}")
    
    return rate_limit_working

def main():
    print(f"\n{bcolors.BOLD}{bcolors.HEADER}")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║          快速高频请求测试 - 频率限制验证脚本                ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"{bcolors.ENDC}")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"目标服务器: {BASE_URL}")
    
    test_results = []
    
    # 测试1: 登录频率限制
    try:
        result = test_login_concurrent()
        test_results.append(("登录频率限制", result))
    except Exception as e:
        print(f"{bcolors.FAIL}测试异常: {e}{bcolors.ENDC}")
        import traceback
        traceback.print_exc()
        test_results.append(("登录频率限制", False))
    
    # 测试2: auth/me 频率限制
    try:
        result = test_auth_me_concurrent()
        test_results.append(("auth/me 频率限制", result))
    except Exception as e:
        print(f"{bcolors.FAIL}测试异常: {e}{bcolors.ENDC}")
        import traceback
        traceback.print_exc()
        test_results.append(("auth/me 频率限制", False))
    
    # 输出最终报告
    print_header("测试报告汇总")
    
    print(f"{bcolors.BOLD}{'测试项':<25} {'结果':<10}{bcolors.ENDC}")
    print("-" * 40)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = f"{bcolors.OKGREEN}✅ 通过{bcolors.ENDC}" if result else f"{bcolors.FAIL}❌ 失败{bcolors.ENDC}"
        print(f"  {test_name:<23} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("-" * 40)
    print(f"\n{bcolors.BOLD}总计: {bcolors.OKGREEN}{passed} 通过{bcolors.ENDC}, {bcolors.FAIL}{failed} 失败{bcolors.ENDC}")
    
    if failed == 0:
        print(f"\n{bcolors.OKGREEN}{bcolors.BOLD}🎉 所有测试通过！频率限制功能正常工作！{bcolors.ENDC}")
    else:
        print(f"\n{bcolors.FAIL}{bcolors.BOLD}⚠️  有 {failed} 项测试失败，请检查配置。{bcolors.ENDC}")
    
    print(f"\n测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
