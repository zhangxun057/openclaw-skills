---
name: feishu-bitable-upload
description: 飞书多维表格附件上传。核心要点：上传文件到 Bitable 时必须指定 parent_type=bitable_file 参数，否则无法获取 file_token。
author: 张洵
source: 实战经验（2026-03-14）
---

# 飞书多维表格附件上传

## 核心问题

上传文件到多维表格时，如果不指定 `parent_type: "bitable_file"`，会导致：
- 上传成功但返回 `file_token: undefined`
- 无法更新附件字段

## 正确方法

### 单文件上传

```javascript
// 1. 上传文件（关键：parent_type）
const result = await feishu_drive_file({
  action: "upload",
  file_path: "本地文件路径",
  parent_node: "app_token",      // 多维表格 token
  parent_type: "bitable_file"    // 必须指定！
});

const fileToken = result.raw_response.file_token;

// 2. 更新记录
await feishu_bitable_app_table_record({
  action: "update",
  app_token: "app_token",
  table_id: "table_id",
  record_id: "record_id",
  fields: {
    "附件字段名": [{ file_token: fileToken }]
  }
});
```

### 批量上传

```javascript
// 逐个上传获取 file_token
const fileTokens = [];
for (const file of files) {
  const result = await feishu_drive_file({
    action: "upload",
    file_path: file,
    parent_node: "app_token",
    parent_type: "bitable_file"
  });
  fileTokens.push(result.raw_response.file_token);
}

// 批量更新记录（最多500条/批）
const records = fileTokens.map((token, i) => ({
  record_id: recordIds[i],
  fields: { "附件字段": [{ file_token: token }] }
}));

await feishu_bitable_app_table_record({
  action: "batch_update",
  app_token: "app_token",
  table_id: "table_id",
  records: records
});
```

## 故障排查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 返回 `file_token: undefined` | 缺少 `parent_type` 参数 | 添加 `parent_type: "bitable_file"` |
| 附件字段为空 | `file_token` 未正确传入 | 检查 `fields` 格式：`[{ file_token: "..." }]` |

## 限制

- 单文件最大 20MB（飞书 API 限制）
- 批量更新最多 500 条记录/次
- 每个附件字段最多 10 个附件

## 参考

- 飞书上传素材 API：https://open.feishu.cn/document/server-docs/docs/drive-v1/upload
- 飞书多维表格记录 API：https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/create
