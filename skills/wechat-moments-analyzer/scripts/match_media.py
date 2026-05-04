#!/usr/bin/env python3
"""
朋友圈媒体匹配工具
功能：解析 WeFlow 导出的 HTML，建立帖子 -> 本地媒体文件的索引
用法：
  python match_media.py --build --html-dir <dir> --output <path>
  python match_media.py --query <json_file> --media-index <path>
"""
import os
import sys
import json
import re
import glob


def parse_html_posts(html_path):
    """
    解析 WeFlow 导出的 HTML，提取每个帖子的信息和媒体文件。
    WeFlow HTML 结构：
      <div class="post">
        <div class="avatar">...</div>
        <div class="body">
          <div class="hd">
            <div class="nick">昵称</div>
            <div class="tm">时间</div>
          </div>
          <div class="txt">文字内容</div>
          <div class="loc">位置</div>
          <div class="media">
            <img src="media/xxx.jpg">
          </div>
        </div>
      </div>
    """
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    posts = []

    # 匹配每个帖子区块
    post_pattern = re.compile(
        r'<div[^>]*class=["\x27]post["\x27][^>]*>(.*?)</div>\s*</div>\s*</div>',
        re.DOTALL
    )

    # 更稳健的方式：按 .post 分割
    post_blocks = re.split(r'<div[^>]*class=["\x27]post["\x27][^>]*>', content)[1:]

    for block in post_blocks:
        # 提取昵称
        nick_m = re.search(r'class=["\x27]nick["\x27][^>]*>([^<]+)<', block)
        nickname = nick_m.group(1).strip() if nick_m else ""

        # 提取时间
        tm_m = re.search(r'class=["\x27]tm["\x27][^>]*>([^<]+)<', block)
        tm_str = tm_m.group(1).strip() if tm_m else ""

        # 提取文字内容
        txt_m = re.search(r'class=["\x27]txt["\x27][^>]*>(.*?)</div>', block, re.DOTALL)
        content_desc = ""
        if txt_m:
            content_desc = re.sub(r'<[^>]+>', '', txt_m.group(1)).strip()

        # 提取位置
        loc_m = re.search(r'class=["\x27]loc["\x27][^>]*>(.*?)</div>', block, re.DOTALL)
        location = ""
        if loc_m:
            location = re.sub(r'<[^>]+>', '', loc_m.group(1)).strip()

        # 提取媒体文件
        media_files = re.findall(r'<img[^>]+src=["\x27]([^"\x27]+)["\x27]', block)
        # 只保留本地相对路径
        local_media = []
        for src in media_files:
            if src.startswith('media/') or 'media/' in src:
                idx = src.find('media/')
                local_media.append(src[idx:])

        if nickname or content_desc:
            posts.append({
                "nickname": nickname,
                "tm_str": tm_str,
                "contentDesc": content_desc,
                "location": location,
                "media_files": local_media
            })

    return posts


def build_media_index(html_dir):
    """
    扫描 html_dir 下的所有 HTML 文件，建立媒体索引。
    """
    index = {
        "version": 1,
        "entries": []
    }

    html_files = sorted(glob.glob(os.path.join(html_dir, "**", "*.html"), recursive=True))
    for html_file in html_files:
        rel_dir = os.path.relpath(os.path.dirname(html_file), os.path.dirname(html_dir))
        media_dir = os.path.join(rel_dir, "media")

        posts = parse_html_posts(html_file)
        if posts:
            index["entries"].append({
                "html_file": os.path.basename(html_file),
                "media_dir": media_dir,
                "post_count": len(posts),
                "posts": posts
            })

    return index


def query_media_index(media_index, post_info):
    """
    根据帖子信息查找对应的本地媒体路径。
    匹配优先级：
    1. contentDesc 精确匹配
    2. nickname + tm_str 精确匹配
    3. nickname + contentDesc 前 30 字符匹配
    """
    content_desc = post_info.get("contentDesc", "")
    nickname = post_info.get("nickname", "")
    username = post_info.get("username", "")
    create_time = post_info.get("createTime", 0)

    best_match = None
    best_score = 0

    for entry in media_index.get("entries", []):
        for post in entry.get("posts", []):
            score = 0
            method = ""

            # contentDesc 精确匹配（最高优先级）
            if content_desc and post.get("contentDesc") == content_desc:
                score = 100
                method = "content_exact"
            elif content_desc and post.get("contentDesc") and \
                 post.get("contentDesc")[:30] == content_desc[:30]:
                score = 80
                method = "content_prefix"

            # nickname + 时间匹配
            if nickname and post.get("nickname") == nickname:
                if score < 70:
                    score = 70
                    method = "nickname_only"
                if create_time and post.get("tm_str"):
                    # 尝试解析时间字符串
                    score = max(score, 60)

            if score > best_score:
                best_score = score
                best_match = {
                    "media_files": post.get("media_files", []),
                    "match_method": method,
                    "html_file": entry.get("html_file"),
                    "media_dir": entry.get("media_dir")
                }

    if best_match and best_match["media_files"]:
        media_dir = best_match["media_dir"]
        base = os.path.dirname(os.path.dirname(os.path.join(
            os.path.expanduser("~/.openclaw/projects/moments-analysis"),
            media_dir
        )))
        full_paths = []
        for f in best_match["media_files"]:
            full_paths.append(os.path.normpath(os.path.join(
                os.path.expanduser("~/.openclaw/projects/moments-analysis"),
                media_dir,
                os.path.basename(f)
            )))
        best_match["local_paths"] = full_paths

    return best_match


def main():
    import argparse
    parser = argparse.ArgumentParser(description="朋友圈媒体匹配工具")
    parser.add_argument("--build", action="store_true", help="建立媒体索引")
    parser.add_argument("--html-dir", help="HTML 文件目录")
    parser.add_argument("--output", help="输出索引文件路径")
    parser.add_argument("--query", help="查询模式：传入帖子 JSON 文件路径")
    parser.add_argument("--media-index", help="媒体索引文件路径")
    parser.add_argument("--base-dir", help="项目根目录")

    args = parser.parse_args()

    base_dir = args.base_dir or os.path.expanduser("~/.openclaw/projects/moments-analysis")

    if args.build:
        html_dir = args.html_dir or os.path.join(base_dir, "raw")
        output = args.output or os.path.join(base_dir, "state", "media_index.json")
        os.makedirs(os.path.dirname(output), exist_ok=True)

        index = build_media_index(html_dir)
        with open(output, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

        total_posts = sum(e["post_count"] for e in index["entries"])
        print("OK: media index built, %d entries, %d posts total" % (
            len(index["entries"]), total_posts))
        print("Output: %s" % output)

    elif args.query:
        index_path = args.media_index or os.path.join(base_dir, "state", "media_index.json")
        if not os.path.exists(index_path):
            print("ERROR: media index not found, run --build first")
            return

        with open(index_path, "r", encoding="utf-8") as f:
            media_index = json.load(f)

        with open(args.query, "r", encoding="utf-8") as f:
            posts_data = json.load(f)

        post_list = posts_data.get("posts", []) if isinstance(posts_data, dict) else posts_data

        results = []
        for post in post_list:
            if post.get("media_count", 0) > 0:
                match = query_media_index(media_index, post)
                if match:
                    results.append({
                        "id": post.get("id"),
                        "nickname": post.get("nickname"),
                        "contentDesc": post.get("contentDesc", "")[:30],
                        "media_count": post.get("media_count", 0),
                        "matched_files": match.get("local_paths", []),
                        "method": match["match_method"]
                    })

        out_path = os.path.join(base_dir, "state", "media_match.json")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        matched = sum(1 for r in results if r["matched_files"])
        print("OK: %d posts with media, %d matched" % (len(results), matched))
        print("Output: %s" % out_path)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
