#!/bin/bash
# 启动客户拜访访谈

STATE_FILE="$HOME/.openclaw/workspace/skills/interview-tracker/state.json"

# 获取当前时间戳（毫秒）
CURRENT_TIME=$(date +%s)000

# 激活访谈状态
cat > "$STATE_FILE" << EOF
{
  "active": true,
  "round": 0,
  "start_time": $CURRENT_TIME,
  "data": {
    "拜访者": "张洵",
    "客户名称": "",
    "客户类型": "",
    "与客户关系": "",
    "拜访日期": $CURRENT_TIME,
    "联系人姓名": "",
    "联系人职务": "",
    "联系方式": "",
    "拜访目的": [],
    "沟通内容摘要": "",
    "客户需求": "",
    "客户背景信息": "",
    "意向程度": "",
    "下次跟进时间": null,
    "备注": ""
  }
}
EOF

echo "✅ 访谈已启动"
