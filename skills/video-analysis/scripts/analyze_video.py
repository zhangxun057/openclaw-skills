#!/usr/bin/env python3
"""
Video Analysis via MiMo V2 Omni API.
Downloads video, converts format, uploads, and calls Omni for native video analysis.

Usage:
    python analyze_video.py <video_path_or_url> [--prompt "custom prompt"] [--fps 1] [--resolution default] [--duration 120]

Examples:
    python analyze_video.py ./video.mp4 --prompt "逐字转写视频中所有语音内容，带时间戳"
    python analyze_video.py "https://www.bilibili.com/video/BV1xxx/" --fps 2
    python analyze_video.py ./clip.mp4 --duration 60 --fps 1
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
import urllib.error

# ── Config ──────────────────────────────────────────────────────────────
OMNI_API_BASE = "https://token-plan-cn.xiaomimimo.com/v1/chat/completions"
OMNI_API_KEY = os.environ.get("MIMO_API_KEY", "")
UPLOAD_API = "https://tmpfiles.org/api/v1/upload"
UPLOAD_DL_PREFIX = "https://tmpfiles.org/dl/"

DEFAULT_PROMPT = "请详细分析这个视频：1. 逐字转写所有语音内容（带时间戳） 2. 屏幕上出现的所有文字、代码、界面元素 3. 视频主题和核心观点 4. 用中文输出，结构化列表格式"
DEFAULT_FPS = 1
DEFAULT_RESOLUTION = "default"
MAX_FILE_SIZE_MB = 100


def log(msg):
    print(f"[video-analysis] {msg}", file=sys.stderr)


# ── Step 1: Download video ──────────────────────────────────────────────
def is_url(s):
    return s.startswith("http://") or s.startswith("https://")


def get_yt_dlp_cmd():
    """Find yt-dlp executable, trying multiple locations."""
    import shutil
    # Try system PATH first
    path = shutil.which("yt-dlp")
    if path:
        return [path]
    # Try D:\anaconda\Scripts (Windows common install location)
    anaconda_yt = r"D:\anaconda\Scripts\yt-dlp.exe"
    if os.path.exists(anaconda_yt):
        return [anaconda_yt]
    # Fallback to plain name and let subprocess search PATH
    return ["yt-dlp"]


def download_video(source, output_path):
    """Download video from URL using yt-dlp, or copy local file."""
    if not is_url(source):
        if not os.path.exists(source):
            raise FileNotFoundError(f"Local file not found: {source}")
        # Copy to working directory if needed
        import shutil
        ext = os.path.splitext(source)[1].lower()
        if ext in ('.mp4', '.mkv', '.webm', '.avi', '.mov'):
            shutil.copy2(source, output_path)
            return output_path
        else:
            raise ValueError(f"Unsupported format: {ext}")

    log(f"Downloading: {source}")
    yt_cmd = get_yt_dlp_cmd()
    cmd = yt_cmd + [
        "-f", "worst[ext=mp4]/worst",
        "--merge-output-format", "mp4",
        "-o", output_path,
        source
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        # Try without format restriction
        cmd = yt_cmd + [
            "--merge-output-format", "mp4",
            "-o", output_path,
            source
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            raise RuntimeError(f"yt-dlp failed: {result.stderr}")

    if not os.path.exists(output_path):
        # yt-dlp might add a different extension
        for f in os.listdir(os.path.dirname(output_path) or '.'):
            fp = os.path.join(os.path.dirname(output_path) or '.', f)
            if fp.startswith(output_path.rsplit('.', 1)[0]):
                os.rename(fp, output_path)
                break

    return output_path


# ── Step 2: Convert to H.264 ───────────────────────────────────────────
def convert_to_h264(input_path, output_path=None, duration=None):
    """Convert video to H.264 MP4 (Omni compatible). Optionally trim duration."""
    if output_path is None:
        base, _ = os.path.splitext(input_path)
        output_path = f"{base}_h264.mp4"

    cmd = ["ffmpeg", "-y", "-i", input_path, "-c:v", "libx264", "-c:a", "aac", "-preset", "fast"]
    if duration:
        cmd.extend(["-t", str(duration)])
    cmd.append(output_path)

    log(f"Converting to H.264: {os.path.basename(output_path)}" + (f" (trim {duration}s)" if duration else ""))
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0 and not os.path.exists(output_path):
        raise RuntimeError(f"ffmpeg failed: {result.stderr[:500]}")

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    log(f"Output: {output_path} ({size_mb:.1f} MB)")
    if size_mb > MAX_FILE_SIZE_MB:
        raise ValueError(f"File too large: {size_mb:.1f} MB (max {MAX_FILE_SIZE_MB} MB)")

    return output_path


def check_needs_convert(video_path):
    """Check if video needs conversion (not H.264 MP4)."""
    cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", video_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return True  # Can't probe, assume needs convert
    try:
        data = json.loads(result.stdout)
        for s in data.get("streams", []):
            if s.get("codec_type") == "video" and s.get("codec_name") not in ("h264",):
                return True
        return False
    except:
        return True


# ── Step 3: Upload to temp hosting ─────────────────────────────────────
def upload_video(video_path):
    """Upload video to tmpfiles.org and return download URL."""
    log(f"Uploading: {os.path.basename(video_path)} ({os.path.getsize(video_path)/(1024*1024):.1f} MB)")

    cmd = ["curl.exe" if os.name == 'nt' else "curl", "-s", "-F", f"file=@{video_path}", UPLOAD_API]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"Upload failed: {result.stderr}")

    data = json.loads(result.stdout)
    if data.get("status") != "success":
        raise RuntimeError(f"Upload failed: {data}")

    view_url = data["data"]["url"]  # e.g., http://tmpfiles.org/32308834/clip.mp4
    # Convert to download URL: http://tmpfiles.org/ID/NAME → https://tmpfiles.org/dl/ID/NAME
    parts = view_url.replace("http://", "https://").split("tmpfiles.org/")
    dl_url = f"{UPLOAD_DL_PREFIX}{parts[1]}"

    log(f"Uploaded: {dl_url}")
    return dl_url


# ── Step 4: Call Omni API ──────────────────────────────────────────────
def call_omni(video_url, prompt, fps=DEFAULT_FPS, resolution=DEFAULT_RESOLUTION, max_tokens=4096):
    """Call MiMo V2 Omni API with video URL and prompt."""
    if not OMNI_API_KEY:
        raise ValueError("MIMO_API_KEY not set. Export it or pass via --api-key")

    body = json.dumps({
        "model": "mimo-v2-omni",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "video_url",
                        "video_url": {"url": video_url},
                        "fps": fps,
                        "media_resolution": resolution
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ],
        "max_completion_tokens": max_tokens
    }).encode("utf-8")

    req = urllib.request.Request(
        OMNI_API_BASE,
        data=body,
        headers={
            "Content-Type": "application/json",
            "api-key": OMNI_API_KEY,
            "Authorization": f"Bearer {OMNI_API_KEY}"
        }
    )

    log(f"Calling Omni API (fps={fps}, resolution={resolution}, max_tokens={max_tokens})")
    start = time.time()
    resp = urllib.request.urlopen(req, timeout=600)
    result = json.loads(resp.read().decode("utf-8"))
    elapsed = time.time() - start

    msg = result["choices"][0]["message"]["content"]
    usage = result.get("usage", {})
    log(f"Done in {elapsed:.1f}s | tokens: {json.dumps(usage, ensure_ascii=False)}")

    return {
        "content": msg,
        "usage": usage,
        "elapsed_seconds": round(elapsed, 1)
    }


# ── Main ───────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Analyze video using MiMo V2 Omni")
    parser.add_argument("source", help="Video file path or URL")
    parser.add_argument("--prompt", "-p", default=DEFAULT_PROMPT, help="Custom analysis prompt")
    parser.add_argument("--fps", type=float, default=DEFAULT_FPS, help="Frames per second (default: 1)")
    parser.add_argument("--resolution", default=DEFAULT_RESOLUTION, choices=["default", "max"], help="Media resolution")
    parser.add_argument("--duration", "-d", type=int, default=None, help="Max duration in seconds (trim video)")
    parser.add_argument("--max-tokens", type=int, default=4096, help="Max completion tokens")
    parser.add_argument("--api-key", default=None, help="MiMo API key (or set MIMO_API_KEY env)")
    parser.add_argument("--output", "-o", default=None, help="Output file for result JSON")
    parser.add_argument("--skip-upload", action="store_true", help="Skip upload, use local path (for testing)")
    parser.add_argument("--convert", action="store_true", help="Force convert to H.264")

    args = parser.parse_args()

    if args.api_key:
        global OMNI_API_KEY
        OMNI_API_KEY = args.api_key

    work_dir = tempfile.mkdtemp(prefix="video_analysis_")
    log(f"Working directory: {work_dir}")

    # Step 1: Get video file
    if is_url(args.source):
        raw_path = os.path.join(work_dir, "raw.mp4")
        download_video(args.source, raw_path)
    else:
        raw_path = args.source

    # Step 2: Convert if needed
    needs_convert = args.convert or check_needs_convert(raw_path)
    if needs_convert or args.duration:
        video_path = convert_to_h264(raw_path, os.path.join(work_dir, "converted.mp4"), duration=args.duration)
    else:
        video_path = raw_path

    # Step 3: Upload
    if args.skip_upload:
        # For testing with local file serving
        video_url = f"file://{os.path.abspath(video_path)}"
    else:
        video_url = upload_video(video_path)

    # Step 4: Call Omni
    result = call_omni(video_url, args.prompt, fps=args.fps, resolution=args.resolution, max_tokens=args.max_tokens)

    # Output
    output = {
        "source": args.source,
        "prompt": args.prompt,
        "fps": args.fps,
        "resolution": args.resolution,
        "result": result
    }

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        log(f"Saved to: {args.output}")

    # Print result to stdout
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
