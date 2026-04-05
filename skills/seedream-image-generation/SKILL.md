# seedream-image-generation

## 触发条件
用户要求用 Seedream 生成图片、使用字节生图、AI 生图时激活。

## 功能
调用字节 Seedream 图像生成 API，支持文生图、图生图、多图融合、组图，生成后自动上传到文件服务器返回持久化链接。

## 接口信息
- **URL**: https://ark.cn-beijing.volces.com/api/v3/images/generations
- **API Key**: 环境变量 ARK_API_KEY

## 支持模型

**⚠️ 推荐使用**：`doubao-seedream-4-5-251128`（最稳定，生产环境默认）

| 模型 | 说明 | 支持功能 | 稳定性 |
|------|------|----------|--------|
| doubao-seedream-4-5-251128 | **生产环境默认** | 4.5 版本、文生图、图生图、多图融合 | ✅ 稳定 |
| doubao-seedream-4.0 | 经典版 | 1K/2K/4K | ✅ 稳定 |
| doubao-seedream-5.0-lite | 最新测试版 | 联网搜索、组图、多图融合、png 输出 | ⚠️ 测试中 |
| doubao-seedream-3.0-t2i | 轻量版 | 仅文生图 | ✅ 稳定 |

## 使用方式

### 命令行
```bash
cd ~/.openclaw/workspace/skills/seedream-image-generation/scripts

# 文生图
python3 seedream_api.py generate-upload "一只猫"

# 单图生图（图生图）
python3 seedream_api.py generate-upload "将背景换成海边" --image "https://xxx.jpg"

# 多图融合
python3 seedream_api.py generate-upload "将图 1 的服装换为图 2 的服装" --images "URL1,URL2"

# 组图模式
python3 seedream_api.py generate-upload "生成 4 张不同颜色的跑车" --sequential --max-images 4

# 指定参数
python3 seedream_api.py generate-upload "提示词" --size 4K --format png
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| --model | 模型版本 | doubao-seedream-4-5-251128 |
| --size | 分辨率 | 2K |
| --watermark | 加水印 | false |
| --image | 单张参考图 URL | - |
| --images | 多张参考图 URL（逗号分隔） | - |
| --sequential | 开启组图模式 | disabled |
| --max-images | 最大图片数 | 15 |
| --format | 输出格式 (png/jpeg) | png |

### 分辨率选项

| 分辨率 | 像素 |
|--------|------|
| 1K | 1024x1024 |
| 2K | 2048x2048 |
| 3K | 3072x3072 (仅 5.0-lite) |
| 4K | 4096x4096 |

## 环境变量
```bash
export ARK_API_KEY="你的 API Key"
```
不设置则使用默认密钥。

## 文件服务器
生成后自动上传到：https://mjy.gzlex.com:8095

返回永久链接：
```
https://mjyp1.gzlex.com/jjspublic/agent/plugins/2026_3_17_xxx.png
```

## 使用示例

**文生图：**
> "用 Seedream 生成一只猫"

**图生图：**
> "用 Seedream 把这张图的背景换成海边"

**多图融合：**
> "用 Seedream 将图 1 的服装换为图 2 的服装"

**组图：**
> "用 Seedream 生成 4 张不同风格的城市风景图"

**指定分辨率和格式：**
> "用 Seedream 生成一张 4K 分辨率的白酒海报"

## 返回
生成完成后返回文件服务器链接（永久有效），可直接在消息中查看图片。

## 稳定性保障

### ✅ 自动重试机制
- **重试次数**：最多 3 次
- **退避策略**：指数退避（1s → 2s → 4s）
- **触发条件**：
  - API 超时
  - 网络连接失败
  - API 返回错误（5xx）

### ⏱️ 智能超时处理
| 操作类型 | 超时时间 | 说明 |
|---------|---------|------|
| 文生图 | 120 秒 | 默认超时 |
| 图生图 | 180 秒 | 需要处理参考图 |
| 文件上传 | 60 秒 | 上传到文件服务器 |
| 图片下载 | 30 秒 | 从 API 下载临时图 |
| 自定义 | `--timeout` | 手动指定超时 |

### 🔍 状态验证
- ✅ 检查 API Key 配置
- ✅ 验证 HTTP 状态码
- ✅ 检查返回数据结构
- ✅ 验证图片 URL 可访问
- ✅ 确认上传结果

### 🛡️ 错误回退策略
| 错误类型 | 回退方案 |
|---------|---------|
| 文件服务器上传失败 | 返回原始 API URL（24 小时有效） |
| 生成失败（重试 3 次） | 返回详细错误信息 + 重试建议 |
| 网络波动 | 自动重试 + 指数退避 |
| API Key 缺失 | 明确提示配置路径 |

### 📝 详细日志
```
[INFO] 正在生成图像：简约现代商务风格...
[INFO] 生成成功，共 1 张图片
[INFO] 正在下载图片：https://...
[INFO] 正在上传到文件服务器：seedream_1711604400_0.png...
[INFO] 上传成功：https://mjyp1.gzlex.com/...
```

---

## 故障排查

### 常见问题

**1. ARK_API_KEY not found**
```bash
# 检查 ~/.openclaw/.env 文件
echo $ARK_API_KEY

# 添加配置
echo "ARK_API_KEY=d155ace0-ee4d-42b1-936e-4a16d2623c89" >> ~/.openclaw/.env
```

**2. 上传失败但生成成功**
- 检查 FILE_SERVER_URL 和 FILE_SERVER_TOKEN 配置
- 上传失败会自动回退到原始 API URL（24 小时有效）

**3. 反复超时**
```bash
# 增加超时时间
python seedream_api.py generate-upload "提示词" --timeout 180
```

**4. 模型返回错误**
- 检查提示词是否违规
- 尝试切换模型版本：`--model doubao-seedream-4.0`
