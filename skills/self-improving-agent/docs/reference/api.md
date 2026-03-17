# API Reference

## Services

### Learning Service

#### `captureLearning(learning, baseDir)`

Captures a learning entry to `.learnings/LEARNINGS.md`.

**Parameters:**
- `learning` (Object): Learning data
  - `title` (string): Learning title
  - `category` (string): One of `best_practice`, `correction`, `knowledge_gap`
  - `description` (string): Detailed description
  - `solution` (string, optional): Solution or workaround
  - `tags` (string[], optional): Array of tags
- `baseDir` (string, optional): Base directory (default: `process.cwd()`)

**Returns:** Object with `success`, `id`, and `file` properties.

**Example:**
```javascript
const { learning } = require('./src');

const result = learning.captureLearning({
  title: 'Docker M1 Fix',
  category: 'best_practice',
  description: 'Use platform flag for M1 Macs',
  tags: ['docker', 'm1']
});

console.log(result.id); // "LRN-20260305-001"
```

### Error Service

#### `logError(error, baseDir)`

Logs an error entry to `.learnings/ERRORS.md`.

**Parameters:**
- `error` (Object): Error data
  - `command` (string): Command that failed
  - `error` (string): Error message
  - `context` (string, optional): Additional context
  - `resolution` (string, optional): How it was resolved
- `baseDir` (string, optional): Base directory

**Returns:** Object with `success`, `id`, and `file` properties.

#### `detectErrors(output)`

Detects if output contains error patterns.

**Parameters:**
- `output` (string): Output to check

**Returns:** Boolean indicating if errors were detected.

### Extraction Service

#### `extractSkill(options)`

Extracts a skill scaffold from a learning.

**Parameters:**
- `options` (Object):
  - `skillName` (string): Name for the skill (kebab-case)
  - `outputDir` (string, optional): Output directory (default: `./skills`)
  - `dryRun` (boolean, optional): If true, don't create files

**Returns:** Object with `success`, `skillPath`, `skillFile`, and optionally `content`.

## Utilities

### Pattern Matcher

#### `containsError(output, patterns)`

Checks if output contains any error patterns.

**Parameters:**
- `output` (string): Output to check
- `patterns` (string[], optional): Custom patterns (default: built-in patterns)

**Returns:** Boolean

#### `getMatchingPatterns(output, patterns)`

Returns all matching error patterns.

**Returns:** Array of matched pattern strings.

#### `createPatternMatcher(patterns)`

Creates a custom pattern matcher.

**Returns:** Object with `patterns`, `containsError()`, and `getMatchingPatterns()`.

### Template Renderer

#### `getLearningReminder()`

Returns the learning reminder content for display.

#### `getActivatorReminder()`

Returns the activator hook reminder content.

#### `getErrorReminder()`

Returns the error detection reminder content.

#### `renderLearningEntry(learning)`

Renders a learning entry in markdown format.

#### `renderErrorEntry(error)`

Renders an error entry in markdown format.

## Hooks

### Activator Hook

Fires on `UserPromptSubmit` to remind about learning capture.

```javascript
const { handleActivator } = require('./src/hooks/activator-hook');
const reminder = handleActivator();
```

### Error Hook

Fires on `PostToolUse` (Bash) to detect errors.

```javascript
const { handleErrorDetection } = require('./src/hooks/error-hook');
const reminder = handleErrorDetection(output);
// Returns reminder string if errors detected, null otherwise
```

## CLI Commands

### `learning`

Capture a learning entry.

```bash
node src/cli.js learning -t "Title" -c "category" -d "Description" [-s "Solution"] [--tags "tag1,tag2"]
```

### `error`

Log an error entry.

```bash
node src/cli.js error -c "command" -e "error message" [--context "..."] [-r "resolution"]
```

### `extract`

Extract a skill scaffold.

```bash
node src/cli.js extract -n "skill-name" [-o "./output/dir"] [--dry-run]
```

### `activator`

Output activator reminder.

```bash
node src/cli.js activator
```

### `error-hook`

Run error detection hook.

```bash
node src/cli.js error-hook
```
