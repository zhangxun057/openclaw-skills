# Permission Rules - 权限控制规则

## AI 自动权限（无需等待用户批复）

### 1. 任务日志更新
- ✅ 追加日志内容
- ✅ 更新"日志最后更新日期"字段
- ❌ 不能删除或覆盖已有日志

### 2. 状态自动变更

**允许的状态转换**：
- ✅ 未启动 → 进行中
- ✅ 进行中 → 待验收(AI提交)

**禁止的状态转换**：
- ❌ 待验收(AI提交) → 已完成（需要用户批复）
- ❌ 任何状态 → 已放弃
- ❌ 任何状态 → 取消
- ❌ 已完成 → 任何状态

## 需要用户批复的操作

### 1. 验收通过
- 状态：待验收(AI提交) → 已完成
- 触发：用户回复"任务X验收通过"

### 2. 验收不通过
- 状态：待验收(AI提交) → 进行中
- 触发：用户回复"任务X还差xxx"
- 同时追加日志记录用户反馈

### 3. 任务取消/放弃
- 状态：任何状态 → 已放弃/取消
- 触发：用户明确指示

## 实现逻辑

```javascript
function canAutoUpdate(currentStatus, newStatus) {
  const allowedTransitions = [
    ["未启动", "进行中"],
    ["进行中", "待验收(AI提交)"]
  ]
  
  return allowedTransitions.some(([from, to]) => 
    from === currentStatus && to === newStatus
  )
}

// 使用示例
if (canAutoUpdate(task.status, "进行中")) {
  // 直接更新
  await updateTask(task, "进行中")
} else {
  // 需要用户批复
  await requestApproval(task, "已完成")
}
```

## 批复格式

### 验收通过
```
任务2验收通过
diary-assistant 验收通过
微信自动回复验收通过
```

### 验收不通过
```
任务3还差文档
diary-assistant 还差测试
微信自动回复还需要优化错误处理
```

---

_Created: 2026-03-18_
