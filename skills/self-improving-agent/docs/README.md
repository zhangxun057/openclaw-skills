# Self-Improving Agent

Captures learnings, errors, and corrections to enable continuous improvement for AI coding agents.

## Overview

The Self-Improving Agent skill provides a structured way to:
- Log learnings from user corrections and discoveries
- Track errors and their resolutions
- Capture feature requests
- Extract reusable skills from accumulated knowledge

## Installation

```bash
# Via ClawdHub (recommended)
clawdhub install self-improving-agent

# Manual
git clone https://github.com/peterskoett/self-improving-agent.git ~/.openclaw/skills/self-improving-agent
cd ~/.openclaw/skills/self-improving-agent
npm install
```

## Quick Start

### 1. Create Learning Files

```bash
mkdir -p ~/.openclaw/workspace/.learnings
```

### 2. Capture a Learning

```bash
node src/cli.js learning \
  --title "Docker M1 Fix" \
  --category "best_practice" \
  --description "Use --platform linux/amd64 for M1 compatibility"
```

### 3. Log an Error

```bash
node src/cli.js error \
  --command "npm install" \
  --error "Module not found" \
  --resolution "Install with --legacy-peer-deps"
```

### 4. Extract a Skill

```bash
node src/cli.js extract --name "docker-m1-fixes"
```

## Architecture

```
src/
├── index.js              # Main exports
├── cli.js                # CLI entry point
├── services/
│   ├── learning-service.js   # Learning capture logic
│   ├── error-service.js      # Error detection & logging
│   └── extraction-service.js # Skill extraction
├── hooks/
│   ├── activator-hook.js     # UserPromptSubmit hook
│   └── error-hook.js         # PostToolUse hook
└── utils/
    ├── pattern-matcher.js    # Error pattern detection
    └── template-renderer.js  # Template rendering
```

## API Usage

### Learning Service

```javascript
const { learning } = require('./src/index');

// Capture a learning
const result = learning.captureLearning({
  title: 'Docker M1 Fix',
  category: 'best_practice',
  description: 'Use platform flag for M1',
  tags: ['docker', 'm1']
});

console.log(result.id);  // LRN-20260305-001
```

### Error Service

```javascript
const { error } = require('./src/index');

// Detect errors in output
const hasError = error.detectErrors('Command failed with exit code 1');

// Log an error
const result = error.logError({
  command: 'npm install',
  error: 'Module not found',
  resolution: 'Use --legacy-peer-deps'
});
```

### Extraction Service

```javascript
const { extraction } = require('./src/index');

// Extract a skill
const result = extraction.extractSkill({
  skillName: 'docker-fixes',
  outputDir: './skills'
});
```

## Testing

```bash
# Run all tests
npm test

# Run unit tests only
npm run test:unit

# Run integration tests only
npm run test:integration
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CLAUDE_TOOL_OUTPUT` | Tool output for error hook detection | - |

### Learning Categories

- `best_practice` - Better approaches discovered
- `correction` - User corrections
- `knowledge_gap` - Outdated or missing knowledge

## Documentation

- [Examples](./examples/) - Usage examples
- [Reference](./reference/) - API reference
- [SKILL.md](./SKILL.md) - Full skill documentation

## License

MIT
