# Self-Improving Agent

[![Pattern A](https://img.shields.io/badge/Pattern-A-success)](PATTERN_A.md)

Capture learnings, errors, and corrections to enable continuous improvement.

## Quick Start

```bash
# Create learning files
mkdir -p ~/.openclaw/workspace/.learnings

# Log a correction
## [LRN-20260305-001] correction
**Logged**: 2026-03-05T10:00:00Z
**Priority**: high
**Status**: pending
**Area**: backend

### Summary
Use pnpm instead of npm for this project

### Details
Attempted `npm install` but failed. Lock file is `pnpm-lock.yaml`.

### Suggested Action
Update all docs to reference pnpm

### Metadata
- Source: user_feedback
- Related Files: package.json
```

## Structure

```
self-improving-agent/
├── assets/
│   ├── SKILL-TEMPLATE.md      # Template for skill extraction
│   └── runbook-template.md    # Runbook template
├── hooks/
│   └── openclaw/              # Hook scripts for OpenClaw
├── references/
│   ├── hooks-setup.md         # Hook configuration guide
│   └── openclaw-integration.md # OpenClaw integration details
├── scripts/
│   ├── activator.sh           # Learning reminder hook
│   ├── error-detector.sh      # Error detection hook
│   └── extract-skill.sh       # Skill extraction helper
├── SKILL.md                   # ClawHub documentation
└── README.md                  # This file
```

## When to Log

| Situation | Log To |
|-----------|--------|
| Command/operation fails | `.learnings/ERRORS.md` |
| User corrects you | `.learnings/LEARNINGS.md` (category: `correction`) |
| User wants missing feature | `.learnings/FEATURE_REQUESTS.md` |
| API/external tool fails | `.learnings/ERRORS.md` |
| Knowledge was outdated | `.learnings/LEARNINGS.md` (category: `knowledge_gap`) |
| Found better approach | `.learnings/LEARNINGS.md` (category: `best_practice`) |

## Log Files

### LEARNINGS.md
Corrections, knowledge gaps, best practices.

### ERRORS.md
Command failures, exceptions, integration errors.

### FEATURE_REQUESTS.md
User-requested capabilities.

## ID Format

`TYPE-YYYYMMDD-XXX`
- TYPE: `LRN`, `ERR`, `FEAT`
- Date: Current date
- Sequence: 3-digit number

Examples: `LRN-20260305-001`, `ERR-20260305-002`

## Entry Format

```markdown
## [LRN-20260305-001] category

**Logged**: 2026-03-05T10:00:00Z
**Priority**: low | medium | high | critical
**Status**: pending | in_progress | resolved | wont_fix | promoted
**Area**: frontend | backend | infra | tests | docs | config

### Summary
One-line description

### Details
Full context

### Suggested Action
Specific fix

### Metadata
- Source: conversation | error | user_feedback
- Related Files: path/to/file
- Tags: tag1, tag2
- See Also: LRN-20260305-002
- Pattern-Key: simplify.dead_code
- Recurrence-Count: 1

---
```

## Promotion Targets

When learnings prove broadly applicable:

| Target | What Belongs There |
|--------|-------------------|
| `CLAUDE.md` | Project facts, conventions |
| `AGENTS.md` | Agent workflows, automation |
| `.github/copilot-instructions.md` | Copilot context |
| `SOUL.md` | Behavioral guidelines |
| `TOOLS.md` | Tool capabilities, gotchas |

## Hook Integration

Enable automatic reminders:

```bash
# Copy hooks
cp -r hooks/openclaw ~/.openclaw/hooks/self-improvement

# Enable
openclaw hooks enable self-improvement
```

## Skill Extraction

When a learning qualifies as reusable skill:

```bash
./scripts/extract-skill.sh skill-name --dry-run
./scripts/extract-skill.sh skill-name
```

**Criteria:**
- Recurring (2+ similar issues)
- Verified (working fix)
- Non-obvious (required debugging)
- Broadly applicable
- User-flagged

## Periodic Review

Review `.learnings/` at natural breakpoints:
- Before starting major tasks
- After completing features
- When working in areas with past learnings
- Weekly during active development

### Quick Status Check

```bash
# Count pending items
grep -h "Status**: pending" .learnings/*.md | wc -l

# List high-priority pending
grep -B5 "Priority**: high" .learnings/*.md | grep "^## \["

# Find learnings for area
grep -l "Area**: backend" .learnings/*.md
```

## Related Skills

- `agentic-coding` - Contract-first coding with learning capture
- `quality-gate-loop` - Quality enforcement and error tracking
- `elite-longterm-memory` - Long-term memory integration
