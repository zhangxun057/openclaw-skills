# Skill Extraction Example

This example demonstrates extracting a reusable skill from accumulated learnings.

## Scenario

You've logged several Docker-related learnings and realize they form a pattern worth capturing as a skill.

## Prerequisites

Check that you have qualifying learnings:

```bash
grep -n "docker" .learnings/LEARNINGS.md
```

## Extraction Criteria

A learning qualifies for skill extraction when:
- It has recurred (2+ similar issues)
- It has a verified, working fix
- It required investigation to discover
- It's broadly applicable across projects

## Dry Run

First, preview what would be created:

```bash
node src/cli.js extract --name "docker-m1-fixes" --dry-run
```

Output:
```
Dry run - would create:
  ./skills/docker-m1-fixes/
  ./skills/docker-m1-fixes/SKILL.md

Content:
---
name: docker-m1-fixes
description: "[TODO: Add a concise description of what this skill does and when to use it]"
---

# Docker M1 Fixes

[TODO: Brief introduction explaining the skill's purpose]
...
```

## Create the Skill

```bash
node src/cli.js extract --name "docker-m1-fixes"
```

Output:
```
Skill created: ./skills/docker-m1-fixes
File: ./skills/docker-m1-fixes/SKILL.md
```

## Customize the Skill

Edit `./skills/docker-m1-fixes/SKILL.md`:

```markdown
---
name: docker-m1-fixes
description: "Fixes for Docker issues on Apple Silicon (M1/M2) Macs. Use when encountering 'exec format error' or platform compatibility issues."
---

# Docker M1 Fixes

Common fixes for Docker issues on Apple Silicon Macs.

## Quick Reference

| Issue | Solution |
|-------|----------|
| exec format error | Add `--platform linux/amd64` |
| Slow builds | Use native arm64 images when available |
| Rosetta issues | Ensure Rosetta 2 is installed |

## Usage

### Platform Flag

When building images that use AMD64 base images:

```bash
docker build --platform linux/amd64 -t myapp .
docker run --platform linux/amd64 myapp
```

### Docker Compose

```yaml
services:
  app:
    platform: linux/amd64
    build: .
```

## Examples

### Building Cross-Platform Images

```bash
# Build for AMD64 (most production servers)
docker build --platform linux/amd64 -t myapp:latest .

# Build for ARM64 (native M1/M2 performance)
docker build --platform linux/arm64 -t myapp:arm64 .
```

## Source Learning

This skill was extracted from learning entries:
- LRN-20260305-001: Docker M1/M2 Platform Flag
- LRN-20260305-015: Docker Compose platform setting
```

## Update Original Learnings

After extraction, update the original learning entries:

```markdown
### LRN-20260305-001

**Date:** 2026-03-05

**Category:** best_practice

**Title:** Docker M1/M2 Platform Flag

**Status:** promoted_to_skill

**Skill-Path:** ./skills/docker-m1-fixes

...
```

## Verify the Skill

Test the skill in a fresh session:

```bash
# Read the skill
cat ./skills/docker-m1-fixes/SKILL.md

# Verify it's self-contained
# (Should make sense without original context)
```

## Next Steps

1. Commit the skill to your repository
2. Share with team members
3. Install via ClawdHub if publishing
