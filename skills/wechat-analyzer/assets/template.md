# 客户档案：{name}

## 一、基础画像

**关系类型**：{type_label}  
**消息数量**：{message_count}条  
**客户分级**：{level}  
**分析日期**：{date}

---

## 二、社交强度分析

**消息分布**：
- 我方发送：{my_count}条（{my_ratio}）
- 对方发送：{their_count}条（{their_ratio}）
- 平均长度：我方{my_avg_length}字 / 对方{their_avg_length}字

**互动特征**：{initiative}

**互动频率**：{'高频' if message_count > 500 else '中频' if message_count > 200 else '低频'}

---

## 三、互动模式分析

**客户类型**：{type_label}

类型说明：
- **商务型**：关注项目、合作、投资，决策力强
- **技术型**：关注产品、开发、技术，理性分析
- **生活型**：关注家庭、日常，重视体验
- **社交型**：活跃、热情，重视人际关系
- **情感型**：表达丰富，重视情感连接

**性格特征**：{personality}

**情感倾向**：{emotion}

---

## 四、消费特征推断

**消费层级**：{consumption_level}

层级说明：
- **高**：有投资、房产、商务等关键词，消费力强
- **中高**：关注品质、品牌，愿意为体验付费
- **中等**：常规消费，需挖掘需求
- **价格敏感**：关注优惠、性价比，价格导向

**消费偏好推断**：
基于聊天内容关键词分析，该客户属于{type_label}，
{'决策较快，重视效率和回报' if type_label == '商务型' else 
 '理性消费，重视产品功能和性价比' if type_label == '技术型' else
 '重视体验和情感价值' if type_label in ['生活型', '情感型'] else
 '社交驱动型消费，重视分享和认同' if type_label == '社交型' else
 '暂无明显消费特征，需进一步观察'}

---

## 五、价值评估

### 直接价值
- **消费潜力**：{consumption_level}
- **转化难度**：{'低' if type_label == '商务型' else '中' if type_label in ['技术型', '生活型'] else '需培养'}

### 间接价值
- **信息价值**：{'高（掌握行业/业务信息）' if dominant_category == 'business' else 
                '中（技术视角）' if dominant_category == 'tech' else
                '中（社交资源）' if dominant_category == 'social' else '一般'}
- **影响力**：{'高（决策层特征）' if type_label == '商务型' else '中' if message_count > 200 else '待观察'}

### 网络位置
- **关系深度**：{'深（高频互动）' if message_count > 500 else '中等' if message_count > 200 else '浅'}
- **连接度**：{initiative}

---

## 六、触达策略建议

### 最佳时机
- {'工作日上午10-11点，下午15-17点（商务习惯）' if type_label == '商务型' else
   '晚上20-22点（技术交流时间）' if type_label == '技术型' else
   '周末或节假日（生活场景）' if type_label == '生活型' else
   '灵活时间（社交型适应性强）' if type_label == '社交型' else
   '观察对方活跃时段'}
- 节日前2周（礼赠需求高峰）
- 项目节点/季度交替时

### 沟通方式
- {'正式提案 > 社交闲聊，数据说话' if type_label == '商务型' else
   '技术细节 > 营销话术，功能优先' if type_label == '技术型' else
   '情感共鸣 > 产品推销，体验优先' if type_label in ['生活型', '情感型'] else
   '轻松互动 > 正式商务，共同话题切入' if type_label == '社交型' else
   '观察后调整'}
- 尊重对方沟通习惯（{'简洁高效，结论前置' if personality.startswith('极简') else '可深入讨论，分享细节' if personality.startswith('深度') else '保持平衡'}）

### 注意事项
- ❌ 避免：{'过多细节，直接给结论' if personality.startswith('极简') else '空洞承诺，要数据支撑' if type_label == '技术型' else '功利性太强，先建立信任' if message_count < 100 else '过度打扰'}
- ⚠️ 注意：{'对方时间宝贵，降低决策成本' if personality.startswith('极简') else '保持专业度，准备充分' if type_label == '商务型' else '保持适度距离，尊重边界' if emotion == '中性' else '积极互动，回应热情'}
- ✅ 建议：{'提供一站式方案，减少对方工作量' if personality.startswith('极简') else '提供技术细节和案例' if type_label == '技术型' else '创造共同体验机会' if type_label in ['生活型', '社交型'] else '先建立情感连接' if type_label == '情感型' else '根据互动反馈调整策略'}

---

## 七、行动建议

### 立即执行
- [ ] 根据客户类型准备相应资料
- [ ] {'预约正式沟通' if type_label == '商务型' else '寻找技术交流切入点' if type_label == 'tech' else '寻找共同话题/活动机会' if type_label in ['生活型', 'social'] else '发送问候，建立联系'}
- [ ] 记录客户偏好和禁忌

### 持续跟进
- [ ] 定期互动（频率：{'每周' if message_count > 500 else '每两周' if message_count > 200 else '每月'}）
- [ ] 节点触达（节日、生日、项目节点）
- [ ] 价值提供（信息分享、资源对接）

### 关键节点
- 首次深度沟通后：记录反馈，调整策略
- 建立信任后：探索合作机会
- 转化成功后：维护长期关系，挖掘转介绍

---

## 八、备注

- 客户类型：{type_label}
- 消费预估：{consumption_level}
- 优先级：{'最高' if level == '核心客户' else '高' if level == '活跃客户' else '中' if level == '普通客户' else '待激活'}
- 下次联系时间：待填写

---
*档案生成时间：{date}*
*下次更新：首次触达后*
