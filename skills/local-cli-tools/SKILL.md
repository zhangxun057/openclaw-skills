---
name: local-cli-tools
description: |
  本地CLI工具集合管理技能。管理MiniMax海螺AI、Coze扣子、Lark-CLI飞书指挥官三个命令行工具。
  
  使用场景：
  1. 调用MiniMax生成音乐/视频/图片/语音
  2. 调用Coze管理Bot或工作流
  3. 调用Lark-CLI查询飞书企业数据
  4. CLI工具安装检测与自动安装
  
  触发条件：用户提到minimax、海螺、coze、扣子、飞书cli、lark-cli等关键词时。
version: 2.0.0
---

# 本地CLI工具管理技能

---

# 第一部分：MiniMax 海螺AI

## 安装检测

```python
import shutil
if not shutil.which('minimax'):
    exec("npm install -g @minimax-ai/cli")
```

## 核心命令

| 功能 | 命令模板 |
|------|----------|
| 音乐生成 | `minimax music generate --prompt "风格" --lyrics "歌词" --voice "音色" --output "文件名.mp3"` |
| 视频生成 | `minimax video generate --prompt "描述" --output "文件名.mp4"` |
| 图片生成 | `minimax image generate --prompt "描述" --output "文件名.png"` |
| 语音合成 | `minimax speech synthesize --text "内容" --voice "音色" --output "文件名.mp3"` |
| 文本对话 | `minimax text chat --message "问题"` |
| 查看配额 | `minimax quota show` |

## 音乐生成参数

| 参数 | 说明 |
|------|------|
| `--prompt` | 英文风格描述（必填） |
| `--lyrics` | 歌词内容，支持中文 |
| `--voice` | 音色：`young_female_clear`(清澈女声)、`young_female_sweet`(甜美女声)、`female_mature`(成熟女声)、`male_clear`(清澈男声)、`male_deep`(低沉男声) |
| `--output` | 输出文件路径 |
| `--timeout` | 超时秒数，默认300 |

## 故障排查

```bash
# 检查登录状态
minimax auth status

# 重新登录
minimax auth login

# 查看详细错误
minimax music generate ... --verbose
```

---

# 第二部分：Coze 扣子

## 安装检测

```python
import shutil
if not shutil.which('coze'):
    exec("npm install -g @coze/cli")
```

## 核心命令

| 功能 | 命令模板 |
|------|----------|
| Bot列表 | `coze bot list` |
| 运行工作流 | `coze workflow run <id> --input '{"key":"value"}'` |
| 添加知识库 | `coze knowledge add <文件>` |

## 全局参数

| 参数 | 说明 |
|------|------|
| `--format json` | JSON输出 |
| `--org-id` | 组织ID |
| `--space-id` | 空间ID |

---

# 第三部分：Lark-CLI 飞书指挥官

## 安装检测

```python
import shutil
if not shutil.which('lark-cli'):
    exec("npm install -g @larksuite/cli")
    exec("npx skills add larksuite/cli -y -g")
```

## 配置（安装后执行）

```bash
lark-cli config init --new    # 生成授权链接
lark-cli auth login           # 用户授权
```

## 核心命令

| 模块 | 常用命令 |
|------|----------|
| 审批 | `lark-cli approval list --topic 2` |
| 任务 | `lark-cli task list --query "关键词"` |
| 会议 | `lark-cli meeting minutes <id>` |
| 消息 | `lark-cli message search --query "关键词"` |
| 多维表格 | `lark-cli bitable records get <app-token>` |
| 电子表格 | `lark-cli sheet read <token> --range "A1:D10"` |
| 知识库 | `lark-cli wiki search --query "关键词"` |
| 日历 | `lark-cli calendar events list` |
| 通讯录 | `lark-cli contact search --query "姓名"` |
| 画板 | `lark-cli whiteboard export <id> --format png` |
| 邮件 | `lark-cli mail search --query "关键词"` |

---

# 第四部分：统一安装脚本

```python
import shutil
import subprocess

def ensure_cli(name, cmds):
    if not shutil.which(name):
        for cmd in cmds:
            subprocess.run(cmd, shell=True)
    return shutil.which(name) is not None

# 使用
ensure_cli('minimax', ['npm install -g @minimax-ai/cli'])
ensure_cli('coze', ['npm install -g @coze/cli'])
ensure_cli('lark-cli', ['npm install -g @larksuite/cli', 'npx skills add larksuite/cli -y -g'])
```

---

# 快速对照

| 需求 | CLI | 命令 |
|------|-----|------|
| 生成音乐/视频 | MiniMax | `minimax music generate` |
| 管理AI Bot | Coze | `coze bot list` |
| 飞书审批/任务/会议 | Lark-CLI | `lark-cli approval list` |

---

## Usage Logging

```bash
mkdir -p $HOME/.openclaw/skill-logs/local-cli-tools
echo "## [$(date '+%Y-%m-%d %H:%M:%S')]" >> $HOME/.openclaw/skill-logs/local-cli-tools/log.md
echo "- **User Request**: <request>" >> $HOME/.openclaw/skill-logs/local-cli-tools/log.md
echo "- **Action**: <action>" >> $HOME/.openclaw/skill-logs/local-cli-tools/log.md
echo "- **Result**: <result>" >> $HOME/.openclaw/skill-logs/local-cli-tools/log.md
```
