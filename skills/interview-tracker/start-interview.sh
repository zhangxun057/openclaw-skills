#!/bin/bash
# 启动访谈

STATE_FILE="$HOME/.openclaw/workspace/skills/interview-tracker/state.json"

# 激活访谈状态
cat > "$STATE_FILE" << 'EOF'
{
  "active": true,
  "round": 0,
  "start_time": null,
  "data": {
    "客户名称": "",
    "客户类型": "",
    "联系人姓名": "",
    "联系方式": "",
    "拜访目的": [],
    "沟通内容摘要": "",
    "客户需求": "",
    "意向程度": "",
    "下次跟进时间": null,
    "拜访日期": null,
    "备注": ""
  }
}
EOF

echo "访谈已启动"
