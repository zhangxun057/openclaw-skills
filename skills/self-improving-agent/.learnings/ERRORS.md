# Errors Log

Command failures, exceptions, and unexpected behaviors.

---

## [ERR-20260228-001] clawhub_search_timeout

**Logged**: 2026-02-28T09:00:00+08:00  
**Priority**: medium  
**Status**: pending  
**Area**: infra

### Summary
ClawHub search command times out after 5 minutes without returning results

### Error
```
- Searching
✖ Timeout
Error: Timeout
```

### Context
- Command: `npx clawhub@latest search agenticflow`
- Attempted multiple times with different queries
- Same timeout for `search workflow`, `search task`, etc.

### Suggested Fix
Use alternative discovery methods:
- `npx clawhub@latest explore --limit N` for browsing
- `npx clawhub@latest inspect <slug>` if skill name is known
- Direct web search for skill names

### Metadata
- Reproducible: yes
- Related Files: N/A
- See Also: None

---

## [ERR-20260228-002] git_worktree_branch_conflict

**Logged**: 2026-02-28T11:15:00+08:00  
**Priority**: low  
**Status**: resolved  
**Area**: config

### Summary
Cannot create git worktree while checked out on the same branch

### Error
```
fatal: 'proposal/20260228-1100-evaluate-cortex' is already used by worktree
```

### Context
- Attempting to create worktree while on `proposal/20260228-1100-evaluate-cortex` branch
- Git prevents multiple checkouts of same branch

### Resolution
Checkout different branch first:
```bash
git checkout main
git worktree add ../proposal-name proposal/branch-name
```

### Metadata
- Reproducible: yes (by design)
- Related Files: N/A
- See Also: None

---

## [ERR-20260228-003] github_actions_pr_comment_403

**Logged**: 2026-02-28T08:25:00+08:00  
**Priority**: high  
**Status**: resolved  
**Area**: infra

### Summary
GitHub Actions workflow failed to post PR comment due to missing permissions

### Error
```
RequestError [HttpError]: Resource not accessible by integration
status: 403
url: 'https://api.github.com/repos/.../issues/1/comments'
```

### Context
- CI workflow tried to post validation summary as PR comment
- Default GITHUB_TOKEN lacks `pull-requests: write` permission

### Resolution
Added permissions block to workflow:
```yaml
permissions:
  contents: read
  pull-requests: write
```

### Metadata
- Reproducible: yes (without permissions fix)
- Related Files: `.github/workflows/proposals.yml`
- See Also: None

---
