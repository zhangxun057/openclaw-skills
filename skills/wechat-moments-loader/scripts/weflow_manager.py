#!/usr/bin/env python3
"""
WeFlow服务管理器
功能：自动检查、下载、启动WeFlow API服务
"""

import subprocess
import sys
import time
import os
import argparse
import requests
import urllib.request
import zipfile
import shutil

WEFLOW_DIR = os.path.expanduser("D:/WeFlow")
API_BASE = "http://127.0.0.1:5032"
WEFLOW_REPO = "https://github.com/hicccc77/WeFlow"
WEFLOW_RELEASE = "https://github.com/hicccc77/WeFlow/releases"

def check_service():
    """检查WeFlow服务是否运行"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def download_weflow():
    """自动下载WeFlow"""
    print("[INFO] WeFlow未安装，正在自动下载...")
    
    try:
        # 使用git克隆
        parent_dir = os.path.dirname(WEFLOW_DIR)
        os.makedirs(parent_dir, exist_ok=True)
        
        print(f"[INFO] 克隆仓库: {WEFLOW_REPO}")
        result = subprocess.run(
            ["git", "clone", WEFLOW_REPO, WEFLOW_DIR],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print("[OK] WeFlow下载完成")
            return True
        else:
            print(f"[ERROR] Git克隆失败: {result.stderr}")
            print("[INFO] 请手动下载:")
            print(f"  访问: {WEFLOW_RELEASE}")
            return False
            
    except Exception as e:
        print(f"[ERROR] 下载失败: {e}")
        print("[INFO] 请手动下载WeFlow并放置在:")
        print(f"  {WEFLOW_DIR}")
        return False

def install_dependencies():
    """安装WeFlow依赖"""
    print("[INFO] 正在安装依赖...")
    
    try:
        result = subprocess.run(
            ["npm", "install"],
            cwd=WEFLOW_DIR,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print("[OK] 依赖安装完成")
            return True
        else:
            print(f"[ERROR] 依赖安装失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERROR] 安装依赖失败: {e}")
        return False

WEFLOW_EXE = os.path.join(WEFLOW_DIR, "WeFlow.exe")

def start_service():
    """启动WeFlow服务（兼容exe和npm源码两种方式）"""
    print("[INFO] 正在启动WeFlow服务...")

    if not os.path.exists(WEFLOW_DIR):
        print(f"[ERROR] 找不到WeFlow目录: {WEFLOW_DIR}")
        return False

    try:
        # 优先用exe（打包版）
        if os.path.exists(WEFLOW_EXE):
            cmd = [WEFLOW_EXE]
            kwargs = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
            if sys.platform == 'win32':
                kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE
            subprocess.Popen(cmd, **kwargs)
        else:
            # 源码版用npm
            npm = "npm.cmd" if sys.platform == 'win32' else "npm"
            node_modules = os.path.join(WEFLOW_DIR, "node_modules")
            if not os.path.exists(node_modules):
                print("[INFO] 安装npm依赖...")
                subprocess.run([npm, "install"], cwd=WEFLOW_DIR, timeout=300)
            subprocess.Popen(
                [npm, "run", "dev"], cwd=WEFLOW_DIR,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

        print("[INFO] 等待服务启动...")
        for i in range(30):
            time.sleep(2)
            if check_service():
                print("[OK] WeFlow服务已启动")
                return True
            if i % 5 == 0 and i > 0:
                print(f"  等待中... ({i*2}s)")
        print("[ERROR] 服务启动超时")
        return False
    except Exception as e:
        print(f"[ERROR] 启动失败: {e}")
        return False

def stop_service():
    """停止WeFlow服务"""
    print("[INFO] 正在停止WeFlow服务...")
    try:
        if sys.platform == 'win32':
            subprocess.run(["taskkill", "/F", "/IM", "node.exe"], capture_output=True)
        else:
            subprocess.run(["pkill", "-f", "weflow"], capture_output=True)
        print("[OK] 服务已停止")
        return True
    except Exception as e:
        print(f"[ERROR] 停止失败: {e}")
        return False

def check_wechat_connection():
    """检查微信数据库连接状态"""
    try:
        response = requests.get(f"{API_BASE}/api/v1/contacts?limit=1", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('contacts'):
                return True
        return False
    except:
        return False

def wait_for_wechat(timeout=300):
    """等待微信连接"""
    print("[INFO] 等待WeFlow连接微信数据库...")
    print("[INFO] 请确保微信桌面版已登录")
    
    for i in range(timeout):
        if check_wechat_connection():
            print("[OK] 微信数据库已连接")
            return True
        time.sleep(1)
        if i % 10 == 0:
            print(f"  等待微信连接... ({i}s)")
    
    print("[WARN] 等待超时，但服务可能仍在连接中")
    return False

def main():
    parser = argparse.ArgumentParser(description="WeFlow服务管理器（自动下载版）")
    parser.add_argument("--action", choices=["start", "stop", "status", "restart", "setup"], 
                        default="status", help="操作类型")
    parser.add_argument("--wait-wechat", action="store_true", help="启动后等待微信连接")
    args = parser.parse_args()
    
    if args.action == "status":
        if check_service():
            print("[OK] WeFlow服务运行中")
            print(f"[INFO] API地址: {API_BASE}")
            if check_wechat_connection():
                print("[OK] 微信数据库已连接")
            else:
                print("[WARN] 微信数据库未连接")
        else:
            print("[WARN] WeFlow服务未运行")
            print("[INFO] 使用 --action start 启动服务")
    
    elif args.action == "start":
        if check_service():
            print("[OK] 服务已在运行中")
            if args.wait_wechat:
                wait_for_wechat()
        else:
            if start_service() and args.wait_wechat:
                wait_for_wechat()
    
    elif args.action == "stop":
        stop_service()
    
    elif args.action == "restart":
        stop_service()
        time.sleep(2)
        start_service()
        if args.wait_wechat:
            wait_for_wechat()
    
    elif args.action == "setup":
        print("=== WeFlow自动安装 ===")
        if not os.path.exists(WEFLOW_DIR):
            if download_weflow():
                install_dependencies()
                print("[OK] WeFlow安装完成，使用 --action start 启动")
            else:
                print("[ERROR] 安装失败")
        else:
            print("[INFO] WeFlow已安装")
            if not os.path.exists(os.path.join(WEFLOW_DIR, "node_modules")):
                install_dependencies()

if __name__ == "__main__":
    main()
