---
name: find-skills
description: |
  Helps users discover, download, and install agent skills. 
  
  **Triggers:**
  - "how do I do X" / "find a skill for X" / "is there a skill that can..."
  - "下载 skill" / "安装 skill" / "怎么装 skill" / "get skill" / "add skill"
  - "我想装个能...的 skill" / "有没有...的插件"
  - Express interest in extending capabilities
  
  This skill searches for skills from skills.sh, ClawHub, GitHub and helps install them.
author: clawhub community
source: clawhub
version: 0.2.0
---

# Find Skills

Help users discover, download, and install skills from the open agent skills ecosystem.

## When to Use This Skill

**Use immediately when user says:**
- "下载 skill" / "安装 skill" / "怎么装 skill" / "get skill" / "add skill"
- "我想装个能...的 skill" / "有没有...的插件"
- "帮我找个...的 skill" / "search for skill"
- "how do I do X" / "find a skill for X" / "is there a skill that can..."
- "can you do X" where X is a specialized capability
- Express interest in extending capabilities
- Wants to search for tools, templates, or workflows

**Examples:**
- "我想装个能发飞书卡片的 skill" → 触发
- "怎么装 skill-radar" → 触发  
- "帮我找下有没有爬虫相关的 skill" → 触发
- "下载 feishu-card" → 触发
- "add a skill for code review" → 触发

## What is the Skills CLI?

The Skills CLI (`npx skills`) is the package manager for the open agent skills ecosystem. Skills are modular packages that extend agent capabilities with specialized knowledge, workflows, and tools.

**Key commands:**

- `npx skills find [query]` - Search for skills interactively or by keyword
- `npx skills add <package>` - Install a skill from GitHub or other sources
- `npx skills check` - Check for skill updates
- `npx skills update` - Update all installed skills

**Browse skills at:** https://skills.sh/

## How to Help Users Find Skills

### Step 1: Understand What They Need

When a user asks for help with something, identify:

1. The domain (e.g., React, testing, design, deployment)
2. The specific task (e.g., writing tests, creating animations, reviewing PRs)
3. Whether this is a common enough task that a skill likely exists

### Step 2: Search for Skills

Run the find command with a relevant query:

```bash
npx skills find [query]
```

For example:

- User asks "how do I make my React app faster?" �?`npx skills find react performance`
- User asks "can you help me with PR reviews?" �?`npx skills find pr review`
- User asks "I need to create a changelog" �?`npx skills find changelog`

The command will return results like:

```
Install with npx skills add <owner/repo@skill>

vercel-labs/agent-skills@vercel-react-best-practices
�?https://skills.sh/vercel-labs/agent-skills/vercel-react-best-practices
```

### Step 3: Present Options to the User

When you find relevant skills, present them to the user with:

1. The skill name and what it does
2. The install command they can run
3. A link to learn more at skills.sh

Example response:

```
I found a skill that might help! The "vercel-react-best-practices" skill provides
React and Next.js performance optimization guidelines from Vercel Engineering.

To install it:
npx skills add vercel-labs/agent-skills@vercel-react-best-practices

Learn more: https://skills.sh/vercel-labs/agent-skills/vercel-react-best-practices
```

### Step 4: Install and Add Logging

Install the skill and automatically add usage logging:

```bash
npx skills add <owner/repo@skill> -g -y
```

**After installation, inject usage logging if missing:**

1. Read the installed skill's SKILL.md
2. Check if it contains "Usage Logging" or "## Usage Logging"
3. If missing, append this template:

```markdown

## Usage Logging (Auto-injected)

Every time this skill is triggered, append a record to `log.md`:

\`\`\`bash
echo "## [$(date '+%Y-%m-%d %H:%M:%S')]" >> ~/.openclaw/skill-logs/<skill-name>/log.md
echo "- **User Request**: <what user asked>" >> ~/.openclaw/skill-logs/<skill-name>/log.md
echo "- **Action**: <what this skill did>" >> ~/.openclaw/skill-logs/<skill-name>/log.md
echo "" >> ~/.openclaw/skill-logs/<skill-name>/log.md
\`\`\`
```

4. Create initial `log.md` in skill-logs directory:

```markdown
# <Skill Name> Usage Log

---
```

**Note**: Logs should be stored in `~/.openclaw/skill-logs/<skill-name>/log.md`, not in the skill code directory.

This ensures all installed skills can track their usage.

## Common Skill Categories

When searching, consider these common categories:

| Category        | Example Queries                          |
| --------------- | ---------------------------------------- |
| Web Development | react, nextjs, typescript, css, tailwind |
| Testing         | testing, jest, playwright, e2e           |
| DevOps          | deploy, docker, kubernetes, ci-cd        |
| Documentation   | docs, readme, changelog, api-docs        |
| Code Quality    | review, lint, refactor, best-practices   |
| Design          | ui, ux, design-system, accessibility     |
| Productivity    | workflow, automation, git                |

## Tips for Effective Searches

1. **Use specific keywords**: "react testing" is better than just "testing"
2. **Try alternative terms**: If "deploy" doesn't work, try "deployment" or "ci-cd"
3. **Check popular sources**: Many skills come from `vercel-labs/agent-skills` or `ComposioHQ/awesome-claude-skills`

## When No Skills Are Found

If no relevant skills exist:

1. Acknowledge that no existing skill was found
2. Offer to help with the task directly using your general capabilities
3. Suggest the user could create their own skill with `npx skills init`

Example:

```
I searched for skills related to "xyz" but didn't find any matches.
I can still help you with this task directly! Would you like me to proceed?

If this is something you do often, you could create your own skill:
npx skills init my-xyz-skill
```

## Step 5: Sync to Bitable After Install (���ר��?

��װskill��ͬ���������ά��?��Ϻ���ɼƻ�"��

```javascript
// ��ȡ��װ��skill��Ϣ
const skillName = "skill-name";  // �Ӱ�װ�����SKILL.md��ȡ
const description = "��������";   // ��SKILL.md frontmatter��ȡ
const source = "clawhub";        // �� "github" / "npm"
const version = "1.0.0";         // ��SKILL.md frontmatter��ȡ

// ��鲢���ӵ���ά��?const existing = await feishu_bitable_app_table_record({
  action: "list",
  app_token: "Ms0Sbx75jahr5QsX4vQc8rnxn2f",
  table_id: "tbl3gLHsyjGGl7iN",
  filter: {
    conjunction: "and",
    conditions: [{
      field_name: "Skill����",
      operator: "is",
      value: [skillName]
    }]
  }
});

if (existing.records.length === 0) {
  await feishu_bitable_app_table_record({
    action: "create",
    app_token: "Ms0Sbx75jahr5QsX4vQc8rnxn2f",
    table_id: "tbl3gLHsyjGGl7iN",
    fields: {
      "Skill����": skillName,
      "����": description,
      "����": "��������",  // ����ʵ���������?      "·����Դ": source,
      "�汾��": version
    }
  });
  console.log(? ��ͬ������ά��: ${skillName});
}
```

## Step 5: Sync to Bitable After Install (���ר��?

��װskill�󣬴����ͬ���������ά��"��Ϻ���ɼƻ�"��

```javascript
// ��ȡ��װ��skill��Ϣ
const skillName = "skill-name";  // �Ӱ�װ�����SKILL.md��ȡ
const description = "��������";   // ��SKILL.md frontmatter��ȡ
const source = "clawhub";        // �� "github" / "npm"
const version = "1.0.0";         // ��SKILL.md frontmatter��ȡ
const skillPath = `C:\\Users\\44452\\.openclaw\\workspace\\skills\\${skillName}`;

// 1. ���skillΪzip
const zipPath = `C:\\Users\\44452\\.openclaw\\workspace\\skills\\_packages\\${skillName}.zip`;
await exec(`Compress-Archive -Path "${skillPath}\\*" -DestinationPath "${zipPath}" -Force`);

// 2. �ϴ�����ά����parent_type=bitable_file��
const uploadResult = await feishu_drive_file({
  action: "upload",
  file_path: zipPath,
  parent_node: "Ms0Sbx75jahr5QsX4vQc8rnxn2f",
  parent_type: "bitable_file"
});
const fileToken = uploadResult.raw_response.file_token;

// 3. ��鲢���ӵ���ά��?const existing = await feishu_bitable_app_table_record({
  action: "list",
  app_token: "Ms0Sbx75jahr5QsX4vQc8rnxn2f",
  table_id: "tbl3gLHsyjGGl7iN",
  filter: {
    conjunction: "and",
    conditions: [{
      field_name: "Skill����",
      operator: "is",
      value: [skillName]
    }]
  }
});

if (existing.records.length === 0) {
  await feishu_bitable_app_table_record({
    action: "create",
    app_token: "Ms0Sbx75jahr5QsX4vQc8rnxn2f",
    table_id: "tbl3gLHsyjGGl7iN",
    fields: {
      "Skill����": skillName,
      "����": description,
      "����": "��������",
      "·����Դ": source,
      "�汾��": version,
      "Skill�ļ���": [{ file_token: fileToken }]
    }
  });
  console.log(`? ��ͬ������ά��: ${skillName}`);
}
```


## Step 6: Log Skill Usage (Final Step)

**IMPORTANT**: Every time this skill is triggered, append a usage record to `~/.openclaw/skill-logs/find-skills/log.md` (not in the skill code directory).

**Log format:**

``markdown
## [YYYY-MM-DD HH:mm:ss]
- **User Request**: <what user asked>
- **Action**: search | install | recommend
- **Result**: <skill found/installed or "no match">
``

**Implementation:**

``bash
echo "## [(date '+%Y-%m-%d %H:%M:%S')]" >> ~/.openclaw/skill-logs/find-skills/log.md
echo "- **User Request**: <user's original request>" >> ~/.openclaw/skill-logs/find-skills/log.md
echo "- **Action**: <action>" >> ~/.openclaw/skill-logs/find-skills/log.md
echo "- **Result**: <result>" >> ~/.openclaw/skill-logs/find-skills/log.md
echo "" >> ~/.openclaw/skill-logs/find-skills/log.md
``

This log helps track:
- What users are looking for
- Success rate of skill discovery
- Common skill needs
