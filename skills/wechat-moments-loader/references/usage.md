# 微信朋友圈数据采集器 - 详细文档

## 安装

```bash
cd ~/.openclaw/skills/wechat-moments-loader
python scripts/setup.py
```

setup.py自动：检测已安装依赖 → 优先离线安装 → fallback在线安装

### 依赖列表
- opencv-python, pyautogui, pywin32, pillow, numpy, rapidocr_onnxruntime
- requests（WeFlow API调用）
- beautifulsoup4（HTML解析）

## 完整流程

```
1. 解析时间参数（--start/--end）
2. 打开微信朋友圈（OpenCV模板匹配）
3. 滚动加载到目标时间（OCR判断）
4. 检查/启动WeFlow服务
5. POST /api/v1/sns/export 导出HTML
6. 下载HTML中的图片/视频到本地
7. 替换HTML中的URL为本地路径
8. 按命名规则保存，更新status.json
```

## status.json格式

```json
{
  "last_fetch": "2026-04-10T08:00:00",
  "history": [
    {
      "date": "2026-04-10",
      "seq": 1,
      "file": "data/moments_2026-04-10_001.html",
      "media_dir": "data/moments_2026-04-10_001",
      "start_time": "2026-04-09 00:00",
      "end_time": "2026-04-10 00:00",
      "fetch_time": "2026-04-10T08:00:00"
    }
  ]
}
```

## WeFlow API

- Base URL: `http://127.0.0.1:5032`
- 健康检查: `GET /health`
- 导出朋友圈: `POST /api/v1/sns/export`
- 媒体代理: `GET /api/v1/sns/media/proxy?url=xxx`

## Cron调用示例

```bash
# 每天早上9点，更新昨天的数据
# 大模型翻译"更新到昨天" → --start 20260409 --end 20260410
0 9 * * * cd ~/.openclaw/skills/wechat-moments-loader && python scripts/loader.py --start {yesterday} --end {today}

# 每6小时一次
0 */6 * * * cd ~/.openclaw/skills/wechat-moments-loader && python scripts/loader.py --start 6h
```

## 故障排除

**朋友圈图标识别错误** - 调整threshold（0.3-0.7）
**WeFlow服务不可用** - 检查D:/WeFlow目录，手动启动
**导出失败** - 确认朋友圈已滚动加载过
**媒体下载不完整** - 检查网络，可重新运行
