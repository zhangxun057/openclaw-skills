# Learnings Log

Captured learnings, corrections, and discoveries. Review before major tasks.

---

## [LRN-20260228-001] use_gh_cli_not_curl

**Logged**: 2026-02-28T14:45:00+08:00  
**Priority**: high  
**Status**: active  
**Area**: tools

### Summary
Use `gh` CLI instead of `curl` for GitHub API calls — it's authenticated and cleaner

### Details
**Before:**
```bash
curl -s https://api.github.com/repos/... | jq ...
# Requires manual auth headers, token management
```

**After:**
```bash
gh repo view owner/repo --json field
gh pr checks url
gh run view id --log
```

**Benefits:**
- Pre-authenticated (reads from ~/.config/gh/hosts.yml)
- Cleaner syntax
- Better error messages
- Consistent output format

### Suggested Action
- Update TOOLS.md with gh CLI reference
- Replace curl-based GitHub calls with gh equivalents

### Metadata
- Source: user_feedback (Ryan: "Add gh to your tools.md")
- Related Files: `TOOLS.md`
- Tags: github, cli, authentication
- See Also: None
- Pattern-Key: tools.prefer_gh_over_curl
- Recurrence-Count: 1
- First-Seen: 2026-02-28
- Last-Seen: 2026-02-28

---

## [LRN-20260228-002] timestamp_proposal_ids

**Logged**: 2026-02-28T10:30:00+08:00  
**Priority**: high  
**Status**: active  
**Area**: workflow

### Summary
Sequential integer IDs (001, 002, 003) cause conflicts in parallel proposal development

### Details
**Problem:**
- Multiple proposals in development = ID collisions
- Subagents clobber each other's work
- Requires sync overhead

**Solution:**
Use timestamp-based IDs: `YYYYMMDD-HHMM-descriptive-name`

**Examples:**
- `20260228-0930-evaluate-clawsentinel`
- `20260228-0945-evaluate-command-center`

**Benefits:**
- Parallel development without conflicts
- Chronological sorting
- Self-documenting (date + purpose)

### Suggested Action
- Document in `proposals/CONVENTIONS.md`
- Use for all new proposals
- Existing proposals keep integer IDs

### Metadata
- Source: user_feedback (Ryan: "change proposal ids to timestamps")
- Related Files: `proposals/CONVENTIONS.md`
- Tags: proposals, workflow, parallelization
- See Also: LRN-20260228-003 (git worktrees)
- Pattern-Key: workflow.parallel_proposals
- Recurrence-Count: 1
- First-Seen: 2026-02-28
- Last-Seen: 2026-02-28

---

## [LRN-20260228-003] git_worktrees_parallel_dev

**Logged**: 2026-02-28T11:20:00+08:00  
**Priority**: high  
**Status**: active  
**Area**: workflow

### Summary
Git worktrees enable multiple branches checked out simultaneously in isolated directories

### Details
**Usage:**
```bash
# Create worktree from branch
git worktree add ../proposal-20260228-0930-clawsentinel proposal/20260228-0930-clawsentinel

# Result: isolated directory for each branch
# ~/workspace/research-site              (main)
# ~/workspace/proposal-20260228-0930-clawsentinel  (feature branch)
```

**Benefits:**
- No `git stash/checkout` dance
- Subagents get isolated directories — no clobbering
- Parallel proposal development
- Each worktree is a full checkout

**Commands:**
```bash
git worktree list                    # List worktrees
git worktree remove ../path          # Remove worktree
git worktree prune                   # Clean up stale worktrees
```

### Suggested Action
- Use for all parallel proposal development
- Create worktrees in `/tmp/` for subagent isolation
- Document in AGENTS.md for multi-agent workflows

### Metadata
- Source: user_feedback (Ryan: "teach yourself git worktrees")
- Related Files: `AGENTS.md`
- Tags: git, worktrees, parallelization, subagents
- See Also: LRN-20260228-002 (timestamp IDs)
- Pattern-Key: workflow.git_worktrees
- Recurrence-Count: 1
- First-Seen: 2026-02-28
- Last-Seen: 2026-02-28

---

## [LRN-20260228-004] backup_system_architecture

**Logged**: 2026-02-28T13:30:00+08:00  
**Priority**: medium  
**Status**: active  
**Area**: config

### Summary
Workspace root git repo is intentionally empty — backup system handles sync

### Details
**How it works:**
1. Backup script creates fresh temp clone of `archivist-workspace`
2. Copies workspace files into structured directories (identity/, memory/, etc.)
3. Commits and pushes to GitHub
4. Local repo remains uninitialized

**Don't:**
- Try to commit to workspace root directly

**Do:**
- Let backup.sh handle syncing
- Trust the backup system

### Suggested Action
- Document this architecture in AGENTS.md
- Clarify for future reference

### Metadata
- Source: knowledge_gap (discovered during status check)
- Related Files: `.backup/backup.sh`, `AGENTS.md`
- Tags: backup, architecture, git
- See Also: None
- Pattern-Key: None
- Recurrence-Count: 1
- First-Seen: 2026-02-28
- Last-Seen: 2026-02-28

---

## [LRN-20260228-005] self_improvement_skill_usage

**Logged**: 2026-02-28T15:05:00+08:00  
**Priority**: critical  
**Status**: active  
**Area**: workflow

### Summary
I was not using the self-improvement skill correctly — files were empty, wrong format

### Details
**What I was doing wrong:**
- Not logging learnings in real-time
- Using free-form text instead of structured format
- No IDs, timestamps, or metadata
- Retroactive population instead of continuous capture

**Correct usage:**
- Log immediately when error/correction occurs
- Use structured format with ID: `TYPE-YYYYMMDD-XXX`
- Include priority, status, area, metadata
- Review before major tasks

**Format:**
```markdown
## [LRN-YYYYMMDD-XXX] short_name

**Logged**: ISO-8601 timestamp
**Priority**: low | medium | high | critical
**Status**: pending | active | resolved
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
- See Also: LRN-YYYYMMDD-XXX
```

### Suggested Action
- Log learnings immediately going forward
- Review learnings files before major tasks
- Enable hook for automatic reminders

### Metadata
- Source: user_feedback (Ryan: "you're not using the skill correctly")
- Related Files: `skills/self-improving-agent/SKILL.md`
- Tags: self-improvement, process, learning
- See Also: None
- Pattern-Key: process.log_immediately
- Recurrence-Count: 1
- First-Seen: 2026-02-28
- Last-Seen: 2026-02-28

---
