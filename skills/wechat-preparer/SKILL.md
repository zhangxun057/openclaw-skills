---
name: wechat-preparer
description: |
  微信数据预处理引擎。统一处理朋友圈、私聊、群聊的 L0→L1→L2 流水线。
  由当前 Agent 模型完成结构化抽取，脚本只做数据准备和落库，不调用外部 API。
  触发词：微信数据处理、微信预处理、提取朋友圈、分析今天的朋友圈、处理微信聊天记录、跑一下微信数据、openclaw 数据处理、朋友圈数据准备、私聊提取、群聊提取、chat分析、moments prepare。
version: 4.7.0
---

# 微信数据预处理引擎

统一处理朋友圈、私聊、群聊三种数据源。脚本负责数据准备和落库，Agent 模型负责内容抽取。

**执行模式：** 默认按 朋友圈 → 私聊 → 群聊 串行处理。用户指定单一数据源时，只处理该数据源。

---

## 数据源

| 数据源 | L0 路径 | 文件格式 | 抽取方式 |
|--------|---------|---------|---------|
| 朋友圈 | `raw/moments-analysis/YYYYMMDD.json` | `{date, posts[]}` | 去重 → Agent 模型抽取 4 维度 |
| 私聊 | `raw/chat-analysis/chat_YYYYMMDDHH.jsonl` | `{sessionId, sessionName, messages[]}` | prepare_chat 切分去重 → Agent 模型抽取 |
| 群聊 | `raw/group-chat-analysis/group_chat_YYYYMMDDHH.jsonl` | `{sessionId, sessionName, messages[]}` | prepare_group_chat 过滤切段 → Agent 模型抽取 |

朋友圈由 `scripts/prepare_data.py` 做新帖准备；私聊由 `scripts/prepare_chat.py` 做新会话段准备；群聊由 `scripts/prepare_group_chat.py` 做过滤、切段和去重准备。

---

## 目录结构

**数据根目录：** `~/.openclaw/projects`

```
~/.openclaw/projects/
├── raw/
│   ├── moments-analysis/              ← L0 朋友圈原始
│   │   └── YYYYMMDD.json
│   ├── chat-analysis/                 ← L0 私聊原始
│   │   └── chat_YYYYMMDDHH.jsonl
│   ├── group-chat-analysis/           ← L0 群聊原始
│   │   └── group_chat_YYYYMMDDHH.jsonl
│   ├── extracted_moment/              ← L1 朋友圈提取
│   │   ├── moment_extracted_YYYYMMDDHH.jsonl
│   │   ├── moment_media_extracted_YYYYMMDDHH.jsonl     ← L1.5 图片详抽
│   │   └── checkpoint.json
│   ├── extracted_chat/                ← L1 私聊提取
│   │   ├── chat_extracted_YYYYMMDDHH.jsonl
│   │   └── checkpoint.json
│   ├── extracted_group_chat/          ← L1 群聊提取
│   │   ├── group_chat_extracted_YYYYMMDDHH.jsonl
│   │   └── checkpoint.json
│   ├── contact/                       ← L0 通讯录快照
│   │   └── contacts_YYYYMMDDHH.jsonl
│   └── group-contact/                 ← L0 群通讯录/群成员快照（如存在）
│       └── group_contacts_YYYYMMDDHH.jsonl
├── customers/                         ← L2 客户数据
│   ├── whitelist.json
│   ├── customer-index.md
│   └── {wxid}/
│       └── wechat-analysis/
│           ├── {wxid}_moment_extracted.jsonl
│           └── {wxid}_chat_extracted.jsonl
└── reports/
```


---

## 朋友圈处理

### Moment Phase 1: 数据准备

```bash
python scripts/prepare_data.py
```

扫描 `raw/moments-analysis/` 所有 JSON，比对 `raw/extracted_moment/checkpoint.json` 的 `analyzed_ids`，新帖子通过 stdout 输出。

常见输出（stderr）：

- `OK: N new / M total` → 继续 Phase 2
- `NO_DATA` → 需要先拉取 raw 数据
- `NO_RAW_DIR` → 目录不存在

### Moment Phase 2: Agent 模型抽取

Agent 读取 prepare_data 的 stdout 输出，直接分析 `posts` 数组。

输出 JSON 数组，长度与 `posts` 一致，顺序一一对应。与 posts 合并后通过 stdin 传给 apply_analysis.py。

#### 朋友圈抽取提示词

你是朋友圈商业线索分析助手。请逐条分析输入的朋友圈帖子，输出严格 JSON 数组。

**业务背景：** 我方业务包括定制酒服务、会议/宴请/礼品用酒、贵州文旅产品、创始合伙人/创业投资机会。目标是从朋友圈中识别内容类型、发帖人画像变化、可记录事件和销售线索。

**输出要求：**
- 必须返回 JSON 数组，数组长度必须与输入帖子数量一致
- 每个元素必须是对象，不要输出 null，不要解释，不要 Markdown
- 不确定就留空，禁止编造
- 字段值必须精简，避免完整长句复述原文
- 只基于发帖人正文、位置、评论、互动和媒体数量判断；不要把转发内容中的第三方行为当成发帖人行为

**朋友圈特定关切：**
- events 是**单条朋友圈级别**，每条帖子独立提取
- events 主语为发帖人，用"他"/"她"/"TA"（不用"我"）
- 粒度最细：每条有实质内容的帖子都应产生至少 1 条 event
- traits 是对发帖人本人的画像特征
- signals 允许值严格限定为 6 种

**输出字段：**
```json
{
  "post_type": "转发内容|输出观点|分享动态|广告营销|其他",
  "mood": "开心|失落|焦虑|兴奋|平静|无法判断",
  "traits": {},
  "events": [],
  "signals": []
}
```

朋友圈 `rels` 不由模型输出；落库脚本从点赞、评论中提取互动人和互动动作。

### post_type 内容分类

- `转发内容`：转文章、海报、链接、新闻、小程序、视频号等内容，无自己评论
- `输出观点`：发表看法、评论、行业观点、思考，有自身判断
- `分享动态`：发帖人自己的生活、工作、活动、行程，有个人行动
- `广告营销`：产品推广、招商宣传、促销信息
- `其他`：纯表情、纯图片无文字、无法判断

**判断原则：** 内容无法归类填其他。有自身判断输出观点优先，有个人行动分享动态优先，纯招商推广告营销。

### mood 情绪状态

从发帖文字内容和表情中判断发帖人情绪。

**允许值：** 开心、失落、焦虑、兴奋、平静、无法判断

**判断原则：**
- `开心`：庆祝、纪念日、喜悦、成就、正面情绪词
- `失落`：遗憾、失败、告别、负面情绪词
- `焦虑`：担忧、压力、紧张、不确定性表达
- `兴奋`：激动、期待、热情、感叹号密集
- `平静`：中性叙述、日常分享、无明显情绪
- `无法判断`：纯转发无自己评论、空内容、纯图片无文字、纯表情不明确

### traits 画像特征（统一标准）

traits 记录当事人相对稳定的画像，不记录这条内容里出现过什么对象。
只记录有明确证据支撑的特征；证据只能支持动作时，不要上升为画像。

**判断方法：**
- 先问：这条内容能证明当事人本人是什么样，或长期在做什么吗？
- 单次内容也可以写 traits，但证据必须直接指向当事人本人。
- 拿不准时填 `{}`。

**Key 仅允许使用以下 18 个，禁止自创：**
所在城市、婚姻状况、学历、毕业院校、在职单位、职务、行业、家庭结构、社交圈层、人脉资源、性格特征、表达风格、兴趣爱好、价值观倾向、资产档次、投资风格、饮酒偏好、香型偏好

**Value 规范：**
- 有依据的具体描述。
- 每条少于 10 个汉字。
- 禁止"未知""待确认""推测"等占位符。
- 正文少于 30 字或无有效信息时，traits 填 {}。
- 纯转发且无法推断发帖人特征时，traits 填 {}。

**示例：**

正确：
- 朋友圈：A 发帖说"我长期做海外渠道，今年主要看东南亚。"
  输出：`{"关注点": "东南亚渠道"}`
- 私聊：A 说"这个客户一直由我对接，后续我来跟。"
  输出：`{"职责": "客户对接"}`
- 群聊：A 多次用数据拆解行业问题，并给出自己的判断。
  输出：`{"A": "表达风格：数据分析"}`

错误：
- 朋友圈：A 转发"德国前总统出席企业家私享会"。
  错误：`{"人脉资源": "德国前总统"}`
  原因：德国前总统是内容对象，不是 A 本人的属性。
- 私聊：A 说"我把匀东贵州饭店加进名单。"
  错误：`{"职务": "酒店拓展"}`
  原因：只能证明 A 做了这件事，不能证明 A 的稳定职务。
- 群聊：A 问"今天谁订晚餐，3 点前填表。"
  错误：`{"A": "职务：行政"}`
  原因：一次通知不能证明稳定角色。

### events 事件提取（统一标准）

记录现实世界中值得长期保存的人生、职业、业务、组织或关系变化事实。event 是抽象后的精炼事实，不是聊天摘要或工作流水账。

**重要原则：**
- events 与 signals 独立。有长期记忆价值但没有销售机会，也可以进入 events。
- event 是短句事实，不是摘要、原文摘录、聊天金句、文件名或通知原文。
- 只记录能回答"现实世界发生了什么重要变化"的内容。
- 只反映执行过程、沟通成本或临时状态的内容，通常不进入 events；除非它上升为重要业务节点、组织变化或长期关系变化。
- 没有值得长期保存的事实时输出空数组，不要为了凑数量把问题、通知、闲聊、半句原文写成 event。
- 同一事实不要拆成"具体事件 + 泛化事件"两条；例如已有"联合承办上海市场学会品牌论坛"，不要再输出"参加论坛"。
- 同一业务目的、同一活动或同一项目进展下的多个动作合并为一条；例如"接待校友到访并参加座谈会"应合并为一个座谈会事件，"需求扩容、城市增加、领取需求表"应合并为一个需求扩容事件。
- 保留对业务判断有价值的实体信息，优先包含地点、机构、品牌、项目名、活动名、客户或产品名。

**格式要求：**
- 朋友圈可省略主语，用动词开头，因为发帖人就是主体；私聊和群聊必须写清主体，如"TA"、"我"或具体人名。
- 只讲一件事，抓主要矛盾。
- 能回答"谁 + 做了什么 / 去了哪里 / 约定什么"。
- 默认每条不超过 20 个汉字；为了保留产品名、项目名、论坛名、地点等关键实体，可适度超过。
- 必须是完整短语，禁止截断原文半句话。
- 若两个候选事件指向同一行动，保留信息更完整的一条，删除泛化或重复表达。
- 若多个候选事件共享同一目的，保留"目的 + 关键实体 + 核心动作"的合并表达，不拆过程步骤。

**应该抽取的事件类型：**
- 人生变化：婚育、乔迁、升学、移居、长期定居、重要家庭变化。
- 职业变化：入职、离职、创业、晋升、转岗、负责重要业务、加入重要组织。
- 重要业务节点：关键合作、签约、融资、项目上线、产品发布、客户到访、外部资源对接。
- 重要组织动作：承办活动、举办论坛、发布重要需求、招募关键资源、启动重大计划。
- 高价值线下活动：重要会议、论坛、路演、展会、招商会、行业活动、商务拜访。

**禁止提炼为 event 的情况：**
- 社交用语，例如"晚上见""来了"。
- 状态标签，例如"高强度工作"。
- 纯信息发布，例如"发布通知""转发文章"。
- 过程性工作流水：只说明正在沟通、处理、协调、确认、催办、排查或安排，未形成长期可记忆事实。
- 文件名、链接标题、会议邀请原文、聊天引用原文。
- 问句、请示句、寒暄句本身；只有能归纳成具体行动或约定时才进入 events。
- 纯转发内容中的第三方活动。
- 广告话术或招商宣传，除非能确认是发帖人本人组织或参与。
- 低价值日常记录，例如早安问候、餐食碎片、无明确地点或动作的普通打卡；这类信息可放入 traits，不进入 events。
- 只有观点、鸡汤、财经新闻、行业评论，没有发帖人动作时，不进入 events。

**正确示例：**
- "TA将从某科技公司离职"
- "TA全家迁居外地"
- "我赴外地对接战略合作"
- "TA参加省级行业专题会"
- "抵达北京西站"
- "参加医药合规座谈会"
- "接待中国药大校友参加云溪医药合规座谈会"
- "组织客户回厂参观"
- "举办公司周年庆"
- "联合承办上海市场学会品牌论坛"
- "预告项目签约仪式"
- "预告AIROBO和泓服务签约仪式"
- "发布海外媒体需求"
- "扩容海外来华项目30城媒体需求"
- "客户别墅开工"
- "举办团建温泉活动"
- "完成白俄明斯克空运"

**错误示例：**
- "高强度工作"
- "跟进线上问题"（只记录处理过程，未形成长期可记忆事实）
- "同步项目进度"（沟通过程，不是重要变化）
- "博鳌乐城高端体检"
- "吴向东珍酒直播烤酒车间"
- "发布求职信息"
- "早安问候"
- "参加论坛"（已有具体论坛名称时过于泛化）
- "启动项目"（已有具体项目名或活动名时过于泛化）
- "接待中国药大校友到云溪指导"和"参加医药合规座谈会"同时输出（应合并）
- "扩容海外媒体需求"和"发布媒体资源需求"同时输出（应合并）
- "洵总，您看下还有什么要讨论的么"（这是问句，不是事件）
- "[文件] 某专题会议通知.pdf"（这是文件名，不是事件）
- "某人邀请你加入视频会议"（这是会议邀请原文，不是事件）

### signals 销售信号（统一标准）

signals 只记录外部需求方出现的新增可跟进机会。不是关键词触发，必须基于内容事实判断。

满足以下全部条件才可标记：

1. 有明确需求方，且不是我方内部执行者。
2. 需求方表达了采购、使用、定制、合作、资源对接、活动支持、体验服务或进一步了解意向。
3. 我方产品、服务、资源、渠道或关系能够实际介入，值得后续行动。
4. 不是既有项目的普通履约过程；除非出现新的需求方、新场景或新增需求。

供给侧内容不进入 signals。供给侧内容包括：发帖人在销售、招商、推广、代理、宣传自己的产品、品牌、课程、媒体或服务。

**允许值限定为：**
- 定制服务
- 活动支持
- 资源对接
- 产品采购
- 渠道合作
- 投资/合伙

**强信号类型：**
- 需求方明确表达采购、试用、定制、部署、体验或进一步了解意向。
- 需求方正在筹备活动、项目、渠道、客户接待或资源对接，且我方能力可介入。
- 需求方出现新业务、新项目、新场景、新合作对象或新资源缺口。
- 本人创业、融资、新项目落地、寻找合伙人，且不是泛泛资讯转发。

**禁止标记为 signals：**
- 内部业务讨论、方案讨论、产品打磨、素材准备、演示设计。
- 履约、生产、库存、结算、分润、售后、排期等执行过程。
- 既有项目推进，未出现新增需求或新需求方。
- 只出现业务关键词，但没有需求方意向。
- 我方主动构想、主动推荐、主动制作方案，但对方尚未表达需求。
- 一般商务动态，但没有采购、合作、资源或场景需求。
- 泛泛公共机会或公共通知，虽有外部需求但我方不能实际介入。
- 对方在销售、招商、推广自己的产品或服务。
- 泛投资资讯、财经新闻、行业观点转发，不等于本人有投资意向。

**正例：**
- "客户下月办行业沙龙，正在找伴手礼方案" -> signals: ["活动支持"]
- "对方希望试用我方系统并了解报价" -> signals: ["产品采购"]
- "朋友在外地有渠道资源，想了解合作方式" -> signals: ["渠道合作"]

**反例：**
- 内部讨论产品页面、演示素材或方案包装，不是外部需求。
- 既有订单的生产、发货、结算、售后推进，不是新增机会。
- 只有业务关键词，没有需求方意向，不进入 signals。
- 对方招商、卖自己的产品，不作为我方销售对象。
- 财经新闻转发不等于本人有投资意向。

### Moment Phase 3: 落库

流程：`prepare_data.py` 输出新帖子 → Agent 按顺序抽取 JSON 数组 → 将帖子与抽取结果合并后传给 `apply_analysis.py` 落库。

写入：
- `raw/extracted_moment/moment_extracted_YYYYMMDDHH.jsonl`（L1）
- `customers/{wxid}/wechat-analysis/{wxid}_moment_extracted.jsonl`（L2）
- `raw/extracted_moment/checkpoint.json`

脚本只做字段校验、去重写入、`post_time` 格式化、`rels` 提取、`image_trigger` 计算，不调用模型。

### Moment Phase 4: 图片抽取（image_trigger 钩子）

当帖子 `image_trigger = "strong"` 且该帖有图片媒体时触发。由 Agent 调用视觉模型完成图像识别，提示词封装在 `scripts/apply_media_analysis.py` 内。

**输入：**

```bash
python scripts/prepare_media.py
```

扫描 `raw/extracted_moment/moment_extracted_*.jsonl` 中 `image_trigger = "strong"` 的帖子，比对 `raw/extracted_moment/moment_media_extracted_*.jsonl` 已有记录和 `checkpoint_media.json`，输出待处理帖子列表。每条包含 `post_id`、`wxid`、`nickname`、`content`、`post_type` 和待分析图片路径。

**抽取：**

Agent 对每张图组装上下文（替换 `{nickname}` `{gender}` `{age_range}` `{location}` `{post_time}` `{content}` `{post_type}` `{mood}` `{signals}` 占位符），调用视觉 API 输出 6 段结构化结果：整体画面、时空、场景与动作、人物、物品与品牌、图文关系。

**落库：**

```bash
python scripts/apply_media_analysis.py --date YYYYMMDDHH [--workers N]
```

- 写入 `raw/extracted_moment/moment_media_extracted_YYYYMMDDHH.jsonl`（append，一个帖子一条记录，`images[]` 数组展开所有图）
- 更新 `raw/extracted_moment/checkpoint_media.json`
- `--workers N` 控制并发视觉 API 调用数
- 单图失败不阻断同帖其他图

**输出记录以帖子为载体**：`{post_id, wxid, nickname, post_time, content, post_type, images: [{media_index, media_file, overall, time_space, scene_action, people, objects_brands, text_image_relation}], videos: [], articles: [], extracted_at, model}`

---

## 私聊处理

### Chat Phase 1: 数据准备

```bash
python scripts/prepare_chat.py
```

扫描 `raw/chat-analysis/` 下的私聊 JSONL，按对话对象和日期切分会话段，比对 `raw/extracted_chat/checkpoint.json` 的 `analyzed_ids`，只输出未分析的新段。

常见输出（stderr）：

- `OK: N new segments from M sessions` → 继续 Phase 2
- `NO_NEW_SEGMENTS` → 无需继续私聊抽取
- `NO_RAW_DIR` → 需要先拉取 raw 私聊数据

### Chat Phase 2: Agent 模型抽取

读取 `prepare_chat.py` 的 stdout，按 segment 逐段分析。每段对应一个私聊会话片段。

输出 JSON 数组，长度与 segment 数一致，顺序一一对应。

#### 私聊抽取提示词

你是私聊商业分析助手。逐段分析私聊对话，输出严格 JSON 数组。

**业务背景：** 我方业务包括定制酒服务、会议/宴请/礼品用酒、贵州文旅产品、创始合伙人/创业投资机会。目标是从私聊对话中提取结构化信息，供后续画像和行动建议使用。

**输出要求：**
- 必须返回 JSON 数组，长度与输入段数一致，顺序一一对应
- 每个元素必须是对象，不要输出 null，不要解释，不要 Markdown
- 不确定就留空，禁止编造
- 识别 me 和 peer 双方，从对话中提取对双方的描述

**输出字段：**
```json
{
  "session_overview": {
    "time_start": "YYMMDDTHHmm",
    "time_end": "YYMMDDTHHmm",
    "rounds": 0,
    "initiator": "me|them",
    "volume": "me_dominant|them_dominant|balanced"
  },
  "events": [],
  "traits": {},
  "signals": [],
  "topics": [],
  "rels": [],
  "todos": []
}
```

### session_overview 会话概览

- `time_start` / `time_end`：YYMMDDTHHmm 格式
- `rounds`：对话往复轮次
- `initiator`：谁先开口（me / them）
- `volume`：一方总字数为另一方 2 倍以上即为 dominant，否则 balanced

### events 事件

同统一规范。**私聊特定关切：**
- events 是**对话层面**的，不是单条消息。一段对话最多 1-3 条；没有长期记忆价值时输出 []
- 区分"我"和"TA"：私聊 events 必须带主体，例如"TA推进酒店硬件调研"、"我要求TA补充报价"。
- 粒度明显粗于朋友圈：只记录值得以后回看的人生、职业、重要业务或关系变化
- 过程性沟通和临时执行安排不进入 events；只有上升为重要变化或关键节点时才记录
- 不把原话、文件名、会议邀请、问题句、quote 拼接当 event。
- 多条消息属于同一事项时合并成一条短句事实。

示例："TA将从某科技公司离职"、"TA全家迁居外地"、"我赴外地对接战略合作"、"TA公司启动新融资"

### traits 画像

同统一规范。**私聊特定关切：**
- traits 是对**TA**（对话对象）的推断
- 首次出现的新特征才有价值，已知特征不重复输出

### signals 销售信号

同统一规范。**私聊特定关切：**
- 从 TA 或对话中明确出现的外部需求方判断；我方主动推荐、内部讨论或既有执行过程不构成 signal。

### topics 话题标签

开放标签列表，按出现顺序。例如 `["基酒投资", "价格谈判", "样品安排"]`。

### rels 关系判断

私聊 rels 记录**对话对象与我的身份关系**。输出数组；不明确时填 `[]`。

每项 `{relation, confidence, evidence}`：
- `relation`：身份关系，例如 `伴侣`、`亲属`、`朋友`、`同学`、`校友`、`老乡`、`战友`、`同事`、`上级`、`下属`、`客户`、`供应商`、`合作伙伴`、`社会关系`。可使用其他明确社会关系。
- `confidence`：`high|medium|low`。
- `evidence`：一句证据，说明为什么这样判断。

判断原则：
- rels 判断"我和对方是什么关系"，不是判断"我们正在聊什么项目"。
- `业务协作`、`项目协作`、`技术对接`、`供应链协作` 不是身份关系，不进入 rels。
- `上级`、`下属` 必须有方向；不要写 `上下级`。
- 称呼如"洵总""张总"只能作为辅助证据，不能单独判断上下级；需要结合请示、汇报、任务安排、验收或请假等权力方向。
- 如果只知道一起做事，但身份不明，填 `[]` 或低置信度 `合作伙伴`。

示例：
- 对方说"洵总，您看怎么安排，我明天把方案改完发您" → `{relation:"下属", confidence:"high", evidence:"对方请示安排并承接执行任务"}`
- 对方与我讨论孩子、家、宠物、住址、亲昵称呼 → `{relation:"伴侣", confidence:"high", evidence:"共同处理家庭事务并有亲昵称呼"}`
- 对方称我"张总"并报价、谈合同或交付 → 不能仅凭称呼判断下属，应按证据判断为 `供应商`、`客户` 或 `合作伙伴`。

### todos 待办

提取对话中**未来要做的事**。

判断标准：
- 必须是明确的行动项，不是讨论过的话题、建议、或已完成的
- 可以是"我"要做的，也可以是对方要做的，只要对话中明确约定了后续行动
- deadline 有则写，没有则留空
- 模糊表述如"本周""下周""近期"可以保留

每项 `{content, deadline}`。deadline 不确定时留空字符串。

### Chat Phase 3: 落库

```bash
python scripts/apply_chat_analysis.py --date YYYYMMDDHH
```

脚本将 Agent 模型分析结果写入：

- `raw/extracted_chat/chat_extracted_YYYYMMDDHH.jsonl`（L1）
- `customers/{talker}/wechat-analysis/{talker}_chat_extracted.jsonl`（L2）
- `customers/{talker}/wechat-analysis/{talker}_relations.jsonl`（关系记录）
- `raw/extracted_chat/checkpoint.json`

---

## 群聊处理

### Group Phase 1: 数据准备

```bash
python scripts/prepare_group_chat.py
```

扫描 `raw/group-chat-analysis/group_chat_YYYYMMDDHH.jsonl`，按群读取消息，比对 `raw/extracted_group_chat/checkpoint.json` 的 `analyzed_ids`，只输出未分析的新群聊段。

准备脚本只做结构整理、去噪、切段和断点续跑，不判断 event、signal、traits 或 rels。

默认丢弃以下低价值消息：

- 纯表情/表情包
- 单字回复（"收到""好的""嗯"等）
- 系统邀请、撤回、拍一拍等系统消息

默认按每段最多 120 条有效消息切段；原始消息没有逐条时间戳时，不按静默间隔切分，避免制造假时间。

常见输出：
- `OK: N new group segments from M sessions` → 继续 Phase 2
- `NO_DATA` → 无群聊 raw 数据
- `NO_RAW_DIR` → 需要先拉取 raw 群聊数据

### Group Phase 2: Agent 模型抽取

读取 `prepare_group_chat.py` 输出的群聊段，逐段分析。每条对应一个群聊 segment。

#### 群聊抽取提示词

你是群聊商业分析助手。逐段分析群聊对话，输出严格 JSON 数组。

**关注焦点：** 以"我"和"与我相关"为锚点，识别群内的机会和动态。

**输出字段：**
```json
{
  "session_overview": {
    "time_start": "YYMMDDTHHmm",
    "time_end": "YYMMDDTHHmm",
    "rounds": 0
  },
  "topics": [],
  "events": [],
  "traits": {},
  "signals": [],
  "rels": []
}
```

### session_overview

`time_start` / `time_end`：YYMMDDTHHmm 格式。
`rounds`：对话往复轮次。

### topics 话题标签

从对话内容提取话题标签（如"测试环境"、"代码块优化"、"支付功能"）。

### events 群动态

同统一规范。**群聊特定关切：**
- 群聊 events 是**段级摘要**，不是逐条消息。一段对话最多 1-3 条关键 events；没有关键事件时输出 []
- 主语必须是具体发言人昵称，禁用"有人""某群友"等模糊指代
- 优先记录：群聊证明的现实变化，例如重要业务节点、组织关系变化、项目正式上线、合作渠道建立
- 过程性沟通、临时执行安排和群内内部讨论，通常不进入 events
- 日常闲聊、纯表情回复、无意义刷屏不进入 events
- 粒度最粗：同一话题多人讨论合并为一条，标注关键发言人

示例："张三公司正在筹备B轮融资"、"李四推荐区域客户资源给王五"、"赵六推进文旅平台与地图厂商合作"

### traits 画像

同统一规范。**群聊特定关切：**
- 群聊中发言者多、转发多，尤其要区分"发言者本人属性"和"消息内容对象属性"。
- 格式：`{发言人："维度：值"}`。
- 没有足够证据时填 `{}`。

### signals 群聊信号

同统一规范。**群聊特定关切：**
- 只有发言人本人或其明确提到的外部需求方出现新增可跟进机会，才标记为 signal
- 转发文章、分享资讯不构成 signal
- 身份变化、新项目线索、行业动态本身不等于 signal；必须出现需求方意向，且我方能够实际介入

### rels 群聊关系边

群聊 rels 记录群内人物之间明确发生的关系动作。输出数组；没有明确对象时填 `[]`。

每项 `{from, relation, to, status}`：
- `from`：动作发起者或原文主语。
- `relation`：关系动作，例如 `请求处理`、`回应问题`、`推荐资源`、`共同推进`。
- `to`：动作对象。
- `status`：关系状态；无明确证据时留空。

只记录点对点关系；一人对全群广播、普通资讯转发、没有明确对象的发散讨论不进入 rels。

### Group Phase 3: 落库

```bash
python scripts/apply_group_chat_analysis.py --date YYYYMMDDHH
```

写入：
- `raw/extracted_group_chat/group_chat_extracted_YYYYMMDDHH.jsonl`（L1）
- `raw/extracted_group_chat/checkpoint.json`

---

## 压缩比对比

| 数据源 | 压缩比 | 关注焦点 | 信号密度 |
|--------|--------|---------|---------|
| 朋友圈 | 约 3:1 | 发帖人动态 | 中 |
| 私聊 | 约 5:1 | 对话双方 | 高 |
| 群聊 | 约 20:1 | 我 + 关键人物 | 低 |

---

## 脚本

| 脚本 | 功能 |
|------|------|
| `scripts/prepare_data.py` | 朋友圈数据准备（去重 + 媒体索引） |
| `scripts/apply_analysis.py` | 朋友圈分析结果落库 |
| `scripts/match_media.py` | 朋友圈媒体文件匹配 |
| `scripts/generate_report.py` | 朋友圈日报生成 |
| `scripts/prepare_chat.py` | 私聊数据准备（扫描 raw 私聊、切分会话段、按 checkpoint 去重） |
| `scripts/apply_chat_analysis.py` | 私聊分析结果落库到 L1、L2 和 checkpoint |
| `scripts/prepare_group_chat.py` | 群聊数据准备（过滤低价值消息、切分群聊段、按 checkpoint 去重） |
| `scripts/apply_group_chat_analysis.py` | 群聊分析结果落库到 L1 和 checkpoint |
| `scripts/segment_sessions.py` | 历史辅助脚本，仅适用于含逐条 `create_time` 的原始消息 JSONL；正式私聊流程使用 `prepare_chat.py` |
| `scripts/archive_relations.py` | 将 L1 rels 平移为 customer 关系边 |
| `scripts/prepare_media.py` | 朋友圈图片抽取准备：扫描 strong image_trigger 帖子，去重，匹配本地媒体文件 |
| `scripts/apply_media_analysis.py` | 图片分析结果落库到 moment_media_extracted，支持 --workers N 并发 |

所有脚本不调用模型，模型抽取由当前 Agent 在各数据源的抽取 Phase 中完成。

`scripts/generate_report.py` 内置 signal 到行动建议的默认映射，用于生成日报建议；业务方向变化时应同步调整该脚本或迁移为外部配置。

---

## 执行原则

1. 三种数据源可独立运行，互不依赖。
2. 每种数据源各有自己的 checkpoint，断点续跑。
3. Agent 模型抽取在一条消息内完成，不走外部 API。
4. 落库脚本只做格式化和去重，不做语义判断。
