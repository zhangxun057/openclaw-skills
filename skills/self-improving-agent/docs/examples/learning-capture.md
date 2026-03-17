# Learning Capture Example

This example demonstrates capturing a learning after discovering a Docker workaround.

## Scenario

You're working on a project and discover that Docker builds fail on Apple Silicon (M1/M2) Macs when using certain base images.

## The Problem

```bash
$ docker build -t myapp .
[+] Building 2.3s (5/5) FINISHED
 => ERROR [2/3] RUN apt-get update && apt-get install -y python3
------
 > [2/3] RUN apt-get update && apt-get install -y python3:
#0 0.293 exec /bin/sh: exec format error
------
```

## The Solution

Add the `--platform` flag to specify the target architecture:

```bash
docker build --platform linux/amd64 -t myapp .
```

## Capturing the Learning

```bash
node src/cli.js learning \
  --title "Docker M1/M2 Platform Flag" \
  --category "best_practice" \
  --description "When building Docker images on Apple Silicon (M1/M2) Macs that use AMD64 base images, builds may fail with 'exec format error'. Use --platform linux/amd64 to force the target architecture." \
  --solution "Add --platform linux/amd64 to docker build commands when working with cross-platform images." \
  --tags "docker,m1,m2,apple-silicon,platform"
```

## Result

The learning is appended to `.learnings/LEARNINGS.md`:

```markdown
### LRN-20260305-001

**Date:** 2026-03-05

**Category:** best_practice

**Title:** Docker M1/M2 Platform Flag

**Tags:** docker, m1, m2, apple-silicon, platform

**Description:**
When building Docker images on Apple Silicon (M1/M2) Macs that use AMD64 base images, builds may fail with 'exec format error'. Use --platform linux/amd64 to force the target architecture.

**Solution:**
Add --platform linux/amd64 to docker build commands when working with cross-platform images.

---
```

## When to Promote

This learning should be promoted to `CLAUDE.md` or `AGENTS.md` if:
- You frequently work with Docker in this project
- Other team members use M1/M2 Macs
- It's caused issues multiple times

## Promotion

Add to `CLAUDE.md`:

```markdown
## Docker on Apple Silicon

When building Docker images on M1/M2 Macs, always use `--platform linux/amd64` 
for cross-platform compatibility:

```bash
docker build --platform linux/amd64 -t myapp .
```
```
