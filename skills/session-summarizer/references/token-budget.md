# Token 预算策略

## 核心目标

**在有限 Token 内完成高质量摘要**，避免上下文溢出。

---

## 总预算

| 项目 | Token 预算 | 说明 |
|------|-----------|------|
| **总预算** | ~50K-80K tokens | 根据会话数量动态调整 |
| 元数据读取 | ~1K tokens | 快速筛选 |
| 初步筛选 | ~5K tokens | 读取前 20 条消息 |
| 详细读取 | ~30K-60K tokens | 完整读取有价值的会话 |
| 摘要生成 | ~10K-15K tokens | 提炼和输出 |

---

## 分阶段策略

### 阶段 1：元数据读取（~1K tokens）

**目标**：不读取完整内容，先获取会话列表和基本信息。

**方法**：
```powershell
# 读取每个 session 文件的第一行和最后一行
Get-Content $path -First 1
Get-Content $path -Last 1
```

**输出**：
- 会话文件列表
- 时间范围
- 消息数量

---

### 阶段 2：初步筛选（~5K tokens）

**目标**：过滤掉明显无价值的会话。

**方法**：
```python
# 读取每个 session 的前 20 条消息
for line in lines[:20]:
    msg = json.loads(line)
    # 提取关键词
    # 判断是否包含业务内容
```

**筛选标准**：
- 消息数 <= 2 → 过滤（太短）
- 纯技术关键词（API/Key/Referer）→ 过滤
- 包含业务关键词 → 保留

---

### 阶段 3：详细读取（~30K-60K tokens）

**目标**：完整读取有价值的会话。

**策略**：
1. 按会话重要性排序（业务关键词多的优先）
2. 逐个读取完整内容
3. 达到 Token 预算上限后停止

**Token 控制**：
```python
token_count = 0
token_budget = 50000

for session in sessions:
    content = read_full_session(session)
    token_count += estimate_tokens(content)
    
    if token_count > token_budget:
        print(f"达到 Token 预算上限，停止读取")
        break
```

---

### 阶段 4：摘要生成（~10K-15K tokens）

**目标**：提炼结构化摘要。

**方法**：
1. 按摘要结构组织内容
2. 过滤技术细节
3. 保留关键信息

**字数控制**：
- 对话量少：1000-3000 字（~2K-5K tokens）
- 对话量中：3000-6000 字（~5K-10K tokens）
- 对话量多：6000-10000 字（~10K-15K tokens）

---

## Token 估算公式

**中文字符**：1 字 ≈ 1.5 tokens

**英文字符**：1 单词 ≈ 1.3 tokens

**代码/JSON**：1 字符 ≈ 0.5 tokens

**示例**：
```
82.4 KB 的 chat-log 文件
≈ 82,400 字符
≈ 40,000 中文字符（假设 50% 是中文）
≈ 60,000 tokens
```

---

## 优化技巧

### 1. 限制单次读取大小

```python
# 每个 session 最多读取 5000 字符
limit = 5000
content = content[:limit]
```

### 2. 分批次读取

```python
# 先读取元数据
# 筛选出 Top 10 重要会话
# 再读取详细内容
```

### 3. 压缩技术细节

```python
# 原始：
"调用 886 接口，参数为{'key': 'xxx', 'secret': 'yyy'}，返回{...}"

# 压缩后：
"调用企查查 886 接口，获取企业基本信息"
```

### 4. 使用摘要而非原文

```python
# 不保留原文：
"用户说：'帮我查一下北京清格科技有限公司'"

# 保留摘要：
"用户指令：查询北京清格科技有限公司"
```

---

## 监控和日志

**每次执行后记录**：
```markdown
## Token 使用报告

- 元数据读取：1,200 tokens
- 初步筛选：4,800 tokens
- 详细读取：42,500 tokens
- 摘要生成：8,300 tokens
- **总计**：56,800 tokens
- 预算上限：80,000 tokens
- 使用率：71%
```

---

_更新时间：2026-04-04_
