# Hooks API Reference

This document describes the hook API for integrating self-improvement reminders into agent workflows.

## Overview

Hooks are triggered at specific points in the agent lifecycle to inject self-improvement reminders.

## Activator Hook

**File:** `src/hooks/activator-hook.js`

**Trigger:** `UserPromptSubmit` - At the start of each user interaction

### Usage

```javascript
const { handleActivator } = require('./src/hooks/activator-hook');

// Get reminder content
const reminder = handleActivator();
console.log(reminder);
```

### Output

```xml
<self-improvement-reminder>
After completing this task, evaluate if extractable knowledge emerged:
- Non-obvious solution discovered through investigation?
- Workaround for unexpected behavior?
- Project-specific pattern learned?
- Error required debugging to resolve?

If yes: Log to .learnings/ using the self-improvement skill format.
If high-value (recurring, broadly applicable): Consider skill extraction.
</self-improvement-reminder>
```

### CLI Usage

```bash
node src/cli.js activator
```

## Error Hook

**File:** `src/hooks/error-hook.js`

**Trigger:** `PostToolUse` (Bash) - After command execution

### Usage

```javascript
const { handleErrorDetection } = require('./src/hooks/error-hook');

// Check output for errors
const output = 'Command failed with exit code 1';
const reminder = handleErrorDetection(output);

if (reminder) {
  console.log(reminder);
}
```

### Output

Returns `null` if no errors detected, or:

```xml
<error-detected>
A command error was detected. Consider logging this to .learnings/ERRORS.md if:
- The error was unexpected or non-obvious
- It required investigation to resolve
- It might recur in similar contexts
- The solution could benefit future sessions

Use the self-improvement skill format: [ERR-YYYYMMDD-XXX]
</error-detected>
```

### CLI Usage

```bash
# Set output in environment variable
export CLAUDE_TOOL_OUTPUT="Command failed with error"
node src/cli.js error-hook
```

## Error Patterns

The error hook detects these patterns by default:

| Pattern | Example |
|---------|---------|
| `error:` | `error: failed to connect` |
| `Error:` | `Error: Connection refused` |
| `ERROR:` | `ERROR: File not found` |
| `failed` | `Command failed` |
| `FAILED` | `BUILD FAILED` |
| `command not found` | `bash: command not found: xyz` |
| `No such file` | `No such file or directory` |
| `Permission denied` | `Permission denied: /root/file` |
| `fatal:` | `fatal: repository not found` |
| `Exception` | `NullPointerException` |
| `Traceback` | `Traceback (most recent call last):` |
| `npm ERR!` | `npm ERR! code ENOENT` |
| `ModuleNotFoundError` | `ModuleNotFoundError: No module named` |
| `SyntaxError` | `SyntaxError: Unexpected token` |
| `TypeError` | `TypeError: Cannot read property` |
| `exit code` | `exited with exit code 1` |
| `non-zero` | `returned non-zero exit status` |

### Custom Patterns

```javascript
const { createPatternMatcher } = require('./src/utils/pattern-matcher');

const customMatcher = createPatternMatcher([
  'CUSTOM_ERROR',
  'WARNING',
  'DEPRECATED'
]);

const hasError = customMatcher.containsError(output);
```

## Integration Examples

### Claude Code

`.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "node ~/.openclaw/skills/self-improving-agent/src/cli.js activator"
      }]
    }],
    "PostToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "node ~/.openclaw/skills/self-improving-agent/src/cli.js error-hook"
      }]
    }]
  }
}
```

### OpenClaw

Hooks are automatically integrated via the skill system.

## API Reference

### handleActivator()

Returns the activator reminder content.

**Returns:** `string` - Reminder content

### handleErrorDetection(output)

Checks output for errors and returns reminder if found.

**Parameters:**
- `output` (string): Command output to check

**Returns:** `string|null` - Error reminder or null

### runActivator()

CLI entry point. Outputs reminder to stdout.

### runErrorHook()

CLI entry point. Reads from `CLAUDE_TOOL_OUTPUT` env var.
