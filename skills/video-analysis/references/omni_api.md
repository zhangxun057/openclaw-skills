# MiMo V2 Omni API Reference

## Endpoint

```
POST https://token-plan-cn.xiaomimimo.com/v1/chat/completions
```

## Headers

```
Content-Type: application/json
api-key: YOUR_API_KEY
Authorization: Bearer YOUR_API_KEY
```

## Request Body

```json
{
  "model": "mimo-v2-omni",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "video_url",
          "video_url": {"url": "https://example.com/video.mp4"},
          "fps": 1,
          "media_resolution": "default"
        },
        {
          "type": "text",
          "text": "你的分析提示词"
        }
      ]
    }
  ],
  "max_completion_tokens": 4096
}
```

## Parameters

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| model | string | 是 | 固定值: `mimo-v2-omni` |
| messages[].content[].type | string | 是 | `video_url` 或 `text` |
| video_url.url | string | 是 | 视频直链 URL（可直接下载） |
| fps | float | 否 | 每秒采样帧数，默认系统决定。推荐: 口播0.5-1, 教程1-2, 动作2-3 |
| media_resolution | string | 否 | `default` 或 `max`。默认 `default` |
| max_completion_tokens | int | 否 | 最大输出 token，默认 4096 |

## Response

```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "分析结果文本"
      }
    }
  ],
  "usage": {
    "prompt_tokens": 15000,
    "completion_tokens": 500,
    "total_tokens": 15500,
    "prompt_tokens_details": {
      "audio_tokens": 200,
      "cached_tokens": 245,
      "video_tokens": 13000
    },
    "completion_tokens_details": {
      "reasoning_tokens": 300
    }
  }
}
```

## Token Details

| 字段 | 说明 |
|---|---|
| video_tokens | 视频帧消耗的 token（大头） |
| audio_tokens | 音频消耗的 token |
| cached_tokens | 被缓存的 token（prefix caching） |
| reasoning_tokens | 推理消耗的 token |

## 缓存机制

- 支持 prefix caching（跨请求）
- 相同的 prompt 前缀会被缓存
- 首次调用: cached_tokens ≈ 系统前缀 (~245)
- 相同 prompt: cached_tokens 包含完整 prompt
- 不同 prompt: 只缓存系统前缀部分

## 限制

- 视频 URL 必须可直接访问（无需 Referer 等特殊 header）
- media_resolution 仅支持 `default` 和 `max`
- 不支持音频/视频独立输入（必须 video_url 类型）
- 无状态：每次请求独立，不支持多轮追问

## 所需 token 粗算

| 时长 | fps=1, default | fps=2, max |
|---|---|---|
| 10秒 | ~2200 | ~4000 |
| 30秒 | ~2500 | ~8000 |
| 1分钟 | ~9000 | ~16000 |
| 5分钟 | ~45000 | ~80000 |
| 10分钟 | ~90000 | ~160000 |

**口播+PPT 类视频用 fps=1 + default 就够了。**
