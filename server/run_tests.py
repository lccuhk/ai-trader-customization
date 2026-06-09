#!/usr/bin/env python3
"""
统一测试运行脚本 - 用于本地和 CI/CD 环境下运行测试

用法:
    python run_tests.py [options]

选项:
    --unit              只运行单元测试 (默认)
    --security          只运行安全测试
    --performance       运行性能基准测试 (需要启动服务器)
    --all               运行所有测试 (单元 + 性能)
    --verbose, -v          详细输出
    --no-performance    跳过性能测试
"""

import sys
import os
import argparse
import subprocess
import time
from pathlib import Path

# 添加项目路径
SERVER_DIR = Path(__file__).resolve().parent
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))


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


def run_command(cmd, cwd=None, env=None):
    """运行命令并返回结果"""
    print(f"{bcolors.OKCYAN}运行: {cmd}{bcolors.ENDC}")
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"{bcolors.WARNING}{result.stderr}{bcolors.ENDC}")
    return result.returncode


def run_unit_tests(verbose=False):
    """运行所有单元测试"""
    print_header("运行单元测试")
    
    cmd = "python3 -m pytest tests/ -v --tb=short --ignore=tests/test_security_performance.py"
    if verbose:
        cmd += " -v"
    
    returncode = run_command(cmd, cwd=SERVER_DIR)
    
    if returncode == 0:
        print(f"\n{bcolors.OKGREEN}✅ 所有单元测试通过{bcolors.ENDC}")
    else:
        print(f"\n{bcolors.FAIL}❌ 单元测试失败{bcolors.ENDC}")
    
    return returncode


def run_security_tests(verbose=False):
    """运行安全测试"""
    print_header("运行安全测试")
    
    cmd = "python3 -m pytest tests/test_security_unit.py"
    if verbose:
        cmd += " -v"
    
    returncode = run_command(cmd, cwd=SERVER_DIR)
    
    if returncode == 0:
        print(f"\n{bcolors.OKGREEN}✅ 安全测试通过{bcolors.ENDC}")
    else:
        print(f"\n{bcolors.FAIL}❌ 安全测试失败{bcolors.ENDC}")
    
    return returncode


def run_performance_tests():
    """运行性能基准测试"""
    print_header("运行性能基准测试")
    
    # 启动服务器
    print(f"{bcolors.OKCYAN}启动后端服务器...{bcolors.ENDC}")
    server_process = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=SERVER_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # 等待服务器启动
    time.sleep(5)
    
    try:
        # 运行性能测试
        cmd = "python3 tests/test_security_performance.py"
        returncode = run_command(cmd, cwd=SERVER_DIR)
        
        if returncode == 0:
            print(f"\n{bcolors.OKGREEN}✅ 性能测试通过{bcolors.ENDC}")
        else:
            print(f"\n{bcolors.FAIL}❌ 性能测试失败{bcolors.ENDC}")
        
        return returncode
    finally:
        # 停止服务器
        print(f"{bcolors.OKCYAN}停止后端服务器...{bcolors.ENDC}")
        server_process.terminate()
        server_process.wait()


def main():
    parser = argparse.ArgumentParser(description='统一测试运行脚本')
    parser.add_argument('--unit', action='store_true', help='只运行单元测试')
    parser.add_argument('--security', action='store_true', help='只运行安全测试')
    parser.add_argument('--performance', action='store_true', help='运行性能基准测试')
    parser.add_argument('--all', action='store_true', help='运行所有测试')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    parser.add_argument('--no-performance', action='store_true', help='跳过性能测试')
    
    args = parser.parse_args()
    
    print(f"\n{bcolors.HEADER}{bcolors.BOLD}")
    print("╔══════════════════════════════════════════════════════════════════════════╗")
    print("║                        测试运行脚本                                    ║")
    print("╚══════════════════════════════════════════════════════════════════════════╝")
    print(f"{bcolors.ENDC}")
    print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 默认行为
    if not any([args.unit, args.security, args.performance, args.all]):
        args.unit = True
    
    exit_code = 0
    
    # 运行安全测试
    if args.security or args.all:
        result = run_security_tests(args.verbose)
        exit_code = max(exit_code, result)
    
    # 运行单元测试
    if args.unit or args.all:
        result = run_unit_tests(args.verbose)
        exit_code = max(exit_code, result)
    
    # 运行性能测试
    if args.performance or (args.all and not args.no_performance):
        result = run_performance_tests()
        exit_code = max(exit_code, result)
    
    # 总结
    print_header("测试总结")
    if exit_code == 0:
        print(f"{bcolors.OKGREEN}✅ 所有测试通过{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}❌ 部分测试失败，退出码: {exit_code}{bcolors.ENDC}")
    
    print(f"\n测试完成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
