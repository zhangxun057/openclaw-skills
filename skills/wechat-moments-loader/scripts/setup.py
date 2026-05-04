"""
微信朋友圈自动加载器 - 依赖安装脚本
优先从本地assets/packages/离线安装，fallback到pip在线安装
"""
import subprocess
import sys
import os
import glob

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKAGES_DIR = os.path.join(SKILL_DIR, "assets", "packages")

# 依赖列表
DEPENDENCIES = [
    "opencv-python>=4.8.0",
    "pyautogui>=0.9.54",
    "pywin32>=306",
    "pillow>=10.0.0",
    "numpy>=1.24.0",
    "rapidocr_onnxruntime>=1.2.0",
    "requests>=2.31.0",
    "beautifulsoup4>=4.12.0",
]


def check_installed(package_name):
    """检查包是否已安装"""
    try:
        # 处理包名（取第一个单词，去掉版本号）
        name = package_name.split(">=")[0].split("==")[0].split("<")[0]
        # 特殊映射
        name_map = {
            "opencv-python": "cv2",
            "pywin32": "win32gui",
            "rapidocr_onnxruntime": "rapidocr_onnxruntime",
        "requests": "requests",
        "beautifulsoup4": "bs4",
        }
        import_name = name_map.get(name, name.replace("-", "_"))
        __import__(import_name)
        return True
    except ImportError:
        return False


def install_from_local(package_name):
    """从本地wheel文件安装"""
    name = package_name.split(">=")[0].split("==")[0].split("<")[0]

    if not os.path.isdir(PACKAGES_DIR):
        return False

    # 查找匹配的wheel文件
    patterns = [
        os.path.join(PACKAGES_DIR, f"{name}*.whl"),
        os.path.join(PACKAGES_DIR, f"{name.replace('-', '_')}*.whl"),
        os.path.join(PACKAGES_DIR, f"{name.replace('-', '-') }*.whl"),
    ]

    for pattern in patterns:
        wheels = glob.glob(pattern)
        if wheels:
            # 取最新的
            wheel = sorted(wheels)[-1]
            print(f"    本地安装: {os.path.basename(wheel)}")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--no-deps", wheel],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return True
            else:
                print(f"    本地安装失败: {result.stderr[:100]}")
                return False

    return False


def install_from_pip(package_spec):
    """从pip在线安装"""
    print(f"    在线安装: {package_spec}")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", package_spec],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        return True
    else:
        print(f"    在线安装失败: {result.stderr[:200]}")
        return False


def main():
    print("=" * 60)
    print("微信朋友圈自动加载器 - 依赖安装")
    print("=" * 60)

    print(f"\nSkill目录: {SKILL_DIR}")
    print(f"离线包目录: {PACKAGES_DIR}")
    print(f"离线包目录存在: {os.path.isdir(PACKAGES_DIR)}")

    if os.path.isdir(PACKAGES_DIR):
        wheels = glob.glob(os.path.join(PACKAGES_DIR, "*.whl"))
        print(f"离线包数量: {len(wheels)}")

    print(f"\n需要检查 {len(DEPENDENCIES)} 个依赖:\n")

    success_count = 0
    fail_count = 0
    skip_count = 0

    for dep in DEPENDENCIES:
        name = dep.split(">=")[0].split("==")[0]
        print(f"[{name}]")

        # 检查是否已安装
        if check_installed(name):
            print(f"    ✅ 已安装")
            skip_count += 1
            continue

        # 尝试本地安装
        if install_from_local(name):
            print(f"    ✅ 本地安装成功")
            success_count += 1
            continue

        # fallback到在线安装
        if install_from_pip(dep):
            print(f"    ✅ 在线安装成功")
            success_count += 1
            continue

        print(f"    ❌ 安装失败")
        fail_count += 1

    print("\n" + "=" * 60)
    print(f"结果: 跳过 {skip_count}, 安装 {success_count}, 失败 {fail_count}")

    if fail_count == 0:
        print("✅ 所有依赖就绪！")
        print("\n运行: python scripts/loader.py \"每组5次，更新到1小时前\"")
    else:
        print("⚠️ 部分依赖安装失败，请手动安装")
    print("=" * 60)


if __name__ == "__main__":
    main()
