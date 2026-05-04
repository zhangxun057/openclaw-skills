"""端到端分析 Pipeline：run_batch.py → generate_profiles.py"""
import sys, os, time, argparse, subprocess

sys.stdout.reconfigure(encoding='utf-8')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = r'C:\Users\44452\.openclaw\projects\moments-analysis\logs'
PROFILES_DIR = r'C:\Users\44452\.openclaw\projects\moments-analysis\profiles'


def fmt_duration(seconds):
    m, s = divmod(int(seconds), 60)
    return f"{m} 分 {s:02d} 秒" if m else f"{s} 秒"


def run_step(label, cmd, warn_only=False):
    print(f"\n{label}")
    t0 = time.time()
    result = subprocess.run(cmd, cwd=SCRIPT_DIR)
    elapsed = time.time() - t0
    if result.returncode != 0:
        if warn_only:
            print(f"  ! 警告：步骤失败（退出码 {result.returncode}），已跳过")
            return False
        print(f"  ✗ 失败（退出码 {result.returncode}），终止流程")
        sys.exit(result.returncode)
    print(f"  ✓ 完成，耗时 {fmt_duration(elapsed)}")
    return True


def main():
    parser = argparse.ArgumentParser(description='朋友圈端到端分析 Pipeline')
    parser.add_argument('--date', required=True, help='日期，格式 YYYY-MM-DD')
    parser.add_argument('--posts-file', default=None, help='输入 JSON 文件路径（默认 aw/{date}.json）')
    args = parser.parse_args()

    date = args.date
    posts_file = args.posts_file or os.path.join(SCRIPT_DIR, 'aw', f'{date}.json')
    analyzed_file = posts_file.replace('.json', '_analyzed.json')
    log_file = os.path.join(LOG_DIR, f'{date}.jsonl')
    profile_file = os.path.join(PROFILES_DIR, f'{date}_profiles.md')

    print(f"\n{'='*40}")
    print(f"朋友圈端到端分析 - {date}")
    print(f"{'='*40}")

    run_step(
        f"[1/2] 运行批量分析...\n  输入：{posts_file}\n  输出：{analyzed_file}",
        [sys.executable, os.path.join(SCRIPT_DIR, 'run_batch.py'),
         '--posts-file', posts_file, '--output-file', analyzed_file],
    )

    profile_ok = run_step(
        f"[2/2] 生成 Profile 文档...\n  输入：{log_file}\n  输出：{profile_file}",
        [sys.executable, os.path.join(SCRIPT_DIR, 'generate_profiles.py'), '--date', date],
        warn_only=True,
    )

    print(f"\n{'='*40}")
    print("完成！")
    print(f"- 分析结果：{analyzed_file}")
    if profile_ok:
        print(f"- Profile 文档：{profile_file}")
    print(f"{'='*40}\n")


if __name__ == '__main__':
    main()
