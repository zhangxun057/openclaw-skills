"""多维度并发提取主控脚本 — 维度内全并发 + 回头看"""
import json, sys, os, time, argparse
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extract_events import extract_events
from extract_traits import extract_traits
from extract_post_type import extract_post_type
from extract_signals import extract_signals

# ---------------------------------------------------------------------------
# 维度定义
# ---------------------------------------------------------------------------
DIMENSIONS = [
    ('events', extract_events, []),       # 空值占位：空列表
    ('traits', extract_traits, {}),       # 空值占位：空字典
    ('post_type', extract_post_type, None),  # 空值占位：None
    ('signals', extract_signals, []),     # 空值占位：空列表
]

DIM_NAMES = [d[0] for d in DIMENSIONS]

# ---------------------------------------------------------------------------
# 配置读取
# ---------------------------------------------------------------------------
def get_all_configs():
    """读取主模型 + 备选模型配置"""
    cfg_path = r'C:\Users\44452\.openclaw\openclaw.json'
    with open(cfg_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    
    ali = cfg['models']['providers']['aliyun-bailian']
    primary = {
        'apiKey': ali['apiKey'],
        'baseUrl': ali['baseUrl'],
        'model': 'qwen3.6-plus'
    }
    
    fallbacks = []
    fallbacks.append({
        'apiKey': ali['apiKey'],
        'baseUrl': ali['baseUrl'],
        'model': 'qwen3.5-plus'
    })
    if 'minimax' in cfg['models']['providers']:
        mm = cfg['models']['providers']['minimax']
        fallbacks.append({
            'apiKey': mm['apiKey'],
            'baseUrl': mm['baseUrl'],
            'model': mm.get('defaultModel', 'MiniMax-M2.7')
        })
    
    return primary, fallbacks

# ---------------------------------------------------------------------------
# 批次成功检测
# ---------------------------------------------------------------------------
def is_empty_result(value, empty_value):
    """判断一个结果是否为空值（仅用于最终合并统计）"""
    if value is None:
        return True
    if isinstance(empty_value, list) and isinstance(value, list) and len(value) == 0:
        return True
    if isinstance(empty_value, dict) and isinstance(value, dict) and len(value) == 0:
        return True
    return value == empty_value

def find_failed_batches(batch_success_flags):
    """找出执行失败的批次索引（API报错、格式错误、数量不匹配）"""
    return sorted(idx for idx, ok in enumerate(batch_success_flags) if not ok)

# ---------------------------------------------------------------------------
# 并发执行一个维度
# ---------------------------------------------------------------------------
LOG_DIR = r'C:\Users\44452\.openclaw\projects\moments-analysis\logs'

def _write_jsonl_log(entry: dict):
    os.makedirs(LOG_DIR, exist_ok=True)
    log_path = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y-%m-%d')}.jsonl")
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')

def run_dimension_concurrent(dimension_name, extractor_func, posts_batches, api_key, base_url, fallback_configs, max_workers=10):
    """并发处理一个维度的所有批次，返回 (results, success_flags)"""
    num_batches = len(posts_batches)
    results = [None] * num_batches
    success_flags = [False] * num_batches
    done_count = 0
    lock = Lock()

    def process_one_batch(batch_idx, batch):
        t0 = time.time()
        try:
            result = extractor_func(batch, api_key, base_url, fallback_configs)
            elapsed = time.time() - t0
            # 成功判断：返回列表且数量与输入一致
            if not isinstance(result, list):
                raise ValueError(f"返回格式错误：期望list，得到{type(result).__name__}")
            if len(result) != len(batch):
                raise ValueError(f"数量不匹配：输入{len(batch)}条，输出{len(result)}条")
            nonlocal done_count
            with lock:
                done_count += 1
                print(f"    [{done_count}/{num_batches}] {dimension_name} batch#{batch_idx+1} OK ({elapsed:.1f}s, {len(batch)}条)")
            _write_jsonl_log({
                'batch_id': batch_idx, 'dimension': dimension_name,
                'posts_count': len(batch), 'result_count': len(result),
                'success': True, 'elapsed_s': round(elapsed, 2),
                'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')
            })
            return batch_idx, result, True
        except Exception as e:
            elapsed = time.time() - t0
            with lock:
                done_count += 1
                print(f"    [{done_count}/{num_batches}] {dimension_name} batch#{batch_idx+1} FAILED ({elapsed:.1f}s) - {str(e)[:80]}")
            _write_jsonl_log({
                'batch_id': batch_idx, 'dimension': dimension_name,
                'posts_count': len(batch), 'result_count': 0,
                'success': False, 'error': str(e)[:200], 'elapsed_s': round(elapsed, 2),
                'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')
            })
            return batch_idx, None, False

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_one_batch, idx, batch): idx for idx, batch in enumerate(posts_batches)}
        for future in as_completed(futures):
            batch_idx, result, ok = future.result()
            results[batch_idx] = result
            success_flags[batch_idx] = ok

    return results, success_flags

# ---------------------------------------------------------------------------
# 回头看：重试空值批次
# ---------------------------------------------------------------------------
def lookback_retry(dimension_results, success_flags, posts_batches, api_key, base_url, fallback_configs, extractor_func, dimension_name, max_workers=10, max_rounds=2):
    """回头看：重试失败批次（API报错/格式错误/数量不匹配），最多N轮"""
    for round_idx in range(max_rounds):
        failed_indices = find_failed_batches(success_flags)
        if not failed_indices:
            print(f"    {dimension_name} 回头看第{round_idx+1}轮: 无失败批次，跳过")
            break

        print(f"    {dimension_name} 回头看第{round_idx+1}轮: {len(failed_indices)} 个批次失败，重试...")

        retry_batches = [(idx, posts_batches[idx]) for idx in failed_indices]
        retry_results, retry_flags = run_dimension_concurrent(
            f"{dimension_name}(retry{round_idx+1})",
            extractor_func,
            [b for _, b in retry_batches],
            api_key, base_url, fallback_configs,
            max_workers=max_workers
        )

        for (batch_idx, _), new_result, new_ok in zip(retry_batches, retry_results, retry_flags):
            dimension_results[batch_idx] = new_result
            success_flags[batch_idx] = new_ok

    final_failed = find_failed_batches(success_flags)
    if final_failed:
        print(f"    ⚠ {dimension_name} 最终仍有 {len(final_failed)} 个批次失败")
    else:
        print(f"    ✓ {dimension_name} 全部完成")

    return dimension_results, success_flags

# ---------------------------------------------------------------------------
# 断点续跑：保存/加载中间状态
# ---------------------------------------------------------------------------
def get_checkpoint_path(output_file):
    """checkpoint文件路径"""
    base = output_file.replace('.json', '')
    return f"{base}_checkpoint.json"

def save_checkpoint(output_file, dimension_order, dimension_results_map, batch_results):
    """保存中间状态"""
    cp = get_checkpoint_path(output_file)
    checkpoint = {
        'dimension_order': dimension_order,
        'dimension_results_map': dimension_results_map,  # {dim_name: [batch_results]}
        'batch_results': batch_results,  # 已合并的最终结果
        'completed_dimensions': dimension_order,
    }
    with open(cp, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=2)

def load_checkpoint(output_file):
    """加载中间状态"""
    cp = get_checkpoint_path(output_file)
    if not os.path.exists(cp):
        return None
    with open(cp, 'r', encoding='utf-8') as f:
        return json.load(f)

# ---------------------------------------------------------------------------
# 合并批次结果为最终记录
# ---------------------------------------------------------------------------
def merge_batch_results(all_dimension_results, posts, batch_size):
    """将4个维度的批次结果合并为最终记录列表"""
    num_batches = len(all_dimension_results['events'])
    final = []
    
    for batch_idx in range(num_batches):
        ev_batch = all_dimension_results['events'][batch_idx]
        tr_batch = all_dimension_results['traits'][batch_idx]
        pt_batch = all_dimension_results['post_type'][batch_idx]
        sg_batch = all_dimension_results['signals'][batch_idx]
        
        # 找到该批次在原posts中的起始位置
        start = batch_idx * batch_size
        
        for i in range(len(ev_batch)):
            post = posts[start + i] if (start + i) < len(posts) else {}
            record = {
                'wxid': post.get('wxid', post.get('username', '')),
                'nickname': post.get('nickname', ''),
                'content': post.get('contentDesc', post.get('content', '')),
                'post_type': pt_batch[i] if i < len(pt_batch) else None,
                'traits': tr_batch[i] if i < len(tr_batch) else {},
                'events': ev_batch[i] if i < len(ev_batch) else [],
                'signals': sg_batch[i] if i < len(sg_batch) else [],
            }
            # 检查是否有空值
            failed = []
            if is_empty_result(record['events'], []):
                failed.append('events')
            if is_empty_result(record['traits'], {}):
                failed.append('traits')
            if is_empty_result(record['post_type'], None):
                failed.append('post_type')
            if is_empty_result(record['signals'], []):
                failed.append('signals')
            if failed:
                record['_failed_fields'] = failed
            final.append(record)
    
    return final

# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def run_full_analysis(posts_file, batch_size=10, output_file=None, max_workers=10, max_concurrent_batches=30):
    """完整分析流程 — 维度内全并发 + 回头看"""
    with open(posts_file, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    # 支持两种格式：直接数组 或 {"timeline": [...]} 包裹格式
    posts = raw.get('timeline', raw) if isinstance(raw, dict) else raw
    # 字段标准化：contentDesc -> content，避免提取器读取失败
    for p in posts:
        if 'contentDesc' in p and 'content' not in p:
            p['content'] = p.pop('contentDesc')
    
    primary, fallbacks = get_all_configs()
    api_key, base_url = primary['apiKey'], primary['baseUrl']
    
    output_file = output_file or posts_file.replace('.json', '_analyzed.json')
    
    # 检查checkpoint
    checkpoint = load_checkpoint(output_file)
    if checkpoint:
        print(f"发现checkpoint: 已完成 {len(checkpoint.get('completed_dimensions', []))} 个维度")
        # 可以恢复已完成的维度结果
        existing_dim_results = checkpoint.get('dimension_results_map', {})
        completed_dims = checkpoint.get('completed_dimensions', [])
    else:
        existing_dim_results = {}
        completed_dims = []
    
    # 如果已有输出文件但没有checkpoint，检查是否为完整结果
    if os.path.exists(output_file) and not checkpoint:
        with open(output_file, 'r', encoding='utf-8') as f:
            existing_results = json.load(f)
        if existing_results:
            print(f"发现已有结果: {len(existing_results)} 条，直接返回")
            return existing_results
    
    # 划分批次
    num_batches = (len(posts) + batch_size - 1) // batch_size
    posts_batches = []
    for i in range(num_batches):
        start = i * batch_size
        end = min(start + batch_size, len(posts))
        posts_batches.append(posts[start:end])
    
    print(f"总共 {len(posts)} 条，分 {num_batches} 批，{max_workers} 并发，每轮最多 {max_concurrent_batches} 批")
    print("=" * 60)

    # 按维度循环
    all_dimension_results = existing_dim_results.copy()

    for dim_name, extractor_func, empty_value in DIMENSIONS:
        if dim_name in completed_dims:
            print(f"\n维度 {dim_name}: 已完成（从checkpoint恢复），跳过")
            continue

        print(f"\n{'='*60}")
        print(f"维度 {dim_name}：并发处理 {num_batches} 个批次（每轮最多 {max_concurrent_batches} 批）...")
        print("=" * 60)

        t0 = time.time()

        # 分批执行：每次最多 max_concurrent_batches 批
        dim_results = [None] * num_batches
        success_flags = [False] * num_batches
        for chunk_start in range(0, num_batches, max_concurrent_batches):
            chunk = posts_batches[chunk_start:chunk_start + max_concurrent_batches]
            print(f"  批次 {chunk_start+1}~{chunk_start+len(chunk)}/{num_batches}...")
            chunk_results, chunk_flags = run_dimension_concurrent(
                dim_name, extractor_func, chunk,
                api_key, base_url, fallbacks, max_workers=max_workers
            )
            for i, (r, ok) in enumerate(zip(chunk_results, chunk_flags)):
                dim_results[chunk_start + i] = r
                success_flags[chunk_start + i] = ok

        elapsed = time.time() - t0
        print(f"  维度 {dim_name} 完成，总耗时 {elapsed:.1f}s")

        # 回头看：重试失败批次
        dim_results, success_flags = lookback_retry(
            dim_results, success_flags, posts_batches, api_key, base_url, fallbacks,
            extractor_func, dim_name, max_workers=max_workers
        )

        all_dimension_results[dim_name] = dim_results
        
        # 保存checkpoint（断点续跑）
        save_checkpoint(output_file, list(all_dimension_results.keys()), all_dimension_results, [])
        print(f"  ✓ 已保存checkpoint")
    
    print(f"\n{'='*60}")
    print("所有维度完成，合并结果...")
    print("=" * 60)
    
    # 合并为最终结果
    final_results = merge_batch_results(all_dimension_results, posts, batch_size)
    
    # 保存最终结果
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_results, f, ensure_ascii=False, indent=2)
    
    # 清理checkpoint
    cp_path = get_checkpoint_path(output_file)
    if os.path.exists(cp_path):
        os.remove(cp_path)
    
    # 统计
    print(f"\n{'='*60}")
    print(f"完成! 共处理 {len(final_results)} 条")
    failed_count = sum(1 for r in final_results if r.get('_failed_fields'))
    if failed_count:
        print(f"⚠ 有 {failed_count} 条记录存在部分字段失败")
        # 统计每个字段的失败数
        field_fail_counts = {}
        for r in final_results:
            for f in r.get('_failed_fields', []):
                field_fail_counts[f] = field_fail_counts.get(f, 0) + 1
        for f, c in sorted(field_fail_counts.items()):
            print(f"   {f}: {c} 条")
    else:
        print(f"✓ 全部成功，无失败字段")
    
    return final_results

def main():
    parser = argparse.ArgumentParser(description='多维度并发提取朋友圈数据（维度内全并发 + 回头看）')
    parser.add_argument('--posts-file', type=str, required=True, help='输入JSON文件路径')
    parser.add_argument('--batch-size', type=int, default=10, help='每批数量，默认10')
    parser.add_argument('--output-file', type=str, default=None, help='输出JSON文件路径')
    parser.add_argument('--max-workers', type=int, default=10, help='并发线程数，默认10')
    parser.add_argument('--max-concurrent-batches', type=int, default=30, help='每轮最多并发批次数，默认30')

    args = parser.parse_args()

    output_file = args.output_file or args.posts_file.replace('.json', '_analyzed.json')

    run_full_analysis(args.posts_file, args.batch_size, output_file, args.max_workers, args.max_concurrent_batches)
    print(f"结果已保存到: {output_file}")

if __name__ == '__main__':
    main()
